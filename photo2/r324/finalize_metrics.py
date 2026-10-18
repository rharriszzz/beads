"""Reproducible derived closure inventory and scenario-cost bookkeeping."""
from .coupled import *
from collections import defaultdict

def main():
 g=read(OUT/'graph.json');rows=[]
 for c in g['graph']['components']:
  ns=[n for n in g['intersections'] if n['component']==c['id']];row=dict(component=c['id'],observations=len(ns),maps={})
  for key in ['A','B','reverse_A','reverse_B']:
   groups=defaultdict(list)
   for n in ns:groups[n['conditional_indices'][key]].append(n['id'])
   row['maps'][key]=dict(minimum=min(groups),maximum=max(groups),unknown_slots=max(groups)-min(groups)+1-len(groups),equal_index_distinct_observations=[v for v in groups.values() if len(v)>1])
  rows.append(row)
 save(OUT/'closure.json',dict(full_loop_closure=False,total_bead_count=None,components=rows,algebraic_cycle_rank=g['graph']['cycle_rank'],seam_overlap=g['transitions'][0],reason='19 unresolved chart transitions prevent a complete accumulated offset. The 14/14 seam overlap reconciles local charts only; it does not span a supported full-circuit path. No nonzero winding index constraint determines N. No even-count restriction used.',identity42=dict(A_sites=[[6,0],[0,7]],B_sites=[[7,0],[0,6]],weighted_value=42,planar_sites_distinct=True)))
 plan=read(OUT/'runtime-plan.json');plan.setdefault('native_seconds_per_evaluation',copy.deepcopy(plan['seconds_per_evaluation']));fs=read(OUT/'fit-summary.json');es=read(OUT/'expand-summary.json');tr=[read(p) for p in (OUT/'fit-trials').glob('*.gz')];overhead=float(np.median([r['seconds']-r['native']['total_seconds']-r['construction'].get('seconds',0) for r in tr if r.get('feasible') and not r['cached']]))
 plan['seconds_per_evaluation']={'100':float(np.median([j['seconds']/12 for j in fs['jacobians']])),'200':es['jacobian_seconds']/12,'all':plan['native_seconds_per_evaluation']['all']+overhead};plan['coupled_cost_model']='100/200: actual six-variable bilateral Jacobian divided by12; all: measured grouped native evaluation plus median local support/geometry-guard overhead. Full-bracelet global guard optimization not benchmarked.';plan['median_measured_local_guard_overhead_seconds']=overhead
 for s in plan['scenarios']:
  for p in s['phases']:p['seconds']=p['evaluations']*plan['seconds_per_evaluation'][p['scope']]
  raw=sum(p['seconds'] for p in s['phases']);s['raw_hours']=raw/3600;s['total_hours']=(raw*s['verification_and_restarts_allowance']+35.57)/3600
 save(OUT/'runtime-plan.json',plan)
if __name__=='__main__':main()
