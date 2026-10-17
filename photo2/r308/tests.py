"""Native periodicity, bounded effects and objective contracts."""
import unittest
from copy import deepcopy
import numpy as np
from photo2.r297.common import ROOT,read
from photo2.r306.evidence import load
from photo2.r307.fast import Chain
from photo2.r308.search import move,correction,FIELD_LIMITS
from photo2.r308.objective import Objective
class Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data,cls.m,cls.obs=load();cls.p=read(ROOT/'photo2/r306/results/campaign/exports/primary.json.gz')['parameters'];cls.s=Chain(cls.p,cls.data)
    def test_full_phase_period_is_geometry_gauge(self):
        p=deepcopy(self.p);p['phase']+=2*np.pi;s=Chain(p,self.data)
        np.testing.assert_allclose(s.centers,self.s.centers,atol=2e-12,rtol=0)
        xy=np.load(ROOT/'photo2/r296/evidence/cues.npz')['xy'][::11]
        np.testing.assert_array_equal(s.trace(xy)['owner'],self.s.trace(xy)['owner'])
    def test_fourier_corrections_have_bounded_physical_effects(self):
        q=move(self.p,['axis_nodes:2:sin','local_phase:2:cos','local_spacing:2:sin'],[.4,.4,.4]);c=correction(q,self.p,self.data)
        self.assertTrue(c['within_bounds']);self.assertGreater(c['projected_center_displacement_max_px'],0)
        s=Chain(q,self.data);self.assertEqual(s.n,self.s.n);self.assertTrue(s.certify(iterations=80,witnesses=False)['certified'])
        self.assertLess(s.closure()['axis_storage_position_gap'],1e-10)
        for k in FIELD_LIMITS:self.assertAlmostEqual(np.mean(np.array(q[k])-self.p[k]),0,places=12)
        huge=move(self.p,['local_phase:1:sin'],[10]);self.assertFalse(correction(huge,self.p)['within_bounds'])
    def test_global_steps_do_not_change_distributed_fields(self):
        q=move(self.p,['elevation','scale','phase'],[1,1,1])
        for k in FIELD_LIMITS:self.assertEqual(q[k],self.p[k])
        self.assertEqual(self.p['count'],q['count']);self.assertEqual(self.p['hand'],q['hand'])
    def test_native_fixed_owners_and_missing_denominators(self):
        obj=Objective(self.data,self.m,self.obs);v,r,a=obj.evaluate(self.s,step=1);vv,rr,aa=obj.evaluate(self.s,a,step=1)
        np.testing.assert_allclose(v,vv,atol=1e-12,rtol=0);self.assertEqual(a,aa)
        a=deepcopy(a);a['reflections'][next(iter(a['reflections']))]=None
        _,bad,_=obj.evaluate(self.s,a,step=1);self.assertEqual(bad['unmatched'],r['unmatched']+1);self.assertGreater(bad['blocks']['reflection'],r['blocks']['reflection'])
    def test_unknown_separator_sample_is_not_a_boundary(self):
        o=Objective(self.data,self.m,self.obs);_,result,_=o.evaluate(self.s,step=1,detail=True)
        # Use the R307 incumbent where the inherited S25 edge is unresolved.
        p=read(ROOT/'photo2/r307/results/campaign/exports/primary.json.gz')['parameters'];s=Chain(p,self.data)
        row=next(r for r in o.separators if r['id']=='S25');tr=s.trace(np.array(row['xy']));known=~tr['unknown'];own=tr['owner']
        changes=np.flatnonzero((own[:-1]!=own[1:])&known[:-1]&known[1:])+.5
        expected=min(abs(changes-row['valley_sample']))*row['representative_distance']/96
        _,r,_=o.evaluate(s,step=1,detail=True);actual=next(x for x in r['separators'] if x['id']=='S25')
        self.assertGreater(actual['unknown_samples'],0);self.assertAlmostEqual(actual['error'],expected,places=10);self.assertGreater(actual['error'],9.)

    def test_geographic_balance_preserves_component_accounting(self):
        obj=Objective(self.data,self.m,self.obs);v,r,a=obj.evaluate(self.s,step=1)
        self.assertAlmostEqual(float(v@v),sum(r['blocks'].values()),places=10)
        self.assertEqual(len(a['regions']),len(obj.rows));self.assertEqual(set(obj.sections),set(range(32))-set(range(3,32,4)))
if __name__=='__main__':unittest.main()
