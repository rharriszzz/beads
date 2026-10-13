"""Strong homogeneous body color can use a four-degree prototype margin."""
import json,sys
from copy import deepcopy
from collections import Counter
import numpy as np
from PIL import Image,ImageOps
from .centerline_r275 import ROOT,OUT,Band,save,load_rows,write_rows
from .recover_r275 import Recovery,resolve
from .core_r275 import core
from .brightness_r270 import color_managed_photo
from .interiors_r273 import pixels

def guard_ownership(result,old,engine):
 """Defer a weak second color patch connected to an existing brighter body."""
 from .annular_detect import straight_pixels
 from .inventory_r272 import hue_distance
 if not result.get('accepted'):return result
 p=result['brightest'];rivals=[]
 for l in old['locations']:
  q=l['point']
  if l['color']!=result['color'] or np.hypot(p['x']-q['x'],p['y']-q['y'])>16 or p['luminance']>.60*q['luminance']:continue
  path=straight_pixels((p['x'],p['y']),(q['x'],q['y']));hue=result['color_evidence']['hue']
  if all(engine.paper[y,x]==0 and engine.lum[y,x]>=.50*p['luminance'] and (engine.hsv[y,x,1]<.35 or hue_distance(engine.hsv[y,x,0]*360,hue)<=18) for x,y in path):rivals.append(l['id'])
 if rivals:result.update(accepted=False,competing_ids=rivals);result['reasons'].append('same-color-connected-secondary-patch')
 return result

def main():
 path=OUT/'before-homogeneous-inventory.json'
 if not path.exists() or '--refresh' in sys.argv:path.write_bytes((OUT/'inventory.json').read_bytes())
 old=json.loads(path.read_text());base=json.loads((ROOT/'photo2/review/r272-coverage/inventory.json').read_text())['beads'];native=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));srgb,_=color_managed_photo();band=Band();e=Recovery(native,srgb,base,band,pale=True,homogeneous=True);owned=set().union(*(pixels(r) for r in old['beads']));known=np.array([[l['point']['x'],l['point']['y']] for l in old['locations']]);rows=[]
 for p in load_rows(OUT/'all-band-maxima.jsonl.gz'):
  if p['window']==1 or p['score']<.08 or np.linalg.norm(known-p['anchor'],axis=1).min()<8:continue
  r=e.new_colored(p['anchor'],'H'+str(p['window']),True);r['source_maximum']=p
  if not r.get('region') or r['color_evidence']['required_prototype_margin']!=4:continue
  result=e.interior(r,layered=True)
  if not result.get('accepted'):result=core(e,r,owned)
  result['source_maximum']=p;rows.append(guard_ownership(result,old,e))
 beads,loc,dec=resolve(rows,old,band);write_rows('homogeneous-decisions.jsonl.gz',dec);data=deepcopy(old);data.update(beads=beads,locations=loc);save('inventory.json',data);summary=dict(interiors=len(beads),locations=len(loc),new=[r['id'] for r in dec if r['accepted']],statuses=dict(Counter(r['status'] for r in dec)));save('homogeneous-summary.json',summary);print(summary)
if __name__=='__main__':main()
