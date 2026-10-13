"""Connected native hue layers for fragmented red/yellow supports; no forced fill."""
from copy import deepcopy
import json,sys
from collections import Counter
import numpy as np
from PIL import Image,ImageOps
from scipy import ndimage as ndi
from skimage.morphology import disk
from .centerline_r275 import ROOT,OUT,Band,save,load_rows,write_rows
from .recover_r275 import Recovery,resolve
from .brightness_r270 import color_managed_photo
from .inventory_r272 import hue_distance,component,CROSS
from .coverage_r272 import complete
from .interiors_r273 import pixels,shape

def connected(e,rec,owned):
 x,y=rec['anchor'];r=32;origin=(x-r,y-r);hs=e.hsv[y-r:y+r+1,x-r:x+r+1];l=e.lum[y-r:y+r+1,x-r:x+r+1];pp=e.paper[y-r:y+r+1,x-r:x+r+1];out=deepcopy(rec);out['accepted']=False;out['reasons']=['connected-no-safe-layer'];own=rec['color_evidence']['hue'];other=e.palette.get('red' if rec['color']=='yellow' else 'yellow');yy,xx=np.mgrid[-r:r+1,-r:r+1];chromatic=(hs[:,:,1]>=.35)&(hue_distance(hs[:,:,0]*360,own)<=22);near=ndi.distance_transform_edt(~chromatic)<=6;highlight=(hs[:,:,1]<.35)&(xx*xx+yy*yy<=64)&near;vote=~((hs[:,:,1]>=.35)&(hs[:,:,1]*hs[:,:,2]>=.055))|(hue_distance(hs[:,:,0]*360,other)-hue_distance(hs[:,:,0]*360,own)>=2) if other is not None else np.ones(l.shape,bool);allowed=(chromatic|highlight)&vote&(pp==0);peak=float(l[r,r]);attempts=[]
 for fraction in (.12,.20,.30,.40,.50,.60,.70):
  raw=component(allowed&(l>=max(.02,fraction*peak)),(r,r));eroded=ndi.binary_erosion(ndi.binary_opening(raw,structure=disk(2)),CROSS,iterations=2);seed=(r,r)
  if not eroded[r,r]:
   ey,ex=np.where(eroded);near=sorted(zip(((ex-r)**2+(ey-r)**2).tolist(),ey.tolist(),ex.tolist()))
   if near and near[0][0]<=9:seed=(near[0][2],near[0][1])
  clean=component(eroded,seed);ys,xs=np.where(clean);pts=set(zip((xs+origin[0]).tolist(),(ys+origin[1]).tolist()));overlap=len(pts&owned);ok=bool(raw.sum()<=870 and clean.sum()>=45 and not overlap and shape(clean)['solidity']>=.84 and not np.any(ndi.binary_fill_holes(clean)&~clean) and not(raw[0].any() or raw[-1].any() or raw[:,0].any() or raw[:,-1].any()));attempts.append(dict(fraction=fraction,precleanup=int(raw.sum()),pixels=int(clean.sum()),overlap=overlap,accepted=ok))
  if ok:
   out['reasons']=[];complete(out,clean,origin,e.native,e.srgb,e.hsv,e.lum);out['connected_attempts']=attempts;out['interior_seed']=[int(seed[0]+origin[0]),int(seed[1]+origin[1])];out['recovery_method']='connected-hue-layer';out['warnings']=['Connected hue-consistent native layer; all pixels image-supported; no arbitrary ownership partition.'];return out
 out['connected_attempts']=attempts;return out

def main():
 path=OUT/'before-connected-inventory.json'
 if not path.exists() or '--refresh' in sys.argv:path.write_bytes((OUT/'inventory.json').read_bytes())
 old=json.loads(path.read_text());base=json.loads((ROOT/'photo2/review/r272-coverage/inventory.json').read_text())['beads'];native=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));srgb,_=color_managed_photo();band=Band();e=Recovery(native,srgb,base,band,pale=True);owned=set().union(*(pixels(r) for r in old['beads']));rows=[];known=np.array([[l['point']['x'],l['point']['y']] for l in old['locations']])
 for p in load_rows(OUT/'all-band-maxima.jsonl.gz'):
  if p['window']==1 or p['score']<.025 or np.linalg.norm(known-p['anchor'],axis=1).min()<7:continue
  x,y=p['anchor'];color,ev=e.classify(x,y,True)
  if color is None:continue
  rec=dict(id=f'CON{p["window"]}-{x:04d}-{y:04d}',anchor=p['anchor'],color=color,color_evidence=ev,confidence={},source_maximum=p,accepted=False,reasons=[]);rows.append(connected(e,rec,owned))
 beads,loc,dec=resolve(rows,old,band);write_rows('connected-decisions.jsonl.gz',dec);data=deepcopy(old);data.update(beads=beads,locations=loc);save('inventory.json',data);summary=dict(interiors=len(beads),locations=len(loc),new=[r['id'] for r in dec if r['accepted']],statuses=dict(Counter(r['status'] for r in dec)));save('connected-summary.json',summary);print(summary)
if __name__=='__main__':main()
