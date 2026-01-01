"""Color clustering utilities driven by image histograms (no hardcoded palettes)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Tuple

import numpy as np
from skimage import color

Color = Tuple[float, float, float]


def sample_masked_pixels(img_array: np.ndarray, mask: np.ndarray, max_samples: int = 5000) -> np.ndarray:
    """Randomly sample RGB pixels from masked region."""
    assert img_array.ndim == 3 and img_array.shape[2] == 3
    ys, xs = np.nonzero(mask)
    if ys.size == 0:
        return np.zeros((0, 3), dtype=float)
    idx = np.arange(ys.size)
    if ys.size > max_samples:
        idx = np.random.choice(idx, size=max_samples, replace=False)
    pixels = img_array[ys[idx], xs[idx]]
    return pixels.astype(float)


def kmeans_palette_lab(colors: np.ndarray, k: int, iters: int = 10, restarts: int = 5) -> np.ndarray:
    """k-means in LAB space on given RGB colors (0-255). Returns palette in RGB (0-255)."""
    if colors.size == 0:
        return np.zeros((0, 3), dtype=float)
    arr = color.rgb2lab(np.clip(colors / 255.0, 0, 1))
    best_centers_lab = None
    best_inertia = float("inf")
    rng = np.random.default_rng()
    for _ in range(restarts):
        centers = arr[rng.choice(len(arr), size=k, replace=False)]
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
        inertia = float(np.sum((arr - centers[labels]) ** 2))
        if inertia < best_inertia:
            best_inertia = inertia
            best_centers_lab = centers
    palette_rgb = np.clip(color.lab2rgb(best_centers_lab) * 255.0, 0, 255)
    return palette_rgb


def label_image_by_palette(img_array: np.ndarray, palette_rgb: np.ndarray) -> np.ndarray:
    """Assign each pixel to nearest palette color in LAB space."""
    lab_img = color.rgb2lab(np.clip(img_array / 255.0, 0, 1))
    lab_palette = color.rgb2lab(np.clip(palette_rgb / 255.0, 0, 1))
    h, w, _ = img_array.shape
    flat = lab_img.reshape(-1, 3)
    diff = flat[:, None, :] - lab_palette[None, :, :]
    dist2 = np.sum(diff * diff, axis=2)
    labels = np.argmin(dist2, axis=1).astype(np.int32)
    return labels.reshape(h, w)


def most_separable_labels(palette_rgb: np.ndarray, top_n: int = 2) -> List[int]:
    """Return indices of palette colors with largest pairwise distances."""
    if palette_rgb.shape[0] == 0:
        return []
    lab = color.rgb2lab(np.clip(palette_rgb / 255.0, 0, 1))
    k = lab.shape[0]
    dists = np.linalg.norm(lab[None, :, :] - lab[:, None, :], axis=2)
    # Sum distances to others; pick top_n by separability
    scores = dists.sum(axis=1)
    order = np.argsort(-scores)
    return order[:top_n].tolist()
