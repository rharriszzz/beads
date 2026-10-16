"""Numerical geometry, evidence partition, assignment and transaction contracts."""
import unittest
from copy import deepcopy
import numpy as np
from scipy.integrate import quad
from .geometry import Chain,canonical,valid,reference,periodic_field
from .evidence import load
from .search import starts
from .objective import match,Objective,vector

class Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data,cls.m,cls.obs=load();cls.starts=starts(cls.data)
        cls.p=deepcopy(cls.starts[3]['parameters']);cls.p['local_spacing']=[0.]*32
        cls.scene=Chain(cls.p,cls.data)

    def test_closed_axis_phase_and_frame(self):
        s=self.scene;z=s.closure()
        for key in ['axis_storage_position_gap','axis_storage_tangent_gap','string_axis_endpoint_gap','radial_endpoint_gap','tangent_endpoint_gap']:
            self.assertLess(z[key],1e-8,key)
        self.assertLessEqual(abs(z['total_twist_turns']),1.)
        self.assertEqual(len(set(s.indices)),s.n)

    def test_arclength_independent_quadrature(self):
        s=self.scene
        for fraction in [.01,.23,.51,.77,.99]:
            a=fraction*s.length;u=float(s.inverse(a));delta=.15
            v=float(s.inverse(a+delta))
            actual=quad(lambda x:float(np.linalg.norm(s.spline(x,1))),u,v,epsabs=1e-10)[0]
            self.assertAlmostEqual(actual,delta,places=6)
        dense=Chain(self.p,self.data,resolution=32769)
        self.assertLess(np.max(np.linalg.norm(dense.pc-s.pc,axis=1)),1e-4)

    def test_open_axis_distinct_from_string(self):
        p=deepcopy(self.p);p.update(topology='open',gap_steps=3.)
        s=Chain(p,self.data);z=s.closure()
        self.assertLess(z['axis_storage_position_gap'],1e-10)
        self.assertGreater(z['string_axis_endpoint_gap'],.1)
        self.assertEqual(s.n,p['count'])

    def test_axis_adjustment_is_global_and_reference_immutable(self):
        before=reference().points.copy();p=deepcopy(self.p);p['axis_nodes'][0]=3.
        q=Chain(p,self.data)
        self.assertTrue(np.array_equal(before,reference().points))
        self.assertGreater(np.max(np.linalg.norm(q.pc-self.scene.pc,axis=1)),.1)
        self.assertLess(q.closure()['axis_storage_tangent_gap'],1e-10)

    def test_spacing_and_twist_bounded_between_knots(self):
        p=deepcopy(self.p);p['local_spacing']=[.02,-.02]*16
        s=Chain(p,self.data)
        self.assertGreater(np.min(np.diff(s.integral)),0)
        p['turn']=6.;p['topology']='open';self.assertFalse(valid(p))
        p['local_spacing'][0]=.2
        with self.assertRaises(ValueError):Chain(p,self.data)

    def test_assignment_has_no_cheap_skips_or_duplicate_owner(self):
        o=deepcopy(self.obs[:2])
        for i,r in enumerate(o):r['point']=[100.+i,100.]
        pred=[dict(index=5,point=[100.,100.])]
        a=match(o,pred)
        self.assertEqual(a['matched'],1);self.assertEqual(a['unmatched'],1)
        self.assertGreater(a['loss'],1.)
        far=match(o,[dict(index=5,point=[1000.,1000.])])
        self.assertEqual(far['unmatched'],2)

    def test_comparison_partition_never_in_training(self):
        obj=Objective(self.data,self.m,self.obs)
        self.assertTrue(all(o['section']%4!=3 for o in obj.obs))
        self.assertTrue(all(self.m['beads'][i]['split']=='development' for i in obj.bi))
        self.assertTrue(all(self.m['envelope'][i]['split']=='development' for i in obj.ei))
        for r in obj.photo.rows:self.assertNotEqual(int(r['station']/self.data['length']*32)%4,3)

    def test_contact_includes_nonlocal_pairs(self):
        s=self.scene;cert=s.certify(iterations=100)
        from scipy.spatial import cKDTree
        pairs=cKDTree(s.centers).query_pairs(2*s.bound+1e-8)
        self.assertEqual(len(pairs),cert['pairs'])
        self.assertTrue(any(abs(a-b)>s.n-10 for a,b in pairs))

if __name__=='__main__':unittest.main()
