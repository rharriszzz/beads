"""Debug: extract paths from two largest background components and their hole."""

import argparse
from pathlib import Path
from typing import List, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance
from scipy import ndimage, interpolate
from skimage import measure

from image_to_pattern import segmentation


def largest_components(inv_mask: np.ndarray, count: int = 2) -> List[np.ndarray]:
    labeled, num = ndimage.label(inv_mask)
    if num == 0:
        return []
    sizes = ndimage.sum(inv_mask, labeled, index=range(1, num + 1))
    order = np.argsort(sizes)[::-1][:count]
    comps = [(labeled == (idx + 1)) for idx in order]
    return comps


def contour_longest(mask: np.ndarray) -> np.ndarray:
    contours = measure.find_contours(mask.astype(float), level=0.5)
    if not contours:
        return np.zeros((0, 2))
    longest = max(contours, key=lambda c: c.shape[0])
    return longest  # rows of (row, col)


def smooth_path(path: np.ndarray) -> np.ndarray:
    if path.shape[0] < 4:
        return path
    # Lighter smoothing to keep path closer to edges
    sigma = max(0.5, path.shape[0] / 100.0)
    x_smooth = ndimage.gaussian_filter1d(path[:, 1], sigma=sigma, mode="wrap")
    y_smooth = ndimage.gaussian_filter1d(path[:, 0], sigma=sigma, mode="wrap")
    return np.vstack([y_smooth, x_smooth]).T


def spline_path(path: np.ndarray, samples: int = 200) -> np.ndarray:
    if path.shape[0] < 4:
        return path
    # Smaller smoothing parameter to better hug edges
    smooth_factor = max(path.shape[0] * 0.1, 1)
    tck, _ = interpolate.splprep([path[:, 1], path[:, 0]], s=smooth_factor, per=False)
    u_new = np.linspace(0, 1, samples)
    x_new, y_new = interpolate.splev(u_new, tck)
    return np.vstack([y_new, x_new]).T


def draw_path(draw: ImageDraw.ImageDraw, path: np.ndarray, color: Tuple[int, int, int], width: int = 2):
    if path.shape[0] < 2:
        return
    pts = [(float(c), float(r)) for r, c in path]
    draw.line(pts, fill=color, width=width)


def main():
    parser = argparse.ArgumentParser(description="Extract background paths and midline.")
    parser.add_argument("image", type=Path, help="Input image")
    parser.add_argument("--outdir", type=Path, default=Path("image-to-pattern/debug-output"), help="Output directory")
    parser.add_argument("--max-dim", type=int, default=1200, help="Resize longest side if larger")
    args = parser.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)
    img = Image.open(args.image).convert("RGB")
    if max(img.size) > args.max_dim:
        img.thumbnail((args.max_dim, args.max_dim), Image.LANCZOS)
    mask = segmentation.mask_bracelet(img)
    inv = ~mask
    comps = largest_components(inv, count=2)
    if len(comps) < 2:
        print("Not enough background components found")
        return

    # First component: find hole contour
    comp0 = comps[0]
    filled0 = ndimage.binary_fill_holes(comp0)
    holes = filled0 & (~comp0)
    hole_contour = contour_longest(holes)
    comp1_contour = contour_longest(comps[1])

    hole_spline = spline_path(smooth_path(hole_contour))
    comp1_spline = spline_path(smooth_path(comp1_contour))

    # Midline: average the two splines by interpolating to common length
    midline = np.zeros_like(hole_spline)
    if hole_spline.shape[0] > 1 and comp1_spline.shape[0] > 1:
        n = min(hole_spline.shape[0], comp1_spline.shape[0])
        hs = hole_spline[:n]
        cs = comp1_spline[:n]
        midline = 0.5 * (hs + cs)

    # Lighten image for visibility
    enhancer = ImageEnhance.Brightness(img)
    out = enhancer.enhance(1.6)
    draw = ImageDraw.Draw(out)
    draw_path(draw, hole_spline, color=(255, 0, 0), width=2)
    draw_path(draw, comp1_spline, color=(0, 0, 255), width=2)
    draw_path(draw, midline, color=(0, 255, 0), width=2)
    out_path = args.outdir / f"{args.image.stem}-background-paths.png"
    out.save(out_path)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
