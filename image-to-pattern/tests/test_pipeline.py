import sys
from pathlib import Path
import unittest

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from image_to_pattern import pipeline


def synthetic_beads(
    width=200,
    height=80,
    spacing=20,
    radius=8,
    band_y=40,
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
        cy = band_y
        centers.append((cx, cy))
        draw.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            fill=colors[color_idx % len(colors)],
        )
        x += spacing
        color_idx += 1
    return img, centers, radius, colors


class PipelineTests(unittest.TestCase):
    def test_pipeline_recovers_palette_indices(self):
        img, centers, radius, palette_colors = synthetic_beads()
        spacing = centers[1][0] - centers[0][0]
        offset = centers[0][0]
        result = pipeline.infer_palette_indices(
            img,
            palette_colors=palette_colors,
            spacing_px=spacing,
            radius_px=radius * 0.8,
            brightness_threshold=250,
            offset_px=offset,
        )
        # Ensure we sampled roughly as many beads as drawn
        self.assertTrue(abs(len(result.indices) - len(centers)) <= 1)
        expected = [i % len(palette_colors) for i in range(len(result.indices))]
        self.assertEqual(result.indices[: len(expected)], expected)

    def test_pipeline_pattern_detection(self):
        palette_colors = ((255, 0, 0), (0, 255, 0), (0, 0, 255))
        img, centers, radius, _ = synthetic_beads(colors=palette_colors)
        spacing = centers[1][0] - centers[0][0]
        offset = centers[0][0]
        result = pipeline.infer_pattern(
            img,
            palette_colors=palette_colors,
            spacing_px=spacing,
            radius_px=radius * 0.8,
            brightness_threshold=250,
            offset_px=offset,
        )
        self.assertEqual(result.period, 3)
        self.assertEqual(result.pattern, [0, 1, 2])


if __name__ == "__main__":
    unittest.main()
