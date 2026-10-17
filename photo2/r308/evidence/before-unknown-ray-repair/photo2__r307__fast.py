"""Compiled literal native marching kernel; no changed shape or ray tolerance."""
import ctypes,subprocess
from pathlib import Path
import numpy as np
from photo2.r306.geometry import Chain as Original
from photo2.r295.geometry import AXES,unit
from photo2.r279.geometry import R
from photo2.r297.common import sha
SOURCE=Path(__file__).with_suffix('.py').with_name('kernel.cpp')
LIB=Path('/tmp')/('beads-r307-'+sha(SOURCE)[:16]+'.so')
_lib=None
def kernel(q,v,begin,end,dims,direction):
    global _lib
    if _lib is None:
        if not LIB.exists():subprocess.run(['g++','-O3','-std=c++17','-shared','-fPIC',str(SOURCE),'-o',str(LIB)],check=True)
        _lib=ctypes.CDLL(str(LIB));ptr=np.ctypeslib.ndpointer(dtype=np.float64,flags='C_CONTIGUOUS');ip=np.ctypeslib.ndpointer(dtype=np.int32,flags='C_CONTIGUOUS')
        _lib.march.argtypes=[ctypes.c_long,ptr,ptr,ptr,ptr,ptr,ctypes.c_double,ctypes.c_int,ptr,ip]
    n=len(begin);depth=np.empty(n);state=np.empty(n,np.int32)
    args=[np.ascontiguousarray(x,dtype=float) for x in (q,v,begin,end,dims)]
    _lib.march(n,*args,R,direction,depth,state)
    return depth,state
class Chain(Original):
    def trace(self,xy,normals=False):
        if normals:return super().trace(xy,normals)
        xy=np.asarray(xy,float).reshape(-1,2)
        if len(xy)>20000:
            chunks=[self.trace(xy[i:i+20000]) for i in range(0,len(xy),20000)]
            out={k:np.concatenate([r[k] for r in chunks]) for k in ('owner','unknown','points','normal')};out['isolated_counts']=sum(r['isolated_counts'] for r in chunks);return out
        base=((xy-self.offset)/self.scale)@np.array([self.right,self.down]);ray=unit(self.eye-base/self.distance) if np.isfinite(self.distance) else np.tile(self.eye,(len(xy),1))
        near=self.tree.query_ball_point(xy,self.query_radius+1e-4);a=np.repeat(np.arange(len(xy)),[len(k) for k in near]);k=np.array([j for z in near for j in z],int)
        best=np.full(len(xy),-np.inf);owner=np.full(len(xy),-1,int);unknown=np.zeros(len(xy),bool);counts=np.zeros(self.n,int)
        if len(a):
            delta=base[a]-self.centers[k];mid=-(delta*ray[a]).sum(1);perp=(delta*delta).sum(1)-mid*mid;keep=perp<self.bound**2
            a,k,delta,mid,perp=[v[keep] for v in (a,k,delta,mid,perp)]
            axes=[self.g[key][k] for key in AXES];q=np.stack([(delta*v).sum(1) for v in axes],axis=1);v=np.stack([(z*ray[a]).sum(1) for z in axes],axis=1);half=np.sqrt(np.maximum(self.bound**2-perp,0))
            depth,state=kernel(q,v,mid+half,mid-half,self.dims,-1);hit=state==1;active=state==2
            np.maximum.at(best,a[hit],depth[hit]);front=hit&(depth>=best[a]-1e-6);owner[a[front]]=k[front];unknown[a[active]]=True;owner[unknown]=-1;counts=np.bincount(k[hit],minlength=self.n)
        points=base+np.where(np.isfinite(best),best,0)[:,None]*ray
        return dict(owner=owner,unknown=unknown,points=points,normal=np.zeros_like(points),isolated_counts=counts)
    def blocked(self,points,direction,max_distance=np.inf):
        from scipy.spatial import cKDTree
        points=np.asarray(points);d=np.asarray(direction)
        if d.ndim==2:return super().blocked(points,direction,max_distance)
        blocked=np.zeros(len(points),bool);owner=np.full(len(points),-1,int);unknown=0
        if not len(points):return blocked,owner,unknown
        axis=np.eye(3)[np.argmin(abs(d))];r=unit(np.cross(d,axis));s=np.cross(d,r);tree=cKDTree(np.c_[self.centers@r,self.centers@s])
        near=tree.query_ball_point(np.c_[points@r,points@s],self.bound);a=np.repeat(np.arange(len(points)),[len(x) for x in near]);b=np.array([k for x in near for k in x],int)
        delta=points[a]-self.centers[b];mid=-delta@d;perp=np.sum(delta**2,axis=1)-mid**2;half=np.sqrt(np.maximum(self.bound**2-perp,0));t=np.maximum(0,mid-half);end=np.minimum(max_distance,mid+half);keep=end>=t
        a,b,delta,t,end=[z[keep] for z in (a,b,delta,t,end)]
        if not len(a):return blocked,owner,unknown
        axes=[self.g[key][b] for key in AXES];q=np.stack([np.sum(delta*z,axis=1) for z in axes],axis=1);v=np.stack([z@d for z in axes],axis=1)
        t,state=kernel(q,v,t,end,self.dims,1);hit=state==1;active=state==2;unknown=int(active.sum());blocked[a[hit|active]]=True
        first=np.full(len(points),np.inf);np.minimum.at(first,a[hit],t[hit]);front=hit&(t<=first[a]+1e-6);owner[a[front]]=b[front];owner[a[active]]=-2
        return blocked,owner,unknown

def grid(scene,step=2.,owners=None):
    """Union of complete conservative body boxes, on the original pixel lattice."""
    owners=np.arange(scene.n) if owners is None else np.asarray(owners,int)
    width=int(np.ceil(2540/step));height=int(np.ceil(3182/step));parts=[];rad=scene.query_radius+1
    for x,y in scene.pc[owners]:
        x0=max(0,int(np.ceil((x-rad)/step)));x1=min(width,int(np.floor((x+rad)/step))+1)
        y0=max(0,int(np.ceil((y-rad)/step)));y1=min(height,int(np.floor((y+rad)/step))+1)
        if x1>x0 and y1>y0:parts.append((np.arange(y0,y1)[:,None]*width+np.arange(x0,x1)).ravel())
    ids=np.unique(np.concatenate(parts)) if parts else np.empty(0,int)
    xy=np.c_[ids%width,ids//width]*step
    return xy[scene.tree.query(xy)[0]<=rad]

def predict(scene,step=2.,observations=None,detail=False,owners=None):
    from photo2.r299.forward import light_params,shade,highlight
    if owners is None and observations is not None:
        near=scene.tree.query_ball_point([r['point'] for r in observations],55.)
        owners=np.array(sorted({j for row in near for j in row}),int)
    if owners is None:owners=np.arange(scene.n)
    xy=grid(scene,step,owners);light=light_params([scene.p['light_az'],scene.p['light_el'],scene.p['roughness']],'directional',scene.centers.mean(0))
    parts=[];vals=[];unknown=shadow=0
    for start in range(0,len(xy),20000):
        tr=scene.camera(xy[start:start+20000]);sh=shade(scene,tr,light);parts.append(tr['owner']);vals.append(sh['intensity']);unknown+=int(tr['unknown'].sum());shadow+=sh['unknown_shadow_pairs']
    owner=np.concatenate(parts);w=np.concatenate(vals);order=np.argsort(owner,kind='stable');cuts=np.r_[0,np.flatnonzero(np.diff(owner[order]))+1,len(order)];pred=[];allowed=set(owners)
    for a,b in zip(cuts[:-1],cuts[1:]):
        ix=order[a:b];j=int(owner[ix[0]])
        if j<0 or j not in allowed:continue
        h=highlight(xy[ix],w[ix],step)
        if h:pred.append(dict(index=int(scene.indices[j]),point=h['centroid'],peak=h['peak'],strength=h['peak_intensity'],area_px2=h['area_px2']))
    meta=dict(rays=len(xy),unknown_camera=unknown,unknown_shadow=shadow,step=step)
    if detail:meta.update(xy=xy,owner=owner,intensity=w)
    return pred,meta
