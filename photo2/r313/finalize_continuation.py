"""Seal selected experimental models and independent diagnostics, no new proposals."""
from copy import deepcopy
from pathlib import Path
import time
import numpy as np
from photo2.r297.common import ROOT,read,save,sha,utc
from photo2.r306.evidence import load
from .objective_v2 import SurfaceObjective
from .diagnose_geometry import evaluate,make
from .physical_diagnosis import run as physical_diagnosis
from .geometry_experiment import contacts

OUT=ROOT/'photo2/r313/continuation'
def export(name,r,s,tr):
 from .objective_v2 import SurfaceObjective
 ev=OUT.parent/'evidence';eng=SurfaceObjective(dict(np.load(ev/'maps.npz')),read(ev/'freeze.json'));r['buffer']=eng.measure(tr['owner'],tr['unknown'],s.indices,2,True)
 r=dict(r,name=name,positions=dict(indices=s.indices.tolist(),centers=s.centers.tolist(),projected=s.pc.tolist(),frames={k:v.tolist() for k,v in s.g.items()}),cohort=list(range(-100,100)),cohort_positions=200)
 save(OUT/'models'/f'{name}.json.gz',r);np.savez_compressed(OUT/'models'/f'{name}.npz',owner=tr['owner'],unknown=tr['unknown'])
 return r

def main():
 began=time.monotonic();data,_,_=load();ev=OUT.parent/'evidence';eng=SurfaceObjective(dict(np.load(ev/'maps.npz')),read(ev/'freeze.json'));selection=read(OUT/'search-selection.json');assert selection['sealed'];models=[]
 # All original baselines and initial incumbents under the identical new objective.
 for oldpath in sorted((ROOT/'photo2/r313/results/models').glob('*.json.gz')):
  old=read(oldpath);r,s,tr=evaluate(old['parameters'],data,eng,old['implementation'],True)
  assert r['feasible'];r['original_source']=str(oldpath.relative_to(ROOT));models.append(export(old['name'],r,s,tr))
 for i,b in enumerate(selection['best']):
  r,s,tr=evaluate(b['parameters'],data,eng,b['implementation'],True,contact_seconds=3.);assert r['feasible'];r.update(parent=b['start'],trial=b['trial']);models.append(export(f'R313-focused-{i+1}',r,s,tr));print('export',i,b['start'],r['development']['score'],r['comparison']['score'],flush=True)
 # Any photographically promising unresolved proposal receives a larger actual-solid audit.
 trials=[read(p) for p in sorted((OUT/'trials').glob('*.gz'))];unresolved=sorted([r for r in trials if r['classification']=='unresolved' and 'photographic_score' in r],key=lambda r:r['photographic_score']);resolved=[]
 for r in unresolved[:3]:
  s=make(r['parameters'],data,r['implementation']);cert=contacts(s,seconds=8.);resolved.append(dict(trial=r['id'],photographic_score=r['photographic_score'],physical=cert))
 save(OUT/'unresolved-followup.json.gz',dict(unresolved_trials=len(unresolved),selected_checks=resolved,policy='Higher-budget actual hollow-solid checks, never automatic adoption or replacement of frozen selection.'))
 physical_diagnosis(models,OUT/'physical-diagnosis.json')
 summary=[]
 for r in models:
  for label in ['development','comparison']:
   q=r[label];summary.append(dict(name=r['name'],split=label,score=q['score'],legacy_score=q['legacy_score'],explained_percent=100-q['material_unexplained_percent'],paper_percent=q['background_intrusion_percent'],core_one_owner_percent=q['modal_ownership_percent'],seam_conflict_percent=q['seam_same_owner_percent'],transition_p95=q['supported_transition_alignment']['p95_px'],transition_max=q['supported_transition_alignment']['max_px'],owner_specific=q['owner_specific_terms'],explained_target=q['material_explained_by_200_pixels'],explained_context=q['material_explained_by_context_pixels']))
 save(OUT/'summary-table.json',summary)
 feasible=[r for r in trials if r['feasible']];profile={k:dict(total_seconds=float(sum(r.get('profile',{}).get(k,0) for r in trials)),median_feasible_seconds=float(np.median([r['profile'][k] for r in feasible]))) for k in ['geometry','contact','render','measure']}
 from collections import Counter
 save(OUT/'performance.json',dict(search_seconds=selection['seconds'],evaluations=len(trials),classifications=dict(Counter(r['classification'] for r in trials)),median_feasible_evaluation_seconds=float(np.median([r['seconds'] for r in feasible])),profile=profile,finalization_seconds=time.monotonic()-began,new_acceleration='Generalized existing native kernel without approximate predictions. No repeated profiling campaign.'))
 print('finalized',len(models),'models',time.monotonic()-began,flush=True)
if __name__=='__main__':main()
