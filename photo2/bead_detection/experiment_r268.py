"""Photographic R268 inventory, exact climbing traces, comparisons and figures."""
from __future__ import annotations
import csv,gzip,hashlib,json,time
from collections import defaultdict,Counter
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.spatial import cKDTree
from .audit_r267 import ROOT,photo,csvsave,save,FONT,inside
from .climb_r268 import Surface,VARIANTS,background,audit
OUT=ROOT/'photo2/review/r268';PRIOR=ROOT/'photo2/review/r267'

def gzsave(path,data):
    with gzip.GzipFile(filename=str(path),mode='wb',mtime=0) as f:f.write(json.dumps(data,separators=(',',':')).encode())

def inventory():
    manifest=json.loads((PRIOR/'manifest.json').read_text());statuses=json.loads((PRIOR/'r266-statuses.json').read_text());growth=json.loads((PRIOR/'frozen-growth.json').read_text())['grown'];cases={}
    for crop,meta in manifest['summaries'].items():
        box=meta['box'];origins=defaultdict(list);raws=list(csv.DictReader(open(PRIOR/f'{crop}-all-maximum-pixels.csv')));pids={r['plateau_id'] for r in raws}
        for r in raws:origins[int(r['x']),int(r['y'])].append(dict(source='r267-all-native-maximum-pixels',id=r['plateau_id'],role='raw-maximum-pixel',number=int(r['number']),status=r['old12_status']))
        for run,records in statuses.items():
            for pid,r in records.items():
                relevant=pid in pids or (r['location'] and inside(*r['location'],box))
                if not relevant:continue
                origins[tuple(r['peak'])].append(dict(source=run,id=pid,role='seed',status=r['status'],pixels=r['pixel_count']))
                if r['location']:origins[tuple(r['location'])].append(dict(source=run,id=pid,role='supported-coordinate',status=r['status'],pixels=r['pixel_count']))
        for key,r in growth.items():
            if not key.startswith(crop+':'):continue
            origins[tuple(r['seed'])].append(dict(source='r267-frozen-growth',id=r['id'],role='seed',status='diagnostic',pixels=r['pixel_count']))
            origins[tuple(r['location'])].append(dict(source='r267-frozen-growth',id=r['id'],role='supported-coordinate',status='diagnostic',pixels=r['pixel_count']))
        final=json.loads((PRIOR/f'{crop}-hue-size-selection.json').read_text())
        for mode,metrics in final.items():
            for metric,records in metrics.items():
                for r in records['selected']:
                    origins[tuple(r['bright_patch']['peak'])].append(dict(source=f'r267-{mode}-{metric}',id=r['id'],role='selected-seed',status='retained',pixels=r['support_pixels']))
        starts=[]
        for i,(xy,source) in enumerate(sorted(origins.items(),key=lambda item:(item[0][1],item[0][0])),1):starts.append(dict(id=f'S{i:03d}',xy=list(xy),origins=source))
        cases[crop]=dict(box=box,starts=starts,raw_plateau_ids=sorted(pids))
    return cases

def line_panel(rgb,box,traces,starts,title,path,side=7):
    """Legible image with ID-free overview; separate contact sheets label each start."""
    x0,y0,x1,y1=box;scale=12;w=(x1-x0)*scale;h=(y1-y0)*scale
    im=Image.new('RGB',(w,h+75),'#172028');im.paste(Image.fromarray(rgb[y0:y1,x0:x1]).resize((w,h),Image.Resampling.NEAREST),(0,75));d=ImageDraw.Draw(im);font=ImageFont.truetype(FONT,18)
    d.text((12,10),title,fill='white',font=font);d.text((12,37),'White square: start | cyan: climb | orange ring: end (native pixels)',fill='white',font=font)
    def pixel(x,y):return ((x-x0+.5)*scale,75+(y-y0+.5)*scale)
    for s in starts:
        t=traces[s['id']];pts=[pixel(r['x'],r['y']) for r in t['steps']]
        if len(pts)>1:d.line(pts,fill='#00efff',width=2)
        for p in pts[1:-1]:d.ellipse((p[0]-1,p[1]-1,p[0]+1,p[1]+1),fill='#00efff')
    for s in starts:
        t=traces[s['id']];x,y=pixel(*t['start']);xx,yy=pixel(*t['endpoint'])
        if inside(*t['start'],box):d.rectangle((x-3,y-3,x+3,y+3),outline='white',width=1)
        if inside(*t['endpoint'],box):d.ellipse((xx-5,yy-5,xx+5,yy+5),outline='#ffad32',width=2)
    im.save(path)

def contact_sheets(rgb,crop,starts,traces):
    """Every unique start, three guarded12 paths; no overplotted text labels."""
    font=ImageFont.truetype(FONT,14);small=ImageFont.truetype(FONT,12);colors={5:'#00eaff',7:'#ffe564',9:'#ff77cf'};outdir=OUT/f'{crop}-start-cards';outdir.mkdir(exist_ok=True)
    for page,first in enumerate(range(0,len(starts),12),1):
        batch=starts[first:first+12];im=Image.new('RGB',(4*256,3*330),'#172028');d=ImageDraw.Draw(im)
        for j,s in enumerate(batch):
            x,y=s['xy'];paths=[traces[n]['guarded12'][s['id']] for n in (5,7,9)];coords=[(a['x'],a['y']) for t in paths for a in t['steps']];minx=min(a for a,b in coords);maxx=max(a for a,b in coords);miny=min(b for a,b in coords);maxy=max(b for a,b in coords)
            size=max(32,maxx-minx+13,maxy-miny+13);scale=max(1,240//size);cx=(minx+maxx)//2;cy=(miny+maxy)//2;x0=max(0,min(rgb.shape[1]-size,cx-size//2));y0=max(0,min(rgb.shape[0]-size,cy-size//2));px=(j%4)*256;py=(j//4)*330
            d.text((px+6,py+4),f"{s['id']} start ({x},{y})",fill='white',font=font)
            cropim=Image.fromarray(rgb[y0:y0+size,x0:x0+size]).resize((size*scale,size*scale),Image.Resampling.NEAREST);im.paste(cropim,(px+6,py+30))
            for n,t in zip((5,7,9),paths):
                pts=[(px+6+(a['x']-x0+.5)*scale,py+30+(a['y']-y0+.5)*scale) for a in t['steps']]
                if len(pts)>1:d.line(pts,fill=colors[n],width=2)
                xx,yy=pts[-1];d.ellipse((xx-3,yy-3,xx+3,yy+3),outline=colors[n],width=1)
                d.text((px+6,py+275+(n-5)//2*16),f"{n}x{n}: {t['endpoint']}  +{t['steps'][-1]['score_dn']-t['steps'][0]['score_dn']:.2f} DN",fill=colors[n],font=small)
            sx=px+6+(x-x0+.5)*scale;sy=py+30+(y-y0+.5)*scale;d.rectangle((sx-3,sy-3,sx+3,sy+3),outline='white')
        im.save(outdir/f'page-{page:02d}.png')
    return (len(starts)+11)//12

def main():
    started=time.time();OUT.mkdir(exist_ok=True);rgb=photo();v=rgb.max(axis=2);hsv,paper,model=background(rgb);cases=inventory();save(OUT/'starts.json',cases);save(OUT/'parameters.json',dict(windows=[5,7,9],variants={k:__import__('dataclasses').asdict(g) for k,g in VARIANTS.items()},background=model,tie_break='highest admissible exact sum, then smallest y, then x',plateaus='no equal moves; canonical location is an analysis label, never an endpoint relocation'))
    summaries={};audited=0;determinism=0
    # Use the complete old raw inventory for nearest raw plateau and current point comparisons.
    full=json.loads(gzip.open(ROOT/'photo2/review/r266/straight-0-selected12/regions.json.gz').read());rawpoints=[];rawids=[]
    for m in full['maxima']:
        for yy,a,b in m['plateau_runs']:
            for xx in range(a,b+1):rawpoints.append((xx,yy));rawids.append(m['region_id'])
    rawtree=cKDTree(rawpoints);rawset=set(rawpoints);rawpoint_array=np.array(rawpoints);del full
    for crop,case in cases.items():
        starts=case['starts'];box=case['box'];x0,y0,x1,y1=box;traces={};rows=[];groups={};surfaces={};scoreimages={}
        current=[s for s in starts if any(o['source']=='straight-0-selected12' and o['role']=='supported-coordinate' and o['status']=='retained' for o in s['origins'])]
        currenttree=cKDTree([s['xy'] for s in current])
        for side in (5,7,9):
            surface=Surface(v,hsv,paper,side);surfaces[side]=surface;scoreimages[f'sum{side}']=surface.sums[max(0,y0-32):y1+32,max(0,x0-32):x1+32]
            traces[side]={};groups[str(side)]={}
            mean=surface.sums[y0:y1,x0:x1]/side**2;im=Image.fromarray(np.round(mean).astype(np.uint8));im.resize((972,972),Image.Resampling.NEAREST).save(OUT/f'{crop}-mean{side}.png')
            for variant,g in VARIANTS.items():
                records={};endgroups=defaultdict(list);plateaugroups=defaultdict(list)
                for s in starts:
                    t=surface.climb(s['xy'],g);audited+=audit(surface,t,g);records[s['id']]=t;endgroups[tuple(t['endpoint'])].append(s['id'])
                    if t['plateau']:plateaugroups[t['plateau']['id']].append(s['id'])
                    xy=t['endpoint'];dist,idx=rawtree.query(xy);nearcurrent,_=currenttree.query(xy);start=t['steps'][0];end=t['steps'][-1]
                    row=dict(crop=crop,start_id=s['id'],window=side,variant=variant,start_x=start['x'],start_y=start['y'],end_x=end['x'],end_y=end['y'],steps=len(t['steps'])-1,displacement=float(np.linalg.norm(np.array(xy)-s['xy'])),start_raw_v=start['raw_v'],end_raw_v=end['raw_v'],start_mean=start['score_dn'],end_mean=end['score_dn'],gain=end['score_dn']-start['score_dn'],stop=t['stop'],endpoint_is_raw_maximum=tuple(xy) in rawset,nearest_raw_maximum=rawids[idx],nearest_raw_x=int(rawpoint_array[idx,0]),nearest_raw_y=int(rawpoint_array[idx,1]),nearest_raw_distance=float(dist),nearest_current_coordinate_distance=float(nearcurrent),plateau=t['plateau']['id'] if t['plateau'] else '',blocked_moves=len(t['blocked']))
                    rows.append(row)
                for s in current:
                    assert surface.climb(s['xy'],g)==records[s['id']];determinism+=1
                traces[side][variant]=records
                groups[str(side)][variant]=dict(exact_endpoints=[dict(x=x,y=y,starts=ids) for (x,y),ids in sorted(endgroups.items())],equal_score_plateaus=[dict(plateau=p,starts=ids) for p,ids in sorted(plateaugroups.items())])
            for label,chosen in [('all',starts),('current-selected12',current)]:
                line_panel(rgb,box,traces[side]['guarded12'],chosen,f'{crop} | {label} | {side}x{side} guarded12',OUT/f'{crop}-{label}-paths{side}.png',side)
            active=[s for s in starts if any(o['source']==f'r267-fixed-background-size12-square{side}' for o in s['origins'])]
            line_panel(rgb,box,traces[side]['guarded12'],active,f'{crop} | R267 foreground/size candidates | {side}x{side}',OUT/f'{crop}-r267-candidates-paths{side}.png',side)
        # Every endpoint table also reports all three means, independent of optimized window.
        for r in rows:
            for side in (5,7,9):
                r[f'start_mean{side}']=float(surfaces[side].sums[r['start_y'],r['start_x']]/side**2);r[f'end_mean{side}']=float(surfaces[side].sums[r['end_y'],r['end_x']]/side**2)
        gzsave(OUT/f'{crop}-traces.json.gz',traces);save(OUT/f'{crop}-convergence.json',groups);csvsave(OUT/f'{crop}-endpoints.csv',rows)
        visited=[(a['x'],a['y']) for ss in traces.values() for rs in ss.values() for t in rs.values() for a in t['steps']]
        xa=max(0,min(x0-32,min(x for x,y in visited)-4));xb=min(v.shape[1],max(x1+32,max(x for x,y in visited)+5));ya=max(0,min(y0-32,min(y for x,y in visited)-4));yb=min(v.shape[0],max(y1+32,max(y for x,y in visited)+5))
        np.savez_compressed(OUT/f'{crop}-score-images.npz',origin=np.array([xa,ya]),raw_v=v[ya:yb,xa:xb],background_stop_codes=paper[ya:yb,xa:xb],**{f'sum{n}':surfaces[n].sums[ya:yb,xa:xb] for n in (5,7,9)})
        Image.fromarray(rgb[y0:y1,x0:x1]).save(OUT/f'{crop}-original-native.png');Image.fromarray(rgb[y0:y1,x0:x1]).resize((972,972),Image.Resampling.NEAREST).save(OUT/f'{crop}-original.png')
        pages=contact_sheets(rgb,crop,starts,traces);summaries[crop]=dict(unique_starts=len(starts),origin_records=sum(len(s['origins']) for s in starts),current_supported_starts=len(current),start_card_pages=pages,results={})
        for side in (5,7,9):
            for variant in VARIANTS:
                rs=[r for r in rows if r['window']==side and r['variant']==variant];summaries[crop]['results'][f'{side}-{variant}']=dict(moved=sum(r['steps']>0 for r in rs),endpoints=len({(r['end_x'],r['end_y']) for r in rs}),mean_gain=float(np.mean([r['gain'] for r in rs])),stop_counts=dict(Counter(r['stop'] for r in rs)),max_displacement=max(r['displacement'] for r in rs),endpoint_not_raw=sum(not r['endpoint_is_raw_maximum'] for r in rs))
        print(crop,summaries[crop]['unique_starts'],summaries[crop]['results']['7-guarded12'],flush=True)
        del surfaces,traces
    save(OUT/'photo-summary.json',dict(cases=summaries,audited_moves=audited,deterministic_replays=determinism,elapsed_seconds=time.time()-started))
    # All previous R267 files and production modules are protected by hashes.
    inputs=[ROOT/'beads-photo-2.jpg']+sorted(p for p in PRIOR.rglob('*') if p.is_file())+[ROOT/'photo2/bead_detection'/n for n in ['annular_detect.py','repaired_detect.py','refine_r266.py']]
    save(OUT/'input-hashes.json',{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs})
if __name__=='__main__':main()
