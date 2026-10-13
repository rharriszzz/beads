"""Independent full-photo measurements, source preservation and known controls."""
import hashlib,json,gzip,time
from collections import Counter
import numpy as np
from PIL import Image,ImageOps
from scipy import ndimage as ndi
from matplotlib.colors import rgb_to_hsv
from .brightness_r270 import color_managed_photo,linearize,encode
from .inventory_r272 import CROSS
from .experiment_r273 import ROOT,OUT,save
from .interiors_r273 import pixels,refine,Parameters
from .climb_r268 import background

def main():
    data=json.loads((OUT/'inventory.json').read_text());beads=data['beads'];srgb,profile=color_managed_photo();native=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));lum=linearize(srgb/255.)@np.array([.2126,.7152,.0722]);hsv=rgb_to_hsv(srgb/255.);occupied=np.zeros(lum.shape,np.uint8);checks=Counter()
    old=json.loads((ROOT/'photo2/review/r272-coverage/inventory.json').read_text())['beads'];lookup={r['id']:r for r in old};_,paper,_=background(native)
    for i,b in enumerate(beads,1):
        assert b['inventory_number']==i;assert b['color'] in ('black','red','yellow');assert b['accepted'] and not b['reasons'];assert b['id']==f"{'K' if b['color']=='black' else 'C'}-{b['anchor'][0]:04d}-{b['anchor'][1]:04d}"
        points={}
        for key in ('region','bright_patch'):
            r=b[key];pts=np.array([(x,y) for y,a,z in r['runs'] for x in range(a,z+1)]);assert len(pts)==r['pixel_count'];assert len(set(map(tuple,pts)))==len(pts);np.testing.assert_allclose(pts.mean(axis=0),r['centroid'],atol=1e-12);box=r['bbox'];m=np.zeros((box[3]-box[1],box[2]-box[0]),bool);m[pts[:,1]-box[1],pts[:,0]-box[0]]=True;assert ndi.label(m,CROSS)[1]==1;assert not(ndi.binary_fill_holes(m)&~m).any() if key=='region' else True;points[key]=set(map(tuple,pts));checks[key+'_pixels']+=len(pts)
        assert points['bright_patch']<=points['region'];assert b['region']['pixel_count']<=870
        coords=np.array(sorted(points['region'],key=lambda p:(p[1],p[0])));scores=lum[coords[:,1],coords[:,0]];xy=coords[np.argmax(scores)];p=b['brightest'];assert [p['x'],p['y']]==xy.tolist();assert abs(p['luminance']-scores.max())<1e-12;assert p['rgb_srgb']==srgb[xy[1],xy[0]].tolist();assert p['rgb_native']==native[xy[1],xy[0]].tolist();np.testing.assert_allclose([p['hsv_srgb'][k] for k in ('h','s','v')],hsv[xy[1],xy[0]]*[360,1,1]);assert np.all(occupied[coords[:,1],coords[:,0]]==0);occupied[coords[:,1],coords[:,0]]=1
        for key in ('raw','smooth'):assert b['outline'][key][0]==b['outline'][key][-1]
        if b['color']=='black':
            assert all(b[k]==lookup[b['id']][k] for k in ('region','bright_patch','brightest','dark_perimeter'))
            shell=b['dark_perimeter'];pts=np.array([(x,y) for y,a,z in shell['runs'] for x in range(a,z+1)]);assert shell['signal']=='icc-gray' and shell['sigma']==0;values=encode(lum[pts[:,1],pts[:,0]]);assert shell['closed'];assert np.max(values)<=shell['threshold']+1e-12;np.testing.assert_allclose(values.max(),shell['maximum_value']);checks['complete_native_dark_perimeters']+=1
        else:
            assert b['color']==lookup[b['id']]['color'];assert points['region']<=pixels(b,'supported_region');assert b['supported_region']['pixel_count']<=870;assert np.all(paper[coords[:,1],coords[:,0]]!=1);assert b['background_continuation']['confident_paper_pixels']==0;checks['retained_uncertain_background_pixels']+=int(np.sum(paper[coords[:,1],coords[:,0]]==2));assert b['shape']['solidity']>=b['support_parameters']['minimum_solidity'];checks['colored_removal_only']+=1
            assert b['r272_measurements']['region']==lookup[b['id']]['region']
        checks['beads']+=1
    for name,sha in json.loads((OUT/'preserved-hashes.json').read_text()).items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha;checks['preserved_files']+=1
    selected=json.loads((OUT/'selection.json').read_text());p=Parameters(**selected['parameters']);fresh,records,edges,summary=refine(native,srgb,old,p);assert [{k:v for k,v in r.items() if k!='direction_stops'} for r in fresh]==beads;checks['exact_reproduced_records']=len(records)
    assert len(records)==len(old) and len({r['id'] for r in records})==len(old)
    for r in records:
        assert r['accepted']==(not r['reasons'])
        if 'black-secondary' in r['reasons']:
            g=r['black_ownership'];assert g['dark_bridge'] and g['dominant'];assert g['peak_ratio_to_strongest']<=p.secondary_peak_ratio;assert g['contrast_ratio_to_strongest']<=p.secondary_contrast_ratio;checks['secondary_reflections']=checks.get('secondary_reflections',0)+1
    save('validation.json',dict(checks=checks,source_image_sha256=data['source_image_sha256'],profile=profile,scope='Exact pixels, connected masks, measured centroids, maximum luminance, native RGB/HSV, enclosed dark signal, no accepted overlap, stable IDs, closed contours, every R272 accepted candidate retained, old hashes and exact image-only regeneration. Not physical-bead ground truth.'));print(json.dumps(checks),flush=True)
if __name__=='__main__':main()
