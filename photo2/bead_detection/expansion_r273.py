"""Paired expansion controls requested after reviewing early R273 interiors."""
import json,time
from dataclasses import replace
import numpy as np
from PIL import Image,ImageOps
from .experiment_r273 import ROOT,OUT,save,lines
from .brightness_r270 import color_managed_photo
from .interiors_r273 import Parameters,refine
from .review_r273 import triplet
VARIANTS={
 'remedy-shape':replace(Parameters(),method='relative-valley',radius=32,floor_fraction=.035,hue_degrees=32,step_hue_degrees=18,valley_fraction=.25,valley_retreat=1,retreat=2,minimum_solidity=.84),
 'remedy-background':replace(Parameters(),method='relative-valley',radius=32,floor_fraction=.035,hue_degrees=32,step_hue_degrees=18,valley_fraction=.25,valley_retreat=1,retreat=2,uncertain_bridge=True),
 'remedy-combined':replace(Parameters(),method='relative-valley',radius=32,floor_fraction=.035,hue_degrees=32,step_hue_degrees=18,valley_fraction=.25,valley_retreat=1,retreat=2,minimum_solidity=.84,uncertain_bridge=True),
 'relative-valley-safe':replace(Parameters(),method='relative-valley',radius=32,floor_fraction=.035,hue_degrees=32,step_hue_degrees=18,valley_fraction=.25,valley_retreat=1,retreat=2),
 'relative-valley-inset':replace(Parameters(),method='relative-valley',radius=32,floor_fraction=.035,hue_degrees=32,step_hue_degrees=18,valley_fraction=.25,valley_retreat=1),
 'relative-valley':replace(Parameters(),method='relative-valley',radius=32,floor_fraction=.035,hue_degrees=32,step_hue_degrees=18,valley_fraction=.25),
 'relative-valley-wide':replace(Parameters(),method='relative-valley',radius=32,floor_fraction=.035,hue_degrees=32,step_hue_degrees=18,valley_fraction=.5),
 'first-valley':replace(Parameters(),method='first-valley',floor_fraction=.05),
 'lower-floor':replace(Parameters(),floor_fraction=.05),
 'wider-color':replace(Parameters(),floor_fraction=.05,hue_degrees=32,step_hue_degrees=18),
 'shallow-valleys':replace(Parameters(),floor_fraction=.05,hue_degrees=32,step_hue_degrees=18,valley_fraction=.18),
 'dark-envelope':replace(Parameters(),method='star-color',floor_fraction=.05,hue_degrees=32,step_hue_degrees=18),
}
def main(names=None):
 native=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));srgb,_=color_managed_photo();im=Image.fromarray(srgb);base=json.loads((ROOT/'photo2/review/r272-coverage/inventory.json').read_text())['beads'];summaries={}
 for name,p in VARIANTS.items():
  if names is not None and name not in names:continue
  t=time.time();beads,records,edges,summary=refine(native,srgb,base,p);summary['seconds']=time.time()-t;summaries[name]=summary;lines(name+'-candidates.jsonl.gz',records)
  for label,box in [('R00956',[2233,1863,2314,1944]),('R01284',[941,2640,1022,2721]),('red',[2120,1000,2220,1100])]:triplet(im,base,beads,box,name+'-'+label+'.png',name+' / '+label,5)
  print(name,summary,flush=True)
 target=OUT/'expansion-summary.json';prior=json.loads(target.read_text()) if target.exists() else {};save('expansion-summary.json',prior|summaries)
if __name__=='__main__':main()
