"""Final comparison-only evidence and provenance; never imported by detection."""
from pathlib import Path
import json,gzip,hashlib,time,math
from collections import Counter
import numpy as np
from PIL import Image,ImageDraw
from photo2.bead_detection.review_coverage_r272 import pair
from photo2.bead_detection.experiment_coverage_r272 import ROOT,OUT,save
inv=json.loads((OUT/'inventory.json').read_text());bs=inv['beads'];xy=np.array([[b['brightest']['x'],b['brightest']['y']] for b in bs if b['color']=='black']);ids=[b['id'] for b in bs if b['color']=='black']
with gzip.open(ROOT/'photo2/review/r260/regions.json.gz','rt') as f:old=json.load(f)
a=[r for r in old['regions'] if r['kind']=='reflection-on-dark'];rows=[]
for r in a:
 ds=np.linalg.norm(xy-r['initial_center'],axis=1);j=int(np.argmin(ds));rows.append(dict(old_id=r['id'],old_seed=r['initial_center'],nearest_new_id=ids[j],distance=float(ds[j])))
save('r260-black-comparison.json',dict(old_reflection_supports=len(a),within6=sum(r['distance']<=6 for r in rows),within12=sum(r['distance']<=12 for r in rows),rows=rows,note='Nearest-coordinate correspondence only; old labels are not ground truth or runtime inputs.'))
# Explicit, unblinded boundary adjudication; original annotations are untouched.
save('photo-review-limitations.json',dict(frozen_sample_bodies=31,possible_additional_black_bodies=2,annotations='photo-samples.json',unmatched_boundary_cases=[dict(id='K-1377-0268',sample='S1',reason='Visible black bead center lies beyond right counting boundary; its reflection enters the core.'),dict(id='K-0227-1153',sample='S3',reason='Visible black bead center lies beyond right counting boundary; its reflection enters the core.'),dict(id='K-1325-1490',sample='S4',reason='Visible black bead center lies beyond right counting boundary; its reflection enters the core.')],other_flags=['S8: two reflection supports associate with one frozen apparent body. One duplicate unless the ambiguous body is actually two; retain 0–1 duplicate uncertainty.','S1: detector calls a frozen yellow/brown upper body red. Color disagreement remains unresolved.','S3: red proposal adjacent to a black reflection overlaps its approximate matching envelope; true color/ownership needs review.'],interpretation='The automated false_positive field is a conservative mismatch flag, not confirmed photographic false discovery. After excluding three explicitly documented boundary crossings: black 0–1 possible duplicate /7 in-sample predictions; red 0–2 unresolved color/ownership errors /9; yellow 0 flagged /11. Small exploratory sample, no human adjudication or whole-photo inference.'))
# Supporting failure crop for each remaining class of ambiguity, cyan-only photos.
im=Image.open(ROOT/'photo2/review/r272/photo-srgb.png')
for name,box in [('failure-multiple-glints',[1400,2990,1500,3090]),('failure-color-ownership',[145,1095,245,1195]),('failure-dim-yellow',[930,2550,1030,2650])]:pair(im,bs,box,name+'.png',name.replace('-',' '),4)
# Source hashes and verification record apply to final reproducible implementation.
files=list((ROOT/'photo2/bead_detection').glob('*coverage*r272*'))+[ROOT/'photo2/bead_detection/black_controls_r272.py']+list((ROOT/'photo2/coverage_inventory_r272').glob('*'))
save('source-hashes.json',{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.is_file()})
test_log=Path('/tmp/r272-coverage-tests-final.log')
if test_log.exists():(OUT/'unit-tests.txt').write_text(test_log.read_text())
budget=json.loads((OUT/'budget.json').read_text());budget.update(completed=time.time(),elapsed_seconds=time.time()-budget['start'],completed_within_budget=time.time()<budget['start']+budget['seconds'],note='Includes experiment setup, bounded trials, synthetic/photo evaluation and validation. A slow validator was interrupted and fixed to load compressed masks once; final validation passes. No further parameter tuning.');save('budget.json',budget)
s=json.loads((OUT/'summary.json').read_text());grid=np.zeros((4,4),int)
for b in bs:x,y=b['anchor'];grid[min(3,4*y//3182),min(3,4*x//2540)]+=1
s['coverage_grid4x4']=grid.tolist();s['region_sizes']=dict(minimum=min(b['region']['pixel_count'] for b in bs),median=float(np.median([b['region']['pixel_count'] for b in bs])),maximum=max(b['region']['pixel_count'] for b in bs));s['all_region_pixels']=sum(b['region']['pixel_count'] for b in bs);save('summary.json',s)
print('elapsed_minutes',budget['elapsed_seconds']/60,'R260',sum(r['distance']<=6 for r in rows),len(a),'grid',grid.tolist())
