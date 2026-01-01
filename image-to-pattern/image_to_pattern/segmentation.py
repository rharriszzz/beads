"""Segmentation helpers for bracelet images.

This module stays minimal (Pillow + numpy + optional scipy) and provides:
  - mask_bracelet: quick background separation via brightness threshold,
    with optional morphology cleanup.
  - centerline_from_mask: estimate centerline as the mean row per column.
  - band_widths: estimate bracelet thickness per column for spacing/radius.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple

import numpy as np
from scipy import ndimage
from PIL import Image


def mask_bracelet(
    img: Image.Image,
    brightness_threshold: int = 230,
    min_component_area: int | None = None,
) -> np.ndarray:
    """Return a boolean mask where bracelet pixels are True.

    Assumes light/white background; marks pixels darker than threshold.
    Optionally keeps only the largest connected component above a size
    threshold to drop speckle noise.
    """
    gray = np.array(img.convert("L"))
    mask = gray < brightness_threshold

    if min_component_area:
        labeled, num = ndimage.label(mask)
        if num > 0:
            sizes = ndimage.sum(mask, labeled, index=range(1, num + 1))
            keep = sizes >= min_component_area
            # Map keep flags back to labels
            if keep.any():
                mask = keep[(labeled - 1).clip(min=0)]

    # Light morphology to close pinholes
    mask = ndimage.binary_closing(mask, iterations=1)
    return mask


@dataclass
class Centerline:
    xs: List[int]
    ys: List[float]


def centerline_from_mask(mask: np.ndarray) -> Centerline:
    """Estimate centerline as mean y for each x where mask has coverage."""
    if mask.ndim != 2:
        raise ValueError("Mask must be 2D boolean array")
    height, width = mask.shape
    xs: List[int] = []
    ys: List[float] = []
    for x in range(width):
        ys_at_x = np.flatnonzero(mask[:, x])
        if ys_at_x.size == 0:
            continue
        xs.append(x)
        ys.append(float(np.mean(ys_at_x)))
    if not xs:
        raise ValueError("No mask columns with coverage; cannot compute centerline")
    return Centerline(xs=xs, ys=ys)


def centerline_rmse(centerline: Centerline, target_y: float) -> float:
    """Compute RMSE of centerline y-values vs a target y."""
    if not centerline.ys:
        return float("inf")
    diffs = np.array(centerline.ys) - target_y
    return float(np.sqrt(np.mean(diffs**2)))


def band_widths(mask: np.ndarray) -> np.ndarray:
    """Return per-column band thickness (max-min y) where mask is present."""
    if mask.ndim != 2:
        raise ValueError("Mask must be 2D boolean array")
    height, width = mask.shape
    widths = np.zeros(width, dtype=float)
    ys = np.arange(height)
    for x in range(width):
        col = mask[:, x]
        if not col.any():
            widths[x] = 0.0
            continue
        present = ys[col]
        widths[x] = float(present.max() - present.min() + 1)
    return widths
