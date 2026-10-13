"""Focused image-only recovery; frozen successful inventory is additive baseline.
The reference band selects work only. No centerline direction, spacing, or bead count
enters peak finding, color, growth, or ownership. All competing peaks are retained.
"""
from copy import deepcopy
from dataclasses import asdict,replace
from collections import Counter
import json,time
import numpy as np
from PIL import Image,ImageOps
from scipy import ndimage as ndi
from matplotlib.colors import rgb_to_hsv
from .centerline_r275 import ROOT,OUT,Band,SCAN_REACH,save,write_rows
from .brightness_r270 import color_managed_photo,linearize
from .climb_r268 import background
from .inventory_r272 import features,hue_distance,circular_mean,component,measure,CROSS,learn_palette
from .coverage_r272 import Parameters,black_region,colored_region,complete,maxima_rows
from .hue_r274 import grow,color_surface,palette_from,SELECTED
from .interiors_r273 import pixels,shape
from .annular_detect import straight_pixels

class Recovery:
 def __init__(self,native,srgb,base,band,pale=False,homogeneous=False):
  self.native=native;self.srgb=srgb;self.band=band;self.base=base;self.pale=pale;self.homogeneous=homogeneous
  self.hsv=rgb_to_hsv(srgb/255.);self.lum=linearize(srgb/255.)@np.array([.2126,.7152,.0722])
  self.nhsv,self.paper,self.background_model=background(native);self.mean3=ndi.uniform_filter(self.lum,3)
  self.surface=color_surface(self.hsv);self.palette=palette_from(base)
  if not self.palette:
   fs=[features(self.hsv,self.lum,self.paper,x,y) for y in range(11,self.lum.shape[0]-11,4) for x in range(11,self.lum.shape[1]-11,4) if self.paper[y,x]==0 and self.hsv[y,x,1]>=.35]
   self.palette={p['name']:p['hue'] for p in learn_palette(fs) if p['name'] is not None}
 def classify(self,x,y,expanded=False):
  f=features(self.hsv,self.lum,self.paper,x,y)
  if expanded:
   hs=self.hsv[y-6:y+7,x-6:x+7];l=self.lum[y-6:y+7,x-6:x+7];pp=self.paper[y-6:y+7,x-6:x+7];yy,xx=np.mgrid[-6:7,-6:7]
   good=(hs[:,:,1]>=.35)&(hs[:,:,1]*hs[:,:,2]>=.06)&(l>=.025)&(pp==0)&(xx*xx+yy*yy<=36)
   angles=hs[:,:,0][good]*360;h=circular_mean(angles) if len(angles) else None
   f.update(color_samples=len(angles),hue=h,hue_deviation90=float(np.percentile(hue_distance(angles,h),90)) if h is not None else None)
  ds=sorted((float(hue_distance(f['hue'],h)),c) for c,h in self.palette.items()) if f['hue'] is not None else []
  pale_ok=False
  if self.pale and expanded and ds and f['hue_deviation90'] is not None:
   hs=self.hsv[y-8:y+9,x-8:x+9];l=self.lum[y-8:y+9,x-8:x+9];pp=self.paper[y-8:y+9,x-8:x+9];yy,xx=np.mgrid[-8:9,-8:9];ring=(xx*xx+yy*yy>=16)&(xx*xx+yy*yy<=64);sector=np.floor((np.arctan2(yy,xx)+np.pi)*4/np.pi).astype(int)%8
   support=(hs[:,:,1]>=.35)&(hue_distance(hs[:,:,0]*360,f['hue'])<=16)&(l>=.04)&(pp==0);votes=[float(support[ring&(sector==k)].mean()) for k in range(8)]
   pale_ok=bool(f['color_samples']>=35 and f['hue_deviation90']<=12 and np.mean(support[ring])>=.70 and min(votes)>=.50 and np.median(l[ring])>=.07)
   f['pale_highlight_evidence']=dict(accepted=pale_ok,sector_fractions=votes,ring_fraction=float(support[ring].mean()),ring_median_luminance=float(np.median(l[ring])))
  margin=4 if self.homogeneous and f['color_samples']>=50 and f['colored_core_fraction']>=.80 and f['hue_deviation90'] is not None and f['hue_deviation90']<=10 else 6
  f['required_prototype_margin']=margin
  ok=bool(ds and ds[0][0]<=(20 if expanded else 16) and (len(ds)<2 or ds[1][0]-ds[0][0]>=margin) and f['color_samples']>=10 and f['hue_deviation90']<=(25 if expanded else 22) and (f['colored_core_fraction']>=(.25 if expanded else .4) or pale_ok))
  return (ds[0][1] if ok else None),dict(**f,prototype={'name':ds[0][1],'hue':self.palette[ds[0][1]]} if ds else None,distances=ds)
 def new_colored(self,anchor,prefix,expanded):
  x,y=map(int,anchor);rec=dict(id=f'{prefix}-{x:04d}-{y:04d}',anchor=[x,y],pathway='colored',accepted=False,reasons=[],confidence={})
  color,ev=self.classify(x,y,expanded);rec.update(color=color,color_evidence=ev)
  if color is None:rec['reasons']=['color-uncertain'];return rec
  m=float(ndi.uniform_filter(self.lum[y-12:y+13,x-12:x+13],7)[12,12]);l=self.lum[y-12:y+13,x-12:x+13];yy,xx=np.mgrid[-12:13,-12:13];ann=(xx*xx+yy*yy>=64)&(xx*xx+yy*yy<=144);contrast=(m-float(np.median(l[ann])))/max(m,1e-10)
  rec['confidence'].update(mean7_y=m,local_contrast=contrast)
  if m<(.025 if expanded else .04):rec['reasons'].append('dim')
  if contrast<(.08 if expanded else .12):rec['reasons'].append('contrast')
  if self.paper[y-1:y+2,x-1:x+2].any():rec['reasons'].append('background')
  if rec['reasons']:return rec
  colored_region(rec,self.native,self.srgb,self.hsv,self.lum,self.paper,Parameters(),ev['hue'])
  return rec
 def interior(self,rec,layered=False):
  """Prefer R274 broad support; retain a smaller measured color-consistent fallback."""
  if not rec.get('region') or not rec.get('brightest'):return deepcopy(rec)
  new=grow(rec,self.native,self.srgb,self.hsv,self.lum,self.mean3,self.paper,self.surface,self.palette,SELECTED)
  new['r274_attempt']=dict(reasons=new['reasons'].copy(),pixels=new.get('region',{}).get('pixel_count',0))
  if new['accepted']:new['recovery_method']='r274-broad';return new
  if layered and new.get('supported_region'):
   box=new['supported_region']['bbox'];x0,y0,x1,y1=box;support=np.zeros((y1-y0,x1-x0),bool)
   for yy,a,b in new['supported_region']['runs']:support[yy-y0,a-x0:b-x0+1]=True
   seed=(rec['brightest']['x']-x0,rec['brightest']['y']-y0);l=self.lum[y0:y1,x0:x1];peak=rec['brightest']['luminance'];attempts=[]
   from skimage.morphology import disk
   for fraction in (.10,.20,.30,.40,.50,.60):
    before=component(support&(l>=max(.008,peak*fraction)),seed)
    eroded=ndi.binary_erosion(ndi.binary_opening(before,structure=disk(1)),CROSS,iterations=2)
    stable=(rec['anchor'][0]-x0,rec['anchor'][1]-y0);inside=lambda p:0<=p[0]<eroded.shape[1] and 0<=p[1]<eroded.shape[0] and eroded[p[1],p[0]]
    interior_seed=seed if inside(seed) else stable
    clean=component(eroded,interior_seed) if inside(interior_seed) else np.zeros_like(eroded)
    ok=bool(before.sum()<=870 and clean.sum()>=25 and not np.any(ndi.binary_fill_holes(clean)&~clean) and shape(clean)['solidity']>=.85)
    # Reject any level whose support touches the original radius32 context.
    sx,sy=rec['brightest']['x'],rec['brightest']['y'];ys,xs=np.where(before)
    if len(xs) and max(np.max(abs(xs+x0-sx)),np.max(abs(ys+y0-sy)))>=32:ok=False
    attempts.append(dict(fraction=fraction,precleanup=int(before.sum()),pixels=int(clean.sum()),accepted=ok))
    if ok:
     result=deepcopy(new);result['reasons']=[];complete(result,clean,(x0,y0),self.native,self.srgb,self.hsv,self.lum);result['recovery_method']='hue-path-layered-fallback';result['layer_attempts']=attempts;result['interior_seed']=[int(interior_seed[0]+x0),int(interior_seed[1]+y0)];result['warnings'].append('Larger interior failed; selected largest tested bounded brightness layer inside R274 hue/path support.');return result
  original=deepcopy(rec);original['r274_attempt']=new['r274_attempt'];original['recovery_method']='hue-consistent-small-fallback'
  # Recheck every fallback pixel with the R274 local-versus-rival hue test.
  box=rec['region']['bbox'];x0,y0,x1,y1=box;mask=np.zeros((y1-y0,x1-x0),bool)
  for yy,a,b in rec['region']['runs']:mask[yy-y0,a-x0:b-x0+1]=True
  hs=self.hsv[y0:y1,x0:x1];own=rec['color_evidence']['hue'];rival=self.palette.get('red' if rec['color']=='yellow' else 'yellow');reliable=(hs[:,:,1]>=.35)&(hs[:,:,1]*hs[:,:,2]>=.055)
  support=mask if rival is None else mask&(~reliable|(hue_distance(hs[:,:,0]*360,rival)-hue_distance(hs[:,:,0]*360,own)>=2))
  seed=(rec['brightest']['x']-x0,rec['brightest']['y']-y0);clean=component(support,seed);original['reasons']=[]
  if clean.sum()<12:original['reasons'].append('fallback-small')
  if np.any(ndi.binary_fill_holes(clean)&~clean):original['reasons'].append('fallback-holes')
  if shape(clean)['solidity']<.78:original['reasons'].append('fallback-irregular')
  if clean.any():complete(original,clean,(x0,y0),self.native,self.srgb,self.hsv,self.lum)
  else:original['accepted']=False
  original.setdefault('warnings',[]).append('Larger R274 interior uncertain; smaller hue-consistent measured support retained separately.')
  return original
 def peaks(self,windows=(5,7,9),black=False):
  results=[]
  for n in ((1,) if black else windows):
   score=self.lum if n==1 else ndi.uniform_filter(self.lum,n)
   rows,_=maxima_rows(score,'K' if black else f'M{n}')
   xy=np.array([r['anchor'] for r in rows]);distance=self.band.distance(xy)
   for r,d in zip(rows,distance):
    x,y=r['anchor']
    if d<=SCAN_REACH and min(x,y,score.shape[1]-1-x,score.shape[0]-1-y)>=33:
     r['centerline_distance']=float(d);r['window']=n;r['score']=float(score[y,x]);results.append(r)
  return results

def resolve(proposals,old,band):
 """Never silently invalidate a previous success; defer conflicting new supports."""
 regions=deepcopy(old['beads']);locations=deepcopy(old['locations']);owner={};byid={r['id']:r for r in regions};locmap={r['id']:r for r in locations};decisions=[]
 for r in regions:
  for p in pixels(r):owner[p]=r['id']
 eligible=sorted(proposals,key=lambda r:(-r.get('brightest',{}).get('luminance',0),r['id']))
 for source in eligible:
  r=deepcopy(source);status='still unresolved';r['status']=status
  if not r.get('accepted'):
   if 'same-color-connected-secondary-patch' in r['reasons']:r['status']='duplicate removed'
   decisions.append(r);continue
  pt=[r['brightest']['x'],r['brightest']['y']];r['band']=band.qualifies(pt,r['region'])
  if not r['band']['in_band']:r['accepted']=False;r['status']='outside target';decisions.append(r);continue
  alias=[]
  for prior in old.get('superseded_beads',[]):
   current=locmap.get(prior['id'])
   if current is None or current['color']!='black' or r.get('color')=='black':continue
   pp=prior['brightest'];same_fragment=np.linalg.norm(np.array(pt)-[pp['x'],pp['y']])<=4
   if same_fragment and r['brightest']['luminance']<=.35*current['point']['luminance']:alias.append(prior['id'])
  for prior in old.get('suppressed_beads',[]):
   pp=prior['brightest']
   if prior['color']!=r.get('color') or np.linalg.norm(np.array(pt)-[pp['x'],pp['y']])>4:continue
   winners=[d['strong'] for d in old.get('dominance_decisions',[]) if d['weak']==prior['id'] and d['suppress']]
   if any(id in locmap and r['brightest']['luminance']<=.35*locmap[id]['point']['luminance'] for id in winners):alias.append(prior['id'])
  if alias:
   r.update(accepted=False,status='duplicate removed',competing_ids=alias);r['reasons'].append('superseded-colored-reflection-alias' if any(p['id'] in alias for p in old.get('superseded_beads',[])) else 'suppressed-secondary-reflection-alias');decisions.append(r);continue
  pts=pixels(r);overlap={owner[p] for p in pts if p in owner and owner[p]!=r['id']};same=[]
  for l in locations:
   if l['id']==r['id']:continue
   distance=np.linalg.norm(np.array(pt)-[l['point']['x'],l['point']['y']]);m=byid.get(l['id']);inside=m is not None and tuple(pt) in pixels(m)
   if l['color']==r['color'] and (distance<=1.5 or inside):same.append(l['id'])
  if same:
   r.update(accepted=False,status='duplicate removed',competing_ids=same);r['reasons'].append('same-peak-or-contained-highlight');decisions.append(r);continue
  close=[l['id'] for l in locations if l['id']!=r['id'] and np.hypot(pt[0]-l['point']['x'],pt[1]-l['point']['y'])<(12 if r['color']=='black' else 7)]
  if overlap or close:
   r.update(accepted=False,status='still unresolved',competing_ids=sorted(overlap|set(close)));r['reasons'].append('ownership-conflict');decisions.append(r);continue
  if r['id'] in byid:r.update(accepted=False,status='previous support preserved');decisions.append(r);continue
  if r['id'] in locmap:
   l=locmap[r['id']];r['status']='corrected interior';l['interior_status']='accepted'
  else:
   r['status']='recovered missing candidate';l=dict(id=r['id'],color=r['color'],inventory_number=len(locations)+1,point=deepcopy(r['brightest']),bright_patch=deepcopy(r['bright_patch']),interior_status='accepted',reasons=[],explanations=[],source='R275 automatic band recovery',location_confidence=r.get('confidence',{}));locations.append(l);locmap[l['id']]=l
  r['inventory_number']=l['inventory_number'];r['interior_status']='accepted';r['location_status']='trusted';r['explanations']=[];r['acceptance_reasons']=['Image-derived color or enclosed black reflection; native measured support.','No overlap or unresolved nearby conflict with retained inventory.','Centerline only selects this candidate for recovery.'];regions.append(r);byid[r['id']]=r
  for p in pts:owner[p]=r['id']
  decisions.append(r)
 return regions,locations,decisions

def main():
 start=time.time();old=json.loads((ROOT/'photo2/review/r274/inventory.json').read_text());base=json.loads((ROOT/'photo2/review/r272-coverage/inventory.json').read_text())['beads'];band=Band();native=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));srgb,profile=color_managed_photo();engine=Recovery(native,srgb,base,band);frozen={r['id'] for r in old['beads']};fallback=[]
 for b in base:
  pt=[b['brightest']['x'],b['brightest']['y']]
  if b['id'] in frozen or b['color']=='black' or not band.qualifies(pt,b['region'])['in_band']:continue
  fallback.append(engine.interior(b))
 print('fallback',len(fallback),flush=True);summaries={};allmethods={}
 peaks=engine.peaks();raw=engine.peaks(black=True);write_rows('all-band-maxima.jsonl.gz',peaks+raw);print('peaks',len(peaks),len(raw),flush=True)
 methods={'fallback':fallback}
 for name,expanded in [('multi-window',False),('expanded-color-black',True),('layered-fallback',True)]:
  rows=deepcopy(fallback)
  for i,r in enumerate(peaks):
   candidate=engine.new_colored(r['anchor'],('E' if expanded else 'S')+str(r['window']),expanded);candidate['source_maximum']=r
   if candidate.get('accepted') or (name=='layered-fallback' and candidate.get('region')):candidate=engine.interior(candidate,layered=name=='layered-fallback');candidate['source_maximum']=r
   rows.append(candidate)
   if i%500==0:print(name,i,flush=True)
  if expanded:
   for r in raw:
    rec=dict(id='N-'+r['id'],anchor=r['anchor'],accepted=False,reasons=[],confidence={},source_maximum=r)
    black_region(rec,native,srgb,engine.hsv,engine.nhsv,engine.lum,engine.paper,replace(Parameters(),black_peak_value=.18,black_contrast=.10));rows.append(rec)
  methods[name]=rows
 for name,rows in methods.items():
  beads,locations,decisions=resolve(rows,old,band);write_rows(name+'-decisions.jsonl.gz',decisions)
  summary=dict(interiors=len(beads),locations=len(locations),colors=dict(Counter(r['color'] for r in beads)),statuses=dict(Counter(r['status'] for r in decisions)),new_colors=dict(Counter(r['color'] for r in decisions if r['accepted'])),reasons=dict(Counter(k for r in decisions for k in r['reasons'])))
  summaries[name]=summary;print(name,summary,flush=True)
  if name=='layered-fallback':
   compact=[{k:v for k,v in r.items() if k not in ('direction_stops','supported_region','r272_measurements')} for r in beads];data=deepcopy(old);data.update(schema='r275-reference-band-v1',beads=compact,locations=locations);save('inventory.json',data)
 save('methods.json',dict(methods=summaries,elapsed_seconds=time.time()-start,profile=profile,selected='layered-fallback',palette=engine.palette));print('elapsed',time.time()-start,flush=True)
if __name__=='__main__':main()
