"""Independent native measurements, stable locations, old hashes and reproduction."""
import json,hashlib
from collections import Counter
import numpy as np
from PIL import Image,ImageOps
from scipy import ndimage as ndi
from matplotlib.colors import rgb_to_hsv
from .experiment_r274 import ROOT,OUT,save
from .brightness_r270 import color_managed_photo,linearize
from .hue_r274 import refine,VARIANTS
from .coverage_r272 import detect as baseline
from .interiors_r273 import refine as old_refine,pixels,mask_local

def main():
 data=json.loads((OUT/'inventory.json').read_text());locations=data['locations'];beads=data['beads'];old=json.loads((ROOT/'photo2/review/r273/inventory.json').read_text())['beads'];oldmap={r['id']:r for r in old};locmap={r['id']:r for r in locations};checks=Counter();srgb,_=color_managed_photo();native=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));lum=linearize(srgb/255.)@np.array([.2126,.7152,.0722]);hsv=rgb_to_hsv(srgb/255.);seen=set()
 assert len(locmap)==len(locations) and [r['inventory_number'] for r in locations]==list(range(1,len(locations)+1))
 for r in old:
  assert r['id'] in locmap and locmap[r['id']]['point']==r['brightest'];checks['preserved_trusted_locations']+=1
 for r in beads:
  pts=pixels(r);assert not pts&seen;seen|=pts;assert r['region']['pixel_count']==len(pts)<=870;assert ndi.label(mask_local(r['region']))[1]==1;assert not np.any(ndi.binary_fill_holes(mask_local(r['region']))&~mask_local(r['region']));a=np.array(sorted(pts,key=lambda z:(z[1],z[0])));np.testing.assert_allclose(a.mean(axis=0),r['region']['centroid']);assert pixels(r,'bright_patch')<=pts
  patch=np.array(list(pixels(r,'bright_patch')));assert len(patch)==r['bright_patch']['pixel_count'];np.testing.assert_allclose(patch.mean(axis=0),r['bright_patch']['centroid']);assert ndi.label(mask_local(r['bright_patch']))[1]==1
  values=lum[a[:,1],a[:,0]];x,y=a[np.argmax(values)];b=r['brightest'];assert (x,y)==(b['x'],b['y']);assert b['luminance']==float(values.max());assert b['rgb_srgb']==srgb[y,x].tolist();assert b['rgb_native']==native[y,x].tolist();np.testing.assert_allclose([b['hsv_srgb'][k] for k in ('h','s','v')],hsv[y,x]*[360,1,1]);assert locmap[r['id']]['interior_status']=='accepted'
  for k in ('raw','smooth'):assert r['outline'][k][0]==r['outline'][k][-1]
  if r['color']=='black':assert all(r[k]==oldmap[r['id']][k] for k in ('region','brightest','bright_patch','dark_perimeter'));checks['unchanged_black_regions']+=1
  checks['interiors']+=1;checks['native_pixels']+=len(pts)
 for l in locations:
  x,y=l['point']['x'],l['point']['y'];assert l['point']['luminance']==float(lum[y,x]);checks['locations']+=1
  if l['interior_status']!='accepted':assert l['id'] not in {r['id'] for r in beads};assert l['explanations'];checks['locations_with_uncertain_interior']+=1
 for path,sha in json.loads((OUT/'preserved-hashes.json').read_text()).items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==sha,path;checks['preserved_files']+=1
 base=baseline(native,srgb)[0];oldrows=old_refine(native,srgb,base)[1];name=json.loads((OUT/'selection.json').read_text())['method'];fresh,loc,rows,s=refine(native,srgb,base,oldrows,VARIANTS[name]);compact=[{k:v for k,v in r.items() if k not in ('direction_stops','r272_measurements','supported_region')} for r in fresh];assert compact==beads;assert loc==locations;checks['exact_regenerated_decisions']=len(rows)
 for r in fresh:
  if r['color']!='black':assert pixels(r)<=pixels(r,'supported_region')
 save('validation.json',dict(checks=checks,scope='Native measurements, unchanged black cores, preserved location coordinates, all old hashes and exact end-to-end image-only regeneration. No photographic ground-truth claim.'));print(dict(checks),flush=True)
if __name__=='__main__':main()
