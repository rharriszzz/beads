"""Automatic contact-case selection and original-photo boundary evidence."""
import json,gzip
from collections import Counter
import numpy as np
from PIL import Image,ImageDraw
from matplotlib.colors import rgb_to_hsv
from .experiment_r274 import ROOT,OUT,save,lines
from .hue_r274 import palette_from,color_surface
from .interiors_r273 import pixels
from .inventory_r272 import hue_distance
from .brightness_r270 import linearize
from .review_coverage_r272 import marked

def load(name):return [json.loads(l) for l in gzip.open(OUT/(name+'-candidates.jsonl.gz'),'rt')]
def panel(im,old,new,box,name,title,evidence=None,scale=5,locations=()):
 w=(box[2]-box[0])*scale;h=(box[3]-box[1])*scale;sheet=Image.new('RGB',(4*w+30,h+46),'white');draw=ImageDraw.Draw(sheet);ims=[im.crop(box).resize((w,h),Image.Resampling.NEAREST),marked(im,old,box,scale),marked(im,new,box,scale),im.crop(box).resize((w,h),Image.Resampling.NEAREST)]
 for loc in locations:
  if loc['interior_status']!='accepted':
   x,y=loc['point']['x'],loc['point']['y']
   if box[0]<=x<box[2] and box[1]<=y<box[3]:
    d=ImageDraw.Draw(ims[2]);cx=(x-box[0]+.5)*scale;cy=(y-box[1]+.5)*scale;d.ellipse((cx-2,cy-2,cx+2,cy+2),fill='cyan')
 if evidence:
  d=ImageDraw.Draw(ims[3]);pts=evidence.get('opponent_pixels',[])
  for x,y in pts:
   if box[0]<=x<box[2] and box[1]<=y<box[3]:d.rectangle([(x-box[0])*scale,(y-box[1])*scale,(x-box[0]+1)*scale-1,(y-box[1]+1)*scale-1],outline='#ffb000',width=1)
  trace=evidence.get('trace')
  if trace:
   start=evidence['start'];end=trace['trigger'];d.line([(start[0]-box[0]+.5)*scale,(start[1]-box[1]+.5)*scale,(end[0]-box[0]+.5)*scale,(end[1]-box[1]+.5)*scale],fill='cyan',width=2);x,y=end;d.ellipse([(x-box[0])*scale-3,(y-box[1])*scale-3,(x-box[0])*scale+3,(y-box[1])*scale+3],fill='white')
 draw.text((5,3),title,fill='black')
 for i,(label,photo) in enumerate(zip(('Original photograph','R273','Hue rule','Color evidence'),ims)):sheet.paste(photo,(i*(w+10),46));draw.text((i*(w+10)+5,26),label,fill='black')
 sheet.save(OUT/name)

def main():
 im=Image.open(ROOT/'photo2/review/r272/photo-srgb.png');rgb=np.asarray(im);hsv=rgb_to_hsv(rgb/255.);lum=linearize(rgb/255.)@np.array([.2126,.7152,.0722]);old=load('r273');base=[r for r in old if r['accepted']];palette=json.loads((OUT/'summary.json').read_text())['variants']['r273']['palette'];surface=color_surface(hsv);candidates=[];sources=json.loads((ROOT/'photo2/review/r272-coverage/inventory.json').read_text())['beads']
 for r in base:
  if r['color']=='black':continue
  own=palette[r['color']];rival=palette['yellow' if r['color']=='red' else 'red'];pts=pixels(r);wrong=[(x,y) for x,y in pts if hsv[y,x,1]>=.30 and hsv[y,x,1]*hsv[y,x,2]>=.08 and hue_distance(hsv[y,x,0]*360,rival)+4<hue_distance(hsv[y,x,0]*360,own)];rays=[d for d in r.get('direction_stops',[]) if d['reason'] in ('first-valley','color-boundary','brightness-floor')]
  near=[z for z in sources if z['color'] not in (r['color'],'black') and np.linalg.norm(np.array(z['anchor'])-r['anchor'])<45];contact=[pt for pt in wrong if any(np.linalg.norm(np.array(z['anchor'])-pt)<18 for z in near)]
  candidates.append(dict(contact_count=len(contact),other_locations=[z['id'] for z in near],id=r['id'],color=r['color'],opponent_pixels=wrong,opponent_count=len(wrong),old_area=len(pts),anchor=r['anchor']))
 chosen=[]
 for color in ('yellow','red'):
  ranked=sorted([r for r in candidates if r['color']==color],key=lambda r:(-r['contact_count'],-r['opponent_count'],r['id']))
  for r in ranked:
   if r['opponent_count']==0:continue
   if any(np.linalg.norm(np.array(r['anchor'])-z['anchor'])<100 for z in chosen):continue
   chosen.append(r)
   if sum(z['color']==color for z in chosen)==3:break
 save('contact-ranking.json',candidates);save('contact-cases.json',chosen)
 for method in ('seed-hue18','palette','contrast','seed-palette','local-contrast','path-contrast','highlight-palette'):
  rows=load(method);lookup={r['id']:r for r in rows};accepted=[r for r in rows if r['accepted']]
  for i,c in enumerate(chosen,1):
   r=lookup[c['id']];x,y=c['anchor'];box=[x-37,y-37,x+38,y+38];directions=[d for d in r.get('direction_stops',[]) if 'hue' in d['reason']]
   if directions:
    target=np.mean(c['opponent_pixels'],axis=0);trace=min(directions,key=lambda d:np.linalg.norm(np.array(d['trigger'])-target))
   else:trace=None
   c.setdefault('rules',{})[method]=dict(accepted=r['accepted'],area=r.get('region',{}).get('pixel_count',0),reasons=r['reasons'],stops=r.get('stops'),trace=trace)
   origin=r.get('source_location',r.get('brightest'));evidence=dict(opponent_pixels=c['opponent_pixels'],trace=trace,start=[origin['x'],origin['y']]);panel(im,base,accepted,box,f'{c["color"]}-{i}-{method}.png',f'{c["color"]} contact / {method}',evidence,locations=json.loads((OUT/(method+'-locations.json')).read_text()))
 save('contact-cases.json',chosen)
 print([(r['id'],r['color'],r['opponent_count']) for r in chosen],flush=True)
if __name__=='__main__':main()
