"""Exact point identity promotion must not approve unpictured geometry."""
import copy
import json
from pathlib import Path
import unittest
from record_transferred_profile_answer import bind_answer


class TransferredAnswerChecks(unittest.TestCase):
    def setUp(self):
        root=Path(__file__).resolve().parent
        self.manifest=json.loads((root/'profile-transfer-question-r208.json').read_text())
        self.answer=json.loads((root/'profile-transfer-answer-r209.json').read_text())
        self.proposal=json.loads((root/'review/r208/question-proposal.json').read_text())

    def test_only_the_two_point_identities_are_confirmed(self):
        facts=bind_answer(self.manifest,self.proposal,self.answer)
        self.assertEqual(facts['confirmed_distinct_yellow_points'],self.answer['points'])
        for flag in ['safe_regions_confirmed','exact_centers_measured','adjacency_inferred','reference_origin_alias_confirmed']:
            self.assertFalse(facts[flag])

    def test_changed_points_reference_or_reply_cannot_inherit_the_answer(self):
        answer=copy.deepcopy(self.answer); answer['points'][0]['xy'][0]+=1
        with self.assertRaises(ValueError): bind_answer(self.manifest,self.proposal,answer)
        answer=copy.deepcopy(self.answer); answer['answer']='Unanswered'
        with self.assertRaises(ValueError): bind_answer(self.manifest,self.proposal,answer)
        proposal=copy.deepcopy(self.proposal); proposal['observation_id']='Other reference'
        with self.assertRaises(ValueError): bind_answer(self.manifest,proposal,self.answer)


if __name__=='__main__': unittest.main()
