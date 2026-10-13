"""Correct weak colored fragments dominated by a neutral, enclosed main reflection.
All previous coordinates/masks survive as explicit superseded measurements.
"""
import json,sys
from copy import deepcopy
import numpy as np
from PIL import Image,ImageOps
from .centerline_r275 import ROOT,OUT,Band,save,load_rows
from .brightness_r270 import color_managed_photo,linearize,encode
from .climb_r268 import background
from .interiors_r273 import pixels
from .annular_detect import straight_pixels

def correct(data,candidates,native,srgb,band):
 out=deepcopy(data);_,paper,_=background(native);lum=linearize(srgb/255.)@np.array([.2126,.7152,.0722]);changes=[];out.setdefault('superseded_locations',[]);out.setdefault('superseded_beads',[])
 for candidate in sorted(candidates,key=lambda r:-r.get('brightest',{}).get('luminance',0)):
  if candidate.get('color')!='black' or candidate.get('reasons')!=['ownership-conflict'] or not candidate.get('region'):continue
  peak=candidate['brightest'];c=candidate['confidence'];point=np.array([peak['x'],peak['y']]);
  if peak['hsv_srgb']['s']>.25 or c.get('chromatic_core_fraction',1)>.10 or c.get('peak_shell_value_contrast',0)<.25 or not candidate.get('dark_perimeter',{}).get('closed'):continue
  if not band.qualifies(point,candidate['region'])['in_band']:continue
  archived={l['id']:l for l in out.get('suppressed_locations',[])};locs={l['id']:l for l in out['locations']}|archived;allbeads={r['id']:r for r in out['beads']}|{r['id']:r for r in out.get('suppressed_beads',[])};eligible=[]
  for id,l in locs.items():
   r=allbeads.get(id)
   if not r or r['color']=='black' or r['region']['pixel_count']>100 or r['confidence'].get('mean7_y',1)>.12:continue
   weak=r['brightest'];q=np.array([weak['x'],weak['y']]);distance=float(np.linalg.norm(q-point));ratio=weak['luminance']/peak['luminance']
   if distance>16 or ratio>.35:continue
   route=straight_pixels(tuple(point),tuple(q));core=pixels(candidate)|pixels(r);bridge=[(x,y) for x,y in route if (x,y) not in core];clear=bool(bridge and all(paper[y,x]==0 and encode(lum[y,x])<=.50 for x,y in bridge))
   if clear:eligible.append((distance,id,ratio,route))
  if len(eligible)!=1:continue
  distance,id,ratio,route=eligible[0];others=[r for r in out['beads'] if r['id']!=id];owned=set().union(*(pixels(r) for r in others));points=np.array([[l['point']['x'],l['point']['y']] for l in out['locations'] if l['id']!=id]);conflict=bool(pixels(candidate)&owned or (len(points) and np.linalg.norm(points-point,axis=1).min()<12))
  if conflict:continue
  old=allbeads[id];oldloc=locs[id];new=deepcopy(candidate);new.update(id=id,accepted=True,reasons=[],explanations=[],inventory_number=oldloc['inventory_number'],source_candidate_id=candidate['id'],recovery_method='dominant-neutral-reflection-color-correction',interior_status='accepted',location_status='trusted');new['warnings'].append('Prior weak colored fragment superseded by a much brighter neutral reflection with closed dark surround.');location=deepcopy(oldloc);location.update(color='black',point=deepcopy(peak),bright_patch=deepcopy(new['bright_patch']),interior_status='accepted',reasons=[],explanations=[],source='R275 corrected color and reflection location',location_confidence=c)
  out['superseded_locations'].append(deepcopy(oldloc));out['superseded_beads'].append(deepcopy(old));out['beads']=[r for r in out['beads'] if r['id']!=id]+[new];out['locations']=[l for l in out['locations'] if l['id']!=id]+[location];out['suppressed_locations']=[l for l in out.get('suppressed_locations',[]) if l['id']!=id];out['suppressed_beads']=[r for r in out.get('suppressed_beads',[]) if r['id']!=id];changes.append(dict(id=id,old_color=old['color'],new_color='black',old_point=oldloc['point'],new_point=peak,peak_ratio=ratio,distance=distance,source_candidate=candidate['id'],bridge=[dict(x=int(x),y=int(y),luminance=float(lum[y,x]),paper=int(paper[y,x])) for x,y in route],reason='Small dim colored fragment, much stronger neutral peak, closed dark shell and non-paper dark continuity; previous measurements retained.'))
 out['locations'].sort(key=lambda l:(l.get('prior_inventory_number',l['inventory_number']),l['id']));byid={r['id']:r for r in out['beads']}
 for i,l in enumerate(out['locations'],1):
  l.setdefault('prior_inventory_number',l['inventory_number']);l['inventory_number']=i
  if l['id'] in byid:byid[l['id']]['inventory_number']=i
 out['color_corrections']=changes;return out,changes

def main():
 path=OUT/'before-reclassify-inventory.json'
 if not path.exists() or '--refresh' in sys.argv:path.write_bytes((OUT/'inventory.json').read_bytes())
 old=json.loads(path.read_text());native=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));srgb,_=color_managed_photo();out,changes=correct(old,load_rows(OUT/'material-0.25-decisions.jsonl.gz'),native,srgb,Band());save('inventory.json',out);save('color-corrections.json',changes);print([(r['id'],r['old_color'],r['new_color']) for r in changes])
if __name__=='__main__':main()
