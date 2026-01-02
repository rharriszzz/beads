import sys
from pathlib import Path
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from image_to_pattern import palette


class PaletteTests(unittest.TestCase):
    def test_nearest_palette_indices(self):
        palette_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        samples = [
            (250, 10, 10),  # near red
            (5, 240, 5),  # near green
            (0, 0, 250),  # near blue
            (80, 200, 10),  # closer to green than red
        ]
        indices = palette.nearest_palette_indices(samples, palette_colors)
        self.assertEqual(indices, [0, 1, 2, 1])
        indices_lab = palette.nearest_palette_indices(samples, palette_colors, use_lab=True)
        self.assertEqual(indices_lab, [0, 1, 2, 1])

    def test_nearest_palette_indices_hsv(self):
        palette_colors = [(200, 0, 0), (0, 200, 0)]
        samples = [
            (220, 30, 30),  # red bright
            (120, 0, 0),    # red dark
            (10, 180, 10),  # green
        ]
        indices = palette.nearest_palette_indices_hsv(samples, palette_colors)
        self.assertEqual(indices, [0, 0, 1])

    def test_mean_palette_color(self):
        samples = [(10, 20, 30), (20, 30, 40), (30, 40, 50)]
        mean = palette.mean_palette_color(samples)
        self.assertTrue(np.allclose(mean, (20, 30, 40)))

    def test_kmeans_palette_and_indices(self):
        samples = (
            [(250, 5, 5)] * 10
            + [(5, 250, 5)] * 10
            + [(5, 5, 250)] * 10
            + [(250, 250, 5)] * 5
        )
        pal = palette.kmeans_palette(samples, k=3, iters=5, restarts=3, use_lab=True)
        self.assertEqual(len(pal), 3)
        idxs = palette.kmeans_indices(samples, k=3, iters=5)
        self.assertEqual(len(idxs), len(samples))
        # Allow missing a cluster due to randomness; assert at least 2
        self.assertGreaterEqual(len(set(idxs)), 2)

    def test_empty_palette_raises(self):
        with self.assertRaises(ValueError):
            palette.nearest_palette_indices([(0, 0, 0)], [])

    def test_empty_samples_mean_raises(self):
        with self.assertRaises(ValueError):
            palette.mean_palette_color([])


if __name__ == "__main__":
    unittest.main()
