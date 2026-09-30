"""Diagnostic planar-arc extension of the source bead surface; no image priors.

Parameters: tx,ty,pixels/unit,roll,elevation,azimuth,minor phase,curvature,q.
Curvature and q are local continuous parameters, not an estimate of photo N.
"""
import numpy as np
from local_surface_fit import frame, RADIUS

ROW = .65*2*RADIUS*1.05
INDICES = np.arange(-60, 48)
PRINCIPAL = np.array([1269.5, 1590.5])
NOMINAL_FOCAL = 4799.175227618243


def geometry(p, indices, hand):
    s = np.asarray(indices)*ROW/p[8]
    theta = p[7]*s
    # sinc form is stable at zero signed curvature.
    line = np.column_stack((s*np.sinc(theta/np.pi),
                            .5*p[7]*s*s*np.sinc(theta/(2*np.pi))**2,
                            np.zeros_like(s)))
    tangent = np.column_stack((np.cos(theta), np.sin(theta), np.zeros_like(s)))
    normal = np.column_stack((-np.sin(theta), np.cos(theta), np.zeros_like(s)))
    phase = np.radians(p[6]+hand*360*np.asarray(indices)/p[8])
    radial = np.sin(phase)[:, None]*normal
    radial[:, 2] = np.cos(phase)
    return line+4*radial, tangent, normal, line, line+(4+RADIUS)*radial


def project(p, xyz, focal=None):
    r,d,eye = frame(p[:7])
    numerator = np.column_stack((xyz@r, xyz@d))*p[2]+p[:2]
    if focal is None:
        return numerator
    return PRINCIPAL+(numerator-PRINCIPAL)/(1-p[2]*(xyz@eye)[:, None]/focal)


def rays(p, xy, focal=None):
    r,d,eye = frame(p[:7])
    base = (xy[:,0,None]-p[0])/p[2]*r+(xy[:,1,None]-p[1])/p[2]*d
    ray = np.broadcast_to(eye, base.shape).copy()
    if focal is not None:
        ray -= (xy[:,0,None]-PRINCIPAL[0])/focal*r+(xy[:,1,None]-PRINCIPAL[1])/focal*d
        ray /= np.linalg.norm(ray, axis=1)[:,None]
    return base,ray


def sdf(v):
    minor=.43*RADIUS; extra=.2*minor
    qr=np.abs(np.hypot(v[...,1],v[...,2])-.57*RADIUS)-extra
    qa=np.abs(v[...,0])/(.7/.43)-extra
    return np.hypot(np.maximum(qr,0),np.maximum(qa,0))+np.minimum(np.maximum(qr,qa),0)-.8*minor


def trace(p, xy, hand, indices=INDICES, focal=None, targets=None, eps=1e-4):
    """Exact first-hit ownership; optionally return expected-body front depths.

    Marching tolerance is numerical, not measurement uncertainty. Grazing pairs
    still active at the iteration cap are counted, never treated as verified hits.
    """
    xy=np.asarray(xy); indices=np.asarray(indices)
    if len(xy)>2000:
        chunks=[trace(p,xy[i:i+2000],hand,indices,focal,
                      None if targets is None else targets[i:i+2000],eps)
                for i in range(0,len(xy),2000)]
        return (np.concatenate([v[0] for v in chunks]),
                np.concatenate([v[1] for v in chunks]),sum(v[2] for v in chunks),
                None if targets is None else np.concatenate([v[3] for v in chunks]))
    c,t,n,_,_=geometry(p,indices,hand)
    base,ray=rays(p,xy,focal)
    delta=base[:,None,:]-c[None,:,:]
    middle=-np.einsum('ijk,ik->ij',delta,ray)
    perp2=np.sum(delta*delta,axis=2)-middle*middle
    bound=RADIUS*np.sqrt(1+.7**2)
    a,b=np.where(perp2<bound**2)
    best=np.full(len(xy),-np.inf); out=np.full(len(xy),-999,int)
    expected=np.full(len(xy),-np.inf) if targets is not None else None
    if not len(a):return out,best,0,expected
    half=np.sqrt(np.maximum(0,bound**2-perp2[a,b]))
    depth=middle[a,b]+half; end=middle[a,b]-half
    v=delta[a,b]; u=ray[a]
    local=np.column_stack((np.sum(v*t[b],axis=1),np.sum(v*n[b],axis=1),v[:,2]))
    direction=np.column_stack((np.sum(u*t[b],axis=1),np.sum(u*n[b],axis=1),u[:,2]))
    alive=np.ones(len(a),bool); hit=np.zeros(len(a),bool)
    for _ in range(400):
        active=np.flatnonzero(alive)
        if not len(active):break
        distance=sdf(local[active]+depth[active,None]*direction[active])
        reached=distance<eps
        hit[active[reached]]=True; alive[active[reached]]=False
        moving=active[~reached]
        depth[moving]-=np.maximum(distance[~reached],eps)
        alive[moving[depth[moving]<end[moving]]]=False
    np.maximum.at(best,a[hit],depth[hit])
    front=hit&(depth>=best[a]-eps/2)
    out[a[front]]=indices[b[front]]
    if targets is not None:
        desired=hit&(indices[b]==np.asarray(targets)[a])
        np.maximum.at(expected,a[desired],depth[desired])
    return out,best,int(alive.sum()),expected


def point_residual(p, xy, target, hand, focal=None):
    """Positive surface evidence only. SDF/depth guide misses; no background loss.

    Zero is awarded only to the independently checked first-hit ownership test.
    This guide is not a measured screen distance or calibrated likelihood.
    """
    owner,front,unfinished,expected=trace(p,xy,hand,focal=focal,targets=target)
    c,t,n,_,_=geometry(p,target,hand); base,ray=rays(p,xy,focal)
    delta=base-c; middle=-np.sum(delta*ray,axis=1)
    depths=middle[:,None]+np.linspace(-3,3,97)
    points=delta[:,None,:]+depths[:,:,None]*ray[:,None,:]
    local=np.stack((np.sum(points*t[:,None,:],axis=2),
                    np.sum(points*n[:,None,:],axis=2),points[:,:,2]),axis=2)
    miss=np.maximum(np.min(sdf(local),axis=1),0)*p[2]+.1
    occluded=np.isfinite(expected)
    miss[occluded]=np.maximum(front[occluded]-expected[occluded],0)*p[2]+.1
    miss[owner==target]=0
    return miss,owner,unfinished


def anchors(p, indices, hand, focal=None, model_indices=INDICES):
    *_,xyz=geometry(p,indices,hand)
    xy=project(p,xyz,focal)
    owner,front,unfinished,_=trace(p,xy,hand,indices=model_indices,focal=focal)
    base,ray=rays(p,xy,focal)
    depth=np.sum((xyz-base)*ray,axis=1)
    gap=front-depth
    exposed=(owner==indices)&(np.abs(gap)<.005)
    return xy,exposed,owner,gap,unfinished
