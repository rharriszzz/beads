"""Sequential measured stage costs; no pilot-concurrency timings used."""
import time,platform,csv
from copy import deepcopy
import numpy as np
from photo2.r297.common import ROOT,read,save,utc
from photo2.r306.evidence import load
from photo2.r314.geometry import contacts
from photo2.r320.model import parameters as old_parameters,derive as old_derive
from .packing import parameters,derive
from .evaluate import Evidence,evaluate
OUT=ROOT/'photo2/r321/results'

def main():
 data=load()[0];ev=Evidence(data);comparisons=[]
 inputs=[(2200,1.95,.85),(2600,1.95,.85),(2800,1.95,.85),(2800,1.95,.95),(3000,1.85,.85),(3000,1.95,.85),(3200,2.05,.85),(2801,1.95,.85)]
 for repeat in range(3):
  for n,r,a in inputs:
   row=dict(count=n,radius=r,axial=a,hand=-1,repeat=repeat)
   for label,make,build in [('R320',old_parameters,old_derive),('R321',parameters,derive)]:
    p=make(n,r,a);began=time.perf_counter();s,z=build(p,data);construct=time.perf_counter()-began;t=time.perf_counter();c=contacts(s,seconds=.5);cert=time.perf_counter()-t
    row[label]=dict(construction_seconds=construct,contact_seconds=cert,total_before_camera=construct+cert,classification=c['classification'],algebra_seconds=z.get('algebra_seconds'),geometry_seconds=z.get('geometry_seconds'),curvature_construction_seconds=z.get('curvature_construction_seconds'),minor=s.p['minor'],summary=s.summary())
   comparisons.append(row)
 native=[]
 selected=read(OUT/'selection.json')['models']
 # Exactly100/200/all targets, all bodies in visibility/shadows. All22 compact
 # observations retained even if mapped owners outside a target scope: missing
 # predictions remain unavailable, and scope timings are not quality claims.
 for model in selected:
  p=deepcopy(model['parameters']);mapping=read(OUT/f'epoch-N{p["count"]}-h{p["hand"]}.json.gz')['mapping']
  for scope in [100,200,'all']:
   for repeat in range(2):
    q=deepcopy(p);q['radius']+=repeat*.001
    t=time.perf_counter();s,z=derive(q,data);c=contacts(s,seconds=.5);pre=time.perf_counter()-t
    if not c['certified']:
     native.append(dict(label=model['label'],scope=scope,repeat=repeat,skipped=True,contact=c));continue
    o,_,_=evaluate(s.p,data,ev,scope,ev.obs,mapping)
    native.append(dict(label=model['label'],scope=scope,repeat=repeat,construction=z,pre_camera_seconds=pre,optical=o))
 result=dict(utc=utc(),host=platform.platform(),cpu=next((x.split(':',1)[1].strip() for x in open('/proc/cpuinfo') if x.startswith('model name')),'unknown'),threads=1,comparison=comparisons,native=native,policy='Sequential isolated work; warmed compiled libraries. Construction plus full actual-solid checks measured separately from native camera/geometry stages. Original R320 measured timings are historical, not rerun identical ray workloads.')
 save(OUT/'performance.json',result)
 flat=[]
 for row in comparisons:
  for method in ['R320','R321']:flat.append({**{k:row[k] for k in ['count','radius','axial','repeat']},'method':method,**{k:row[method][k] for k in ['construction_seconds','contact_seconds','total_before_camera','classification']}})
 with open(OUT/'performance.csv','w') as f:
  w=csv.DictWriter(f,fieldnames=list(flat[0]),lineterminator="\n");w.writeheader();w.writerows(flat)
 plan=read(ROOT/'photo2/r320/results/optimization-plan.json');rates={method:sum(r[method]['classification']=='certified-separation' for r in comparisons)/len(comparisons) for method in ['R320','R321']}
 costs={scope:float(np.median([r['optical']['total_seconds'] for r in native if not r.get('skipped') and r['scope']==scope])) for scope in [100,200,'all']}
 packing=float(np.mean([r['R321']['total_before_camera'] for r in comparisons]));phases=[]
 for p in plan['phases']:
  m=p['expected_evaluations'];scope=int(p['scope']) if p['scope']!='all' else 'all';factor=p['scenarios']['expected']['verification_allowance_multiplier']
  # Pilot feasibility fraction is a workload scenario, not a population estimate.
  phases.append(dict(phase=p['phase'],evaluations=m,scope=scope,all_render_seconds=m*(packing+costs[scope])*factor,pilot_yield_seconds=m*(packing+rates['R321']*costs[scope])*factor,verification_allowance=factor))
 save(OUT/'optimization-plan.json',dict(source='R320 phase counts unchanged; no larger search authorized',measured_packing_mean_seconds=packing,measured_native_medians={str(k):v for k,v in costs.items()},observed_feasibility_fraction= rates,phases=phases,all_render_total_hours=sum(x['all_render_seconds'] for x in phases)/3600,pilot_yield_scenario_hours=sum(x['pilot_yield_seconds'] for x in phases)/3600,limitations=['Pilot is purposive, feasibility fraction is not an estimated population rate.','Verification10x remains unmeasured.','Setup overhead and broader shape/count workloads not remeasured.','Different geometry changes camera workloads; no isolated camera speedup claimed.','No convergence or runtime guarantee.']))
 print('BENCHMARK',len(comparisons),len(native),costs,packing,rates,flush=True)
if __name__=='__main__':main()
