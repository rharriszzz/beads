import unittest
from copy import deepcopy
import numpy as np
from scipy.spatial import cKDTree
from photo2.r297.common import ROOT,read
from photo2.r306.evidence import load
from photo2.r314.geometry import ShapeChain
from photo2.r314.run import engine
from .model import Chain,bump,refined_trace,subset
from .diagnose import brackets

class Contracts(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.data=load()[0];cls.p=read(ROOT/'photo2/r314/results/models/R306-2405.json.gz')['parameters'];cls.s=Chain(cls.p,cls.data);cls.e=engine()
 def test_zero_extension_preserves_original_geometry(self):
  old=ShapeChain(self.p,self.data)
  for k in ['centers','pc','indices']:np.testing.assert_array_equal(getattr(old,k),getattr(self.s,k))
  for key in old.g:np.testing.assert_array_equal(old.g[key],self.s.g[key])
 def test_translation_does_not_move_physical_glass(self):
  q=Chain(dict(self.p,translation=[4.,-8.]),self.data);np.testing.assert_array_equal(q.centers,self.s.centers);np.testing.assert_allclose(q.pc-self.s.pc,np.tile([4,-8],(q.n,1)),atol=1e-12)
  xy=self.e.xy[::133];a=refined_trace(self.s,xy);b=refined_trace(q,xy+[4,-8]);np.testing.assert_array_equal(a['owner'],b['owner'])
 def test_compact_field_is_rigid_local_and_rate_bounded(self):
  q=Chain(dict(self.p,compact_phase=[.1,0,0],compact_spacing=[.004,0,0]),self.data);outside=abs(q.indices)>101;np.testing.assert_array_equal(q.centers[outside],self.s.centers[outside]);frame=np.stack([q.g[k] for k in ['surface_tangent','surface_normal','surface_binormal']],axis=1);np.testing.assert_allclose(frame@frame.transpose(0,2,1),np.tile(np.eye(3),(q.n,1,1)),atol=1e-12);np.testing.assert_array_equal(q.dims,self.s.dims)
  with self.assertRaises(ValueError):Chain(dict(self.p,compact_phase=[5,0,0]),self.data)
 def test_compact_bump_has_zero_boundary_value_and_slope(self):
  eps=1e-5
  for x in [-45,45]:self.assertEqual(bump(x,0,45),0);self.assertLess(abs((bump(x+eps,0,45)-bump(x-eps,0,45))/(2*eps)),1e-10)
 def test_uniform_index_relabel_cannot_repair_render(self):
  q=deepcopy(self.s);q.indices=q.indices+7;xy=self.e.xy[::173];a=refined_trace(self.s,xy);b=refined_trace(q,xy);np.testing.assert_array_equal(a['owner'],b['owner']);np.testing.assert_array_equal(a['depth'],b['depth'])
 def test_occluder_removal_exposes_saved_candidate(self):
  row=next(r for r in read(ROOT/'photo2/r315/results/ledger.json.gz') if r['model']=='R306-2405' and r['id']=='R282-1537-0308');xy=np.array(row['pixels']);j=int(np.flatnonzero(self.s.indices==11)[0]);a=refined_trace(self.s,xy);b=refined_trace(self.s,xy,remove=(12,));self.assertEqual(int(np.sum(b['owner']==j)-np.sum(a['owner']==j)),238)
 def test_old_missing_boundary_has_finite_measured_distance(self):
  old=read(ROOT/'photo2/r314/results/boundary-brackets.json.gz');old=next(r for r in old['models'] if r['name']=='R306-2405');new=read(ROOT/'photo2/r315/results/R306-2405-brackets.json.gz');missing=[i for i,r in enumerate(old['brackets']) if r['missing_in_extended_scan']];self.assertEqual(len(missing),20);self.assertTrue(all(new[i]['found'] and new[i]['displacement'] is not None for i in missing))
 def test_camera_depth_fixture_and_no_false_empty_minimax(self):
  r=read(ROOT/'photo2/r315/results/sensitivity.json')['camera'];self.assertEqual(r['near_fixture_owner'],r['expected_near_owner']);self.assertLess(r['ray_reprojection_px'],1e-10)
  from photo2.r314.correspondence import evaluate_fixed
  from photo2.r314.bright import freeze_epoch
  result=evaluate_fixed(freeze_epoch([],{},'r315-empty'),[],geometry_passed=False);self.assertIsNone(result['metrics']['peak']['maximum_px'])
 def test_unfinished_ray_behind_front_surface_is_irrelevant(self):
  a=np.load(ROOT/'photo2/r314/results/models/R306-2405.npz');ix=np.flatnonzero(a['unknown']);fast=refined_trace(self.s,self.e.xy[ix],iterations=0);full=refined_trace(self.s,self.e.xy[ix]);known=~fast['unknown'];self.assertEqual(int(known.sum()),29);np.testing.assert_array_equal(fast['owner'][known],full['owner'][known])
 def test_unrelated_unknown_does_not_veto_readiness(self):
  from .measurement import measure_readiness
  a=np.load(ROOT/'photo2/r315/results/baseline-raster.npz');r=read(ROOT/'photo2/r315/results/baseline-model.json.gz')['development'];outside=np.flatnonzero(~self.e.m['roi'].ravel())[0];tr=dict(owner=a['owner'].copy(),unknown=a['unknown'].copy());before=measure_readiness(self.e,tr,r,0);tr['unknown'][outside]=True;after=measure_readiness(self.e,tr,r,0);self.assertEqual(before,after)
if __name__=='__main__':unittest.main()
