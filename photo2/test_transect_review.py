"""Controls for interval evaluation and image-coordinate rectification."""
import unittest
import numpy as np
from transect_review import assess, interval_distance, strip_image


class TransectReviewTests(unittest.TestCase):
    def test_interval_distance_preserves_uncertainty(self):
        for value in [-4, 0, 7]:
            self.assertEqual(interval_distance(value, [-4, 7]), 0)
        self.assertEqual(interval_distance(-8, [-4, 7]), 4)
        self.assertEqual(interval_distance(10, [-4, 7]), 3)
        for value, bounds in [(0, [2, 1]), (np.nan, [0, 1]), (0, [0, np.inf])]:
            with self.assertRaises(ValueError):
                interval_distance(value, bounds)

    def test_width_and_midpoint_bounds_cover_endpoint_combinations(self):
        item = dict(id='test', review=dict(outer_interval_px=[-60, -50], inner_interval_px=[30, 45]),
                    original=dict(outer=-65, inner=50, center=0),
                    corrected=dict(outer=-55, inner=40, center=-7.5),
                    clear=dict(outer=True, inner=False))
        summary = assess([item])
        self.assertEqual(item['review']['width_interval_px'], [80, 105])
        self.assertEqual(item['review']['midpoint_interval_px'], [-15, -2.5])
        self.assertEqual(summary['original']['mean_edge_distance_outside_px'], 5)
        self.assertEqual(summary['corrected']['edges_inside'], 2)
        self.assertEqual(summary['original']['centers_inside'], 0)
        self.assertEqual(summary['corrected']['centers_inside'], 1)
        self.assertEqual(summary['clear_anchors'][0]['outside_px'], 5)

    def test_rectification_uses_xy_and_fourfold_normal_scale(self):
        y, x = np.mgrid[:250, :250]
        rgb = np.stack([x, y, np.full_like(x, 99)], axis=-1).astype('uint8')
        image = np.asarray(strip_image(rgb, np.array([120., 120.]), np.array([1., 0.]), np.array([0., 1.])))
        np.testing.assert_array_equal(image[112, 360], [120, 120, 99])
        np.testing.assert_array_equal(image[112, 400], [130, 120, 99])
        np.testing.assert_array_equal(image[152, 360], [120, 130, 99])

    def test_rotated_rectification_and_outside_frame(self):
        y, x = np.mgrid[:250, :250]
        rgb = np.stack([x, y, np.full_like(x, 99)], axis=-1).astype('uint8')
        image = np.asarray(strip_image(rgb, np.array([120., 120.]), np.array([0., 1.]), np.array([-1., 0.])))
        np.testing.assert_array_equal(image[112, 400], [120, 130, 99])
        np.testing.assert_array_equal(image[152, 360], [110, 120, 99])
        edge = np.asarray(strip_image(rgb, np.array([5., 5.]), np.array([1., 0.]), np.array([0., 1.])))
        np.testing.assert_array_equal(edge[112, 0], [255, 255, 255])


if __name__ == '__main__':
    unittest.main()
