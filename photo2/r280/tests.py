import ast,copy,unittest
from pathlib import Path
import numpy as np
from .geometry import R,certify,templates,sdf,SURFACE
from .common import runs,mask_from_runs
from .detector import infer,prepare,transform
from .experiments import perturb

class ScientificChecks(unittest.TestCase):
 def test_intended_radius_and_exact_surface(self):
  self.assertAlmostEqual(R,.96*4*np.sin(np.pi/6.5),14)
  np.testing.assert_allclose(sdf(SURFACE),0,atol=1e-12)
 def test_valid_packing_both_hands_all_pairs(self):
  for hand in (-1,1):
   c=certify(dict(hand=hand,phase=.713,pitch=1.12))
   self.assertTrue(c['certified']);self.assertGreater(c['minimum_gap_units'],.019)
   self.assertTrue(all(w['gap_units']>1e-6 for w in c['witnesses']))
 def test_stress_packing_rejected(self):
  self.assertFalse(certify(dict(hand=1,phase=.713,pitch=1.))['certified'])
 def test_raster_roundtrip(self):
  rng=np.random.default_rng(280);m=rng.random((23,37))>.6
  np.testing.assert_array_equal(mask_from_runs(runs(m),m.shape),m)
 def test_shadowed_paper_never_positive_from_darkness_alone(self):
  rgb=np.full((80,80,3),[150,100,140],np.uint8);rgb[25:55,25:55]=[30,20,28]
  m=np.zeros((80,80),bool);m[28:52,28:52]=True
  p=dict(id='p',visible=runs(m),silhouette=runs(m),center=[40,40],diameter=24,uncertainty_px=0)
  r=infer(rgb,[p])[0];self.assertNotEqual(r['status'],'strong');self.assertEqual(r['positive_pixels'],0)
 def test_geometry_cannot_confirm_blank_paper(self):
  rgb=np.full((64,64,3),[140,90,130],np.uint8);m=np.zeros((64,64),bool);m[20:45,20:45]=True
  p=dict(id='p',visible=runs(m),center=[32,32],diameter=25)
  r=infer(rgb,[p])[0];self.assertEqual(r['status'],'contradicted');self.assertIsNone(r['physical_center'])
 def test_identical_owners_abstain_symmetrically(self):
  rgb=np.full((64,64,3),[140,90,130],np.uint8);rgb[20:45,20:45]=[220,10,10];m=np.zeros((64,64),bool);m[20:45,20:45]=True
  p=dict(id='p',visible=runs(m),center=[32,32],diameter=25);q={**p,'id':'q'}
  rs=infer(rgb,[p,q]);self.assertEqual([r['status'] for r in rs],['ambiguous']*2)
  self.assertEqual(rs[0]['competing_ids'],['q']);self.assertEqual(rs[1]['competing_ids'],['p'])
 def test_inputs_immutable_and_no_physical_center_claim(self):
  rgb=np.full((64,64,3),[140,90,130],np.uint8);m=np.zeros((64,64),bool);m[20:45,20:45]=True
  p=dict(id='p',visible=runs(m),silhouette=runs(m),center=[32,32],diameter=25);old=copy.deepcopy(p);arr=rgb.copy()
  infer(rgb,[p],phase1=[dict(id='old',point=[30,30])]);self.assertEqual(p,old);np.testing.assert_array_equal(rgb,arr)
 def test_prediction_translation_no_wraparound(self):
  m=np.zeros((30,30),bool);m[10:20,10:20]=True
  q=transform(m,[15,15],shift=[40,0]);self.assertEqual(q.sum(),0)
 def test_inference_dependency_barrier(self):
  text=(Path(__file__).parent/'detector.py').read_text();tree=ast.parse(text)
  imports=[n.module for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
  self.assertFalse(any(any(k in str(m) for k in ('synthetic','evaluate','geometry','phase1','r279')) for m in imports))
  self.assertFalse(any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='open' for n in ast.walk(tree)))
 def test_duplicate_ids_rejected(self):
  with self.assertRaises(ValueError):infer(np.zeros((10,10,3),np.uint8),[{'id':'a'},{'id':'a'}])

if __name__=='__main__':unittest.main()
