"""Frozen photo regression plus owner-known synthetic evidence controls."""
import contextlib
import copy
import io
import tempfile
import unittest
from pathlib import Path
import numpy as np
from PIL import Image
from photo2.stage1_recovery import BUNDLE,ROOT,RULES,detect_section
from photo2.stage1_pilot import read,sha
from photo2.evaluate_stage1_recovery import score

class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.inputs=read(BUNDLE/'inputs.json')
        self.params=self.inputs['parameters']

    def toy(self,color=None,reflection=True,center=(50,50)):
        y,x=np.indices((110,110));cx,cy=center;r=np.hypot(x-cx,y-cy)
        rgb=np.full((110,110,3),[190,90,170],dtype=np.uint8)
        rgb[r<12]=[25,15,25] if color is None else color
        if reflection:rgb[r<3]=[235,225,230]
        section=dict(id='D3',box=[10,10,100,100],halo=[0,0,110,110],baseline=[],colored_pool=[],black_pool=[])
        return rgb,section

    def test_native_reflection_detected_after_translation(self):
        for center in [(35,45),(75,70)]:
            rgb,s=self.toy(center=center)
            result=detect_section(rgb,s,self.params)
            accepted=result['additions']
            self.assertEqual(len(accepted),1)
            self.assertLess(np.linalg.norm(np.array(accepted[0]['xy'])-center),2)

    def test_dark_body_without_reflection_is_not_promoted(self):
        rgb,s=self.toy(reflection=False)
        self.assertEqual(detect_section(rgb,s,self.params)['additions'],[])

    def test_colored_highlights_not_black_for_two_learned_palettes(self):
        for color,hue in [([225,120,25],27),([30,180,220],193)]:
            rgb,s=self.toy(color=color)
            params=copy.deepcopy(self.params);params['hue_modes_degrees']=[hue]
            self.assertEqual(detect_section(rgb,s,params)['additions'],[])

    def test_flat_paper_has_no_reflection(self):
        rgb,s=self.toy();rgb[:]=[190,90,170]
        self.assertEqual(detect_section(rgb,s,self.params)['additions'],[])

    def test_baseline_preserved_and_rejected_arm_does_not_use_native_search(self):
        rgb,s=self.toy();s['baseline']=[dict(source_id='test:1',xy=[50,50],color='black')]
        before=copy.deepcopy(s)
        r=detect_section(rgb,s,self.params)
        self.assertEqual(s,before);self.assertEqual(r['baseline'],before['baseline'])
        self.assertEqual(r['additions'],[])
        s['baseline']=[]
        self.assertEqual(detect_section(rgb,s,self.params,native=False)['additions'],[])

    def test_frozen_photo_reproduction_and_no_reference_inputs(self):
        freeze=read(BUNDLE/'freeze.json')
        self.assertEqual(sha(ROOT/'photo2/stage1_recovery.py'),freeze['script_sha256'])
        rgb=np.asarray(Image.open(ROOT/'beads-photo-2.jpg').convert('RGB'))
        for split in ['development','transfer']:
            doc=read(BUNDLE/split/'candidates.json')
            for expected in doc['results']:
                s=next(s for s in self.inputs['sections'] if s['id']==expected['section'])
                self.assertFalse(any('reference' in key or 'adjudication' in key for key in s))
                self.assertEqual(detect_section(rgb,s,self.params),expected)
                rejected=detect_section(rgb,s,self.params,native=False)
                self.assertEqual(rejected['additions'],[p for p in expected['additions'] if p['arm']=='rejected'])

    def test_accounting_retains_errors_unknowns_and_baseline(self):
        with tempfile.TemporaryDirectory() as temp,contextlib.redirect_stdout(io.StringIO()):
            result=score(output=Path(temp))
        self.assertEqual(result,read(BUNDLE/'summary.json'))
        final=result['arms']['native']['total']
        self.assertEqual(final['baseline_retained'],76)
        self.assertEqual((final['reference_uncertain'],final['deferred_no_reflection']),(13,6))
        self.assertFalse(result['passed'])
        self.assertGreater(final['false_positives'],0)
        self.assertGreater(final['duplicate_proposals'],0)
        self.assertGreater(final['incorrect_colors'],0)
        self.assertGreater(final['unresolved_candidates'],7)

if __name__=='__main__':unittest.main()
