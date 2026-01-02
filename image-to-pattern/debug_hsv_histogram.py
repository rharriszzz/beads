"""Debug: HSV bin counts and bargraph of top bins."""

import argparse
from pathlib import Path
import os

import matplotlib

matplotlib.use("Agg")
os.environ.setdefault("MPLCONFIGDIR", "/tmp/mplcache")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from skimage import color

from image_to_pattern import segmentation


def hsv_histogram(img_arr, mask, h_bins, s_bins, v_bins):
    hsv = color.rgb2hsv(np.clip(img_arr / 255.0, 0, 1))
    h = hsv[:, :, 0][mask]
    s = hsv[:, :, 1][mask]
    v = hsv[:, :, 2][mask]
    hist, edges = np.histogramdd(
        np.stack([h, s, v], axis=1),
        bins=(h_bins, s_bins, v_bins),
        range=((0, 1), (0, 1), (0, 1)),
    )
    return hist, edges


def bin_midpoints(edges):
    return [0.5 * (e[:-1] + e[1:]) for e in edges]


def main():
    parser = argparse.ArgumentParser(description="HSV histogram bargraph per bin size.")
    parser.add_argument("image", type=Path, help="Input image")
    parser.add_argument("--h-bins", type=int, default=36, help="Hue bins")
    parser.add_argument("--s-bins", type=int, default=10, help="Saturation bins")
    parser.add_argument("--v-bins", type=int, default=10, help="Value bins")
    parser.add_argument("--top", type=int, default=50, help="Top bins to plot")
    parser.add_argument("--use-mask", action="store_true", help="Use bracelet mask; otherwise use full image")
    parser.add_argument("--outdir", type=Path, default=Path("image-to-pattern/debug-output"), help="Output directory")
    args = parser.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)
    img = Image.open(args.image).convert("RGB")
    if args.use_mask:
        mask = segmentation.mask_bracelet(img)
    else:
        mask = np.ones((img.height, img.width), dtype=bool)
    img_arr = np.array(img)
    hist, edges = hsv_histogram(img_arr, mask, args.h_bins, args.s_bins, args.v_bins)
    mid_h, mid_s, mid_v = bin_midpoints(edges)

    flat_hist = hist.flatten()
    flat_indices = np.argsort(flat_hist)[::-1][: args.top]
    counts = flat_hist[flat_indices]
    # Map flat index to bin centers
    h_idx = flat_indices // (args.s_bins * args.v_bins)
    rem = flat_indices % (args.s_bins * args.v_bins)
    s_idx = rem // args.v_bins
    v_idx = rem % args.v_bins
    colors = []
    for hi, si, vi in zip(h_idx, s_idx, v_idx):
        hsv_mid = np.array([mid_h[hi], mid_s[si], mid_v[vi]])
        rgb = color.hsv2rgb([hsv_mid])[0]
        if np.all(rgb > 0.9):  # too white
            rgb = np.array([0.5, 0.5, 0.5])
        colors.append(rgb)

    plt.figure(figsize=(12, 6))
    plt.bar(range(len(counts)), counts, color=colors)
    plt.yscale("log")
    plt.xlabel("Top bins (sorted)")
    plt.ylabel("Pixel count (log)")
    plt.title(f"HSV bins h={args.h_bins}, s={args.s_bins}, v={args.v_bins}")
    out_path = args.outdir / f"{args.image.stem}-hsv-bars.png"
    plt.tight_layout()
    plt.savefig(out_path)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
