"""Independent saved-artifact arithmetic, actual-solid witnesses and raw pixels."""
import re
from pathlib import Path
from collections import Counter
import numpy as np
from PIL import Image
from photo2.r297.common import ROOT,read,save,sha,utc
from photo2.r306.evidence import load
from photo2.r295.geometry import AXES
from photo2.r318.detect import principal,linear
from .model import Chain
OUT=ROOT/'photo2/r321/results'

def main():
 data=load()[0];epoch=read(ROOT/'photo2/r318/results/epoch2/epoch.json');obs={o['id']:o for o in epoch['observations']};image=np.array(Image.open(ROOT/'beads-photo-2.jpg'));maxshift=0.
 for o in obs.values():
  x,y,w,h=o['window'];crop=linear(image[y:y+h,x:x+w]).min(2);yy,xx=np.indices(crop.shape);p=principal(np.c_[xx.ravel()+x,yy.ravel()+y],crop.ravel());shift=float(np.linalg.norm(np.array(p['point'])-o['point']));maxshift=max(maxshift,shift);assert shift<1e-9
 rows=[read(f) for f in sorted((OUT/'trials').glob('*.gz'))];assert [r['id'] for r in rows]==list(range(len(rows)));witnesses=0;photographic=0
 for r in rows:
  p=r['parameters'];sm=r['construction']['summary'];assert p['topology']=='closed' and p['gap_steps']==0 and p['seam_fraction']==-.5;assert p['winding']==int(np.floor(p['count']/6.5+.5));assert abs(p['turn']-p['count']/p['winding'])<1e-12
  assert abs(sm['H']-1.4*p['radius']*p['axial'])<1e-12;assert sm['axis_correction_px']<=3.3468+1e-9
  for key in ['center_endpoint_gap','orientation_endpoint_gap']:assert sm['closure'][key]<1e-8
  c=r['contact']
  if c['classification']=='demonstrated-interpenetration':
   s=Chain(p,data);vv=[v for v in c['actual_solid_checks'] if v['state']=='demonstrated-interpenetration'];assert vv
   for v in vv:
    for j in v['pair']:
     q=(np.array(v['point'])-s.centers[j])@np.stack([s.g[k][j] for k in AXES]).T;rho=np.hypot(q[1],q[2])/s.radius;u=abs(rho-.57)-.086;w=abs(q[0])/(s.radius*s.axial*(.7/.43))-.086
     implicit=np.hypot(max(u,0),max(w,0))+min(max(u,w),0)-.344;assert implicit<-1e-8,(r['id'],implicit)
    witnesses+=1
  if 'optical' in r:
   photographic+=1;o=r['optical'];assert c['certified'] and o['physical']['certified'];assert o['bodies']==p['count'];assert len(o['rows'])==22 and {v['id'] for v in o['rows']}==set(obs)
   mapping=read(OUT/f'epoch-N{p["count"]}-h{p["hand"]}.json.gz')['mapping'];errors=[];missing=0
   for v in o['rows']:
    assert v['index']==mapping[v['id']];np.testing.assert_array_equal(v['observed'],obs[v['id']]['point'])
    if v['predicted'] is None:missing+=1;assert v['error_px'] is None
    else:
     error=float(np.linalg.norm(np.array(v['predicted'])-v['observed']));assert abs(error-v['error_px'])<1e-10;errors.append(error)
   assert o['missing']==missing and o['maximum_is_infinite']==bool(missing)
   if missing:assert o['emax_px'] is None
   else:assert abs(max(errors)-o['emax_px'])<1e-10
 perf=read(OUT/'performance.json');assert len(perf['comparison'])==24;assert len(perf['native'])==18
 for r in perf['native']:
  if r.get('skipped'):continue
  o=r['optical'];assert o['physical']['certified'];assert o['target_bodies']==(o['bodies'] if r['scope']=='all' else r['scope']);assert o['total_seconds']>=sum(o['times'].values())-1e-5
 plan=read(OUT/'optimization-plan.json');assert abs(plan['all_render_total_hours']-sum(p['all_render_seconds'] for p in plan['phases'])/3600)<1e-10
 straight=read(OUT/'straight-audit.json');assert len(straight)==30
 for r in straight:
  assert all(p['actual_contact_within_1e_6'] for p in r['pairs'][:2]);assert r['pairs'][2]['plane_gap']>0;assert r['nearby_finite_scene']['certified']
 for f in OUT.glob('*-neighbor-gaps.json.gz'):
  for row in read(f):
   assert row['lower_min']>0 and row['endpoint_sdf_max']<1e-8 and row['side_segment_sdf_max']<1e-8
   assert sum(p['seam'] for p in row['pairs'])==row['offset']
   for p in row['pairs']:assert p['lower']>0 and p['upper']+1e-8>=p['lower']
 for f in OUT.glob('*.png'):
  with Image.open(f) as im:im.verify()
 for link in re.findall(r'(?:href|src)="([^"]+)"',(OUT/'index.html').read_text()):assert (OUT/link).exists(),link
 original=read(OUT/'start.json');assert sha(ROOT/'beads-photo-2.jpg')==original['photo_sha256'];assert sha(ROOT/'beads.pov')==original['beads_pov_sha256']
 save(OUT/'artifact-verification.json',dict(passed=True,utc=utc(),trials=len(rows),optical_trials=photographic,actual_penetration_witnesses=witnesses,raw_photo_centroids=len(obs),maximum_centroid_difference=maxshift,straight_contact_references=30,benchmark_comparisons=24,native_benchmark_evaluations=18,photo_sha256=original['photo_sha256'],beads_pov_sha256=original['beads_pov_sha256'],checks=['all frozen maps/cohorts/maxima/missing predictions','all demonstrated penetration witnesses independently expanded implicit glass','all dimensions/closure/budgets','all selected neighbors including seam and actual surface endpoints','30 straight contact endpoints and nearby finite scenes','all timing scopes and totals','PNG and static links','photo and beads.pov hashes']))
 print('VALIDATED',len(rows),photographic,witnesses,flush=True)
if __name__=='__main__':main()
