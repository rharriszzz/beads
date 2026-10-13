"""Post-detection review crop traces; coordinates never enter the detector."""
import csv,json,gzip
from collections import Counter
import numpy as np
from scipy import ndimage as ndi
from PIL import Image
from .experiment_r273 import ROOT,OUT,save,lines
from .brightness_r270 import linearize
from .annular_detect import straight_pixels
from .interiors_r273 import pixels
from .test_r273 import reflections
from .coverage_r272 import detect as baseline
from .interiors_r273 import refine
from .review_r273 import triplet
BOXES={'R00956':[2233,1863,2314,1944],'R01284':[941,2640,1022,2721],'red':[2120,1000,2220,1100]}
def main():
 selected=json.loads((OUT/'selection.json').read_text())['method'];rows=[json.loads(l) for l in gzip.open(OUT/(selected+'-candidates.jsonl.gz'),'rt')];srgb=np.asarray(Image.open(ROOT/'photo2/review/r272/photo-srgb.png'));lum=linearize(srgb/255.)@np.array([.2126,.7152,.0722]);mean3=ndi.uniform_filter(lum,3);traces=[];comparison=[]
 for path in sorted(OUT.glob('*-candidates.jsonl.gz')):
  if path.name.startswith(('synthetic','historical')):continue
  for l in gzip.open(path,'rt'):
   rec=json.loads(l);x,y=rec['anchor'];crop=next((k for k,(x0,y0,x1,y1) in BOXES.items() if x0<=x<x1 and y0<=y<y1),None)
   if not crop or rec['color']=='black':continue
   a=rec['interior_attempts'][-1];comparison.append(dict(crop=crop,method=path.name.removesuffix('-candidates.jsonl.gz'),id=rec['id'],accepted=rec['accepted'],region_pixels=rec.get('region',{}).get('pixel_count',0),supported_pixels=a['supported_pixels'],floor_fraction=a['floor_fraction'],context_open=a['context_open'],reasons=';'.join(rec['reasons']),stops=json.dumps(a['stops'])))
 for rec in rows:
  x,y=rec['anchor'];crop=next((k for k,(x0,y0,x1,y1) in BOXES.items() if x0<=x<x1 and y0<=y<y1),None)
  if not crop or rec['color']=='black':continue
  p=rec['r272_measurements']['brightest'];start=(p['x'],p['y'])
  for stop in rec.get('direction_stops',[]):
   path=straight_pixels(start,tuple(stop['target']));trigger=tuple(stop['trigger']);path=path[:path.index(trigger)+1]
   traces.append(dict(id=rec['id'],crop=crop,accepted=rec['accepted'],stop=stop,steps=[dict(x=int(x),y=int(y),luminance=float(lum[y,x]),mean3=float(mean3[y,x])) for x,y in path]))
 lines('review-direction-traces.jsonl.gz',traces)
 with (OUT/'review-stopping-comparison.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(comparison[0]),lineterminator='\n');w.writeheader();w.writerows(comparison)
 images={};truths={}
 for kind in ('weak','equal','close','separate'):
  rgb,t=reflections(kind);old=baseline(rgb)[0];new,_,_,_=refine(rgb,rgb,old);images[kind]=rgb;truths[kind]=t;triplet(Image.fromarray(rgb),old,new,[30,30,110,80],'synthetic-black-'+kind+'.png','Black reflections: '+kind,4)
 np.savez_compressed(OUT/'black-fixture-inputs.npz',**images);np.savez_compressed(OUT/'black-fixture-truth.npz',**truths)
 beads=[r for r in rows if r['accepted']];cells=Counter((int(r['brightest']['x']//(2540/4)),int(r['brightest']['y']//(3182/4))) for r in beads);save('geography.json',dict(occupied_full_frame_cells=len(cells),grid='4x4; posthoc description, never an acceptance quota',cells={str(k):v for k,v in sorted(cells.items())}));save('review-traces-summary.json',dict(directions=len(traces),rows=len(comparison),crops=BOXES,scope='Review coordinates select output for display only; detector uses no crop coordinates.'))
if __name__=='__main__':main()
