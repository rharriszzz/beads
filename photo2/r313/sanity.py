"""Deliberately corrupt predicted visible geometry; observations never change."""
import numpy as np
from scipy import ndimage as ndi
from photo2.r297.common import ROOT,read,save
from .objective import Objective

def run():
 out=ROOT/'photo2/r313/results';dest=out.parent/'continuation';m=dict(np.load(out.parent/'evidence/maps.npz'));doc=read(out.parent/'evidence/freeze.json');eng=Objective(m,doc);base=read(out/'models/R306-2405.json.gz');a=np.load(out/'models/R306-2405.npz');own=a['owner'].reshape(tuple(m['shape']));un=a['unknown'].reshape(own.shape);indices=np.array(base['positions']['indices']);cases=[]
 def add(name,o,u=un,expected='worse'):
  r=eng.measure(o,u,indices,0,True);cases.append(dict(name=name,expected=expected,metrics=r));print(name,r['score'],flush=True)
 add('unchanged',own,expected='baseline')
 add('pure_index_permutation',np.where(own>=0,len(indices)-1-own,-1),expected='identical')
 for n in [3,7]:
  fill=ndi.distance_transform_edt(own<0,return_distances=False,return_indices=True);d=ndi.distance_transform_edt(own<0);oo=own.copy();mask=(d<=n)&(own<0);oo[mask]=own[tuple(fill[:,mask])];add(f'overgrow_all_surfaces_{n}px',oo)
  oo=own.copy()
  for k in np.unique(own[own>=0]):oo[(own==k)&~ndi.binary_erosion(own==k,iterations=n)]=-1
  add(f'erode_all_surfaces_{n}px',oo)
 add('single_owner_all_image',np.zeros_like(own))
 add('erase_every_second_body',np.where((own>=0)&(own%2==0),-1,own))
 # Retain observed material but fill unobserved region with nearest owners: not a fit.
 fill=ndi.distance_transform_edt(own<0,return_distances=False,return_indices=True);nearest=own[tuple(fill)];add('fill_all_background_nearest_owner',nearest)
 # Delete only model surfaces carrying no reliable pigment evidence. This tests the
 # identifiable boundary of the objective, not an artificial black silhouette prior.
 ids=np.unique(own[m['material']]);oo=own.copy();oo[~np.isin(own,ids)]=-1
 add('delete_bodies_without_pigment_evidence',oo,expected='may_be_unidentifiable')
 save(dest/'objective-controls.json',dict(cases=cases,baseline=cases[0]['metrics']['score'],policy='Artificial corruptions are nonphysical controls only, never accepted as geometry. Pure relabeling must be invariant. Unknown black geometry need not be identifiable from colored material.'))
if __name__=='__main__':run()
