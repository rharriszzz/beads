"""User steering: fixed hue-only background + discard small ambiguous supports.

No outline tuning. Reuse the R266 learned paper hue and existing 30-degree
uncertainty half-band, and the prior 12-pixel recovery minimum for small supports.
All exclusions remain evidence. These are local review controls, not a new default.
"""
import copy,json
from unittest.mock import patch
import numpy as np
from matplotlib.colors import rgb_to_hsv
from .audit_r267 import OUT,ROOT,METRICS,photo,averages,inside,save,csvsave,map_image
from .compare_r267 import rows_for
from . import refine_r266 as ref,annular_detect as d

MIN_PIXELS=12

def main():
    rgb=photo();v=rgb.max(axis=2);hsv=rgb_to_hsv(rgb/255.);h,w=v.shape
    params=d.Parameters(**json.loads((OUT/'r266-parameters.json').read_text())['parameters'])
    border=np.zeros((h,w),bool);margin=max(1,round(min(h,w)*params.border_fraction));border[:margin]=border[-margin:]=True;border[:,:margin]=border[:,-margin:]=True
    model,paper,uncertain=d.background_maps(hsv,border);valleys=d.valley_pixels(v,params.valley_depth_dn)
    center=model['center'][0]*360;half=model['uncertainty_hue_deg']
    snapshots=json.loads((OUT/'r266-statuses.json').read_text())['straight-0-selected12'];oldrecords=json.loads((OUT/'r266-selected-records.json').read_text());manifest=json.loads((OUT/'manifest.json').read_text());sizes={};summaries={};all_exclusions=[];replayed=0
    def size(x,y,pid):
        nonlocal replayed
        key=f'{x},{y}'
        if key not in sizes:
            if pid in oldrecords and oldrecords[pid]['bright_patch']['peak']==[x,y]:
                n=oldrecords[pid]['pixel_count'];limited=oldrecords[pid].get('size_limited',False);source='preserved-exact-R266-support'
            else:
                mask,t=d.grow(v,hsv,(x,y),params,valleys=valleys,paper=paper);n=int(mask.sum());limited=t['size_limited'];source='frozen-R266-growth';replayed+=1
            sizes[key]=dict(plateau_id=pid,x=x,y=y,pixels=n,size_limited=limited,source=source)
        return sizes[key]
    for name,summary in manifest['summaries'].items():
        rows=rows_for(name);box=summary['box'];domain=[box[0]-36,box[1]-36,box[2]+36,box[3]+36]
        # Start from the prior fixed-background control's FULL eligible candidate
        # inventory before association, including all eligible halo candidates.
        fixed=json.loads((OUT/f'{name}-fixed-background-selection.json').read_text())
        results={}
        for mode in ('fixed-background-size12','hue-only-size12'):
            results[mode]={}
            for metric in METRICS:
                pool=[]
                fixed_candidates={r['id']:r for r in fixed[metric]['eligible_candidates']}
                for pid,s in snapshots.items():
                    if not inside(*s['peak'],domain):continue
                    same=[r for r in rows if r['plateau_id']==pid]
                    chosen=max(same,key=lambda r:r[metric]) if same else None
                    x,y=(chosen['x'],chosen['y']) if chosen else s['peak']
                    if mode=='fixed-background-size12' and pid in fixed_candidates:
                        x,y=fixed_candidates[pid]['bright_patch']['peak']
                        chosen=next((r for r in same if (r['x'],r['y'])==(x,y)),None)
                    hue=float(hsv[y,x,0]*360);distance=abs((hue-center+180)%360-180)
                    hue_bg=distance<=half
                    if mode=='hue-only-size12':background=hue_bg;reason='existing-learned-paper-hue-band'
                    else:
                        background=pid not in fixed_candidates
                        reason='preserved-background-control'
                    outcome=dict(crop=name,mode=mode,metric=metric,id=pid,number=chosen['number'] if chosen else None,x=x,y=y,h_deg=hue,paper_hue_distance=distance,mean=averages(v,x,y)[metric],pixels=None,decision='candidate',reason='')
                    if background:outcome.update(decision='excluded',reason=reason)
                    else:
                        info=size(x,y,pid);outcome['pixels']=info['pixels']
                        if info['pixels']<MIN_PIXELS:outcome.update(decision='excluded',reason='small-ambiguous-support-below-12-native-pixels')
                        elif info['size_limited']:outcome.update(decision='excluded',reason='preserved-870-native-pixel-cap')
                    if inside(x,y,box):all_exclusions.append(outcome)
                    if outcome['decision']=='candidate':pool.append(dict(id=pid,bright_patch=dict(peak=[x,y]),audit_average=outcome['mean'],support_pixels=outcome['pixels']))
                with patch.object(ref,'quality',lambda r,v,h:dict(score=r['audit_average'])):
                    kept,suppressed,pairs=ref.associate(copy.deepcopy(pool),v,hsv)
                kept=[r for r in kept if inside(*r['bright_patch']['peak'],box)]
                results[mode][metric]=dict(selected=kept,suppressed=suppressed,associations=pairs,domain=domain)
                pts={(r['id'],*r['bright_patch']['peak']) for r in kept};display=[r for r in rows if (r['plateau_id'],r['x'],r['y']) in pts]
                map_image(rgb,box,display,metric,OUT/f'{name}-{mode}-{metric}.png',f'{name} | {mode} | {metric} candidates',rank_population=len(rows))
                assert all(r['support_pixels']>=MIN_PIXELS for r in kept)
        save(OUT/f'{name}-hue-size-selection.json',results)
        summaries[name]={mode:{metric:len(r['selected']) for metric,r in rs.items()} for mode,rs in results.items()}
        print(name,summaries[name],flush=True)
    csvsave(OUT/'hue-size-candidate-decisions.csv',all_exclusions);save(OUT/'hue-size-growth-sizes.json',sizes)
    save(OUT/'hue-size-summary.json',dict(summaries=summaries,paper_hue_center_deg=center,paper_hue_half_band_deg=half,minimum_pixels=MIN_PIXELS,new_frozen_growth_replays=replayed,exclusions_retained=True,detector_changed=False,scope='Hue-only uses the existing learned paper-hue uncertainty band without S/V/texture. Compare with fixed background plus the same size discard. No foreground identity or outline optimization.'))
if __name__=='__main__':main()
