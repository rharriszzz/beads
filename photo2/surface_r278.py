"""Rounded annulus ray marcher with arbitrary orthonormal bead hole axes.

The old surface is rotationally symmetric about its first local coordinate.
This extends orientation only; it does not alter dimensions, fill the hole or
substitute spheres for surfaces. Spheres bound ray candidates.
"""
import numpy as np
from scipy.spatial import cKDTree
from .construction_r278 import sdf
from .bead_debugger.surface import local_normal,unit,RADIUS

KEYS=('surface_tangent','surface_normal','surface_binormal')

def local(s,vec,owner):return np.stack([np.sum(vec*s.g[k][owner],axis=-1) for k in KEYS],axis=-1)

def march(s,delta,direction,owner,start,end,sign):
    q=local(s,delta,owner);v=local(s,direction,owner);t=start.copy()
    active=np.ones(len(t),bool);hit=np.zeros(len(t),bool);eps=1e-5*s.factor
    for _ in range(800):
        ix=np.flatnonzero(active)
        if not len(ix):break
        distance=sdf(q[ix]+t[ix,None]*v[ix],s.radius);yes=distance<eps
        hit[ix[yes]]=True;active[ix[yes]]=False;move=ix[~yes]
        t[move]+=sign*np.maximum(distance[~yes],eps)
        active[move[sign*(t[move]-end[move])>0]]=False
    return t,hit,active

def camera(s,xy):
    xy=np.asarray(xy,float)
    if len(xy)>4000:
        parts=[camera(s,xy[i:i+4000]) for i in range(0,len(xy),4000)]
        return {k:np.concatenate([p[k] for p in parts]) for k in parts[0]}
    view=s.model.view;v=view.directions(xy);base=view.base(xy);bound=s.bound
    rad=bound*view.scale+1e-4
    if view.focal:
        den=1-view.scale*(s.centers@view.basis()[2])/view.focal
        rad=bound*view.scale*(1+np.max(np.linalg.norm(s.pc-[view.tx,view.ty],axis=1))/view.focal)/(den.min()-bound*view.scale/view.focal)+1e-4
    nearby=cKDTree(s.pc).query_ball_point(xy,rad)
    a=np.repeat(np.arange(len(xy)),[len(z) for z in nearby]);b=np.array([k for z in nearby for k in z],int)
    owner=np.full(len(xy),-1,int);best=np.full(len(xy),-np.inf);unknown=np.zeros(len(xy),int)
    if len(a):
        delta=base[a]-s.centers[b];u=v[a];mid=-np.sum(delta*u,axis=1);perp=np.sum(delta**2,axis=1)-mid**2;keep=perp<bound**2
        a,b,delta,u,mid,perp=[z[keep] for z in (a,b,delta,u,mid,perp)]
        half=np.sqrt(np.maximum(bound**2-perp,0));t,hit,active=march(s,delta,u,b,mid+half,mid-half,-1)
        np.add.at(unknown,a[active],1);np.maximum.at(best,a[hit],t[hit]);front=hit&(t>=best[a]-5e-6*s.factor);owner[a[front]]=b[front]
    points=base+np.where(np.isfinite(best),best,0)[:,None]*v;normal=np.zeros_like(points)
    ok=(owner>=0)&(unknown==0);k=owner[ok]
    nn=local_normal(local(s,points[ok]-s.centers[k],k)/s.factor)
    normal[ok]=sum(nn[:,j,None]*s.g[key][k] for j,key in enumerate(KEYS));owner[unknown>0]=-1
    return dict(xy=xy,owner=owner,points=points,normal=normal,viewer=v,unknown=unknown)

def blocked(s,points,direction,return_owner=False):
    p=np.asarray(points);d=unit(direction);r=unit(np.cross(d,np.eye(3)[np.argmin(abs(d))]));v=np.cross(d,r)
    tree=cKDTree(np.c_[s.centers@r,s.centers@v]);result=np.zeros(len(p),bool);owners=np.full(len(p),-1,int);unfinished=0
    for start in range(0,len(p),4000):
        q=p[start:start+4000];near=tree.query_ball_point(np.c_[q@r,q@v],s.bound)
        a=np.repeat(np.arange(len(q)),[len(z) for z in near]);b=np.array([k for z in near for k in z],int)
        if not len(a):continue
        delta=q[a]-s.centers[b];mid=-delta@d;perp=np.sum(delta**2,axis=1)-mid**2;half=np.sqrt(np.maximum(s.bound**2-perp,0))
        t=np.maximum(mid-half,0);end=mid+half;keep=end>=t
        a,b,delta,t,end=[z[keep] for z in (a,b,delta,t,end)]
        t,hit,active=march(s,delta,np.broadcast_to(d,delta.shape),b,t,end,1)
        result[start+a[hit|active]]=True;unfinished+=int(active.sum())
        front=np.full(len(q),np.inf);np.minimum.at(front,a[hit],t[hit]);first=hit&(t<=front[a]+5e-6*s.factor)
        owners[start+a[first]]=b[first];owners[start+a[active]]=-2
    return (result,unfinished,owners) if return_owner else (result,unfinished)
