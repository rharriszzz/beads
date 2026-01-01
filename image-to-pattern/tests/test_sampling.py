import sys
from math import sqrt
from pathlib import Path
import unittest

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from image_to_pattern import sampling, segmentation


def synthetic_beads(
    width=200,
    height=80,
    spacing=20,
    radius=8,
    band_top=30,
    colors=((255, 0, 0), (0, 255, 0), (0, 0, 255)),
):
    """Create a horizontal bracelet with colored beads on white background."""
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    centers = []
    x = radius
    color_idx = 0
    while x < width - radius:
        cx = x
        cy = band_top
        centers.append((cx, cy))
        draw.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            fill=colors[color_idx % len(colors)],
        )
        x += spacing
        color_idx += 1
    return img, centers, radius


class SamplingTests(unittest.TestCase):
    def test_positions_along_centerline_spacing(self):
        xs = list(range(0, 101, 1))
        ys = [10.0 for _ in xs]
        cl = segmentation.Centerline(xs=xs, ys=ys)
        positions = sampling.positions_along_centerline(cl, spacing_px=10.0, offset_px=0.0)
        # Expect roughly length/spacing positions
        self.assertTrue(9 <= len(positions) <= 11)
        self.assertAlmostEqual(positions[0][0], 0.0, delta=0.5)
        self.assertAlmostEqual(positions[-1][0], 100.0, delta=0.5)

    def test_positions_offset(self):
        xs = [0, 100]
        ys = [0, 0]
        cl = segmentation.Centerline(xs=xs, ys=ys)
        positions = sampling.positions_along_centerline(cl, spacing_px=25.0, offset_px=10.0)
        self.assertAlmostEqual(positions[0][0], 10.0, delta=0.1)

    def test_sample_bead_colors(self):
        img, centers, radius = synthetic_beads()
        samples = sampling.sample_beads(img, centers, radius=radius * 0.8)
        self.assertEqual(len(samples), len(centers))
        expected_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        for i, bead in enumerate(samples[:3]):
            exp = np.array(expected_colors[i], dtype=float)
            color = np.array(bead.color)
            # Colors should be close to the fill values
            self.assertTrue(np.allclose(color, exp, atol=5.0))

    def test_centerline_length(self):
        xs = [0, 3, 6]
        ys = [0, 4, 0]
        cl = segmentation.Centerline(xs=xs, ys=ys)
        length = sampling.centerline_length(cl)
        # Two segments: 3-4-5 triangles
        self.assertAlmostEqual(length, 10.0)


if __name__ == "__main__":
    unittest.main()
