import unittest
import numpy as np
from .strict_r260 import strict_stop,color_stop,retreat_mask,radial_mask


class StrictMonotonicTests(unittest.TestCase):
    def test_tiny_rise_stops_without_tolerance(self):
        self.assertEqual(strict_stop(np.array([1.,.9,.8,.800001,.6]),.3)[:2],(2,1))

    def test_equal_value_stops(self):
        self.assertEqual(strict_stop(np.array([1.,.9,.9,.5]),.3)[:2],(1,0))

    def test_retreat_excludes_dark_tail(self):
        profile=np.array([1.,.9,.8,.7,.6,.5,.4,.3,.2,.1,.2])
        end,keep,threshold=strict_stop(profile,.3)
        self.assertEqual(end,9);self.assertEqual(keep,6)
        self.assertTrue(np.all(profile[:keep+1]>threshold))
        self.assertTrue(np.all(profile[keep+1:end+1]<=threshold))

    def test_first_increase_retains_seed_only(self):
        self.assertEqual(strict_stop(np.array([.9,1.,.5]),.3)[:2],(0,0))

    def test_red_yellow_transition_both_directions_and_palette_rotation(self):
        for offset in [0.,.4,.93]:
            for hues in [[0.,.01,.12,.13],[.13,.12,.01,0.]]:
                hsv=np.c_[np.mod(np.array(hues)+offset,1),[.8]*4,[1.,.9,.8,.7]]
                event=color_stop(hsv)
                self.assertEqual(event['reason'],'relative-hue-change')
                self.assertEqual(event['index'],2)

    def test_red_hue_wrap_is_not_a_boundary(self):
        self.assertIsNone(color_stop(np.c_[[.98,.99,.01,.02],[.8]*4,[1.,.9,.8,.7]]))

    def test_low_saturation_hue_is_ignored(self):
        self.assertIsNone(color_stop(np.c_[[0.,.2,.4,.6],[.1]*4,[1.,.9,.8,.7]]))

    def test_one_sample_hue_noise_is_not_a_transition(self):
        self.assertIsNone(color_stop(np.c_[[0.,.12,.01,.02],[.8]*4,[1.,.9,.8,.7]]))

    def test_dark_color_loss_and_achromatic_reflection(self):
        for saturation in [[.8,.8,.2,.2],[.1,.1,.1,.1]]:
            event=color_stop(np.c_[[0.,0.,.4,.6],saturation,[.9,.6,.3,.25]])
            self.assertEqual(event['reason'],'dark-low-chroma-clue')
            self.assertEqual(event['index'],2)

    def test_dark_pixels_with_too_little_peak_contrast_are_not_a_clue(self):
        self.assertIsNone(color_stop(np.c_[[0.,.2,.4,.6],[.1]*4,[.3,.29,.28,.27]]))

    def test_retreat_removes_off_ray_dark_pixels_and_disconnected_island(self):
        value=np.ones((5,5));value[:,3]=.1;value[1,1]=.1
        mask=retreat_mask(np.ones((5,5),bool),value,[.3]*64,2,2,0,0)
        self.assertFalse(mask[1,1]);self.assertFalse(mask[:,4].any())
        self.assertTrue(mask[2,2]);self.assertTrue(np.all(value[mask]>.3))

    def test_shrinking_rays_never_add_pixels_even_with_zero_length_rays(self):
        rng=np.random.default_rng(260)
        for _ in range(100):
            outer=rng.integers(0,20,64);inner=rng.integers(0,outer+1)
            a=radial_mask(outer,25,25,0,0,(51,51))
            b=radial_mask(inner,25,25,0,0,(51,51))
            self.assertFalse((b&~a).any())


if __name__=='__main__':unittest.main()
