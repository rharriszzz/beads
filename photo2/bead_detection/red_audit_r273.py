"""Diagnose red losses after detection; do not change acceptance or use manual IDs."""
import json,gzip
from collections import Counter
import numpy as np
from PIL import Image,ImageOps
from .climb_r268 import background
from .experiment_r273 import ROOT,OUT,save
from .review_r273 import triplet
from .interiors_r273 import shape,mask_local

def main():
 name='relative-valley-safe';rows=[json.loads(l) for l in gzip.open(OUT/(name+'-candidates.jsonl.gz'),'rt')];old=json.loads((ROOT/'photo2/review/r272-coverage/inventory.json').read_text())['beads'];im=Image.open(ROOT/'photo2/review/r272/photo-srgb.png');summary={};native=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));_,paper,_=background(native)
 for c in ('red','yellow'):
  a=[r for r in rows if r['color']==c];fail=[r for r in a if not r['accepted']];shape_only=[r for r in a if r['reasons']==['interior-irregular']];scope=dict(input=len(a),accepted=sum(r['accepted'] for r in a),excluded=len(fail),reasons=dict(Counter(k for r in fail for k in r['reasons'])),sole_reasons=dict(Counter(r['reasons'][0] for r in fail if len(r['reasons'])==1)),context_and_cap=dict(Counter('open-and-cap' if r['interior_attempts'][-1]['context_open'] and r['supported_region']['pixel_count']>870 else 'open-only' if r['interior_attempts'][-1]['context_open'] else 'cap-only' if r['supported_region']['pixel_count']>870 else 'bounded' for r in a)),shape_only_solidity_quantiles=np.quantile([r['shape']['solidity'] for r in shape_only],[0,.25,.5,.75,1]).tolist(),shape_only_above_084=sum(r['shape']['solidity']>=.84 for r in shape_only),shape_only_above_080=sum(r['shape']['solidity']>=.8 for r in shape_only),stops=dict(Counter(k for r in fail for d in r.get('direction_stops',[]) for k in [d['reason']])));scope['background_stop_types']=dict(Counter('confident-paper' if paper[d['trigger'][1],d['trigger'][0]]==1 else 'uncertain-paper-context' for r in fail for d in r.get('direction_stops',[]) if d['reason']=='background'));summary[c]=scope
 red=[r for r in rows if r['color']=='red'];examples=[]
 for category,pool in [('shape-only',[r for r in red if r['reasons']==['interior-irregular']]),('open-and-shape',[r for r in red if 'interior-open' in r['reasons'] and 'interior-irregular' in r['reasons']]),('open-only',[r for r in red if r['reasons']==['interior-open']])]:
  pool=sorted(pool,key=lambda r:(r['anchor'][1],r['anchor'][0]))
  for i,fraction in enumerate((.25,.75),1):
   r=pool[min(len(pool)-1,int(len(pool)*fraction))];x,y=r['anchor'];file=f'red-excluded-{category}-{i}.png';title=f"Excluded red: {category}; {r['region']['pixel_count']} pixels, solidity {r['shape']['solidity']:.3f}";triplet(im,old,[r],[x-38,y-38,x+39,y+39],file,title,5);examples.append(dict(id=r['id'],category=category,image=file,area=r['region']['pixel_count'],supported_area=r['supported_region']['pixel_count'],solidity=r['shape']['solidity'],supported_solidity=shape(mask_local(r['supported_region']))['solidity'],context_open=r['interior_attempts'][-1]['context_open'],stops=r['interior_attempts'][-1]['stops']))
 save('red-failure-audit.json',dict(selected=name,summary=summary,examples=examples,note='Post-detection diagnosis. Shape threshold counts are upper bounds before renewed ownership/overlap checks; no acceptance changes.'))
 print(json.dumps(summary),flush=True)
if __name__=='__main__':main()
