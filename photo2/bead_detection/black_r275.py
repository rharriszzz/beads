"""Additional whole-band dark-perimeter controls after residual gap inspection."""
import json,sys
from copy import deepcopy
from dataclasses import replace
from collections import Counter
import numpy as np
from PIL import Image,ImageOps
from .centerline_r275 import ROOT,OUT,Band,load_rows,save,write_rows
from .recover_r275 import Recovery,resolve
from .coverage_r272 import Parameters,black_region
from .brightness_r270 import color_managed_photo

def main():
 path=OUT/'layered-inventory.json'
 if not path.exists() or "--refresh" in sys.argv:path.write_bytes((OUT/'inventory.json').read_bytes())
 old=json.loads(path.read_text());base=json.loads((ROOT/'photo2/review/r272-coverage/inventory.json').read_text())['beads'];native=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));srgb,_=color_managed_photo();band=Band();engine=Recovery(native,srgb,base,band);raw=[r for r in load_rows(OUT/'all-band-maxima.jsonl.gz') if r['window']==1];summaries={}
 for level in (.36,.40):
  rows=[]
  for p in raw:
   r=dict(id=f"D{int(level*100)}-"+p['id'],anchor=p['anchor'],reasons=[],accepted=False,confidence={},source_maximum=p);black_region(r,native,srgb,engine.hsv,engine.nhsv,engine.lum,engine.paper,replace(Parameters(),black_maximum_value=level));rows.append(r)
  beads,loc,dec=resolve(rows,old,band);write_rows(f'black-{level:.2f}-decisions.jsonl.gz',dec);new=[r for r in dec if r['accepted']];summaries[str(level)]=dict(interiors=len(beads),locations=len(loc),new_ids=[r['id'] for r in new],statuses=dict(Counter(r['status'] for r in dec)),reasons=dict(Counter(k for r in dec for k in r['reasons'])))
  if level==.40:
   data=deepcopy(old);data.update(beads=beads,locations=loc);save('inventory.json',data)
 save('black-controls.json',dict(selected=.40,controls=summaries,note='First enclosed dark perimeter at higher encoded-Y threshold; all saturation, neutral shell, contrast, size, paper and ownership tests unchanged. Whole band, not individual gaps.'));print(summaries,flush=True)
if __name__=='__main__':main()
