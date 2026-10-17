import unittest
from copy import deepcopy
import numpy as np
from photo2.r306.evidence import load
from photo2.r306.geometry import Chain as Original
from photo2.r309.geometry import Chain
from photo2.r309.search import starts
from photo2.r309.measure import reference_dimension,distances,tail_loss
from photo2.r309.render import predict
from photo2.r307.fast import predict as historical

class Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data,cls.m,cls.obs=load();cls.p=starts()[0]['parameters']
    def test_independent_linear_reference(self):
        d=reference_dimension(self.m);a,b=np.array(d['reference']['endpoints']);self.assertAlmostEqual(d['D_px'],np.linalg.norm(a-b));self.assertEqual(d['reference']['id'],'B14');self.assertLess(d['D_px'],50)
    def test_missing_and_absolute_max(self):
        rows=[dict(id='weak',error_px=40,strong=False),dict(id='strong',error_px=10,strong=True),dict(id='missing',error_px=None)];s=distances(rows,40);self.assertEqual(s['missing'],1);self.assertEqual(s['maximum_record']['id'],'weak');self.assertEqual(s['maximum_D'],1)
    def test_tail_is_not_mean_only(self):self.assertGreater(tail_loss([0,2]),tail_loss([np.sqrt(2),np.sqrt(2)]))
    def test_zero_height_exact_historical(self):
        a=Chain(self.p,self.data);b=Original(self.p,self.data);np.testing.assert_array_equal(a.centers,b.centers);np.testing.assert_allclose(a.g['surface_tangent'],b.g['surface_tangent'],atol=1e-14)
    def test_height_is_one_smooth_global_law(self):
        p=deepcopy(self.p);p.update(minor_y=.02,tilt_y=1.);s=Chain(p,self.data);y=(s.axis_xy[:,1]-1591)/1591;np.testing.assert_allclose(s.centers-s.line,p['minor']*(1+.02*y)[:,None]*s.g['radial']);self.assertTrue(s.certify(iterations=100,witnesses=False)['certified']);self.assertLess(s.closure()['axis_storage_position_gap'],1e-8)
    def test_directional_native_centroid_unchanged(self):
        s=Chain(self.p,self.data);obs=[r for r in self.obs if r['strong']][::40];a,_=predict(s,1.,obs);b,_=historical(s,1.,obs);self.assertEqual(a,b)
if __name__=='__main__':unittest.main()
