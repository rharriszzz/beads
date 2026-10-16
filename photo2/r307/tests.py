"""Scientific contracts exercise kernels, fixed owners and physical continuity."""
import unittest
from copy import deepcopy
import numpy as np
from photo2.r297.common import ROOT,read
from photo2.r306.evidence import load
from photo2.r306.geometry import Chain as Original
from photo2.r299.forward import shade,light_params
from photo2.r307.fast import Chain,predict
from photo2.r307.objective import Objective
class Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data,cls.m,cls.obs=load();cls.p=read(ROOT/'photo2/r306/results/campaign/exports/primary.json.gz')['parameters'];cls.s=Chain(cls.p,cls.data);cls.original=Original(cls.p,cls.data)
    def test_native_rays_and_shadows(self):
        xy=np.load(ROOT/'photo2/r296/evidence/cues.npz')['xy'][::7]
        a=self.s.camera(xy);b=self.original.camera(xy)
        np.testing.assert_array_equal(a['owner'],b['owner']);np.testing.assert_array_equal(a['unknown'],b['unknown']);np.testing.assert_allclose(a['points'],b['points'],atol=1e-10,rtol=0)
        light=light_params([self.p['light_az'],self.p['light_el'],self.p['roughness']],'directional',self.s.centers.mean(0))
        aa=shade(self.s,a,light);bb=shade(self.original,b,light)
        np.testing.assert_allclose(aa['intensity'],bb['intensity'],atol=1e-10,rtol=0);self.assertEqual(aa['unknown_shadow_pairs'],bb['unknown_shadow_pairs'])
    def test_geometry_is_original_full_chain(self):
        np.testing.assert_array_equal(self.s.centers,self.original.centers);self.assertEqual(len(self.s.indices),2405)
        self.assertLess(self.s.closure()['axis_storage_position_gap'],1e-12)
        self.assertTrue(self.s.certify(iterations=100,witnesses=False)['certified'])
    def test_fixed_owners_and_denominators(self):
        o=Objective(self.data,self.m,self.obs);v,r,a=o.evaluate(self.s,step=2);w,s,b=o.evaluate(self.s,a,step=2)
        np.testing.assert_allclose(v,w,rtol=0,atol=1e-12);self.assertEqual(a,b);self.assertEqual(r['unmatched'],0)
        self.assertEqual(len(a['reflections']),len(o.obs));self.assertGreater(np.median(np.diff(o.bounds)),24)
        self.assertTrue(all(x<1 for x,row in zip(o.confidence,o.rows) if not row['accepted']))
    def test_missing_lobes_are_penalized_not_removed(self):
        o=Objective(self.data,self.m,self.obs);_,r,a=o.evaluate(self.s,step=2);a=deepcopy(a)
        first=next(iter(a['reflections']));a['reflections'][first]=None
        v,s,_=o.evaluate(self.s,a,step=2);self.assertEqual(s['unmatched'],r['unmatched']+1);self.assertGreater(s['blocks']['reflection'],r['blocks']['reflection'])
    def test_geographic_blocks_cover_every_field_once(self):
        from photo2.r307.search import block_names
        from photo2.r297.geometry import reference
        counts={key:[] for key in ['axis_nodes','local_phase','local_spacing']}
        arc=reference().project(self.s.project(self.s.placement((np.arange(32)/32-.5)*self.s.n)[0]))['arc']
        bins=(arc/reference().length*32).astype(int)%32
        for block in range(1,5):
            names=block_names(self.p,block,self.data)
            for name in names:
                key,index=name.split(':');index=int(index);counts[key].append(index)
                if key!='axis_nodes':self.assertIn(int(bins[index]),range((block-1)*8,block*8))
        for value in counts.values():self.assertEqual(sorted(value),list(range(32)))

    def test_observed_reference_not_fitted(self):
        from photo2.r297.geometry import reference
        before=reference().points.copy();p=deepcopy(self.p);p['axis_nodes'][3]+=1;s=Chain(p,self.data)
        np.testing.assert_array_equal(reference().points,before);self.assertGreater(np.max(np.linalg.norm(s.pc-self.s.pc,axis=1)),.1)
        self.assertLess(np.max(np.linalg.norm(Chain(p,self.data,32769).pc-s.pc,axis=1)),1e-4)
if __name__=='__main__':unittest.main()
