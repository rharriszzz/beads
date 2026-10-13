"""Independent full-photo measurements, source preservation and known controls."""
import hashlib,json,gzip,time
from collections import Counter
import numpy as np
from PIL import Image,ImageOps
from scipy import ndimage as ndi
from matplotlib.colors import rgb_to_hsv
from .brightness_r270 import color_managed_photo,linearize,encode
from .inventory_r272 import CROSS
from .experiment_coverage_r272 import ROOT,OUT,save,check_budget

def main():
    check_budget();data=json.loads((OUT/'inventory.json').read_text());beads=data['beads'];srgb,profile=color_managed_photo();native=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));lum=linearize(srgb/255.)@np.array([.2126,.7152,.0722]);hsv=rgb_to_hsv(srgb/255.);occupied=np.zeros(lum.shape,np.uint8);checks=Counter()
    for i,b in enumerate(beads,1):
        assert b['inventory_number']==i;assert b['color'] in ('black','red','yellow');assert b['accepted'] and not b['reasons'];assert b['id']==f"{'K' if b['color']=='black' else 'C'}-{b['anchor'][0]:04d}-{b['anchor'][1]:04d}"
        points={}
        for key in ('region','bright_patch'):
            r=b[key];pts=np.array([(x,y) for y,a,z in r['runs'] for x in range(a,z+1)]);assert len(pts)==r['pixel_count'];assert len(set(map(tuple,pts)))==len(pts);np.testing.assert_allclose(pts.mean(axis=0),r['centroid'],atol=1e-12);box=r['bbox'];m=np.zeros((box[3]-box[1],box[2]-box[0]),bool);m[pts[:,1]-box[1],pts[:,0]-box[0]]=True;assert ndi.label(m,CROSS)[1]==1;assert not(ndi.binary_fill_holes(m)&~m).any() if key=='region' else True;points[key]=set(map(tuple,pts));checks[key+'_pixels']+=len(pts)
        assert points['bright_patch']<=points['region'];assert b['region']['pixel_count']<=870
        coords=np.array(sorted(points['region'],key=lambda p:(p[1],p[0])));scores=lum[coords[:,1],coords[:,0]];xy=coords[np.argmax(scores)];p=b['brightest'];assert [p['x'],p['y']]==xy.tolist();assert abs(p['luminance']-scores.max())<1e-12;assert p['rgb_srgb']==srgb[xy[1],xy[0]].tolist();assert p['rgb_native']==native[xy[1],xy[0]].tolist();np.testing.assert_allclose([p['hsv_srgb'][k] for k in ('h','s','v')],hsv[xy[1],xy[0]]*[360,1,1]);assert np.all(occupied[coords[:,1],coords[:,0]]==0);occupied[coords[:,1],coords[:,0]]=1
        for key in ('raw','smooth'):assert b['outline'][key][0]==b['outline'][key][-1]
        if b['color']=='black':
            shell=b['dark_perimeter'];pts=np.array([(x,y) for y,a,z in shell['runs'] for x in range(a,z+1)]);assert shell['signal']=='icc-gray' and shell['sigma']==0;values=encode(lum[pts[:,1],pts[:,0]]);assert shell['closed'];assert np.max(values)<=shell['threshold']+1e-12;np.testing.assert_allclose(values.max(),shell['maximum_value']);checks['complete_native_dark_perimeters']+=1
        else:assert b['primary_endpoint']==b['anchor'];assert b['color_evidence']['colored_core_fraction']>=.40;assert b['interior_attempts'][-1]['pre_retreat_pixels']<=870
        checks['beads']+=1
    for name,sha in json.loads((OUT/'preserved-hashes.json').read_text()).items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha;checks['preserved_files']+=1
    assert hashlib.sha256((OUT/'photo-samples.json').read_bytes()).hexdigest()==(OUT/'photo-samples.sha256').read_text().strip()
    archive=np.load(OUT/'all-maxima.npz');mask={k:archive[k] for k in archive.files};n=Counter();plateaus=Counter()
    with gzip.open(OUT/'candidates.jsonl.gz','rt') as f:
        for line in f:
            r=json.loads(line);key='raw' if r['pathway']=='black' else 'mean7';plateaus[key]+=1
            for x,y in r['plateau_pixels']:assert mask[key][y,x];n[key]+=1
            assert r['accepted']==(not r['reasons'])
    for key in mask:assert n[key]==int(mask[key].sum())
    checks.update({k+'_maximum_pixels':v for k,v in n.items()});checks.update({k+'_plateaus':v for k,v in plateaus.items()});save('validation.json',dict(checks=checks,source_image_sha256=data['source_image_sha256'],profile=profile,scope='Exact pixels, connected masks, measured centroids, maximum luminance, native RGB/HSV, enclosed dark signal, no accepted overlap, IDs, contours, every maximum retained, old evidence hashes. Not physical-bead ground truth.'));print(json.dumps(checks),flush=True)
if __name__=='__main__':main()
