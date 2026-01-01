import sys
from pathlib import Path
import unittest

import numpy as np
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from image_to_pattern import bead_detect


def synthetic_mask_grid(rows=3, cols=4, radius=5, spacing=15):
    h = rows * spacing + spacing
    w = cols * spacing + spacing
    mask = np.zeros((h, w), dtype=bool)
    yy, xx = np.ogrid[:h, :w]
    centers = []
    for r in range(rows):
        for c in range(cols):
            cx = spacing + c * spacing
            cy = spacing + r * spacing
            circle = (xx - cx) ** 2 + (yy - cy) ** 2 <= radius * radius
            mask[circle] = True
            centers.append((cx, cy))
    return mask, centers


class BeadDetectTests(unittest.TestCase):
    def test_detect_bead_centers(self):
        mask, centers = synthetic_mask_grid()
        beads = bead_detect.detect_bead_centers(mask, spacing_px=15, min_distance_scale=0.5)
        self.assertGreaterEqual(len(beads), len(centers) - 1)  # allow one miss
        xs = [b.center[0] for b in beads]
        ys = [b.center[1] for b in beads]
        self.assertTrue(all(0 <= x <= mask.shape[1] for x in xs))
        self.assertTrue(all(0 <= y <= mask.shape[0] for y in ys))


if __name__ == "__main__":
    unittest.main()
