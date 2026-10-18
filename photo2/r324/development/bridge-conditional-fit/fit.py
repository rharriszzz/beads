"""Bounded native graph-conditioned experiment, with separately reported gates."""
import time,copy,json,resource
from collections import Counter
import numpy as np
from scipy.optimize import minimize
from .coupled import *
import photo2.r319.evidence as evidence_module

def main():
 start=time.perf_counter();deadline=start+180;data=load()[0];g=read(OUT/'graph.json');doc=read(OUT/'R321-photo-sized-rescue-frozen.json.gz');seed=doc['seed_options'][0];p=doc['parameters'];evdoc=read(OUT/'fit-evidence.json');allobs={o['id']:o for o in g['observations']};nodes={n['id']:n for n in g['intersections']};pixels={r['id']:np.array(r['pixels_xy']) for r in read(OUT/'observation-pixels.json')}
 ci=nodes[next(iter(seed['mapping']))]['component'];component=[n for n in nodes.values() if n['component']==ci];mapping={n['id']:int(seed['origin']+np.dot(n['relative_ab'],seed['weights'])) for n in component}
 evidence_module.OUT=OUT;legacy=evidence_module.Evidence(read(ROOT/'photo2/r318/results/epoch2/epoch.json'))
 records=[];cache={};hits=0;misses=0
 scopes={100:list(range(-99,1)),200:list(range(-149,51))}
 def evaluate(q,scope,stage,meta=None,construct=True):
  nonlocal hits,misses
  t=time.perf_counter();rec=dict(id=len(records),stage=stage,scope=scope,requested_parameters=q,meta=meta or {})
  selected=[allobs[n['id']] for n in component if mapping[n['id']] in scopes[scope]];refs=[r for r in evdoc['reflections'] if r['observation'] in {o['id'] for o in selected}];key=digest(dict(parameters=q,scope=scope,observations=[o['id'] for o in selected],mapping=mapping));cached=key in cache
  if cached:rec.update(copy.deepcopy(cache[key]));hits+=1
  else:
   misses+=1
   try:
    s,z=derive(q,data) if construct else (R321(q,data),dict(seconds=0.,frozen=True))
    if s is None:rec.update(feasible=False,construction=z)
    else:
     rec['parameters']=s.p;rec['construction']=z;cert=contacts(s,seconds=.5)
     if not cert['certified']:rec.update(feasible=False,contact=cert)
     else:
      native,raster=optical(s,scopes[scope],refs,mapping,scope,certificate=cert);rows,frac,rays=support_ledger(s,selected,pixels);assigned=[]
      for i,o in enumerate(selected):
       j=int(np.flatnonzero(s.indices==mapping[o['id']])[0]);assigned.append(dict(id=o['id'],index=mapping[o['id']],fraction=float(frac[i,j]),color=o['color'],projected_center=s.pc[j].tolist(),xy=o['xy']))
      geometry=legacy.measure(s);rec.update(feasible=native['feasible'],native={k:v for k,v in native.items() if k!='predictions'},geometry=geometry,support=assigned,mean_assigned_support=float(np.mean([r['fraction'] for r in assigned])),support_rays=rays)
      if stage in ['baseline100','baseline200','final100','final200']:np.savez_compressed(OUT/f'{stage}-raster.npz',**raster);rec['predictions']=native['predictions']
   except (ValueError,AssertionError,FloatingPointError) as ex:rec.update(feasible=False,error=str(ex))
   cache[key]={k:copy.deepcopy(v) for k,v in rec.items() if k not in ['id','stage','scope','requested_parameters','meta']}
  rec['cached']=cached;rec['seconds']=time.perf_counter()-t;records.append(rec);save(OUT/'fit-trials'/f'{rec["id"]:04}.json.gz',rec)
  return rec
 def acceptance(r,b):
  fail=[]
  if not r.get('feasible'):return ['physical or numerical failure']
  if r['native']['missing']:fail.append('missing reflection')
  if r['mean_assigned_support']<b['mean_assigned_support']-.01:fail.append('mean assigned support loss')
  for a,z in zip(r['support'],b['support']):
   if a['fraction']<z['fraction']-.1:fail.append('individual support:'+a['id'])
  fail+=evidence_module.gate(r['geometry'],b['geometry'])['failures']
  return fail
 def objective(r):
  return r['native']['emax_px'] if r.get('feasible') and r['native']['emax_px'] is not None else float('inf')
 baseline=evaluate(p,100,'baseline100',construct=False);assert baseline.get('feasible')
 parent=baseline;vs=[('phase',.04),('s0',.8),('radius',.02),('axial',.02),('axis0',.5),('axis31',.5)]
 def changed(p,key,step):
  q=copy.deepcopy(p)
  if key.startswith('axis'):
   c=np.array(q['axis_bspline']);c[int(key[4:])]+=step;q=corrected(q,c)
  else:q[key]+=step
  return q
 jacobians=[]
 for epoch in range(2):
  pp=parent['parameters'];pr=np.array([r['predicted'] for r in parent['native']['rows']]);observed=np.array([r['observed'] for r in parent['native']['rows']]);columns=[];active=[];probes=[];jt=time.perf_counter()
  for key,step in vs:
   rr=[evaluate(changed(pp,key,sign*step),100,'sensitivity',dict(epoch=epoch,key=key,sign=sign,step=step)) for sign in [-1,1]]
   probes+=rr
   if all(r.get('feasible') and r['native']['missing']==0 for r in rr):
    minus,plus=[np.array([a['predicted'] for a in r['native']['rows']]) for r in rr];columns.append((plus-minus)/2);active.append((key,step))
  record=dict(epoch=epoch,parent=parent['id'],probes=[r['id'] for r in probes],seconds=time.perf_counter()-jt,variables=active)
  if columns:
   J=np.stack(columns,axis=2);residual=pr-observed;record.update(jacobian=J.tolist(),residual=residual.tolist(),singular_values=np.linalg.svd(J.reshape(-1,J.shape[-1]),compute_uv=False).tolist());candidates=[]
   for trust in [.5,1.]:
    sol=minimize(lambda x:x[-1],np.r_[np.zeros(len(active)),np.linalg.norm(residual,axis=1).max()],method='SLSQP',bounds=[(-trust,trust)]*len(active)+[(0,None)],constraints=[dict(type='ineq',fun=lambda x:x[-1]-np.linalg.norm(residual+np.einsum('ijk,k->ij',J,x[:-1]),axis=1))],options=dict(maxiter=100,ftol=1e-7))
    q=copy.deepcopy(pp)
    for (key,step),d in zip(active,sol.x[:-1]):q=changed(q,key,step*d)
    r=evaluate(q,100,'joint-step',dict(epoch=epoch,trust=trust,predicted_max=float(sol.x[-1]),scaled_step=sol.x[:-1].tolist(),solver_success=bool(sol.success)));candidates.append(r)
   record['candidates']=[r['id'] for r in candidates]
  jacobians.append(record)
  eligible=[r for r in records if r['scope']==100 and not acceptance(r,baseline)]
  parent=min(eligible,key=objective) if eligible else baseline
  if time.perf_counter()>deadline:break
 # Count and packing-law controls retain the map: these are family comparisons,
 # not free correspondence rematches or evidence for even N.
 for count in [2799,2801,2700,2900]:
  q=copy.deepcopy(p);q['count']=count;q['winding']=int(np.floor(count/6.5+.5));q['turn']=count/q['winding'];evaluate(q,100,'count-control',dict(count=count))
 q=copy.deepcopy(p);q['packing_spacing']='uniform';evaluate(q,100,'uniform-spacing-control')
 b200=evaluate(p,200,'baseline200',construct=False)
 # Explicit final evaluations have separate raster writes; no cache substitution.
 cache.clear();final=evaluate(parent['parameters'],100,'final100',construct=False);f200=evaluate(parent['parameters'],200,'final200',construct=False)
 for r in records:
  b=baseline if r['scope']==100 else b200;r['gate_failures']=acceptance(r,b);r['accepted_nonregression']=not r['gate_failures'];save(OUT/'fit-trials'/f'{r["id"]:04}.json.gz',r)
 feasible=[r for r in records if r['scope']==100 and r.get('feasible')];trade=min(feasible,key=objective)
 # Discrete remapping reuses exact saved native predictions; no ray retracing.
 rt=time.perf_counter();pred={int(k):v for k,v in final['predictions'].items()};remaps=[]
 for off in [-7,-6,-1,0,1,6,7]:
  vals=[];missing=0
  for r in final['native']['rows']:
   h=pred.get(r['index']+off)
   if h:vals.append(float(np.linalg.norm(np.array(h['point'])-r['observed'])))
   else:missing+=1
  remaps.append(dict(offset=off,missing=missing,maximum_is_infinite=bool(missing),emax_px=max(vals) if vals and not missing else None,geometry_changed=False))
 save(OUT/'correspondence-control.json',dict(seconds=time.perf_counter()-rt,controls=remaps,camera_cache_hits=7,camera_cache_misses=0,policy='Fixed geometry, target pool -99..0. Predictions outside pool unavailable. No assignment gain counted as geometry.'))
 summary=dict(seconds=time.perf_counter()-start,trials=len(records),baseline100=baseline['id'],baseline200=b200['id'],selected=parent['id'],final100=final['id'],final200=f200['id'],reflection_tradeoff=trade['id'],jacobians=jacobians,cache_hits=hits,cache_misses=misses,peak_rss_mb=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,photo_graph_changed=False,physical_rules='Closed chain; derived minor radius; no local phase/spacing/tilt or bead translations; fixed light/camera; full-chain contact and visibility',selection='Reflection minimax under explicit support and geometry nonregression gates; no scalar mixture of objectives',baseline_emax=objective(baseline),final_emax=objective(final),baseline_mean_support=baseline['mean_assigned_support'],final_mean_support=final['mean_assigned_support'],expanded_gate_failures=acceptance(f200,b200))
 save(OUT/'fit-summary.json',summary);print('FIT',summary['trials'],summary['baseline_emax'],summary['final_emax'],summary['baseline_mean_support'],summary['final_mean_support'],summary['expanded_gate_failures'],flush=True)
if __name__=='__main__':main()
