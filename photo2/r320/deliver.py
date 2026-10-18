"""Small photographic review and independently reproducible selected exports."""
from copy import deepcopy
import time,html
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from photo2.r297.common import ROOT,read,save,sha,utc
from photo2.r306.evidence import load
from photo2.r318.optics import Engine as OldEngine,Chain as OldChain
from photo2.r297.geometry import periodic_field
from photo2.r315.model import bump
from .model import Chain,parameters,corrected,D
from .evaluate import Evidence,evaluate,errors
from .audit import verify_scene
OUT=ROOT/'photo2/r320/results'
def draw(label,result,xy,boundary):
 photo=Image.open(ROOT/'beads-photo-2.jpg').convert('RGB');obs=np.array([r['observed'] for r in result['rows']]);lo=np.floor(obs.min(0)-35).astype(int);hi=np.ceil(obs.max(0)+35).astype(int)
 im=photo.crop(tuple(np.r_[lo,hi]));pix=np.asarray(im).copy();points=np.asarray(xy)[boundary].astype(int)-lo
 good=(points[:,0]>=0)&(points[:,1]>=0)&(points[:,0]<im.width)&(points[:,1]<im.height);points=points[good];pix[points[:,1],points[:,0]]=[0,220,230];im=Image.fromarray(pix);d=ImageDraw.Draw(im)
 for row in result['rows']:
  x,y=np.array(row['observed'])-lo;d.ellipse((x-3,y-3,x+3,y+3),outline=(255,230,0),width=1)
  if row['predicted'] is not None:
   a,b=np.array(row['predicted'])-lo;d.line((x,y,a,b),fill=(255,255,255),width=1);d.line((a-3,b,a+3,b),fill=(255,80,200),width=1);d.line((a,b-3,a,b+3),fill=(255,80,200),width=1)
  else:d.line((x-5,y-5,x+5,y+5),fill='red',width=2)
 im.resize((im.width*2,im.height*2)).save(OUT/f'{label}-overlay.png')
 photo.crop(tuple(np.r_[lo,hi])).resize((im.width*2,im.height*2)).save(OUT/'original-crop.png')
 return [int(v) for v in np.r_[lo,hi]]
def main():
 start=time.perf_counter();data=load()[0];ev=Evidence(data)
 rows=[]
 for folder in ['optical-trials','coupled-trials']:
  for f in sorted((OUT/folder).glob('*.gz')):
   r=read(f);r['source']=str(f.relative_to(ROOT));rows.append(r)
 good=[r for r in rows if r.get('optical',{}).get('emax_px') is not None]
 strict=[r for r in good if r['packing']['eligible']]
 winner=min(strict,key=lambda r:r['optical']['emax_px'])
 corrected_rows=[r for r in strict if r['kind']=='centerline-bilateral']
 center=min(corrected_rows,key=lambda r:r['optical']['emax_px']) if corrected_rows else winner
 third=min([r for r in strict if r['family'][0]==2600],key=lambda r:r['optical']['emax_px'])
 selected=[('derived-best',winner),('centerline-control',center),('derived-2600',third)]
 # Full original R319 baseline, same exact 22-point localization and old map.
 pold=read(ROOT/'photo2/r319/results/best-full.json.gz')['parameters'];old,so,arr=OldEngine(ev.epoch).evaluate(pold,True);old['geometry']=ev.local.measure(so);old['parameters']=pold;old['summary']=dict(count=so.n,winding_nominal=round(so.n/6.5),circumference_ratio=so.length/(round(so.n/6.5)*1.4*so.radius*so.axial),diameter_photo_px=2*so.radius*so.scale,topology='open',interpretation='Nominal winding diagnostic only; historical model remains open')
 save(OUT/'R319-baseline.json.gz',old)
 geo,visible=ev.local.measure(so,detail=True);draw('R319',old,visible['xy'],visible['boundary'].ravel())
 verifications=[];models=[]
 for label,r in selected:
  p=r['parameters'];ep=read(OUT/f'epoch-N{p["count"]}-h{p["hand"]}.json.gz')
  o,cache,sh=evaluate(p,data,ev,'pilot',ev.obs,ep['mapping'],keep=True);s=cache['s'];pred={int(k):v for k,v in o['predictions'].items()}
  control=errors(ev.obs,ev.epoch['mapping'],pred)
  save(OUT/f'{label}-assignment-control.json',dict(same_geometry=True,new_map=o['emax_px'],historical_map=control,geometric_gain=False))
  export=dict(source=r['source'],parameters=p,summary=s.summary(),optical=o,positions=dict(indices=s.indices.tolist(),centers=s.centers.tolist(),frames={k:v.tolist() for k,v in s.g.items()},projected=s.pc.tolist()))
  save(OUT/f'{label}-model.json.gz',export);np.savez_compressed(OUT/f'{label}-raster.npz',xy=cache['xy'],owner=cache['tr']['owner'],boundary=cache['boundary'],intensity=sh['intensity'])
  draw(label,o,cache['xy'],cache['boundary']);v=verify_scene(p,data,label);verifications.append(v);models.append(dict(label=label,source=r['source'],summary=s.summary(),emax=o['emax_px'],geometry=o['geometry'],parameters=p))
 # Record inherited totals, not merely small increments.
 k=np.linspace(-pold['count']/2,pold['count']/2,20001);phase=periodic_field(pold['local_phase'],k/pold['count'])
 phase+=sum(a*bump(k,c,pold['phase_halfwidth']) for a,c in zip(pold['compact_phase'],pold['compact_centers']))
 station=so.station(k);uniform=pold['s0']/so.scale+k*so.extent/so.n
 rate=np.gradient(station,k)/(so.extent/so.n)-1
 inherited=dict(axis_max_px=float(np.max(abs(periodic_field(pold['axis_nodes'],np.linspace(0,1,4097))))),phase_max_deg=float(np.degrees(abs(phase).max())),station_max_departure_px=float(np.max(abs(station-uniform))*so.scale),local_spacing_rate_max_percent=float(abs(rate).max()*100),registration_translation_px=pold['translation'],registration_station_px=pold['s0'],interpretation='Totals relative to uniform placement with same open extent, prior to R320 reset. These fields are all removed in the new model; centerline only gets explicit two-harmonic departures.')
 save(OUT/'inherited-corrections.json',inherited)
 save(OUT/'verification.json',dict(models=verifications,photo_sha256=sha(ROOT/'beads-photo-2.jpg'),beads_pov_sha256=sha(ROOT/'beads.pov'),elapsed_seconds=time.perf_counter()-start,utc=utc()))
 save(OUT/'delivery-summary.json',dict(models=models,R319=dict(emax=old['emax_px'],geometry=old['geometry'],summary=old['summary']),inherited=inherited,trial_counts={k:len(list((OUT/k).glob('*.gz'))) for k in ['physical-trials','optical-trials','coupled-trials']},no_adoption=True))
 print('DELIVERED',[(m['label'],m['emax'],m['summary']['circumference_ratio'],m['summary']['axis_correction_px']) for m in models],flush=True)
if __name__=='__main__':main()
