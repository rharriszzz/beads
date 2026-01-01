"""Sampling utilities to place bead centers along a centerline and read colors."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple

import numpy as np
from PIL import Image

from .segmentation import Centerline


@dataclass
class BeadSample:
    center: Tuple[float, float]
    color: Tuple[float, float, float]  # RGB in [0, 255]


def positions_along_centerline(
    centerline: Centerline, spacing_px: float, offset_px: float = 0.0
) -> List[Tuple[float, float]]:
    """Return bead centers placed every `spacing_px` along the centerline.

    Uses arc-length parameterization and linear interpolation between sampled
    centerline points. `offset_px` shifts the starting position along the curve.
    """
    if spacing_px <= 0:
        raise ValueError("spacing_px must be positive")
    xs = np.array(centerline.xs, dtype=float)
    ys = np.array(centerline.ys, dtype=float)
    if xs.size < 2:
        raise ValueError("Centerline needs at least two points")

    dx = np.diff(xs)
    dy = np.diff(ys)
    seg_lengths = np.sqrt(dx * dx + dy * dy)
    arc = np.concatenate([[0.0], np.cumsum(seg_lengths)])
    total_length = arc[-1]
    if total_length <= 0:
        raise ValueError("Centerline has zero length")

    # Sample positions
    positions: List[Tuple[float, float]] = []
    target = offset_px
    while target <= total_length:
        x = np.interp(target, arc, xs)
        y = np.interp(target, arc, ys)
        positions.append((float(x), float(y)))
        target += spacing_px
    return positions


def centerline_length(centerline: Centerline) -> float:
    """Compute arc length of a centerline."""
    xs = np.array(centerline.xs, dtype=float)
    ys = np.array(centerline.ys, dtype=float)
    if xs.size < 2:
        return 0.0
    dx = np.diff(xs)
    dy = np.diff(ys)
    seg_lengths = np.sqrt(dx * dx + dy * dy)
    return float(seg_lengths.sum())


def sample_disk_mean(img: Image.Image, center: Tuple[float, float], radius: float) -> Tuple[float, float, float]:
    """Average RGB color inside a disk region."""
    if radius <= 0:
        raise ValueError("radius must be positive")
    arr = np.array(img.convert("RGB"))
    h, w, _ = arr.shape
    cx, cy = center
    x0 = max(int(cx - radius), 0)
    x1 = min(int(cx + radius) + 1, w)
    y0 = max(int(cy - radius), 0)
    y1 = min(int(cy + radius) + 1, h)
    if x0 >= x1 or y0 >= y1:
        return (0.0, 0.0, 0.0)
    y_grid, x_grid = np.ogrid[y0:y1, x0:x1]
    mask = (x_grid - cx) ** 2 + (y_grid - cy) ** 2 <= radius * radius
    if not np.any(mask):
        return (0.0, 0.0, 0.0)
    region = arr[y0:y1, x0:x1][mask]
    mean = region.mean(axis=0)
    return (float(mean[0]), float(mean[1]), float(mean[2]))


def sample_beads(
    img: Image.Image,
    positions: Sequence[Tuple[float, float]],
    radius: float,
) -> List[BeadSample]:
    """Sample colors at bead centers."""
    samples: List[BeadSample] = []
    for pos in positions:
        color = sample_disk_mean(img, pos, radius)
        samples.append(BeadSample(center=pos, color=color))
    return samples
