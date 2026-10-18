"""Matched native all-body localization optimization; exact predictions required."""
from .coupled import *

def main():
 data=load()[0];doc=read(OUT/'R321-photo-sized-rescue-frozen.json.gz');p=copy.deepcopy(doc['parameters']);p['radius']+=.002;s,z=derive(p,data);mapping=doc['seed_options'][0]['mapping'];refs=[r for r in read(OUT/'fit-evidence.json')['reflections'] if r['observation'] in mapping]
 old,oa=optical(s,s.indices,refs,mapping,'all',grouped=False);new,na=optical(s,s.indices,refs,mapping,'all',grouped=True)
 assert old['predictions']==new['predictions'];assert old['rows']==new['rows'];assert all(np.array_equal(oa[k],na[k]) for k in oa)
 result=dict(original={k:v for k,v in old.items() if k not in ['rows','predictions','target_addresses']},optimized={k:v for k,v in new.items() if k not in ['rows','predictions','target_addresses']},exact_prediction_count=len(old['predictions']),exact_camera_ray_count=len(oa['xy']),exact_owner_intensity_arrays=True,change='Stable group by first-hit owner once instead of full-ray scan for every target; no geometry, light, visibility, centroid or scope changes')
 save(OUT/'optical-speed.json',result)
 plan=read(OUT/'runtime-plan.json');plan['ungrouped_seconds_per_evaluation']=copy.deepcopy(plan['seconds_per_evaluation']);plan['seconds_per_evaluation']['all']=new['total_seconds']+z['seconds'];plan['native_grouping_optimization']=dict(exact=True,measured_all_seconds=new['total_seconds'],construction_seconds=z['seconds']);
 for sc in plan['scenarios']:
  for phase in sc['phases']:phase['seconds']=phase['evaluations']*plan['seconds_per_evaluation'][phase['scope']]
  raw=sum(p['seconds'] for p in sc['phases']);sc['raw_hours']=raw/3600;sc['total_hours']=(raw*sc['verification_and_restarts_allowance']+35.57)/3600
 save(OUT/'runtime-plan.json',plan);print('OPTICAL SPEED',old['total_seconds'],new['total_seconds'],len(old['predictions']),flush=True)
if __name__=='__main__':main()
