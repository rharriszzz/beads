"""Paired global controls for implemented red-region remedies."""
import json,gzip
from collections import Counter
from PIL import Image
from .experiment_r273 import ROOT,OUT,save
from .review_r273 import triplet

def load(name):return [json.loads(l) for l in gzip.open(OUT/(name+'-candidates.jsonl.gz'),'rt')]
def main():
 im=Image.open(ROOT/'photo2/review/r272/photo-srgb.png');before=load('relative-valley-safe');after=load('remedy-shape');old={r['id']:r for r in before if r['accepted']};new={r['id']:r for r in after if r['accepted']};gained=[r for r in after if r['accepted'] and r['id'] not in old];lost=[r for r in before if r['accepted'] and r['id'] not in new];examples=[]
 reds=sorted([r for r in gained if r['color']=='red'],key=lambda r:(r['anchor'][1],r['anchor'][0]))
 for i,fraction in enumerate((.05,.23,.41,.59,.77,.95),1):
  r=reds[min(len(reds)-1,int(len(reds)*fraction))];x,y=r['anchor'];file=f'red-remedy-addition-{i}.png';triplet(im,list(old.values()),list(new.values()),[x-38,y-38,x+39,y+39],file,f"Red remedy addition: {r['id']}",5,labels=('Original photograph','Before remedies','With remedies'));examples.append(dict(id=r['id'],file=file))
 bg=load('remedy-background');background_new=[r for r in bg if r['accepted'] and r['id'] not in old]
 for i,r in enumerate(background_new,1):
  x,y=r['anchor'];file=f'background-remedy-addition-{i}.png';triplet(im,list(old.values()),[z for z in bg if z['accepted']],[x-38,y-38,x+39,y+39],file,'Supported continuation through uncertain background',5,labels=('Original photograph','Before remedy','Background remedy'))
 save('red-remedies-comparison.json',dict(before=dict(Counter(r['color'] for r in old.values())),after=dict(Counter(r['color'] for r in new.values())),gained=dict(Counter(r['color'] for r in gained)),lost=dict(Counter(r['color'] for r in lost)),gained_ids=[r['id'] for r in gained],lost_ids=[r['id'] for r in lost],examples=examples,background_addition_ids=[r['id'] for r in background_new],retained_uncertain_pixels=sum(r.get('background_continuation',{}).get('retained_uncertain_pixels',0) for r in new.values()),retained_regions_with_uncertain_pixels=sum(r.get('background_continuation',{}).get('retained_uncertain_pixels',0)>0 for r in new.values())))
if __name__=='__main__':main()
