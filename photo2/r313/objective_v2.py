"""Add owner-specific transition and worst-core material distances, fixed evidence.

This is a separate scoring epoch. Original maps and every legacy score survive.
No complete contour or black body is inferred. Modal owners are conditional, not
verified identities. Pure relabeling leaves every term invariant.
"""
import numpy as np
from scipy import ndimage as ndi
from .objective import Objective,stats,D,boundaries

class SurfaceObjective(Objective):
 def __init__(self,maps,doc):
  super().__init__(maps,doc)
  distance,nearest=ndi.distance_transform_edt(maps['core']==0,return_indices=True)
  labels=maps['core'][tuple(nearest)];labels[distance>14]=0
  self.transition_core=labels;self.fixed=[]
  for r,ix in self.regions:
   # Compact fixed boxes include every measured transition attached to this core.
   mask=(labels==r['label']);yy,xx=np.where(mask)
   box=(slice(max(0,yy.min()-30),min(self.shape[0],yy.max()+31)),slice(max(0,xx.min()-30),min(self.shape[1],xx.max()+31)))
   self.fixed.append((r,ix,box))
 def measure(self,owner,unknown,indices,split=0,detail=False):
  r=super().measure(owner,unknown,indices,split,detail);old=r['score'];own=np.asarray(owner).reshape(self.shape);un=np.asarray(unknown).reshape(self.shape);errors=[];rim=[];rows=[]
  for core,ix,box in self.fixed:
   if core['split']!=split:continue
   oo=own.ravel()[ix];uu=un.ravel()[ix];ids,n=np.unique(oo[(oo>=0)&~uu],return_counts=True);j=int(ids[n.argmax()]) if len(n) else -2
   mask=(own[box]==j)&~un[box];d=ndi.distance_transform_edt(~mask) if mask.any() else np.full(mask.shape,60.)
   material=(self.m['core'][box]==core['label']);dd=d[material]
   # A nonempty core must be covered by one connected visible physical surface;
   # missing and split portions contribute actual pixel distance, not just counts.
   p95=float(np.percentile(dd,95));errors.append(p95)
   # Use outer visible-region envelope for photographic transitions; bore edges
   # cannot stand in for an external outline. Closed occlusion holes are also
   # excluded here, so this is a conditional exterior diagnostic, not truth.
   filled=ndi.binary_fill_holes(mask);edges=filled&~ndi.binary_erosion(filled)
   de=ndi.distance_transform_edt(~edges) if edges.any() else np.full(mask.shape,60.)
   support=self.m['edges'].any(0)[box]&(self.transition_core[box]==core['label'])
   rr=de[support];rim.extend(rr.tolist())
   rows.append(dict(id=core['id'],point=core['point'],index=int(indices[j]) if j>=0 else None,material_distance=stats(dd),owner_specific_exterior_transition=stats(rr)))
  tail=float(np.mean(sorted(errors)[-min(3,len(errors)):])) if errors else 60.
  worst=float(max(errors,default=60.));rms=float(np.sqrt(np.mean(np.square(errors)))) if errors else 60.
  rimtail=float(np.percentile(rim,90)) if rim else 60.
  extra=(rms+tail+worst+max(0,rimtail-3))/D
  r.update(legacy_score=old,score=old+extra,owner_specific_terms=dict(core_p95_rms_px=rms,worst_three_core_p95_px=tail,worst_core_p95_px=worst,exterior_transition_p90_px=rimtail,additional_loss=extra))
  if detail:r['owner_specific_cores']=rows
  return r
