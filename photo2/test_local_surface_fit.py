"""Guard holdout isolation and camera/phase coordinate equivalence."""
import copy,json,unittest
from pathlib import Path
import numpy as np
from local_surface_fit import ROOT,INDICES,canonical_view,outward,trace,initial_fit,refine


class LocalSurfaceFitTests(unittest.TestCase):
    def test_equivalent_local_camera_phase(self):
        p=np.array([1348,289,8,9,35,-15,45.]);q=canonical_view(p)
        self.assertNotEqual(p[4],q[4])
        for hand in [-1,1]:
            np.testing.assert_allclose(outward(p,INDICES,hand),outward(q,INDICES,hand),atol=1e-10)
            xy=np.array([[1348,280],[1360,290],[1380,260],[1375,315]])
            self.assertTrue(np.array_equal(trace(p,xy,hand)[0],trace(q,xy,hand)[0]))

    def test_held_out_body_never_changes_fit(self):
        cfg=json.loads((ROOT/'photo2/local-fit-r126.json').read_text());altered=copy.deepcopy(cfg)
        altered['observations']['G']=(np.array(altered['observations']['G'])+[250,-200]).tolist()
        mapping=cfg['hypotheses']['H1']
        initial=initial_fit(cfg,mapping,1);changed=initial_fit(altered,mapping,1)
        for first,second in zip(initial,changed):
            self.assertEqual(first[0],second[0]);np.testing.assert_array_equal(first[1],second[1])
        a=refine(initial[0][1],1,mapping,cfg,maxfev=30)
        b=refine(initial[0][1],1,mapping,altered,maxfev=30)
        np.testing.assert_array_equal(a[0],b[0]);self.assertEqual(a[1:],b[1:])


if __name__=='__main__':unittest.main()
