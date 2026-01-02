"""Debug script: extract patches along the bracelet, align by tangent, and compute 2D FFTs."""

import argparse
from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import os
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from scipy import ndimage

os.environ.setdefault("MPLCONFIGDIR", "/tmp/mplcache")

from image_to_pattern import segmentation


def centerline_with_tangent(centerline):
    xs = np.array(centerline.xs, dtype=float)
    ys = np.array(centerline.ys, dtype=float)
    dx = np.diff(xs)
    dy = np.diff(ys)
    angles = np.degrees(np.arctan2(dy, dx)) % 360.0
    # Pad last angle with previous
    angles = np.concatenate([angles, angles[-1:]])
    return xs, ys, angles


def extract_patches(img_arr, xs, ys, angles, patch_size=32, step=10):
    """Extract square patches centered on the centerline and rotate locally."""
    half = patch_size // 2
    # Pad to avoid boundary issues
    pad = patch_size
    padded = np.pad(img_arr, ((pad, pad), (pad, pad), (0, 0)), mode="reflect")
    patches = []
    for i in range(0, len(xs), step):
        cx = xs[i] + pad
        cy = ys[i] + pad
        ang = angles[i]
        xi = int(round(cx))
        yi = int(round(cy))
        x0 = xi - half
        x1 = xi + half
        y0 = yi - half
        y1 = yi + half
        patch = padded[y0:y1, x0:x1]
        if patch.shape[0] != patch_size or patch.shape[1] != patch_size:
            continue
        # Rotate patch so tangent is horizontal; use -ang to align
        rot = ndimage.rotate(
            patch,
            angle=-ang,
            reshape=False,
            order=1,
            mode="nearest",
            prefilter=False,
        )
        patches.append(rot)
    return patches


def fft_magnitude(patch):
    # grayscale for simplicity
    gray = np.dot(patch[..., :3], [0.299, 0.587, 0.114])
    f = np.fft.fftshift(np.fft.fft2(gray - gray.mean()))
    return np.abs(f)


def main():
    parser = argparse.ArgumentParser(description="2D FFT of patches along bracelet aligned by tangent.")
    parser.add_argument("image", type=Path, help="Input image path")
    parser.add_argument("--patch-size", type=int, default=64, help="Square patch size")
    parser.add_argument("--step", type=int, default=10, help="Step along centerline for patch sampling")
    parser.add_argument("--outdir", type=Path, default=Path("image-to-pattern/debug-output"), help="Output directory")
    args = parser.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)
    img = Image.open(args.image).convert("RGB")
    img_arr = np.array(img)
    mask = segmentation.mask_bracelet(img)
    cl = segmentation.centerline_from_mask(mask)
    xs, ys, angles = centerline_with_tangent(cl)

    patches = extract_patches(img_arr, xs, ys, angles, patch_size=args.patch_size, step=args.step)
    if not patches:
        print("No patches extracted")
        return
    mags = [fft_magnitude(p) for p in patches]
    avg_mag = np.mean(np.stack(mags), axis=0)

    # Normalize and save FFT magnitude
    avg_norm = np.log1p(avg_mag)
    plt.figure(figsize=(5, 5))
    plt.imshow(avg_norm, cmap="inferno")
    plt.title("Average FFT magnitude (log scale)")
    plt.axis("off")
    out_fft = args.outdir / f"{args.image.stem}-patch-fft.png"
    plt.savefig(out_fft, bbox_inches="tight")

    # Save a grid of sample patches
    grid_cols = 5
    grid_rows = min(4, (len(patches) + grid_cols - 1) // grid_cols)
    fig, axes = plt.subplots(grid_rows, grid_cols, figsize=(3 * grid_cols, 3 * grid_rows))
    for idx, ax in enumerate(axes.flatten()):
        if idx < len(patches):
            ax.imshow(patches[idx].astype(np.uint8))
        ax.axis("off")
    out_patches = args.outdir / f"{args.image.stem}-patches.png"
    plt.savefig(out_patches, bbox_inches="tight")

    print(f"Saved {out_fft} and {out_patches}")


if __name__ == "__main__":
    main()
