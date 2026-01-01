"""Segmentation helpers for bracelet images.

This module stays minimal (Pillow + numpy + optional scipy) and provides:
  - mask_bracelet: quick background separation via brightness threshold,
    with optional morphology cleanup.
  - centerline_from_mask: estimate centerline as the mean row per column.
  - band_widths: estimate bracelet thickness per column for spacing/radius.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple

import numpy as np
from scipy import ndimage
from PIL import Image


def mask_bracelet(
    img: Image.Image,
    brightness_threshold: Optional[int] = None,
    min_component_area: Optional[int] = None,
) -> np.ndarray:
    """Return a boolean mask where bracelet pixels are True.

    Assumes light/white background; marks pixels darker than threshold.
    Optionally keeps only the largest connected component above a size
    threshold to drop speckle noise.
    """
    gray = np.array(img.convert("L"))
    thresh = brightness_threshold if brightness_threshold is not None else otsu_threshold(gray)
    mask = gray <= thresh

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


@dataclass
class GeometryEstimate:
    thickness_px: float
    spacing_px: float
    radius_px: float


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
    """Return per-column band thickness as the longest run of contiguous True."""
    if mask.ndim != 2:
        raise ValueError("Mask must be 2D boolean array")
    height, width = mask.shape
    widths = np.zeros(width, dtype=float)
    for x in range(width):
        col = mask[:, x]
        widths[x] = float(_longest_run(col))
    return widths


def estimate_geometry(
    mask: np.ndarray,
    spacing_scale: float = 1.05,
    radius_scale: float = 0.45,
) -> GeometryEstimate:
    """Estimate bead spacing/radius from mask thickness.

    Uses the median nonzero band width; spacing/radius scales are heuristic
    and can be tuned. spacing_scale > 1 gives slight separation.
    """
    widths = band_widths(mask)
    nz = widths[widths > 0]
    if nz.size == 0:
        raise ValueError("No mask coverage to estimate geometry")
    thickness = float(np.median(nz))
    spacing = float(thickness * spacing_scale)
    radius = float(thickness * radius_scale)
    return GeometryEstimate(thickness_px=thickness, spacing_px=spacing, radius_px=radius)


def otsu_threshold(gray: np.ndarray) -> int:
    """Compute Otsu's threshold for a grayscale image."""
    if gray.ndim != 2:
        raise ValueError("Expected 2D grayscale array")
    hist, bin_edges = np.histogram(gray.ravel(), bins=256, range=(0, 256))
    total = gray.size
    sum_total = np.dot(hist, np.arange(256))

    sum_b = 0.0
    w_b = 0.0
    max_var = -1.0
    threshold = 0
    for t in range(256):
        w_b += hist[t]
        if w_b == 0:
            continue
        w_f = total - w_b
        if w_f == 0:
            break
        sum_b += t * hist[t]
        m_b = sum_b / w_b
        m_f = (sum_total - sum_b) / w_f
        var_between = w_b * w_f * (m_b - m_f) ** 2
        if var_between > max_var:
            max_var = var_between
            threshold = t
    return int(threshold)


def _longest_run(col: np.ndarray) -> int:
    """Return length of the longest contiguous True run in a 1D boolean array."""
    if col.size == 0:
        return 0
    # Pad with False to flush any trailing run
    padded = np.concatenate([[False], col.astype(bool), [False]])
    diffs = np.diff(padded.astype(int))
    starts = np.flatnonzero(diffs == 1)
    ends = np.flatnonzero(diffs == -1)
    if starts.size == 0:
        return 0
    lengths = ends - starts
    return int(lengths.max())
