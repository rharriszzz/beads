"""Fixed-parent reflection diagnostics and before/after attribution, after selection."""
import time
import numpy as np
from copy import deepcopy
from photo2.r297.common import ROOT,read,save
from photo2.r306.evidence import load
from photo2.r297.geometry import reference
from photo2.r309.render import predict
from photo2.r312.objective import bottleneck,statistics
from .diagnose_geometry import make,evaluate
from .objective_v2 import SurfaceObjective

OUT=ROOT/'photo2/r313/continuation'
def main():
 began=time.monotonic();data,_,obs=load();ref=reference();local=[o for o in obs if o['strong'] and abs(((o['arc']-data['arc0'])*data['direction']+ref.length/2)%ref.length-ref.length/2)<=400]
 selected=read(OUT/'search-selection.json');parent_map={'shared-profile-R297':'R297-2337','initial-R312':'R312-best','R309':'R309-2733','trajectory-thin':'R306-2405'};parents={f'R313-focused-{i+1}':parent_map[r['start']] for i,r in enumerate(selected['best'][:2])};names=sorted(set(parents.values()))+list(parents);mappings={};out=[]
 for name in names:
  r=read(OUT/'models'/f'{name}.json.gz');s=make(r['parameters'],data,r['implementation']);owners=np.array(sorted({j for z in s.tree.query_ball_point([o['point'] for o in local],60.) for j in z}),int);pred,meta=predict(s,owners=owners);mapping=mappings[parents[name]] if name in parents else bottleneck(local,pred);mappings[name]=mapping;by={r['index']:r for r in pred};rows=[]
  for o in local:
   k=mapping[o['id']];p=by.get(k);rows.append(dict(id=o['id'],index=k,color=o['color'],observed=o['point'],predicted=p['point'] if p else None,error_px=float(np.linalg.norm(np.array(p['point'])-o['point'])) if p else None))
  out.append(dict(name=name,parent=parents.get(name),metrics=statistics(rows),rows=rows,numerics=meta,enters_selection=False));print('secondary reflection',name,statistics(rows),flush=True)
 save(OUT/'reflection-diagnostics.json',dict(models=out,observations=len(local),seconds=time.monotonic()-began,limitations='Inherited approximate lighting law, not a calibrated glass optical model. No light fit. Parent maps frozen for candidates; different parents have different conditional maps.'))
 # Shared shape/orientation versus placement interventions; no further candidate search.
 best=read(OUT/'models/R313-focused-1.json.gz');base=read(OUT/'models'/f'{parents["R313-focused-1"]}.json.gz');ev=OUT.parent/'evidence';eng=SurfaceObjective(dict(np.load(ev/'maps.npz')),read(ev/'freeze.json'));variants=[]
 for label,keys in [('revert_shared_profile',['hole','rounding','axial']),('revert_orientation',['tilt','trajectory_mix']),('revert_position_camera',['phase','s0','minor','scale','elevation','roll','yaw','local_spacing'])]:
  p=deepcopy(best['parameters'])
  for k in keys:
   if k in base['parameters']:p[k]=deepcopy(base['parameters'][k])
   elif k in ['hole','rounding','trajectory_mix']:p[k]={'hole':.14,'rounding':.8,'trajectory_mix':0.}[k]
  r,s,tr=evaluate(p,data,eng,best['implementation'],True,contact_seconds=1.);variants.append(dict(label=label,**r));print('attribution',label,r['physical']['classification'],r['development']['score'],flush=True)
 save(OUT/'attribution-controls.json.gz',dict(variants=variants,policy='Counterfactual groups from same selected model, no reranking. Infeasible combinations cannot establish a photographic causal preference. Changes interact; no unique cause inferred.'))
 # Conditional index changes are separately counted against each parent, not credited as identity recovery.
 ownership=[]
 for name,parent in parents.items():
  r=read(OUT/'models'/f'{name}.json.gz');b=read(OUT/'models'/f'{parent}.json.gz');rows=[]
  ra=sum([r[s]['cores'] for s in ['development','comparison','buffer']],[]);ba={z['id']:z for s in ['development','comparison','buffer'] for z in b[s]['cores']};ras=np.load(OUT/'models'/f'{name}.npz');m=dict(np.load(ev/'maps.npz'));doc=read(ev/'freeze.json');labels={v['id']:v['label'] for v in doc['regions']};indices=np.array(r['positions']['indices'])
  for a in ra:
   old=ba[a['id']];mask=m['core'].ravel()==labels[a['id']];k=old['index'];j=np.flatnonzero(indices==k) if k is not None else [];fixed=float(np.mean(ras['owner'][mask]==j[0])) if len(j) else 0.
   rows.append(dict(id=a['id'],old_index=k,new_index=a['index'],changed=k!=a['index'],old_fraction=old['modal_fraction'],new_modal_fraction=a['modal_fraction'],new_fixed_parent_fraction=fixed))
  ownership.append(dict(name=name,parent=parent,changed=sum(v['changed'] for v in rows),rows=rows))
 save(OUT/'ownership-changes.json',ownership)
if __name__=='__main__':main()
