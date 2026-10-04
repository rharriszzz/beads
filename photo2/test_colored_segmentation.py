"""Adverse reflection controls, independent of manually labeled photo beads."""
import unittest
import numpy as np
from segment_colored_beads import reflection_regions


class ReflectionSegmentationTests(unittest.TestCase):
    def setUp(self):
        self.hsv = np.zeros((81,81,3),np.float32)
        self.hsv[...,0] = .05; self.hsv[...,1] = .8; self.hsv[...,2] = .12
        self.band = np.ones((81,81),bool)
        self.border = np.zeros((81,81),bool); self.border[:5] = True
        self.yy,self.xx = np.indices((81,81))

    def test_compact_neutral_highlight_is_localized_not_expanded_to_body(self):
        truth = (self.xx-40)**2+(self.yy-40)**2 <= 9
        self.hsv[truth,1] = .05; self.hsv[truth,2] = .96
        labels, rows, _ = reflection_regions(self.hsv,self.band,24.,self.border,.03)
        self.assertEqual(len(rows),1)
        self.assertLess(np.linalg.norm(np.asarray(rows[0]['xy'])-[40,40]),.1)
        self.assertTrue(np.all(truth[labels>0]))
        self.assertLessEqual(rows[0]['pixels'],truth.sum())

    def test_bright_saturated_diffuse_blob_is_not_a_specular_reflection(self):
        self.hsv[...,2] += .75*np.exp(-((self.xx-40)**2+(self.yy-40)**2)/32)
        labels, rows, _ = reflection_regions(self.hsv,self.band,24.,self.border,.03)
        self.assertEqual(len(rows),0)
        self.assertFalse(labels.any())


if __name__ == '__main__':
    unittest.main()
