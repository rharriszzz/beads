"""One additional bounded step: first neutral-dark stop and residual diagnostics."""
import argparse,gzip,json,os,subprocess,sys,time,tarfile
from pathlib import Path
import numpy as np
from matplotlib.colors import rgb_to_hsv
from . import repaired_detect as new
from .experiment_r265 import save,photo,compare_image,pixels,metrics
from .test_repaired import audit
ROOT=new.ROOT;OUT=ROOT/'photo2/review/r265-first-dark';WORK=ROOT/'photo2/output/r265-first-dark/joint'


def worker():
    data=new.generate(ROOT/'beads-photo-2.jpg',WORK)
    before=json.loads((ROOT/'photo2/output/r265/joint/regions.json').read_text())
    rgb=photo();hsv=rgb_to_hsv(rgb/255.);v=rgb.max(axis=2);p=new.Parameters();counts=[0,0]
    for r in data['regions']+data['rejected']:
        t=json.load(gzip.open(WORK/r['trace_file'],'rt'));mx,my=t['mask_offset']
        mask=np.zeros((max(a[1] for a in t['accepted'])-my+1,max(a[0] for a in t['accepted'])-mx+1),bool)
        for a in t['accepted']:
            if a[7]:mask[a[1]-my,a[0]-mx]=True
            q=hsv[a[1],a[0]]
            assert not (a[3]<=min(p.dark_dn,p.black_peak_fraction*t['accepted'][0][3]) and new.neutral_gray(q,p))
        ac,st=audit(v,hsv,mask,t,p);counts[0]+=ac;counts[1]+=st
    oldr={r['id']:r for r in before['regions']};newr={r['id']:r for r in data['regions']}
    changed=[k for k in oldr.keys()&newr.keys() if oldr[k]['pixel_runs']!=newr[k]['pixel_runs']]
    moved=[k for k in oldr.keys()&newr.keys() if oldr[k]['location']!=newr[k]['location']]
    dark_seeds=[m for m in data['maxima'] if m['reason']=='first-dark-seed']
    for m in [m for m in before['maxima'] if m['meaningful'] and m['value_dn']<=81]:
        x,y=m['peak'];compare_image(rgb,[x-25,y-25,x+26,y+26],[('before',before['regions']),('first dark',data['regions'])],OUT/(m['region_id']+'.png'),m['region_id']+' | dim seed review; no material label')
    ev=json.loads((ROOT/'photo2/review/r265/photo-evaluation.json').read_text())
    ids={r['id'] for r in ev['coordinate_shifts'][:3]}|set(ev['lost'])
    ids|={r['id'] for r in data['regions'] if any(1992<=x<=1997 and 2628<=y<=2634 for x,y in pixels(r))}
    byid={r['id']:r for r in data['regions']+data['rejected']};model=data['background']['hsv_seed_model'];c=np.array(model['center']);tol=np.array(model['tolerance']);diagnostics=[]
    for rid in sorted(ids):
        r=byid[rid];x,y=r['bright_patch']['peak'];q=hsv[y-1:y+2,x-1:x+2];delta=abs(q-c);delta[:,:,0]=abs((q[:,:,0]-c[0]+.5)%1-.5)
        diagnostics.append(dict(id=rid,seed=[x,y],rgb=rgb[y,x].tolist(),hsv=hsv[y,x].tolist(),channel_match_fraction=(delta<=tol).mean(axis=(0,1)).tolist(),all_channels_match_fraction=float(np.all(delta<=tol,axis=2).mean()),status=r['status'],reason=r['rejected_reasons']))
    paper=sum(1992<=x<=1997 and 2628<=y<=2634 for r in data['regions'] for x,y in pixels(r))
    result=dict(generation_id=data['generation_id'],parameters=data['parameters'],accepted_audited=counts[0],stops_audited=counts[1],regions=len(data['regions']),grown=len(data['regions'])+len(data['rejected']),first_dark_seeds=dark_seeds,changed_masks=sorted(changed),moved_coordinates=sorted(moved),lost=sorted(oldr.keys()-newr.keys()),added=sorted(newr.keys()-oldr.keys()),paper_window_pixels=paper,background_diagnostics=diagnostics,metrics=metrics(data),source_sha256=new.sha(new.__file__),image_sha256=new.sha(ROOT/'beads-photo-2.jpg'))
    save(OUT/'results.json',result)
    with gzip.GzipFile(filename=str(OUT/'regions.json.gz'),mode='wb',mtime=0) as f:f.write((WORK/'regions.json').read_bytes())
    with tarfile.open(OUT/'traces.tar','w') as tar:
        for path in sorted((WORK/'traces').glob('*.json.gz')):tar.add(path,arcname='traces/'+path.name)
    for name in ('summary.json','coordinates.csv'):(OUT/name).write_bytes((WORK/name).read_bytes())


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--worker',action='store_true');ap.add_argument('--seconds',type=float,default=300);ap.add_argument('--deadline-from',type=Path);a=ap.parse_args();OUT.mkdir(parents=True,exist_ok=True)
    if a.worker:worker();return
    start=time.time();deadline=start+a.seconds
    if a.deadline_from:deadline=min(deadline,json.loads(a.deadline_from.read_text())['deadline_epoch'])
    state=dict(started_epoch=start,deadline_epoch=deadline,stages=[],status='running')
    stages=[('tests',[sys.executable,'-m','unittest','discover','-s','photo2/bead_detection','-t','.']),('comparison',[sys.executable,'-m','photo2.bead_detection.first_dark_r265','--worker'])]
    for name,cmd in stages:
        remaining=deadline-time.time()
        if remaining<=0:state['status']='deadline';break
        with (OUT/(name+'.log')).open('w') as log:
            proc=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            try:code=proc.wait(timeout=remaining)
            except subprocess.TimeoutExpired:
                import signal
                os.killpg(proc.pid,signal.SIGTERM)
                try:proc.wait(timeout=.1)
                except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
                code=-1;state['status']='deadline'
        state['stages'].append(dict(stage=name,returncode=code));state['elapsed_seconds']=time.time()-start;save(OUT/'checkpoint.json',state)
        if code:
            if state['status']!='deadline':state['status']='failed'
            break
    else:state['status']='complete'
    state['elapsed_seconds']=time.time()-start;save(OUT/'checkpoint.json',state)
    raise SystemExit(0 if state['status']=='complete' else 1)

if __name__=='__main__':main()
