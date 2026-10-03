"""Point confirmation must not inherit whole-model or boundary certainty."""
import copy
import json
from pathlib import Path
import unittest
from record_correspondence_answer import bind_answer


class CorrespondenceAnswerTests(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).resolve().parent
        self.manifest = json.loads((root/'correspondence-question-r210.json').read_text())
        self.answer = json.loads((root/'correspondence-answer-r211.json').read_text())
        self.proposal = json.loads((root/'review/r210/question-proposal.json').read_text())

    def test_same_points_do_not_certify_geometry_or_region(self):
        facts = bind_answer(self.manifest, self.proposal, self.answer)
        self.assertEqual(facts['confirmed_same_bead_points'], self.manifest['points'])
        self.assertIsNone(facts['bead_index'])
        for key in ['safe_regions_confirmed', 'exact_centers_measured', 'predicted_visible_region_accepted',
                    'outward_geometry_measured', 'model_count_or_hand_confirmed', 'predicted_generator_index_confirmed']:
            self.assertFalse(facts[key])

    def test_changed_geometry_identity_or_reply_cannot_inherit_confirmation(self):
        answer = copy.deepcopy(self.answer); answer['points']['O'][0] += 1
        with self.assertRaises(ValueError): bind_answer(self.manifest, self.proposal, answer)
        proposal = copy.deepcopy(self.proposal); proposal['center_id'] = 'different center'
        with self.assertRaises(ValueError): bind_answer(self.manifest, proposal, self.answer)
        answer = copy.deepcopy(self.answer); answer['answer'] = 'V only'
        with self.assertRaises(ValueError): bind_answer(self.manifest, self.proposal, answer)


if __name__ == '__main__':
    unittest.main()
