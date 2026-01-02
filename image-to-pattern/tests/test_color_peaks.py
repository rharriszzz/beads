import sys
from pathlib import Path
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from image_to_pattern import color_peaks


class ColorPeaksTests(unittest.TestCase):
    def test_find_hs_peaks(self):
        img = np.zeros((10, 10, 3), dtype=float)
        img[:, :5] = [1.0, 0.0, 0.0]  # red-ish in HSV
        img[:, 5:] = [0.33, 1.0, 1.0]  # green-ish
        mask = np.ones((10, 10), dtype=bool)
        peaks = color_peaks.find_hs_peaks(img, mask, num_peaks=2, h_bins=10, s_bins=10)
        self.assertGreaterEqual(len(peaks), 2)

    def test_build_peak_masks(self):
        img = np.zeros((10, 10, 3), dtype=float)
        img[:, :5] = [0.0, 1.0, 1.0]  # H=0
        mask = np.ones((10, 10), dtype=bool)
        masks = color_peaks.build_peak_masks(img, mask, peaks=[(0.0, 1.0)], radius_h=0.1, radius_s=0.2, radius_v=0.5)
        self.assertEqual(len(masks), 1)
        self.assertTrue(masks[0][:, :5].all())
        self.assertFalse(masks[0][:, 5:].any())

    def test_auto_shrink_peak_masks(self):
        img = np.zeros((20, 20, 3), dtype=float)
        img[:, :10] = [0.0, 1.0, 1.0]
        img[:, 10:] = [0.5, 1.0, 1.0]
        mask = np.ones((20, 20), dtype=bool)
        peaks, radii = color_peaks.auto_shrink_peak_masks(img, mask, num_peaks=2, spacing_px=5.0)
        self.assertTrue(len(peaks) >= 1)


if __name__ == "__main__":
    unittest.main()
