"""Geometric checks for a provisional inverse curve, including contrary cases."""
import unittest

import numpy as np

from fit_bead_centerline import fit_pairs, local_pairs, nearest_distances


def ellipse_rows():
    rows = []
    for u in np.linspace(0, 1, 128, endpoint=False):
        a = 2*np.pi*u
        xy = np.array([300+100*np.cos(a), 200+65*np.sin(a)])
        tangent = np.array([-100*np.sin(a), 65*np.cos(a)])
        normal = np.array([-tangent[1], tangent[0]])/np.linalg.norm(tangent)
        width = 15+2*np.cos(a)
        rows.append(dict(u=float(u), supported=True, normal=normal.tolist(),
                         low_xy=(xy-width*normal).tolist(),
                         high_xy=(xy+width*normal).tolist(), weight=1.))
    return rows


class CurveChecks(unittest.TestCase):
    def test_recovers_closed_ellipse_from_sides_without_old_curve(self):
        fit = fit_pairs(ellipse_rows())
        u = np.array(fit['u'])
        truth = np.column_stack([300+100*np.cos(2*np.pi*u),
                                 200+65*np.sin(2*np.pi*u)])
        # Varying nuisance width is regularized; middle remains independently determined.
        self.assertLess(np.max(np.linalg.norm(np.array(fit['points'])-truth, axis=1)), 1e-8)
        np.testing.assert_allclose(fit['points'][0], fit['points'][-1], atol=1e-9)
        transformed = ellipse_rows()
        rotation = np.array([[0., -1.], [1., 0.]])
        for row in transformed:
            row['normal'] = (np.array(row['normal'])@rotation).tolist()
            for name in ['low_xy', 'high_xy']:
                row[name] = (np.array(row[name])@rotation+[10, 20]).tolist()
        rotated = fit_pairs(transformed)
        np.testing.assert_allclose(rotated['points'], np.array(fit['points'])@rotation+[10, 20], atol=1e-8)

    def test_sparse_false_side_support_does_not_create_a_large_indent(self):
        rows = ellipse_rows()
        for i in [20, 21, 22]:
            rows[i]['low_xy'][0] += 60
        fit = fit_pairs(rows)
        truth = np.array(fit_pairs(ellipse_rows())['points'])
        rms = np.sqrt(np.mean(np.sum((np.array(fit['points'])-truth)**2, axis=1)))
        self.assertLess(rms, 2.)
        self.assertLess(min(fit['paired_robust_weights'][20:23]), .3)

    def test_unsupported_side_is_preserved_and_exclusion_is_explicit(self):
        axis = dict(xy=np.column_stack([np.arange(100), np.zeros(100)]),
                    normal=np.tile([0., 1.], (100, 1)))
        points = [dict(observation_number=i+1, station=i*3, cross=0.,
                       inset_support_radius=2., support_area=20.) for i in range(24)]
        rows, admitted, rejected = local_pairs(points, axis, 5., excluded=[7])
        self.assertNotIn(7, admitted)
        self.assertIn(7, rejected)
        self.assertFalse(any(row['supported'] for row in rows))
        with self.assertRaisesRegex(ValueError, 'Insufficient'):
            fit_pairs(rows)

    def test_one_sided_color_coverage_can_bias_middle_despite_tiny_fit_error(self):
        # Systematic ownership/visibility bias is not removed by robust fitting.
        biased = ellipse_rows()
        for row in biased:
            row['low_xy'][1] += 8.
            row['high_xy'][1] += 8.
        fit = fit_pairs(biased)
        truth = np.array(fit_pairs(ellipse_rows())['points'])
        np.testing.assert_allclose(np.array(fit['points'])-truth, np.tile([0., 8.], (513, 1)), atol=1e-8)

    def test_distances_are_to_segments_and_crossing_curve_is_refused(self):
        self.assertEqual(float(nearest_distances([[0, 0], [10, 0]], [[5, 3]])[0]), 3.)
        rows = ellipse_rows()
        for row in rows:
            a = 2*np.pi*row['u']
            xy = np.array([100*np.sin(a), 100*np.sin(2*a)])
            row['low_xy'] = (xy-[0, 10]).tolist()
            row['high_xy'] = (xy+[0, 10]).tolist()
            row['normal'] = [0., 1.]
        with self.assertRaisesRegex(ValueError, 'Self-intersecting'):
            fit_pairs(rows)
        for row in rows:
            xy = np.array([100*np.sin(2*np.pi*row['u']), 0.])
            row['low_xy'] = (xy-[0, 10]).tolist()
            row['high_xy'] = (xy+[0, 10]).tolist()
        with self.assertRaisesRegex(ValueError, 'Self-intersecting'):
            fit_pairs(rows)


if __name__ == '__main__':
    unittest.main()
