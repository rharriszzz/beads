"""Geometric gauge and loss controls for the registration search."""
import unittest
import numpy as np
from fit_positive_registration import canonical_pose, metrics, rank_trial
from test_tangent_circles import circular_model


class PositiveRegistrationTests(unittest.TestCase):
    def test_confirmed_membership_precedes_better_soft_score(self):
        cheap = dict(candidate=0, same_body_constraints_satisfied=False, metrics=dict(objective=.1),
                     phase_delta_degrees=0., origin_shift_beads=0.)
        consistent = dict(cheap, candidate=1, same_body_constraints_satisfied=True, metrics=dict(objective=.2))
        self.assertEqual(min([cheap, consistent], key=rank_trial)['candidate'], 1)

    def test_origin_gauge_relabels_the_same_complete_geometry_for_both_hands(self):
        for hand in [-1, 1]:
            source, model = circular_model(hand)
            phase, shift = 25., 1.23
            model.phase = phase; model.origin = shift/source.nbeads
            raw = model.geometry(np.arange(source.nbeads))
            cp, cs = canonical_pose(phase, shift, source.nrows, source.nbeads, hand)
            model.phase = cp; model.origin = cs/source.nbeads
            canonical = model.geometry(np.arange(source.nbeads))
            for key in ['centers', 'outward', 'tangent', 'radial']:
                np.testing.assert_allclose(canonical[key], np.roll(raw[key], 1, axis=0), atol=2e-9, rtol=0)

    def member(self, fraction=1., exposed=True):
        return dict(dominant_fraction=fraction, outward_exposed=exposed,
                    coherent_central_membership=fraction >= .95 and exposed, unresolved_pixels=0)

    def test_sector_balance_prevents_dense_cluster_dominance(self):
        centers = [dict(sector=0, alternatives=[dict(distance_pixels=0.)]) for _ in range(19)]
        centers.append(dict(sector=1, alternatives=[dict(distance_pixels=10.)]))
        result = metrics(centers, [self.member(), self.member()], [0, 1], 20.)
        self.assertAlmostEqual(result['balanced_center_rms_pixels'], np.sqrt(50))
        self.assertAlmostEqual(result['objective'], 50/400)

    def test_split_hidden_missing_or_unknown_support_cannot_disappear_from_loss(self):
        center = [dict(sector=0, alternatives=[dict(distance_pixels=0.)])]
        self.assertEqual(metrics(center, [self.member(.5)], [0], 20.)['objective'], .5)
        self.assertEqual(metrics(center, [self.member(1., False)], [0], 20.)['objective'], 1.)
        missing = [dict(sector=0, alternatives=[])]
        self.assertEqual(metrics(missing, [self.member()], [0], 20.)['objective'], 9.)
        # A partially unresolved positive patch still contributes its original
        # denominator through the verified-owner fraction, rather than being dropped.
        unknown = self.member(.75); unknown['unresolved_pixels'] = 1
        result = metrics(center, [unknown], [0], 20.)
        self.assertEqual(result['objective'], .25)
        self.assertEqual(result['uncertain_patches'], 1)


if __name__ == '__main__':
    unittest.main()
