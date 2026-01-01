"""Palette utilities for mapping sampled bead colors to pattern indices."""

from __future__ import annotations

from typing import Iterable, List, Sequence, Tuple

import numpy as np
from skimage import color

Color = Tuple[float, float, float]


def nearest_palette_indices(
    colors: Sequence[Color], palette: Sequence[Color], use_lab: bool = False
) -> List[int]:
    """Assign each color to the nearest palette entry (Euclidean in RGB)."""
    if len(palette) == 0:
        raise ValueError("Palette is empty")
    palette_arr = np.array(palette, dtype=float)
    color_arr = np.array(colors, dtype=float)
    if use_lab:
        # Convert from [0,255] RGB to LAB for perceptual distance
        palette_arr = color.rgb2lab(np.clip(palette_arr / 255.0, 0, 1))
        color_arr = color.rgb2lab(np.clip(color_arr / 255.0, 0, 1))
    out: List[int] = []
    for c in color_arr:
        diff = palette_arr - c
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


def kmeans_palette(colors: Sequence[Color], k: int, iters: int = 10, restarts: int = 3, use_lab: bool = False) -> List[Color]:
    """Simple k-means clustering to derive a palette from samples."""
    if k <= 0:
        raise ValueError("k must be positive")
    arr = np.array(colors, dtype=float)
    if use_lab:
        arr = color.rgb2lab(np.clip(arr / 255.0, 0, 1))
    if arr.shape[0] < k:
        raise ValueError("Not enough samples for requested k")
    best_inertia = float("inf")
    best_centers = None
    rng = np.random.default_rng()
    for _ in range(restarts):
        # Init centers using a simple farthest-point heuristic to avoid duplicate seeds.
        centers = [arr[rng.integers(0, len(arr))]]
        for _ in range(1, k):
            diff = arr[:, None, :] - np.array(centers)[None, :, :]
            dist2 = np.sum(diff * diff, axis=2)
            min_dist = dist2.min(axis=1)
            next_idx = int(np.argmax(min_dist))
            centers.append(arr[next_idx])
        centers = np.array(centers)
        for _ in range(iters):
            diff = arr[:, None, :] - centers[None, :, :]
            dist2 = np.sum(diff * diff, axis=2)
            labels = np.argmin(dist2, axis=1)
            new_centers = []
            for i in range(k):
                cluster = arr[labels == i]
                if cluster.size == 0:
                    new_centers.append(centers[i])
                else:
                    new_centers.append(cluster.mean(axis=0))
            new_centers = np.array(new_centers)
            if np.allclose(new_centers, centers):
                break
            centers = new_centers
        inertia = 0.0
        diff = arr - centers[labels]
        inertia = float(np.sum(diff * diff))
        if inertia < best_inertia:
            best_inertia = inertia
            best_centers = centers
    return [tuple(map(float, c)) for c in best_centers]


def kmeans_indices(colors: Sequence[Color], k: int, iters: int = 10) -> List[int]:
    """Cluster colors then assign indices to nearest derived palette."""
    palette = kmeans_palette(colors, k=k, iters=iters, restarts=3, use_lab=True)
    return nearest_palette_indices(colors, palette, use_lab=True)
