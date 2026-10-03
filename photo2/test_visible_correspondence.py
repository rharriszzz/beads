"""Adverse correspondence controls; real known-POV checks run in the review."""
import unittest
from unittest.mock import patch
import numpy as np
from visible_correspondence import nearest_centers, center_score, interior_membership, mode_conflicts


class CorrespondenceTests(unittest.TestCase):
    def bank(self):
        # A crescent-like region centroid can differ greatly from physical and
        # outward centers. Neither source index is a recovered photo identity.
        return dict(conservative_radius_pixels=10, records=[dict(generator_index=i,
            visible_centroid_xy=[x, 0], projected_physical_center_xy=[20-x, 0],
            outward_xy=[20-x, 0], pixels=20, sampled_area_pixels2=80, outward_exposed=True,
            finite_grid_centroid_unknown_shift_bound_pixels=.2) for i, x in [(5, 0), (12, 20)]])

    def records(self):
        return [dict(id='a', number=1, x=0, y=0, approximate_image_arc_fraction=0),
                dict(id='b', number=2, x=1, y=0, approximate_image_arc_fraction=.5)]

    def test_visible_center_semantics_and_duplicate_observations_preserved(self):
        result = nearest_centers(self.records(), self.bank())
        self.assertEqual([r['alternatives'][0]['generator_index'] for r in result], [5, 5])
        self.assertEqual(center_score(result)['duplicate_nearest_associations'], 1)
        self.assertEqual([r['bead_index'] for r in result], [None, None])
        wrong_semantics = nearest_centers(self.records(), self.bank(), 'outward_xy')
        self.assertEqual(wrong_semantics[0]['alternatives'][0]['generator_index'], 12)

    def test_missing_far_or_hidden_candidate_cannot_improve_score(self):
        bank = self.bank(); bank['records'][0]['outward_exposed'] = False
        bank['records'][1]['visible_centroid_xy'] = [1000, 0]
        result = center_score(nearest_centers(self.records(), bank))
        self.assertEqual(result['missing'], 2)
        self.assertIsNone(result['sse_pixels2'])
        # A refined grid must not admit a 12px² sliver merely because it has
        # twelve samples: the same 48px² native-area gate applies at both steps.
        bank = self.bank(); bank['records'][0]['sampled_area_pixels2'] = 12
        bank['records'][1]['outward_exposed'] = False
        self.assertFalse(nearest_centers(self.records(), bank)[0]['alternatives'])

    def test_patch_ownership_uses_every_pixel_and_keeps_unknowns(self):
        records = [dict(observation_id='p', observation_number=3, source_xy=[1, 0],
            appearance_mode=1, region=dict(pixel_runs=[[0, 0, 2]]))]
        with patch('visible_correspondence.rays', return_value=(np.array([5, 12, 5]),
                np.zeros(3), np.array([0, 0, 1]))) as ray_call, \
             patch('visible_correspondence.visible_anchors', return_value=dict(exposed=np.ones(20, bool))):
            result = interior_membership(None, records, None)[0]
        np.testing.assert_array_equal(ray_call.call_args.args[1], [[0, 0], [1, 0], [2, 0]])
        self.assertEqual(result['unresolved_pixels'], 1)
        self.assertEqual(result['dominant_fraction'], 1/3)
        self.assertFalse(result['coherent_central_membership'])
        self.assertIsNone(result['bead_index'])

    def test_different_appearance_on_same_predicted_owner_is_conflict(self):
        rows = [dict(coherent_central_membership=True, dominant_generator_index=5,
            observation_number=n, appearance_mode=mode) for n, mode in [(1, 1), (2, 2)]]
        result = mode_conflicts(rows)
        self.assertEqual(result[0]['observation_numbers'], [1, 2])
        # No resolved photo aliases or color order are generated.
        self.assertEqual(set(result[0]), {'generator_index', 'observation_numbers', 'modes'})


if __name__ == '__main__':
    unittest.main()
