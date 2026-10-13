"""Control dark-perimeter color purity independently of darkness and peak neutrality."""
import json,sys
from copy import deepcopy
from dataclasses import replace
from collections import Counter
import numpy as np
from PIL import Image,ImageOps
from .centerline_r275 import ROOT,OUT,Band,save,load_rows,write_rows
from .recover_r275 import Recovery,resolve
from .coverage_r272 import Parameters,black_region
from .brightness_r270 import color_managed_photo

def main():
 path=OUT/'before-material-inventory.json'
 if not path.exists() or '--refresh' in sys.argv:path.write_bytes((OUT/'inventory.json').read_bytes())
 old=json.loads(path.read_text());base=json.loads((ROOT/'photo2/review/r272-coverage/inventory.json').read_text())['beads'];native=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));srgb,_=color_managed_photo();band=Band();e=Recovery(native,srgb,base,band);raw=[r for r in load_rows(OUT/'all-band-maxima.jsonl.gz') if r['window']==1];summaries={}
 for fraction in (.40,.35,.25):
  rows=[]
  for p in raw:
   r=dict(id=f'MAT{int(fraction*100)}-'+p['id'],anchor=p['anchor'],reasons=[],accepted=False,confidence={},source_maximum=p);black_region(r,native,srgb,e.hsv,e.nhsv,e.lum,e.paper,replace(Parameters(),black_maximum_value=.40,black_surround_fraction=fraction));rows.append(r)
  beads,loc,dec=resolve(rows,old,band);write_rows(f'material-{fraction:.2f}-decisions.jsonl.gz',dec);summaries[str(fraction)]=dict(interiors=len(beads),locations=len(loc),new_ids=[r['id'] for r in dec if r['accepted']],statuses=dict(Counter(r['status'] for r in dec)))
  if fraction==.25:
   data=deepcopy(old);data.update(beads=beads,locations=loc);save('inventory.json',data)
 save('material-controls.json',dict(selected=.25,controls=summaries));print(summaries)
if __name__=='__main__':main()
