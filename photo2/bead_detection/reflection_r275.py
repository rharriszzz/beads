"""Tighter native reflection core, with the same absolute dark-shell ceiling.
The frozen R272 routine is copied here only to expose its relative shell level.
No growth across the shell, added exterior pixels or review coordinates.
"""
import json,sys
from copy import deepcopy
from dataclasses import replace
from collections import Counter
import numpy as np
from scipy import ndimage as ndi
from PIL import Image,ImageOps
from .coverage_r272 import Parameters,complete
from .inventory_r272 import component,measure,hue_distance
from .brightness_r270 import encode,linearize,color_managed_photo
from .centerline_r275 import ROOT,OUT,Band,save,load_rows,write_rows
from .recover_r275 import Recovery,resolve

def reflection_region(rec,native,srgb,hsv,nhsv,lum,paper,p,fraction=.70,color_hues=None,tinted=False):
    x,y=rec['anchor'];r=p.context_radius;cut=np.s_[y-r:y+r+1,x-r:x+r+1];hs=nhsv[cut];l=lum[cut];pp=paper[cut]
    v=hs[:,:,2] if p.black_signal=='native-v' else encode(l)
    if p.black_sigma:v=ndi.gaussian_filter(v,p.black_sigma)
    peak=float(v[r,r]);level=min(p.black_maximum_value,fraction*peak)
    rec['color']='black';rec['dark_threshold_v']=level
    if hsv[y,x,1]>.55:rec['reasons'].append('black-color')
    if peak<p.black_peak_value:rec['reasons'].append('black-contrast')
    if paper[y,x]:rec['reasons'].append('background')
    if rec['reasons']:return
    # No blur, rays or skipped gaps: first 8-connected above-dark component.
    color_barrier=np.zeros(v.shape,bool)
    if color_hues:
        color_barrier=(hsv[cut][:,:,1]>=.60)&(np.minimum.reduce([hue_distance(hsv[cut][:,:,0]*360,h) for h in color_hues])<=16)
    labels,_=ndi.label((v>level)&~color_barrier,np.ones((3,3)));label=labels[r,r];core=labels==label if label else np.zeros_like(v,bool)
    shell=ndi.binary_dilation(core,np.ones((3,3)))&~core
    closed=bool(core.any() and not(core[0].any() or core[-1].any() or core[:,0].any() or core[:,-1].any()) and shell.any() and np.all((v[shell]<=level)|color_barrier[shell]) and np.mean(v[shell]<=level)>=.75)
    rec['dark_perimeter']=dict(closed=closed,kind='dark plus confident colored-material boundary' if color_hues else 'dark only',dark_fraction=float(np.mean(v[shell]<=level)) if shell.any() else 0.,core_pixels=int(core.sum()),runs=measure(shell,(x-r,y-r))['runs'],maximum_value=float(v[shell].max()) if shell.any() else None,signal=p.black_signal,sigma=p.black_sigma,threshold=level,linear_luminance_threshold=float(linearize(level)) if p.black_signal=='icc-gray' else None)
    if not closed or core.sum()>p.maximum_pixels:rec['reasons'].append('black-open');return
    neutral=(hs[:,:,1]<=.45)|(hs[:,:,1]*hs[:,:,2]<=.10)
    fraction=float(np.mean(neutral[shell]));contrast=peak-float(np.median(v[shell]));paper_fraction=float(np.mean(pp[core|shell]>0));colored_core=float(np.mean(hsv[cut][:,:,1][core]>.55))
    rec['confidence'].update(dark_neutral_shell_fraction=fraction,peak_shell_value_contrast=contrast,paper_fraction=paper_fraction,chromatic_core_fraction=colored_core)
    tint_ok=bool(tinted and color_hues and fraction>=.10 and colored_core<=.10 and hsv[y,x,1]<=.35 and contrast>=.25 and rec['dark_perimeter']['dark_fraction']>=.85)
    rec['confidence']['tinted_shell_exception']=tint_ok
    if (fraction<p.black_surround_fraction and not tint_ok) or colored_core>.25:rec['reasons'].append('black-material')
    if contrast<p.black_contrast:rec['reasons'].append('black-contrast')
    if paper_fraction:rec['reasons'].append('background')
    # Retain the reflection component, never add enclosing dark pixels or fill holes.
    mask=component(core,(r,r))
    if mask.sum()<p.minimum_black_pixels or mask.sum()>220 or np.any(ndi.binary_fill_holes(mask)&~mask):rec['reasons'].append('black-size')
    if mask.any():complete(rec,mask,(x-r,y-r),native,srgb,hsv,lum)
    rec['warnings']=['Reflection support only; not the whole black bead.','Dark material evidence is photographic, not a calibrated material probability.']

def main():
 path=OUT/'before-reflection-inventory.json'
 if not path.exists() or '--refresh' in sys.argv:path.write_bytes((OUT/'inventory.json').read_bytes())
 old=json.loads(path.read_text());base=json.loads((ROOT/'photo2/review/r272-coverage/inventory.json').read_text())['beads'];native=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));srgb,_=color_managed_photo();band=Band();e=Recovery(native,srgb,base,band);raw=[r for r in load_rows(OUT/'all-band-maxima.jsonl.gz') if r['window']==1];summary={}
 for fraction,mixed,tinted in ((.65,False,False),(.70,False,False),(.75,False,False),(.70,True,False),(.70,True,True)):
  rows=[]
  for p in raw:
   r=dict(id=f'RF{int(fraction*100)}'+('T-' if tinted else 'C-' if mixed else '-')+p['id'],anchor=p['anchor'],reasons=[],accepted=False,confidence={},source_maximum=p);reflection_region(r,native,srgb,e.hsv,e.nhsv,e.lum,e.paper,replace(Parameters(),black_maximum_value=.40,black_surround_fraction=.25),fraction,list(e.palette.values()) if mixed else None,tinted);rows.append(r)
  beads,loc,dec=resolve(rows,old,band);write_rows(f'reflection-{fraction:.2f}'+('-tinted' if tinted else '-color' if mixed else '')+'-decisions.jsonl.gz',dec);summary[str(fraction)+('-tinted' if tinted else '-color' if mixed else '')]=dict(interiors=len(beads),locations=len(loc),new_ids=[r['id'] for r in dec if r['accepted']],statuses=dict(Counter(r['status'] for r in dec)))
  if fraction==.70 and tinted:
   data=deepcopy(old);data.update(beads=beads,locations=loc);save('inventory.json',data)
 save('reflection-controls.json',dict(selected='0.7-tinted',controls=summary));print(summary)
if __name__=='__main__':main()
