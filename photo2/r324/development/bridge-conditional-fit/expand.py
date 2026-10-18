"""One bounded 200-address joint step, preserving the 100-address photo cohort."""
from .coupled import *
import photo2.r319.evidence as evidence_module
from scipy.optimize import minimize

def main():
 start=time.perf_counter();data=load()[0];g=read(OUT/'graph.json');old=read(OUT/'fit-summary.json');parent=read(OUT/f'fit-trials/{old["final200"]:04}.json.gz');original=read(OUT/f'fit-trials/{old["baseline200"]:04}.json.gz');evdoc=read(OUT/'fit-evidence.json');pixels={r['id']:np.array(r['pixels_xy']) for r in read(OUT/'observation-pixels.json')};lookup={o['id']:o for o in g['observations']};selected=[lookup[r['id']] for r in parent['support']];mapping={r['id']:r['index'] for r in parent['support']};refs=[r for r in evdoc['reflections'] if r['observation'] in mapping];targets=list(range(-149,51));records=[]
 evidence_module.OUT=OUT;legacy=evidence_module.Evidence(read(ROOT/'photo2/r318/results/epoch2/epoch.json'))
 def trial(p,stage,meta):
  began=time.perf_counter();r=dict(id=len(records),stage=stage,meta=meta,requested_parameters=p);s,z=derive(p,data);r['construction']=z
  if s is None:r['feasible']=False
  else:
   r['parameters']=s.p;native,raster=optical(s,targets,refs,mapping,200);r['native']={k:v for k,v in native.items() if k!='predictions'};r['feasible']=native['feasible']
   if r['feasible']:
    rr,frac,_=support_ledger(s,selected,pixels);support=[dict(id=o['id'],index=mapping[o['id']],fraction=float(frac[i,int(np.flatnonzero(s.indices==mapping[o['id']])[0])])) for i,o in enumerate(selected)];r['support']=support;r['geometry']=legacy.measure(s);r['mean_assigned_support']=float(np.mean([v['fraction'] for v in support]));fail=evidence_module.gate(r['geometry'],original['geometry'])['failures']
    if r['mean_assigned_support']<original['mean_assigned_support']-.01:fail.append('mean support')
    for a,b in zip(support,original['support']):
     if a['fraction']<b['fraction']-.1:fail.append('support:'+a['id'])
    if native['missing']:fail.append('missing reflection')
    if native.get('emax_px') is None or native['emax_px']>original['native']['emax_px']:fail.append('200 reflection max regression')
    small=[v['error_px'] for v in native['rows'] if -99<=v['index']<=0];oldsmall=read(OUT/f'fit-trials/{old["baseline100"]:04}.json.gz')['native']['emax_px']
    if any(v is None for v in small) or max(small)>oldsmall:fail.append('100 reflection max regression')
    r['gate_failures']=fail
    if stage=='joint':np.savez_compressed(OUT/f'expand-{r["id"]}-raster.npz',**raster)
  r['seconds']=time.perf_counter()-began;records.append(r);save(OUT/'expand-trials'/f'{r["id"]:04}.json.gz',r);return r
 p=parent['parameters'];vs=[('phase',.04),('s0',.8),('radius',.02),('axial',.02),('axis0',.5),('axis31',.5)]
 def change(p,k,d):
  q=copy.deepcopy(p)
  if k.startswith('axis'):
   c=np.array(q['axis_bspline']);c[int(k[4:])]+=d;return corrected(q,c)
  q[k]+=d;return q
 cols=[];keys=[];jt=time.perf_counter()
 for k,h in vs:
  a,b=[trial(change(p,k,h*sg),'sensitivity',dict(variable=k,sign=sg,step=h)) for sg in [-1,1]]
  if all(r.get('feasible') and r['native']['missing']==0 for r in [a,b]):cols.append((np.array([r['predicted'] for r in b['native']['rows']])-np.array([r['predicted'] for r in a['native']['rows']]))/2);keys.append((k,h))
 jtime=time.perf_counter()-jt;J=np.stack(cols,axis=2);res=np.array([np.array(r['predicted'])-r['observed'] for r in parent['native']['rows']]);candidates=[]
 for trust in [.5,1.]:
  sol=minimize(lambda x:x[-1],np.r_[np.zeros(len(keys)),np.linalg.norm(res,axis=1).max()],method='SLSQP',bounds=[(-trust,trust)]*len(keys)+[(0,None)],constraints=[dict(type='ineq',fun=lambda x:x[-1]-np.linalg.norm(res+np.einsum('ijk,k->ij',J,x[:-1]),axis=1))],options=dict(maxiter=100,ftol=1e-7));q=copy.deepcopy(p)
  for (k,h),x in zip(keys,sol.x[:-1]):q=change(q,k,h*x)
  candidates.append(trial(q,'joint',dict(trust=trust,predicted_max=float(sol.x[-1]),scaled_step=sol.x[:-1].tolist())))
 good=[r for r in records if r.get('feasible') and not r.get('gate_failures',['unavailable'])];best=min(good,key=lambda r:r['native']['emax_px']) if good else None
 save(OUT/'expand-summary.json',dict(seconds=time.perf_counter()-start,trials=len(records),jacobian_seconds=jtime,jacobian=J.tolist(),variables=keys,baseline_emax=original['native']['emax_px'],best=best['id'] if best else None,best_emax=best['native']['emax_px'] if best else None,candidates=[dict(id=r['id'],emax=r.get('native',{}).get('emax_px'),failures=r.get('gate_failures')) for r in candidates],note='One 200-address epoch. All 2800 physical bodies; same graph-derived map; no rematching.'))
 print('EXPAND',len(records),best['native']['emax_px'] if best else None,flush=True)
if __name__=='__main__':main()
