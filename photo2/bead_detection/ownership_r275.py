"""Retry independent brightness layers when a broad support overlaps a neighbor.
Never cut a mask along another bead's outline. Select a naturally disjoint layer,
retreat conservatively, and preserve the original broad attempt as uncertain.
"""
import json,sys
from copy import deepcopy
from collections import Counter
import numpy as np
from scipy import ndimage as ndi
from skimage.morphology import disk
from PIL import Image,ImageOps
from matplotlib.colors import rgb_to_hsv
from .centerline_r275 import ROOT,OUT,Band,save,load_rows,write_rows
from .brightness_r270 import color_managed_photo,linearize
from .inventory_r272 import component,CROSS
from .coverage_r272 import complete
from .interiors_r273 import pixels,shape
from .recover_r275 import resolve

def contract(r,owned,native,srgb,hsv,lum):
 result=deepcopy(r);box=r['region']['bbox'];x0,y0,x1,y1=box;mask=np.zeros((y1-y0,x1-x0),bool)
 for y,a,b in r['region']['runs']:mask[y-y0,a-x0:b-x0+1]=True
 l=lum[y0:y1,x0:x1];peak=r['brightest']['luminance'];seed=(r['brightest']['x']-x0,r['brightest']['y']-y0);attempts=[]
 for fraction in (.15,.25,.35,.45,.55,.65,.75,.85):
  raw=component(mask&(l>=fraction*peak),seed);clean=component(ndi.binary_erosion(ndi.binary_opening(raw,structure=disk(1)),CROSS),seed);ys,xs=np.where(clean);pts=set(zip((xs+x0).tolist(),(ys+y0).tolist()));overlap=len(pts&owned);ok=bool(clean.sum()>=25 and not overlap and shape(clean)['solidity']>=.85 and not np.any(ndi.binary_fill_holes(clean)&~clean));attempts.append(dict(fraction=fraction,pixels=int(clean.sum()),overlap_pixels=overlap,accepted=ok))
  if ok:
   result['reasons']=[];complete(result,clean,(x0,y0),native,srgb,hsv,lum);result['recovery_method']='naturally-disjoint-hue-brightness-layer';result['ownership_layer_attempts']=attempts;result['warnings'].append('Broad interior overlaps a retained neighbor; smaller naturally disjoint brightness layer retained.');return result
 result['accepted']=False;result['ownership_layer_attempts']=attempts;return result

def main():
 path=OUT/'before-ownership-inventory.json'
 if not path.exists() or "--refresh" in sys.argv:path.write_bytes((OUT/'inventory.json').read_bytes())
 old=json.loads(path.read_text());owned=set().union(*(pixels(r) for r in old['beads']));known={r['id'] for r in old['locations']};native=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));srgb,_=color_managed_photo();hs=rgb_to_hsv(srgb/255.);lum=linearize(srgb/255.)@np.array([.2126,.7152,.0722]);sources=load_rows(OUT/'layered-fallback-decisions.jsonl.gz')+load_rows(OUT/'pale-decisions.jsonl.gz');rows=[]
 for r in sources:
  if r['id'] in known or r.get('color') not in ('red','yellow') or r['reasons']!=['ownership-conflict'] or not r.get('region'):continue
  rows.append(contract(r,owned,native,srgb,hs,lum))
 beads,loc,dec=resolve(rows,old,Band());write_rows('ownership-decisions.jsonl.gz',dec);data=deepcopy(old);data.update(beads=beads,locations=loc);save('inventory.json',data);summary=dict(interiors=len(beads),locations=len(loc),statuses=dict(Counter(r['status'] for r in dec)),new=[r['id'] for r in dec if r['accepted']]);save('ownership-summary.json',summary);print(summary)
if __name__=='__main__':main()
