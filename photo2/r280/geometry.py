"""Forward geometry only; no historical fitted parameters or image observations."""
from types import SimpleNamespace
import numpy as np
from photo2.r279.geometry import R,PITCH,INDICES,centers,frame,project,trace,sdf,SURFACE
from .contact import certificate
from .common import runs

def certify(p):
 c=centers(INDICES,p['hand'],p['phase'],p['pitch'])
 return certificate(SimpleNamespace(centers=c,bound=R*np.sqrt(1+.7**2),radius=R,g={'surface_tangent':np.tile([1.,0,0],(len(c),1))}))

def templates(p,shape=(224,320)):
 """Rasterized predicted first-hit surfaces; these are model outputs, not data."""
 y,x=np.indices(shape);xy=np.c_[x.ravel(),y.ravel()]
 owner,depth,unknown=trace(p,xy);owner=owner.reshape(shape)
 pc=project(p,centers(INDICES,p['hand'],p['phase'],p['pitch']))
 result=[]
 for k,c in zip(INDICES,pc):
  bound=R*1.23*p['scale'];lo=np.maximum(0,np.floor(c-bound).astype(int));hi=np.minimum(shape[::-1],np.ceil(c+bound+1).astype(int))
  isolated=np.zeros(shape,bool)
  if np.all(hi>lo):
   yy,xx=np.mgrid[lo[1]:hi[1],lo[0]:hi[0]];o,_,_=trace(p,np.c_[xx.ravel(),yy.ravel()],[k]);isolated[yy,xx]=(o==k).reshape(xx.shape)
  result.append(dict(id=f'model-{k:+03}',model_index=int(k),center=c.tolist(),diameter=float(2*R*p['scale']),visible=runs(owner==k),silhouette=runs(isolated),uncertainty_px=0.,scale_uncertainty=0.,angle_uncertainty_deg=0.,physical_center_observed=False))
 return result,dict(owner=owner,unknown=unknown.reshape(shape),depth=depth.reshape(shape))
