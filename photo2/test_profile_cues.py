"""Hue/chroma and ownership controls for parallel feature diagnostics."""
import unittest
import numpy as np

from bead_profile_cues import trace_cues, parallel_cues
from review_profile_cues import truth_at, evaluate_profiles


class ProfileCueChecks(unittest.TestCase):
    def test_hue_wrap_is_a_small_signed_change(self):
        hsv=np.ones((81,3)); hsv[:40,0]=359/360; hsv[40:,0]=1/360
        result=trace_cues(hsv,20)
        self.assertLess(np.max(np.abs(result['signed_hue_change_degrees'])),2.001)
        self.assertGreater(max(result['signed_hue_change_degrees']),1.99)
        self.assertFalse(any(e['kind']=='V trough' for e in result['events']))

    def test_neutral_or_black_hue_supplies_no_evidence(self):
        for saturation,value in [(0.,1.),(1.,0.)]:
            hsv=np.column_stack([np.linspace(0,1,81),np.full(81,saturation),np.full(81,value)])
            result=trace_cues(hsv,20)
            np.testing.assert_allclose(result['hue_score'],0.)
            self.assertFalse(any(e['kind']=='hue change' for e in result['events']))

    def test_persistent_shading_and_glint_can_both_be_inside_one_body(self):
        x=np.arange(160); shade=.5*np.exp(-((x-60)/4)**2); glint=np.exp(-((x-110)/3)**2)
        rgb=np.zeros((80,160,3)); rgb[:,:,0]=1-shade
        rgb[:,:,1]=glint; rgb[:,:,2]=glint
        distances=np.arange(40,141); offsets=np.array([-4.,-2.,0.,2.,4.])
        coordinates=np.array([np.column_stack([distances,np.full(len(distances),40+o)]) for o in offsets])
        result=parallel_cues(rgb,coordinates,20,offsets,50)
        base=result['paths'][result['base_path_index']]
        self.assertTrue(any(e['kind']=='V trough' and e['matched_paths']==5 for e in base['events']))
        self.assertTrue(any(e['kind']=='neutral bright feature' and e['matched_paths']==5 for e in base['events']))
        self.assertFalse(any(e['kind']=='hue change' for e in base['events']))
        row=dict(observation_number=1,**result)
        evaluation=evaluate_profiles(dict(records=[row],native_diameter=20),np.ones((80,160),int))
        self.assertGreater(evaluation['persistent_event_counts']['V trough']['within one body'],0)
        self.assertGreater(evaluation['persistent_event_counts']['neutral bright feature']['within one body'],0)
        self.assertTrue(all(w['owner_at_event']==1 for w in evaluation['witnesses']))
        self.assertFalse(any('owner' in e or 'black' in e for e in base['events']))

    def test_bilinear_mixed_and_outside_points_remain_explicit(self):
        labels=np.array([[1,2],[1,2]])
        owners,pure=truth_at([[0.,0.],[.5,.5],[-.1,0.],[1.,1.]],labels)
        np.testing.assert_array_equal(owners,[1,1,-2,2])
        np.testing.assert_array_equal(pure,[True,False,False,True])


if __name__=='__main__': unittest.main()
