"""Artifact/cohort/arithmetic verification independent of optimization selection."""
from pathlib import Path
from collections import Counter
import re,json
import numpy as np
from PIL import Image
from photo2.r297.common import ROOT,read,save,sha,digest,utc
from photo2.r318.detect import principal,linear
OUT=ROOT/'photo2/r320/results'
def main():
 epoch=read(ROOT/'photo2/r318/results/epoch2/epoch.json');obs={o['id']:o for o in epoch['observations']};im=np.array(Image.open(ROOT/'beads-photo-2.jpg'));maxshift=0
 for o in obs.values():
  x,y,w,h=o['window'];crop=linear(im[y:y+h,x:x+w]).min(2);yy,xx=np.indices(crop.shape);q=principal(np.c_[xx.ravel()+x,yy.ravel()+y],crop.ravel());shift=float(np.linalg.norm(np.array(q['point'])-o['point']));maxshift=max(maxshift,shift);assert shift<1e-9
 rows=[]
 for folder in ['optical-trials','coupled-trials']:
  files=sorted((OUT/folder).glob('*.gz'));assert [read(f)['id'] for f in files]==list(range(len(files)))
  for f in files:
   r=read(f);p=r['parameters'];z=r['packing'];sm=z['summary'];assert sm['count']==p['count'];assert p['topology']=='closed' and p['gap_steps']==0 and p['seam_fraction']==-.5
   assert p['winding']==int(np.floor(p['count']/6.5+.5));assert abs(p['turn']-p['count']/p['winding'])<1e-12
   assert abs(sm['H']-1.4*p['radius']*p['axial'])<1e-12
   assert abs(sm['circumference_ratio']-sm['length']/(p['winding']*sm['H']))<1e-12
   assert sm['axis_correction_px']<=3.3468+1e-9
   for k in ['center_endpoint_gap','orientation_endpoint_gap']:assert sm['closure'][k]<1e-8
   if 'optical' in r:
    o=r['optical'];assert z['certified'] and o['physical']['certified'];assert o['bodies']==p['count'];assert len(o['rows'])==22 and {v['id'] for v in o['rows']}==set(obs)
    ep=read(OUT/f'epoch-N{p["count"]}-h{p["hand"]}.json.gz');errs=[];missing=0
    for v in o['rows']:
     assert v['index']==ep['mapping'][v['id']];np.testing.assert_array_equal(v['observed'],obs[v['id']]['point'])
     if v['predicted'] is None:missing+=1;assert v['error_px'] is None
     else:
      e=float(np.linalg.norm(np.array(v['predicted'])-v['observed']));assert abs(e-v['error_px'])<1e-10;errs.append(e)
    assert missing==o['missing'];assert o['maximum_is_infinite']==bool(missing)
    if missing:assert o['emax_px'] is None
    else:assert abs(o['emax_px']-max(errs))<1e-10
   rows.append(r)
 perf=read(OUT/'performance.json');bench=[]
 for f in sorted(OUT.glob('benchmark-*-*.json.gz')):
  if 'epoch' in f.name:continue
  r=read(f);assert len(r['rows'])==6;assert Counter(v['mode'] for v in r['rows'])==Counter({'process-cold':1,'geometry-invalidated':1,'exact-geometry-cached-light-change':4})
  for v in r['rows']:
   assert v['bodies']==v['physical'].get('bodies',v['bodies']);assert v['total_seconds']>=sum(v['times'].values())-1e-5
   assert v['target_bodies']==(v['bodies'] if r['scope']=='all' else r['scope'])
   if v['cached']:assert v['times']['camera_rays_and_normals']==0 and v['times']['all_body_nonintersection']==0
  bench.append(r)
 assert len(bench)==9
 plan=read(OUT/'optimization-plan.json')
 for scenario,total in plan['serial_totals_seconds'].items():
  actual=0
  for p in plan['phases']:
   s=p['scenarios'][scenario];x=s['evaluations']*(s['fast_evaluation_seconds']+s['packing_seconds'])*s['verification_allowance_multiplier']+s['cold_setup_overhead_seconds'];assert abs(x-s['total_seconds'])<1e-8;actual+=x
  assert abs(actual-total)<1e-8
 for f in OUT.glob('*.png'):
  with Image.open(f) as x:x.verify()
 html=(OUT/'index.html').read_text()
 for link in re.findall(r'(?:href|src)="([^"]+)"',html):assert (OUT/link).exists(),link
 for label in ['derived-best','centerline-control','derived-2600']:
  g=read(OUT/f'{label}-neighbor-gaps.json.gz');s=read(OUT/f'{label}-model.json.gz')['summary'];n=s['count']
  for row in g:
   assert len(row['pairs'])==n;assert sum(p['seam'] for p in row['pairs'])==row['offset'];assert row['endpoint_sdf_max']<1e-8
   for p in row['pairs']:assert p['lower']>0 and p['upper']+1e-8>=p['lower']
 allp=[r['parameters'] for r in rows]+[r['parameters'] for r in read(OUT/'physical-grid.json')['rows']]
 ranges={k:dict(minimum=min(p[k] for p in allp),maximum=max(p[k] for p in allp),unique=len({p[k] for p in allp})) for k in ['count','radius','axial','phase','s0']}
 save(OUT/'actual-search-ranges.json',dict(parameters=ranges,serialized_inputs=len(allp),unique_parameter_hashes=len({digest(p) for p in allp}),physical_only=288,optical_trials=140,coupled_trials=110))
 save(OUT/'artifact-verification.json',dict(passed=True,utc=utc(),optical_trials=len(rows),photo_centroids=22,maximum_observed_centroid_difference=maxshift,benchmark_cases=len(bench),benchmark_evaluations=sum(len(r['rows']) for r in bench),photo_sha256=sha(ROOT/'beads-photo-2.jpg'),photo_unchanged=sha(ROOT/'beads-photo-2.jpg')==read(OUT/'start.json')['photo_sha256'],checks=['all trial cohorts/maps and missing-infinite convention','Euclidean maxima','derived dimensions/ratios','closed positions and frames','54 benchmark mode/count/timer records','runtime arithmetic','all selected neighbor pairs including seam','actual-glass upper endpoints','PNG integrity and static links']))
 print('VALIDATED',len(rows),'optical trials',len(bench),'benchmark cases',ranges,flush=True)
if __name__=='__main__':main()
