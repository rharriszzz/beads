"""User follow-up: stop at first photographic darkness, never seek beyond it."""
import unittest
from dataclasses import replace
import numpy as np
from matplotlib.colors import rgb_to_hsv
from . import repaired_detect as new
from . import straight_detect_r265 as before

class FirstDarkTests(unittest.TestCase):
    def test_neutral_darkness_always_stops_even_without_peak_drop(self):
        for peak,dark in [(82,41),(100,50),(90,45),(110,55),(220,0),(220,1),(220,40)]:
            for hue in [0,.12,.6,.9]:
                v=np.array([[peak,dark,220]],np.uint8)
                hsv=np.array([[[hue,.06,d/255] for d in v[0]]])
                _,t=new.grow(v,hsv,(0,0))
                self.assertEqual([a[0] for a in t['accepted']],[0])
                self.assertEqual(t['stops'][0][7],'dark-frontier')
                self.assertEqual(t['stop_details'][0]['blocker'],[1,0])
                self.assertNotIn(2,[s[0] for s in t['stops']]) # no subsequent bright search
    def test_old_low_contrast_dark_exception_is_removed(self):
        v=np.array([[60,30,20]],np.uint8);h=rgb_to_hsv(np.repeat(v[:,:,None],3,axis=2)/255)
        _,a=before.grow(v,h,(0,0));_,b=new.grow(v,h,(0,0))
        self.assertIn([1,0],[r[:2] for r in a['accepted']]);self.assertEqual(len(b['accepted']),1)
    def test_low_gray_reflection_is_preserved(self):
        v=np.array([[60,45,30,200]],np.uint8);h=rgb_to_hsv(np.repeat(v[:,:,None],3,axis=2)/255)
        _,t=new.grow(v,h,(0,0));self.assertEqual([r[3] for r in t['accepted']],[60,45])
        self.assertEqual(t['stops'][0][3],30)
        with self.assertRaises(ValueError):new.grow(np.zeros((1,1),np.uint8),np.zeros((1,1,3)),(0,0))

    def test_dim_chromatic_sample_is_not_called_neutral_black(self):
        v=np.array([[100,80]],np.uint8);hsv=np.array([[[.02,.8,100/255],[.02,.8,80/255]]])
        _,t=new.grow(v,hsv,(0,0));self.assertEqual(len(t['accepted']),2)
        self.assertEqual(t['neutral_path_fraction'],[0.,0.])

    def test_just_above_dark_remains_eligible(self):
        v=np.array([[100,90,82]],np.uint8);h=rgb_to_hsv(np.repeat(v[:,:,None],3,axis=2)/255)
        _,t=new.grow(v,h,(0,0));self.assertEqual(len(t['accepted']),3)
    def test_nonzero_black_stop_is_irreversible_in_2d(self):
        v=np.array([[100,95,90],[41,40,39],[180,190,200]],np.uint8)
        h=rgb_to_hsv(np.repeat(v[:,:,None],3,axis=2)/255)
        _,t=new.grow(v,h,(0,0));self.assertTrue(all(a[1]==0 for a in t['accepted']))

if __name__=='__main__':unittest.main()
