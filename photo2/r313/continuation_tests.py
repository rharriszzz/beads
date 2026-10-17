"""Scientific controls for shared glass profiles, hollow-solid contact and fixed evidence."""
import unittest
from copy import deepcopy
import numpy as np
from photo2.r297.common import ROOT,read,sha
from photo2.r306.evidence import load
from photo2.r295.geometry import AXES
from photo2.r295.contact_fallback import audit_pair
from .geometry_experiment import ShapeChain,contacts
from .objective_v2 import SurfaceObjective

class StructuralContracts(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.data,_,_=load();cls.base=read(ROOT/'photo2/r313/results/models/R306-2405.json.gz')['parameters']
 def test_shared_profile_zero_sets_and_glass_rigidity(self):
  for h,f,a in [(.14,.8,.8),(.5,.4,.4),(.03,1.,1.1)]:
   p=deepcopy(self.base);p.update(hole=h,rounding=f,axial=a);s=ShapeChain(p,self.data);r=s.radius
   points=np.array([[0,r,0],[0,h*r,0],[.7*r*a,(1+h)/2*r,0]])
   np.testing.assert_allclose(s.local_sdf(points),0,atol=1e-12);self.assertGreater(s.local_sdf([[0,0,0]])[0],0)
   self.assertEqual(s.dims.shape,(3,));self.assertEqual(s.indices[(s.indices>=-100)&(s.indices<=99)].tolist(),list(range(-100,100)))
 def test_independent_support_and_gradient(self):
  p=deepcopy(self.base);p.update(hole=.4,rounding=.6,axial=.5,trajectory_mix=.7);s=ShapeChain(p,self.data);rng=np.random.default_rng(31304);n=rng.normal(size=(60,3));t=s.g[AXES[0]][:60];dot=np.sum(n*t,axis=1);rad=np.linalg.norm(np.cross(n,t),axis=1);r=s.radius;rr=(1-s.hole)/2*s.rounding
  expected=r*((1-rr)*rad+.7*s.axial*(1-s.rounding)*abs(dot)+np.hypot(rr*rad,.7*s.axial*s.rounding*dot))
  value,grad=s.support(n,t,True);np.testing.assert_allclose(value,expected,atol=1e-12)
  numeric=np.stack([(s.support(n+np.eye(3)[j]*1e-6,t)-s.support(n-np.eye(3)[j]*1e-6,t))/2e-6 for j in range(3)],axis=1);np.testing.assert_allclose(grad,numeric,atol=1e-7)
  frame=np.stack([s.g[k] for k in AXES],axis=1);np.testing.assert_allclose(frame@frame.transpose(0,2,1),np.broadcast_to(np.eye(3),frame.shape),atol=1e-10)
 def fixture(self,offset):
  p=deepcopy(self.base);p.update(hole=.6,rounding=.8,axial=.25);s=ShapeChain(p,self.data);s.n=2;s.centers=np.array([[0.,0.,0.],[0.,offset*s.radius,0.]])
  s.g={AXES[0]:np.array([[1.,0.,0.],[0.,0.,1.]]),AXES[1]:np.array([[0.,1.,0.],[0.,1.,0.]]),AXES[2]:np.array([[0.,0.,1.],[-1.,0.,0.]])};s.indices=np.arange(2);return s
 def test_interlinked_hollow_fixture_not_convex_separable(self):
  s=self.fixture(1.);cert=s.certify(220,True);self.assertFalse(cert['certified']);actual=audit_pair(s,0,1,max_depth=16,max_nodes=300000);self.assertEqual(actual['state'],'certified-nonintersection',actual)
 def test_actual_interpenetration_fixture(self):
  s=self.fixture(0.);actual=audit_pair(s,0,1,max_depth=14,max_nodes=100000);self.assertEqual(actual['state'],'demonstrated-interpenetration',actual)
 def test_fixed_evidence_and_initial_trials(self):
  start=read(ROOT/'photo2/r313/continuation/start.json');self.assertEqual(len(start['preserved_trials']),426)
  for path,h in start['preserved_trials'].items():self.assertEqual(sha(ROOT/path),h)
  self.assertEqual(sha(ROOT/'photo2/r313/evidence/maps.npz'),start['evidence_sha256'])
 def test_relabel_and_gross_corruption(self):
  cases=read(ROOT/'photo2/r313/continuation/objective-controls-v2.json')['cases'];a={r['name']:r['metrics']['score'] for r in cases};self.assertEqual(a['unchanged'],a['pure_index_permutation'])
  for name in ['single_owner_all_image','fill_all_background_nearest_owner','erase_every_second_body','erode_all_surfaces_3px','overgrow_all_surfaces_7px']:self.assertGreater(a[name],a['unchanged'])
if __name__=='__main__':unittest.main()
