"""Pure counterfactual forward geometry; no observations or truth masks."""
import numpy as np
from scipy import ndimage as ndi
from photo2.r280.geometry import R,INDICES,centers,project,trace,certify
from .common import runs

def owner_map(parameters,shape):
 y,x=np.indices(shape);owner,depth,unknown=trace(parameters,np.c_[x.ravel(),y.ravel()])
 return owner.reshape(shape),unknown.reshape(shape)

def counterfactual(parameters,target,shape,owner=None,unknown=None):
 if owner is None:owner,unknown=owner_map(parameters,shape)
 mask=owner==target;y,x=np.where(mask);h0=owner.copy();un=np.zeros(shape,bool) if unknown is None else unknown.copy()
 if len(x):
  exposed,_,uu=trace(parameters,np.c_[x,y],INDICES[INDICES!=target]);h0[y,x]=exposed;un[y,x]|=uu
 center=project(parameters,centers([target],parameters['hand'],parameters['phase'],parameters['pitch']))[0]
 return dict(id=f'k{target:+03}',target=int(target),center=center.tolist(),diameter=float(2*R*parameters['scale']),h1=owner.copy(),h0=h0,unknown=un,uncertainty_px=0.,angle_uncertainty_deg=0.,competitors=[],projected_centers=project(parameters,centers(INDICES,parameters['hand'],parameters['phase'],parameters['pitch'])).tolist())

def baseline_predictions(hyp):
 return [dict(id=f'k{k:+03}',center=hyp.get('projected_centers',[[0.,0.]]*29)[int(k)+14],diameter=hyp['diameter'],visible=runs(hyp['h1']==k),silhouette=runs(hyp['h1']==k),uncertainty_px=hyp.get('uncertainty_px',0.),angle_uncertainty_deg=hyp.get('angle_uncertainty_deg',0.),scale_uncertainty=0.) for k in INDICES]

def warp(hyp,shift=(0,0),angle=0.,uncertainty=0.,angle_uncertainty=0.):
 """Shared 2D pose perturbation of both explanations, retaining owner alternatives."""
 from photo2.r280.detector import transform
 q={**hyp};a=np.radians(angle);rot=np.array([[np.cos(a),-np.sin(a)],[np.sin(a),np.cos(a)]]);matrix=rot.T[[1,0]][:,[1,0]];c=np.array(hyp['center'])[::-1];delta=np.array(shift)[::-1]
 for name in ('h1','h0'):q[name]=ndi.affine_transform(hyp[name],matrix,offset=c-matrix@(c+delta),order=0,cval=-999)
 q['unknown']=ndi.affine_transform(hyp['unknown'].astype(np.uint8),matrix,offset=c-matrix@(c+delta),order=0,cval=1)>0
 q['center']=(np.array(hyp['center'])+shift).tolist();q['projected_centers']=((np.asarray(hyp.get('projected_centers',[hyp['center']]))-hyp['center'])@rot.T+hyp['center']+shift).tolist();q['uncertainty_px']=float(uncertainty);q['angle_uncertainty_deg']=float(angle_uncertainty)
 return q

def serial(hyp):
 return {k:v for k,v in hyp.items() if k not in ('h1','h0','unknown')}|{'h1_surfaces':{str(k):runs(hyp['h1']==k) for k in np.unique(hyp['h1'])},'h0_surfaces':{str(k):runs(hyp['h0']==k) for k in np.unique(hyp['h0'])},'unknown':runs(hyp['unknown'])}
