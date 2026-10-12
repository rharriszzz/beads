"""One-at-a-time threshold sensitivity, sharing the hard local search deadline."""
import argparse
import csv
from dataclasses import asdict, replace
import json
import os
import subprocess
import sys
import time
from .tunable_detect import ROOT, Parameters, detect, save
from .search_parameters import profiles, rank
from .test_pixels import fixtures
from .test_tuning import audit


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--deadline-epoch',required=True,type=float);a=ap.parse_args()
    out=ROOT/'photo2/review/r263';work=ROOT/'photo2/output/search-r263'
    rows=[];trials=[];failed=[];started=time.time()
    changes=[('dark_dn',80),('dark_dn',82),('retreat_dn',1),('retreat_dn',3),
             ('patch_drop_dn',9),('patch_drop_dn',11),('reflection_drop_dn',35),('reflection_drop_dn',37),
             ('hue_stop_deg',19.),('hue_stop_deg',21.),('retreat_fraction',.15),('retreat_fraction',.45),
             ('dark_dn',72),('dark_dn',96)]
    def checkpoint():
        save(out/'sensitivity.json',dict(started_epoch=started,updated_epoch=time.time(),deadline_epoch=a.deadline_epoch,
             trials=trials,incomplete=failed,completed_parameter_combinations=len(rows),
             baseline=dict(prominence_dn=40,rise_budget_dn=0),one_at_a_time=True))
        if rows:
            with (out/'sensitivity-grid.csv').open('w',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    for field,value in changes:
        remaining=a.deadline_epoch-time.time()-5
        if remaining<30:break
        name='p40-b0-'+field+'-'+str(value);p=replace(Parameters(),prominence_dn=40,**{field:value})
        # Native adjacency, irrevocable locks and the rise bound before each photo.
        begin=time.time();checks=0
        for rgb in fixtures().values():
            data,_,_=detect(rgb,p)
            for r in data['regions']+data['rejected']:audit(r['trace'],0);checks+=1
        path=work/name
        cmd=[sys.executable,'-m','photo2.bead_detection.tunable_detect','--output',str(path),'--prominence-dn','40',
             '--'+field.replace('_','-'),str(value)]
        print('Starting '+name,flush=True)
        with (out/(name+'.log')).open('w') as log:
            try:
                result=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,
                    timeout=max(.1,a.deadline_epoch-time.time()-5),env=dict(os.environ,MPLCONFIGDIR='/tmp/beads-r263-mpl'))
            except subprocess.TimeoutExpired:
                failed.append(dict(name=name,reason='deadline; partial trial excluded'));checkpoint();break
        if result.returncode:
            failed.append(dict(name=name,reason='nonzero exit',code=result.returncode));checkpoint();continue
        data=json.loads((path/'regions.json').read_text());summary=json.loads((path/'summary.json').read_text())
        rr=[r|dict(changed_parameter=field,changed_value=value) for r in profiles(data,name)];rows.extend(rr)
        trials.append(dict(name=name,work=str(path.relative_to(ROOT)),parameters=asdict(p),summary=summary,
                           elapsed_seconds=time.time()-begin,synthetic_traces_checked=checks,best=min(rr,key=rank)))
        import gzip
        records=[{k:r[k] for k in ('id','centroid','location','pixel_count','pixel_runs','bbox','kind','overlap_pixel_count')}
                 |dict(peak_value_dn=r['bright_patch']['value_dn']) for r in data['regions']]
        with gzip.GzipFile(filename=str(out/(name+'-regions.json.gz')),mode='wb',mtime=0) as f:
            f.write(json.dumps(records,separators=(',',':')).encode())
        checkpoint();print(json.dumps(trials[-1]['best']),flush=True)
    checkpoint()

if __name__=='__main__':main()
