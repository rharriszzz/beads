"""Photographic selection only. No model, neighbor chart or R280 result inputs."""
import numpy as np
from PIL import Image,ImageOps,ImageDraw
from .common import OUT,ROOT,read,save,sha

def pixels(bead):return np.array([(x,y) for y,a,b in bead['region']['runs'] for x in range(a,b+1)])

def main():
 path=ROOT/'photo2/review/r278/phase1-inventory.json.gz';data=read(path);by={b['id']:b for b in data['beads']};observations=[]
 for l in data['locations']:
  b=by.get(l['id'])
  if b is None:continue
  p=pixels(b);confidence=l.get('location_confidence',{});quality=float(confidence.get('mean7_y',0))
  observations.append(dict(id=l['id'],color=l['color'],point=[l['point']['x'],l['point']['y']],centroid=p.mean(0).tolist(),pixels=p.tolist(),area=len(p),light=quality,peak=l['point']['luminance']))
 points=np.array([o['centroid'] for o in observations]);eligible=np.array([o['color'] in ('red','yellow') and o['area']>=80 and o['peak']>=.25 and o['light']>=.07 for o in observations]);candidates=[]
 for j,o in enumerate(observations):
  if not eligible[j]:continue
  delta=points-points[j];near=np.linalg.norm(delta,axis=1)<90
  if near.sum()<12:continue
  eig,vec=np.linalg.eigh(np.cov(points[near].T));axis=vec[:,-1]
  if axis[0]<0:axis=-axis
  normal=np.array([-axis[1],axis[0]]);center=np.median(points[near],axis=0);along=(points-center)@axis;cross=(points-center)@normal
  selected=np.where(eligible&(abs(along)<65)&(abs(cross)<18))[0]
  if not 6<=len(selected)<=12 or eig[-1]/max(1,eig[0])<3:continue
  train=[k for k in selected if along[k]<0]
  if len(train)<4:continue
  # Favor reliable illumination and a near-horizontal straight region so the
  # axis-aligned native crop shows a short section rather than a long diagonal.
  if abs(axis[1])>.6:continue
  quality=float(np.median([observations[k]['light'] for k in selected]))
  score=quality+.03*min(eig[-1]/eig[0],8)-.025*abs(len(selected)-9)
  candidates.append(dict(center=center.tolist(),axis=axis.tolist(),score=score,straightness=float(eig[-1]/eig[0]),work_ids=[observations[k]['id'] for k in selected],eligible_anchor_ids=[observations[k]['id'] for k in train],quality=quality))
 candidates.sort(key=lambda r:(-r['score'],r['center']));assert candidates,'No eligible photographic region'
 selected=candidates[0];center=np.array(selected['center']);origin=np.floor(center-[110,90]).astype(int);im=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');raw=im.crop((*origin,*(origin+[220,180])))
 folder=OUT/'real';folder.mkdir(parents=True,exist_ok=True);raw.save(folder/'raw.png');raw.resize((880,720),Image.Resampling.NEAREST).save(folder/'enlarged.png')
 local=[]
 for o in observations:
  point=np.array(o['point'])-origin
  if not (0<=point[0]<220 and 0<=point[1]<180):continue
  item={**o,'point':point.tolist(),'centroid':(np.array(o['centroid'])-origin).tolist(),'pixels':(np.array(o['pixels'])-origin).tolist()};local.append(item)
 bylocal={o['id']:o for o in local};pool=[bylocal[k] for k in selected['eligible_anchor_ids'] if k in bylocal];pool.sort(key=lambda o:(-o['light']*np.sqrt(o['area']),o['id']));anchors=[pool.pop(0)]
 while len(anchors)<4:
  best=max(pool,key=lambda o:min(np.linalg.norm(np.array(o['centroid'])-a['centroid']) for a in anchors));anchors.append(best);pool.remove(best)
 # Fit file contains ONLY four immutable photographic observations. Other
 # locations remain in an evaluator file that fit.py never opens.
 save(folder/'anchors.json',dict(origin=origin.tolist(),selection=selected,anchors=anchors,phase1_sha256=sha(path),photo_sha256=sha(ROOT/'beads-photo-2.jpg')))
 save(folder/'photo-evidence.json',dict(origin=origin.tolist(),observations=local,anchor_ids=[a['id'] for a in anchors],work_ids=selected['work_ids'],selection_candidates=candidates))
 draw=ImageDraw.Draw(raw)
 for o in local:
  x,y=o['point'];color='cyan' if o['id'] not in {a['id'] for a in anchors} else '#20ff40';draw.ellipse((x-2,y-2,x+2,y+2),outline=color,width=1)
 raw.resize((880,720),Image.Resampling.NEAREST).save(folder/'phase1.png');print('selected',origin.tolist(),'work',len(selected['work_ids']),'anchors',[a['id'] for a in anchors],flush=True)
if __name__=='__main__':main()
