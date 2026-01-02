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

    def test_palette_from_hist_peaks(self):
        img = np.zeros((10, 20, 3), dtype=float)
        img[:, :10] = [255, 0, 0]
        img[:, 10:] = [0, 255, 0]
        mask = np.ones((10, 20), dtype=bool)
        palette = color_detect.palette_from_hist_peaks(
            img,
            mask=mask,
            max_colors=3,
            drop_background=False,
            h_bins=12,
            s_bins=4,
            min_prominence=0.05,
            radius_s=0.4,
            radius_v=0.6,
        )
        self.assertGreaterEqual(palette.shape[0], 2)

    def test_merge_close_hues(self):
        palette = np.array([[255, 0, 0], [250, 5, 5], [0, 255, 0]], dtype=float)
        counts = [100, 50, 80]
        merged, mapping = color_detect.merge_close_hues(palette, counts=counts, hue_tol=0.05, sat_tol=1.0, val_tol=1.0)
        self.assertLess(merged.shape[0], palette.shape[0])
        self.assertEqual(len(mapping), len(palette))


if __name__ == "__main__":
    unittest.main()
