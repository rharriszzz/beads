"""Deadline-limited local coarse/fine search. Counts guide, never certify beads.

Every trial evaluates all 256 minimum-peak settings exactly by filtering independent
regions. That threshold affects seed eligibility only, not other regions' growth or
dark-enclosure significance. Synthetic tests verify equivalence to fresh detection.
"""
import argparse
import csv
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import numpy as np
from .tunable_detect import ROOT, sha, save


def profiles(data, trial):
    regions=data['regions'];peaks=np.array([r['bright_patch']['value_dn'] for r in regions])
    dark=np.array([r['dark_enclosure'] is not None for r in regions])
    out=[]
    for threshold in range(256):
        keep=peaks>=threshold;n=int(keep.sum())
        out.append(dict(trial=trial,prominence_dn=data['parameters']['prominence_dn'],
            rise_budget_dn=data['parameters'].get('rise_budget_dn',0),minimum_peak_dn=threshold,
            regions=n,dark_enclosed=int(dark[keep].sum()),distance_to_target=max(1500-n,0,n-1650),
            count_change_minus_one=int(np.count_nonzero(peaks==threshold-1)) if threshold else 0,
            count_change_plus_one=int(np.count_nonzero(peaks==threshold))))
    return out


def rank(row):
    # Declared heuristic: count range, preserve dark supports, then avoid a high
    # absolute brightness cutoff. No claim these proxies measure precision/recall.
    return (row['distance_to_target'],-row['dark_enclosed'],row['minimum_peak_dn'],
            row['rise_budget_dn'],row['prominence_dn'])


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--deadline-epoch',type=float,required=True)
    ap.add_argument('--output',type=Path,default=ROOT/'photo2/review/r263')
    args=ap.parse_args();out=args.output;out.mkdir(parents=True,exist_ok=True)
    work=ROOT/'photo2/output/search-r263';work.mkdir(parents=True,exist_ok=True)
    started=time.time();rows=[];trials=[];failed=[]
    state=dict(started_epoch=started,deadline_epoch=args.deadline_epoch,
        target=[1500,1650],target_source='photo2/GLOBAL_GEOMETRY_R253.md:214-239; conditional model estimate, not ground truth',
        detector_sha256=sha(Path(__file__).with_name('tunable_detect.py')),trials=trials,incomplete=failed)

    def checkpoint():
        state.update(updated_epoch=time.time(),completed_parameter_combinations=len(rows))
        if rows:state['count_guided_candidate']=min(rows,key=rank)
        save(out/'search.json',state)
        if rows:
            with (out/'parameter-grid.csv').open('w',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)

    def add(path,name,elapsed):
        data=json.loads((path/'regions.json').read_text())
        summary=json.loads((path/'summary.json').read_text())
        row=profiles(data,name);rows.extend(row)
        trials.append(dict(name=name,work=str(path.relative_to(ROOT)),elapsed_seconds=elapsed,
            summary=summary,best=min(row,key=rank)))
        # Native coordinates / masks of each grown candidate, for exact comparison.
        import gzip
        records=[{k:r[k] for k in ('id','centroid','location','pixel_count','pixel_runs','bbox','kind','overlap_pixel_count')}
                 | dict(peak_value_dn=r['bright_patch']['value_dn']) for r in data['regions']]
        with gzip.GzipFile(filename=str(out/(name+'-regions.json.gz')),mode='wb',mtime=0) as f:
            f.write(json.dumps(records,separators=(',',':')).encode())
        checkpoint();print(json.dumps(trials[-1]['best']),flush=True)

    baseline=ROOT/'photo2/output/detection-r262'
    add(baseline,'p10-b0',0)

    def run(prominence,budget):
        name=f'p{prominence}-b{budget}'
        if any(t['name']==name for t in trials):return True
        remaining=args.deadline_epoch-time.time()-5
        if remaining<25:return False
        path=work/name;begin=time.time()
        cmd=[sys.executable,'-m','photo2.bead_detection.tunable_detect','--output',str(path),
             '--prominence-dn',str(prominence),'--rise-budget-dn',str(budget)]
        print('Starting '+name+'; remaining '+str(round(remaining))+' seconds',flush=True)
        with (out/(name+'.log')).open('w') as log:
            try:
                result=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,
                    timeout=remaining,env=dict(os.environ,MPLCONFIGDIR='/tmp/beads-r263-mpl'))
            except subprocess.TimeoutExpired:
                failed.append(dict(name=name,reason='deadline; partial trial excluded',elapsed_seconds=time.time()-begin));checkpoint();return False
        if result.returncode:
            failed.append(dict(name=name,reason='nonzero exit',code=result.returncode));checkpoint();return True
        add(path,name,time.time()-begin);return True

    for prominence in (20,40,80):
        if not run(prominence,0):break
    if time.time()<args.deadline_epoch-25:
        best=min(rows,key=rank);p=best['prominence_dn']
        for budget in (1,2,4):
            if not run(p,budget):break
        # One-level prominence comparisons, followed by intermediate coarse steps.
        for h in (max(1,p-1),p+1,15,30,60):
            if not run(h,0):break
    state['finished_epoch']=time.time();state['wall_seconds']=time.time()-started
    state['stopped_by_deadline']=bool(failed and 'deadline' in failed[-1]['reason'])
    checkpoint()

if __name__=='__main__':main()
