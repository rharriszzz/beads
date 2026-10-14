"""Photographic inference API. No benchmark/truth/evaluation/file I/O imports.

infer(rgb, predictions, method, thresholds, phase1=()) -> per-hypothesis evidence.
Predicted visible/silhouette runs are MODEL rasterizations, not observed masks.
Photographic locations are supported-interior centroids, never physical centers.
"""
import numpy as np
from scipy import ndimage as ndi
from skimage.color import rgb2hsv
from skimage.segmentation import watershed
from .common import runs,mask_from_runs

DEFAULT=dict(strong=.65,partial=.40,min_pixels=8,strong_min_pixels=40,boundary=.40,foreground=.55,conflict=.25)

def prepare(rgb):
 a=np.asarray(rgb,float)/255.;hsv=rgb2hsv(a);lum=a@np.array([.2126,.7152,.0722]);chroma=a/np.maximum(a.sum(2,keepdims=True),.06)
 border=np.concatenate([chroma[:6].reshape(-1,3),chroma[-6:].reshape(-1,3),chroma[:,:6].reshape(-1,3),chroma[:,-6:].reshape(-1,3)])
 bg=np.median(border,axis=0);dist=np.linalg.norm(chroma-bg,axis=2)
 # Illumination changes alone do not make paper bead material.
 chromatic=(dist>.13)&(hsv[:,:,1]>.24)&(lum>.025)
 neutral=(hsv[:,:,1]<.25)&(lum<.16)&(np.linalg.norm(bg-1/3)>.06)
 positive=chromatic|neutral
 paper=(dist<.045)&(lum>.04)
 gradient=np.sqrt(sum(ndi.sobel(a[:,:,c],axis=ax,mode='nearest')**2 for c in range(3) for ax in (0,1)))/4
 edge=ndi.maximum_filter(gradient,3)>.07
 smooth=ndi.gaussian_filter(lum,1)
 peaks=(smooth==ndi.maximum_filter(smooth,7))&positive&(smooth>.045)
 markers,n=ndi.label(peaks);labels=watershed(-smooth,markers,mask=positive)
 observations=[]
 for k,sl in enumerate(ndi.find_objects(labels),1):
  if sl is None:continue
  yy,xx=np.where(labels[sl]==k);xx+=sl[1].start;yy+=sl[0].start
  if len(xx)<8:continue
  best=int(np.argmax(lum[yy,xx]));observations.append(dict(x=xx,y=yy,peak=np.array([xx[best],yy[best]]),score=float(min(1.,.40+.30*min(1,len(xx)/120)+.30*min(1,lum[yy,xx].max()/.5)))))
 return dict(rgb=a,hsv=hsv,lum=lum,positive=positive,paper=paper,gradient=gradient,edge=edge,observations=observations,background_chroma=bg.tolist())

def transform(mask,center,shift=(0,0),scale=1.,angle=0.):
 a=np.radians(angle);rot=np.array([[np.cos(a),-np.sin(a)],[np.sin(a),np.cos(a)]])/scale
 # scipy acts on y,x; desired forward x,y rotation is converted here.
 matrix=rot[[1,0]][:,[1,0]];c=np.array(center)[::-1];delta=np.array(shift)[::-1]
 return ndi.affine_transform(mask.astype(np.uint8),matrix,offset=c-matrix@(c+delta),order=0,output_shape=mask.shape,mode='constant')>0

def _color(state,support):
 h,s,v=state['hsv'][support].T if support.any() else (np.array([]),)*3
 if len(h)<8:return 'unknown'
 chrom=(s>.40)&(v>.12)
 if chrom.mean()>.55:
  z=np.mean(np.exp(2j*np.pi*h[chrom]));hue=np.angle(z)/2/np.pi%1
  if abs(z)<.92:return 'unknown'
  if min(hue,1-hue)<.07:return 'red'
  if .08<hue<.20:return 'yellow'
 if np.mean((s<.3)&(v<.28))>.65:return 'black'
 return 'unknown'

def _record(p,state,support,score,metrics,registration,alternatives):
 yy,xx=np.where(support);xy=np.c_[xx,yy];loc=xy.mean(0) if len(xy) else None
 # Conservative engineering radius; coverage evaluated, no confidence claim.
 uncertainty=None if loc is None else float(max(2.,.25*p['diameter'],p.get('uncertainty_px',0.)))
 return dict(id=p['id'],method=None,score=float(score),status=None,positive_pixels=len(xy),support=runs(support),location=loc.tolist() if loc is not None else None,location_kind='photographic supported-interior centroid',physical_center=None,uncertainty_radius_px=uncertainty,color=_color(state,support),metrics=metrics,registration=registration,registration_alternatives=alternatives,competing_ids=[],phase1_overlap_ids=[])

def measure(state,p,method):
 shape=state['lum'].shape;vis=mask_from_runs(p['visible'],shape);diam=p['diameter'];u=p.get('uncertainty_px',0.)
 if method=='A':
  pool=[o for o in state['observations'] if np.linalg.norm(o['peak']-p['center'])<=diam*.6+u]
  if not pool:return _record(p,state,np.zeros(shape,bool),0.,dict(boundary=0.,foreground=0.,paper=0.),{},[])
  o=max(pool,key=lambda o:o['score']-.25*np.linalg.norm(o['peak']-p['center'])/(diam+u))
  support=np.zeros(shape,bool);yy,xx=o['y'],o['x'];keep=np.linalg.norm(np.c_[xx,yy]-p['center'],axis=1)<=diam*.6+u;support[yy[keep],xx[keep]]=True
  return _record(p,state,support,o['score'],dict(boundary=1.,foreground=1.,paper=0.),dict(feature_peak=o['peak'].tolist()),[])
 if vis.sum()<8:return _record(p,state,np.zeros(shape,bool),0.,dict(boundary=0.,foreground=0.,paper=0.),{},[])
 # Evaluate sparse pixel coordinates, not a full raster per translation.
 base=vis;variants=[(1.,0.,base)]
 su=p.get('scale_uncertainty',0.);au=p.get('angle_uncertainty_deg',0.)
 if su:variants += [(s,0.,transform(vis,p['center'],scale=s)) for s in (1-su,1+su)]
 elif au:variants += [(1.,a,transform(vis,p['center'],angle=a)) for a in (-au,au)]
 offsets=[(0.,0.)] if u<.5 else [(dx,dy) for dx in np.linspace(-u,u,5) for dy in np.linspace(-u,u,5) if dx*dx+dy*dy<=u*u*1.01]
 candidates=[]
 for scale,angle,v in variants:
  interior=ndi.binary_erosion(v);boundary=v&~interior
  iy,ix=np.where(interior);by,bx=np.where(boundary)
  for dx,dy in offsets:
   xx=ix+int(round(dx));yy=iy+int(round(dy));ok=(xx>=0)&(xx<shape[1])&(yy>=0)&(yy<shape[0]);xx=xx[ok];yy=yy[ok]
   ex=bx+int(round(dx));ey=by+int(round(dy));ok=(ex>=0)&(ex<shape[1])&(ey>=0)&(ey<shape[0]);ex=ex[ok];ey=ey[ok]
   if len(xx)<8 or len(ex)<4:continue
   fg=float(state['positive'][yy,xx].mean());paper=float(state['paper'][yy,xx].mean());edge=float(state['edge'][ey,ex].mean())
   score=.45*fg+.55*edge-.35*paper
   candidates.append(dict(score=float(score),foreground=fg,paper=paper,boundary=edge,dx=float(dx),dy=float(dy),scale=float(scale),angle=float(angle),x=xx,y=yy))
 if not candidates:return _record(p,state,np.zeros(shape,bool),0.,dict(boundary=0.,foreground=0.,paper=0.),{},[])
 candidates.sort(key=lambda c:(-c['score'],c['dx']**2+c['dy']**2));best=candidates[0]
 support=np.zeros(shape,bool);yy,xx=best['y'],best['x'];good=state['positive'][yy,xx];support[yy[good],xx[good]]=True
 alts=[{k:v for k,v in c.items() if k not in ('x','y')} for c in candidates[:5]]
 return _record(p,state,support,best['score'],{k:best[k] for k in ('foreground','paper','boundary')},{k:best[k] for k in ('dx','dy','scale','angle')},alts)

def classify(r,thresholds=None):
 t={**DEFAULT,**(thresholds or {})}
 if r['positive_pixels']<t['min_pixels']:
  r['status']='contradicted' if r['metrics']['paper']>.75 else 'insufficient';return r
 if r['competing_ids']:r['status']='ambiguous';return r
 if r['positive_pixels']>=t['strong_min_pixels'] and r['score']>=t['strong'] and r['metrics']['boundary']>=t['boundary'] and r['metrics']['foreground']>=t['foreground']:r['status']='strong'
 elif r['score']>=t['partial']:r['status']='partial'
 elif r['metrics']['paper']>.75:r['status']='contradicted'
 else:r['status']='insufficient'
 return r

def infer(rgb,predictions,method='C',thresholds=None,phase1=(),state=None):
 if method not in ('A','B','C'):raise ValueError(method)
 ids=[p['id'] for p in predictions]
 if len(ids)!=len(set(ids)):raise ValueError('Hypothesis IDs must be distinct')
 state=prepare(rgb) if state is None else state;t={**DEFAULT,**(thresholds or {})}
 results=[measure(state,p,method) for p in predictions]
 if method=='C':
  masks=[mask_from_runs(r['support'],state['lum'].shape) for r in results]
  for i,a in enumerate(results):
   if a['positive_pixels']<8:continue
   for j in range(i):
    b=results[j]
    if b['positive_pixels']<8:continue
    overlap=int((masks[i]&masks[j]).sum())/min(a['positive_pixels'],b['positive_pixels'])
    if overlap>t['conflict']:
     a['competing_ids'].append(b['id']);b['competing_ids'].append(a['id'])
 for r in results:
  r['method']=method
  # Phase1 is immutable and advisory. Overlap means comparison, not a new bead.
  support=mask_from_runs(r['support'],state['lum'].shape)
  for o in phase1:
   x,y=np.rint(o['point']).astype(int)
   if 0<=y<support.shape[0] and 0<=x<support.shape[1] and support[y,x]:r['phase1_overlap_ids'].append(o['id'])
  classify(r,t)
 return results
