"""Frozen per-family maps, bounded physical coarse-to-fine optical pilot."""
import time,itertools
from copy import deepcopy
from collections import defaultdict
import numpy as np
from photo2.r297.common import ROOT,read,save,digest,utc
from photo2.r306.evidence import load
from photo2.r318.optics import Engine
from .model import Chain,derive,parameters,corrected,D
from .evaluate import Evidence,evaluate,errors
OUT=ROOT/'photo2/r320/results'
def main():
 data=load()[0];ev=Evidence(data);obs=ev.obs;grid=read(OUT/'physical-grid.json')['rows'];by=defaultdict(list)
 for r in grid:
  if r['certified']:by[(r['summary']['count'],r['summary']['hand'])].append(r)
 maps={};rows=[];start=time.perf_counter()
 def trial(p,family,kind,meta=None):
  s,z=derive(p,data);r=dict(id=len(rows),kind=kind,family=list(family),parameters=s.p,packing=z,meta=meta or {})
  if z['certified']:
   optical,_,_=evaluate(s.p,data,ev,'pilot',obs,maps[family]['mapping']);r['optical']=optical
  rows.append(r);save(OUT/'optical-trials'/f'{r["id"]:04}.json.gz',r)
  print('OPTICAL',r['id'],family,kind,z['certified'],r.get('optical',{}).get('emax_px'),z['summary']['circumference_ratio'],flush=True)
  return r
 for family,gg in sorted(by.items()):
  parent=min(gg,key=lambda r:abs(np.log(r['summary']['circumference_ratio'])))
  s=Chain(parent['parameters'],data);maps[family]=ev.assignment(s,obs)
  save(OUT/f'epoch-N{family[0]}-h{family[1]}.json.gz',dict(parameters=s.p,observations=obs,**maps[family]))
  # At identical geometry, preserve historical-map score separately. No optical
  # distance participates in map initialization or its frozen continuation.
  first=trial(parent['parameters'],family,'family-parent')
  for rad in sorted({r['summary']['radius'] for r in gg}):
   choices=[r for r in gg if r['summary']['radius']==rad]
   q=min(choices,key=lambda r:abs(np.log(r['summary']['circumference_ratio'])))
   if q['id']!=parent['id']:trial(q['parameters'],family,'coarse-radius-axial')
 # Refine at most three different counts, preserving their own frozen map.
 candidates=[r for r in rows if r.get('optical',{}).get('emax_px') is not None and r['packing']['summary']['circumference_ratio']<=1.35]
 candidates.sort(key=lambda r:(not r['packing']['eligible'],r['optical']['geometry']['dual_count'],r['optical']['emax_px']))
 chosen=[]
 for r in candidates:
  if r['family'][0] not in [v['family'][0] for v in chosen]:chosen.append(r)
  if len(chosen)==3:break
 for base in chosen:
  family=tuple(base['family']);p=base['parameters'];local=[base]
  # Bilateral physical probes plus a joint grid; no light or camera fitting.
  for dr,da in itertools.product([-.04,0,.04],[-.04,0,.04]):
   if dr==da==0:continue
   q=deepcopy(p);q['radius']+=dr;q['axial']+=da
   local.append(trial(q,family,'joint-radius-axial',dict(parent=base['id'],dr=dr,da=da)))
  # New user steering: bounded two-harmonic centerline corrections, tested
  # against both contacts and all fixed photographic safeguards.
  for j,sign in itertools.product(range(4),[-1,1]):
   co=[0.]*4;co[j]=sign*1.5
   local.append(trial(corrected(p,co),family,'centerline-bilateral',dict(parent=base['id'],coordinate=j,step_px=co[j])))
  good=[r for r in local if r.get('optical',{}).get('emax_px') is not None]
  # Rank only feasible near-rise models first. Never bury geometric failures.
  def key(r):
   g=r['optical']['geometry'];return (not r['packing']['eligible'],g['dual_count'],g['seam_conflict_fraction'],r['optical']['emax_px'])
  best=min(good,key=key)
  for dp,ds in itertools.product([-.12,0,.12],[-.1*D,0,.1*D]):
   if dp==0 and ds==0:continue
   q=deepcopy(best['parameters']);q['phase']+=dp;q['s0']+=ds
   trial(q,family,'small-registration',dict(parent=best['id'],phase_delta_rad=dp,station_delta_px=ds))
 save(OUT/'search-summary.json',dict(utc=utc(),seconds=time.perf_counter()-start,trial_count=len(rows),families=[list(k) for k in maps],refinement_parents=[r['id'] for r in chosen],rows=[dict(id=r['id'],family=r['family'],kind=r['kind'],certified=r['packing']['certified'],eligible=r['packing']['eligible'],ratio=r['packing']['summary']['circumference_ratio'],emax=r.get('optical',{}).get('emax_px'),missing=r.get('optical',{}).get('missing')) for r in rows]))
 print('SEARCH COMPLETE',len(rows),time.perf_counter()-start,flush=True)
if __name__=='__main__':main()
