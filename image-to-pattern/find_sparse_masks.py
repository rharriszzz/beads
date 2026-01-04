"""Search for HSV-based masks that resemble the sparse first-pair look.

Loop: randomly sample a pixel, build an HSV range mask with fixed tolerances,
classify the mask shape, and keep only those that look like the sparse "first pair".
Saves mask/overlay images for accepted samples and stops after N successes.

Usage:
  python3.11 image-to-pattern/find_sparse_masks.py --image beads-photo-2.jpg --count 10
"""

from __future__ import annotations

import argparse
import random
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
from PIL import Image


def load_image(path: Path) -> Tuple[np.ndarray, np.ndarray]:
    img_rgb = np.array(Image.open(path).convert("RGB"))
    img_hsv = np.array(Image.open(path).convert("HSV"))
    return img_rgb, img_hsv


def build_mask(img_hsv: np.ndarray, x: int, y: int, tol_h: int, tol_s: int, tol_v: int) -> Tuple[np.ndarray, Tuple[int, int, int, int, int, int]]:
    h0, s0, v0 = map(int, img_hsv[y, x, :])
    hmin, hmax = max(0, h0 - tol_h), min(255, h0 + tol_h)
    smin, smax = max(0, s0 - tol_s), min(255, s0 + tol_s)
    vmin, vmax = max(0, v0 - tol_v), min(255, v0 + tol_v)
    h = img_hsv[:, :, 0]
    s = img_hsv[:, :, 1]
    v = img_hsv[:, :, 2]
    mask = (h >= hmin) & (h <= hmax) & (s >= smin) & (s <= smax) & (v >= vmin) & (v <= vmax)
    return mask, (hmin, hmax, smin, smax, vmin, vmax)


def hsv_in_ranges(hsv: Tuple[int, int, int], ranges: list[Tuple[int, int, int, int, int, int]]) -> bool:
    h, s, v = hsv
    for (hmin, hmax, smin, smax, vmin, vmax) in ranges:
        if hmin <= h <= hmax and smin <= s <= smax and vmin <= v <= vmax:
            return True
    return False


def downsample(mask: np.ndarray, step: int = 4) -> np.ndarray:
    return mask[::step, ::step]


def largest_component_fraction(mask: np.ndarray) -> float:
    """Compute largest component fraction (4-neighbor)."""
    visited = np.zeros_like(mask, dtype=bool)
    coords = np.argwhere(mask)
    total = mask.size
    largest = 0
    # Simple stack-based flood fill
    for y, x in coords:
        if visited[y, x]:
            continue
        stack = [(y, x)]
        visited[y, x] = True
        size = 0
        while stack:
            cy, cx = stack.pop()
            size += 1
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < mask.shape[0] and 0 <= nx < mask.shape[1]:
                    if mask[ny, nx] and not visited[ny, nx]:
                        visited[ny, nx] = True
                        stack.append((ny, nx))
        if size > largest:
            largest = size
        # Early exit if remaining pixels can't beat largest
        if (coords.shape[0] - visited.sum()) + largest <= largest:
            break
    return largest / float(total if total else 1)


def edge_ratio_and_thickness(mask: np.ndarray) -> Tuple[float, float]:
    """Approximate edge ratio and thickness using a 1-pixel erosion."""
    total = mask.size
    # 4-neighbor erosion
    shifted = (
        np.roll(mask, 1, axis=0)
        & np.roll(mask, -1, axis=0)
        & np.roll(mask, 1, axis=1)
        & np.roll(mask, -1, axis=1)
    )
    inner = mask & shifted
    edge = mask & (~inner)
    edge_ratio = edge.sum() / float(total if total else 1)
    area_ratio = mask.sum() / float(total if total else 1)
    thickness = area_ratio / max(edge_ratio, 1e-6)
    return edge_ratio, thickness


def classify_sparse(mask: np.ndarray) -> bool:
    """Return True if mask resembles the sparse first-pair look."""
    m = downsample(mask, step=4)
    area_ratio = m.mean()
    largest_frac = largest_component_fraction(m)
    edge_ratio, thickness_est = edge_ratio_and_thickness(m)
    # Heuristics tuned to separate sparse dots from outlines/bands
    return (area_ratio < 0.01) and (largest_frac < 0.005) and (thickness_est < 0.02) and (edge_ratio < 0.005)


def save_mask_and_overlay(img_rgb: np.ndarray, mask: np.ndarray, outdir: Path, stem: str):
    outdir.mkdir(parents=True, exist_ok=True)
    mask_img = (mask.astype(np.uint8) * 255)
    overlay = np.full_like(img_rgb, 255, dtype=np.uint8)
    if mask.any():
        overlay[mask] = img_rgb[mask]
    Image.fromarray(mask_img, mode="L").save(outdir / f"{stem}_mask.png")
    Image.fromarray(overlay, mode="RGB").save(outdir / f"{stem}_overlay.png")


def main():
    parser = argparse.ArgumentParser(description="Find sparse-looking HSV masks via random sampling.")
    parser.add_argument("--image", required=True, help="Image file")
    parser.add_argument("--count", type=int, default=10, help="Number of good samples to collect")
    parser.add_argument("--tol_h", type=int, default=10)
    parser.add_argument("--tol_s", type=int, default=24)
    parser.add_argument("--tol_v", type=int, default=24)
    parser.add_argument("--outdir", type=Path, default=Path("image-to-pattern/debug-output"))
    args = parser.parse_args()

    img_rgb, img_hsv = load_image(Path(args.image))
    h, w, _ = img_rgb.shape

    kept = 0
    attempts = 0
    excluded_ranges: list[Tuple[int, int, int, int, int, int]] = []
    while kept < args.count:
        attempts += 1
        x = random.randint(0, w - 1)
        y = random.randint(0, h - 1)
        base_hsv = tuple(map(int, img_hsv[y, x, :]))
        if hsv_in_ranges(base_hsv, excluded_ranges):
            print(f"[attempt {attempts}] skip x={x} y={y} base_hsv={base_hsv} (in excluded ranges)")
            continue
        mask, rng = build_mask(img_hsv, x, y, args.tol_h, args.tol_s, args.tol_v)
        is_sparse = classify_sparse(mask)
        stem = f"{Path(args.image).stem}_x{x}_y{y}_h{args.tol_h}_s{args.tol_s}_v{args.tol_v}"
        if is_sparse:
            save_mask_and_overlay(img_rgb, mask, args.outdir, stem)
            kept += 1
            print(f"[{kept}/{args.count}] kept {stem}")
        else:
            if not hsv_in_ranges(base_hsv, excluded_ranges):
                excluded_ranges.append(rng)
            print(f"[attempt {attempts}] discard {stem}; added range {rng}")

    print(f"Done. Attempts: {attempts}, kept: {kept}")


if __name__ == "__main__":
    main()
