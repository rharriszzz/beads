"""Debug script: bin centerline points by tangent angle and FFT HSV values."""

import argparse
from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import os
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from skimage import color

# Silence fontconfig cache warnings by using a tmp config dir
os.environ.setdefault("MPLCONFIGDIR", "/tmp/mplcache")

from image_to_pattern import segmentation


def centerline_angles(centerline):
    xs = np.array(centerline.xs, dtype=float)
    ys = np.array(centerline.ys, dtype=float)
    dx = np.diff(xs)
    dy = np.diff(ys)
    angles = np.degrees(np.arctan2(dy, dx)) % 360.0
    return angles


def main():
    parser = argparse.ArgumentParser(description="FFT HSV values binned by centerline angle.")
    parser.add_argument("image", type=Path, help="Input image")
    parser.add_argument("--bins", type=int, default=8, help="Number of angle bins (e.g., 8 or 16)")
    parser.add_argument("--channel", choices=["h", "s", "v"], default="v", help="HSV channel to analyze")
    parser.add_argument("--outdir", type=Path, default=Path("image-to-pattern/debug-output"), help="Output directory")
    args = parser.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)
    img = Image.open(args.image).convert("RGB")
    mask = segmentation.mask_bracelet(img)
    cl = segmentation.centerline_from_mask(mask)
    angles = centerline_angles(cl)

    hsv = color.rgb2hsv(np.array(img) / 255.0)
    channel_map = {"h": 0, "s": 1, "v": 2}
    chan_idx = channel_map[args.channel]

    # Collect samples per bin (ordered along centerline)
    bin_values = [[] for _ in range(args.bins)]
    xs = np.array(cl.xs, dtype=int)
    ys = np.array(cl.ys, dtype=int)
    for i in range(len(angles)):
        ang = angles[i]
        bin_idx = int((ang / 360.0) * args.bins) % args.bins
        x = xs[i]
        y = ys[i]
        if 0 <= y < hsv.shape[0] and 0 <= x < hsv.shape[1]:
            bin_values[bin_idx].append(hsv[y, x, chan_idx])

    # Plot FFT magnitude per bin
    cols = min(4, args.bins)
    rows = (args.bins + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(4 * cols, 3 * rows), squeeze=False)
    for idx in range(args.bins):
        ax = axes[idx // cols][idx % cols]
        vals = np.array(bin_values[idx], dtype=float)
        if vals.size > 0:
            fft = np.abs(np.fft.rfft(vals - vals.mean()))
            ax.plot(fft)
        ax.set_title(f"Bin {idx}")
        ax.set_xlabel("Freq")
        ax.set_ylabel("|FFT|")
    for j in range(args.bins, rows * cols):
        axes[j // cols][j % cols].axis("off")
    fig.tight_layout()
    out_path = args.outdir / f"{args.image.stem}-angle-fft.png"
    fig.savefig(out_path)
    print(f"Saved angle FFT plot to {out_path}")


if __name__ == "__main__":
    main()
