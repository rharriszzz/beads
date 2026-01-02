"""Debug utility to visualize HSV peak detection and masks."""

import argparse
from pathlib import Path
import random

import numpy as np
from PIL import Image

from image_to_pattern import color_peaks, segmentation


def overlay_masks(img: np.ndarray, masks, alpha: float = 0.4):
    """Overlay colored masks on image."""
    out = img.astype(float).copy()
    h, w, _ = img.shape
    colors = []
    random.seed(42)
    for _ in masks:
        colors.append(np.array([random.randint(0, 255) for _ in range(3)], dtype=float))
    for idx, mask in enumerate(masks):
        c = colors[idx]
        out[mask] = (1 - alpha) * out[mask] + alpha * c
    return np.clip(out, 0, 255).astype(np.uint8)


def main():
    parser = argparse.ArgumentParser(description="Visualize HSV peak masks.")
    parser.add_argument("image", type=Path, help="Input image path")
    parser.add_argument("--num-peaks", type=int, default=3, help="Number of peaks to find")
    parser.add_argument("--radius-h", type=float, default=0.08, help="Hue radius")
    parser.add_argument("--radius-s", type=float, default=0.25, help="Saturation radius")
    parser.add_argument("--radius-v", type=float, default=0.25, help="Value radius")
    parser.add_argument("--outdir", type=Path, default=Path("image-to-pattern/debug-output"), help="Output directory")
    args = parser.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)
    img = Image.open(args.image).convert("RGB")
    img_arr = np.array(img)
    mask = segmentation.mask_bracelet(img)
    hsv = color_peaks.hsv_image(img_arr)
    peaks = color_peaks.adaptive_peak_masks(
        hsv,
        mask,
        num_peaks=args.num_peaks,
        radius_h=args.radius_h,
        radius_s=args.radius_s,
        radius_v=args.radius_v,
    )

    peak_masks = [p.mask for p in peaks]
    overlay = overlay_masks(img_arr, peak_masks)
    Image.fromarray(overlay).save(args.outdir / f"{args.image.stem}-peaks.png")

    # Save individual peak masks
    for i, p in enumerate(peaks):
        m_img = np.zeros_like(img_arr)
        m_img[p.mask] = [255, 0, 0]
        Image.fromarray(m_img).save(args.outdir / f"{args.image.stem}-peak-{i}.png")

    print(f"Saved overlays to {args.outdir}")


if __name__ == "__main__":
    main()
