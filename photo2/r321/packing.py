"""Rounded-annular support constraints, straight contact reference and closed law.

The support is exact for glass but equals the convex hull's support. Positive
planes prove separation; negative optimized planes alone do not prove collision.
"""
import time
from copy import deepcopy
import numpy as np
from scipy.optimize import minimize_scalar, root, brentq
from .model import Chain, parameters, corrected
from photo2.r320.audit import support
from photo2.r295.geometry import AXES

OFFSETS=(1,6,7)
MARGIN=2e-5

def straight_gaps(T,a,R,P,r=1.,details=False):
    """Symmetry-reduced exact support maximization in pair mid-plane.

    R,P,r in the same units. Reflection in the midpoint radial plane exchanges
    the two centrally symmetric convex hulls. A maximizing separator can be
    chosen in its orthogonal tangent/circumferential plane by symmetrization.
    """
    alpha=-np.arctan(P/(2*np.pi*R));out=[]
    for d in OFFSETS:
        theta=np.pi*d/T;delta=np.array([d*P/T,2*R*np.sin(theta),0.])
        ta=np.array([np.cos(alpha),np.sin(alpha)*np.cos(theta),np.sin(alpha)*np.sin(theta)])
        def gap(beta):
            beta=np.asarray(beta);n=np.stack([np.cos(beta),np.sin(beta),np.zeros_like(beta)],axis=-1)
            return n@delta-2*support(n,ta,r,a)
        mesh=np.linspace(-np.pi,np.pi,129);v=gap(mesh);j=int(np.argmax(v));step=2*np.pi/128
        sol=minimize_scalar(lambda x:-float(gap(x)),bounds=(mesh[j]-step,mesh[j]+step),method='bounded',options={'xatol':1e-12})
        out.append(dict(offset=d,gap=float(-sol.fun),normal=[float(np.cos(sol.x)),float(np.sin(sol.x)),0.],theta=float(theta)))
    return out if details else np.array([z['gap'] for z in out])

def straight_reference(T,a):
    """Two active contact branches, minimum feasible P within local roots.

    Not a global density optimum. T and a determine dimensionless R/r,P/r.
    A positive numerical margin is added by the closed construction.
    """
    began=time.perf_counter();R0=1/np.sin(np.pi/T);branches=[]
    for j in (1,2):
        sol=root(lambda x:straight_gaps(T,a,*x)[[0,j]], [R0,1.4*a*1.04],tol=1e-9)
        g=straight_gaps(T,a,*sol.x)
        branches.append(dict(active=[1,OFFSETS[j]],success=bool(sol.success),R_over_r=float(sol.x[0]),P_over_r=float(sol.x[1]),gaps_over_r=g.tolist(),feasible=bool(sol.success and min(g)>-1e-7)))
    good=[b for b in branches if b['feasible'] and .8*R0<b['R_over_r']<1.2*R0 and b['P_over_r']>0]
    return dict(T=T,axial=a,branches=branches,best=min(good,key=lambda z:z['P_over_r']) if good else None,seconds=time.perf_counter()-began)

def derive(p,data):
    """Closed P=L/W; R follows straight +1 contact, never photographic fitting.

    If no local radius root exists, the construction is unresolved. The full
    curved chain must still pass actual support/solid checks before rendering.
    """
    start=time.perf_counter();q=deepcopy(p);base=Chain(q,data);P=base.length/q['winding'];r=q['radius'];T=q['turn'];R0=r/np.sin(np.pi/T)
    t=time.perf_counter()
    theta=np.pi/T;sn=np.sin(theta);cs=np.cos(theta);target=2*r+MARGIN*r
    A=P*P*cs/(2*np.pi*T);B=(P*cs/(2*np.pi))**2
    coefficients=[4*sn*sn,4*sn*A-target*target,A*A-target*target*B]
    roots=np.roots(coefficients);valid=[float(x.real) for x in roots if abs(x.imag)<1e-10 and x.real>0]
    if not valid:return None,dict(classification='unresolved-radius-root',seconds=time.perf_counter()-start)
    R=np.sqrt(max(valid))
    if not .85*R0<R<1.15*R0:return None,dict(classification='unresolved-radius-branch',seconds=time.perf_counter()-start)
    q['minor']=float(R);sg=straight_gaps(T,q['axial'],R,P,r,True);algebra=time.perf_counter()-t
    s=Chain(q,data)
    return s,dict(classification='pending-curved-certification',straight=sg,algebra_seconds=algebra,geometry_seconds=time.perf_counter()-start-algebra,seconds=time.perf_counter()-start,summary=s.summary())

def curvature(s):
    a=(s.a0+s.direction*s.station(s.indices))%s.length;u=s.inverse(a);v=s.spline(u,1);w=s.spline(u,2)
    return s.direction*(v[:,0]*w[:,1]-v[:,1]*w[:,0])/np.linalg.norm(v,axis=1)**3

def planes(s,offsets=OFFSETS,iterations=100):
    """Numerical plane directions, algebraically exact support values."""
    a=np.tile(np.arange(s.n),len(offsets));b=np.concatenate([(np.arange(s.n)+d)%s.n for d in offsets]);delta=s.centers[b]-s.centers[a]
    ta=s.g[AXES[0]][a];tb=s.g[AXES[0]][b];n=delta/np.linalg.norm(delta,axis=1)[:,None];step=np.full(len(n),.2)
    for _ in range(iterations):
        ha,ga=support(n,ta,s.radius,s.axial,True);hb,gb=support(n,tb,s.radius,s.axial,True);g=np.sum(n*delta,axis=1)-ha-hb
        grad=delta-ga-gb;grad-=np.sum(grad*n,axis=1)[:,None]*n;nn=n+step[:,None]*grad;nn/=np.linalg.norm(nn,axis=1)[:,None]
        ng=np.sum(nn*delta,axis=1)-support(nn,ta,s.radius,s.axial)-support(nn,tb,s.radius,s.axial);good=ng>g
        n[good]=nn[good];step[~good]*=.5;step[good]=np.minimum(.5,step[good]*1.1)
    return np.sum(n*delta,axis=1)-support(n,ta,s.radius,s.axial)-support(n,tb,s.radius,s.axial),n,a,b


def side_planes(s):
    """Five explicit plane candidates, each an exact sufficient inequality.

    Delta, projections perpendicular to either or mean hole axis, and cross
    axes. Choosing the largest gap is safe: ANY positive plane separates glass.
    No claim that this finite stencil finds the closest surfaces.
    """
    a=np.arange(s.n);b=(a+1)%s.n;delta=s.centers[b]-s.centers[a]
    ta=s.g[AXES[0]][a];tb=s.g[AXES[0]][b];mean=ta+tb;mean/=np.linalg.norm(mean,axis=1)[:,None]
    vectors=[delta]+[delta-np.sum(delta*t,axis=1)[:,None]*t for t in [ta,tb,mean]]+[np.cross(ta,tb)]
    gs=[];ns=[]
    for n in vectors:
        length=np.linalg.norm(n,axis=1);tiny=length<1e-10;n=n.copy();n[tiny]=delta[tiny]
        n/=np.linalg.norm(n,axis=1)[:,None];n*=np.where(np.sum(n*delta,axis=1)<0,-1,1)[:,None]
        gs.append(np.sum(n*delta,axis=1)-support(n,ta,s.radius,s.axial)-support(n,tb,s.radius,s.axial));ns.append(n)
    gs=np.array(gs);ns=np.array(ns);j=np.argmax(gs,axis=0);return gs[j,a],ns[j,a],a,b

straight_derive=derive

def derive(p,data):
    """Curvature-aware +1 contact envelope; no photograph objective in R."""
    start=time.perf_counter();s,z=straight_derive(p,data)
    if s is None:return s,z
    t=time.perf_counter();history=[]
    # Secant correction of the worst +1 support constraint. A fresh nonlinear
    # check is mandatory; no monotonicity or global minimum is asserted.
    for iteration in range(5):
        g,n,aa,bb=side_planes(s);j=int(np.argmin(g));low=float(g[j]);history.append(dict(minor=s.p['minor'],minimum_plus1_plane=low,pair=[int(s.indices[aa[j]]),int(s.indices[bb[j]])]))
        if low>=MARGIN*s.radius*.95:break
        q=deepcopy(s.p);dr=1e-3*s.radius;q['minor']+=dr;test=Chain(q,data)
        delta=test.centers[bb[j]]-test.centers[aa[j]];nn=n[j]
        new=float(delta@nn-support(nn,test.g[AXES[0]][aa[j]],s.radius,s.axial)-support(nn,test.g[AXES[0]][bb[j]],s.radius,s.axial));derivative=(new-low)/dr
        if derivative<=0:break
        q['minor']=s.p['minor']+(MARGIN*s.radius-low)/derivative+1e-6*s.radius;s=Chain(q,data)
    z.update(curvature_construction_seconds=time.perf_counter()-t,curvature_history=history,summary=s.summary(),seconds=time.perf_counter()-start)
    return s,z
