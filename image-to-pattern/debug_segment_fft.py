"""Debug: angle-binned, variable-size patches along the bracelet with 2D FFT."""

import argparse
from pathlib import Path
import os
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from scipy import ndimage

os.environ.setdefault("MPLCONFIGDIR", "/tmp/mplcache")

from image_to_pattern import segmentation


def centerline_with_angles(centerline):
    xs = np.array(centerline.xs, dtype=float)
    ys = np.array(centerline.ys, dtype=float)
    dx = np.diff(xs)
    dy = np.diff(ys)
    angles = np.degrees(np.arctan2(dy, dx)) % 360.0
    angles = np.concatenate([angles, angles[-1:]])  # pad last
    return xs, ys, angles


def segment_for_angle(xs, ys, angles, idx, half_range_deg):
    target = angles[idx]
    lo = (target - half_range_deg) % 360.0
    hi = (target + half_range_deg) % 360.0

    def within(a):
        if lo <= hi:
            return (a >= lo) & (a <= hi)
        return (a >= lo) | (a <= hi)

    start = idx
    while start > 0 and within(angles[start - 1]):
        start -= 1
    end = idx
    while end < len(angles) - 1 and within(angles[end + 1]):
        end += 1
    return start, end, target


def extract_segment_patch(img_arr, xs, ys, start, end, angle_deg, margin=10):
    pts = np.stack([xs[start:end+1], ys[start:end+1]], axis=1)
    x_min, y_min = pts.min(axis=0)
    x_max, y_max = pts.max(axis=0)
    cx = (x_min + x_max) / 2.0
    cy = (y_min + y_max) / 2.0
    width = (x_max - x_min) + 2 * margin
    height = (y_max - y_min) + 2 * margin
    # Pad image to avoid boundary issues
    pad = int(max(width, height))
    padded = np.pad(img_arr, ((pad, pad), (pad, pad), (0, 0)), mode="reflect")
    cx_p = cx + pad
    cy_p = cy + pad
    x0 = int(cx_p - width / 2)
    x1 = int(cx_p + width / 2)
    y0 = int(cy_p - height / 2)
    y1 = int(cy_p + height / 2)
    crop = padded[y0:y1, x0:x1]
    rotated = ndimage.rotate(crop, angle=-angle_deg, reshape=True, order=1, mode="nearest", prefilter=False)
    return rotated


def fft_magnitude(patch):
    gray = np.dot(patch[..., :3], [0.299, 0.587, 0.114])
    f = np.fft.fftshift(np.fft.fft2(gray - gray.mean()))
    return np.log1p(np.abs(f))


def main():
    parser = argparse.ArgumentParser(description="Angle-binned variable patches FFT along bracelet.")
    parser.add_argument("image", type=Path, help="Input image")
    parser.add_argument("--bins", type=int, default=12, help="Number of angle bins (e.g., 12 -> 30 deg)")
    parser.add_argument("--step", type=int, default=15, help="Index step along centerline to place anchors")
    parser.add_argument("--outdir", type=Path, default=Path("image-to-pattern/debug-output"), help="Output directory")
    args = parser.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)
    img = Image.open(args.image).convert("RGB")
    img_arr = np.array(img)
    mask = segmentation.mask_bracelet(img)
    cl = segmentation.centerline_from_mask(mask)
    xs, ys, angs = centerline_with_angles(cl)

    half_range = 180.0 / args.bins  # half of bin width
    patches = []
    patch_angles = []
    for idx in range(0, len(xs), args.step):
        start, end, ang = segment_for_angle(xs, ys, angs, idx, half_range)
        patch = extract_segment_patch(img_arr, xs, ys, start, end, ang, margin=20)
        patches.append(patch)
        patch_angles.append(ang)

    if not patches:
        print("No patches extracted")
        return

    # Crop patches to common size (smallest) to allow stacking
    min_h = min(p.shape[0] for p in patches)
    min_w = min(p.shape[1] for p in patches)
    cropped = [p[:min_h, :min_w] for p in patches]

    mags = [fft_magnitude(p) for p in cropped]
    avg_mag = np.mean(np.stack(mags), axis=0)

    plt.figure(figsize=(5, 5))
    plt.imshow(avg_mag, cmap="inferno")
    plt.title("Average FFT magnitude (log scale)")
    plt.axis("off")
    out_fft = args.outdir / f"{args.image.stem}-seg-fft.png"
    plt.savefig(out_fft, bbox_inches="tight")

    # Save a grid of sample patches
    grid_cols = 4
    grid_rows = min(4, (len(patches) + grid_cols - 1) // grid_cols)
    fig, axes = plt.subplots(grid_rows, grid_cols, figsize=(3 * grid_cols, 3 * grid_rows))
    for idx, ax in enumerate(axes.flatten()):
        if idx < len(patches):
            ax.imshow(patches[idx].astype(np.uint8))
            ax.set_title(f"{patch_angles[idx]:.1f} deg")
        ax.axis("off")
    out_patches = args.outdir / f"{args.image.stem}-seg-patches.png"
    plt.savefig(out_patches, bbox_inches="tight")

    print(f"Saved {out_fft} and {out_patches}")


if __name__ == "__main__":
    main()
