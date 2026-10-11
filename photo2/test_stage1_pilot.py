"""Tests of scientific accounting, not of the provisional photo interpretation."""
import copy
import unittest

from photo2.stage1_pilot import (
    BUNDLE, assemble_candidates, apply_evaluation_amendments, contains,
    evaluate, read, reference_records,
)


class PilotAccountingTests(unittest.TestCase):
    def setUp(self):
        self.protocol = read(BUNDLE/'protocol.json')
        self.raw = read(BUNDLE/'reference-input.json')
        self.refs = reference_records(self.protocol, self.raw)

    def fixture(self):
        base = copy.deepcopy(next(r for r in self.refs if r['eligibility']=='eligible'))
        base.update(observation_id='D3-B01',color='red')
        deferred = dict(base,observation_id='D3-B02',color='black',eligibility='deferred_black')
        unknown = dict(base,observation_id='D3-B03',color='unknown',eligibility='uncertain_color')
        return [base,deferred,unknown]

    def test_deferred_black_and_uncertain_not_silent_misses(self):
        report=evaluate(self.fixture(),{'sections':{'D3':[]}}, {})
        s=report['summary']['D3']
        self.assertEqual((s['eligible'],s['missed'],s['deferred_no_reflection'],s['reference_uncertain']),(1,1,1,1))
        self.assertFalse(s['automatic_local_gate_passed'])

    def test_duplicate_wrong_color_and_false_positive_accounting(self):
        points=[dict(candidate_id=f'D3-P{i:02d}',color=c,xy=[1,2],role='test interior',reflection_xy=None)
                for i,c in enumerate(['red','red','yellow','black'],1)]
        decisions={p['candidate_id']:dict(status='supported',observation_id='D3-B01',reason='test') for p in points}
        decisions['D3-P04']=dict(status='false_positive',observation_id=None,reason='test paper feature')
        s=evaluate(self.fixture(),{'sections':{'D3':points}},decisions)['summary']['D3']
        self.assertEqual((s['correctly_detected'],s['missed'],s['duplicate_proposals'],s['incorrect_colors'],s['false_positives']),(1,0,1,1,1))
        s=evaluate(self.fixture(),{'sections':{'D3':[points[2]]}},{'D3-P03':decisions['D3-P03']})['summary']['D3']
        self.assertEqual((s['correctly_detected'],s['missed'],s['incorrect_colors']),(0,1,1))

    def test_every_candidate_requires_explicit_decision(self):
        point=dict(candidate_id='D3-P01',color='red',xy=[1,2],role='test',reflection_xy=None)
        with self.assertRaises(ValueError):evaluate(self.fixture(),{'sections':{'D3':[point]}},{})
        with self.assertRaises(ValueError):
            evaluate(self.fixture(),{'sections':{'D3':[point]}},
                     {'D3-P01':dict(status='supported',observation_id='D3-B03',reason='unknown cannot be truth')})

    def test_boundary_amendment_preserves_frozen_inputs_and_denominator(self):
        auto=assemble_candidates(self.protocol);before=copy.deepcopy((self.raw,auto))
        amendments=read(BUNDLE/'evaluation-amendments.json')
        refs,amended,audit=apply_evaluation_amendments(self.protocol,self.raw,auto,amendments)
        self.assertEqual((self.raw,auto),before)
        self.assertEqual(len(refs),len(self.refs)+len(amendments['reference_additions']))
        self.assertEqual(sum(map(len,amended['sections'].values())),sum(map(len,auto['sections'].values()))+5)
        self.assertEqual(sum(a['association'] is not None for a in audit),5)
        self.assertTrue(all(r['physical_center_xyz'] is None and r['bead_index'] is None for r in refs))

    def test_coordinates_are_half_open_and_reference_uncertainty_retained(self):
        self.assertTrue(contains([10,20,30,40],[10,20]))
        self.assertFalse(contains([10,20,30,40],[30,25]))
        r=next(r for r in self.refs if r['observation_id']=='H1-B13')
        self.assertLess(r['visible_fraction_range'][0],.1)
        self.assertGreater(r['visible_fraction_range'][1],.1)
        self.assertEqual(r['eligibility'],'threshold_uncertain')


if __name__=='__main__':unittest.main()
