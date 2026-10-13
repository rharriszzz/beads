"""Compact review tables and photographic convergence/neighbor witnesses."""
import csv,gzip,json
from collections import defaultdict
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from .experiment_r268 import OUT
from .audit_r267 import photo,FONT,save,csvsave


def main():
    cases=json.loads((OUT/'starts.json').read_text());rgb=photo();current_rows=[];convergences=[];curated=[]
    for crop,case in cases.items():
        ts=json.load(gzip.open(OUT/f'{crop}-traces.json.gz'));starts=case['starts'];byid={s['id']:s for s in starts};endpoints=list(csv.DictReader(open(OUT/f'{crop}-endpoints.csv')));lookup={(r['start_id'],r['window'],r['variant']):r for r in endpoints}
        for s in starts:
            for o in s['origins']:
                if o['source']=='straight-0-selected12' and o['status']=='retained':
                    for side in (5,7,9):
                        r=lookup[s['id'],str(side),'guarded12'];current_rows.append(dict(crop=crop,maximum_id=o['id'],role=o['role'],start_id=s['id'],start=s['xy'],window=side,endpoint=[int(r['end_x']),int(r['end_y'])],raw_before=int(r['start_raw_v']),raw_after=int(r['end_raw_v']),mean_before=float(r['start_mean']),mean_after=float(r['end_mean']),gain=float(r['gain']),stop=r['stop'],moves=int(r['steps'])))
        for side in (5,7,9):
            groups=defaultdict(list)
            for s in starts:groups[tuple(ts[str(side)]['guarded12'][s['id']]['endpoint'])].append(s)
            for xy,ss in groups.items():
                rawids=sorted({o['id'] for s in ss for o in s['origins'] if o['role']=='raw-maximum-pixel'});activeids=sorted({o['id'] for s in ss for o in s['origins'] if o['source']==f'r267-fixed-background-size12-square{side}'})
                selectedids=sorted({o['id'] for s in ss for o in s['origins'] if o['source']=='straight-0-selected12' and o['status']=='retained'})
                pts=np.array([s['xy'] for s in ss]);span=float(np.linalg.norm(pts[:,None]-pts[None,:],axis=2).max())
                convergences.append(dict(crop=crop,window=side,endpoint=list(xy),start_count=len(ss),start_ids=[s['id'] for s in ss],raw_plateau_ids=rawids,r267_active_ids=activeids,r266_selected_ids=selectedids,maximum_start_separation=span,interpretation='coordinate convergence only; no identity merge'))
        # Named old IDs select review witnesses only; not inputs to climbing.
        pairs=([('upper-yellow','P090697','P090766'),('middle-yellow','P091868','P091694'),('lower-yellow','P093030','P092706')] if crop=='R00956' else [('central-yellow','P128915','P128672'),('shadowed-neighbor','P129034','P128915')])
        for label,left,right in pairs:
            ss=[]
            for pid in (left,right):ss.append(next(s for s in starts if any(o['id']==pid and o['source']=='straight-0-selected12' and o['role']=='seed' for o in s['origins'])))
            x0,y0,x1,y1=case['box'];scale=6;w=(x1-x0)*scale;h=(y1-y0)*scale;im=Image.new('RGB',(w*3,h*3+140),'#172028');d=ImageDraw.Draw(im);font=ImageFont.truetype(FONT,15);small=ImageFont.truetype(FONT,13);colors=['#00f4ff','#95ff72']
            d.text((10,8),f'{crop} {label}: cyan {left} / {ss[0]["id"]}, green {right} / {ss[1]["id"]}',fill='white',font=font)
            for row,side in enumerate((5,7,9)):
                for col,variant in enumerate(('original','unguarded','guarded12')):
                    px=col*w;py=44+row*(h+32);im.paste(Image.fromarray(rgb[y0:y1,x0:x1]).resize((w,h),Image.Resampling.NEAREST),(px,py+24));d.text((px+8,py+3),f'{side}x{side} | {variant}',fill='white',font=small)
                    for s,color in zip(ss,colors):
                        t=ts[str(side)]['guarded12' if variant=='original' else variant][s['id']];steps=t['steps'][:1] if variant=='original' else t['steps'];pts=[(px+(a['x']-x0+.5)*scale,py+24+(a['y']-y0+.5)*scale) for a in steps]
                        if len(pts)>1:d.line(pts,fill=color,width=2)
                        sx,sy=pts[0];d.rectangle((sx-3,sy-3,sx+3,sy+3),outline='white');ex,ey=pts[-1];d.ellipse((ex-4,ey-4,ex+4,ey+4),outline=color,width=2)
                        if variant!='original':curated.append(dict(crop=crop,case=label,maximum_id=left if s==ss[0] else right,start_id=s['id'],window=side,variant=variant,start=s['xy'],endpoint=t['endpoint'],start_raw=t['steps'][0]['raw_v'],end_raw=t['steps'][-1]['raw_v'],start_mean=t['steps'][0]['score_dn'],end_mean=t['steps'][-1]['score_dn'],stop=t['stop'],final_blocked=[b for b in t['blocked'] if b['step']==len(t['steps'])-1]))
            im.save(OUT/f'{crop}-{label}-witness.png')
    csvsave(OUT/'current-selected12-comparison.csv',current_rows);save(OUT/'convergence-review.json',convergences);csvsave(OUT/'convergence-review.csv',convergences);save(OUT/'curated-witnesses.json',curated)
    lines=['# R268 current selected12 seeds and supported coordinates','', 'IDs name R266 maximum plateaus, not verified beads. Every row climbs on an exact mean surface with the primary 12-DN raw-valley guard. Start and end coordinates are native pixels; raw brightness and mean brightness are different quantities. Stops at blocked higher neighbors are not unconstrained score maxima.','', '| Crop | Maximum / role | Start ID | Start | Window | Endpoint | Raw V before→after | Mean before→after | Stop |','|---|---|---|---|---:|---|---|---|---|']
    for r in current_rows:lines.append(f"| {r['crop']} | {r['maximum_id']} / {r['role']} | {r['start_id']} | {r['start']} | {r['window']} | {r['endpoint']} | {r['raw_before']}→{r['raw_after']} | {r['mean_before']:.2f}→{r['mean_after']:.2f} | {r['stop']} |")
    (OUT/'CURRENT_POINTS.md').write_text('\n'.join(lines)+'\n')
    summary={}
    for crop in cases:
        summary[crop]={}
        for side in (5,7,9):
            rs=[r for r in convergences if r['crop']==crop and r['window']==side];summary[crop][str(side)]=dict(multi_raw_plateau_endpoints=sum(len(r['raw_plateau_ids'])>1 for r in rs),multi_r267_active_endpoints=sum(len(r['r267_active_ids'])>1 for r in rs),multi_r266_selected_endpoints=sum(len(r['r266_selected_ids'])>1 for r in rs),active_groups=[r for r in rs if len(r['r267_active_ids'])>1])
    save(OUT/'convergence-summary.json',summary)
    index=['# All R268 starting points','','Every unique coordinate has a photographic card. Cyan5×5, yellow7×7, magenta9×9; white square=start. All paths use guarded12. S IDs map to all original sources in starts.json. Stopped/ambiguous starts remain audit evidence, not accepted beads.','','| Crop | Start IDs | Contact sheet |','|---|---|---|']
    for crop,c in cases.items():
        for k in range(0,len(c['starts']),12):
            batch=c['starts'][k:k+12];page=k//12+1
            index.append(f"| {crop} | {batch[0]['id']}–{batch[-1]['id']} | [page {page}]({crop}-start-cards/page-{page:02d}.png) |")
    (OUT/'START_CARDS.md').write_text('\n'.join(index)+'\n')
if __name__=='__main__':main()
