"""Native feature localization checks, not complete bead-identity guarantees."""
import unittest
from copy import deepcopy
import json
from pathlib import Path
import numpy as np
from recover_local_reflections import apply_local_answers, native_peaks


class NativeReflectionTests(unittest.TestCase):
    def test_weak_peak_near_stronger_peak_and_native_origin(self):
        yy,xx=np.indices((65,65))
        value=.08+.08*np.exp(-((xx-25)**2+(yy-30)**2)/(2*1.4**2))
        value+=.7*np.exp(-((xx-41)**2+(yy-30)**2)/(2*2**2))
        rgb=np.repeat((value*255)[:,:,None],3,axis=2)
        peaks=native_peaks(rgb,np.array([100,200]))
        weak=min(peaks,key=lambda p:np.linalg.norm(np.array(p['xy'])-[125,230]))
        np.testing.assert_allclose(weak['xy'],[125,230],atol=.7)
        self.assertGreaterEqual(len(weak['scale_matches']),3)
        self.assertGreater(weak['positive_peak_surround_contrast'],.04)
        self.assertLess(weak['threshold_sensitivity_pixels'],.5)
        for y,lo,hi in weak['pixel_runs']:
            self.assertTrue(200<=y<265 and 100<=lo<=hi<165)

    def test_flat_image_has_no_peaks(self):
        self.assertEqual(native_peaks(np.ones((40,40,3))*32,np.array([0,0])),[])

    def test_filter_maximum_without_raw_positive_peak_remains_unresolved(self):
        value=np.full((51,51),.55)
        value[24:27,24:27]=.8;value[25,25]=.5
        rgb=np.repeat((value*255)[:,:,None],3,axis=2)
        peaks=native_peaks(rgb,np.array([0,0]))
        self.assertTrue(peaks)
        unsupported=[p for p in peaks if p['positive_peak_surround_contrast']<=0]
        self.assertTrue(unsupported)
        self.assertTrue(all(p['localization_status'].startswith('unresolved') for p in unsupported))
        # Retain the feature as a diagnostic witness, not a positive reflection.
        self.assertTrue(all(p['pixels']>=1 for p in unsupported))

    def test_review_promotes_exact_patch_and_excludes_only_D_reflections(self):
        root=Path(__file__).resolve().parents[1]
        prior=json.loads((root/'photo2/review/r193/trusted-facts.json').read_text())
        report=json.loads((root/'photo2/review/r196/report.json').read_text())
        answer=json.loads((root/'photo2/D-interior-answers-r197-r198.json').read_text())
        before=deepcopy(prior);facts=apply_local_answers(prior,report,answer)
        self.assertEqual(prior,before)
        self.assertEqual(len(facts['region_facts']),12)
        self.assertEqual(facts['region_facts'][-1]['region']['pixels'],13)
        self.assertEqual(facts['region_facts'][-1]['region'],report['assisted_sampling_patch']['region'])
        self.assertEqual(facts['black_reflection_point_facts'],prior['black_reflection_point_facts'])
        self.assertEqual(len(facts['negative_reflection_facts']),2)
        self.assertFalse(facts['complete'])
        changed=deepcopy(answer);changed['answers']['Q196.2']['region']['pixels']+=1
        with self.assertRaisesRegex(ValueError,'sampling pixels'):
            apply_local_answers(prior,report,changed)


if __name__=='__main__': unittest.main()
