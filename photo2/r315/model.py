"""Explicit image registration, bounded compact fields, and relevant-ray refinement."""
from copy import copy
import numpy as np
from scipy.spatial import cKDTree
from photo2.r295.geometry import AXES,unit
from photo2.r314.geometry import ShapeChain,kernel


def bump(k,c,w):
    z=(np.asarray(k)-c)/w
    return np.maximum(0,1-z*z)**3

class Chain(ShapeChain):
    def station(self,k):
        base=super().station(k)
        for c,a in zip(self.p.get('compact_centers',[-35,0,35]),self.p.get('compact_spacing',[0,0,0])):
            base=base+a*self.extent/self.n*(np.asarray(k)-c)*bump(k,c,self.p.get('spacing_halfwidth',65))
        return base
    def placement(self,k):
        line,g,phase=super().placement(k)
        d=sum(a*bump(k,c,self.p.get('phase_halfwidth',45)) for c,a in zip(self.p.get('compact_centers',[-35,0,35]),self.p.get('compact_phase',[0,0,0])))
        if np.any(d):
            t=g['axis_tangent'];co=np.cos(d)[:,None];si=np.sin(d)[:,None]
            # Rotation around -t maps sin(phi)*normal+cos(phi)*z to phi+d.
            for key in [*AXES,'radial']:
                v=g[key];g[key]=co*v-si*np.cross(t,v)+(1-co)*np.sum(t*v,axis=1)[:,None]*t
            phase=phase+d
        return line,g,phase
    def __init__(self,p,data):
        super().__init__(p,data)
        k=np.linspace(-101,101,809);eps=.001;centers=p.get('compact_centers',[-35,0,35]);pw=p.get('phase_halfwidth',45);sw=p.get('spacing_halfwidth',65)
        ph=sum(a*(bump(k+eps,c,pw)-bump(k-eps,c,pw))/(2*eps) for c,a in zip(centers,p.get('compact_phase',[0,0,0])))
        sp=sum(a*((k+eps-c)*bump(k+eps,c,sw)-(k-eps-c)*bump(k-eps,c,sw))/(2*eps) for c,a in zip(centers,p.get('compact_spacing',[0,0,0])))
        if p.get('compact_phase_rate_limit',.02)>.05:raise ValueError('Maximum exploratory phase rate is 5 percent')
        if np.max(abs(ph))>p.get('compact_phase_rate_limit',.02)*2*np.pi/6.5 or np.max(abs(sp))>.02:raise ValueError('compact rate bound')
        self.compact_rate_bounds=dict(phase_rad_per_address=float(np.max(abs(ph))),spacing_fraction=float(np.max(abs(sp))))
        self.offset=self.offset+np.array(p.get('translation',[0.,0.]));self.pc=self.project(self.centers);self.tree=cKDTree(self.pc)


def refined_trace(s,xy,remove=(),iterations=12000):
    """Same native kernel, continue only unresolved pair rays; irrelevant uncertainty cannot hide a nearer certified hit."""
    xy=np.asarray(xy,float).reshape(-1,2)
    if len(xy)>20000:
        rr=[refined_trace(s,xy[i:i+20000],remove,iterations) for i in range(0,len(xy),20000)]
        return {k:np.concatenate([r[k] for r in rr]) for k in rr[0]}
    base=((xy-s.offset)/s.scale)@np.array([s.right,s.down]);ray=unit(s.eye-base/s.distance) if np.isfinite(s.distance) else np.tile(s.eye,(len(xy),1))
    near=s.tree.query_ball_point(xy,s.query_radius+1e-4);a=np.repeat(np.arange(len(xy)),[len(v) for v in near]);j=np.array([j for v in near for j in v],int)
    if remove:
        keep=~np.isin(s.indices[j],remove);a,j=a[keep],j[keep]
    delta=base[a]-s.centers[j];mid=-np.sum(delta*ray[a],axis=1);perp=np.sum(delta*delta,axis=1)-mid*mid;keep=perp<s.bound*s.bound
    a,j,delta,mid,perp=[v[keep] for v in [a,j,delta,mid,perp]];half=np.sqrt(np.maximum(s.bound*s.bound-perp,0))
    q=np.stack([np.sum(delta*s.g[key][j],axis=1) for key in AXES],axis=1);v=np.stack([np.sum(ray[a]*s.g[key][j],axis=1) for key in AXES],axis=1)
    dep,state=kernel(q,v,mid+half,mid-half,np.r_[s.dims,s.hole,s.rounding,float(s.exterior),s.edge,s.face,s.bore],-1)
    initial=np.zeros(len(xy),bool);initial[a[state==2]]=True
    for _ in range(iterations):
        ix=np.flatnonzero(state==2)
        if not len(ix):break
        sd=s.local_sdf(q[ix]+dep[ix,None]*v[ix]);hit=sd<1e-5;state[ix[hit]]=1;z=ix[~hit];dep[z]-=np.maximum(sd[~hit],1e-5);state[z[dep[z]<mid[z]-half[z]]]=0
    best=np.full(len(xy),-np.inf);owner=np.full(len(xy),-1,int);hit=state==1;np.maximum.at(best,a[hit],dep[hit]);front=hit&(dep>=best[a]-1e-6);owner[a[front]]=j[front]
    unknown=np.zeros(len(xy),bool);danger=(state==2)&(dep>=best[a]-1e-6);unknown[a[danger]]=True;owner[unknown]=-1
    return dict(owner=owner,unknown=unknown,points=base+np.where(np.isfinite(best),best,0)[:,None]*ray,depth=best,initial_unknown=initial)


def subset(s,js):
    z=copy(s);js=np.asarray(js,int);z.n=len(js);z.centers=s.centers[js];z.pc=s.pc[js];z.indices=s.indices[js];z.g={k:v[js] for k,v in s.g.items()};z.tree=cKDTree(z.pc);return z
