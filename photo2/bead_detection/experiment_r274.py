"""Reproducible paired R274 hue experiment; all detector inputs come from pixels."""
from pathlib import Path
import json,gzip,time,hashlib
import numpy as np
from PIL import Image,ImageOps
from .brightness_r270 import color_managed_photo
from .coverage_r272 import detect as base_detect
from .interiors_r273 import refine as old_refine
from .hue_r274 import refine,VARIANTS
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'photo2/review/r274'
def save(name,obj):(OUT/name).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def lines(name,rows):
 with gzip.GzipFile(filename=str(OUT/name),mode='wb',mtime=0) as f:
  for r in rows:f.write((json.dumps(r,separators=(',',':'),allow_nan=False)+'\n').encode())
def main(names=None):
 OUT.mkdir(exist_ok=True);start=time.time();files=[p for p in (ROOT/'photo2/review/r273').glob('*') if p.is_file()]+list((ROOT/'photo2/interior_inventory_r273').glob('*'))+list((ROOT/'photo2/bead_detection').glob('*r273.py'))+[ROOT/'photo2/INTERIORS_R273.md',ROOT/'photo2/RED_LOSSES_R273.md'];save('preserved-hashes.json',{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files});native=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));srgb,profile=color_managed_photo();base=base_detect(native,srgb)[0];old_beads,old_rows,_,_=old_refine(native,srgb,base)
 previous=json.loads((ROOT/'photo2/review/r273/inventory.json').read_text());assert [{k:v for k,v in r.items() if k!='direction_stops'} for r in old_beads]==previous['beads'];print('R273 exactly regenerated',len(old_beads),flush=True);summaries={}
 for name,p in VARIANTS.items():
  if names is not None and name not in names:continue
  t=time.time();b,l,rows,s=refine(native,srgb,base,old_rows,p);s['seconds']=time.time()-t;summaries[name]=s;lines(name+'-candidates.jsonl.gz',rows);save(name+'-locations.json',l);print(name,s,flush=True)
 prior=json.loads((OUT/'summary.json').read_text())['variants'] if (OUT/'summary.json').exists() else {};save('summary.json',dict(variants=prior|summaries,elapsed_seconds=time.time()-start,baseline_exact=True,profile=profile,source_image_sha256=previous['source_image_sha256']));print('done',time.time()-start,flush=True)
if __name__=='__main__':main()
