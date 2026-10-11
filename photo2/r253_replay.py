import sys,json,hashlib,subprocess
from pathlib import Path
import numpy as np
sys.path.insert(0,'photo2')
from global_fit_r253 import *
rows=data();train=[r for r in rows if r['split']=='train'];scanrows=json.loads((OUT/'scan.json').read_text());checks=[]
for n in [2000,2312,2529,2670,2671,2679,2698,2833,3200,3592,3600]:
 for h in [1,-1]:
  best=None
  for phase in np.arange(8)*2*np.pi/8:
   for shift in [-.25,.25]:
    p=np.array([phase,shift,0,0,89,0]+[0]*8);_,cost,*_=assign(Model(n,h,p),train);score=float(cost@weights(train))
    if best is None or score<best['train_score']:best=dict(n=n,h=h,p=p.tolist(),train_score=score)
  original=next(r for r in scanrows if r['n']==n and r['h']==h)
  assert best==original
  checks.append(dict(n=n,h=h,exact_replay=True))
trial=next(r for r in json.loads((OUT/'polished.json').read_text()) if r['n']==2671 and r['h']==1 and r['kind']=='both')
groups,_=patch_points(rows);m,rr,_,_=audit_one(trial,rows,groups)
assert m==json.loads((OUT/(m['model_id']+'-metrics.json')).read_text())
assert rr==json.loads((OUT/(m['model_id']+'-assignments.json')).read_text())
save(OUT/'numerical-replay.json',dict(screening=checks,full_310_point_and_patch_audit='N2671_h+1_both exactly equal: all residuals, assignments, alternatives, sectors, colors and metrics'))
files=['beads.pov','beads-photo-2.jpg','photo2/spline-seed-r175.json','photo2/review/r252/accepted.csv','photo2/review/r252/inventory.json','photo2/review/r250/angle-range-observations.csv']
checks=[]
for p in files:
 old=subprocess.check_output(['git','show','90c8325:'+p]);new=(ROOT/p).read_bytes();assert old==new
 checks.append(dict(path=p,sha256=hashlib.sha256(new).hexdigest(),unchanged_since_90c8325=True))
save(OUT/'source-integrity.json',checks)
print('22 scan minima and full310-point/patch audit replay exactly; source files unchanged')
