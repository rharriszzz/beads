"""Feedback-driven next trials; hard deadline, explicit regression gates, no adoption."""
import argparse
import gzip
import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps
from matplotlib.colors import rgb_to_hsv
from .tunable_detect import ROOT, save, Parameters
from .search_parameters import profiles,rank
from dataclasses import asdict,replace


def regressions(base,data):
    old={r['id']:r for r in base['regions']+base['rejected']};bad=[]
    for r in data['regions']:
        if r['id'] not in old:continue
        b=old[r['id']];ratio=r['pixel_count']/b['pixel_count']
        shift=float(np.linalg.norm(np.array(r['centroid'])-b['centroid']))
        if ratio>4 and shift>max(10,3*math.sqrt(b['pixel_count']/math.pi)):
            bad.append(dict(id=r['id'],area_ratio=ratio,centroid_shift_px=shift))
    return sorted(bad,key=lambda r:-r['centroid_shift_px'])


def next_prominence(rows,target=1575):
    ordered=sorted(rows)
    for (p,n),(q,m) in zip(ordered,ordered[1:]):
        if n>=target>=m and q-p>1:
            guess=round(p+(q-p)*(n-target)/(n-m)) if n!=m else (p+q)//2
            return max(p+1,min(q-1,guess))
    return None


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--deadline-epoch',type=float,required=True);a=ap.parse_args()
    out=ROOT/'photo2/review/r263';work=ROOT/'photo2/output/search-r263'
    base=json.loads((ROOT/'photo2/output/detection-r262/regions.json').read_text())
    prior=json.loads((out/'search.json').read_text());decisions=[];trials=[];failed=[]
    state=dict(deadline_epoch=a.deadline_epoch,started_epoch=time.time(),decisions=decisions,trials=trials,incomplete=failed,
        gate='Reject area ratio >4 AND centroid movement >max(10px, 3*sqrt(baseline area/pi)). Heuristic regression gate, not precision/recall.',
        hue_note='Circular hue guarded by saturation/value reliability. Similar hue does not establish bead material; shadows may retain paper hue.')
    def checkpoint():state['updated_epoch']=time.time();save(out/'adaptive.json',state)
    def run(p,reason):
        if a.deadline_epoch-time.time()<35:return None
        name=f'adaptive-{len(decisions)+1}';path=work/name
        decisions.append(dict(name=name,reason=reason,parameters=asdict(p),started_epoch=time.time()));checkpoint()
        flags=[v for k,val in asdict(p).items() for v in ('--'+k.replace('_','-'),str(val))]
        begin=time.time()
        with (out/(name+'.log')).open('w') as log:
            try:
                result=subprocess.run([sys.executable,'-m','photo2.bead_detection.tunable_detect','--output',str(path)]+flags,
                    cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=min(75,a.deadline_epoch-time.time()-5),
                    env=dict(os.environ,MPLCONFIGDIR='/tmp/beads-r263-mpl'))
            except subprocess.TimeoutExpired:
                failed.append(dict(name=name,reason='trial/deadline time limit'));checkpoint();return None
        if result.returncode:
            failed.append(dict(name=name,reason='nonzero exit',code=result.returncode));checkpoint();return None
        data=json.loads((path/'regions.json').read_text());bad=regressions(base,data);summary=json.loads((path/'summary.json').read_text())
        rr=profiles(data,name);save(out/(name+'-peak-grid.json'),rr)
        trials.append(dict(name=name,work=str(path.relative_to(ROOT)),parameters=asdict(p),summary=summary,
            elapsed_seconds=time.time()-begin,regressions=bad,eligible_for_recommendation=not bad,best=min(rr,key=rank)))
        records=[{k:r[k] for k in ('id','centroid','location','pixel_count','pixel_runs','bbox','kind','overlap_pixel_count')}
                 |dict(peak_value_dn=r['bright_patch']['value_dn']) for r in data['regions']]
        with gzip.GzipFile(filename=str(out/(name+'-regions.json.gz')),mode='wb',mtime=0) as f:f.write(json.dumps(records,separators=(',',':')).encode())
        checkpoint();print(name,len(data['regions']),len(bad),flush=True);return data
    # A selected next point is computed from observed completed counts, not a fixed grid.
    rows=[(t['summary']['parameters']['prominence_dn'],t['summary']['regions']) for t in prior['trials'] if t['summary']['parameters'].get('rise_budget_dn',0)==0]
    h=next_prominence(rows)
    if h is not None:run(replace(Parameters(),prominence_dn=h),'Interpolate the measured strict-growth count bracket toward1575; retain dim peaks and freeze all growth rules.')
    noisy=json.loads((work/'p40-b1/regions.json').read_text());initial=regressions(base,noisy)
    state['original_noise_regressions']=initial;checkpoint()
    if initial:
        p=replace(Parameters(),prominence_dn=40,rise_budget_dn=1,hue_stop_deg=10.)
        result=run(p,'Observed area/coordinate regressions at one-level allowance; test tighter circular hue stopping20→10 degrees as a background/shadow boundary clue.')
        if result is not None and regressions(base,result):
            run(replace(p,reliable_saturation=.25),'Tighter hue threshold still leaves large regressions; test earlier hue eligibility by lowering reliable saturation0.35→0.25. Low-saturation hue remains uncertain.')
    state['finished_epoch']=time.time();checkpoint()

if __name__=='__main__':main()
