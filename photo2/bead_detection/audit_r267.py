"""R267 photographic seed audit. No detector modifications or bead identities.

Crop boxes choose diagnostics only. Native regional maxima are computed on the
whole image. Every plateau pixel is measured; old IDs name plateaus, not beads.
"""
from __future__ import annotations
import copy, csv, gzip, hashlib, json, time
from pathlib import Path
from unittest.mock import patch
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi
from skimage.morphology import local_maxima
from matplotlib.colors import rgb_to_hsv
from .experiment_r266 import ROOT, photo
from . import refine_r266 as ref

OUT=ROOT/'photo2/review/r267'
METRICS=['square5','square7','square9','disk2','disk3','disk4']
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

def save(path,data):
    path.write_text(json.dumps(data,indent=2)+'\n')

def csvsave(path,rows):
    if not rows:return
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)

def averages(value,x,y):
    out={}
    for r in (2,3,4):
        yy,xx=np.mgrid[-r:r+1,-r:r+1];v=value[y-r:y+r+1,x-r:x+r+1].astype(float)
        assert v.shape==xx.shape, 'Audit neighborhood must be inside photograph'
        out[f'square{2*r+1}']=float(v.mean())
        out[f'disk{r}']=float(v[xx*xx+yy*yy<=r*r].mean())
    return out

def exact_prominence(value,points,box):
    """Topographic drop to a component containing a strictly higher pixel.

    Descending connected superlevel sets; certify no path escaped the ROI above
    the merger level, otherwise enlarge ROI. Equal global maxima use image range,
    matching the h-maxima convention. No watershed/catchment/identity assignment.
    """
    h,w=value.shape;answers={};peak=np.array([int(value[y,x]) for x,y in points]);globalmax=int(value.max());globalmin=int(value.min())
    for i,v in enumerate(peak):
        if v==globalmax:answers[i]=(globalmax-globalmin,globalmin,'global-maximum/image-range')
    halo=32
    while len(answers)<len(points):
        x0,y0,x1,y1=box;a,b=max(0,x0-halo),max(0,y0-halo);c,d=min(w,x1+halo),min(h,y1+halo)
        v=value[b:d,a:c];xy=np.array(points)-[a,b];escaped=np.zeros(len(points),bool)
        unresolved=set(range(len(points)))-answers.keys()
        for level in range(int(v.max()),int(v.min())-1,-1):
            labels,n=ndi.label(v>=level,np.ones((3,3)))
            top=ndi.maximum(v,labels,np.arange(n+1))
            ids=labels[xy[:,1],xy[:,0]]
            border=np.zeros(n+1,bool)
            if a>0:border[labels[:,0]]=True
            if b>0:border[labels[0]]=True
            if c<w:border[labels[:,-1]]=True
            if d<h:border[labels[-1]]=True
            for i in list(unresolved):
                if peak[i]<level:continue
                if top[ids[i]]>peak[i]:
                    if not escaped[i]:answers[i]=(int(peak[i]-level),level,f'certified-halo-{halo}')
                    unresolved.remove(i)
                elif border[ids[i]]:escaped[i]=True
            if not unresolved:break
        if len(answers)==len(points):break
        assert not(a==0 and b==0 and c==w and d==h), 'Unresolved full-image maximum'
        halo*=2
    return [answers[i] for i in range(len(points))]

def rank(rows):
    for key in METRICS:
        values=sorted({r[key] for r in rows},reverse=True)
        ranks={v:1+sum(r[key]>v for r in rows) for v in values}
        for r in rows:r['rank_'+key]=ranks[r[key]]

def inside(x,y,box):return box[0]<=x<box[2] and box[1]<=y<box[3]

def color(rank,n):
    # Fixed rank-percentile bins, readable against both paper and beads.
    return '#00ffff' if rank<=max(1,n*.1) else '#72ff64' if rank<=n*.25 else '#ffe45c' if rank<=n*.5 else '#ff9652' if rank<=n*.75 else '#e98bff'

def map_image(rgb,box,rows,key,path,title,number_key='number',rank_population=None):
    x0,y0,x1,y1=box;scale=18;top=82;w=(x1-x0)*scale;h=(y1-y0)*scale
    im=Image.new('RGB',(w,h+top),'#172028');im.paste(Image.fromarray(rgb[y0:y1,x0:x1]).resize((w,h),Image.Resampling.NEAREST),(0,top));d=ImageDraw.Draw(im);font=ImageFont.truetype(FONT,16)
    d.text((12,8),title,fill='white',font=font)
    d.text((12,32),'Rank: cyan top 10% | green 25% | yellow 50% | orange 75% | purple rest',fill='white',font=font)
    d.text((12,55),'Number = maximum pixel, not bead. Full native photograph; no outlines.',fill='white',font=font)
    occupied=[];markerboxes=[];placements=[]
    for r in rows:
        px=(r['x']-x0+.5)*scale;py=(r['y']-y0+.5)*scale+top;markerboxes.append((px-4,py-4,px+4,py+4))
    def overlaps(a,b):return a[0]<b[2] and a[2]>b[0] and a[1]<b[3] and a[3]>b[1]
    for r,mb in zip(rows,markerboxes):
        px=(mb[0]+mb[2])/2;py=(mb[1]+mb[3])/2;label=str(r[number_key]);bw=d.textbbox((0,0),label,font=font)[2]+6;bh=22
        chosen=None
        for radius in range(10,600,9):
            for angle in np.linspace(-np.pi/2,3*np.pi/2,24,endpoint=False):
                lx=int(px+radius*np.cos(angle)-bw/2);ly=int(py+radius*np.sin(angle)-bh/2);b=(lx,ly,lx+bw,ly+bh)
                if lx<1 or ly<top+1 or b[2]>=w or b[3]>=h+top:continue
                if any(overlaps(b,z) for z in occupied+markerboxes):continue
                chosen=b;break
            if chosen:break
        assert chosen is not None,'Label packing failed'
        occupied.append(chosen);placements.append((r,px,py,chosen))
    for r,px,py,b in placements:
        col=color(r['rank_'+key],rank_population or len(rows));cx=(b[0]+b[2])/2;cy=(b[1]+b[3])/2
        d.line((px,py,cx,cy),fill=col,width=1)
    for r,px,py,b in placements:
        col=color(r['rank_'+key],rank_population or len(rows));d.rectangle(b,fill='#101820');d.text((b[0]+3,b[1]+1),str(r[number_key]),fill=col,font=font)
        d.ellipse((px-3,py-3,px+3,py+3),outline='black',width=1);d.point((px,py),fill=col);d.line((px-4,py,px+4,py),fill=col);d.line((px,py-4,px,py+4),fill=col)
    im.save(path)
    assert all(not overlaps(a,b) for i,a in enumerate(occupied) for b in occupied[i+1:])
    return dict(labels=len(rows),overlapping_labels=0,labels_covering_maximum_markers=0)

def run():
    started=time.time();OUT.mkdir(exist_ok=True);rgb=photo();value=rgb.max(axis=2);hsv=rgb_to_hsv(rgb/255.)
    cases=[c for c in json.loads((ROOT/'photo2/review/r264/comparison.json').read_text())['cases'] if c['name'] in ('R00956','R01284')]
    boxes={c['name']:c['box'] for c in cases}
    inputs=[ROOT/'beads-photo-2.jpg',ROOT/'photo2/review/r264/comparison.json']
    snapshots={};maxima=None;source_records={}
    for method in ('straight','annular'):
        for threshold in (12,6,3):
            name=f'{method}-0-selected{threshold}';p=ROOT/'photo2/review/r266'/name/'regions.json.gz';inputs.append(p)
            data=json.load(gzip.open(p));byid={r['id']:r for k in ('regions','rejected','suppressed','deferred') for r in data[k]}
            snapshots[name]={}
            for m in data['maxima']:
                x,y=m['peak']
                if not any(inside(x,y,[b[0]-40,b[1]-40,b[2]+40,b[3]+40]) for b in boxes.values()):continue
                r=byid.get(m['region_id'],{});snap=dict(status=m['status'],reason=m['reason'],suppressed_by=r.get('suppressed_by'),location=r.get('location'),score=r.get('peak_quality'),rejected_reasons=r.get('rejected_reasons'),background=r.get('background_evidence'),pixel_count=r.get('pixel_count'),peak=m['peak'],prominence_lower_bound=m['prominence_lower_bound_dn'],meaningful=m['meaningful'])
                snapshots[name][m['region_id']]=snap
            if name=='straight-0-selected12':
                maxima=data['maxima'];source_records={k:v for k,v in byid.items() if k in snapshots[name]}
                save(OUT/'r266-parameters.json',dict(parameters=data['parameters'],association_parameters=data['association_parameters'],generation_id=data['generation_id']))
                save(OUT/'r266-local-associations.json',[r for r in data['associations'] if any(i in snapshots[name] for i in r['ids'])])
            del data
    save(OUT/'r266-statuses.json',snapshots)
    raw=local_maxima(value,connectivity=2,allow_borders=True)
    summaries={};allselection={}
    for name,box in boxes.items():
        x0,y0,x1,y1=box;records=[];plateaus=[];savedmask=np.zeros((y1-y0,x1-x0),bool)
        # Include intersecting plateaus even if the old representative is outside.
        for m in maxima:
            pts=[(x,y) for y,a,b in m['plateau_runs'] if y0<=y<y1 for x in range(max(a,x0),min(b+1,x1))]
            if not pts:continue
            for x,y in pts:savedmask[y-y0,x-x0]=True
            plateaus.append(m)
            for x,y in pts:
                r=dict(number=0,plateau_id=m['region_id'],x=x,y=y,old_peak_pixel=[x,y]==m['peak'],peak_v=int(value[y,x]),h_deg=float(hsv[y,x,0]*360),s=float(hsv[y,x,1]),plateau_pixels=m['plateau_pixel_count'],**averages(value,x,y))
                for short,runname in [('old12','straight-0-selected12'),('old6','straight-0-selected6'),('old3','straight-0-selected3')]:
                    q=snapshots[runname].get(m['region_id'],{});r[short+'_status']=q.get('status','representative-outside-audit-halo');r[short+'_reason']=q.get('reason','');r[short+'_suppressed_by']=q.get('suppressed_by') or ''
                snap=snapshots['straight-0-selected12'].get(m['region_id'],{})
                score=snap.get('score') or {}
                r['old12_prominence_lower_bound']=m['prominence_lower_bound_dn']
                r['old12_score']=score.get('score','')
                r['old12_median7']=score.get('neighborhood_median_dn','')
                r['old12_p25_7']=score.get('neighborhood_p25_dn','')
                r['old12_location']=snap.get('location')
                r['old12_stale_reason']=r['old12_status']=='retained' and 'inferior' in r['old12_reason']
                records.append(r)
        assert np.array_equal(savedmask,raw[y0:y1,x0:x1]), 'Saved maxima must match independent full-image extraction'
        prom=exact_prominence(value,[m['peak'] for m in plateaus],box);byid={m['region_id']:p for m,p in zip(plateaus,prom)}
        records.sort(key=lambda r:(r['y'],r['x']))
        for i,r in enumerate(records,1):
            r['number']=i;r['prominence_dn'],r['saddle_v'],r['prominence_certificate']=byid[r['plateau_id']]
        rank(records);csvsave(OUT/f'{name}-all-maximum-pixels.csv',records)
        save(OUT/f'{name}-plateaus.json',plateaus)
        for key in METRICS:csvsave(OUT/f'{name}-rank-{key}.csv',sorted(records,key=lambda r:(r['rank_'+key],r['number'])))
        # All raw plateaus in a halo enter the fixed R266 association test. Only
        # ranking changes; masks, paper tests, prominence gates are NOT invented.
        domain=[x0-36,y0-36,x1+36,y1+36];pool=[m for m in maxima if inside(*m['peak'],domain)];selection={}
        for key in METRICS:
            candidates=[]
            for m in pool:
                pts=[(x,y) for y,a,b in m['plateau_runs'] for x in range(a,b+1)]
                x,y=max(pts,key=lambda p:(averages(value,*p)[key],-p[1],-p[0]))
                candidates.append(dict(id=m['region_id'],bright_patch=dict(peak=[x,y]),audit_average=averages(value,x,y)[key]))
            with patch.object(ref,'quality',lambda r,v,h:dict(score=r['audit_average'])):
                kept,suppressed,evidence=ref.associate(copy.deepcopy(candidates),value,hsv)
            selection[key]=dict(selected=[r for r in kept if inside(*r['bright_patch']['peak'],box)],suppressed=[r for r in suppressed if inside(*r['bright_patch']['peak'],box)],associations=evidence,domain=domain)
        save(OUT/f'{name}-selection-experiment.json',selection);allselection[name]=selection
        Image.fromarray(rgb[y0:y1,x0:x1]).save(OUT/f'{name}-original-native.png')
        Image.fromarray(rgb[y0:y1,x0:x1]).resize((972,972),Image.Resampling.NEAREST).save(OUT/f'{name}-original.png')
        layout={}
        for key in METRICS:layout[key]=map_image(rgb,box,records,key,OUT/f'{name}-all-{key}.png',f'{name} | ALL native maximum pixels | {key} mean V ranking')
        summaries[name]=dict(box=box,plateaus=len(plateaus),pixels=len(records),maxima_mask_exact=True,label_checks=layout,selected_counts={k:len(v['selected']) for k,v in selection.items()},top_square7=[{k:r[k] for k in ('number','plateau_id','x','y','square7','prominence_dn','old12_status','old12_reason')} for r in sorted(records,key=lambda r:-r['square7'])[:12]])
        print(name,json.dumps(summaries[name]['top_square7']),flush=True)
    inputs += [Path(__file__),ROOT/'photo2/bead_detection/refine_r266.py',ROOT/'photo2/bead_detection/annular_detect.py',ROOT/'photo2/bead_detection/repaired_detect.py']
    save(OUT/'manifest.json',dict(elapsed_seconds=time.time()-started,python=__import__('sys').version,inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},metrics=METRICS,disk_pixel_counts=[13,29,49],summaries=summaries))
    save(OUT/'r266-selected-records.json',source_records)

if __name__=='__main__':run()
