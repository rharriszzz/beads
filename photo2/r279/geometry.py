"""Fresh straight local limit. No historical model/observation imports or I/O."""
import numpy as np
from photo2.bead_placement import Rope, bead_surface_samples

ROPE=Rope(2600,radius_convention='intended')
R=ROPE.bead_radius
PITCH=.65*2*R*1.05/6.5
INDICES=np.arange(-14,15)
# Reuse the independently implemented existing analytic rounded-annulus sampler.
_s=bead_surface_samples(ROPE,0,8,32)-ROPE.place(0)[0]
SURFACE=_s[:,[1,0,2]]

def centers(indices,hand,phase,pitch=1.):
    k=np.asarray(indices); a=phase+hand*2*np.pi*k/6.5
    return np.c_[k*PITCH*pitch,4*np.sin(a),4*np.cos(a)]

def frame(inclination,roll=0.):
    a,b=np.radians([inclination,roll]);r=np.array([np.cos(a),0,-np.sin(a)])
    d=np.array([0.,1.,0.]);e=np.cross(r,d)
    return np.cos(b)*r-np.sin(b)*d,np.sin(b)*r+np.cos(b)*d,e

def project(p,xyz):
    r,d,_=frame(p['inclination'],p.get('roll',0.))
    return np.c_[xyz@r,xyz@d]*p['scale']+p['translation']

def sdf(q):
    q=np.asarray(q); a=abs(np.hypot(q[...,1],q[...,2])-.57*R)-.086*R
    b=abs(q[...,0])/(.7/.43)-.086*R
    return np.hypot(np.maximum(a,0),np.maximum(b,0))+np.minimum(np.maximum(a,b),0)-.344*R

def trace(p,xy,indices=INDICES):
    """Exact implicit annulus; all-neighbor first hit, unknown rays kept separate."""
    xy=np.asarray(xy,float)
    if len(xy)>2500:
        v=[trace(p,xy[i:i+2500],indices) for i in range(0,len(xy),2500)]
        return tuple(np.concatenate([z[j] for z in v]) for j in range(3))
    r,d,e=frame(p['inclination'],p.get('roll',0.));base=((xy-np.array(p['translation']))/p['scale'])@np.array([r,d])
    c=centers(indices,p['hand'],p['phase'],p.get('pitch',1.));delta=base[:,None,:]-c
    mid=-delta@e;perp=(delta*delta).sum(2)-mid*mid;bound=R*np.sqrt(1+.7**2)
    a,b=np.where(perp<bound**2);half=np.sqrt(np.maximum(bound**2-perp[a,b],0));t=mid[a,b]+half;end=mid[a,b]-half
    live=np.ones(len(a),bool);hit=np.zeros(len(a),bool)
    for _ in range(450):
        ix=np.flatnonzero(live)
        if not len(ix):break
        sd=sdf(delta[a[ix],b[ix]]+t[ix,None]*e);yes=sd<1e-5
        hit[ix[yes]]=True;live[ix[yes]]=False;ii=ix[~yes];t[ii]-=np.maximum(sd[~yes],1e-5);live[ii[t[ii]<end[ii]]]=False
    depth=np.full(len(xy),-np.inf);owner=np.full(len(xy),-999,int);unknown=np.zeros(len(xy),bool)
    np.maximum.at(depth,a[hit],t[hit]);front=hit&(t>=depth[a]-1e-6);owner[a[front]]=np.asarray(indices)[b[front]];unknown[a[live]]=True;owner[unknown]=-999
    return owner,depth,unknown

def visible(p,k,step=2):
    pc=project(p,centers([k],p['hand'],p['phase'],p.get('pitch',1.)))[0];rad=R*1.23*p['scale']
    yy,xx=np.mgrid[np.floor(pc[1]-rad):np.ceil(pc[1]+rad):step,np.floor(pc[0]-rad):np.ceil(pc[0]+rad):step]
    xy=np.c_[xx.ravel(),yy.ravel()];o,_,u=trace(p,xy)
    return xy[o==k],int(u.sum())

def contact(pitch=1.):
    c=centers(np.arange(8),1,0,pitch);out={}
    for k in (1,6,7):
        out[str(k)]=float(min(sdf(SURFACE+c[0]-c[k]).min(),sdf(SURFACE+c[k]-c[0]).min()))
    return out
