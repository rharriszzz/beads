"""Quick bead-vs-background segmentation using saturation alone.

Uses Otsu's method on the S channel to pick a threshold and saves a mask and overlay.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image


def otsu_threshold(values: np.ndarray) -> int:
    """Compute Otsu threshold for 0-255 uint8 values."""
    hist, _ = np.histogram(values, bins=256, range=(0, 256))
    total = values.size
    sum_total = np.dot(np.arange(256), hist)
    sum_b = 0.0
    w_b = 0.0
    max_var = 0.0
    threshold = 0
    for t in range(256):
        w_b += hist[t]
        if w_b == 0:
            continue
        w_f = total - w_b
        if w_f == 0:
            break
        sum_b += t * hist[t]
        m_b = sum_b / w_b
        m_f = (sum_total - sum_b) / w_f
        var_between = w_b * w_f * (m_b - m_f) ** 2
        if var_between > max_var:
            max_var = var_between
            threshold = t
    return threshold


def main():
    parser = argparse.ArgumentParser(description="Segment beads via saturation threshold (Otsu).")
    parser.add_argument("--image", required=True, type=Path, help="Input image")
    parser.add_argument("--outdir", type=Path, default=Path("image-to-pattern/debug-output"), help="Output directory")
    args = parser.parse_args()

    img_rgb = np.array(Image.open(args.image).convert("RGB"))
    img_hsv = np.array(Image.open(args.image).convert("HSV"))
    s_channel = img_hsv[:, :, 1]

    thr = otsu_threshold(s_channel)
    mask = s_channel > thr

    args.outdir.mkdir(parents=True, exist_ok=True)
    stem = args.image.stem

    mask_img = (mask.astype(np.uint8) * 255)
    Image.fromarray(mask_img, mode="L").save(args.outdir / f"{stem}-s-mask.png")

    overlay = np.full_like(img_rgb, 255, dtype=np.uint8)
    overlay[mask] = img_rgb[mask]
    Image.fromarray(overlay, mode="RGB").save(args.outdir / f"{stem}-s-overlay.png")

    print(f"S threshold (Otsu): {thr}")
    print(f"Mask true ratio: {mask.mean():.4f}")
    print(f"Saved mask and overlay to {args.outdir}")


if __name__ == "__main__":
    main()
