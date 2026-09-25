import unittest
import numpy as np
from beads5_188_diagnostic import partition, sample_profile, trough_measure


class DiagnosticControls(unittest.TestCase):
    def test_partition_conserves_irregular_support(self):
        mask = np.zeros((12, 14), bool)
        mask[1:11, 2:12] = True
        mask[4:7, 5:8] = False
        for dx in [-2, 0, 2]:
            for cut in [7, 9, 11]:
                parts = partition(mask, [[7, 1], [5, 10]], cut, dx)
                np.testing.assert_array_equal(sum(p.astype(int) for p in parts), mask.astype(int))

    def test_subpixel_sampling_on_linear_rgb_field(self):
        y, x = np.indices((20, 20))
        rgb = np.stack([x+2*y, 3*x-y, x+y], axis=-1)
        t = np.array([-1.5, 0, 1.5])
        result = sample_profile(rgb, [8.5, 7.5], [1, 0], t, [-1, 0, 1])
        for i, offset in enumerate([-1, 0, 1]):
            xx, yy = 8.5+t, 7.5+offset
            np.testing.assert_allclose(result[i], np.stack([xx+2*yy, 3*xx-yy, xx+yy], axis=-1))

    def test_trough_does_not_turn_monotone_slope_into_positive_depth(self):
        t = np.arange(-7, 7.01, .25)
        self.assertLess(trough_measure(t, 100+t)['depth_below_lower_shoulder'], 0)
        valley = 100-20*np.exp(-t*t/2)
        self.assertAlmostEqual(trough_measure(t, valley)['depth_below_lower_shoulder'], 20, places=3)


if __name__ == '__main__':
    unittest.main()
