"""Stable, isolated dim color can retain a small honest hue-supported core."""
import json,sys
from copy import deepcopy
from collections import Counter
import numpy as np
from scipy.spatial import cKDTree
from PIL import Image,ImageOps
from .centerline_r275 import ROOT,OUT,Band,save,load_rows,write_rows
from .recover_r275 import Recovery,resolve
from .core_r275 import core
from .brightness_r270 import color_managed_photo
from .interiors_r273 import pixels

def proposals(e,peaks,old):
 colored=[p for p in peaks if p['window'] in (5,7,9)];trees={n:cKDTree([p['anchor'] for p in colored if p['window']==n]) for n in (5,7,9)} if all(any(p['window']==n for p in colored) for n in (5,7,9)) else {};known=np.array([[l['point']['x'],l['point']['y']] for l in old['locations']]);owned=set().union(*(pixels(r) for r in old['beads']));rows=[]
 for p in colored:
  if p['window']!=7 or not .025<=p['score']<.04 or not trees or (len(known) and np.linalg.norm(known-p['anchor'],axis=1).min()<16):continue
  spread=max(trees[n].query(p['anchor'])[0] for n in (5,7,9))
  if spread>3:continue
  r=e.new_colored(p['anchor'],'DIM',True);r['source_maximum']=p;ev=r.get('color_evidence',{})
  if not r.get('region') or ev.get('color_samples',0)<30 or ev.get('hue_deviation90',180)>10 or ev.get('colored_core_fraction',0)<.8:continue
  r=core(e,r,owned,minimum_radius=2);r['confidence']['window_endpoint_spread']=float(spread);r['source_maximum']=p;r['warnings']=r.get('warnings',[])+['Dim stable color: small interior retained under stronger hue and isolation checks; full extent remains uncertain.'];rows.append(r)
 return rows

def main():
 path=OUT/'before-dim-inventory.json'
 if not path.exists() or '--refresh' in sys.argv:path.write_bytes((OUT/'inventory.json').read_bytes())
 old=json.loads(path.read_text());base=json.loads((ROOT/'photo2/review/r272-coverage/inventory.json').read_text())['beads'];native=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));srgb,_=color_managed_photo();band=Band();e=Recovery(native,srgb,base,band,pale=True);rows=proposals(e,load_rows(OUT/'all-band-maxima.jsonl.gz'),old);beads,loc,dec=resolve(rows,old,band);write_rows('dim-decisions.jsonl.gz',dec);data=deepcopy(old);data.update(beads=beads,locations=loc);save('inventory.json',data);summary=dict(interiors=len(beads),locations=len(loc),new=[r['id'] for r in dec if r['accepted']],statuses=dict(Counter(r['status'] for r in dec)));save('dim-summary.json',summary);print(summary)
if __name__=='__main__':main()
