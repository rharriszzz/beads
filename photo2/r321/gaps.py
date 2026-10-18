"""Tighter upper gaps using closest points on actual outer-side segments.

The literal legacy bead contains rho=r, |x|<=.14*r*axial. Optimizing two
segments gives explicit glass endpoints, not a convex-hull contact assertion.
"""
import numpy as np
from photo2.r295.geometry import AXES
from photo2.r320.audit import neighbor_gaps as initial_gaps

def neighbor_gaps(s):
 rows=initial_gaps(s)
 for row in rows:
  a=np.arange(s.n);b=(a+row['offset'])%s.n;n=np.array([p['normal'] for p in row['pairs']]);ta=s.g[AXES[0]][a];tb=s.g[AXES[0]][b]
  def radial(direction,indices,toward):
   v=np.stack([np.sum(direction*s.g[key][indices],axis=1) for key in AXES[1:]],axis=1);length=np.linalg.norm(v,axis=1);tiny=length<1e-8
   tv=np.stack([np.sum(toward*s.g[key][indices],axis=1) for key in AXES[1:]],axis=1);v[tiny]=tv[tiny];length=np.linalg.norm(v,axis=1);v[length<1e-10]=[1.,0.];v/=np.linalg.norm(v,axis=1)[:,None]
   return v[:,0,None]*s.g[AXES[1]][indices]+v[:,1,None]*s.g[AXES[2]][indices]
  delta_centers=s.centers[b]-s.centers[a];ra=radial(n,a,delta_centers);rb=radial(-n,b,-delta_centers)
  pa=s.radius*ra;pb=s.radius*rb;delta=s.centers[b]-s.centers[a]+pb-pa
  dot=np.sum(ta*tb,axis=1);da=np.sum(delta*ta,axis=1);db=np.sum(delta*tb,axis=1);limit=.14*s.radius*s.axial
  det=1-dot*dot;xx=(da-dot*db)/np.maximum(det,1e-30);yy=(dot*da-db)/np.maximum(det,1e-30)
  candidates=[(np.clip(xx,-limit,limit),np.clip(yy,-limit,limit))]
  for sign in [-1,1]:
   x=np.full(s.n,sign*limit);candidates.append((x,np.clip(dot*x-db,-limit,limit)))
   y=np.full(s.n,sign*limit);candidates.append((np.clip(da+dot*y,-limit,limit),y))
  values=np.array([np.linalg.norm(delta+y[:,None]*tb-x[:,None]*ta,axis=1) for x,y in candidates]);best=np.argmin(values,axis=0);ix=np.arange(s.n);side=values[best,ix];x=np.array([v[0] for v in candidates])[best,ix];y=np.array([v[1] for v in candidates])[best,ix]
  pts=[pa+x[:,None]*ta,pb+y[:,None]*tb];res=[]
  for q,j in zip(pts,[a,b]):res.append(abs(s.local_sdf(np.stack([np.sum(q*s.g[key][j],axis=1) for key in AXES],axis=1))))
  residual=float(np.max(res));assert residual<1e-8,residual
  lo=np.array([p['lower'] for p in row['pairs']]);old=np.array([p['upper'] for p in row['pairs']]);hi=np.minimum(old,side);assert np.all(hi+1e-8>=lo)
  for p,u,v in zip(row['pairs'],hi,old):p['initial_upper']=p['upper'];p['upper']=float(u);p['upper_method']='outer-side-segments' if u<v else 'support-endpoints'
  row.update(upper_median=float(np.median(hi)),upper_max=float(hi.max()),max_interval_width=float((hi-np.maximum(lo,0)).max()),near_contacts_upper_le_002r=int(np.sum(hi<=.02*s.radius)),small_gaps_upper_le_01r=int(np.sum(hi<=.1*s.radius)),side_segment_sdf_max=residual)
 return rows
