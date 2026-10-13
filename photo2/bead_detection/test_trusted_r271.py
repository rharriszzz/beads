import unittest
import numpy as np
from .trusted_r271 import detect,Criteria

def scene(shift=(0,0),dim=False,twin=False,small=False):
    yy,xx=np.mgrid[:80,:100];x=45+shift[0];y=40+shift[1]
    rgb=np.full((80,100,3),[175,90,160],np.uint8)
    d=(xx-x)**2+(yy-y)**2;body=d<14**2
    bright=np.exp(-d/(2*(1 if small else 5)**2))
    if twin:bright=np.maximum(np.exp(-((xx-x-4)**2+(yy-y)**2)/50),np.exp(-((xx-x+4)**2+(yy-y)**2)/50))
    color=np.array([.95,.83,.42])*(.22+.78*bright[...,None])
    if dim:color*=.38
    rgb[body]=np.rint(255*color[body]).astype(np.uint8)
    return rgb

class TrustedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.rows,cls.traces,cls.summary,_,_=detect(scene())
    def test_clear_patch_nonvacuous(self):
        accepted=[r for r in self.rows if r['trusted']]
        self.assertEqual(len(accepted),1);self.assertEqual([accepted[0]['x'],accepted[0]['y']],[45,40])
    def test_dim_location_excluded_automatically(self):
        rows,*_=detect(scene(dim=True));self.assertFalse(any(r['trusted'] for r in rows))
        self.assertTrue(any('insufficient-light' in r['reasons'] for r in rows))
    def test_tiny_highlight_excluded(self):
        rows,*_=detect(scene(small=True));self.assertFalse(any(r['trusted'] for r in rows))
    def test_competing_highlights_withheld(self):
        rows,*_=detect(scene(twin=True));self.assertFalse(any(r['trusted'] for r in rows))
        self.assertTrue(any('competing-highlights' in r['reasons'] for r in rows))
    def test_uniform_background_has_no_trusted(self):
        rows,*_=detect(np.full((80,100,3),[180,80,160],np.uint8));self.assertFalse(any(r['trusted'] for r in rows))
    def test_translation_no_coordinate_prior(self):
        rows,*_=detect(scene((7,-3)));accepted=[(r['x'],r['y']) for r in rows if r['trusted']]
        self.assertEqual(accepted,[(52,37)])
    def test_rejections_have_plain_reasons(self):
        for r in self.rows:self.assertEqual(r['trusted'],not bool(r['reasons']));self.assertEqual(len(r['reasons']),len(r['explanations']))
    def test_criteria_monotone_light_floor(self):
        rows,*_=detect(scene(),criteria=Criteria(minimum_mean_y=.99));self.assertFalse(any(r['trusted'] for r in rows))
    def test_saved_paths_have_exact_endpoints(self):
        for t in self.traces:
            self.assertEqual(len(t['searches']),18)
            for r in t['searches']:
                self.assertEqual([r['path'][-1]['x'],r['path'][-1]['y']],r['endpoint'])

if __name__=='__main__':unittest.main()
