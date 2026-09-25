"""Numerical controls for curved diagnostic cuts; no bead truth asserted."""
import unittest
import numpy as np
from beads6_boundary_diagnostic import partition


class PartitionTests(unittest.TestCase):
    def test_curved_cut_known_pixels_and_shift(self):
        mask = np.ones((5, 5), bool)
        lower = [[0, 1], [4, 3]]
        parts = partition(mask, None, lower)
        self.assertEqual(int(parts['upper'].sum()), 11)
        self.assertEqual(int(parts['lower'].sum()), 14)
        shifted = partition(mask, None, lower, lower_shift=1)
        self.assertEqual(int(shifted['upper'].sum()), 16)

    def test_two_cuts_with_holes_conserve_without_overlap(self):
        mask = np.ones((7, 9), bool)
        mask[2:4, 3:5] = False
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                parts = partition(mask, [[2,0],[5,6]], [[0,3],[8,5]], dx, dy)
                summed = sum(p.astype(int) for p in parts.values())
                np.testing.assert_array_equal(summed, mask.astype(int))
                self.assertTrue(all(not np.any(p & ~mask) for p in parts.values()))


if __name__ == '__main__':
    unittest.main()
