"""Cold-start planar closed rope and literal rounded-annulus first-hit rays.

Only pure source placement/SDF and analytic contact math are reused. No historical
fitted camera, ownership chart or model file is imported or loaded.
"""
from types import SimpleNamespace
import numpy as np
from scipy.interpolate import CubicSpline
from scipy.spatial import cKDTree
from photo2.r279.geometry import R, sdf
from photo2.r280.contact import certificate


def unit(a):
    a = np.asarray(a, float)
    return a/np.maximum(np.linalg.norm(a,axis=-1,keepdims=True),1e-30)


def smooth_curve(points, harmonics=30, samples=4096):
    points=np.asarray(points,float)
    arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(np.vstack([points,points[0]]),axis=0),axis=1))]
    uniform=np.c_[*[np.interp(np.linspace(0,arc[-1],2048,endpoint=False),arc,np.r_[points[:,j],points[0,j]]) for j in range(2)]]
    coeff=np.fft.rfft(uniform,axis=0);coeff[harmonics+1:]=0
    filtered=np.fft.irfft(coeff,n=2048,axis=0)
    spline=CubicSpline(np.linspace(0,1,2049),np.vstack([filtered,filtered[0]]),bc_type='periodic')
    return spline(np.arange(samples)/samples)


class Scene:
    def __init__(self, curve, parameters):
        self.p=dict(parameters);p=self.p;self.n=int(p['n']);self.radius=R;self.bound=R*np.sqrt(1+.7**2)
        self.turns=int(np.floor(.5+self.n/6.5));e=np.radians(p['elevation'])
        self.right=np.array([1.,0,0]);self.down=np.array([0,np.sin(e),-np.cos(e)])
        self.eye=np.cross(self.right,self.down);self.offset=np.asarray(curve).mean(0)+[p.get('dx',0),p.get('dy',0)]
        curve=np.asarray(curve,float);t=np.arange(len(curve))/len(curve)
        tangent=unit(np.roll(curve,-1,axis=0)-np.roll(curve,1,axis=0));normal=np.c_[-tangent[:,1],tangent[:,0]]
        bend=np.asarray(p.get('bend',[0.,0.,0.,0.]))
        b=np.c_[np.sin(2*np.pi*t),np.cos(2*np.pi*t),np.sin(4*np.pi*t),np.cos(4*np.pi*t)]@bend
        image=curve+b[:,None]*normal
        plane=(image-curve.mean(0))/[1,np.sin(e)]
        segment=np.linalg.norm(np.roll(plane,-1,axis=0)-plane,axis=1);arc=np.r_[0,np.cumsum(segment)]
        physical_length=self.turns*(.65*2*R*1.05)*p['pitch']
        self.scale=float(arc[-1]/physical_length);self.length=physical_length
        fractions=(np.arange(self.n)/self.n+p.get('origin',0)/self.n)%1
        xy=np.c_[*[np.interp(fractions,arc/arc[-1],np.r_[plane[:,j],plane[0,j]]) for j in range(2)]]/self.scale
        dplane=unit(np.roll(plane,-1,axis=0)-np.roll(plane,1,axis=0))
        tt=unit(np.c_[*[np.interp(fractions,arc/arc[-1],np.r_[dplane[:,j],dplane[0,j]]) for j in range(2)]])
        tangent=np.c_[tt,np.zeros(self.n)];normal=np.c_[-tt[:,1],tt[:,0],np.zeros(self.n)]
        z=np.tile([0.,0.,1.],(self.n,1));phi=p.get('phase',0)+p['hand']*2*np.pi*self.turns*np.arange(self.n)/self.n
        radial=np.sin(phi)[:,None]*normal+np.cos(phi)[:,None]*z
        self.line=np.c_[xy,np.zeros(self.n)];self.centers=self.line+4*radial
        self.g=dict(surface_tangent=tangent,surface_normal=normal,surface_binormal=z,radial=radial)
        self.pc=self.project(self.centers);self.tree=cKDTree(self.pc)

    def project(self, xyz):
        xyz=np.asarray(xyz);return np.c_[xyz@self.right,xyz@self.down]*self.scale+self.offset

    def trace(self, xy, normals=False):
        xy=np.asarray(xy,float).reshape(-1,2)
        if len(xy)>4000:
            rows=[self.trace(xy[i:i+4000],normals) for i in range(0,len(xy),4000)]
            keys=('owner','unknown','points','normal')
            result={k:np.concatenate([r[k] for r in rows]) for k in keys}
            result['isolated_counts']=np.sum([r['isolated_counts'] for r in rows],axis=0);return result
        base=((xy-self.offset)/self.scale)@np.array([self.right,self.down])
        near=self.tree.query_ball_point(xy,self.bound*self.scale+1e-4)
        a=np.repeat(np.arange(len(xy)),[len(k) for k in near]);k=np.array([j for z in near for j in z],int)
        best=np.full(len(xy),-np.inf);owner=np.full(len(xy),-1,int);unknown=np.zeros(len(xy),bool);counts=np.zeros(self.n,int)
        if len(a):
            delta=base[a]-self.centers[k];mid=-delta@self.eye;perp=(delta*delta).sum(1)-mid*mid;keep=perp<self.bound**2
            a,k,delta,mid,perp=[v[keep] for v in (a,k,delta,mid,perp)]
            axes=[self.g[key][k] for key in ('surface_tangent','surface_normal','surface_binormal')]
            q=np.stack([(delta*v).sum(1) for v in axes],axis=1);v=np.stack([z@self.eye for z in axes],axis=1)
            half=np.sqrt(np.maximum(self.bound**2-perp,0));depth=mid+half;end=mid-half
            active=np.ones(len(a),bool);hit=np.zeros(len(a),bool)
            for _ in range(450):
                ix=np.flatnonzero(active)
                if not len(ix):break
                distance=sdf(q[ix]+depth[ix,None]*v[ix]);yes=distance<1e-5
                hit[ix[yes]]=True;active[ix[yes]]=False;j=ix[~yes]
                depth[j]-=np.maximum(distance[~yes],1e-5);active[j[depth[j]<end[j]]]=False
            np.maximum.at(best,a[hit],depth[hit]);front=hit&(depth>=best[a]-1e-6)
            owner[a[front]]=k[front];unknown[a[active]]=True;owner[unknown]=-1
            counts=np.bincount(k[hit],minlength=self.n)
        points=base+np.where(np.isfinite(best),best,0)[:,None]*self.eye
        n=np.zeros_like(points)
        if normals:
            ok=owner>=0;k=owner[ok];delta=points[ok]-self.centers[k]
            axes=[self.g[key][k] for key in ('surface_tangent','surface_normal','surface_binormal')]
            q=np.stack([(delta*v).sum(1) for v in axes],axis=1)
            gradient=np.stack([(sdf(q+np.eye(3)[j]*1e-4)-sdf(q-np.eye(3)[j]*1e-4))/2e-4 for j in range(3)],axis=1)
            n[ok]=unit(sum(gradient[:,j,None]*axes[j] for j in range(3)))
        return dict(owner=owner,unknown=unknown,points=points,normal=n,isolated_counts=counts)

    def certify(self):
        return certificate(self,iterations=160)

    def grid(self, shape, step=2):
        # Only the union of bounding-square pixels is traced; no image evidence selects it.
        h,w=shape;mask=np.zeros((int(np.ceil(h/step)),int(np.ceil(w/step))),bool)
        bound=self.bound*self.scale
        for cx,cy in self.pc:
            x0,y0=np.maximum(0,np.floor((np.array([cx,cy])-bound)/step).astype(int))
            x1,y1=np.minimum(mask.shape[::-1],np.ceil((np.array([cx,cy])+bound)/step).astype(int)+1)
            if x1>x0 and y1>y0:mask[y0:y1,x0:x1]=True
        yy,xx=np.where(mask);xy=np.c_[xx,yy]*step
        return xy,self.trace(xy,normals=True)


def cold_parameters(n, hand, elevation=75., pitch=1.40):
    return dict(n=int(n),hand=int(hand),elevation=float(elevation),pitch=float(pitch),
                phase=0.,origin=0.,dx=0.,dy=0.,bend=[0.,0.,0.,0.])
