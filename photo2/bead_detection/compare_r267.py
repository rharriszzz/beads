"""Frozen R266 pair/growth controls following the pre-growth R267 audit."""
import copy,csv,gzip,json,hashlib
from collections import Counter
from unittest.mock import patch
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from matplotlib.colors import rgb_to_hsv
from .audit_r267 import OUT,ROOT,METRICS,averages,inside,save,csvsave,map_image,photo,FONT
from . import refine_r266 as ref,annular_detect as d
from .experiment_r266 import irregularity

def rows_for(name):
    rows=list(csv.DictReader(open(OUT/f'{name}-all-maximum-pixels.csv')))
    for r in rows:
        for k in ['number','x','y','peak_v','prominence_dn']+[f'rank_{k}' for k in METRICS]:r[k]=int(r[k])
        for k in METRICS:r[k]=float(r[k])
    return rows

def run():
    rgb=photo();v=rgb.max(axis=2);hsv=rgb_to_hsv(rgb/255.)
    manifest=json.loads((OUT/'manifest.json').read_text());records=json.loads((OUT/'r266-selected-records.json').read_text());statuses=json.loads((OUT/'r266-statuses.json').read_text());allpairs=[];comparisons=[];growpoints={};sourcechecks=[]
    params=d.Parameters(**json.loads((OUT/'r266-parameters.json').read_text())['parameters'])
    for name,summary in manifest['summaries'].items():
        box=summary['box'];rows=rows_for(name);old=[r for r in records.values() if r['status']=='retained' and inside(*r['bright_patch']['peak'],box)]
        representatives=[]
        for key in METRICS:
            chosen={}
            for row in rows:
                pid=row['plateau_id']
                if pid not in chosen or row[key]>chosen[pid][key]:chosen[pid]=row
            representatives.extend((key,r) for r in chosen.values())
        for r in old:
            seed=r['bright_patch']['peak'];oldavg=averages(v,*seed)
            growpoints[(name,*seed)]=r['id']
            # Reconstruct score terms exactly for every selected old maximum.
            q=r['peak_quality'];terms=dict(peak=.04*q['brightness_dn'],prominence=.08*min(q['prominence_lower_bound_dn'],60),median=.20*q['neighborhood_median_dn'],p25=.25*q['neighborhood_p25_dn'],area=.04*min(r['pixel_count'],150),compactness=60*q['compactness'])
            assert abs(sum(terms.values())-q['score'])<1e-9
            pool={k:[] for k in METRICS}
            for key,a in representatives:
                if np.linalg.norm(np.array(seed)-[a['x'],a['y']])>18:continue
                cand=dict(id=a['plateau_id'],bright_patch=dict(peak=[a['x'],a['y']]),audit_average=a[key])
                if cand['id']==r['id']:pool[key].append(a);continue
                target=dict(id=r['id'],bright_patch=dict(peak=seed),audit_average=oldavg[key])
                with patch.object(ref,'quality',lambda r,v,h:dict(score=r['audit_average'])):
                    kept,suppressed,evidence=ref.associate([target,cand],v,hsv)
                ev=evidence[0];allpairs.append(dict(crop=name,metric=key,old_id=r['id'],pixel_number=a['number'],**ev))
                if ev['decision']=='suppress':pool[key].append(a)
            for key in METRICS:
                best=max(pool[key],key=lambda a:a[key]);growpoints[(name,best['x'],best['y'])]=best['plateau_id']
                comparisons.append(dict(crop=name,old_id=r['id'],old_x=seed[0],old_y=seed[1],old_location=r['location'],old_mean=oldavg[key],old_score=q['score'],old_score_terms=terms,metric=key,best_id=best['plateau_id'],best_number=best['number'],best_x=best['x'],best_y=best['y'],best_mean=best[key],gain=best[key]-oldavg[key],distance=float(np.linalg.norm(np.array(seed)-[best['x'],best['y']])),best_prominence=best['prominence_dn'],best_old_status=best['old12_status'],best_old_reason=best['old12_reason'],compatible_plateaus=len(pool[key])))
        for key in METRICS:
            selected=json.loads((OUT/f'{name}-selection-experiment.json').read_text())[key]['selected'];pts={(r['id'],*r['bright_patch']['peak']) for r in selected};display=[r for r in rows if (r['plateau_id'],r['x'],r['y']) in pts]
            # Rank colors are relative to the COMPLETE audit, not only winners.
            map_image(rgb,box,display,key,OUT/f'{name}-candidates-{key}.png',f'{name} | average-only + unchanged bridge | {key} | diagnostic candidates',rank_population=len(rows))
        # Three clean panels: raw, old seeds, independent mean-only candidates.
        key='square7';selected=json.loads((OUT/f'{name}-selection-experiment.json').read_text())[key]['selected'];pts={(r['id'],*r['bright_patch']['peak']) for r in selected};display=[r for r in rows if (r['plateau_id'],r['x'],r['y']) in pts]
        oldrows=[]
        for r in old:
            found=[a for a in rows if [a['x'],a['y']]==r['bright_patch']['peak']]
            oldrows.extend(found)
        map_image(rgb,box,oldrows,key,OUT/f'{name}-old-seeds.png',f'{name} | R266 selected12 SEEDS (numbers match all-maxima tables)',rank_population=len(rows))
        scale=8;x0,y0,x1,y1=box;w=(x1-x0)*scale;h=(y1-y0)*scale;font=ImageFont.truetype(FONT,16)
        im=Image.new('RGB',(w*3,h+82),'#172028');draw=ImageDraw.Draw(im)
        for panel,(title,points) in enumerate([('Original',[]),('R266 selected12 seeds',oldrows),('7x7 diagnostic: all candidates',display)]):
            im.paste(Image.fromarray(rgb[y0:y1,x0:x1]).resize((w,h),Image.Resampling.NEAREST),(panel*w,82));draw.text((panel*w+12,8),title,fill='white',font=font)
            for a in points:
                xx=panel*w+(a['x']-x0+.5)*scale;yy=82+(a['y']-y0+.5)*scale
                draw.ellipse((xx-3,yy-3,xx+3,yy+3),outline='#00ffff',width=2)
        draw.text((12,36),'Dots are native maxima, not centroids or physical centers. Labels and all six methods are in separate full-size maps.',fill='white',font=font)
        draw.text((12,59),'Average-only test deliberately bypasses prominence/background/support gates; it is not a replacement detector.',fill='white',font=font)
        im.save(OUT/f'{name}-comparison.png')
    save(OUT/'coordinate-comparisons.json',comparisons);csvsave(OUT/'coordinate-comparisons.csv',comparisons);save(OUT/'pair-controls.json',allpairs)
    # Same RGB, native valleys, learned paper map and all growth parameters.
    h,w=v.shape;border=np.zeros((h,w),bool);margin=max(1,round(min(h,w)*params.border_fraction));border[:margin]=border[-margin:]=True;border[:,:margin]=border[:,-margin:]=True
    _,paper,_=d.background_maps(hsv,border);valleys=d.valley_pixels(v,params.valley_depth_dn);grown={}
    for (name,x,y),pid in growpoints.items():
        mask,t=d.grow(v,hsv,(x,y),params,valleys=valleys,paper=paper);ox,oy=t['mask_offset'];r=dict(id=pid,seed=[x,y],**d.measure(mask,ox,oy),pixel_runs=d.runs(mask,ox,oy));r.update(irregularity(r));r['thin_fraction']=r['thin_pixels']/r['pixel_count'];r['stops']=dict(Counter(row[7] for row in t['stops']));r['size_limited']=t['size_limited'];grown[f'{name}:{x},{y}']=r
        if pid in records and records[pid]['bright_patch']['peak']==[x,y]:
            equal=r['pixel_runs']==records[pid]['pixel_runs'];assert equal,(pid,'frozen reproduction mismatch');sourcechecks.append(dict(id=pid,mask_exact=equal))
    save(OUT/'frozen-growth.json',dict(parameters=__import__('dataclasses').asdict(params),grown=grown,old_mask_checks=sourcechecks))
    growthrows=[]
    for c in comparisons:
        a=grown[f"{c['crop']}:{c['old_x']},{c['old_y']}"];b=grown[f"{c['crop']}:{c['best_x']},{c['best_y']}"]
        growthrows.append({k:c[k] for k in ('crop','metric','old_id','best_id','best_number','gain')}|dict(old_area=a['pixel_count'],best_area=b['pixel_count'],old_perimeter_area=a['perimeter_area'],best_perimeter_area=b['perimeter_area'],old_thin=a['thin_pixels'],best_thin=b['thin_pixels'],old_stops=a['stops'],best_stops=b['stops']))
    csvsave(OUT/'frozen-growth-comparisons.csv',growthrows)
    # Outline control ONLY illustrates frozen growth, never tunes its parameters.
    for name,summary in manifest['summaries'].items():
        box=summary['box'];x0,y0,x1,y1=box;scale=10;w=(x1-x0)*scale;h=(y1-y0)*scale;font=ImageFont.truetype(FONT,16)
        im=Image.new('RGB',(3*w,h+60),'#172028');draw=ImageDraw.Draw(im)
        cs=[c for c in comparisons if c['crop']==name and c['metric']=='square7']
        for j,kind in enumerate(('Original','R266 seeds: frozen straight growth','Best direct-compatible 7x7: same growth')):
            im.paste(Image.fromarray(rgb[y0:y1,x0:x1]).resize((w,h),Image.Resampling.NEAREST),(j*w,60));draw.text((j*w+10,8),kind,fill='white',font=font)
            if not j:continue
            for c in cs:
                sx,sy=(c['old_x'],c['old_y']) if j==1 else (c['best_x'],c['best_y']);r=grown[f'{name}:{sx},{sy}']
                pts={(x,y) for y,a,b in r['pixel_runs'] for x in range(a,b+1)}
                for x,y in pts:
                    if not inside(x,y,box):continue
                    for dx,dy,edge in [(-1,0,(0,0,0,1)),(1,0,(1,0,1,1)),(0,-1,(0,0,1,0)),(0,1,(0,1,1,1))]:
                        if (x+dx,y+dy) not in pts:
                            a,b,cx,cy=edge;draw.line((j*w+(x-x0+a)*scale,60+(y-y0+b)*scale,j*w+(x-x0+cx)*scale,60+(y-y0+cy)*scale),fill='#00ffff',width=1)
                px=j*w+(sx-x0+.5)*scale;py=60+(sy-y0+.5)*scale;draw.ellipse((px-3,py-3,px+3,py+3),fill='white')
        draw.text((12,35),'Unsmoothed native mask edges. Seed changes only; these supports are not claimed bead outlines.',fill='white',font=font);im.save(OUT/f'{name}-frozen-growth.png')
    save(OUT/'control-summary.json',dict(old_mask_exact_checks=len(sourcechecks),frozen_seeds=len(grown),comparison_rows=len(comparisons),pair_rows=len(allpairs)))
    print(json.dumps([r for r in growthrows if r['metric']=='square7'],indent=2))

if __name__=='__main__':run()
