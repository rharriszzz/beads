"""Measured timings and explicit scenario arithmetic, never a linear N forecast."""
from collections import defaultdict
import csv
import numpy as np
from photo2.r297.common import ROOT,read,save
OUT=ROOT/'photo2/r320/results'
def stats(x):
 x=list(map(float,x));return dict(n=len(x),mean=float(np.mean(x)),minimum=min(x),median=float(np.median(x)),p95=float(np.percentile(x,95)),maximum=max(x))
def main():
 docs=[read(p) for p in sorted(OUT.glob('benchmark-*-*.json.gz')) if 'epoch' not in p.name];group=defaultdict(list)
 for d in docs:
  for r in d['rows']:group[(str(d['scope']),r['mode'])].append(r)
 table={}
 for (scope,mode),rr in group.items():
  table.setdefault(scope,{})[mode]=dict(total_seconds=stats(r['total_seconds'] for r in rr),operations={k:stats(r['times'][k] for r in rr) for k in rr[0]['times']},camera_rays=stats(r['camera_rays'] for r in rr),bodies=sorted(set(r['bodies'] for r in rr)),measured_observations=sorted(set(r['observations'] for r in rr)),target_bodies=sorted(set(r['target_bodies'] for r in rr)),peak_rss_mib=max(r['peak_rss_mib'] for r in rr),unknown_camera=[r['unknown_camera'] for r in rr],unknown_shadow_pairs=[r['unknown_shadow_pairs'] for r in rr])
 grid=read(OUT/'physical-grid.json');physical=grid['rows'];packing=stats(r['seconds'] for r in physical);packing['observed_batch_seconds_per_trial']=grid['seconds']/len(physical);packing['batch_overhead_seconds_per_trial']=(grid['seconds']-sum(r['seconds'] for r in physical))/len(physical);setup=stats(d['setup_seconds'] for d in docs)
 summary=dict(schema=1,unit='seconds',table=table,packing_solver_seconds=packing,setup_seconds=setup,hardware=docs[0]['hardware'],conditions='Sequential one-process measurements, 1px native lattice. Process-cold follows loading frozen photo data and epoch, with axis cache cleared; precompiled C++ shared libraries reused from disk. Geometry-invalidated changes radius AND a 0.25px centerline harmonic. Cached timings change only shared light and reuse exact scene, contact, camera and photographic evidence. Local geometry evidence is the fixed R319 patch at both 100/200; all includes 447 historical positive-interior supports and paper cues. These are different evidence workloads, not linear scaling samples.',statistical_limit='Three physical configurations and two rebuilt evaluations per configuration. P95 is an empirical small-sample percentile, not a calibrated tail bound. Preliminary overlapped runs are archived and excluded.')
 save(OUT/'performance.json',summary)
 with (OUT/'performance.csv').open('w',newline='') as f:
  w=csv.writer(f,lineterminator="\n");w.writerow(['scope','mode','operation','samples','median_seconds','p95_seconds','minimum_seconds','maximum_seconds'])
  for scope,modes in table.items():
   for mode,rec in modes.items():
    for op,v in dict(rec['operations'],TOTAL=rec['total_seconds']).items():w.writerow([scope,mode,op,v['n'],v['median'],v['p95'],v['minimum'],v['maximum']])
 phases=[('coarse_count',49,25,1,1225,'100'),('coarse_radius_axial',8,81,1,648,'100'),('basin_refinement',6,1,200,1200,'100'),('bilateral_jacobians',6,1,68,408,'100'),('local_minimax_proposals',6,1,300,1800,'100'),('expand_200',3,1,300,900,'200'),('full_bracelet_refinement',3,1,200,600,'all'),('independent_final_verification',6,1,5,30,'all')]
 plan=[]
 for name,fam,comb,probes,M,scope in phases:
  warm=table[scope]['geometry-invalidated']['total_seconds'];cold=table[scope]['process-cold']['total_seconds'];scenarios={}
  for label,fac,unit,pack,over in [('low',.5,warm['minimum'],packing['minimum'],setup['minimum']),('expected',1,warm['median'],packing['observed_batch_seconds_per_trial'],setup['median']),('high',2,max(cold['maximum'],warm['maximum']),packing['p95']+packing['batch_overhead_seconds_per_trial'],setup['maximum'])]:
   count=int(np.ceil(M*fac));cost=unit+pack
   # Independent original-kernel final verification is not measured by fast
   # evaluator; expose a planning allowance, not an invented measurement.
   multiplier=10 if name=='independent_final_verification' else 1
   total=count*cost*multiplier+fam*over
   scenarios[label]=dict(evaluations=count,fast_evaluation_seconds=unit,packing_seconds=pack,verification_allowance_multiplier=multiplier,cold_setup_overhead_seconds=fam*over,total_seconds=total)
  plan.append(dict(phase=name,count_families=fam,radius_axial_combinations=comb,probes_or_iterations_per_family=probes,expected_evaluations=M,scope=scope,scenarios=scenarios))
 totals={k:sum(p['scenarios'][k]['total_seconds'] for p in plan) for k in ['low','expected','high']}
 save(OUT/'optimization-plan.json',dict(schema=1,phases=plan,serial_totals_seconds=totals,parallel_policy='Serial wall-time baseline. Independent family jobs could run concurrently, but throughput and memory contention are unmeasured; no parallel speedup credited.',assumptions=['No phase authorized or launched by this plan.','49 counts roughly every25 over2000..3200, then probe exact neighboring integer winding transitions in refinement.','Jacobian phase counts four 17-evaluation matrices per family; minimax proposals counted separately.','Cached-light timings not substituted for geometry-changing work.','All coarse proposals charged a full photo evaluation even when contacts would reject early; count-dependent rejection savings not assumed.','Low/high vary evaluation counts by0.5x/2x and use observed min/max timing; not probabilistic confidence intervals.','Full-bracelet projected times apply to measured workloads, not an assertion that every count/radius/camera has equal cost.','Independent verification uses an explicit unmeasured10x allowance; original-kernel whole-field verification remains to be benchmarked.']))
 print('PERFORMANCE', {s:table[s]['geometry-invalidated']['total_seconds'] for s in table},'PLAN_SECONDS',totals)
if __name__=='__main__':main()
