"""Second, mechanistically distinct control: phase variation within 2-3 revolutions.

The initial 45-address halfwidth still couples early neighbors to the reference.
Test 18-address halfwidth and explicitly declared 5% added phase-rate bound.
No other physical dimensions or per-bead changes; separate sealed trial epoch.
"""
from copy import deepcopy
import time
import numpy as np
from scipy.stats import qmc
from photo2.r297.common import ROOT,read,save
from photo2.r306.evidence import load
from photo2.r314.run import engine
from photo2.r314.geometry import contacts
from photo2.r314.diagnostics import EARLY
from photo2.r307.fast import grid
from .experiment import evaluate
from .model import refined_trace
from .diagnose import OUT,brackets

def main():
 data=load()[0];e=engine();base=read(OUT/'baseline-model.json.gz');p=deepcopy(base['parameters']);p.update(compact_centers=[-13,0,13],phase_halfwidth=18,spacing_halfwidth=35,compact_phase_rate_limit=.05,compact_phase=[0,0,0],compact_spacing=[0,0,0]);start=time.monotonic();rows=[];best=None
 def rank(r):
  if not r['feasible']:return (1e6,)
  z=r['development'];v=z['vector'];cs={c['id']:c['modal_fraction'] for c in z['cores']};bb=z['bracket_finite_p95'] or 0
  # Local hypothesis test, simultaneous core deficits; explicit global contradictions.
  violations=[(1-cs[k])/.2 for k in EARLY]+[v['paper']/.5,v['seam']/10,bb/3,v['omission']/5]
  return tuple(sorted(violations,reverse=True))+(-z['early_mean'],)
 def trial(q,label):
  nonlocal best
  try:r,s,tr=evaluate(q,data,e)
  except ValueError as ex:r=dict(parameters=q,feasible=False,classification='rate-bound',reason=str(ex))
  r.update(id=len(rows),experiment=label)
  if r['feasible'] and (best is None or rank(r)<rank(best)):best=deepcopy(r);print('NARROW',r['id'],rank(r),flush=True)
  if 'physical' in r:r['physical'].pop('witnesses',None)
  rows.append(r);save(OUT/'narrow-trials'/f'{r["id"]:04d}.json.gz',r)
 trial(p,'narrow-zero')
 for i in range(3):
  for a in [-.35,-.2,.2,.35]:
   q=deepcopy(p);q['compact_phase'][i]=a;trial(q,'narrow-phase-control')
 seed=deepcopy(best['parameters'])
 for i,v in enumerate(qmc.Sobol(8,scramble=True,seed=31518).random_base2(7)*2-1):
  if time.monotonic()-start>110:break
  q=deepcopy(seed if i<64 else best['parameters']);f=1 if i<64 else .3;q['compact_phase']=(np.array(q['compact_phase'])+v[:3]*.25*f).tolist();q['compact_spacing']=(np.array(q['compact_spacing'])+v[3:6]*.005*f).tolist();q['translation']=(np.array(q.get('translation',[0,0]))+v[6:]*3*f).tolist();trial(q,'narrow-coupled')
 r,s,tr=evaluate(best['parameters'],data,e);r.update(name='narrow',source_trial=best['id']);r['comparison']=e.measure(tr['owner'],tr['unknown'],s.indices,1,True);r['buffer']=e.measure(tr['owner'],tr['unknown'],s.indices,2,True);r['positions']=dict(indices=s.indices.tolist(),centers=s.centers.tolist(),frames={k:v.tolist() for k,v in s.g.items()},projected=s.pc.tolist());ix=np.flatnonzero((s.indices>=-100)&(s.indices<=99));xy=grid(s,1.,ix);full=refined_trace(s,xy);r['target']=dict(count=len(ix),rays=len(xy),unknown=int(full['unknown'].sum()));np.savez_compressed(OUT/'narrow-target.npz',xy=xy,owner=full['owner'],unknown=full['unknown']);np.savez_compressed(OUT/'narrow-raster.npz',owner=tr['owner'],unknown=tr['unknown']);save(OUT/'narrow-model.json.gz',r);save(OUT/'narrow-brackets.json.gz',brackets(e,tr));save(OUT/'narrow-experiment.json',dict(trials=len(rows),seconds=time.monotonic()-start,best=best['id'],feasible=sum(r['feasible'] for r in rows),classification_counts={k:sum(r['classification']==k for r in rows) for k in set(r['classification'] for r in rows)},rate_limit=.05,rank=rank(r),new_basis_halfwidth=18,policy='Exploratory 5% phase-rate bound is unmeasured; compared against unchanged baseline on fixed observations. Not a mechanical crochet solution.'))
if __name__=='__main__':main()
