"""Targeted smooth centerline interventions; fixed shape and count controls."""
import time
from copy import deepcopy
import numpy as np
from scipy.optimize import minimize
from photo2.r297.common import ROOT,save,read
from photo2.r306.evidence import load
from photo2.r314.geometry import contacts
from photo2.r295.geometry import AXES
from .packing import parameters,derive,planes,curvature
from .model import corrected,Chain
OUT=ROOT/'photo2/r321/results'

def solve(p,data,label,free_axial=False):
 began=time.perf_counter();initial,z=derive(p,data);g,n,aa,bb=planes(initial,(6,7),140)
 # Fix physical pairs/planes for cheap nonlinear support inequalities. Verify
 # every spatial pair after solving; a fixed plane stays a sufficient witness.
 select=np.flatnonzero(g<.25*p['radius']);a=aa[select];b=bb[select];normal=n[select]
 worst=int(np.argmin(g));u=initial.inverse((initial.a0+initial.direction*initial.station([initial.indices[aa[worst]]])[0])%initial.length)/initial.inverse(initial.length)
 center=int(round(u*32))%32;knots=[(center+i)%32 for i in [-2,-1,0,1,2]];history=[];cache={}
 def calc(x):
  key=tuple(x)
  if key in cache:return cache[key]
  q=deepcopy(p);co=np.zeros(32);co[knots]=x[:5];q=corrected(q,co)
  if free_axial:q['axial']=x[5]
  # Max-norm B-spline is bounded by the maximum coefficient: convex weights.
  s,z=derive(q,data)
  from photo2.r320.audit import support
  delta=s.centers[b]-s.centers[a];gap=np.sum(delta*normal,axis=1)-support(normal,s.g[AXES[0]][a],s.radius,s.axial)-support(normal,s.g[AXES[0]][b],s.radius,s.axial)
  result=(s,z,gap);cache[key]=result
  history.append(dict(coefficients=co.tolist(),axial=q['axial'],minimum_fixed_plane=float(gap.min()),summary=s.summary()))
  return result
 x=np.zeros(6 if free_axial else 5)
 if free_axial:x[-1]=p['axial']
 def objective(x):
  s,z,gap=calc(x)
  if free_axial:return -x[-1]+.00005*sum(x[:5]**2)
  return .001*sum(x*x)+sum(np.minimum(gap-1e-4,0)**2)*100
 if free_axial:
  constraints=[{'type':'ineq','fun':lambda x:calc(x)[2]-1e-4}]
 else:constraints=[]
 result=minimize(objective,x,method='SLSQP',bounds=[(-3.3468,3.3468)]*5+([(.55,1.05)] if free_axial else []),constraints=constraints,options={'maxiter':24,'ftol':1e-8,'eps':1e-3})
 s,z,gap=calc(result.x);c=contacts(s,seconds=2.);c.pop('witnesses',None)
 out=dict(label=label,knots=knots,free_axial=free_axial,initial_parameters=p,parameters=s.p,construction=z,initial_summary=initial.summary(),summary=s.summary(),optimizer_success=bool(result.success),message=result.message,history=history,contact=c,seconds=time.perf_counter()-began,initial_curvature_max=float(abs(curvature(initial)).max()),final_curvature_max=float(abs(curvature(s)).max()))
 save(OUT/f'centerline-{label}.json.gz',out);print('CENTERLINE',label,result.success,c['classification'],s.axial,s.summary()['axis_correction_px'],out['initial_curvature_max'],out['final_curvature_max'],len(history),out['seconds'],flush=True)
 return out

def main():
 data=load()[0]
 for h in [-1,1]:
  p=parameters(2800,1.95,.85,h)
  solve(p,data,f'fixed-h{h}')
  solve(p,data,f'thickness-h{h}',True)
if __name__=='__main__':main()
