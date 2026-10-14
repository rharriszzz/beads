"""H1/H0 photographic comparison. No renderer, truth, file or fitted-model I/O."""
import numpy as np
from scipy import ndimage as ndi
from skimage.color import rgb2hsv
from photo2.r280.common import runs
from .geometry import warp

DEFAULT=dict(margin=.15,minimum_pixels=40,coverage=.65,coherence=.65,edge=.30,loss=.45)

def prepare(rgb):
 a=np.asarray(rgb,float)/255.;hsv=rgb2hsv(a);lum=a@np.array([.2126,.7152,.0722]);chroma=a/np.maximum(a.sum(2,keepdims=True),.03)
 good=(lum>.035)&~((hsv[:,:,1]<.20)&(hsv[:,:,2]>.50))
 gx=np.stack([ndi.sobel(a[:,:,k],axis=1)/4 for k in range(3)],2);gy=np.stack([ndi.sobel(a[:,:,k],axis=0)/4 for k in range(3)],2)
 strength=np.sqrt((gx*gx+gy*gy).sum(2));edges=np.clip(ndi.maximum_filter(strength,3)/.12,0,1)
 border=np.r_[chroma[:6].reshape(-1,3),chroma[-6:].reshape(-1,3),chroma[:,:6].reshape(-1,3),chroma[:,-6:].reshape(-1,3)];bg=np.median(border,axis=0)
 return dict(rgb=a,hsv=hsv,lum=lum,chroma=chroma,good=good,edges=edges,paper=(np.linalg.norm(chroma-bg,axis=2)<.045)&(lum>.04),bg=bg)

def boundary(owner):
 b=np.zeros(owner.shape,bool);b[1:]|=owner[1:]!=owner[:-1];b[:-1]|=owner[:-1]!=owner[1:];b[:,1:]|=owner[:,1:]!=owner[:,:-1];b[:,:-1]|=owner[:,:-1]!=owner[:,1:]
 return b

def _cost(state,hyp):
 h1,h0=hyp['h1'],hyp['h0'];target=hyp['target'];mask=h1==target;erode=ndi.binary_erosion(mask,iterations=2);region=erode&state['good']&~hyp['unknown']
 yy,xx=np.where(region);n=len(xx)
 if n<8:return None
 # Spatial folds: avoid training the target color on each evaluated pixel.
 folds=(xx>=np.median(xx)).astype(int)+2*(yy>=np.median(yy)).astype(int);features=state['chroma'][yy,xx]
 loss1=np.ones(n);loss0=np.ones(n);known=np.zeros(n,bool);protos={};target_protos=[]
 exterior=~ndi.binary_dilation(mask,iterations=3)
 for fold in range(4):
  train=folds!=fold;test=folds==fold
  if train.sum()<8 or not test.any():continue
  proto=np.median(features[train],axis=0);target_protos.append(proto);loss1[test]=np.minimum(1.,np.linalg.norm(features[test]-proto,axis=1)/.15)
 for k in np.unique(h0[region]):
  dest=h0[yy,xx]==k;context=(h1==k)&exterior&state['good']
  if context.sum()>=12:
   proto=np.median(state['chroma'][context],axis=0);loss0[dest]=np.minimum(1.,np.linalg.norm(features[dest]-proto,axis=1)/.15);known[dest]=True;protos[str(int(k))]=dict(source='observed outside target',pixels=int(context.sum()),chroma=proto.tolist())
  elif k==-999:
   proto=state['bg'];loss0[dest]=np.minimum(1.,np.linalg.norm(features[dest]-proto,axis=1)/.15);known[dest]=True;protos[str(int(k))]=dict(source='image border chromaticity',chroma=proto.tolist())
  else:
   # Entirely concealed material is unconstrained. Give H0 equal opportunity
   # to fit it, and retain the missing independent extrapolation as uncertainty.
   for fold in range(4):
    train=dest&(folds!=fold);test=dest&(folds==fold)
    if train.sum()>=8:
     proto=np.median(features[train],axis=0);loss0[test]=np.minimum(1.,np.linalg.norm(features[test]-proto,axis=1)/.15)
    else:loss0[test]=loss1[test]  # unknown cannot be evidence against H0
   protos[str(int(k))]=dict(source='cross-validated newly exposed component; no independent material evidence',pixels=int(dest.sum()))
 proto=np.median(features,axis=0);coherent=np.linalg.norm(state['chroma']-proto,axis=2)<.075
 labels,num=ndi.label(erode&coherent&state['good']);counts=np.bincount(labels.ravel());counts[0]=0;support=labels==int(np.argmax(counts)) if counts.max() else np.zeros(mask.shape,bool)
 coherence=float(support.sum()/max(1,region.sum()))
 # Compare only boundary segments on which H1/H0 disagree. Shared contours
 # cannot count as proof of the target. H0 includes newly exposed internal seams.
 band=ndi.binary_dilation(mask,iterations=3);b1=boundary(h1)&band;b0=boundary(h0)&band
 unique1=b1&~ndi.binary_dilation(b0,iterations=1);unique0=b0&~ndi.binary_dilation(b1,iterations=1)
 edge1=float(state['edges'][unique1].mean()) if unique1.sum()>=8 else 0.
 edge0=float(state['edges'][unique0].mean()) if unique0.sum()>=8 else 0.
 # Each explanation pays for unsupported unique contours; no contours is neutral.
 boundary_margin=(edge1-.5 if unique1.sum()>=8 else 0.)-(edge0-.5 if unique0.sum()>=8 else 0.)
 material_margin=float(np.mean(loss0-loss1));h1_loss=float(loss1.mean());h0_loss=float(loss0.mean())
 pos=np.zeros(mask.shape,bool);neg=pos.copy();pos[yy,xx]=loss1+.10<loss0;neg[yy,xx]=loss0+.10<loss1
 return dict(material_margin=material_margin,boundary_margin=float(boundary_margin),h1_loss=h1_loss,h0_loss=h0_loss,h1_boundary=edge1,h0_boundary=edge0,h1_unique_boundary_pixels=int(unique1.sum()),h0_unique_boundary_pixels=int(unique0.sum()),context_coverage=float(known.mean()),coherence=coherence,paper_fraction=float(state['paper'][region].mean()),pixels=n,support=support,positive=pos,negative=neg,prototypes=protos,target_chroma=proto.tolist(),boundary1=unique1,boundary0=unique0)

def decide(record,rules=None,method='combined'):
 t={**DEFAULT,**(rules or {})};r=dict(record);m=r['metrics']
 margin={'material':r['material_margin'],'boundary':r['boundary_margin'],'combined':r['margin']}[method]
 enough=r['support_pixels']>=t['minimum_pixels'] and m.get('coherence',0)>=t['coherence'] and m.get('context_coverage',0)>=t['coverage']
 if r.get('competing_ids'):status='ambiguous'
 elif m.get('pixels',0)<8:status='insufficient'
 elif margin<=-t['margin'] or m.get('paper_fraction',0)>.75:status='contradicted'
 elif enough and margin>=t['margin'] and m.get('h1_loss',1)<=t['loss'] and m.get('h1_boundary',0)>=t['edge']:status='supported'
 else:status='ambiguous'
 r.update(status=status,method=method);return r

def infer(rgb,hypothesis,rules=None,method='combined',state=None):
 state=prepare(rgb) if state is None else state;h=hypothesis;u=h.get('uncertainty_px',0.);au=h.get('angle_uncertainty_deg',0.)
 offsets=[(0.,0.)] if u<.5 else [(dx,dy) for dx in (-u,0.,u) for dy in (-u,0.,u) if dx*dx+dy*dy<=u*u*1.01]
 angles=[0.] if not au else [-au,0.,au];variants=[]
 for angle in angles:
  for dx,dy in offsets:
   q=warp(h,(dx,dy),angle) if dx or dy or angle else h;c=_cost(state,q)
   if c is None:continue
   h1_score=.6*(1-c['h1_loss'])+.4*c['h1_boundary'];h0_score=.6*(1-c['h0_loss'])+.4*c['h0_boundary']
   variants.append((h1_score,h0_score,c,dict(dx=float(dx),dy=float(dy),angle=float(angle))))
 if not variants:
  return decide(dict(id=h['id'],margin=0.,material_margin=0.,boundary_margin=0.,h1_score=None,h0_score=None,support_pixels=0,support=[],positive=[],negative=[],boundary1=[],boundary0=[],location=None,physical_center=None,uncertainty_radius_px=None,metrics=dict(pixels=0),alternatives=[],competing_ids=h.get('competitors',[])),rules,method)
 best=max(variants,key=lambda v:v[0]);null=max(variants,key=lambda v:v[1]);c=best[2];support=c['support'];yy,xx=np.where(support);location=np.c_[xx,yy].mean(0).tolist() if len(xx) else None
 # Both models independently receive the same registration budget. The margin
 # does not compare optimized H1 to a fixed, deliberately disadvantaged H0.
 margin=best[0]-null[1]
 metrics={k:v for k,v in c.items() if k not in ('support','positive','negative','boundary1','boundary0','material_margin','boundary_margin')}
 result=dict(id=h['id'],margin=float(margin),material_margin=float(null[2]['h0_loss']-c['h1_loss']),boundary_margin=float(c['h1_boundary']-null[2]['h0_boundary']),h1_score=float(best[0]),h0_score=float(null[1]),support_pixels=int(support.sum()),support=runs(support),positive=runs(c['positive']),negative=runs(c['negative']),boundary1=runs(c['boundary1']),boundary0=runs(c['boundary0']),location=location,physical_center=None,uncertainty_radius_px=float(max(2.,.15*h['diameter']+u)),metrics=metrics,registration_h1=best[3],registration_h0=null[3],alternatives=[dict(h1_score=float(a),h0_score=float(b),registration=p,metrics={k:v for k,v in c.items() if k not in ('support','positive','negative','boundary1','boundary0')}) for a,b,c,p in variants],competing_ids=h.get('competitors',[]))
 return decide(result,rules,method)
