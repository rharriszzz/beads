"""Stable peaks survive irregular broad growth via a rounded, supported inset core.
No bead shape/center is predicted: every disk pixel must exist in the eroded native
R274 hue/path support. This is an interior fallback, never a whole-bead outline.
"""
import json,sys
from copy import deepcopy
from collections import Counter
import numpy as np
from PIL import Image,ImageOps
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from skimage.morphology import disk
from .centerline_r275 import ROOT,OUT,Band,save,load_rows,write_rows
from .recover_r275 import Recovery,resolve
from .brightness_r270 import color_managed_photo
from .hue_r274 import grow,SELECTED
from .inventory_r272 import CROSS
from .coverage_r272 import complete
from .interiors_r273 import pixels

def core(e,rec,owned,minimum_radius=3):
 broad=grow(rec,e.native,e.srgb,e.hsv,e.lum,e.mean3,e.paper,e.surface,e.palette,SELECTED);out=deepcopy(rec);out['accepted']=False;out['reasons']=['no-supported-rounded-core'];reg=broad.get('supported_region')
 if not reg or not reg['runs']:return out
 x0,y0,x1,y1=reg['bbox'];mask=np.zeros((y1-y0+4,x1-x0+4),bool);origin=(x0-2,y0-2)
 for y,a,b in reg['runs']:mask[y-origin[1],a-origin[0]:b-origin[0]+1]=True
 inset=ndi.binary_erosion(mask,CROSS,iterations=2);ay,ax=np.where(inset);px,py=rec['anchor'];allowed_centers=[(int(x),int(y)) for x,y in zip(ax,ay) if (x+origin[0]-px)**2+(y+origin[1]-py)**2<=25];choices=[]
 for x,y in allowed_centers:
  for radius in range(8,minimum_radius-1,-1):
   yy,xx=np.mgrid[-radius:radius+1,-radius:radius+1];keep=xx*xx+yy*yy<=radius*radius;gx=xx[keep]+x;gy=yy[keep]+y
   if gx.min()<0 or gy.min()<0 or gx.max()>=inset.shape[1] or gy.max()>=inset.shape[0] or not inset[gy,gx].all():continue
   pts=set(zip((gx+origin[0]).tolist(),(gy+origin[1]).tolist()))
   if pts&owned:continue
   choices.append((-len(pts),(x+origin[0]-px)**2+(y+origin[1]-py)**2,y,x,radius));break
 if not choices:return out
 _,_,cy,cx,radius=min(choices);yy,xx=np.indices(inset.shape);selected=(xx-cx)**2+(yy-cy)**2<=radius*radius;out['reasons']=[];complete(out,selected,origin,e.native,e.srgb,e.hsv,e.lum);out['supported_inset_pixels']=int(inset.sum());out['core_radius']=radius;out['core_center']=[cx+origin[0],cy+origin[1]];out['recovery_method']='stable-peak-supported-rounded-core';out['warnings']=['Broad interior remains uncertain; round native core lies entirely inside twice-retreated R274 hue/path support.','Core shape is conservative support, not estimated full bead shape.'];out['broad_attempt']=dict(reasons=broad['reasons'],pixels=broad.get('region',{}).get('pixel_count',0));return out

def main():
 path=OUT/'before-core-inventory.json'
 if not path.exists() or '--refresh' in sys.argv:path.write_bytes((OUT/'inventory.json').read_bytes())
 old=json.loads(path.read_text());base=json.loads((ROOT/'photo2/review/r272-coverage/inventory.json').read_text())['beads'];native=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));srgb,_=color_managed_photo();band=Band();e=Recovery(native,srgb,base,band,pale=True);owned=set().union(*(pixels(r) for r in old['beads']));known=np.array([[l['point']['x'],l['point']['y']] for l in old['locations']]);peaks=load_rows(OUT/'all-band-maxima.jsonl.gz');trees={n:cKDTree([p['anchor'] for p in peaks if p['window']==n]) for n in (5,7,9)};rows=[]
 for p in peaks:
  if p['window']!=7 or p['score']<.04 or np.linalg.norm(known-p['anchor'],axis=1).min()<7:continue
  if max(trees[n].query(p['anchor'])[0] for n in (5,7,9))>3:continue
  r=e.new_colored(p['anchor'],'CORE',True);r['source_maximum']=p
  if not r.get('region'):continue
  rows.append(core(e,r,owned))
 beads,loc,dec=resolve(rows,old,band);write_rows('core-decisions.jsonl.gz',dec);data=deepcopy(old);data.update(beads=beads,locations=loc);save('inventory.json',data);summary=dict(interiors=len(beads),locations=len(loc),new=[r['id'] for r in dec if r['accepted']],statuses=dict(Counter(r['status'] for r in dec)));save('core-summary.json',summary);print(summary)
if __name__=='__main__':main()
