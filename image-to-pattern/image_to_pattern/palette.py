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


def kmeans_palette(colors: Sequence[Color], k: int, iters: int = 10) -> List[Color]:
    """Simple k-means clustering to derive a palette from samples."""
    if k <= 0:
        raise ValueError("k must be positive")
    arr = np.array(colors, dtype=float)
    if arr.shape[0] < k:
        raise ValueError("Not enough samples for requested k")
    # Init centers using a simple farthest-point heuristic to avoid duplicate seeds.
    centers = [arr[0]]
    # Choose remaining centers
    for _ in range(1, k):
        diff = arr[:, None, :] - np.array(centers)[None, :, :]
        dist2 = np.sum(diff * diff, axis=2)
        min_dist = dist2.min(axis=1)
        next_idx = np.argmax(min_dist)
        centers.append(arr[next_idx])
    centers = np.array(centers)
    for _ in range(iters):
        # Assign
        diff = arr[:, None, :] - centers[None, :, :]
        dist2 = np.sum(diff * diff, axis=2)
        labels = np.argmin(dist2, axis=1)
        # Recompute
        new_centers = []
        for i in range(k):
            cluster = arr[labels == i]
            if cluster.size == 0:
                # Keep old center if empty cluster
                new_centers.append(centers[i])
            else:
                new_centers.append(cluster.mean(axis=0))
        new_centers = np.array(new_centers)
        if np.allclose(new_centers, centers):
            break
        centers = new_centers
    return [tuple(map(float, c)) for c in centers]


def kmeans_indices(colors: Sequence[Color], k: int, iters: int = 10) -> List[int]:
    """Cluster colors then assign indices to nearest derived palette."""
    palette = kmeans_palette(colors, k=k, iters=iters)
    return nearest_palette_indices(colors, palette)
