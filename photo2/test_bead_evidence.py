"""Evidence guarantees and counterexamples; no simulation-to-photo fitting."""
import unittest
import os

os.environ.setdefault('MPLCONFIGDIR', '/tmp/beads-evidence-mpl')

import numpy as np
from matplotlib.colors import rgb_to_hsv

from bead_evidence_inventory import connected_near, encode_pixels, extract_region, region_record, hue_distance


class EvidenceTests(unittest.TestCase):
    def test_hue_wrap_and_native_pixel_encoding(self):
        np.testing.assert_equal(hue_distance([359, 1], 0), [1, 1])
        mask = np.array([[True, True, False, True], [False, True, False, False]])
        self.assertEqual(encode_pixels(mask, [10, 20]), [[20, 10, 11], [20, 13, 13], [21, 11, 11]])

    def test_inset_is_internal_and_unresolved_holes_are_not_filled(self):
        mask = np.zeros((25, 25), bool); mask[3:22, 3:22] = True
        record, core = region_record(mask, np.array([12., 12.]), np.array([0, 0]))
        self.assertGreaterEqual(record['minimum_support_margin'], 3.)
        self.assertFalse(np.any(core & ~mask))
        mask[12, 12] = False
        with self.assertRaisesRegex(ValueError, 'hole'):
            region_record(mask, np.array([12., 8.]), np.array([0, 0]))

    def test_colored_interior_does_not_bridge_a_dark_interbead_seam(self):
        rgb = np.zeros((50, 60, 3)); rgb[:] = [.1, .05, .05]
        rgb[8:42, 4:56] = [.8, .03, .03]
        rgb[:, 29:32] = [.07, .02, .02]
        point = dict(source_xy=[23., 25.], kind='chromatic', appearance_mode=1)
        result = extract_region(rgb_to_hsv(rgb), point, 40., 50., [0])
        self.assertTrue(all(run[2] < 29 for run in result['region']['pixel_runs']))
        self.assertIsNone(result['reflection'])

    def test_black_reflection_has_separate_dark_body_and_centroid(self):
        rgb = np.full((50, 50, 3), .08); rgb[23:28, 23:28] = .85
        point = dict(source_xy=[25., 25.], kind='dark-reflection', appearance_mode=0)
        result = extract_region(rgb_to_hsv(rgb), point, 40., 50., [])
        np.testing.assert_allclose(result['reflection']['xy'], [25., 25.])
        self.assertGreater(result['parameters']['separate_dark_support_pixels'], 8)
        self.assertLess(result['reflection']['pixels'], result['region']['pixels'])
        limited = extract_region(rgb_to_hsv(rgb), point, 40., 10., [])
        self.assertIsNone(limited['region'])
        np.testing.assert_allclose(limited['reflection']['xy'], [25., 25.])
        # A uniform bright spot without dark context isn't certified as a body.
        with self.assertRaisesRegex(ValueError, 'distinct native-pixel reflection'):
            extract_region(rgb_to_hsv(np.ones((50, 50, 3))*.85), point, 40., 50., [])

    def test_competing_seed_and_distant_component_remain_unresolved(self):
        rgb = np.full((50, 50, 3), .1)
        with self.assertRaisesRegex(ValueError, 'competing'):
            extract_region(rgb_to_hsv(rgb), dict(source_xy=[25, 25], kind='chromatic', appearance_mode=1), 30, 5, [0])
        mask = np.zeros((30, 30), bool); mask[20:25, 20:25] = True
        with self.assertRaisesRegex(ValueError, 'too far'):
            connected_near(mask, np.array([2., 2.]), 3.)


if __name__ == '__main__':
    unittest.main()
