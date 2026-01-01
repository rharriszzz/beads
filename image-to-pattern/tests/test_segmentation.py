import sys
from pathlib import Path
import unittest

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from image_to_pattern import segmentation


def synthetic_band(width=200, height=100, band_top=40, band_height=20, band_color=(180, 0, 180)):
    """Create a simple synthetic bracelet image: colored horizontal band on white."""
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    band_bottom = band_top + band_height
    draw.rectangle([0, band_top, width, band_bottom], fill=band_color)
    return img, (band_top, band_bottom)


class SegmentationTests(unittest.TestCase):
    def test_mask_bracelet_counts(self):
        img, (top, bottom) = synthetic_band()
        mask = segmentation.mask_bracelet(img, brightness_threshold=230)
        self.assertEqual(mask.dtype, np.bool_)
        expected_area = (bottom - top + 1) * img.width
        self.assertGreater(mask.sum(), 0.9 * expected_area)

    def test_centerline_horizontal_band(self):
        img, (top, bottom) = synthetic_band()
        mask = segmentation.mask_bracelet(img, brightness_threshold=230)
        centerline = segmentation.centerline_from_mask(mask)
        self.assertLessEqual(min(centerline.xs), 1)  # morphology may shave a pixel
        self.assertGreaterEqual(max(centerline.xs), img.width - 2)
        target_y = (top + bottom) / 2.0
        rmse = segmentation.centerline_rmse(centerline, target_y)
        self.assertLess(rmse, 0.6)  # should be near-perfect horizontal line

    def test_centerline_no_mask(self):
        img = Image.new("RGB", (50, 50), color=(255, 255, 255))
        mask = segmentation.mask_bracelet(img, brightness_threshold=10)  # nothing passes
        with self.assertRaises(ValueError):
            segmentation.centerline_from_mask(mask)

    def test_band_widths(self):
        band_top = 30
        band_height = 15
        img, (top, bottom) = synthetic_band(band_top=band_top, band_height=band_height)
        mask = segmentation.mask_bracelet(img, brightness_threshold=230)
        widths = segmentation.band_widths(mask)
        # Widths where band exists should be close to band_height + 1 (inclusive range)
        non_zero = widths[widths > 0]
        self.assertTrue(np.allclose(non_zero, band_height + 1))


if __name__ == "__main__":
    unittest.main()
