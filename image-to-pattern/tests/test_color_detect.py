import sys
from pathlib import Path
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from image_to_pattern import color_detect


class ColorDetectTests(unittest.TestCase):
    def test_kmeans_palette_lab(self):
        colors = np.array(
            [[255, 0, 0]] * 50
            + [[0, 255, 0]] * 50
            + [[0, 0, 255]] * 50,
            dtype=float,
        )
        pal = color_detect.kmeans_palette_lab(colors, k=3, iters=5, restarts=3)
        self.assertEqual(pal.shape, (3, 3))

    def test_label_image_by_palette(self):
        img = np.zeros((2, 2, 3), dtype=float)
        img[0, 0] = [255, 0, 0]
        img[0, 1] = [0, 255, 0]
        palette = np.array([[255, 0, 0], [0, 255, 0]], dtype=float)
        labels = color_detect.label_image_by_palette(img, palette)
        self.assertEqual(labels[0, 0], 0)
        self.assertEqual(labels[0, 1], 1)

    def test_most_separable_labels(self):
        palette = np.array([[255, 0, 0], [0, 255, 0], [10, 10, 10]], dtype=float)
        idxs = color_detect.most_separable_labels(palette, top_n=2)
        self.assertEqual(len(idxs), 2)


if __name__ == "__main__":
    unittest.main()
