import unittest

from area_warning_stability import area_state, omission_audit, audit_inventory
from inventory_selection import PARAMETERS, select_records
import numpy as np


class StabilityControls(unittest.TestCase):
    def test_strict_thresholds_and_equalities(self):
        for ratio, expected in [(.499, 'small'), (.5, 'ordinary'), (2, 'ordinary'), (2.001, 'large')]:
            self.assertEqual(area_state(ratio, PARAMETERS), expected)

    def test_known_even_median_crossing(self):
        result = omission_audit(534, list(range(8)), [288, 238, 240, 547, 240, 279, 261, 271], PARAMETERS)
        self.assertEqual(result['nominal_median_area_px'], 266)
        self.assertEqual(result['omission_state_counts'], {'large': 4, 'ordinary': 4})
        self.assertEqual(result['category'], 'threshold_sensitive')
        self.assertAlmostEqual(result['omission_ratio_min'], 534/271)
        self.assertAlmostEqual(result['omission_ratio_max'], 534/261)

    def test_odd_median_and_persistent_warning(self):
        result = omission_audit(400, list(range(5)), [100, 110, 120, 130, 140], PARAMETERS)
        self.assertEqual(result['category'], 'persistent_large')
        self.assertEqual([r['median_area_px'] for r in result['trials']], [125, 125, 120, 115, 115])

    def test_omission_cannot_use_three_references(self):
        result = omission_audit(100, [1, 2, 3, 4], [100]*4, PARAMETERS)
        self.assertEqual(result['nominal_state'], 'ordinary')
        self.assertEqual(result['category'], 'insufficient_reference')
        self.assertIsNone(result['omission_ratio_min'])
        self.assertTrue(all(t['ratio'] is None for t in result['trials']))

    def test_area_excluded_neighbors_remain_frozen_references(self):
        records = [dict(id=i+1, marker_xy=[100+i, 100], region_pixels=a,
                        status='reviewed_body', color='red', bead_index=None)
                   for i, a in enumerate([100, 100, 100, 100, 100, 10])]
        params = dict(PARAMETERS, explicit_excluded_ids=[])
        active, excluded = select_records(records, np.zeros((600, 800)), params)
        self.assertEqual([r['id'] for r in excluded], [6])
        result = audit_inventory(dict(active_observations=active, excluded_observations=excluded), params)
        self.assertEqual(len(result), 5)
        self.assertTrue(all(r['area_excluded_reference_ids'] == [6] for r in result))
        self.assertTrue(all(len(r['trials']) == 5 for r in result))
        active[0]['selection']['local_median_area_px'] = 99
        with self.assertRaisesRegex(ValueError, 'replay mismatch'):
            audit_inventory(dict(active_observations=active, excluded_observations=excluded), params)


if __name__ == '__main__':
    unittest.main()
