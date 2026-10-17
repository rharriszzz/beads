import unittest
from copy import deepcopy
import numpy as np
from matplotlib.path import Path
from photo2.r297.common import ROOT,read
from photo2.r306.evidence import load
from photo2.r315.model import refined_trace
from photo2.r295.geometry import AXES
from .model import Chain
from .renderer import Hybrid,RayLayers,sandwich,plane_orders
from .fixtures import arrange
OUT=ROOT/'photo2/r316/results'

class Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=load()[0];cls.p=read(ROOT/'photo2/r315/results/baseline-model.json.gz')['parameters'];p=deepcopy(cls.p);p.update(perspective=0,exterior=True);cls.s=Chain(p,cls.data)
    def test_saved_native_owner_equivalence(self):
        self.assertTrue(read(OUT/'benchmark-summary.json')['passed'])
        for r in read(OUT/'benchmarks.json'):
            self.assertEqual(r['target_bodies'],200);self.assertGreater(r['full_bodies'],200);self.assertEqual(r['oracle_unknown'],0)
    def test_holes_are_not_opaque(self):
        s=arrange(self.s,[[0,0,0]],[self.s.eye]);r=Hybrid().trace(s,s.pc)
        self.assertEqual(r['owner'][0],-1);self.assertEqual(r['stats']['fallback_pixels'],1)
    def test_overlap_without_separation_is_fallback(self):
        s=arrange(self.s,[[0,0,0],[0,0,0]],[self.s.eye,self.s.eye]);xy=s.pc[:1]+[s.radius*s.scale*.5,0];r=Hybrid().trace(s,xy);o=refined_trace(s,xy)
        self.assertEqual(r['stats']['proved_pairs'],0);self.assertEqual(r['stats']['fallback_pixels'],1);np.testing.assert_array_equal(r['owner'],o['owner'])
    def test_support_sandwich_contains_independent_extremes(self):
        s=arrange(self.s,[[0,0,0]],[self.s.eye+self.s.right]);z=sandwich(s,0);self.assertLessEqual(z['bound'],.025)
        angles=np.linspace(0,2*np.pi,997,endpoint=False);n=np.c_[np.cos(angles),np.sin(angles)]@np.array([s.right,s.down]);_,g=s.support(n,s.g[AXES[0]][0],True);xy=s.project(g);self.assertTrue(Path(z['outer']).contains_points(xy,radius=1e-7).all())
    def test_regional_cycle_defeats_global_sort(self):
        f=read(OUT/'fixtures.json');self.assertTrue(f['passed']);self.assertTrue(f['cycle_demonstrated']);r=next(z for z in f['cases'] if z['name']=='regional-cycle');self.assertGreater(r['center_sort_disagreements'],0)
    def test_cache_changes_coordinates_and_geometry(self):
        s=arrange(self.s,[[0,0,0]],[self.s.eye]);xy=np.array([s.pc[0]+[s.radius*s.scale*.5,0],s.pc[0]+[0,s.radius*s.scale*.7]]);c=RayLayers();a=c.trace(s,xy);self.assertFalse(a['stats']['cache_hit']);self.assertTrue(c.trace(s,xy)['stats']['cache_hit']);b=c.trace(s,xy+50);self.assertFalse(b['stats']['cache_hit']);np.testing.assert_array_equal(b['owner'],refined_trace(s,xy+50)['owner'])
        q=deepcopy(s);q.bore=.3;r=c.trace(q,xy);self.assertFalse(r['stats']['cache_hit']);np.testing.assert_array_equal(r['owner'],refined_trace(q,xy)['owner'])
    def test_partial_reuse_and_global_invalidation(self):
        z=read(OUT/'cache-benchmark.json');self.assertTrue(z['passed']);rows={r['name']:r for r in z['cases']};self.assertGreater(rows['local-phase']['layers']['reused_beads'],0)
        for k in ['radius','translation']:self.assertEqual(rows[k]['layers']['reused_beads'],0)
    def test_boolean_and_continuous_clipping(self):self.assertTrue(read(OUT/'clipping.json')['passed'])
    def test_legacy_occupancy_never_certified_from_hull(self):
        r=next(z for z in read(OUT/'benchmarks.json') if z['name']=='legacy-ortho');self.assertEqual(r['hybrid']['occupied_certified'],0)
    def test_finite_camera_explicit_fallback(self):
        r=next(z for z in read(OUT/'benchmarks.json') if z['name']=='convex-finite');self.assertEqual(r['hybrid']['fallback_pixels'],r['rays'])
    def test_coherent_orientation_rigid_and_bounded(self):
        p=deepcopy(self.p);p['compact_tilt']=[8,0,-8];s=Chain(p,self.data);f=np.stack([s.g[k] for k in AXES],axis=1);np.testing.assert_allclose(f@f.transpose(0,2,1),np.broadcast_to(np.eye(3),f.shape),atol=1e-12)
        p['compact_tilt']=[100,0,0]
        with self.assertRaises(ValueError):Chain(p,self.data)
    def test_no_reconstruction_promoted(self):
        self.assertFalse(read(OUT/'experiment.json')['adopted']);self.assertFalse(read(OUT/'recovery.json')['adopted'])
        for k in ['R306','narrow','negative-repair','positive-recovery','joint-recovery']:
            r=read(OUT/f'{k}-model.json.gz');self.assertEqual(r['cohort'],list(range(-100,100)));self.assertFalse(r['readiness']['development']['ready'])
if __name__=='__main__':unittest.main()
