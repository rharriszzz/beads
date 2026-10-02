"""Checks for precise answer scope and diagnostic ownership accounting."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

import numpy as np

from audit_bead_evidence import apply_ownership_answers, confirmed_ledger, diagnose_records


class OwnershipAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[1]
        folder = root / 'photo2/review/r192'
        cls.data = json.loads((folder / 'candidates.json').read_text())
        cls.prior = json.loads((folder / 'trusted-facts.json').read_text())
        cls.summary = json.loads((folder / 'summary.json').read_text())
        cls.answer = json.loads((root / 'photo2/interiors-confirmed-r193.json').read_text())
        cls.ownership = json.loads((root / 'photo2/ownership-answers-r194-r195.json').read_text())
        cls.photo_audit = json.loads((root / 'photo2/review/r193/photo-audit.json').read_text())

    def test_exact_six_confirmations_preserve_candidate_and_prior_evidence(self):
        data_before = deepcopy(self.data); prior_before = deepcopy(self.prior)
        facts = confirmed_ledger(self.data, self.prior, self.answer, self.summary)
        self.assertEqual(facts['accepted_observations'], [959, 566, 565, 561, 558, 557])
        self.assertEqual(len(facts['region_facts']), 11)
        self.assertEqual(len(facts['black_reflection_point_facts']), 6)
        self.assertFalse(facts['complete'])
        rows = {r['observation_number']: r for r in self.data['records']}
        for fact in facts['region_facts'][5:]:
            self.assertEqual(fact['region'], rows[fact['observation_number']]['region'])
            self.assertNotIn('maker_number', fact)
        self.assertEqual(self.data, data_before)
        self.assertEqual(self.prior, prior_before)

    def test_changed_identity_target_or_answer_cannot_promote_regions(self):
        for change in ['identity', 'target', 'appearance', 'answer']:
            with self.subTest(change=change):
                answer = deepcopy(self.answer)
                question = answer['questions']['Q192.1']
                if change == 'identity': question['observations'][0]['observation_id'] = 'changed'
                elif change == 'target': question['observations'][0]['observation_number'] = 960
                elif change == 'appearance': question['observations'][0]['appearance'] = 'red'
                else: question['answer'] = 'Cannot tell'
                with self.assertRaises(ValueError):
                    confirmed_ledger(self.data, self.prior, answer, self.summary)

    def test_mixed_false_black_duplicate_and_excluded_bodies_stay_in_accounting(self):
        labels = np.full((24, 48), -1)
        labels[2:22, 2:20] = 0
        labels[2:22, 22:40] = 2
        labels[2:22, 42:46] = 3
        def row(number, seed, kind, region=None, status='region-proposal', reflection=None):
            return dict(observation_number=number, seed_xy=seed, kind=kind,
                        source='independent test image', status=status, region=region, reflection=reflection)
        # Two patches of body0, one with a false black label; body2 has only a
        # cross-background patch and an excluded seed. Body3 has no seed at all.
        records = [
            row(1, [8, 8], 'chromatic', dict(pixel_runs=[[8, 8, 10]])),
            row(2, [12, 8], 'dark-reflection', dict(pixel_runs=[[8, 12, 14]]),
                reflection=dict(xy=[13, 8])),
            row(3, [22, 10], 'dark-reflection', dict(pixel_runs=[[10, 19, 23]])),
            row(4, [28, 10], 'chromatic', status='excluded-edge-uncertainty'),
        ]
        diagnostic = diagnose_records(records, labels, [0, 2, 3])
        self.assertEqual(diagnostic['eligible_single_body_located'], 1)
        self.assertEqual(diagnostic['eligible_correct_kind_with_3px_pixel_margin'], 1)
        self.assertEqual(diagnostic['duplicate_groups'], [dict(body=0, observations=[1, 2])])
        self.assertFalse(diagnostic['observations'][1]['reflection_on_black'])
        self.assertFalse(diagnostic['observations'][2]['single_body'])
        self.assertEqual(diagnostic['miss_reasons'], {
            'seed present; no single-body region': 1, 'no accepted seed on visible body': 1})
        excluded_only = diagnose_records(records[:2] + records[3:], labels, [0, 2, 3])
        self.assertEqual(excluded_only['miss_reasons']['only seed(s) excluded by provisional edge guard'], 1)

    def test_identity_answers_do_not_invent_regions_or_reflections(self):
        before = confirmed_ledger(self.data, self.prior, self.answer, self.summary)
        facts = apply_ownership_answers(before, self.data, self.ownership, self.photo_audit)
        self.assertEqual(facts['region_facts'], before['region_facts'])
        self.assertEqual(facts['black_reflection_point_facts'], before['black_reflection_point_facts'])
        self.assertNotIn('distinct_body_point_groups', before)
        self.assertEqual([f.get('observation_number') for f in facts['other_point_facts'][-3:-1]], [119, 960])
        gap = facts['confirmed_coverage_gaps'][0]
        self.assertEqual(gap['xy'], [241, 1272])
        self.assertEqual(gap['reflection_status'], 'unresolved')
        self.assertNotIn('observation_number', gap)
        self.assertFalse(facts['complete'])
        altered = deepcopy(self.ownership)
        altered['answers']['Q193.2']['points'][0]['xy'][0] += 1
        with self.assertRaisesRegex(ValueError, 'pictured points'):
            apply_ownership_answers(before, self.data, altered, self.photo_audit)


if __name__ == '__main__':
    unittest.main()
