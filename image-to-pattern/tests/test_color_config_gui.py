import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import color_config_gui as gui
import numpy as np

# Use a writable cache to avoid fontconfig warnings during tests
_TMP_CACHE = tempfile.mkdtemp()
os.environ.setdefault("MPLCONFIGDIR", _TMP_CACHE)
os.environ.setdefault("XDG_CACHE_HOME", _TMP_CACHE)


class ColorConfigGUITests(unittest.TestCase):
    def test_rectangles_to_hsv_set(self):
        img = np.zeros((4, 4, 3), dtype=np.uint8)
        img[1:3, 1:3, :] = [10, 20, 30]
        rects = [[1, 2, 1, 2]]
        hsv_set = gui.rectangles_to_hsv_set(img, rects)
        self.assertIn((10, 20, 30), hsv_set)
        self.assertEqual(len(hsv_set), 1)

    def test_mask_from_hsv_set(self):
        img = np.array(
            [
                [[0, 0, 0], [1, 1, 1]],
                [[2, 2, 2], [0, 0, 0]],
            ],
            dtype=np.uint8,
        )
        hsv_set = {(0, 0, 0)}
        mask = gui.mask_from_hsv_set(img, hsv_set)
        self.assertTrue(mask[0, 0])
        self.assertTrue(mask[1, 1])
        self.assertFalse(mask[0, 1])
        self.assertFalse(mask[1, 0])

    def test_hsv_swatch_image(self):
        vals = [(0, 255, 255), (120, 255, 255), (240, 255, 255)]
        swatch = gui.hsv_swatch_image(vals, max_cells=4)
        self.assertEqual(swatch.shape[2], 3)
        # Expect rows/cols sufficient for 3 values
        self.assertTrue(swatch.shape[0] * swatch.shape[1] >= 3)


if __name__ == "__main__":
    unittest.main()
