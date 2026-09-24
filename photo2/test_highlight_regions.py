"""Behavioral controls for bright-gap filling, independent of rendered truth."""
import unittest

import numpy as np

from highlight_regions import fill_highlights


class HighlightTests(unittest.TestCase):
    def scene(self):
        labels = np.zeros((32, 40), np.int32)
        labels[4:28, 4:36] = 7
        rgb = np.full((*labels.shape, 3), 255, np.uint8)
        rgb[labels > 0] = 100
        return rgb, labels

    def test_multiple_glints_fill_without_changing_labels_or_inputs(self):
        rgb, labels = self.scene()
        labels[10:14, 10:14] = 0
        labels[18:21, 25:29] = 0
        rgb[labels == 0] = 255
        original = labels.copy()
        result, report = fill_highlights(rgb, labels)
        self.assertEqual(report['added_pixels'], 28)
        self.assertEqual(report['filled_cavities'], 2)
        np.testing.assert_array_equal(result[original > 0], original[original > 0])
        np.testing.assert_array_equal(labels, original)
        self.assertEqual(set(np.unique(result)), {0, 7})

    def test_open_and_diagonally_open_glints_remain_unassigned(self):
        for diagonal in (False, True):
            rgb, labels = self.scene()
            labels[10:14, 10:14] = 0
            if diagonal:
                for i in range(4, 11):
                    labels[i, i] = 0
            else:
                labels[4:11, 10] = 0
            rgb[labels == 0] = 255
            result, report = fill_highlights(rgb, labels)
            np.testing.assert_array_equal(result, labels)
            self.assertEqual(report['added_pixels'], 0)

    def test_cavity_between_two_bodies_is_not_joined(self):
        rgb, labels = self.scene()
        labels[:, 20:][labels[:, 20:] > 0] = 19
        labels[10:14, 18:22] = 0
        rgb[labels == 0] = 255
        result, report = fill_highlights(rgb, labels)
        np.testing.assert_array_equal(result, labels)
        self.assertEqual(report['cavities'][0]['adjacent_labels'], [7, 19])

    def test_shadow_or_saturated_missing_region_is_not_invented(self):
        for value in ((90, 90, 90), (255, 30, 30)):
            rgb, labels = self.scene()
            labels[10:14, 10:14] = 0
            rgb[10:14, 10:14] = value
            result, report = fill_highlights(rgb, labels)
            np.testing.assert_array_equal(result, labels)
            self.assertFalse(report['cavities'][0]['all_bright'])

    def test_one_dark_pixel_rejects_whole_cavity(self):
        rgb, labels = self.scene()
        labels[10:14, 10:14] = 0
        rgb[10:14, 10:14] = 255
        rgb[10, 10] = 0
        result, _ = fill_highlights(rgb, labels)
        np.testing.assert_array_equal(result, labels)

    def test_absent_regions_and_black_image_create_no_detections(self):
        for level in (0, 255):
            rgb = np.full((32, 40, 3), level, np.uint8)
            labels = np.zeros((32, 40), np.int32)
            result, report = fill_highlights(rgb, labels)
            np.testing.assert_array_equal(result, labels)
            self.assertEqual(report['filled_cavities'], 0)

    def test_idempotent_repair_and_invalid_inputs(self):
        rgb, labels = self.scene()
        labels[10:14, 10:14] = 0
        rgb[10:14, 10:14] = 255
        result, _ = fill_highlights(rgb, labels)
        repeated, report = fill_highlights(rgb, result)
        np.testing.assert_array_equal(result, repeated)
        self.assertEqual(report['added_pixels'], 0)
        with self.assertRaises(ValueError):
            fill_highlights(rgb, labels.astype(float))
        with self.assertRaises(ValueError):
            fill_highlights(rgb.astype(float), labels)

    def test_evaluator_counts_background_and_missing_pixels(self):
        from highlight_region_audit import pixel_metrics
        truth = np.zeros((10, 10), np.int32)
        truth[:5] = 3
        empty = pixel_metrics(np.zeros_like(truth), truth)
        self.assertEqual((empty['tp_pixels'], empty['fp_pixels'], empty['fn_pixels']), (0, 0, 50))
        full = pixel_metrics(np.full_like(truth, 700), truth)
        self.assertEqual((full['tp_pixels'], full['fp_pixels'], full['fn_pixels']), (50, 50, 0))
        self.assertEqual(full['foreground_iou'], .5)

    def test_evaluator_detects_merges_and_splits_with_sparse_labels(self):
        from highlight_region_audit import pixel_metrics
        truth = np.zeros((10, 10), np.int32)
        truth[:, :5], truth[:, 5:] = 3, 9
        merged = pixel_metrics(np.full_like(truth, 700), truth)
        self.assertEqual(merged['merged_predictions'], 1)
        self.assertEqual(merged['split_truth_beads'], 0)
        split = truth.copy()
        split[:5, :5] = 17
        result = pixel_metrics(split, truth)
        self.assertEqual(result['merged_predictions'], 0)
        self.assertEqual(result['split_truth_beads'], 1)


if __name__ == '__main__':
    unittest.main()
