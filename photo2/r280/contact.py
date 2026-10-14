"""Sufficient nonintersection witnesses for exact convex outer bead envelopes.

Filling an annulus's hole enlarges it. The filled rounded profile is a cylinder
(radius .656r, axial half-height .14r) Minkowski-summed with an ellipsoid
(radial radius .344r, axial radius .56r). Its support function is analytic.
A positive separating-plane gap proves the actual hole-bearing beads disjoint.
Negative/unfinished searches do NOT prove an intersection.
"""
import numpy as np
from scipy.spatial import cKDTree
def unit(v):
    v=np.asarray(v,float)
    return v/np.maximum(np.linalg.norm(v,axis=-1,keepdims=True),1e-30)


def support(n,t,r,gradient=False):
    a=np.sum(n*t,axis=-1);v=n-a[...,None]*t;q=np.linalg.norm(v,axis=-1)
    ell=np.sqrt((.344*r)**2*np.sum(n*n,axis=-1)+((.56*r)**2-(.344*r)**2)*a*a)
    h=.656*r*q+.14*r*abs(a)+ell
    if not gradient:return h
    g=.656*r*v/np.maximum(q[...,None],1e-15)+.14*r*np.sign(a)[...,None]*t
    g+=((.344*r)**2*n+((.56*r)**2-(.344*r)**2)*a[...,None]*t)/np.maximum(ell[...,None],1e-15)
    return h,g


def certificate(s,iterations=160):
    pairs=cKDTree(s.centers).query_pairs(2*s.bound+1e-8,output_type='ndarray')
    if not len(pairs):return dict(certified=True,pairs=0,witnesses=[])
    a,b=pairs.T;delta=s.centers[b]-s.centers[a];ta=s.g['surface_tangent'][a];tb=s.g['surface_tangent'][b]
    n=unit(delta);step=np.full(len(n),.25);best=np.full(len(n),-np.inf)
    for _ in range(iterations):
        ha,ga=support(n,ta,s.radius,True);hb,gb=support(n,tb,s.radius,True)
        gap=np.sum(delta*n,axis=1)-ha-hb;grad=delta-ga-gb;grad-=np.sum(grad*n,axis=1)[:,None]*n
        candidate=unit(n+step[:,None]*grad)
        nextgap=np.sum(delta*candidate,axis=1)-support(candidate,ta,s.radius)-support(candidate,tb,s.radius)
        good=nextgap>gap;n[good]=candidate[good];step[~good]*=.5;step[good]=np.minimum(.5,step[good]*1.1)
    gap=np.sum(delta*n,axis=1)-support(n,ta,s.radius)-support(n,tb,s.radius)
    # Explicit margin exceeds floating point roundoff by many orders here.
    ok=gap>1e-6
    return dict(certified=bool(ok.all()),pairs=len(pairs),separated_pairs=int(ok.sum()),unresolved_pairs=int((~ok).sum()),
                minimum_gap_units=float(gap.min()),required_margin_units=1e-6,
                method='Analytic support-function separating planes for convex filled outer envelopes; bounding spheres exclude all other pairs. Sufficient floating-point witnesses, not interval-arithmetic formal proof.',
                witnesses=[dict(pair=list(map(int,p)),normal=v.tolist(),gap_units=float(g),separated=bool(k)) for p,v,g,k in zip(pairs,n,gap,ok)])
