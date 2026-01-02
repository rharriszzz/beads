"""Color clustering utilities driven by image histograms (no hardcoded palettes)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Tuple, Optional

import numpy as np
from skimage import color

from . import color_peaks

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


def _hsv_distance(a: np.ndarray, b: np.ndarray, weights=(1.0, 0.5, 0.2)) -> np.ndarray:
    """Compute weighted HSV distance with hue wrap; a shape (...,3), b shape (k,3)."""
    dh = np.minimum(np.abs(a[..., 0:1] - b[:, 0]), 1.0 - np.abs(a[..., 0:1] - b[:, 0]))
    ds = np.abs(a[..., 1:2] - b[:, 1])
    dv = np.abs(a[..., 2:3] - b[:, 2])
    w_h, w_s, w_v = weights
    return (w_h * dh) ** 2 + (w_s * ds) ** 2 + (w_v * dv) ** 2


def _mean_hsv(hsv_vals: np.ndarray) -> np.ndarray:
    """Compute mean HSV, handling hue circular mean."""
    if hsv_vals.size == 0:
        return np.array([0.0, 0.0, 0.0])
    h = hsv_vals[:, 0] * 2 * np.pi
    s = hsv_vals[:, 1]
    v = hsv_vals[:, 2]
    h_mean = np.arctan2(np.mean(np.sin(h)), np.mean(np.cos(h))) / (2 * np.pi)
    if h_mean < 0:
        h_mean += 1.0
    return np.array([h_mean, float(s.mean()), float(v.mean())])


def kmeans_palette_hsv(colors: np.ndarray, k: int, iters: int = 10, restarts: int = 5, weights=(1.0, 0.2, 0.1)) -> np.ndarray:
    """k-means in HSV space with hue wrap; returns palette in RGB (0-255)."""
    if colors.size == 0:
        return np.zeros((0, 3), dtype=float)
    arr = color.rgb2hsv(np.clip(colors / 255.0, 0, 1))
    n = arr.shape[0]
    if n < k:
        k = n
    rng = np.random.default_rng()
    best_inertia = float("inf")
    best_centers = None
    for _ in range(restarts):
        centers = arr[rng.choice(n, size=k, replace=False)]
        for _ in range(iters):
            dist2 = _hsv_distance(arr, centers, weights=weights)
            labels = np.argmin(dist2, axis=1)
            new_centers = []
            for i in range(k):
                cluster = arr[labels == i]
                if cluster.size == 0:
                    new_centers.append(centers[i])
                else:
                    new_centers.append(_mean_hsv(cluster.reshape(-1, 3)))
            new_centers = np.array(new_centers)
            if np.allclose(new_centers, centers):
                break
            centers = new_centers
        inertia = float(np.sum(_hsv_distance(arr, centers, weights=weights).min(axis=1)))
        if inertia < best_inertia:
            best_inertia = inertia
            best_centers = centers
    palette_rgb = np.clip(color.hsv2rgb(best_centers) * 255.0, 0, 255)
    return palette_rgb


def label_image_by_palette(img_array: np.ndarray, palette_rgb: np.ndarray, mode: str = "lab"):
    """Assign each pixel to nearest palette color in LAB or HSV."""
    if palette_rgb.size == 0:
        return np.zeros(img_array.shape[:2], dtype=np.int32)
    if mode == "lab":
        return label_image_by_palette_lab(img_array, palette_rgb)
    elif mode == "hsv":
        return label_image_by_palette_hsv(img_array, palette_rgb)
    else:
        raise ValueError("mode must be 'lab' or 'hsv'")


def label_image_by_palette_lab(img_array: np.ndarray, palette_rgb: np.ndarray):
    lab_img = color.rgb2lab(np.clip(img_array / 255.0, 0, 1))
    lab_palette = color.rgb2lab(np.clip(palette_rgb / 255.0, 0, 1))
    h, w, _ = img_array.shape
    flat = lab_img.reshape(-1, 3)
    diff = flat[:, None, :] - lab_palette[None, :, :]
    dist2 = np.sum(diff * diff, axis=2)
    labels = np.argmin(dist2, axis=1).astype(np.int32)
    return labels.reshape(h, w)


def label_image_by_palette_hsv(img_array: np.ndarray, palette_rgb: np.ndarray, weights=(1.0, 0.5, 0.2)):
    hsv_img = color.rgb2hsv(np.clip(img_array / 255.0, 0, 1))
    hsv_palette = color.rgb2hsv(np.clip(palette_rgb / 255.0, 0, 1))
    h, w, _ = img_array.shape
    flat = hsv_img.reshape(-1, 3)
    dist2 = _hsv_distance(flat, hsv_palette, weights=weights)
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


def merge_close_hues(
    palette_rgb: np.ndarray,
    counts: Optional[Sequence[int]] = None,
    hue_tol: float = 0.02,
    sat_tol: float = 1.0,
    val_tol: float = 1.0,
) -> Tuple[np.ndarray, List[int]]:
    """Merge palette entries whose hues are within tolerance (wrap-aware).

    Returns (merged_palette_rgb, mapping_from_original_to_merged).
    """
    if palette_rgb.size == 0:
        return palette_rgb, []
    hsv = color.rgb2hsv(np.clip(palette_rgb / 255.0, 0, 1))
    used = np.zeros(len(hsv), dtype=bool)
    merged = []
    mapping = [-1] * len(hsv)
    # Sort by count (descending) so large clusters anchor merges
    order = np.argsort(-(np.array(counts) if counts is not None else np.ones(len(hsv))))
    for idx in order:
        if used[idx]:
            continue
        anchor = hsv[idx]
        cluster = [idx]
        for j in range(len(hsv)):
            if used[j]:
                continue
            dh = min(abs(anchor[0] - hsv[j][0]), 1.0 - abs(anchor[0] - hsv[j][0]))
            ds = abs(anchor[1] - hsv[j][1])
            dv = abs(anchor[2] - hsv[j][2])
            if dh <= hue_tol and ds <= sat_tol and dv <= val_tol:
                cluster.append(j)
        # Mark used
        for j in cluster:
            used[j] = True
        # Weighted mean in HSV (circular for hue)
        weights = np.array([counts[j] for j in cluster]) if counts is not None else np.ones(len(cluster))
        weights = weights / weights.sum()
        h_angles = hsv[cluster, 0] * 2 * np.pi
        h_mean = np.arctan2(np.sum(np.sin(h_angles) * weights), np.sum(np.cos(h_angles) * weights)) / (2 * np.pi)
        if h_mean < 0:
            h_mean += 1.0
        s_mean = float(np.sum(hsv[cluster, 1] * weights))
        v_mean = float(np.sum(hsv[cluster, 2] * weights))
        merged_hsv = np.array([[h_mean, s_mean, v_mean]])
        merged_rgb = color.hsv2rgb(merged_hsv) * 255.0
        merged_idx = len(merged)
        merged.append(merged_rgb[0])
        for j in cluster:
            mapping[j] = merged_idx
    return np.array(merged, dtype=float), mapping


def palette_from_hist_peaks(
    img_array: np.ndarray,
    mask: Optional[np.ndarray] = None,
    max_colors: int = 6,
    h_bins: int = 72,
    s_bins: int = 16,
    min_prominence: float = 0.02,
    min_separation: float = 0.03,
    radius_h: float = 0.06,
    radius_s: float = 0.25,
    radius_v: float = 0.25,
    background_factor: float = 3.0,
    bead_factor: float = 3.0,
    drop_background: bool = True,
) -> np.ndarray:
    """Estimate a palette from HS histogram peaks instead of a fixed k.

    Peaks are taken from an HS histogram (optionally masked). If the largest peak
    is far larger than the next, it is treated as background. Remaining peaks
    are filtered so their areas stay within `bead_factor` of the largest bead
    peak, then limited to `max_colors`.
    """
    if mask is None:
        mask = np.ones(img_array.shape[:2], dtype=bool)
    hsv = color.rgb2hsv(np.clip(img_array / 255.0, 0, 1))
    peaks = color_peaks.hs_peaks_with_prominence(
        hsv, mask, h_bins=h_bins, s_bins=s_bins, min_prominence=min_prominence, min_separation=min_separation
    )
    if not peaks:
        return np.zeros((0, 3), dtype=float)
    peaks = sorted(peaks, key=lambda p: p[2], reverse=True)
    peak_centers = [(h, s) for h, s, _ in peaks]
    masks = color_peaks.build_peak_masks(
        hsv, mask, peak_centers, radius_h=radius_h, radius_s=radius_s, radius_v=radius_v
    )
    counts = [int(m.sum()) for m in masks]
    ordered = sorted(zip(peak_centers, masks, counts), key=lambda t: t[2], reverse=True)

    start_idx = 0
    if drop_background and len(ordered) > 1 and ordered[0][2] >= background_factor * ordered[1][2]:
        start_idx = 1
    bead_entries = ordered[start_idx:]
    if not bead_entries:
        return np.zeros((0, 3), dtype=float)

    top_bead = bead_entries[0][2]
    bead_entries = [entry for entry in bead_entries if entry[2] >= top_bead / max(1.0, bead_factor)]
    bead_entries = bead_entries[:max_colors]

    palette = []
    for (_, _), m, _ in bead_entries:
        ys, xs = np.nonzero(m)
        if len(ys) == 0:
            continue
        colors = img_array[ys, xs].astype(float)
        palette.append(tuple(np.median(colors, axis=0)))
    if not palette:
        return np.zeros((0, 3), dtype=float)
    return np.array(palette, dtype=float)
