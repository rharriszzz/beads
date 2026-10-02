"""Controls for sparse sampling, ownership accounting and 1D HSV sampling."""
import unittest
import numpy as np

from colored_bead_centers import balanced_subset
from practice_centerline_profiles import sample_path, periodic_route
from review_distributed_interiors import evaluate_known


class ColoredPositionChecks(unittest.TestCase):
    def test_uniform_selection_without_dropping_unselected_records(self):
        rows = [dict(observation_number=b*20+i+1, route_fraction=(b+.5)/20,
            source_xy=[b*100+i*4., 0.], status='good', selection_cost=i) for b in range(20) for i in range(20)]
        before = [dict(r) for r in rows]
        selected, available = balanced_subset(rows, accepted_status='good')
        self.assertEqual(len(selected), 300)
        self.assertEqual(available, [20]*20)
        self.assertEqual([sum(n in selected for n in range(b*20+1, b*20+21)) for b in range(20)], [15]*20)
        self.assertEqual(rows, before)

    def test_spacing_across_bins_without_alias_merging(self):
        rows = [dict(observation_number=1, route_fraction=.049, source_xy=[0., 0.], status='good', selection_cost=0),
                dict(observation_number=2, route_fraction=.051, source_xy=[1., 0.], status='good', selection_cost=0),
                dict(observation_number=3, route_fraction=.06, source_xy=[10., 0.], status='good', selection_cost=1),
                dict(observation_number=4, route_fraction=.2, source_xy=[20., 0.], status='uncertain', selection_cost=0)]
        selected, _ = balanced_subset(rows, accepted_status='good', minimum_separation=5)
        self.assertEqual(selected, [1, 3])
        self.assertEqual(len(rows), 4)  # Nearby proposals retain distinct observations.

    def test_rgb_interpolation_handles_red_hue_wrap(self):
        rgb = np.array([[[1., 0., .1], [1., .1, 0.]]])
        sampled, hsv = sample_path(rgb, np.array([[.5, 0.]]))
        np.testing.assert_allclose(sampled, [[1., .05, .05]])
        self.assertEqual(hsv[0, 0], 0.)

    def test_periodic_route_has_unit_normals_and_one_pixel_steps(self):
        angle = np.linspace(0, 2*np.pi, 65)
        points = np.column_stack([100+50*np.cos(angle), 100+50*np.sin(angle)])
        stations, xy, normal = periodic_route(points)
        np.testing.assert_allclose(np.diff(stations), 1.)
        np.testing.assert_allclose(np.linalg.norm(normal, axis=1), 1.)
        self.assertLess(np.max(np.linalg.norm(np.diff(xy, axis=0), axis=1)), 1.001)

    def test_evaluator_preserves_mixed_background_and_duplicate_witnesses(self):
        labels = np.ones((8, 12), int); labels[:, :2] = -1; labels[:, 7:] = 2
        def row(n, runs, xy):
            return dict(observation_number=n, selected=True, source_xy=xy, region=dict(pixel_runs=runs))
        data = dict(records=[row(1, [[3, 3, 4]], [3.5, 3]), row(2, [[4, 3, 4]], [3.5, 4]),
            row(3, [[3, 6, 8]], [7, 3]), row(4, [[4, 0, 0]], [0, 4]), row(5, [[4, 9, 9]], [9, 4])])
        result = evaluate_known(data, labels)
        self.assertEqual(result['mixed_or_background'], [3, 4])
        self.assertEqual(result['duplicate_bodies'], {'1': 2})
        self.assertEqual(result['on_black'], [5])
        self.assertEqual(result['single_body'], 3)


if __name__ == '__main__':
    unittest.main()
