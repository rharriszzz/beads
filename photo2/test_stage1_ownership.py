"""Owner-known controls and frozen accounting for the bounded R239 experiment."""
import copy
import tempfile
import unittest
from pathlib import Path
import numpy as np
from PIL import Image
from photo2.stage1_pilot import ROOT,read,sha
from photo2.stage1_ownership import BUNDLE,RULES,filter_section,ray_evidence
from photo2.evaluate_stage1_ownership import score


class OwnershipTests(unittest.TestCase):
    def setUp(self):
        self.params=read(ROOT/'photo2/review/r238/inputs.json')['parameters']
        self.d=self.params['native_diameter']

    def test_enclosure_rejects_rim_and_colored_highlight(self):
        yy,xx=np.indices((100,100));body=(xx-50)**2+(yy-50)**2<16**2
        v=np.full((100,100),.75);v[body]=.12;v[(xx-50)**2+(yy-50)**2<3**2]=.95
        empty=np.zeros(v.shape,bool)
        self.assertEqual(ray_evidence(v,empty,[50,50],self.d)['dark_rays'],16)
        self.assertLess(ray_evidence(v,empty,[34,50],self.d)['dark_rays'],12)
        color=body.copy();color[(xx-50)**2+(yy-50)**2<3**2]=False
        e=ray_evidence(v,color,[50,50],self.d)
        self.assertEqual(e['dark_rays'],0);self.assertEqual(e['color_first_rays'],16)

    def test_enclosure_translation_rotation(self):
        yy,xx=np.indices((120,120))
        for x,y in [(40,45),(72,67)]:
            v=np.full((120,120),.8);v[((xx-x)/16)**2+((yy-y)/12)**2<1]=.15
            v[(xx-x)**2+(yy-y)**2<3**2]=.9
            self.assertGreaterEqual(ray_evidence(v,np.zeros(v.shape,bool),[x,y],self.d)['dark_rays'],12)
            self.assertGreaterEqual(ray_evidence(v.T,np.zeros(v.shape,bool),[y,x],self.d)['dark_rays'],12)

    def section(self,points):
        return dict(section='S',box=[0,0,100,100],halo=[0,0,100,100],baseline=[],additions=[dict(source_id=str(i),candidate_id=f'S-A{i}',xy=xy,color='red',arm='test') for i,xy in enumerate(points)])

    def test_two_maxima_one_body_versus_two_bodies(self):
        yy,xx=np.indices((100,100));rgb=np.full((100,100,3),160,np.uint8)
        rgb[(xx-50)**2+(yy-50)**2<14**2]=[190,12,35]
        # Two brightness maxima on one known body cannot create two owners.
        for x in [44,56]:rgb[(xx-x)**2+(yy-50)**2<2**2]=[250,75,85]
        sec=self.section([[44,50],[56,50]]);original=copy.deepcopy(sec)
        out=filter_section(rgb,sec,self.params)
        self.assertEqual(sum(p['ownership_decision']=='retain' for p in out['proposals']),1)
        self.assertEqual(sec,original)
        # Two faces separated by a dark seam should remain two even at short spacing.
        rgb[:]=160
        for x in [38,62]:rgb[(xx-x)**2+(yy-50)**2<11**2]=[190,12,35]
        out=filter_section(rgb,self.section([[38,50],[62,50]]),self.params)
        self.assertEqual(sum(p['ownership_decision']=='retain' for p in out['proposals']),2)

    def test_close_black_features_abstain_without_owner_seam(self):
        yy,xx=np.indices((100,100));rgb=np.full((100,100,3),170,np.uint8)
        rgb[(xx-50)**2+(yy-50)**2<23**2]=[25,25,25]
        for x in [44,56]:rgb[(xx-x)**2+(yy-50)**2<2**2]=240
        sec=self.section([[44,50],[56,50]])
        for p in sec['additions']:p['color']='black'
        out=filter_section(rgb,sec,self.params)
        self.assertTrue(all(p['ownership_decision']=='abstain' for p in out['proposals']))
        self.assertTrue(out['pairs'])

    def test_frozen_photo_and_complete_accounting(self):
        freeze=read(BUNDLE/'freeze.json')
        self.assertEqual(sha(ROOT/'photo2/stage1_ownership.py'),freeze['script_sha256'])
        self.assertEqual(sha(BUNDLE/'references.json'),freeze['references_sha256'])
        self.assertEqual(sha(BUNDLE/'protocol.json'),freeze['protocol_sha256'])
        rgb=np.asarray(Image.open(ROOT/'beads-photo-2.jpg').convert('RGB'))
        for split in ['development','transfer']:
            before=read(BUNDLE/split/'r238.json');after=read(BUNDLE/split/'ownership.json')['results']
            for original,expected in zip(before,after):
                self.assertEqual(filter_section(rgb,original,self.params),expected)
                self.assertEqual(len(original['baseline'])+len(original['additions']),len(expected['proposals']))
        with tempfile.TemporaryDirectory() as td:
            result=score(td)
            self.assertEqual(result,read(BUNDLE/'summary.json'))
            self.assertEqual(result['development']['r238']['correctly_detected'],103)
            self.assertEqual(result['development']['ownership']['correctly_detected'],96)
            self.assertEqual(result['fresh_transfer']['ownership']['correctly_detected'],30)
            self.assertEqual(len(result['fresh_transfer']['lost_correct_bodies']),11)

if __name__=='__main__':unittest.main()
