"""Guards for the R149 held-out evidence and paired-family symmetry."""
import json
import unittest

import numpy as np

from fit_maker_points import ROOT, PATCH, TRAIN, mappings, training_setup, proposal_seeds
from local_surface_fit import centers


class MakerPointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        report = json.loads((ROOT/'photo2/review/r144/corrected-report.json').read_text())
        cls.families = mappings(report)
        saved = json.loads((ROOT/'photo2/manual-labels-r146.json').read_text())
        cls.points = {a['number']: [a['x'],a['y']] for a in saved['annotations'] if a['number'] in PATCH}

    def test_signed_offsets_and_paired_minor_circle_positions(self):
        a = [self.families['A'][n] for n in PATCH]
        b = [self.families['B'][n] for n in PATCH]
        self.assertEqual(a, [-7,-6,-1,0,1,6,7])
        self.assertEqual(b, [-6,-7,1,0,-1,7,6])
        for phase in (-95, 35, 178):
            p = [0,0,1,0,55,13,phase]
            ca, cb = centers(p,np.array(a),1), centers(p,np.array(b),-1)
            np.testing.assert_allclose(ca[:,1:], cb[:,1:], atol=1e-13)
            self.assertGreater(np.max(np.abs(ca[:,0]-cb[:,0])), .8)

    def test_g_does_not_change_crop_bounds_or_proposals(self):
        changed = dict(self.points)
        changed[23] = [-99999, 99999]
        a, b = training_setup(self.points), training_setup(changed)
        for left, right in zip(a,b):
            np.testing.assert_array_equal(left,right)
        left = proposal_seeds(self.points,self.families['A'],1)[0]
        right = proposal_seeds(changed,self.families['A'],1)[0]
        for (lm,lp), (rm,rp) in zip(left,right):
            self.assertEqual(lm,rm)
            np.testing.assert_array_equal(lp,rp)
        self.assertNotIn(23,TRAIN)


if __name__ == '__main__':
    unittest.main()
