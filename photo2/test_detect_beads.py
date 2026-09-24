import unittest

import numpy as np

from detect_beads import METHODS, color_classes, detect
from detection_metrics import score_instances


class DetectionTests(unittest.TestCase):
    def test_empty_white_image(self):
        for method in METHODS:
            labels, result = detect(np.full((64, 64, 3), 255, np.uint8), method)
            self.assertFalse(labels.any())
            self.assertEqual(result['objects'], [])

    def test_red_hue_wrap_and_unknown_is_not_black(self):
        rgb = np.array([[[255, 0, 10], [255, 10, 0], [255, 255, 255], [0, 0, 0]]], np.uint8)
        classes, _ = color_classes(rgb, ('red', 'yellow', 'black'))
        np.testing.assert_array_equal(classes, [[1, 1, 0, 3]])

    def test_two_separated_same_color_objects(self):
        rgb = np.full((128, 128, 3), 255, np.uint8)
        rgb[30:55, 20:45] = (255, 0, 0)
        rgb[70:95, 70:95] = (255, 0, 0)
        labels, result = detect(rgb, 'color_components', 'ryb')
        self.assertEqual(labels.max(), 2)
        self.assertEqual([o['color'] for o in result['objects']], ['red', 'red'])
        self.assertTrue(all(o['bead_index'] is None for o in result['objects']))

    def test_perfect_overlap_and_missing_truth(self):
        truth = np.zeros((20, 30), np.int32)
        truth[2:10, 2:10] = 1
        truth[10:18, 20:28] = 2
        objects = [{'color': 'red'}, {'color': 'black'}]
        report = score_instances(truth, truth, objects, ['red', 'black', 'yellow'])
        self.assertEqual(report['zero_pixel_indices'], [2])
        self.assertEqual(report['thresholds']['12']['tp'], 2)
        self.assertEqual(report['thresholds']['12']['color_correct'], 2)
        self.assertEqual(report['foreground_union']['iou'], 1.)

    def test_merge_and_split_not_counted_as_exact_instances(self):
        truth = np.zeros((20, 20), np.int32)
        truth[2:10, 2:10] = 1
        truth[10:18, 2:10] = 2
        merged = (truth > 0).astype(np.int32)
        r = score_instances(merged, truth, [{'color': 'black'}], ['black', 'black'])
        self.assertEqual(r['merged_predictions'], 1)
        self.assertEqual(r['thresholds']['12']['tp'], 0)  # exactly .5 is not > .5
        self.assertEqual(r['foreground_union']['iou'], 1.)  # perfect silhouette, failed instances
        single = merged
        r = score_instances(truth, single, [{'color': 'black'}]*2, ['black'])
        self.assertEqual(r['split_truth_beads'], 1)
        self.assertEqual(r['thresholds']['12']['tp'], 0)

    def test_false_shadow_and_subthreshold_match_retained(self):
        truth = np.zeros((30, 30), np.int32)
        truth[1:3, 1:3] = 1
        truth[10:20, 10:20] = 2
        pred = truth.copy()
        pred[23:28, 23:28] = 3
        r = score_instances(pred, truth, [{'color': 'black'}]*3, ['black', 'red'])
        s = r['thresholds']['12']
        self.assertEqual((s['tp'], s['fp'], s['ignored']), (1, 1, 1))
        self.assertEqual(s['color_correct'], 0)

    def test_relabeling_truth_does_not_change_scores(self):
        truth = np.array([[0, 1, 1], [0, 2, 2]], np.int32)
        pred = truth.copy()
        one = score_instances(pred, truth, [{'color': 'red'}, {'color': 'black'}],
                              ['red', 'black'], thresholds=(1,))
        two = score_instances(pred, np.array([0, 2, 1])[truth],
                              [{'color': 'red'}, {'color': 'black'}], ['black', 'red'], thresholds=(1,))
        self.assertEqual(one['thresholds'], two['thresholds'])


if __name__ == '__main__':
    unittest.main()
