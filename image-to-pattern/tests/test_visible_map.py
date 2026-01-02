import sys
from pathlib import Path
import unittest

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from image_to_pattern import visible_map


def synthetic_three_color_band(width=120, height=40):
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    spacing = 20
    radius = 6
    centers = []
    for i in range(5):
        cx = spacing + i * spacing
        cy = height // 2
        centers.append((cx, cy, i % 3))
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=colors[i % 3])
    return img, centers


class VisibleMapTests(unittest.TestCase):
    def test_build_visibility_map(self):
        img, centers = synthetic_three_color_band()
        vis = visible_map.build_visibility_map(img, expected_beads=5, num_peaks=3, min_coverage=0.0)
        self.assertEqual(len(vis), 5)
        visible_count = sum(1 for v in vis if v.visible)
        self.assertGreaterEqual(visible_count, 3)


if __name__ == "__main__":
    unittest.main()
