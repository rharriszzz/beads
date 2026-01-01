"""Bead detection helpers using distance transform peaks on the bracelet mask."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
from scipy import ndimage
from skimage.feature import peak_local_max


@dataclass
class DetectedBead:
    center: Tuple[float, float]  # (x, y)
    distance: float  # distance transform value (proxy for radius/coverage)


def detect_bead_centers(mask: np.ndarray, spacing_px: float, min_distance_scale: float = 0.6) -> List[DetectedBead]:
    """Detect bead centers from a binary mask using distance-transform peaks.

    Args:
        mask: boolean array, True on bracelet pixels.
        spacing_px: expected bead spacing (used to set min_distance between peaks).
        min_distance_scale: fraction of spacing to enforce between peaks.

    Returns:
        List of DetectedBead with image-plane coordinates (x, y).
    """
    if mask.ndim != 2:
        raise ValueError("mask must be 2D")
    if spacing_px <= 0:
        raise ValueError("spacing_px must be positive")
    if not np.any(mask):
        return []

    dist = ndimage.distance_transform_edt(mask)
    min_dist = max(1, int(spacing_px * min_distance_scale))
    peaks = peak_local_max(dist, min_distance=min_dist, threshold_abs=1, labels=mask, exclude_border=False)

    beads: List[DetectedBead] = []
    for (y, x) in peaks:
        beads.append(DetectedBead(center=(float(x), float(y)), distance=float(dist[y, x])))
    return beads
