"""R258 source-annulus dimension sensitivity; default equals R254/R257 rays.

Exact same rounded rectangular radial profile; no sphere footprint approximation.
Spheres accelerate candidate tests only. Size/axial factors default to source1.
"""
import numpy as np
from scipy.spatial import cKDTree
from .models import RADIUS

def annulus_sdf(v,size=1.,axial=1.):
    r=RADIUS*size;extra=.2*.43*r
    qr=np.abs(np.hypot(v[...,1],v[...,2])-.57*r)-extra
    qa=np.abs(v[...,0])/(.7/.43*axial)-extra
    # Conservative Lipschitz bound even for compressed axial diagnostics.
    return (np.hypot(np.maximum(qr,0),np.maximum(qa,0))+np.minimum(np.maximum(qr,qa),0)-.8*.43*r)/max(1,1/(.7/.43*axial))

def trace(model,xy,g=None,size=1.,axial=1.):
    xy=np.asarray(xy,float)
    if len(xy)>4000:
        parts=[trace(model,xy[i:i+4000],g,size,axial) for i in range(0,len(xy),4000)]
        return tuple(np.concatenate([p[j] for p in parts]) for j in range(3))
    if g is None:g=model.geometry(np.arange(model.source.nbeads))
    c=g['centers'];v=model.view;bound=RADIUS*size*np.sqrt(1+(.7*axial)**2);pc=v.project(c);radius=bound*v.scale+1e-4
    if v.focal:
        den=1-v.scale*(c@v.basis()[2])/v.focal
        radius=bound*v.scale*(1+np.max(np.linalg.norm(pc-[v.tx,v.ty],axis=1))/v.focal)/(den.min()-bound*v.scale/v.focal)+1e-4
    nearby=cKDTree(pc).query_ball_point(xy,radius);a=np.repeat(np.arange(len(xy)),[len(x) for x in nearby]);b=np.array([k for x in nearby for k in x],int)
    best=np.full(len(xy),-np.inf);owner=np.full(len(xy),-1,int);unknown=np.zeros(len(xy),int)
    if not len(a):return owner,best,unknown
    base=v.base(xy);ray=v.directions(xy);delta=base[a]-c[b];u=ray[a];middle=-np.sum(delta*u,axis=1);perp=np.sum(delta**2,axis=1)-middle**2;keep=perp<bound**2
    a,b,delta,u,middle,perp=[x[keep] for x in (a,b,delta,u,middle,perp)];half=np.sqrt(np.maximum(bound**2-perp,0));depth=middle+half;end=middle-half
    local=np.c_[np.sum(delta*g['tangent'][b],axis=1),np.sum(delta*g['normal'][b],axis=1),delta[:,2]]
    direction=np.c_[np.sum(u*g['tangent'][b],axis=1),np.sum(u*g['normal'][b],axis=1),u[:,2]]
    alive=np.ones(len(a),bool);hit=np.zeros(len(a),bool);eps=1e-5
    for _ in range(600):
        ix=np.flatnonzero(alive)
        if not len(ix):break
        distance=annulus_sdf(local[ix]+depth[ix,None]*direction[ix],size,axial);yes=distance<eps;hit[ix[yes]]=True;alive[ix[yes]]=False;moving=ix[~yes];depth[moving]-=np.maximum(distance[~yes],eps);alive[moving[depth[moving]<end[moving]]]=False
    np.add.at(unknown,a[alive],1);np.maximum.at(best,a[hit],depth[hit]);front=hit&(depth>=best[a]-eps/2);owner[a[front]]=g['indices'][b[front]]
    return owner,best,unknown
