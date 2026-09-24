"""Seed jitter, region merges, unsupported bodies and index-origin controls."""
import unittest

import numpy as np

from local_patch import assess
from region_anchors import (apply_gate, correspondence, interior_distances,
                            legacy_gate, region_gate)
from region_anchor_audit import anchor_diagnostics, summarize, variants


class RegionAnchorTests(unittest.TestCase):
    def setUp(self):
        self.labels=np.zeros((150,150),np.int32)
        for x,y,label in [(20,20,100),(80,20,101),(20,80,106),(80,80,107)]:
            self.labels[y:y+40,x:x+40]=label
        self.anchors=np.array([(21,40),(81,40),(21,100),(81,100)],float)
        self.rgb=np.full((150,150,3),100,np.uint8)
        self.objects=assess(self.labels,np.zeros(self.labels.shape),self.anchors,'gray',self.rgb)['objects']

    def gate(self,observed=None,objects=None,anchors=None):
        observed=self.labels if observed is None else observed
        objects=self.objects if objects is None else objects
        anchors=self.anchors if anchors is None else anchors
        return region_gate(observed,anchors,correspondence(observed,self.labels,objects))

    def test_near_edge_clicks_stable_within_observed_regions(self):
        first=self.gate()
        moved=self.gate(anchors=self.anchors+[6,0])
        self.assertTrue(first['anchor_ok'])
        self.assertEqual(first,moved)
        self.assertFalse(legacy_gate(self.labels,self.anchors,interior_distances(self.labels))['anchor_ok'])

    def test_three_beads_need_two_families_not_all_three(self):
        gate=self.gate(anchors=self.anchors[:3])
        self.assertTrue(gate['anchor_ok'])
        self.assertEqual(gate['anchor_families'],[1,6])

    def test_equal_merge_and_split_abstain(self):
        merged=self.labels.copy(); merged[merged==101]=100
        self.assertFalse(self.gate(observed=merged)['anchor_ok'])
        split=self.labels.copy(); split[20:60,40:60]=200
        self.assertFalse(self.gate(observed=split)['anchor_ok'])

    def test_no_snapping_background_duplicates_and_unsupported_fail(self):
        for point in [(19,40),(-5,40),(151,40),tuple(self.anchors[1])]:
            anchors=self.anchors.copy();anchors[0]=point
            self.assertFalse(self.gate(anchors=anchors)['anchor_ok'])
        objects=[dict(o,supported=False) if o['model_label']==100 else o for o in self.objects]
        self.assertFalse(self.gate(objects=objects)['anchor_ok'])

    def test_legacy_gate_matches_original_assessment(self):
        interiors=interior_distances(self.labels)
        for _,anchors in variants(self.anchors+[10,0]):
            for count in (3,4):
                original=assess(self.labels,np.zeros(self.labels.shape),anchors[:count],'gray',self.rgb)
                gate=legacy_gate(self.labels,anchors[:count],interiors)
                for key in ('anchor_labels','anchor_edges','anchor_families','anchor_margins','anchor_ok'):
                    self.assertEqual(original[key],gate[key])

    def test_indices_follow_matched_region_not_raw_click_model_label(self):
        observed=self.labels.copy()
        # A small extension is still a valid region. Click lies outside prediction.
        observed[35:45,17:20]=100
        anchors=self.anchors.copy();anchors[0]=[18,40]
        gate=self.gate(observed=observed,anchors=anchors)
        self.assertTrue(gate['anchor_ok'])
        result=apply_gate(self.objects,gate)
        self.assertEqual([o['relative_index'] for o in result['objects']],[0,1,6,7])

    def test_jitter_does_not_reset_evaluation_origin(self):
        evaluation=dict(all_model=dict(missing_truth=[],eligible_truth=1),records=[
            dict(model_label=106,truth_label=401,supported=True,matched=True,
                 eligible_truth=True,actual_relative_index=6,correct_color=True,color='red')])
        correct=summarize(evaluation,dict(anchor_ok=True,anchor_labels=[100]))
        shifted=summarize(evaluation,dict(anchor_ok=True,anchor_labels=[101]))
        self.assertEqual(correct['correct_region_color_index'],1)
        self.assertEqual(shifted['wrong_index'],1)

    def test_anchor_slip_is_reported_even_with_correct_origin(self):
        evaluation=dict(records=[dict(model_label=100,truth_label=401,matched=True),
                                 dict(model_label=106,truth_label=407,matched=True)])
        observed=dict(records=[dict(model_label=8,truth_label=401,matched=True),
                               dict(model_label=9,truth_label=407,matched=True)])
        gate=dict(anchor_labels=[100,106],observed_labels=[8,9])
        result=anchor_diagnostics(evaluation,observed,gate,[401,408])
        self.assertFalse(result['all_model_anchors_correct'])
        self.assertFalse(result['all_observed_anchors_correct'])
        self.assertTrue(result['anchors'][0]['model_correct'])


if __name__=='__main__':unittest.main()
