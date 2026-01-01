"""Palette utilities for mapping sampled bead colors to pattern indices."""

from __future__ import annotations

from typing import Iterable, List, Sequence, Tuple

import numpy as np

Color = Tuple[float, float, float]


def nearest_palette_indices(
    colors: Sequence[Color], palette: Sequence[Color]
) -> List[int]:
    """Assign each color to the nearest palette entry (Euclidean in RGB)."""
    if len(palette) == 0:
        raise ValueError("Palette is empty")
    palette_arr = np.array(palette, dtype=float)
    out: List[int] = []
    for color in colors:
        diff = palette_arr - np.array(color, dtype=float)
        dist2 = np.sum(diff * diff, axis=1)
        out.append(int(np.argmin(dist2)))
    return out


def mean_palette_color(samples: Sequence[Color]) -> Color:
    """Compute the mean RGB of provided samples."""
    if len(samples) == 0:
        raise ValueError("No samples provided")
    arr = np.array(samples, dtype=float)
    mean = arr.mean(axis=0)
    return (float(mean[0]), float(mean[1]), float(mean[2]))
