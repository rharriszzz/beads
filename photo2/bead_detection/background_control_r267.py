"""R267 steering: hold established background tests fixed during mean ranking.

Reuses R266 learned margin model, native texture, seed check and smooth-context
uncertainty. No new background estimator/FFT, threshold search or manual mask.
All unfiltered maxima remain in the primary numerical inventory.
"""
import copy,json
from unittest.mock import patch
import numpy as np
from scipy import ndimage as ndi
from matplotlib.colors import rgb_to_hsv
from .audit_r267 import OUT,ROOT,METRICS,photo,averages,inside,save,csvsave,map_image
from .compare_r267 import rows_for
from . import refine_r266 as ref,annular_detect as d

def main():
    rgb=photo();v=rgb.max(axis=2);hsv=rgb_to_hsv(rgb/255.);h,w=v.shape
    params=json.loads((OUT/'r266-parameters.json').read_text())['parameters'];border=np.zeros((h,w),bool);margin=max(1,round(min(h,w)*params['border_fraction']));border[:margin]=border[-margin:]=True;border[:,:margin]=border[:,-margin:]=True
    model,paper,uncertain=d.background_maps(hsv,border);texture=ndi.maximum_filter(v,5).astype(float)-ndi.minimum_filter(v,5)
    smooth=uncertain & (texture<=max(18,model.get('texture_limit_dn',18)*ref.RULE['background_smooth_factor']))
    statuses=json.loads((OUT/'r266-statuses.json').read_text());manifest=json.loads((OUT/'manifest.json').read_text());summaries={}
    def evidence(x,y,pid):
        nearby=float(smooth[max(0,y-12):y+13,max(0,x-12):x+13].mean());reasons=[]
        if d.obvious_background(hsv,x,y,model):reasons.append('R266-obvious-background-before-growth')
        if np.all(paper[max(0,y-1):y+2,max(0,x-1):x+2]) and abs(hsv[y,x,2]-model['center'][2])<=model['tolerance'][2]:reasons.append('R266-local-paper-seed-test')
        if nearby>ref.RULE['background_nearby_fraction'] and uncertain[y,x]:reasons.append('R266-smooth-context-and-learned-HSV-paper-uncertainty')
        for name in ['straight-0-selected12','straight-0-selected6','straight-0-selected3']:
            s=statuses[name].get(pid,{})
            if s.get('status') in ('rejected','deferred') and any(word in s.get('reason','') for word in ('paper','background')):reasons.append('preserved-'+name+':'+s['reason'])
        return dict(eligible=not reasons,reasons=sorted(set(reasons)),nearby_smooth_uncertain_fraction=nearby,uncertain_seed=bool(uncertain[y,x]))
    for name,summary in manifest['summaries'].items():
        box=summary['box'];rows=rows_for(name);domain=[box[0]-36,box[1]-36,box[2]+36,box[3]+36]
        # The old statuses include all raw plateaus in a 40px halo.
        pool=[(pid,s) for pid,s in statuses['straight-0-selected12'].items() if inside(*s['peak'],domain)]
        assessments=[]
        for r in rows:
            e=evidence(r['x'],r['y'],r['plateau_id']);assessments.append(dict(number=r['number'],plateau_id=r['plateau_id'],x=r['x'],y=r['y'],**e))
        csvsave(OUT/f'{name}-fixed-background.csv',assessments)
        selections={}
        for key in METRICS:
            candidates=[]
            for pid,s in pool:
                # Prefer per-plateau best point inside the crop; outside use old
                # representative. This is a scoped diagnostic with a fixed halo.
                same=[r for r in rows if r['plateau_id']==pid and evidence(r['x'],r['y'],pid)['eligible']]
                if same:
                    best=max(same,key=lambda r:r[key]);x,y=best['x'],best['y']
                else:x,y=s['peak']
                if not evidence(x,y,pid)['eligible']:continue
                candidates.append(dict(id=pid,bright_patch=dict(peak=[x,y]),audit_average=averages(v,x,y)[key]))
            with patch.object(ref,'quality',lambda r,v,h:dict(score=r['audit_average'])):
                kept,suppressed,pairs=ref.associate(copy.deepcopy(candidates),v,hsv)
            kept=[r for r in kept if inside(*r['bright_patch']['peak'],box)];selections[key]=dict(selected=kept,suppressed=suppressed,associations=pairs,domain=domain)
            pts={(r['id'],*r['bright_patch']['peak']) for r in kept};display=[r for r in rows if (r['plateau_id'],r['x'],r['y']) in pts]
            map_image(rgb,box,display,key,OUT/f'{name}-fixed-background-{key}.png',f'{name} | fixed R266 background + {key} candidates',rank_population=len(rows))
        save(OUT/f'{name}-fixed-background-selection.json',selections)
        summaries[name]=dict(eligible_maximum_pixels=sum(r['eligible'] for r in assessments),all_maximum_pixels=len(rows),selected_counts={k:len(s['selected']) for k,s in selections.items()})
    save(OUT/'fixed-background-summary.json',dict(summaries=summaries,background_model=model,scope='Existing R266 seed/context tests plus preserved paper deferrals; not new background work. Region-fraction test is reused only when already recorded, not invented before growth. Passing means background-eligible, not verified bead.'))
    print(json.dumps(summaries))
if __name__=='__main__':main()
