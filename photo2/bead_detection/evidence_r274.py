"""Paired native mask accounting and saved hue-versus-brightness path evidence."""
import json,csv
from collections import Counter
import numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage as ndi
from matplotlib.colors import rgb_to_hsv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .experiment_r274 import ROOT,OUT,save,lines
from .review_r274 import load
from .brightness_r270 import linearize
from .inventory_r272 import hue_distance
from .interiors_r273 import pixels
from .annular_detect import straight_pixels
from .review_coverage_r272 import marked

def main():
 name=json.loads((OUT/'selection.json').read_text())['method'];old=load('r273');rows=load(name);lookup={r['id']:r for r in rows};oldmap={r['id']:r for r in old};accepted=[r for r in rows if r['accepted']];im=Image.open(ROOT/'photo2/review/r272/photo-srgb.png');rgb=np.asarray(im);hs=rgb_to_hsv(rgb/255.);lum=linearize(rgb/255.)@np.array([.2126,.7152,.0722]);mean3=ndi.uniform_filter(lum,3);pairs=[];summary={}
 for c in ('red','yellow','black'):
  a=[r for r in rows if r['color']==c];common=[r for r in a if r['accepted'] and oldmap[r['id']]['accepted']];changed=[r for r in common if pixels(r)!=pixels(oldmap[r['id']])];summary[c]=dict(old=sum(r['accepted'] for r in old if r['color']==c),new=sum(r['accepted'] for r in a),retained=len(common),changed=len(changed),unchanged=len(common)-len(changed),added=sum(r['accepted'] and not oldmap[r['id']]['accepted'] for r in a),interior_withheld=sum(not r['accepted'] and oldmap[r['id']]['accepted'] for r in a),median_paired_area_ratio=float(np.median([r['region']['pixel_count']/oldmap[r['id']]['region']['pixel_count'] for r in common])) if common else None)
 for r in rows:
  oldr=oldmap[r['id']];a=pixels(oldr) if 'region' in oldr else set();b=pixels(r) if 'region' in r else set();pairs.append(dict(id=r['id'],color=r['color'],old_accepted=oldr['accepted'],new_accepted=r['accepted'],location_status=r['location_status'],old_pixels=len(a),new_pixels=len(b),removed_pixels=len(a-b),added_pixels=len(b-a),reasons='; '.join(r['explanations'])))
 with (OUT/'paired-interiors.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(pairs[0]),lineterminator='\n');w.writeheader();w.writerows(pairs)
 save('paired-summary.json',summary);traces=[];cases=json.loads((OUT/'contact-cases.json').read_text())
 for i,c in enumerate(cases,1):
  r=lookup[c['id']];trace=c['rules'][name]['trace']
  if not trace:continue
  start=r['source_location'];xy=(start['x'],start['y']);oldtrace=next(d for d in oldmap[r['id']]['direction_stops'] if d['target']==trace['target']);route=straight_pixels(xy,tuple(trace['target']));stop=route.index(tuple(trace['trigger']));end=max(stop,route.index(tuple(oldtrace['trigger'])));route=route[:end+1];steps=[];minimum=float(mean3[xy[1],xy[0]]);peak=float(lum[xy[1],xy[0]])
  for j,(x,y) in enumerate(route):
   value=float(mean3[y,x]);steps.append(dict(step=j,x=x,y=y,hue=float(hs[y,x,0]*360),saturation=float(hs[y,x,1]),value=float(hs[y,x,2]),luminance=float(lum[y,x]),mean3=value,seed_hue_distance=float(hue_distance(hs[y,x,0]*360,r['seed_hue'])),old_floor_pass=bool(lum[y,x]>=max(.008,.035*peak)),old_valley_trigger=bool(minimum<.6*peak and value>minimum+max(.003,.25*minimum))));minimum=min(minimum,value)
  entry=dict(id=r['id'],color=r['color'],old_trace=oldtrace,new_trace=trace,new_stop_step=stop,steps=steps);traces.append(entry)
  fig,axes=plt.subplots(2,1,figsize=(6,4),sharex=True,layout='constrained');axes[0].plot([z['step'] for z in steps],[(z['hue']-r['seed_hue']+180)%360-180 for z in steps]);axes[0].set_ylabel('Hue drift (degrees)');axes[1].plot([z['step'] for z in steps],[z['luminance'] for z in steps],label='Native Y');axes[1].plot([z['step'] for z in steps],[z['mean3'] for z in steps],label='3 x 3 mean Y');axes[1].set_ylabel('ICC luminance');axes[1].set_xlabel('Native path step');axes[1].legend()
  for ax in axes:ax.axvline(stop,color='teal',linestyle='--');ax.grid(alpha=.2)
  fig.suptitle(c['id']+': '+trace['reason']);fig.savefig(OUT/f'path-{i}.png',dpi=140);plt.close(fig)
 lines('review-paths.jsonl.gz',traces);save('review-stops.json',[dict(id=t['id'],color=t['color'],old_reason=t['old_trace']['reason'],new_reason=t['new_trace']['reason'],at_stop=t['steps'][t['new_stop_step']]) for t in traces])
 # Same simple photo crops as the prior review, plus region size examples.
 from .review_r274 import panel
 for label,box in [('R00956',[2233,1863,2314,1944]),('R01284',[941,2640,1022,2721])]:panel(im,[r for r in old if r['accepted']],accepted,box,label+'.png',label,scale=4)
 for color in ('red','yellow','black'):
  a=sorted([r for r in accepted if r['color']==color],key=lambda r:(r['region']['pixel_count'],r['id']))
  for label,r in [('smallest',a[0]),('median',a[len(a)//2]),('largest',a[-1])]:
   x,y=r['anchor'];panel(im,[r for r in old if r['accepted']],accepted,[x-35,y-35,x+36,y+36],f'{color}-{label}.png',f'{color} {label}',scale=4)
 # All trusted locations, including those without accepted regions, are cyan dots.
 overview=marked(im,accepted,[0,0,im.width,im.height],1);d=ImageDraw.Draw(overview)
 for l in json.loads((OUT/(name+'-locations.json')).read_text()):
  x,y=l['point']['x'],l['point']['y'];d.ellipse((x-1,y-1,x+1,y+1),fill='cyan')
 overview.resize((1016,1273),Image.Resampling.LANCZOS).save(OUT/'whole-photo.png');print(summary,flush=True)
if __name__=='__main__':main()
