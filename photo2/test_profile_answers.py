"""Maker answers bind point identities without certifying seams or centers."""
import copy
import json
from pathlib import Path
import unittest

from record_profile_answers import interpret


class ProfileAnswerChecks(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).resolve().parent
        self.manifest = json.loads((root/'profile-questions-r203.json').read_text())
        self.answers = json.loads((root/'profile-answers-r204-r205.json').read_text())
        self.report = json.loads((root/'review/r203/report.json').read_text())

    def test_distinct_bodies_and_reflection_do_not_certify_geometry(self):
        facts = interpret(self.manifest, self.report, self.answers)
        self.assertEqual([p['label'] for p in facts['yellow_distinct_points']], ['S', 'Q'])
        self.assertEqual(facts['confirmed_black_reflection_point']['label'], 'R')
        for flag in ['black_active_for_fitting', 'exact_regions_confirmed',
                     'exact_centers_measured', 'adjacency_inferred']:
            self.assertFalse(facts[flag])
        transition = facts['transition']
        self.assertEqual(transition['sample_count'], 21)
        self.assertEqual(transition['minimum_value_distance_pixels'], 11)
        self.assertAlmostEqual(transition['endpoint_hue_change_degrees'], 11.393579162330525)

    def test_changed_points_or_replies_cannot_inherit_confirmations(self):
        for question in ['Q203.1', 'Q203.2']:
            answers = copy.deepcopy(self.answers)
            answers['answers'][question]['points'][0]['xy'][0] += 1
            with self.assertRaises(ValueError):
                interpret(self.manifest, self.report, answers)
            answers = copy.deepcopy(self.answers)
            answers['answers'][question]['answer'] = 'Unanswered'
            with self.assertRaises(ValueError):
                interpret(self.manifest, self.report, answers)
        manifest = copy.deepcopy(self.manifest)
        manifest['questions']['Q203.1']['points'][0]['xy'][0] += 1
        with self.assertRaises(ValueError):
            interpret(manifest, self.report, self.answers)


if __name__ == '__main__':
    unittest.main()
