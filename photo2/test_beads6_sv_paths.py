"""Analytic controls for descriptive S/V paths, not tests of bead identity."""
import unittest
import numpy as np
from beads6_sv_paths import sv, sample_path, metrics


class PathControls(unittest.TestCase):
    def test_encoded_color_and_black(self):
        s,v = sv(np.array([[0.,0,0],[255,255,255],[255,0,0],[100,150,200]]))
        np.testing.assert_allclose(s,[0,0,1,.5])
        np.testing.assert_allclose(v,[0,255,255,200])

    def test_oblique_ramp_coordinates_and_offsets(self):
        y,x = np.indices((30,30))
        rgb = np.stack([2*x+y,x+3*y,4*x+2*y],axis=-1).astype(float)
        d,xy,p = sample_path(rgb,[[5,6],[13,12]],[-2,0,2],.3)
        self.assertEqual(d[-1],10)
        self.assertLessEqual(np.diff(d).max(),.3)
        np.testing.assert_allclose(xy[1,[0,-1]],[[5,6],[13,12]])
        np.testing.assert_allclose(xy[2]-xy[1],np.tile([-1.2,1.6],(len(d),1)))
        np.testing.assert_allclose(p[...,0],2*xy[...,0]+xy[...,1])
        np.testing.assert_allclose(p[...,1],xy[...,0]+3*xy[...,1])
        np.testing.assert_allclose(p[...,2],4*xy[...,0]+2*xy[...,1])

    def test_internal_highlight_is_large_s_change_without_valley(self):
        d = np.linspace(0,12,49)
        highlight = np.exp(-((d-6)/1.1)**2)
        rgb = np.stack([np.full_like(d,255),255*highlight,255*highlight],axis=-1)
        m = metrics(d,rgb,2)
        self.assertAlmostEqual(m['v_dip'],0)
        self.assertGreater(m['s_range'],.99)
        self.assertAlmostEqual(m['s_delta'],0)

    def test_shading_valley_can_mimic_seam_without_color_change(self):
        d = np.linspace(0,12,49)
        shade = 1-.4*np.exp(-((d-6)/1.1)**2)
        rgb = shade[:,None]*np.array([100,150,200])
        m = metrics(d,rgb,2)
        self.assertGreater(m['v_dip'],79)
        self.assertAlmostEqual(m['s_range'],0)
        self.assertAlmostEqual(m['v_dip_distance_px'],6)

    def test_invalid_paths_rejected(self):
        rgb = np.zeros((10,10,3))
        for ends,offsets in [([[1,1],[1,1]],[0]),([[0,0],[5,0]],[-2])]:
            with self.assertRaises(ValueError):
                sample_path(rgb,ends,offsets,.25)


if __name__=='__main__':
    unittest.main()
