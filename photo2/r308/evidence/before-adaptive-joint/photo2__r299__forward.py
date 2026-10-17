"""Current annular surfaces, inverse-transpose normals, all-chain shadow visibility.

One source only. Shared half-vector BRDF is a positional approximation, not a
radiometrically calibrated microfacet material. No observation enters prediction.
"""
import numpy as np
from scipy.spatial import cKDTree
from photo2.r298.geometry import Chain, R, unit
from photo2.r295.geometry import AXES
from photo2.bead_debugger.surface import moments,directions


def normal_local(q,dims):
    p=np.asarray(q)/dims;rho=np.linalg.norm(p[...,1:],axis=-1);qr=abs(rho-.57*R)-.086*R;qa=abs(p[...,0])/(.7/.43)-.086*R
    gr=np.maximum(qr,0);ga=np.maximum(qa,0);inside=(gr+ga)==0
    gr=np.where(inside&(qr>=qa),1,gr);ga=np.where(inside&(qa>qr),1,ga)
    rr=gr*np.sign(rho-.57*R)/np.maximum(rho,1e-30)
    grad=np.stack([ga*np.sign(p[...,0])/(.7/.43),rr*p[...,1],rr*p[...,2]],axis=-1)
    return unit(grad/dims)


class Surface(Chain):
    def camera(self,xy):
        xy=np.asarray(xy).reshape(-1,2);tr=self.trace(xy);ok=tr['owner']>=0;k=tr['owner'][ok];p=tr['points'];delta=p[ok]-self.centers[k];axes=[self.g[key][k] for key in AXES];q=np.stack([np.sum(delta*a,axis=1) for a in axes],axis=1);n=normal_local(q,self.dims)
        tr['normal'][ok]=sum(n[:,j,None]*a for j,a in enumerate(axes));tr['xy']=xy
        tr['viewer']=unit(self.distance*self.eye-p) if np.isfinite(self.distance) else np.tile(self.eye,(len(xy),1))
        return tr

    def blocked(self,points,direction,max_distance=np.inf):
        """Finite segments and distant rays against every body's exact annulus.

        Directional perpendicular tree is exact conservative acceleration; finite
        rays test all bounding spheres in chunks, then exact conservative SDF.
        Unknown grazing pairs block the ray, and are counted separately.
        """
        points=np.asarray(points);d=np.asarray(direction);vary=d.ndim==2;blocked=np.zeros(len(points),bool);owner=np.full(len(points),-1,int);unknown=0
        if not len(points):return blocked,owner,unknown
        if not vary:
            axis=np.eye(3)[np.argmin(abs(d))];r=unit(np.cross(d,axis));s=np.cross(d,r);tree=cKDTree(np.c_[self.centers@r,self.centers@s])
        for start in range(0,len(points),512):
            p=points[start:start+512];v=d[start:start+len(p)] if vary else np.tile(d,(len(p),1));limits=np.asarray(max_distance)[start:start+len(p)] if np.ndim(max_distance) else np.full(len(p),max_distance)
            if vary:
                delta=p[:,None,:]-self.centers[None];mid=-np.einsum('ijk,ik->ij',delta,v);perp=np.einsum('ijk,ijk->ij',delta,delta)-mid**2
                a,b=np.where((perp<self.bound**2)&(mid+self.bound>0)&(mid-self.bound<limits[:,None]));delta=delta[a,b];mid=mid[a,b];perp=perp[a,b]
            else:
                near=tree.query_ball_point(np.c_[p@r,p@s],self.bound);a=np.repeat(np.arange(len(p)),[len(x) for x in near]);b=np.array([k for x in near for k in x],int);delta=p[a]-self.centers[b];mid=-np.sum(delta*v[a],axis=1);perp=np.sum(delta**2,axis=1)-mid**2
            half=np.sqrt(np.maximum(self.bound**2-perp,0));t=np.maximum(0,mid-half);end=np.minimum(limits[a],mid+half);keep=end>=t;a,b,delta,t,end=[z[keep] for z in (a,b,delta,t,end)]
            if not len(a):continue
            axes=[self.g[key][b] for key in AXES];q=np.stack([np.sum(delta*z,axis=1) for z in axes],axis=1);vlocal=np.stack([np.sum(v[a]*z,axis=1) for z in axes],axis=1);active=np.ones(len(a),bool);hit=np.zeros(len(a),bool)
            for _ in range(450):
                ix=np.flatnonzero(active)
                if not len(ix):break
                sd=self.local_sdf(q[ix]+t[ix,None]*vlocal[ix]);yes=sd<1e-5;hit[ix[yes]]=True;active[ix[yes]]=False;move=ix[~yes];t[move]+=np.maximum(sd[~yes],1e-5);active[move[t[move]>end[move]]]=False
            unknown+=int(active.sum());blocked[start+a[hit|active]]=True;first=np.full(len(p),np.inf);np.minimum.at(first,a[hit],t[hit]);front=hit&(t<=first[a]+1e-6);owner[start+a[front]]=b[front];owner[start+a[active]]=-2
        return blocked,owner,unknown


def shade(scene,data,light,order=3,shadows=True):
    p=data['points'];n=data['normal'];v=data['viewer'];valid=data['owner']>=0;spec=np.zeros(len(p));diff=np.zeros(len(p));unknown=0;self_count=0;neighbor_count=0
    alpha=np.radians(light['roughness_deg']);exponent=max(1,2/alpha**2-2)
    samples=[(None,1.)] if light['kind']=='finite' else directions(light,order)
    for direct,weight in samples:
        distance=np.inf
        if direct is None:
            delta=np.array(light['position'])-p;distance=np.linalg.norm(delta,axis=1);direct=unit(delta);attenuation=(light['distance']/np.maximum(distance,1e-9))**2
        else:attenuation=1.
        nl=np.maximum(np.sum(n*direct,axis=1),0) if np.ndim(direct)==2 else np.maximum(n@direct,0);h=unit(v+direct);lobe=np.maximum(np.sum(n*h,axis=1),0)**exponent*nl*attenuation
        blocked=np.zeros(len(p),bool)
        if shadows:
            # Omitted lobe tails sum below 1e-8 relative per quadrature node.
            ix=np.flatnonzero(valid&(nl>0)&(lobe>1e-8))
            blocked[ix],b,u=scene.blocked(p[ix]+n[ix]*1e-3,direct[ix] if np.ndim(direct)==2 else direct,distance[ix] if np.ndim(distance) else distance);unknown+=u
            self_count+=int(np.sum(b==data['owner'][ix]));neighbor_count+=int(np.sum((b>=0)&(b!=data['owner'][ix])))
        spec+=weight*lobe*(~blocked);diff+=weight*nl*(~blocked)
    spec[~valid]=0;diff[~valid]=0
    return dict(intensity=spec,unknown_shadow_pairs=unknown,self_shadow_samples=self_count,neighbor_shadow_samples=neighbor_count)


def highlight(xy,intensity,step=1.):
    if not len(intensity) or intensity.max()<1e-4:return None
    peak=float(intensity.max());mask=intensity>=max(peak*.5,1e-4);pts=xy[mask];w=intensity[mask];m=moments(pts,w)
    m.update(peak=xy[np.argmax(intensity)].tolist(),peak_intensity=peak,area_px2=float(mask.sum()*step**2),region=pts.tolist(),intensity=w.tolist(),threshold_fraction=.5)
    return m


def grids(scene,owners,step=1.):
    """Complete projected bounding boxes of owners; all chain beads occlude."""
    chunks=[];size=scene.query_radius+2
    for k in sorted(set(owners)-{-1}):
        x,y=scene.pc[k];x0=max(0,np.floor((x-size)/step)*step);x1=min(2539,x+size);y0=max(0,np.floor((y-size)/step)*step);y1=min(3181,y+size)
        yy,xx=np.mgrid[y0:y1+step/2:step,x0:x1+step/2:step];xy=np.c_[xx.ravel(),yy.ravel()];tr=scene.camera(xy);keep=tr['owner']==k
        chunks.append({key:tr[key][keep] for key in ['xy','owner','points','normal','viewer','unknown']})
    return {key:np.concatenate([c[key] for c in chunks]) if chunks else np.empty((0,3) if key in ['points','normal','viewer'] else (0,2) if key=='xy' else (0,)) for key in ['xy','owner','points','normal','viewer','unknown']}


def light_params(v,kind,center):
    az,el=np.radians(v[:2]);d=np.array([np.cos(el)*np.cos(az),np.cos(el)*np.sin(az),np.sin(el)]);light=dict(kind=kind,direction=d.tolist(),roughness_deg=float(v[2]),width_deg=0.,height_deg=0.)
    if kind=='finite':light.update(distance=float(v[3]),position=(center+v[3]*d).tolist())
    if kind=='extended':light.update(width_deg=float(v[3]),height_deg=float(v[3]))
    return light
