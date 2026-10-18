import unittest
import numpy as np
from photo2.r306.evidence import load
from photo2.r295.geometry import AXES
from .model import parameters,Chain,corrected,D
from .audit import support
class Contracts(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.data=load()[0]
 def test_shape_dimensions_and_literal_support(self):
  s=Chain(parameters(2405,1.8,.95),self.data);t=np.array([1.,0,0])
  self.assertAlmostEqual(float(s.support(t,t)),.7*1.8*.95)
  self.assertAlmostEqual(float(s.support([0.,1,0],t)),1.8)
  rng=np.random.default_rng(320);n=rng.normal(size=(100,3));n/=np.linalg.norm(n,axis=1)[:,None]
  np.testing.assert_allclose(s.support(n,np.tile(t,(100,1))),support(n,np.tile(t,(100,1)),1.8,.95),atol=1e-12)
  self.assertLess(abs(float(s.local_sdf([.7*1.8*.95,.57*1.8,0]))),1e-12)
  self.assertLess(abs(float(s.local_sdf([0,1.8,0]))),1e-12)
 def test_closure_both_hands_and_winding_transition(self):
  for n in [2000,2401,2402,2405,3200]:
   for h in [-1,1]:
    s=Chain(parameters(n,1.65,1.05,h),self.data);c=s.summary()['closure']
    for key in ['axis_storage_position_gap','string_axis_endpoint_gap','center_endpoint_gap','orientation_endpoint_gap']:self.assertLess(c[key],1e-8)
    self.assertAlmostEqual(abs(c['phase_turns']),round(n/6.5),places=8)
    a=s.g[AXES[0]];r=s.g['radial'];self.assertLess(abs(np.sum(a*r,axis=1)).max(),1e-12)
    self.assertLess(abs(np.sum(a*a,axis=1)-1).max(),1e-12)
    self.assertEqual(s.p['turn'],n/s.p['winding'])
  self.assertEqual(parameters(2401,1.65,1.)['winding'],369)
  self.assertEqual(parameters(2402,1.65,1.)['winding'],370)
 def test_centerline_bound_and_zero_recovery(self):
  p=parameters(2405,1.65,1.05);s=Chain(p,self.data);z=Chain(corrected(p,[0]*4),self.data);np.testing.assert_array_equal(s.centers,z.centers)
  q=Chain(corrected(p,[1.5,0,0,0]),self.data);self.assertAlmostEqual(q.summary()['axis_correction_px'],1.5)
  self.assertLess(q.summary()['closure']['center_endpoint_gap'],1e-8)
  with self.assertRaises(ValueError):Chain(corrected(p,[.11*D,0,0,0]),self.data)
 def test_forbidden_independent_angles_and_open_gap(self):
  for key,value in [('tilt',1),('radial_cant',1),('gap_steps',1),('seam_fraction',-.46),('topology','open'),('winding',369),('turn',6.4),('hole',.2),('s0',4)]:
   p=parameters(2405,1.65,1.05);p[key]=value
   with self.assertRaises(ValueError):Chain(p,self.data)
if __name__=='__main__':unittest.main()
