"""Serial measured workloads and explicitly hypothetical search budgets."""
from .coupled import *

def main():
 data=load()[0];doc=read(OUT/'R321-photo-sized-rescue-frozen.json.gz');p=doc['parameters'];mapping=doc['seed_options'][0]['mapping'];refs=[r for r in read(OUT/'fit-evidence.json')['reflections'] if r['observation'] in mapping];rows=[]
 for category in ['count','radius','axial','centerline','registration','unchanged']:
  q=copy.deepcopy(p)
  if category=='count':q['count']+=1;q['winding']=int(np.floor(q['count']/6.5+.5));q['turn']=q['count']/q['winding']
  if category=='radius':q['radius']+=.001
  if category=='axial':q['axial']+=.001
  if category=='registration':q['s0']+=.1
  if category=='centerline':c=np.array(q['axis_bspline']);c[0]+=.1;q=corrected(q,c)
  t=time.perf_counter();s,z=derive(q,data) if category!='unchanged' else (R321(q,data),dict(seconds=0));construction=time.perf_counter()-t
  result,_=optical(s,range(-99,1),refs,mapping,100);rows.append(dict(category=category,scope=100,construction_seconds=construction,evaluation={k:v for k,v in result.items() if k not in ['predictions','rows','target_addresses']},total_seconds=construction+result.get('total_seconds',0)))
 for scope in [200,'all']:
  q=copy.deepcopy(p);q['radius']+=.002;t=time.perf_counter();s,z=derive(q,data);construction=time.perf_counter()-t;targets=range(-149,51) if scope==200 else s.indices;result,_=optical(s,targets,refs,mapping,scope);rows.append(dict(category='radius',scope=scope,construction_seconds=construction,evaluation={k:v for k,v in result.items() if k not in ['predictions','rows','target_addresses']},total_seconds=construction+result.get('total_seconds',0)))
 costs={str(scope):float(np.median([r['total_seconds'] for r in rows if r['scope']==scope])) for scope in [100,200,'all']}
 scenarios=[]
 for name,iterations,factor in [('low',[10,20,10],1.5),('expected',[50,100,50],2),('high',[200,300,200],3)]:
  phases=[dict(scope=scope,iterations=it,evaluations=14*it,seconds=14*it*costs[scope]) for scope,it in zip(['100','200','all'],iterations)];raw=sum(r['seconds'] for r in phases);scenarios.append(dict(name=name,phases=phases,raw_hours=raw/3600,verification_and_restarts_allowance=factor,total_hours=(raw*factor+35.57)/3600))
 save(OUT/'runtime-plan.json',dict(benchmarks=rows,seconds_per_evaluation=costs,scenarios=scenarios,iteration_definition='six-variable bilateral sensitivity plus two trust proposals =14 native evaluations',empirical_iterations_completed={'100':2,'200':1},warning='Evaluation costs measured. Iteration counts and 1.5/2/3 overhead factors are explicit planning budgets, not convergence predictions or measured verification multipliers. One 200/all timing each; no parallel speedup. Full solve accuracy/runtime unknown. Different target sizes retain all physical bodies; timings are not equal-workload comparisons.'))
 print('BENCHMARK',costs,[(r['name'],r['total_hours']) for r in scenarios],flush=True)
if __name__=='__main__':main()
