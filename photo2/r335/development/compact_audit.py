"""Bounded intensity-only check of reflection extent; no pattern inputs."""
from photo2.r334.common import read,ROOT
import numpy as np
from PIL import Image,ImageOps
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
import json
photo=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'))/255.
g=read(ROOT/'photo2/r334/overlay/graph.json.gz');obs={x['id']:x for x in g['observations']};names=sorted(obs);tree=cKDTree([obs[o]['xy'] for o in names]);rgb=photo;I=rgb@np.array([.299,.587,.114]);audit=read(ROOT/'photo2/r334/classification/audit.json.gz');result=[]
for row in audit['records']:
 o=row['id'];cx,cy=row['xy'];x,y=np.rint([cx,cy]).astype(int);tests=[]
 for radius in [9,12,15]:
  x0=max(0,x-radius);y0=max(0,y-radius);p=rgb[y0:y+radius+1,x0:x+radius+1];gray=I[y0:y+radius+1,x0:x+radius+1];yy,xx=np.indices(gray.shape);xx+=x0;yy+=y0;dx=xx-cx;dy=yy-cy;domain=dx*dx+dy*dy<=radius*radius
  for j in tree.query_ball_point([cx,cy],2*radius+6):
   q=obs[names[j]]['xy']
   if names[j]==o or np.linalg.norm(np.array(q)-[cx,cy])<8:continue
   domain&=(dx*dx+dy*dy<.86*((xx-q[0])**2+(yy-q[1])**2))
  central=domain&(dx*dx+dy*dy<=10**2);maxi=np.max(gray[central]);base=np.quantile(gray[domain],.2);threshold=base+.7*(maxi-base);regions,num=ndi.label(domain&(gray>=threshold));peak=np.unravel_index(np.where(central,gray,-1).argmax(),gray.shape);reflection=regions==regions[peak] if regions[peak] else np.zeros_like(domain);reflection=ndi.binary_dilation(reflection,iterations=1)&domain
  allbright=ndi.binary_dilation(domain&(gray>=threshold),iterations=1)&domain
  ring=ndi.binary_dilation(reflection,iterations=4)&~ndi.binary_dilation(reflection,iterations=1)&domain&~allbright
  sy,sx=np.where(reflection);ry,rx=np.where(ring);pixels=p[ring];value=pixels.max(1) if len(pixels) else np.array([]);v=gray[ring]
  sectors=len(set(((np.arctan2(ry-sy.mean(),rx-sx.mean())+np.pi)/(2*np.pi)*8).astype(int).clip(0,7))) if len(pixels) else 0
  valid=len(v)>=25 and sectors>=4 and maxi-base>=.08
  positive=bool(valid and np.median(v)<=.15 and np.quantile(v,.75)<=.20 and np.median(value)<=.30 and np.quantile(value,.75)<=.40 and np.mean(value<=.35)>=.70 and np.median(v)/max(row['lighting']['intensity'],.1)<=.65)
  negative=bool(valid and (np.median(value)>=.45 or np.mean(value<=.35)<=.30))
  tests.append(dict(radius=radius,count=len(v),sectors=sectors,positive=positive,negative=negative,med=float(np.median(v)) if len(v) else None,q75=float(np.quantile(v,.75)) if len(v) else None,maxmed=float(np.median(value)) if len(v) else None,spec=len(sx),peak=float(maxi),base=float(base)))
 pos=sum(t['positive'] for t in tests);neg=sum(t['negative'] for t in tests);dec='black' if pos>=2 and neg==0 else 'not-black' if neg>=2 and pos==0 else 'unknown';result.append(dict(id=o,status=row['status'],color=row['overlay_color'],old=row['body_prediction'],new=dec,tests=tests,maker=row['maker_reviewed']))
from collections import Counter
print('decisions',Counter((r['color'],r['new']) for r in result if r['status']=='recorded'))
for r in result:
 if (r['color']=='red' and (r['old']=='black' or r['new']=='black')) or r['maker']:print(r['id'],r['color'],r['old'],r['new'],r['maker'])
(ROOT/'photo2/r335/development/compact-audit.json').write_text(json.dumps(result))
