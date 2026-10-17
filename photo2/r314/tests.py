import unittest
from copy import deepcopy
import numpy as np
from types import MethodType
from photo2.r297.common import ROOT,read
from photo2.r306.evidence import load
from photo2.r295.geometry import Chain as Python,AXES
from .geometry import ShapeChain
from .bright import components,freeze_epoch,evaluate
from .evidence import persistence

class Contracts(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.data,_,_=load();cls.p=read(ROOT/'photo2/r313/continuation/models/R306-2405.json.gz')['parameters']
 def test_serialization_cannot_change_ranking(self):
  import json
  from .run import merit
  from .objective import dominates
  a={'development':{'vector':dict(omission=10.,paper=.2,ownership=30.,external=6.,seam=40.,worst=12.),'cores':[{'modal_fraction':.3}]}}
  b=json.loads(json.dumps(a,sort_keys=True));self.assertEqual(merit(a),merit(b));self.assertFalse(dominates(a['development'],b['development']))
 def test_independent_persistence(self):
  a=np.zeros((9,9),bool);a[4,4]=True;self.assertFalse(persistence(a,0).any());a[3:6,4]=True;self.assertTrue(persistence(a,0)[4,4])
 def test_bore_independent_exterior_and_support(self):
  p=dict(self.p,exterior=True,edge=.3,face=.7,bore=.08);a=ShapeChain(p,self.data);b=ShapeChain(dict(p,bore=.25),self.data)
  q=np.array([[0,a.radius,0],[.7*a.axial*a.radius,.5*a.radius,0],[.1*a.radius,.9*a.radius,0]])
  np.testing.assert_allclose(a.local_sdf(q),b.local_sdf(q),atol=1e-12)
  n=np.eye(3);np.testing.assert_allclose(a.support(n,n),b.support(n,n),atol=1e-12);self.assertGreater(a.local_sdf([[0,0,0]])[0],0)
  self.assertLess(a.local_sdf([[0,.15*a.radius,0]])[0],0);self.assertGreater(b.local_sdf([[0,.15*b.radius,0]])[0],0)
 def test_support_gradient(self):
  s=ShapeChain(dict(self.p,exterior=True,edge=.4,face=.6,bore=.1),self.data);rng=np.random.default_rng(314);n=rng.normal(size=(100,3));t=s.g[AXES[0]][:100];h,g=s.support(n,t,True)
  dot=(n*t).sum(1);rad=np.linalg.norm(np.cross(n,t),axis=1);expected=s.radius*((1-s.edge)*rad+.7*s.axial*(1-s.face)*abs(dot)+np.hypot(s.edge*rad,.7*s.axial*s.face*dot));np.testing.assert_allclose(h,expected,atol=1e-12)
  numeric=np.stack([(s.support(n+np.eye(3)[j]*1e-6,t)-s.support(n-np.eye(3)[j]*1e-6,t))/2e-6 for j in range(3)],1);np.testing.assert_allclose(g,numeric,atol=1e-7)
 def test_native_independent_rays(self):
  s=ShapeChain(dict(self.p,exterior=True,edge=.6,face=.25,bore=.1,trajectory_mix=.1),self.data);m=np.load(ROOT/'photo2/r313/evidence/maps.npz');xy=m['xy'][::83];a=s.trace(xy);s.trace=MethodType(Python.trace,s);b=s.trace(xy);np.testing.assert_array_equal(a['owner'],b['owner']);np.testing.assert_array_equal(a['unknown'],b['unknown'])
 def test_connected_lobes_not_between_patches(self):
  xy=np.array([[0,0],[1,0],[8,0],[9,0]]);c=components(xy,[1,.8,.9,.8]);self.assertEqual(len(c),2);self.assertLess(c[0]['centroid'][0],2);self.assertGreater(c[1]['centroid'][0],7)
 def test_missing_and_correspondence_epoch(self):
  obs=[dict(id='a',peak=[0,0],centroid=[.5,0],reliable_correspondence=True,reliably_localized=True,specular_status='supported')];e=freeze_epoch(obs,{'a':[0,1]},'fixture');r=evaluate(e,[],geometry_passed=True);self.assertTrue(r['metrics']['peak']['maximum_is_infinite']);self.assertIsNone(r['metrics']['peak']['maximum_px'])
  with self.assertRaises(ValueError):evaluate(e,[],{'a':[0,2]})
 def test_multiple_features_per_bead_and_peak_maximum(self):
  obs=[dict(id=str(i),peak=[i*10,0],centroid=[i*10+.5,0],reliable_correspondence=True,reliably_localized=True,specular_status='supported') for i in range(2)];e=freeze_epoch(obs,{'0':[0,1],'1':[0,2]},'fixture');r=evaluate(e,[dict(index=0,lobe=i+1,peak=[i*10+d,0],centroid=[i*10+.5+d,0]) for i,d in enumerate([3,4])],geometry_passed=True);self.assertEqual(r['metrics']['peak']['maximum_px'],4.);self.assertAlmostEqual(r['metrics']['peak']['rms_px'],np.sqrt(12.5))
if __name__=='__main__':unittest.main()
