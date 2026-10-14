"""Exact reflection-only replay, no new contour tuning or physical ownership."""
import shutil
import numpy as np
from photo2.r282.phase1 import image_features
from photo2.r284b.methods import reflection
from photo2.r284b.run import mask_of
from .common import *

def main():
    _,rgb,_=photo();f=image_features(rgb);old=read(OLD/'reflections.json.gz');baseline={r['record_id']:r for r in read(ROOT/'photo2/r283/results/phase1.json.gz')['records']};checks=[]
    for o in old['observations']:
        x,y=o['seed'];origin=np.array(o['origin']);sl=np.s_[y-24:y+25,x-24:x+25];lum=f['lum'][sl];hs=f['hsv'][sl];initial=mask_of(o.get('initial_support') or baseline[o['id']]['measured_support'],origin);domain=((hs[:,:,1]<.65)|(hs[:,:,1]*hs[:,:,2]<.12))&~f['paper'][sl]
        for m in ('R1','R2','R4'):
            mask,c,meta=reflection(lum,domain,initial,variant=m);v=o['variants'][m];np.testing.assert_array_equal(mask,mask_of(v['measured_support'],origin));np.testing.assert_array_equal(c+origin,np.array(v['subpixel_contour']).reshape(-1,2));np.testing.assert_array_equal(np.array(meta['peak'])+origin,v['peak_location']);checks.append(dict(id=o['id'],method=m,area=int(mask.sum()),exact_mask_contour_peak=True,physical_owner=None))
    names=['upper-good-black','lower-secondary-black']
    # Use saved selection names rather than assumptions about review filenames.
    selected=old['selected'][:2];observations={o['id']:o for o in old['observations']};overlap={}
    for m in ('R1','R2','R4'):
        a,b=[set(map(tuple,pixels(observations[q['id']]['variants'][m]['measured_support']))) for q in selected];overlap[m]=len(a&b)
    for q in selected:
        for suffix in ('.png','-native.png'):shutil.copyfile(ROOT/'photo2/review/r285'/(q['name']+suffix),REVIEW/(q['name']+suffix))
    save(OUT/'reflection-stability.json',dict(checks=checks,features=len(old['observations']),comparisons=len(checks),selected=selected,upper_lower_overlap=overlap,retained_default='R2',alternatives=['R1','R4'],previous_summary=old['summary'],interpretation='Exact R285 native masks, subpixel contours and peaks. Separate upper/secondary measurements; unknown physical ownership. No black-body inference or new smoothing tuning.'))
    print(len(checks),'exact reflection replays',overlap)
if __name__=='__main__':main()
