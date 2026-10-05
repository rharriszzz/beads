"""Adverse interior controls: a colored bridge and neutral reflections."""
import os
import unittest

os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-segmentation-mpl')

import numpy as np
from matplotlib.colors import hsv_to_rgb

from trim_colored_masks import diffuse_fields, trim_region


class ColoredTrimmingTests(unittest.TestCase):
    def test_brighter_same_color_neighbor_across_dark_bridge_is_excluded(self):
        yy, xx = np.indices((101, 141))
        target = (xx-40)**2+(yy-50)**2 <= 20**2
        neighbor = (xx-80)**2+(yy-50)**2 <= 16**2
        bridge = (xx>=59)&(xx<=65)&(abs(yy-50)<=1)
        candidate = (target|neighbor|bridge)&(np.hypot(xx-40, yy-50)<=34)
        for hue in (350, 27, 210):
            with self.subTest(hue=hue):
                hsv = np.zeros((101, 141, 3), np.float32)
                hsv[...,0], hsv[...,1], hsv[...,2] = hue/360, .8, .08
                hsv[target,2], hsv[neighbor,2], hsv[bridge&~target&~neighbor,2] = .72, .92, .18
                image = (hsv_to_rgb(hsv)*255).astype(np.uint8)
                arrays = {'reflections':np.zeros(candidate.shape,np.int32)}
                diffuse, smooth = diffuse_fields(image, arrays, 40)
                result = trim_region(candidate, candidate, diffuse, smooth, (50,40), 40, 'stable')
                self.assertEqual(int((result&neighbor).sum()), 0)
                self.assertGreater((result&target).sum()/target.sum(), .70)
                self.assertFalse(np.any(result&~candidate))

    def test_neutral_reflections_remain_inside_supported_colored_face(self):
        yy, xx = np.indices((101, 121))
        target = (xx-50)**2+(yy-50)**2 <= 20**2
        tail = (xx>=69)&(xx<=84)&(abs(yy-50)<=2)
        candidate = target|tail
        hsv = np.zeros((101,121,3),np.float32)
        hsv[...,0], hsv[...,1], hsv[...,2] = 350/360, .8, .08
        hsv[target,2], hsv[tail&~target,2] = .72, .17
        reflections = np.zeros(target.shape,np.int32)
        for ident, (x,y) in enumerate(((46,48),(55,53)),1):
            spot=(xx-x)**2+(yy-y)**2<=4
            hsv[spot,0],hsv[spot,1],hsv[spot,2]=0,.03,1
            reflections[spot]=ident
        image=(hsv_to_rgb(hsv)*255).astype(np.uint8)
        original=reflections.copy()
        diffuse,smooth=diffuse_fields(image, {'reflections':reflections},40)
        result=trim_region(candidate,candidate,diffuse,smooth,(50,50),40,'stable')
        self.assertTrue(np.all(result[reflections>0]))
        self.assertFalse(np.any(result&tail&~target))
        self.assertGreater((result&target).sum()/target.sum(),.70)
        self.assertTrue(np.array_equal(reflections,original))


if __name__ == '__main__':
    unittest.main()
