import unittest
from copy import deepcopy
import numpy as np
from .geometry import *
from .calibrate import BASE,measurements
from photo2.r297.common import ROOT,read,sha,load_evidence,photo

class GeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data,_=load_evidence();cls.p=read(ROOT/'photo2/r297/results/pilot/exports/model-767.json.gz')['parameters']
    def test_zero_axis_replays_original(self):
        a=Baseline(self.p,self.data);b=Chain(self.p,self.data)
        np.testing.assert_allclose(a.pc,b.pc,atol=1e-8,rtol=0)
        np.testing.assert_allclose(a.g[AXES[0]],b.g[AXES[0]],atol=1e-9)
    def test_axis_moves_anchor_and_closes(self):
        p=deepcopy(self.p);p['axis_nodes']=[20.]*16;s=Chain(p,self.data);old=Chain(self.p,self.data)
        self.assertGreater(np.max(np.linalg.norm(s.project(s.line)-old.project(old.line),axis=1)),15)
        self.assertLess(s.closure()['axis_endpoint_gap'],1e-8)
        self.assertLess(s.closure()['radial_endpoint_gap'],1e-8)
    def test_roll_changes_foreshortening_and_is_planar(self):
        p=deepcopy(self.p);p['roll']=30;s=Chain(p,self.data);a=Chain(self.p,self.data)
        self.assertGreater(np.max(abs(s.pc-a.pc)),10);self.assertEqual(np.max(abs(s.line[:,2])),0)
        np.testing.assert_allclose(np.cross(s.right,s.down),s.eye,atol=1e-12)
    def test_yaw_is_gauge(self):
        p=deepcopy(self.p);p['yaw']=17
        np.testing.assert_allclose(Chain(p,self.data).pc,Chain(self.p,self.data).pc,atol=1e-7,rtol=0)
    def test_world_scale_gauge(self):
        p=deepcopy(self.p);factor=1.17
        for k in ['radius','minor','pitch']:p[k]*=factor
        p['scale']/=factor;p['perspective']/=factor
        np.testing.assert_allclose(Chain(p,self.data).pc,Chain(self.p,self.data).pc,atol=1e-7,rtol=0)
        np.testing.assert_allclose(outlines(Chain(p,self.data)),outlines(Chain(self.p,self.data)),atol=1e-7,rtol=0)
    def test_support_polygon_and_native_outer_boundary(self):
        s=Chain(self.p,self.data);m=measurements();r=m['envelope'][0];coarse=envelope(s,[r],outlines(s,96),lanes=(0,))[0]
        offsets=np.arange(-80,81,.25);xy=np.array(r['point'])+offsets[:,None]*r['normal'];tr=s.trace(xy);bounds=offsets[tr['owner']>=0][[0,-1]]
        np.testing.assert_allclose(bounds,coarse,atol=.8)
    def test_measurement_native_pixels_and_freeze(self):
        m=measurements();a,_,_=photo()
        for r in m['envelope'][::13]:
            xy=np.array(r['samples_xy']);np.testing.assert_array_equal(a[xy[:,1],xy[:,0]],r['samples_rgb'])
        for p,h in read(BASE/'evidence/freeze.json')['files'].items():self.assertEqual(sha(ROOT/p),h)
    def test_reciprocal_inverse_transpose(self):
        a=np.array([[4.,24.],[31.,-15.]]);b=np.linalg.inv(a).T
        np.testing.assert_allclose(a.T@b,np.eye(2),atol=1e-12)
        self.assertAlmostEqual(float(a[:,0]@b[:,1]),0)
        self.assertAlmostEqual(float((a[:,0]+a[:,1])@(b[:,0]-b[:,1])),0)
    def test_collision_distinct_from_unresolved(self):
        s=Chain(self.p,self.data);self.assertTrue(contact(s)['certified'])
        p=deepcopy(self.p);p['axial']=1.5;c=contact(Chain(p,self.data));self.assertEqual(c['state'],'demonstrated-interpenetration')
if __name__=='__main__':unittest.main()
