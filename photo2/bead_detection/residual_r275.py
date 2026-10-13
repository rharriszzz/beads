"""Independent native chromatic-component census, not a physical bead denominator."""
import json
from collections import Counter
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from skimage.morphology import disk
from matplotlib.colors import rgb_to_hsv
from PIL import Image
from .centerline_r275 import ROOT,OUT,Band,save
from .brightness_r270 import linearize
from .climb_r268 import background
from .inventory_r272 import hue_distance,measure
from .review_r275 import panel,textfont

def main():
 data=json.loads((OUT/'inventory.json').read_text());im=Image.open(ROOT/'photo2/review/r272/photo-srgb.png');rgb=np.asarray(im);hs=rgb_to_hsv(rgb/255.);lum=linearize(rgb/255.)@np.array([.2126,.7152,.0722]);from PIL import ImageOps
 native=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));_,paper,_=background(native);palette=json.loads((OUT/'methods.json').read_text())['palette'];band=Band();rows=[]
 for color in ('red','yellow'):
  own=palette[color];other=palette['red' if color=='yellow' else 'yellow'];good=(hs[:,:,1]>=.35)&(lum>=.04)&(paper==0)&(hue_distance(hs[:,:,0]*360,own)<=22)&(hue_distance(hs[:,:,0]*360,other)-hue_distance(hs[:,:,0]*360,own)>=6);clean=ndi.binary_opening(good,structure=disk(1));labels,n=ndi.label(clean)
  for k,sl in enumerate(ndi.find_objects(labels),1):
   mask=labels[sl]==k
   if mask.sum()<40:continue
   origin=(sl[1].start,sl[0].start);ys,xs=np.where(mask);l=lum[sl];iy,ix=np.unravel_index(np.argmax(np.where(mask,l,-1)),mask.shape);pt=[int(ix+origin[0]),int(iy+origin[1])];region=measure(mask,origin);membership=band.qualifies(pt,region)
   if not membership['in_band']:continue
   tree=cKDTree(np.c_[xs+origin[0],ys+origin[1]]);associations=[]
   for loc in data['locations']:
    d=float(tree.query([loc['point']['x'],loc['point']['y']])[0])
    if d<=6:associations.append(dict(id=loc['id'],color=loc['color'],distance=d))
   rows.append(dict(id=f'CC-{color}-{pt[0]}-{pt[1]}',color=color,point=pt,region=region,band=membership,associations=associations,status='unrepresented chromatic component' if not associations else 'associated',note='A component may be part of one bead or several same-color touching beads; no bead identity is inferred.'))
 missing=sorted([r for r in rows if not r['associations']],key=lambda r:-r['region']['pixel_count']);save('independent-components.json',dict(records=rows,unrepresented=len(missing),associated=len(rows)-len(missing)))
 from PIL import ImageDraw
 for i,r in enumerate(missing,1):
  x,y=r['point'];box=[x-45,y-45,x+45,y+45];raw=im.crop(box).resize((360,360),Image.Resampling.NEAREST);marked=raw.copy();d=ImageDraw.Draw(marked)
  for yy,a,b in r['region']['runs']:
   if box[1]<=yy<box[3]:
    for xx in range(max(a,box[0]),min(b+1,box[2])):d.point(((xx-box[0])*4,(yy-box[1])*4),fill='cyan')
  sheet=Image.new('RGB',(730,390),'white');sheet.paste(raw,(0,30));sheet.paste(marked,(370,30));ImageDraw.Draw(sheet).text((5,5),f"Residual {i}: {r['color']}, {r['region']['pixel_count']} native chromatic pixels",fill='black',font=textfont());sheet.save(OUT/f'residual-{i:02d}.png');r['image']=f'residual-{i:02d}.png'
 save('residual-review.json',missing);print('components',len(rows),'unrepresented',len(missing),'areas',[r['region']['pixel_count'] for r in missing],flush=True)
if __name__=='__main__':main()
