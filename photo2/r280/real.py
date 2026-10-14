"""A5: fresh local hypotheses from frozen image-only observations; no old poses."""
import copy
import numpy as np
from scipy.optimize import linear_sum_assignment
from PIL import Image,ImageOps
from .common import OUT,ROOT,read,save,sha
from .geometry import R,INDICES,SURFACE,centers,project,trace,templates,certify
from .detector import infer,prepare

def pixels(bead):return np.array([(x,y) for y,a,b in bead['region']['runs'] for x in range(a,b+1)])
def anchors(data):
 by={b['id']:b for b in data['beads']};points=np.array([[l['point']['x'],l['point']['y']] for l in data['locations']]);pool=[]
 for j,l in enumerate(data['locations']):
  b=by.get(l['id'])
  if not b or l['color'] not in ('red','yellow') or b['region']['pixel_count']<100 or l['point']['luminance']<.25:continue
  delta=points-points[j];near=delta[np.linalg.norm(delta,axis=1)<100]
  if len(near)<12:continue
  _,v=np.linalg.eigh(np.cov(near.T));axis=v[:,-1];normal=v[:,0];cross=near@normal
  if abs(np.median(cross))>np.std(cross)*.40:continue
  pool.append(dict(id=l['id'],point=points[j].tolist(),roll=float(np.degrees(np.arctan2(axis[1],axis[0]))),area=b['region']['pixel_count']))
 pool.sort(key=lambda r:(-r['area'],r['id']));selected=[]
 while pool and len(selected)<6:
  row=max(pool,key=lambda r:min(np.linalg.norm(np.array(r['point'])-q['point']) for q in selected)) if selected else pool[0]
  selected.append(row);pool.remove(row)
 return selected

def fit(anchor,observations,origin):
 by={r['id']:r for r in observations};a=by[anchor['id']];acent=np.array(a['centroid']);scale0=np.sqrt(a['area']/(np.pi*R*R*.65));scale0=float(np.clip(scale0,4.,10.))
 samples=[]
 for o in observations[:7]:
  xy=np.array(o['pixels']);samples.append(xy[np.linspace(0,len(xy)-1,min(24,len(xy))).astype(int)])
 xy=np.concatenate(samples);candidates=[]
 for hand in (-1,1):
  for inclination in (-30.,0.,30.):
   for phase in np.linspace(-np.pi,np.pi,12,endpoint=False):
    for scale in (scale0*.85,scale0*1.10):
     p=dict(hand=hand,inclination=inclination,phase=float(phase),pitch=1.12,roll=anchor['roll'],scale=scale,translation=[0.,0.])
     surface=project(p,SURFACE+centers([0],hand,phase,1.12)[0]);own,_,unknown=trace(p,surface);seen=surface[(own==0)&~unknown]
     if len(seen)<20:continue
     # Visible-surface centroid initialization, explicitly uncertain interior bias.
     p['translation']=(acent-seen.mean(0)).tolist();owner,_,unknown=trace(p,xy)
     matrix=[];start=0
     for sample in samples:
      values=owner[start:start+len(sample)];matrix.append([np.mean(values==k) for k in INDICES]);start+=len(sample)
     matrix=np.array(matrix);anchor_support=float(matrix[0,14]);other=matrix[1:].copy();other[:,14]=0
     ii,jj=linear_sum_assignment(-other);score=float((anchor_support+other[ii,jj].sum())/len(matrix))
     candidates.append(dict(parameters=p,score=score,anchor_support=anchor_support,positive_observation_assignments=[dict(observation=observations[0]['id'],model_index=0,support=anchor_support)]+[dict(observation=observations[i+1]['id'],model_index=int(INDICES[j]),support=float(other[i,j])) for i,j in zip(ii,jj)],fit_scope='Only frozen Phase1 interiors. No manual identities; model-index zero arbitrary; centroid initialization is not a physical-center measurement.'))
 candidates.sort(key=lambda r:-r['score']);chosen=[]
 for hand in (-1,1):
  pool=[r for r in candidates if r['parameters']['hand']==hand and r['anchor_support']>=.5]
  if pool:chosen.append(pool[0])
 return candidates,chosen

def main():
 frozen=read(OUT/'freeze.json');path=ROOT/'photo2/review/r278/phase1-inventory.json.gz';data=read(path);by={b['id']:b for b in data['beads']};selected=anchors(data)
 root=OUT/'real';root.mkdir(exist_ok=True);save(root/'selected-anchors.json',dict(phase1_sha256=sha(path),anchors=selected,selection='Largest reliable colored interior then spatial farthest sampling; centrality from local photographic PCA only. No historical centerline.'))
 image=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');allpoints=np.array([[l['point']['x'],l['point']['y']] for l in data['locations']])
 for i,a in enumerate(selected):
  folder=root/f'region-{i:02}';folder.mkdir(exist_ok=True);c=np.array(a['point']);lo=np.maximum(0,np.floor(c-100).astype(int));hi=np.minimum(image.size,lo+200);rgb=np.asarray(image.crop((*lo,*hi)));Image.fromarray(rgb).save(folder/'photo.png')
  order=np.argsort(np.linalg.norm(allpoints-c,axis=1));obs=[]
  for j in order:
   l=data['locations'][j];b=by.get(l['id'])
   if not b or np.linalg.norm(allpoints[j]-c)>85:continue
   px=pixels(b)-lo;inside=(px[:,0]>=0)&(px[:,1]>=0)&(px[:,0]<rgb.shape[1])&(px[:,1]<rgb.shape[0]);px=px[inside]
   if len(px)<20:continue
   obs.append(dict(id=l['id'],point=(allpoints[j]-lo).tolist(),centroid=px.mean(0).tolist(),area=len(px),pixels=px.tolist(),color=l['color']))
  # Ensure selected anchor is the first fit observation.
  obs.sort(key=lambda o:(o['id']!=a['id'],np.linalg.norm(np.array(o['point'])-(c-lo))))
  alternatives,chosen=fit(a,obs,lo);save(folder/'initializations.json.gz',dict(anchor=a,crop_origin=lo.tolist(),phase1=obs,all_candidates=alternatives))
  state=prepare(rgb)
  for h,best in enumerate(chosen):
   p=best['parameters'];pred,audit=templates(p,rgb.shape[:2]);cert=certify(p)
   for q in pred:q['uncertainty_px']=.10*q['diameter']
   result=dict(parameters=p,fit=best,certificate=cert,predictions=pred,phase1=obs,methods={m:infer(rgb,pred,m,frozen['thresholds'],obs,state) for m in 'ABC'},target_families=[-7,-6,-1,1,6,7],status='Conditional photographic evidence; no independent physical identity truth; both hands retained.')
   save(folder/f'model-{h}.json.gz',result)
  print('A5',i,'candidates',len(alternatives),'retained',len(chosen),flush=True)
if __name__=='__main__':main()
