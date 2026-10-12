"""Checkpointed R265 comparisons. Supervisor enforces one configurable wall deadline.

Evaluation labels/crops are used only by this module, never by repaired_detect.
Run: .venv/bin/python -m photo2.bead_detection.experiment_r265 --seconds 1800
"""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
import os
import subprocess
import sys
import time
from dataclasses import asdict, replace
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-r265-mpl')
import numpy as np
from PIL import Image, ImageOps, ImageDraw
from scipy import ndimage as ndi
from matplotlib.colors import rgb_to_hsv, hsv_to_rgb
from . import straight_detect_r265 as new
from . import bounded_detect as old
from .test_repaired import audit
ROOT=new.ROOT
WORK=ROOT/'photo2/output/r265'
OUT=ROOT/'photo2/review/r265'
VARIANTS={
 'old':new.Parameters(local_growth=False,valley_guard=False,local_retreat=False,background_precheck=False),
 'straight':new.Parameters(valley_guard=False,local_retreat=False,background_precheck=False),
 'straight_valley':new.Parameters(local_retreat=False,background_precheck=False),
 'retreat':new.Parameters(local_growth=False,valley_guard=False,background_precheck=False),
 'background':new.Parameters(local_growth=False,valley_guard=False,local_retreat=False),
 'straight_retreat':new.Parameters(valley_guard=False,background_precheck=False),
 'joint':new.Parameters(),
}


def save(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(obj,separators=(',',':'),allow_nan=False,default=lambda x:x.item())+'\n');tmp.replace(path)


def scenes():
    """Known disjoint bead footprints; touching ellipses have a narrow dark seam.

    Color, position, shadow and illumination vary independently. Labels are not
    supplied to detection. Multiple peaks deliberately do not imply two beads.
    """
    rng=np.random.default_rng(265)
    y,x=np.mgrid[:65,:97]
    for i in range(24):
        hue=(.08+i*.137)%1
        hsv=np.zeros((65,97,3));hsv[:]=[(hue+.47)%1,.4,.68]
        hsv[:,:,2]-=.28*np.exp(-((x-50)**2+(y-34)**2)/500)
        truth=np.zeros((65,97),np.int16);centers=[]
        bodies=[(30+i%3,31,17,19),(64+i%3,34,17,19)] if i<12 else [(34+i%3,31,12,14),(58+i%3,34,12,14)]
        for k,(cx,cy,rx,ry) in enumerate(bodies,1):
            d=((x-cx)/rx)**2+((y-cy)/ry)**2;body=d<=1
            truth[body]=k;centers.append([cx,cy])
            v=.92-.48*np.sqrt(np.minimum(d,1))
            if i%3==1:v-=.13*(x-cx)/rx
            if i%3==2:
                v=.48-.10*d+.38*np.exp(-((x-cx-6)**2+(y-cy)**2)/9)+.40*np.exp(-((x-cx+6)**2+(y-cy)**2)/9)
            hsv[body,0]=(hue+.12*(k-1))%1;hsv[body,1]=.8;hsv[body,2]=v[body]
            if i%12 in (3,7,11): # dark body plus specular peak, still known one bead
                hsv[body,1]=.05;hsv[body,2]=.12+.8*np.exp(-((x[body]-cx)**2+(y[body]-cy)**2)/8)
        rgb=np.round(hsv_to_rgb(hsv.clip(0,1))*255).astype(np.int16)
        if i%2:rgb+=rng.integers(-2,3,rgb.shape)
        rgb=np.clip(rgb,0,255).astype(np.uint8)
        yield f'scene-{i:02d}',rgb,truth,centers


def pixels(r):return {(x,y) for y,a,b in r['pixel_runs'] for x in range(a,b+1)}


def hole_diagnostics(r,t):
    x0,y0,x1,y1=r['bbox'];mask=np.zeros((y1-y0,x1-x0),bool)
    for y,a,b in r['pixel_runs']:mask[y-y0,a-x0:b-x0+1]=True
    yy,xx=np.where(ndi.binary_fill_holes(mask)&~mask)
    removed={tuple(a[:2]):i for i,a in enumerate(t['accepted']) if not a[7]}
    stopped={tuple(a[:2]) for a in t['stops']}
    out=dict(hole_removed_by_retreat=0,hole_stopped_during_growth=0,hole_unvisited=0)
    for x,y in zip(xx+x0,yy+y0):
        xy=(int(x),int(y))
        key='hole_removed_by_retreat' if xy in removed else 'hole_stopped_during_growth' if xy in stopped else 'hole_unvisited'
        out[key]+=1
    return out


def metrics(data):
    rs=data['regions'];holes=0;unexplained=0;disconnect=0;duplicate_coords=len(rs)-len({tuple(r['location']) for r in rs})
    for r in rs:
        x0,y0,x1,y1=r['bbox'];mask=np.zeros((y1-y0,x1-x0),bool)
        for y,a,b in r['pixel_runs']:mask[y-y0,a-x0:b-x0+1]=True
        holes+=int((ndi.binary_fill_holes(mask)&~mask).sum())
        disconnect+=ndi.label(mask,np.ones((3,3)))[1]!=1
        t=r.get('trace')
        if t:
            # Accepted pixels removed despite exceeding the corrected local cutoff.
            for a in t['accepted']:
                if not a[7] and a[3]>data['parameters']['dark_dn']+.3*(t['accepted'][0][3]-data['parameters']['dark_dn']):unexplained+=1
    pairs=0
    occupied={}
    for r in rs:
        for xy in pixels(r):occupied.setdefault(xy,[]).append(r['id'])
    counts={};areas={r['id']:r['pixel_count'] for r in rs}
    from itertools import combinations
    for ids in occupied.values():
        for a,b in combinations(ids,2):counts[a,b]=counts.get((a,b),0)+1
    pairs=sum(n/(areas[a]+areas[b]-n)>.5 for (a,b),n in counts.items())
    return dict(regions=len(rs),grown=len(rs)+len(data['rejected']),precheck_rejected=sum(m['reason']=='obvious-background-before-growth' for m in data['maxima']),
                size_limited=sum(r['size_limited'] for r in rs+data['rejected']),holes_native_pixels=holes,
                bright_removed_proxy=unexplained,disconnected=disconnect,identical_coordinate_extras=duplicate_coords,iou_over_half_pairs=pairs)


def compare_image(rgb,box,records,path,title):
    x0,y0,x1,y1=map(int,box);w=x1-x0;h=y1-y0;scale=max(2,min(5,650//max(w,h)))
    panels=[]
    for name,rs in [('raw',[])]+records:
        base=Image.fromarray(rgb[y0:y1,x0:x1]).convert('RGB')
        if rs:
            overlay=np.zeros((h,w,4),np.uint8)
            for r in rs:
                for y,a,b in r['pixel_runs']:
                    if y0<=y<y1:overlay[y-y0,max(a,x0)-x0:max(min(b+1,x1)-x0,0)]=[0,255,255,85] if a<x1 and b>=x0 else [0,0,0,0]
            base=Image.alpha_composite(base.convert('RGBA'),Image.fromarray(overlay)).convert('RGB')
        base=base.resize((w*scale,h*scale),Image.Resampling.NEAREST);draw=ImageDraw.Draw(base)
        for r in rs:
            x,y=r['location']
            if x0<=x<x1 and y0<=y<y1:
                xx=(x-x0+.5)*scale;yy=(y-y0+.5)*scale;draw.line((xx-4,yy,xx+4,yy),fill='white',width=1);draw.line((xx,yy-4,xx,yy+4),fill='white',width=1)
        panel=Image.new('RGB',(w*scale,h*scale+25),'#20252a');panel.paste(base,(0,25));ImageDraw.Draw(panel).text((5,7),name,fill='white');panels.append(panel)
    out=Image.new('RGB',(sum(p.width for p in panels),panels[0].height+25),'#20252a');d=ImageDraw.Draw(out);d.text((5,7),title,fill='white')
    xx=0
    for panel in panels:out.paste(panel,(xx,25));xx+=panel.width
    out.save(path)


def synthetic():
    results=[];truths={}
    for name,rgb,truth,centers in scenes():
        truths[name]=truth
        records={}
        for variant,p in VARIANTS.items():
            data,_,_=new.detect(rgb,p);records[variant]=data
            if p.local_growth:
                hsv=rgb_to_hsv(rgb/255.);v=rgb.max(axis=2)
                for r in data['regions']+data['rejected']:
                    t=r['trace'];x0,y0=t['mask_offset'];m=np.zeros((max(a[1] for a in t['accepted'])-y0+1,max(a[0] for a in t['accepted'])-x0+1),bool)
                    for a in t['accepted']:
                        if a[7]:m[a[1]-y0,a[0]-x0]=True
                    audit(v,hsv,m,t,p)
            m=metrics(data);assign=[int(truth[r['location'][1],r['location'][0]]) for r in data['regions']]
            m.update(scene=name,variant=variant,missed_known_bodies=sum(k not in assign for k in (1,2)),
                     duplicate_body_extras=sum(max(0,assign.count(k)-1) for k in (1,2)),
                     background_coordinates=assign.count(0),background_pixels=sum(truth[y,x]==0 for r in data['regions'] for x,y in pixels(r)),
                     neighbor_pixels=sum(truth[y,x] not in (0,truth[r['bright_patch']['peak'][1],r['bright_patch']['peak'][0]]) for r in data['regions'] for x,y in pixels(r)),
                     coordinate_errors=[float(np.linalg.norm(np.array(r['location'])-centers[k-1])) for r,k in zip(data['regions'],assign) if k])
            results.append(m)
        if name in ('scene-00','scene-01','scene-02','scene-03','scene-07','scene-12','scene-13','scene-14','scene-15'):
            compare_image(rgb,[0,0,97,65],[(k,records[k]['regions']) for k in ('old','joint')],OUT/f'{name}.png',name+' | known two bodies')
        save(OUT/'synthetic.json',dict(seed=265,results=results))
    np.savez_compressed(OUT/'synthetic-truth.npz',**truths)
    assert all(r['disconnected']==0 for r in results if r['variant']=='joint')


def photo():return np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'))


def targeted():
    rgb=photo();v=rgb.max(axis=2);hsv=rgb_to_hsv(rgb/255.)
    with gzip.open(ROOT/'photo2/review/r264/10/regions.json.gz','rt') as f:baseline=json.load(f)
    comp=json.loads((ROOT/'photo2/review/r264/comparison.json').read_text());cases=comp['cases'][:6]
    records=baseline['regions']+baseline['rejected']
    # Select old retained supports with most topological holes, plus the largest
    # R264 coordinate movements. These are evaluation targets, not detector priors.
    ranked=[]
    for r in baseline['regions']:
        x0,y0,x1,y1=r['bbox'];m=np.zeros((y1-y0,x1-x0),bool)
        for y,a,b in r['pixel_runs']:m[y-y0,a-x0:b-x0+1]=True
        ranked.append((int((ndi.binary_fill_holes(m)&~m).sum()),r['id'],r['location']))
    for score,rid,(x,y) in sorted(ranked,reverse=True)[:3]:cases.append(dict(name='auto-holes-'+rid,box=[x-35,y-35,x+36,y+36],selection_score=score))
    # Existing R264 stress crops were selected numerically by the R264 harness.
    cases+=comp['cases'][6:]
    selected=[r for r in records if any(c['box'][0]<=r['bright_patch']['peak'][0]<c['box'][2] and c['box'][1]<=r['bright_patch']['peak'][1]<c['box'][3] for c in cases)]
    valleys=new.valley_pixels(v);rows=[];outputs={k:[] for k in VARIANTS}
    for r in selected:
        for variant,p in VARIANTS.items():
            if variant=='background':continue # full-image detector stage evaluates the precheck
            mask,t=new.grow(v,hsv,tuple(r['bright_patch']['peak']),p,valleys=valleys if p.valley_guard else np.zeros((1,1),bool))
            if p.local_growth:audit(v,hsv,mask,t,p)
            x0,y0=t['mask_offset'];rec=dict(id=r['id'],**new.measure(mask,x0,y0),pixel_runs=new.runs(mask,x0,y0),size_limited=t['size_limited'])
            outputs[variant].append(rec)
            rows.append(dict(id=r['id'],variant=variant,location=rec['location'],centroid=rec['centroid'],area=rec['pixel_count'],growth=len(t['accepted']),size_limited=t['size_limited']))
    for c in cases:compare_image(rgb,c['box'],[(k,outputs[k]) for k in ('old','joint')],OUT/(c['name']+'.png'),c['name']+' | same source pixels; cyan support, white coordinate')
    save(OUT/'targeted.json',dict(cases=cases,seed_count=len(selected),rows=rows,note='Growth ablation on fixed R264 seeds; ignores pre/post background rejection here. Full stage evaluates retention.'))


def full(variant):
    path=WORK/variant;path.mkdir(parents=True,exist_ok=True)
    data=new.generate(ROOT/'beads-photo-2.jpg',path,VARIANTS[variant])
    # Save a completion checkpoint only after all outputs have been flushed.
    save(path/'complete.json',dict(variant=variant,generation=data['generation_id']))


def summarize():
    rgb=photo();v=rgb.max(axis=2);hsv=rgb_to_hsv(rgb/255.);results={};data_by={};audits={}
    for variant,p in VARIANTS.items():
        path=WORK/variant
        if not (path/'complete.json').exists():continue
        data=json.loads((path/'regions.json').read_text());accepted=stops=bright_removed=0;holes=dict(hole_removed_by_retreat=0,hole_stopped_during_growth=0,hole_unvisited=0)
        for r in data['regions']+data['rejected']:
            with gzip.open(path/r['trace_file'],'rt') as f:t=json.load(f)
            if p.local_growth:
                mx,my=t['mask_offset'];m=np.zeros((max(a[1] for a in t['accepted'])-my+1,max(a[0] for a in t['accepted'])-mx+1),bool)
                for a in t['accepted']:
                    if a[7]:m[a[1]-my,a[0]-mx]=True
                ac,st=audit(v,hsv,m,t,p);accepted+=ac;stops+=st
            if r['status']=='retained':
                for key,n in hole_diagnostics(r,t).items():holes[key]+=n
            bright_removed+=sum(not a[7] and a[3]>p.dark_dn+.3*(t['accepted'][0][3]-p.dark_dn) for a in t['accepted'])
        met=metrics(data);met['bright_removed_proxy']=bright_removed;met.update(holes)
        results[variant]=met;data_by[variant]=data;audits[variant]=dict(accepted=accepted,stops=stops,exact_audit=p.local_growth)
        save(OUT/'full-metrics.json',dict(metrics=results,audits=audits))
    if 'old' not in data_by or 'joint' not in data_by:return
    oldr={r['id']:r for r in data_by['old']['regions']};newr={r['id']:r for r in data_by['joint']['regions']}
    shifts=[dict(id=k,distance=float(np.linalg.norm(np.array(r['location'])-newr[k]['location'])),old=r['location'],new=newr[k]['location'],centroid_distance=float(np.linalg.norm(np.array(r['centroid'])-newr[k]['centroid']))) for k,r in oldr.items() if k in newr]
    shifts.sort(key=lambda r:(-r['distance'],r['id']))
    evidence=json.loads((ROOT/'photo2/review/r264/visual-review.json').read_text())
    coverage=[]
    for variant,data in data_by.items():
        coords=np.array([r['location'] for r in data['regions']]);ids={r['id'] for r in data['regions']}
        for m in evidence['missing']:
            dist=np.linalg.norm(coords-m['approximate_review_location'],axis=1);j=int(dist.argmin())
            coverage.append(dict(variant=variant,landmark=m['label'],confidence=m['confidence'],nearest_distance=float(dist[j]),nearest_id=data['regions'][j]['id'],within5=bool(dist[j]<=5),within10=bool(dist[j]<=10)))
        results[variant]['review_duplicate_pairs_remaining']=sum(all(k in ids for k in d['ids']) for d in evidence['duplicates'])
        results[variant]['paper_window_pixels']=sum(1992<=x<=1997 and 2628<=y<=2634 for r in data['regions'] for x,y in pixels(r))
    save(OUT/'full-metrics.json',dict(metrics=results,audits=audits))
    save(OUT/'photo-evaluation.json',dict(coordinate_shifts=shifts,added=sorted(newr.keys()-oldr.keys()),lost=sorted(oldr.keys()-newr.keys()),landmarks=coverage,
        warning='Landmark distance is a proximity proxy, not confirmed body coverage; duplicate pair retention is not a reverified identity. Paper window is an R264 visual judgment.'))
    for c in json.loads((OUT/'targeted.json').read_text())['cases']:
        compare_image(rgb,c['box'],[(k,data_by[k]['regions']) for k in ('old','joint')],OUT/(c['name']+'.png'),c['name']+' | retained supports; native pixels, white coordinates')
    for i,r in enumerate(shifts[:3]):
        x,y=r['old'];compare_image(rgb,[x-40,y-40,x+41,y+41],[(k,data_by[k]['regions']) for k in ('old','joint')],OUT/f'auto-shift-{i+1}.png',f"Largest movement {r['id']}: {r['distance']:.2f} px")
    # Compare generated old ablation to preserved R264 exactly for masks/coordinates.
    with gzip.open(ROOT/'photo2/review/r264/10/regions.json.gz','rt') as f:saved=json.load(f)
    fields=['id','location','centroid','pixel_runs','size_limited','status']
    exact=all([{k:r[k] for k in fields} for r in saved[group]]==[{k:r[k] for k in fields} for r in data_by['old'][group]] for group in ('regions','rejected'))
    assert exact,'old ablation does not reproduce R264'
    save(OUT/'baseline-replay.json',dict(exact_regions_rejected_masks_coordinates=exact,source_sha256=new.sha(ROOT/'photo2/bead_detection/bounded_detect.py')))
    # Curate compressed exact output; traces are reproducible and kept in ignored work.
    for variant in data_by:
        dest=OUT/variant;dest.mkdir(exist_ok=True)
        for name in ('summary.json','coordinates.csv'):(dest/name).write_bytes((WORK/variant/name).read_bytes())
        if variant=='joint':
            with gzip.GzipFile(filename=str(dest/'regions.json.gz'),mode='wb',mtime=0) as f:f.write((WORK/variant/'regions.json').read_bytes())
            import tarfile
            with tarfile.open(dest/'traces.tar','w') as tar:
                for trace in sorted((WORK/variant/'traces').glob('*.json.gz')):tar.add(trace,arcname='traces/'+trace.name)
    save(OUT/'manifest.json',dict(python=sys.version,dependency_versions={name:__import__(name).__version__ for name in ('numpy','scipy','skimage','PIL')},test_sha256=new.sha(Path(__file__).with_name('test_repaired.py')),image_sha256=new.sha(ROOT/'beads-photo-2.jpg'),detector_sha256=new.sha(new.__file__),harness_sha256=new.sha(__file__),parameters={k:asdict(v) for k,v in VARIANTS.items()}))


def supervise(seconds,resume=False):
    WORK.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
    start=time.monotonic();deadline=start+seconds
    state=dict(deadline_epoch=time.time()+seconds,budget_seconds=seconds,started_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),stages=[],status='running')
    if resume and (OUT/'checkpoint.json').exists():
        state=json.loads((OUT/'checkpoint.json').read_text())
        state.setdefault('deadline_epoch',__import__('datetime').datetime.fromisoformat(state['started_utc'].replace('Z','+00:00')).timestamp()+state['budget_seconds'])
        deadline=time.monotonic()+max(0,state['deadline_epoch']-time.time())
        start=deadline-state['budget_seconds'];state['status']='running'
    fingerprint=hashlib.sha256(''.join(new.sha(p) for p in [__file__,new.__file__,old.__file__,Path(__file__).with_name('test_repaired.py')]).encode()).hexdigest()
    passed={r['name'] for r in state['stages'] if r['status']=='passed' and r.get('input_sha256')==fingerprint}
    stages=[('units',[sys.executable,'-m','unittest','discover','-s','photo2/bead_detection','-t','.']),('synthetic',None),('targeted',None)]+[('full-'+k,None) for k in VARIANTS]+[('summarize',None)]
    for name,cmd in stages:
        if name in passed:continue
        remaining=deadline-time.monotonic()
        if remaining<=0:state['status']='deadline';break
        cmd=cmd or [sys.executable,'-m','photo2.bead_detection.experiment_r265','--stage',name,'--work',str(WORK),'--output',str(OUT)]
        now=time.monotonic()
        with (OUT/(name+'.log')).open('w') as log:
            proc=subprocess.Popen(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            try:code=proc.wait(timeout=remaining);status='passed' if code==0 else 'failed'
            except subprocess.TimeoutExpired:
                import signal
                os.killpg(proc.pid,signal.SIGTERM)
                try:proc.wait(timeout=min(2,max(.1,deadline-time.monotonic())))
                except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
                code=proc.returncode;status='deadline'
        current=hashlib.sha256(''.join(new.sha(p) for p in [__file__,new.__file__,old.__file__,Path(__file__).with_name('test_repaired.py')]).encode()).hexdigest()
        if current!=fingerprint:status='source-changed'
        state['stages'].append(dict(name=name,status=status,returncode=code,input_sha256=fingerprint,elapsed_seconds=time.monotonic()-now))
        state['elapsed_seconds']=time.monotonic()-start
        save(OUT/'checkpoint.json',state);print(name,status,round(state['elapsed_seconds'],2),flush=True)
        if status!='passed':state['status']=status;break
    else:state['status']='complete'
    state['elapsed_seconds']=time.monotonic()-start;save(OUT/'checkpoint.json',state)
    return 0 if state['status']=='complete' else 1


def main():
    global WORK,OUT
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--seconds',type=float,default=1800);ap.add_argument('--stage');ap.add_argument('--resume',action='store_true');ap.add_argument('--work',type=Path,default=WORK);ap.add_argument('--output',type=Path,default=OUT);a=ap.parse_args()
    WORK=a.work;OUT=a.output
    if a.stage:
        if a.stage.startswith('full-'):full(a.stage[5:])
        else:globals()[a.stage]()
    else:
        if a.seconds<=0:ap.error('seconds must be positive')
        raise SystemExit(supervise(a.seconds,a.resume))

if __name__=='__main__':main()
