"""Independent inventory, preservation, native-mask and circular-spacing checks."""
import json,hashlib,subprocess
from collections import Counter
import numpy as np
from PIL import Image,ImageOps
from scipy import ndimage as ndi
from matplotlib.colors import rgb_to_hsv
from .centerline_r275 import ROOT,OUT,Band,save
from .brightness_r270 import color_managed_photo,linearize
from .interiors_r273 import pixels,mask_local

def main():
 data=json.loads((OUT/'inventory.json').read_text());old=json.loads((ROOT/'photo2/review/r274/inventory.json').read_text());loc={l['id']:l for l in data['locations']};beads={b['id']:b for b in data['beads']};allloc=loc|{l['id']:l for l in data.get('suppressed_locations',[])}|{l['id']:l for l in data.get('superseded_locations',[])};allbeads=beads|{b['id']:b for b in data.get('suppressed_beads',[])}|{b['id']:b for b in data.get('superseded_beads',[])};native=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));srgb,_=color_managed_photo();hsv=rgb_to_hsv(srgb/255.);lum=linearize(srgb/255.)@np.array([.2126,.7152,.0722]);checks=Counter();seen=set();band=Band()
 assert len(loc)==len(data['locations']) and len(beads)==len(data['beads']);assert [l['inventory_number'] for l in data['locations']]==list(range(1,len(loc)+1))
 for l in old['locations']:
  assert allloc[l['id']]['point']==l['point'];assert allloc[l['id']]['color']==l['color'];assert allloc[l['id']].get('prior_inventory_number',allloc[l['id']]['inventory_number'])==l['inventory_number'];checks['preserved_prior_locations']+=1
  if l['id'] not in loc:checks['prior_locations_suppressed_with_evidence']+=1;assert band.qualifies([l['point']['x'],l['point']['y']],allbeads[l['id']]['region'])['in_band'];assert any(r['weak']==l['id'] and r['suppress'] for r in data['dominance_decisions'])
 for b in old['beads']:
  assert all(allbeads[b['id']][key]==b[key] for key in ('region','brightest','bright_patch','outline','color'));checks['preserved_prior_interiors']+=1
 for b in beads.values():
  pts=pixels(b);assert not pts&seen;seen|=pts;assert len(pts)==b['region']['pixel_count']<=870;assert ndi.label(mask_local(b['region']))[1]==1;assert not np.any(ndi.binary_fill_holes(mask_local(b['region']))&~mask_local(b['region']));assert pixels(b,'bright_patch')<=pts;patch=np.array(list(pixels(b,'bright_patch')));assert len(patch)==b['bright_patch']['pixel_count'];np.testing.assert_allclose(patch.mean(axis=0),b['bright_patch']['centroid']);assert ndi.label(mask_local(b['bright_patch']))[1]==1
  a=np.array(sorted(pts,key=lambda p:(p[1],p[0])));np.testing.assert_allclose(a.mean(axis=0),b['region']['centroid']);v=lum[a[:,1],a[:,0]];x,y=a[np.argmax(v)];peak=b['brightest'];assert (int(x),int(y))==(peak['x'],peak['y']);assert peak['luminance']==float(v.max());assert peak['rgb_srgb']==srgb[y,x].tolist();assert peak['rgb_native']==native[y,x].tolist();np.testing.assert_allclose([peak['hsv_srgb'][k] for k in ('h','s','v')],hsv[y,x]*[360,1,1]);assert all(b['outline'][k][0]==b['outline'][k][-1] for k in ('raw','smooth'));checks['measured_masks']+=1;checks['native_pixels']+=len(pts)
 for l in loc.values():
  x,y=l['point']['x'],l['point']['y'];assert l['point']['luminance']==float(lum[y,x]);r=beads.get(l['id']);assert l['centerline_near']==band.qualifies([x,y],r['region'] if r else None);checks['locations']+=1
  if l['source']=='R275 automatic band recovery':assert l['centerline_near']['in_band'];checks['new_target_locations']+=1
 assert set(l['id'] for l in data['locations']).isdisjoint(r['id'] for r in data['uncertain'])
 import csv
 increments=list(csv.DictReader((OUT/'angular-increments.csv').open()))
 for version in ('r274','r275'):
  for subset in ('whole-target','central-anchors','measured-crossings'):
   rr=[r for r in increments if r['version']==version and r['subset']==subset];assert abs(sum(float(r['step_degrees']) for r in rr)-360)<1e-8;checks['closed_angular_loops']+=1
 groups=json.loads((OUT/'stations.json').read_text())['groups'];assert abs(sum(r['step_degrees'] for r in groups)-360)<1e-8;ids=[id for r in groups for id in r['ids']];assert len(ids)==len(set(ids))==sum(l['centerline_near']['in_band'] for l in loc.values());checks['station_members_once']=len(ids)
 js=(OUT/'inventory.js').read_text();assert json.loads(js.removeprefix('window.BEAD_INVENTORY=').removesuffix(';\n'))==data
 # All protected artifacts compared with the actual parent Git commit, not a
 # newly generated hash pretending to establish preservation.
 files=subprocess.check_output(['git','ls-files','photo2/review/r272','photo2/review/r272-coverage','photo2/review/r273','photo2/review/r274','photo2/bead_detection/*r272.py','photo2/bead_detection/*r273.py','photo2/bead_detection/*r274.py','photo2/HUE_INTERIORS_R274.md','photo2/INTERIORS_R273.md','photo2/COVERAGE_R272.md'],cwd=ROOT,text=True).splitlines();hashes={}
 for file in files:
  raw=(ROOT/file).read_bytes();gitsha=subprocess.check_output(['git','hash-object','--stdin'],input=raw,cwd=ROOT).decode().strip();expected=subprocess.check_output(['git','rev-parse','HEAD:'+file],cwd=ROOT,text=True).strip();assert gitsha==expected,file;hashes[file]=hashlib.sha256(raw).hexdigest()
 checks['preserved_upstream_files']=len(files);save('preserved-hashes.json',hashes);save('validation.json',dict(checks=checks,scope='Exact measurements and preserved successful records; no independent claim of physical bead identity or 100% photographic recall.'));print(dict(checks))
if __name__=='__main__':main()
