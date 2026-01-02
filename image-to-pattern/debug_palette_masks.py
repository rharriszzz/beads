"""Visualize palette masks with true pixels colored and others white/gray."""

import argparse
from pathlib import Path
import numpy as np
from PIL import Image

from image_to_pattern import segmentation, color_detect


def main():
    parser = argparse.ArgumentParser(description="Save palette masks with colored pixels.")
    parser.add_argument("image", type=Path, help="Input image")
    parser.add_argument("--k", type=int, default=7, help="Number of palette colors (k-means mode)")
    parser.add_argument("--method", choices=["kmeans", "peaks"], default="kmeans", help="Palette selection method")
    parser.add_argument("--max-colors", type=int, default=8, help="Max colors when using peak-based palette")
    parser.add_argument("--drop-background", action="store_true", help="Drop dominant background peak (peaks mode)")
    parser.add_argument("--merge-hues", action="store_true", help="Merge palette bins with nearby hues")
    parser.add_argument("--hue-tol", type=float, default=0.03, help="Hue tolerance for merging (0-1)")
    parser.add_argument("--outdir", type=Path, default=Path("image-to-pattern/debug-output"), help="Output directory")
    args = parser.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)
    img = Image.open(args.image).convert("RGB")
    img_arr = np.array(img)

    if args.method == "kmeans":
        pixels = img_arr.reshape(-1, 3).astype(float)
        palette = color_detect.kmeans_palette_hsv(pixels, k=args.k, iters=15, restarts=5)
    else:
        mask = segmentation.mask_bracelet(img)
        palette = color_detect.palette_from_hist_peaks(
            img_arr,
            mask=mask,
            max_colors=args.max_colors,
            drop_background=args.drop_background,
            min_prominence=0.01,
            min_separation=0.02,
        )

    if palette.size == 0:
        print("No palette colors found.")
        return
    labels = color_detect.label_image_by_palette(np.array(img), palette, mode="hsv")
    if args.merge_hues:
        counts = np.bincount(labels.flatten(), minlength=palette.shape[0])
        palette, mapping = color_detect.merge_close_hues(palette, counts=counts, hue_tol=args.hue_tol)
        labels = color_detect.label_image_by_palette(np.array(img), palette, mode="hsv")

    for i in range(palette.shape[0]):
        color_rgb = palette[i]
        base = np.full_like(np.array(img), 255, dtype=np.uint8)
        if np.all(color_rgb > 240):
            base = np.full_like(np.array(img), 200, dtype=np.uint8)  # gray for white-ish
        mask_i = labels == i
        base[mask_i] = color_rgb.astype(np.uint8)
        Image.fromarray(base).save(args.outdir / f"{args.image.stem}-k{args.k}-color-{i}-vis.png")
    print(f"Saved color visualizations to {args.outdir}")


if __name__ == "__main__":
    main()
