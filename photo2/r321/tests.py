import unittest
from copy import deepcopy
import numpy as np
from scipy.optimize import minimize
from photo2.r306.evidence import load
from photo2.r295.geometry import AXES
from photo2.r314.geometry import contacts
from photo2.r320.controls import straight
from photo2.r320.audit import support
from .packing import parameters,derive,straight_reference,straight_gaps,side_planes
from .model import Chain,corrected

class Contracts(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.data=load()[0]
 def test_straight_symmetry_reduction_against_3d(self):
  parent=Chain(parameters(2800,1.95,.85),self.data)
  for ratio in [1.,1.03,1.14]:
   s=straight(parent,ratio);analytic=straight_gaps(s.p['turn'],s.axial,s.p['minor'],1.4*s.radius*s.axial*ratio,s.radius)
   for j,d in enumerate([1,6,7]):
    a=20;b=a+d;delta=s.centers[b]-s.centers[a];ta=s.g[AXES[0]][a];tb=s.g[AXES[0]][b]
    def f(x):
     n=x/np.linalg.norm(x);return -(delta@n+0.-support(n,ta,s.radius,s.axial)-support(n,tb,s.radius,s.axial))
    vals=[minimize(f,x,method='Powell',options={'xtol':1e-11,'ftol':1e-12}).fun for x in [delta,ta,tb]]
    self.assertAlmostEqual(analytic[j],-min(vals),places=6)
 def test_curvature_density_closes_and_reference_station(self):
  for count in [2401,2402,2800,2801]:
   for hand in [-1,1]:
    s,z=derive(parameters(count,1.95,.85,hand),self.data)
    self.assertAlmostEqual(s.station([0])[0],0.,places=9)
    self.assertAlmostEqual(s.station([s.start+s.n])[0]-s.station([s.start])[0],s.length,places=8)
    for key in ['center_endpoint_gap','orientation_endpoint_gap']:self.assertLess(s.summary()['closure'][key],1e-8)
    g,n,a,b=side_planes(s);self.assertGreater(g.min(),0)
    self.assertLess(abs(np.sum(n*n,axis=1)-1).max(),1e-12)
 def test_known_curvature_collision_repaired_without_shrinking(self):
  p=parameters(2800,1.95,.85);p['packing_spacing']='uniform';s,z=derive(p,self.data);c=contacts(s,seconds=1.)
  self.assertEqual(c['classification'],'demonstrated-interpenetration')
  p['packing_spacing']='curvature-density';s,z=derive(p,self.data);c=contacts(s,seconds=1.)
  self.assertTrue(c['certified']);self.assertEqual(s.radius,1.95);self.assertEqual(s.axial,.85)
 def test_local_basis_support_and_budget(self):
  from photo2.r297.geometry import periodic_field
  p=parameters(2800,1.95,.85);co=np.zeros(32);co[14]=3.;p=corrected(p,co)
  u=np.linspace(0,1,4097);field=periodic_field(p['axis_nodes'],u-.5)
  far=abs((u-14/32+.5)%1-.5)>2/32+1e-8;self.assertLess(abs(field[far]).max(),1e-12)
  self.assertLess(abs(field).max(),3.00001)
  co[14]=10
  with self.assertRaises(ValueError):Chain(corrected(p,co),self.data)
 def test_actual_side_segment_upper_bounds(self):
  from .gaps import neighbor_gaps
  s,z=derive(parameters(2800,1.95,.85),self.data);rows=neighbor_gaps(s)
  for row in rows:
   self.assertLess(row['side_segment_sdf_max'],1e-8)
   for pair in row['pairs']:
    self.assertGreaterEqual(pair['upper']+1e-8,pair['lower'])
    self.assertLessEqual(pair['upper'],pair['initial_upper']+1e-12)
 def test_contact_reference_competing_branch(self):
  z=straight_reference(2800/431,.85);self.assertIsNotNone(z['best']);self.assertGreater(z['best']['gaps_over_r'][2],.01)
  self.assertLess(z['branches'][1]['gaps_over_r'][1],-.01)
if __name__=='__main__':unittest.main()
