"""Consistent colored enclosure recovers desaturated highlights without a count prior."""
import json,sys
from copy import deepcopy
from collections import Counter
import numpy as np
from PIL import Image,ImageOps
from .centerline_r275 import ROOT,OUT,Band,save,load_rows,write_rows
from .recover_r275 import Recovery,resolve
from .brightness_r270 import color_managed_photo

def main():
 path=OUT/'before-pale-inventory.json'
 if not path.exists() or "--refresh" in sys.argv:path.write_bytes((OUT/'inventory.json').read_bytes())
 old=json.loads(path.read_text());base=json.loads((ROOT/'photo2/review/r272-coverage/inventory.json').read_text())['beads'];native=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));srgb,_=color_managed_photo();band=Band();engine=Recovery(native,srgb,base,band,pale=True);rows=[]
 for peak in load_rows(OUT/'all-band-maxima.jsonl.gz'):
  if peak['window']==1:continue
  r=engine.new_colored(peak['anchor'],'P'+str(peak['window']),True);r['source_maximum']=peak
  if not r.get('color_evidence',{}).get('pale_highlight_evidence',{}).get('accepted'):continue
  if r.get('region'):r=engine.interior(r,layered=True);r['source_maximum']=peak
  rows.append(r)
 beads,loc,dec=resolve(rows,old,band);write_rows('pale-decisions.jsonl.gz',dec);data=deepcopy(old);data.update(beads=beads,locations=loc);save('inventory.json',data);summary=dict(interiors=len(beads),locations=len(loc),statuses=dict(Counter(r['status'] for r in dec)),new=[dict(id=r['id'],color=r['color'],brightest=r['brightest'],recovery_method=r.get('recovery_method')) for r in dec if r['accepted']]);save('pale-summary.json',summary);print({k:v for k,v in summary.items() if k!='new'},'new',len(summary['new']))
if __name__=='__main__':main()
