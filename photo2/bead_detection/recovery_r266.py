"""Deadline-shared low-prominence controls; never given diagnostic coordinates."""
import json,subprocess,sys,time,gzip,tarfile
from pathlib import Path
from dataclasses import replace,asdict
import numpy as np
from . import annular_detect as d
from .experiment_r266 import ROOT,OUT,WORK,VARIANTS,photo,outline_image,save,irregularity


def main():
    deadline=json.loads((OUT/'checkpoint.json').read_text())['deadline_epoch'];results=[];visual=json.loads((ROOT/'photo2/review/r264/visual-review.json').read_text());rgb=None
    for prominence in (6,3):
        for method in ('straight','annular'):
            variant=f'{method}-0-joint{prominence}';dest=WORK/variant;p=replace(VARIANTS[f'{method}-0-joint'],recovery_prominence_dn=prominence)
            remaining=deadline-time.time()
            if remaining<120:save(OUT/'recovery-controls.json',dict(status='deadline-reserve',results=results));return
            cmd=[sys.executable,'-m','photo2.bead_detection.annular_detect','--output',str(dest)]
            for k,v in asdict(p).items():cmd.extend(['--'+k.replace('_','-'),str(v)])
            start=time.time()
            with (OUT/(variant+'.log')).open('w') as log:
                try:r=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=max(1,remaining-90))
                except subprocess.TimeoutExpired:save(OUT/'recovery-controls.json',dict(status='deadline',incomplete=variant,results=results));return
            if r.returncode:save(OUT/'recovery-controls.json',dict(status='failed',variant=variant,results=results));return
            data=json.loads((dest/'regions.json').read_text());save(dest/'complete.json',dict(generation_id=data['generation_id'],parameters=asdict(p)))
            rs=data['regions'];coords=np.array([q['location'] for q in rs]);ids={q['id'] for q in rs};landmarks=[]
            for m in visual['missing']:
                distances=np.linalg.norm(coords-m['approximate_review_location'],axis=1);j=int(distances.argmin());landmarks.append(dict(label=m['label'],distance=float(distances[j]),id=rs[j]['id']))
            row=dict(variant=variant,seconds=time.time()-start,regions=len(rs),suppressed=len(data['suppressed']),deferred=len(data['deferred']),landmarks=landmarks,review_duplicate_pairs_remaining=sum(all(k in ids for k in q['ids']) for q in visual['duplicates']),paper_window_pixels=sum(1992<=x<=1997 and 2628<=y<=2634 for q in rs for y,a,b in q['pixel_runs'] for x in range(a,b+1)),thin_pixels=sum(irregularity(q)['thin_pixels'] for q in rs));results.append(row)
            out=OUT/variant;out.mkdir(exist_ok=True)
            for name in ('summary.json','coordinates.csv'):(out/name).write_bytes((dest/name).read_bytes())
            with gzip.GzipFile(filename=str(out/'regions.json.gz'),mode='wb',mtime=0) as f:f.write((dest/'regions.json').read_bytes())
            with tarfile.open(out/'traces.tar','w') as tar:
                for trace in sorted((dest/'traces').glob('*.json.gz')):tar.add(trace,arcname='traces/'+trace.name)
            save(OUT/'recovery-controls.json',dict(status='running',results=results));print(variant,row['regions'],row['seconds'],flush=True)
    save(OUT/'recovery-controls.json',dict(status='complete',results=results))
if __name__=='__main__':main()
