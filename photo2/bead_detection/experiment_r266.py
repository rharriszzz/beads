"""R266 deadline-controlled ablations, known truth and photographic diagnostics.

All named locations are evaluation-only. Detector consumes RGB and parameters.
A stage commits completion only after full output; timed-out stages stay incomplete.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,json,os,signal,subprocess,sys,time,tarfile
from pathlib import Path
from dataclasses import asdict,replace
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-r266-mpl')
import numpy as np
from PIL import Image,ImageOps,ImageDraw
from scipy import ndimage as ndi
from matplotlib.colors import rgb_to_hsv,hsv_to_rgb
from . import annular_detect as d
from . import repaired_detect as baseline
from .experiment_r265 import scenes,pixels,metrics,save
from .test_annular import audit
ROOT=d.ROOT;WORK=ROOT/'photo2/output/r266';OUT=ROOT/'photo2/review/r266'
VARIANTS={f'{method}-{rise}':d.Parameters(method=method,rise_budget_dn=rise) for method in ('straight','annular') for rise in range(4)}
VARIANTS.update({
 'straight-2-peaks':d.Parameters(rise_budget_dn=2,peak_selection=True),
 'straight-2-background':d.Parameters(rise_budget_dn=2,background_guard=True),
 'straight-2-recovery':d.Parameters(rise_budget_dn=2,recover_peaks=True),
 'straight-2-joint':d.Parameters(rise_budget_dn=2,peak_selection=True,background_guard=True,recover_peaks=True),
 'annular-2-joint':d.Parameters(method='annular',rise_budget_dn=2,peak_selection=True,background_guard=True,recover_peaks=True,split_regions=True),
 'straight-0-joint':d.Parameters(peak_selection=True,background_guard=True,recover_peaks=True),
 'annular-0-joint':d.Parameters(method='annular',peak_selection=True,background_guard=True,recover_peaks=True,split_regions=True),
})


def photo():return np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'))

def all_records(data):return sum([data.get(k,[]) for k in ('regions','rejected','suppressed','deferred')],[])


def outline_image(rgb,box,records,path,title):
    """Unaltered native photograph with thin cyan edges; separate raw panel."""
    x0,y0,x1,y1=map(int,box);h,w=y1-y0,x1-x0;scale=max(2,min(5,400//max(w,h)))
    panels=[]
    for name,rs in [('original',[])]+records:
        im=Image.fromarray(rgb[y0:y1,x0:x1]).resize((w*scale,h*scale),Image.Resampling.NEAREST);draw=ImageDraw.Draw(im)
        for r in rs:
            for contour in r.get('contours',[]):
                if len(contour)>1:draw.line([((x-x0+.5)*scale,(y-y0+.5)*scale) for x,y in contour],fill='#00f4ff',width=1)
            x,y=r['location']
            if x0<=x<x1 and y0<=y<y1:
                xx,yy=(x-x0+.5)*scale,(y-y0+.5)*scale
                draw.line((xx-3,yy,xx+3,yy),fill='white');draw.line((xx,yy-3,xx,yy+3),fill='white')
                draw.text((xx+3,yy-10),r['id'][1:],fill='#6fffff',stroke_width=1,stroke_fill='black')
        panel=Image.new('RGB',(w*scale,h*scale+24),'#20252a');panel.paste(im,(0,24));ImageDraw.Draw(panel).text((5,5),name,fill='white');panels.append(panel)
    out=Image.new('RGB',(sum(p.width for p in panels),panels[0].height+28),'#20252a');ImageDraw.Draw(out).text((5,7),title,fill='white');xx=0
    for panel in panels:out.paste(panel,(xx,28));xx+=panel.width
    out.save(path)


def irregularity(r):
    x0,y0,x1,y1=r['bbox'];m=np.zeros((y1-y0+2,x1-x0+2),bool)
    for y,a,b in r['pixel_runs']:m[y-y0+1,a-x0+1:b-x0+2]=True
    neighbors=ndi.convolve(m.astype(np.uint8),np.ones((3,3),np.uint8),mode='constant')-m
    edge=m & ~ndi.binary_erosion(m)
    return dict(perimeter_area=float(edge.sum()/max(m.sum(),1)),thin_pixels=int((m & (neighbors<=2)).sum()))


def truth_metrics(data,truth,centers):
    rs=data['regions'];assign=[int(truth[r['location'][1],r['location'][0]]) for r in rs]
    result=dict(missing=sum(k not in assign for k in (1,2)),duplicates=sum(max(0,assign.count(k)-1) for k in (1,2)),background_coordinates=assign.count(0),
      background_pixels=sum(int(truth[y,x]==0) for r in rs for x,y in pixels(r)),neighbor_pixels=sum(int(truth[y,x] not in (0,truth[r['bright_patch']['peak'][1],r['bright_patch']['peak'][0]])) for r in rs for x,y in pixels(r)),
      coordinate_errors=[float(np.linalg.norm(np.array(r['location'])-centers[k-1])) for r,k in zip(rs,assign) if k],deferred=len(data['deferred']),suppressed=len(data['suppressed']))
    result['false_suppression_cross_body']=sum(truth[r['bright_patch']['peak'][1],r['bright_patch']['peak'][0]]!=truth[next(q for q in rs if q['id']==r['suppressed_by'])['bright_patch']['peak'][1],next(q for q in rs if q['id']==r['suppressed_by'])['bright_patch']['peak'][0]] for r in data['suppressed'])
    return result


def synthetic():
    rows=[];truths={};audits=dict(accepted=0,stops=0)
    for name,rgb,truth,centers in scenes():
        truths[name]=truth;records={}
        for variant,p in VARIANTS.items():
            data,_,_=d.detect(rgb,p);records[variant]=data
            for r in all_records(data):
                t=r['trace'];mx,my=t['mask_offset'];m=np.zeros((max(a[1] for a in t['accepted'])-my+1,max(a[0] for a in t['accepted'])-mx+1),bool)
                for a in t['accepted']:
                    if a[7]:m[a[1]-my,a[0]-mx]=True
                na,ns=audit(rgb.max(axis=2),rgb_to_hsv(rgb/255.),m,t,p);audits['accepted']+=na;audits['stops']+=ns
            rows.append(dict(scene=name,variant=variant,**truth_metrics(data,truth,centers)))
        if name in ('scene-02','scene-03','scene-12','scene-13','scene-14','scene-15'):
            outline_image(rgb,[0,0,97,65],[(k,records[k]['regions']) for k in ('straight-0','straight-0-joint','annular-0-joint')],OUT/(name+'.png'),name+' | known two bodies')
        save(OUT/'synthetic.json',dict(seed=265,results=rows,audits=audits))
    np.savez_compressed(OUT/'synthetic-truth.npz',**truths)
    assert not any(r['false_suppression_cross_body'] for r in rows),'cross-body synthetic suppression'


def full(variant):
    dest=WORK/variant;dest.mkdir(parents=True,exist_ok=True)
    data=d.generate(ROOT/'beads-photo-2.jpg',dest,VARIANTS[variant])
    save(dest/'complete.json',dict(variant=variant,generation_id=data['generation_id'],fingerprint=fingerprint()))


def fingerprint():
    sources=[__file__,d.__file__,baseline.__file__,Path(__file__).with_name('test_annular.py')]
    return hashlib.sha256(''.join(d.sha(p) for p in sources).encode()).hexdigest()


def stability():
    """Palette rotations, placement translations, native noise; seeded truth only."""
    rows=[];rng=np.random.default_rng(266)
    for name,rgb,truth,centers in scenes():
        if int(name[-2:])<12:continue
        for change in ('original','hue90','shift','noise1','noise2','noise3'):
            im=rgb.copy();tr=truth.copy();cs=np.array(centers)
            if change=='hue90':
                hsv=rgb_to_hsv(im/255.);hsv[:,:,0]=(hsv[:,:,0]+.25)%1;im=np.round(hsv_to_rgb(hsv)*255).astype(np.uint8)
            elif change=='shift':im=np.roll(im,3,axis=1);tr=np.roll(tr,3,axis=1);cs=cs+[3,0]
            elif change.startswith('noise'):
                n=int(change[-1]);im=np.clip(im.astype(int)+rng.integers(-n,n+1,im.shape),0,255).astype(np.uint8)
            for variant in ('straight-0','straight-2','annular-2','straight-0-joint','annular-0-joint'):
                data,_,_=d.detect(im,VARIANTS[variant]);rows.append(dict(scene=name,change=change,variant=variant,**truth_metrics(data,tr,cs)))
            save(OUT/'stability.json',dict(seed=266,results=rows))


def summarize():
    rgb=photo();hsv=rgb_to_hsv(rgb/255.);v=rgb.max(axis=2)
    visual=json.loads((ROOT/'photo2/review/r264/visual-review.json').read_text())
    cases=[dict(name=c['name'],box=c['box']) for c in json.loads((ROOT/'photo2/review/r264/comparison.json').read_text())['cases']]
    evidence={};met={};landmarks=[];per_region={};audits={};baseline_records=None
    for variant,p in VARIANTS.items():
        dest=WORK/variant
        if not (dest/'complete.json').exists():continue
        data=json.loads((dest/'regions.json').read_text());rs=data['regions'];evidence[variant]=rs
        m=metrics(data);m.update(deferred=len(data['deferred']),suppressed=len(data['suppressed']),split_parents=len(data['split_evidence']),recovered_selected=sum(r['bright_patch']['recovered_low_prominence'] for r in rs))
        ids={r['id'] for r in rs};coords=np.array([r['location'] for r in rs]);m['review_duplicate_pairs_remaining']=sum(all(k in ids for k in row['ids']) for row in visual['duplicates'])
        m['paper_window_pixels']=sum(1992<=x<=1997 and 2628<=y<=2634 for r in rs for x,y in pixels(r))
        irr={r['id']:irregularity(r) for r in rs};m['thin_pixels']=sum(q['thin_pixels'] for q in irr.values());m['mean_perimeter_area']=float(np.mean([q['perimeter_area'] for q in irr.values()]));met[variant]=m
        per_region[variant]={r['id']:dict(location=r['location'],centroid=r['centroid'],area=r['pixel_count'],**irr[r['id']]) for r in rs}
        for item in visual['missing']:
            dist=np.linalg.norm(coords-item['approximate_review_location'],axis=1);j=int(dist.argmin());landmarks.append(dict(variant=variant,label=item['label'],nearest_id=rs[j]['id'],distance=float(dist[j]),confidence=item['confidence']))
        accepted=stopped=0
        # Full audit every saved proposed support, including suppressed and deferred.
        for r in all_records(data):
            with gzip.open(dest/r['trace_file'],'rt') as f:t=json.load(f)
            mx,my=t['mask_offset'];mask=np.zeros((max(a[1] for a in t['accepted'])-my+1,max(a[0] for a in t['accepted'])-mx+1),bool)
            for a in t['accepted']:
                if a[7]:mask[a[1]-my,a[0]-mx]=True
            na,ns=audit(v,hsv,mask,t,p);accepted+=na;stopped+=ns
        audits[variant]=dict(accepted=accepted,stops=stopped)
        out=OUT/variant;out.mkdir(exist_ok=True)
        for name in ('summary.json','coordinates.csv'):(out/name).write_bytes((dest/name).read_bytes())
        with gzip.GzipFile(filename=str(out/'regions.json.gz'),mode='wb',mtime=0) as f:f.write((dest/'regions.json').read_bytes())
        # Archive all variants: exact comparison replay survives ignored work cleanup.
        with tarfile.open(out/'traces.tar','w') as tar:
            for path in sorted((dest/'traces').glob('*.json.gz')):tar.add(path,arcname='traces/'+path.name)
        save(OUT/'metrics.json',dict(variants=met,audits=audits,landmarks=landmarks))
    for c in cases:
        outline_image(rgb,c['box'],[(k,evidence[k]) for k in ('straight-0','straight-0-joint','annular-0-joint')],OUT/(c['name']+'.png'),c['name']+' | coordinates, not verified centers')
    # Paired common-identity numerical proxies, never called measured bead error.
    deltas=[];before=per_region['straight-0']
    for variant in ('straight-2','annular-2','straight-0-joint','annular-0-joint'):
        after=per_region[variant]
        for rid in before.keys() & after.keys():
            a,b=before[rid],after[rid];deltas.append(dict(variant=variant,id=rid,shift=float(np.linalg.norm(np.array(a['location'])-b['location'])),thin_delta=b['thin_pixels']-a['thin_pixels'],irregularity_delta=b['perimeter_area']-a['perimeter_area'],before=a,after=b))
    save(OUT/'coordinate-comparison.json',dict(rows=deltas,warning='Coordinate shift and irregularity are stability proxies; identity and physical centers are not truth-labeled.'))
    ranked={}
    for label,reverse in [('improvements',False),('regressions',True)]:
        items=sorted([r for r in deltas if r['variant']=='annular-0-joint'],key=lambda r:(r['irregularity_delta'],r['thin_delta']),reverse=reverse)[:3];ranked[label]=items
        for i,row in enumerate(items):
            x,y=row['before']['location'];outline_image(rgb,[max(0,x-35),max(0,y-35),min(rgb.shape[1],x+36),min(rgb.shape[0],y+36)],[(k,evidence[k]) for k in ('straight-0','annular-0-joint')],OUT/f'auto-{label}-{i+1}.png',f"{label} proxy {row['id']} | perimeter/area delta {row['irregularity_delta']:.3f}")
    save(OUT/'ranked-examples.json',ranked)
    save(OUT/'cases.json',cases)
    # Exact baseline replay includes all original seeds, masks and coordinates.
    with gzip.open(ROOT/'photo2/review/r265-first-dark/regions.json.gz','rt') as f:old=json.load(f)
    current=json.loads((WORK/'straight-0/regions.json').read_text())
    fields=['id','location','centroid','pixel_runs','status']
    exact=all([{k:r[k] for k in fields} for r in old[group]]==[{k:r[k] for k in fields} for r in current[group]] for group in ('regions','rejected'))
    save(OUT/'baseline-replay.json',dict(exact=exact));assert exact
    save(OUT/'manifest.json',dict(image_sha256=d.sha(ROOT/'beads-photo-2.jpg'),detector_sha256=d.sha(d.__file__),baseline_sha256=d.sha(baseline.__file__),harness_sha256=d.sha(__file__),test_sha256=d.sha(Path(__file__).with_name('test_annular.py')),python=sys.version,parameters={k:asdict(v) for k,v in VARIANTS.items()}))


def supervise(seconds,resume):
    OUT.mkdir(parents=True,exist_ok=True);WORK.mkdir(parents=True,exist_ok=True)
    state=dict(started_epoch=time.time(),deadline_epoch=time.time()+seconds,budget_seconds=seconds,stages=[],status='running')
    if resume and (OUT/'checkpoint.json').exists():state=json.loads((OUT/'checkpoint.json').read_text())
    fp=fingerprint();passed={r['name'] for r in state['stages'] if r['status']=='passed' and r['fingerprint']==fp}
    stages=['units','synthetic']+['full-'+k for k in VARIANTS]+['stability','summarize']
    save(OUT/'checkpoint.json',state)
    for stage in stages:
        if stage in passed:continue
        remaining=state['deadline_epoch']-time.time()
        if remaining<=0:state['status']='deadline';break
        cmd=[sys.executable,'-m','unittest','discover','-s','photo2/bead_detection','-t','.'] if stage=='units' else [sys.executable,'-m','photo2.bead_detection.experiment_r266','--stage',stage,'--work',str(WORK),'--output',str(OUT)]
        start=time.monotonic()
        with (OUT/(stage+'.log')).open('w') as log:
            proc=subprocess.Popen(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            try:code=proc.wait(timeout=remaining);status='passed' if code==0 else 'failed'
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid,signal.SIGTERM)
                try:proc.wait(timeout=1)
                except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
                code=proc.returncode;status='deadline'
        if fingerprint()!=fp:status='source-changed'
        state['stages'].append(dict(name=stage,status=status,returncode=code,seconds=time.monotonic()-start,fingerprint=fp));state['elapsed_seconds']=time.time()-state['started_epoch'];save(OUT/'checkpoint.json',state)
        print(stage,status,round(state['elapsed_seconds'],2),flush=True)
        if status!='passed':state['status']=status;break
    else:state['status']='complete'
    state['elapsed_seconds']=time.time()-state['started_epoch'];save(OUT/'checkpoint.json',state)
    return state['status']=='complete'


def main():
    global WORK,OUT
    ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,default=1800);ap.add_argument('--resume',action='store_true');ap.add_argument('--stage');ap.add_argument('--work',type=Path,default=WORK);ap.add_argument('--output',type=Path,default=OUT);a=ap.parse_args();WORK=a.work;OUT=a.output
    if a.stage:
        if a.stage.startswith('full-'):full(a.stage[5:])
        else:globals()[a.stage]()
    else:
        if a.seconds<=0:ap.error('positive seconds required')
        raise SystemExit(0 if supervise(a.seconds,a.resume) else 1)
if __name__=='__main__':main()
