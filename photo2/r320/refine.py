"""Small coupled minimax probes with derived packing and bounded centerline."""
import itertools,time
from copy import deepcopy
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from photo2.r297.common import ROOT,read,save,utc
from photo2.r306.evidence import load
from .model import derive,corrected,D
from .evaluate import Evidence,evaluate
OUT=ROOT/'photo2/r320/results'
SCALES=np.array([.02,.02,.03,.5,.5,.5,.5,.5])
def vector(p):return np.r_[p['radius'],p['axial'],p['phase'],p['s0'],p.get('axis_harmonics',[0]*4)]
def change(p,x):
 q=deepcopy(p);q.update(radius=float(x[0]),axial=float(x[1]),phase=float(x[2]),s0=float(x[3]));return corrected(q,x[4:])
def main():
 data=load()[0];ev=Evidence(data);old=[read(f) for f in (OUT/'optical-trials').glob('*.gz')];rows=[];start=time.perf_counter()
 chosen=[]
 for n in [2800,2600,2200]:
  good=[r for r in old if r['family'][0]==n and r.get('optical',{}).get('emax_px') is not None]
  chosen.append(min(good,key=lambda r:r['optical']['emax_px']))
 def trial(p,family,kind,meta=None):
  s,z=derive(p,data);r=dict(id=len(rows),kind=kind,family=family,parameters=s.p,packing=z,meta=meta or {})
  if z['certified']:
   ep=read(OUT/f'epoch-N{family[0]}-h{family[1]}.json.gz');o,_,_=evaluate(s.p,data,ev,'pilot',ev.obs,ep['mapping']);r['optical']=o
  rows.append(r);save(OUT/'coupled-trials'/f'{r["id"]:04}.json.gz',r);return r
 matrices=[]
 for parent in chosen:
  family=parent['family'];base=trial(parent['parameters'],family,'parent',dict(optical_trial=parent['id']))
  for iteration in range(2):
   p=base['parameters'];x=vector(p);y=np.array([r['predicted'] for r in base['optical']['rows']]);obs=np.array([r['observed'] for r in base['optical']['rows']]);columns=[];ids=[];probeids=[]
   for j,scale in enumerate(SCALES):
    tests=[]
    for sign in [-1,1]:
     xx=x.copy();xx[j]+=sign*scale
     if abs(xx[3])>.1*D:tests.append(None);continue
     try:r=trial(change(p,xx),family,'bilateral',dict(parent=base['id'],coordinate=j,step=float(sign*scale)))
     except ValueError:tests.append(None);continue
     tests.append(r);probeids.append(r['id'])
    good=[r is not None and r.get('optical',{}).get('emax_px') is not None for r in tests]
    if all(good):col=(np.array([r['predicted'] for r in tests[1]['optical']['rows']])-np.array([r['predicted'] for r in tests[0]['optical']['rows']]))/2
    elif good[1]:col=np.array([r['predicted'] for r in tests[1]['optical']['rows']])-y
    elif good[0]:col=y-np.array([r['predicted'] for r in tests[0]['optical']['rows']])
    else:continue
    columns.append(col);ids.append(j)
   if not columns:break
   J=np.stack(columns,axis=2);residual=y-obs;sv=np.linalg.svd(J.reshape(-1,len(ids)),compute_uv=False);attempts=[]
   for trust in [.5,1.,2.]:
    bounds=[]
    for j in ids:
     lo,hi=-trust,trust
     if j==3:lo=max(lo,(-.1*D-x[j])/SCALES[j]);hi=min(hi,(.1*D-x[j])/SCALES[j])
     bounds.append((lo,hi))
    def constraints(v):return v[-1]-np.linalg.norm(residual+np.einsum('ijk,k->ij',J,v[:-1]),axis=1)
    sol=minimize(lambda v:v[-1],np.r_[np.zeros(len(ids)),base['optical']['emax_px']],bounds=bounds+[(0,None)],constraints=[dict(type='ineq',fun=constraints)],method='SLSQP',options=dict(maxiter=100,ftol=1e-8))
    xx=x.copy();xx[ids]+=SCALES[ids]*sol.x[:-1]
    try:r=trial(change(p,xx),family,'coupled-minimax',dict(parent=base['id'],iteration=iteration,trust=trust,predicted_emax=float(sol.x[-1]),solver_success=bool(sol.success)))
    except ValueError as ex:attempts.append(dict(trust=trust,rejected=str(ex)));continue
    attempts.append(dict(trust=trust,trial=r['id']));
   matrices.append(dict(family=family,parent=base['id'],coordinates=ids,scales=SCALES.tolist(),jacobian=J.tolist(),singular_values=sv.tolist(),probe_trials=probeids,attempts=attempts))
   good=[r for r in rows if r['family']==family and r.get('optical',{}).get('emax_px') is not None and (not parent['packing']['eligible'] or r['packing']['eligible'])]
   # This is a diagnostic minimax continuation. Every geometric contradiction
   # is reported separately; improvement is not adoption or absolute readiness.
   nextbase=min(good,key=lambda r:r['optical']['emax_px'])
   if nextbase['optical']['emax_px']>=base['optical']['emax_px']-1e-5:break
   base=nextbase
 save(OUT/'coupled-summary.json',dict(utc=utc(),seconds=time.perf_counter()-start,trials=len(rows),parents=[r['id'] for r in chosen],matrices=matrices))
 print('COUPLED COMPLETE',len(rows),time.perf_counter()-start,flush=True)
if __name__=='__main__':main()
