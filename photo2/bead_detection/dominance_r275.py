"""Suppress strongly dominated close highlights using photographic bridge evidence.
Applies uniformly in the fixed target band; retains complete suppressed records.
"""
import json,sys
from copy import deepcopy
import numpy as np
from scipy.spatial import cKDTree
from matplotlib.colors import rgb_to_hsv
from PIL import Image,ImageOps
from .centerline_r275 import ROOT,OUT,Band,save
from .brightness_r270 import color_managed_photo,linearize,encode
from .climb_r268 import background
from .inventory_r272 import hue_distance
from .interiors_r273 import pixels
from .annular_detect import straight_pixels

def suppress(data,native,srgb,band):
 data=deepcopy(data);records={r['id']:r for r in data['beads']};locations={r['id']:r for r in data['locations']};hs=rgb_to_hsv(srgb/255.);nhs,paper,_=background(native);lum=linearize(srgb/255.)@np.array([.2126,.7152,.0722]);selected=[l for l in data['locations'] if l['id'] in records and band.qualifies([l['point']['x'],l['point']['y']],records[l['id']]['region'])['in_band']];xy=np.array([[l['point']['x'],l['point']['y']] for l in selected]);decisions=[];removed=set()
 pairs=sorted(cKDTree(xy).query_pairs(16)) if len(xy)>1 else []
 for i,j in pairs:
  a,b=[records[selected[k]['id']] for k in (i,j)]
  if a['color']!=b['color']:continue
  strong,weak=sorted((a,b),key=lambda r:(-r['brightest']['luminance'],r['id']));s=strong['brightest'];w=weak['brightest'];ratio=w['luminance']/s['luminance'];area_ratio=weak['region']['pixel_count']/strong['region']['pixel_count'];path=straight_pixels((s['x'],s['y']),(w['x'],w['y']));inside=pixels(strong)|pixels(weak);bridge=[(x,y) for x,y in path if (x,y) not in inside];evidence=[]
  for x,y in path:evidence.append(dict(x=int(x),y=int(y),luminance=float(lum[y,x]),hue=float(hs[y,x,0]*360),saturation=float(hs[y,x,1]),paper=int(paper[y,x])))
  contrast_ratio=None
  if strong['color']=='black':
   contrast_ratio=weak['confidence']['peak_shell_value_contrast']/strong['confidence']['peak_shell_value_contrast'];clear=bool(bridge and all(paper[y,x]==0 and encode(lum[y,x])<=.40 and (nhs[y,x,1]<=.55 or nhs[y,x,1]*nhs[y,x,2]<=.14) for x,y in bridge));dominant=ratio<=.35 and contrast_ratio<=.65
  else:
   hue=strong['color_evidence']['hue'];clear=bool(bridge and all(paper[y,x]==0 and lum[y,x]>=.25*w['luminance'] for x,y in bridge) and all(hs[y,x,1]<.35 or hue_distance(hs[y,x,0]*360,hue)<=18 for x,y in path));dominant=ratio<=.35 and area_ratio<=.20
  fragment=bool(strong['color']!='black' and dominant and weak['region']['pixel_count']<30 and locations[weak['id']].get('source')=='R275 automatic band recovery');accept=bool(dominant and (clear or fragment) and strong['id'] not in removed);reason=('strong peak and continuous material bridge' if clear else 'new tiny colored fragment beside a much stronger same-color interior; independent bead/color ownership unreliable') if accept else 'insufficient dominance or bridge evidence';decision=dict(strong=strong['id'],weak=weak['id'],color=strong['color'],peak_ratio=ratio,area_ratio=area_ratio,contrast_ratio=contrast_ratio,clear_bridge=clear,suppress=accept,classification=('secondary reflection' if clear else 'uncertain colored fragment'),reason=reason,path=evidence);decisions.append(decision)
  if accept:removed.add(weak['id'])
 data['suppressed_locations']=data.get('suppressed_locations',[])+[dict(**l,suppression_status='duplicate removed') for l in data['locations'] if l['id'] in removed];data['suppressed_beads']=data.get('suppressed_beads',[])+[r for r in data['beads'] if r['id'] in removed];data['beads']=[r for r in data['beads'] if r['id'] not in removed];data['locations']=[r for r in data['locations'] if r['id'] not in removed]
 for i,l in enumerate(data['locations'],1):
  l['prior_inventory_number']=l.get('prior_inventory_number',l['inventory_number']);l['inventory_number']=i
  if l['id'] in records:records[l['id']]['inventory_number']=i
 data['dominance_decisions']=data.get('dominance_decisions',[])+decisions;return data,decisions

def main():
 path=OUT/'before-dominance-inventory.json'
 if not path.exists() or '--refresh' in sys.argv:path.write_bytes((OUT/'inventory.json').read_bytes())
 old=json.loads(path.read_text());native=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));srgb,_=color_managed_photo();data,dec=suppress(old,native,srgb,Band());save('inventory.json',data);save('dominance.json',dec);print([(r['weak'],r['strong'],r['suppress'],r['clear_bridge']) for r in dec])
if __name__=='__main__':main()
