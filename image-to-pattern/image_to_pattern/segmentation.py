"""Lightweight segmentation helpers for bracelet images.

This module stays minimal (Pillow + numpy) and provides:
  - mask_bracelet: quick background separation via brightness threshold.
  - centerline_from_mask: estimate centerline as the mean row per column.

These are baseline implementations for early testing; real photos may
require better color models and morphology.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple

import numpy as np
from PIL import Image


def mask_bracelet(img: Image.Image, brightness_threshold: int = 230) -> np.ndarray:
    """Return a boolean mask where bracelet pixels are True.

    Assumes light/white background; marks pixels darker than threshold.
    """
    gray = np.array(img.convert("L"))
    mask = gray < brightness_threshold
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
