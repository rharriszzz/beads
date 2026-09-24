"""Independent controls for ownership, symmetry, abstention and gradient cost."""
import unittest

import numpy as np

from highlight_regions import fill_highlights
from shared_highlights import METHODS, assign_shared


class SharedHighlightTests(unittest.TestCase):
    def scene(self):
        labels = np.full((11, 11), 7, np.int32)
        labels[:, 6:] = 19
        labels[4:7, 4:7] = 0
        labels[7, 5] = 19
        rgb = np.full((11, 11, 3), 255, np.uint8)
        return rgb, labels

    def test_conservative_parity_and_flat_gradient(self):
        rgb, labels = self.scene()
        baseline, _ = fill_highlights(rgb, labels)
        result, _ = assign_shared(rgb, labels, 'conservative')
        np.testing.assert_array_equal(result, baseline)
        distance, _ = assign_shared(rgb, labels, 'distance')
        gradient, _ = assign_shared(rgb, labels, 'gradient')
        np.testing.assert_array_equal(distance, gradient)

    def test_symmetric_ties_abstain_and_inputs_stay_fixed(self):
        rgb, labels = self.scene()
        original, colors = labels.copy(), rgb.copy()
        for method in ('distance', 'gradient'):
            result, report = assign_shared(rgb, labels, method)
            self.assertEqual(result[5, 5], 0)
            self.assertGreater(report['tie_pixels'], 0)
            self.assertGreater(report['shared_added_pixels'], 0)
            np.testing.assert_array_equal(result[labels > 0], labels[labels > 0])
            self.assertLessEqual(set(np.unique(result)), set(np.unique(labels)))
        np.testing.assert_array_equal(labels, original)
        np.testing.assert_array_equal(rgb, colors)

    def test_gradient_can_override_nearest_boundary(self):
        labels = np.full((9, 11), 7, np.int32)
        labels[:, 6:] = 19
        labels[4, 3:8] = 0
        rgb = np.full((9, 11, 3), 255, np.uint8)
        rgb[labels == 7] = 0
        distance, _ = assign_shared(rgb, labels, 'distance')
        gradient, _ = assign_shared(rgb, labels, 'gradient')
        self.assertEqual(distance[4, 5], 7)
        self.assertEqual(gradient[4, 5], 19)

    def test_label_permutation_and_rotation_do_not_choose_ties(self):
        rgb, labels = self.scene()
        renamed = np.where(labels == 7, 101, np.where(labels == 19, 2, 0)).astype(np.int32)
        for method in METHODS:
            result, _ = assign_shared(rgb, labels, method)
            permutation, _ = assign_shared(rgb, renamed, method)
            expected = np.where(result == 7, 101, np.where(result == 19, 2, 0))
            np.testing.assert_array_equal(permutation, expected)
            rotated, _ = assign_shared(np.rot90(rgb), np.rot90(labels), method)
            np.testing.assert_array_equal(rotated, np.rot90(result))

    def test_dark_saturated_or_one_dark_pixel_abstain(self):
        for color in ((80, 80, 80), (255, 10, 10), (0, 0, 0)):
            rgb, labels = self.scene()
            if color == (0, 0, 0):
                rgb[5, 5] = color
            else:
                rgb[labels == 0] = color
            for method in METHODS:
                result, _ = assign_shared(rgb, labels, method)
                np.testing.assert_array_equal(result, labels)

    def test_open_and_diagonal_exit_abstain(self):
        for diagonal in (False, True):
            rgb, labels = self.scene()
            if diagonal:
                for i in range(5):
                    labels[i, i] = 0
            else:
                labels[:5, 4] = 0
            for method in METHODS:
                result, _ = assign_shared(rgb, labels, method)
                np.testing.assert_array_equal(result, labels)

    def test_absent_and_deleted_region_never_recreated(self):
        rgb, labels = self.scene()
        labels[labels == 7] = 0  # removed region now connected to exterior
        for method in METHODS:
            result, _ = assign_shared(rgb, labels, method)
            np.testing.assert_array_equal(result, labels)
            for level in (0, 255):
                empty = np.zeros_like(labels)
                result, _ = assign_shared(np.full_like(rgb, level), empty, method)
                np.testing.assert_array_equal(result, empty)

    def test_multiple_single_owner_glints_keep_conservative_result(self):
        rgb, labels = self.scene()
        labels[labels == 19] = 7
        labels[8, 8] = 0
        baseline, _ = fill_highlights(rgb, labels)
        for method in METHODS:
            result, report = assign_shared(rgb, labels, method)
            np.testing.assert_array_equal(result, baseline)
            self.assertEqual(report['shared_added_pixels'], 0)
        with self.assertRaises(ValueError):
            assign_shared(rgb, labels, 'unknown')
        with self.assertRaises(ValueError):
            assign_shared(rgb, labels.astype(float), 'distance')


if __name__ == '__main__':
    unittest.main()
