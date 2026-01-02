"""Find dominant color peaks in HSV and build adaptive masks around them."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
from skimage import color
from skimage.feature import peak_local_max
from scipy import ndimage


@dataclass
class ColorPeak:
    center: Tuple[float, float, float]  # HSV center
    radius: float  # radius in HSV space (same units as HSV)
    mask: np.ndarray  # boolean mask of pixels near the peak


def hsv_image(img_array: np.ndarray) -> np.ndarray:
    """Convert RGB [0,255] image to HSV with H,S,V in [0,1]."""
    return color.rgb2hsv(np.clip(img_array / 255.0, 0, 1))


def find_hs_peaks(hsv: np.ndarray, mask: np.ndarray, num_peaks: int = 3, h_bins: int = 72, s_bins: int = 32):
    """Find dominant peaks in HS histogram within the masked region."""
    h = hsv[:, :, 0][mask]
    s = hsv[:, :, 1][mask]
    if h.size == 0:
        return []
    hist, h_edges, s_edges = np.histogram2d(h, s, bins=[h_bins, s_bins], range=[[0, 1], [0, 1]])
    coords = peak_local_max(hist, num_peaks=num_peaks, exclude_border=False)
    peaks = []
    for (h_idx, s_idx) in coords:
        h_center = 0.5 * (h_edges[h_idx] + h_edges[h_idx + 1])
        s_center = 0.5 * (s_edges[s_idx] + s_edges[s_idx + 1])
        peaks.append((h_center, s_center))
    return peaks


def hs_peaks_with_prominence(hsv: np.ndarray, mask: np.ndarray, h_bins: int = 72, s_bins: int = 32, min_prominence: float = 0.05, min_separation: float = 0.05):
    """Find HS peaks by prominence and separation; return centers and counts."""
    h = hsv[:, :, 0][mask]
    s = hsv[:, :, 1][mask]
    if h.size == 0:
        return []
    hist, h_edges, s_edges = np.histogram2d(h, s, bins=[h_bins, s_bins], range=[[0, 1], [0, 1]])
    hist_sm = ndimage.gaussian_filter(hist, sigma=1.0)
    max_val = hist_sm.max()
    coords = peak_local_max(hist_sm, exclude_border=False)
    peaks = []
    for (h_idx, s_idx) in coords:
        val = hist_sm[h_idx, s_idx]
        if val < min_prominence * max_val:
            continue
        h_center = 0.5 * (h_edges[h_idx] + h_edges[h_idx + 1])
        s_center = 0.5 * (s_edges[s_idx] + s_edges[s_idx + 1])
        peaks.append((h_center, s_center, val))
    # Enforce separation
    selected = []
    for hc, sc, val in sorted(peaks, key=lambda p: p[2], reverse=True):
        if all(np.minimum(np.abs(hc - ph), 1.0 - np.abs(hc - ph)) >= min_separation or abs(sc - ps) >= min_separation for ph, ps, _ in selected):
            selected.append((hc, sc, val))
    return selected


def build_peak_masks(
    hsv: np.ndarray,
    mask: np.ndarray,
    peaks: List[Tuple[float, float]],
    radius_h: float = 0.08,
    radius_s: float = 0.25,
    radius_v: float = 0.25,
):
    """Build masks around HS peaks using separable thresholds."""
    h = hsv[:, :, 0]
    s = hsv[:, :, 1]
    v = hsv[:, :, 2]
    masks = []
    for (hc, sc) in peaks:
        dh = np.minimum(np.abs(h - hc), 1.0 - np.abs(h - hc))  # wrap hue
        ds = np.abs(s - sc)
        # Clamp V window around median of masked pixels near the HS center
        v_center = float(np.median(v[(dh <= radius_h) & (ds <= radius_s) & mask])) if mask.any() else 0.5
        dv = np.abs(v - v_center)
        band = (dh <= radius_h) & (ds <= radius_s) & (dv <= radius_v) & mask
        masks.append(band)
    return masks


def adaptive_peak_masks(
    hsv: np.ndarray,
    mask: np.ndarray,
    radius_h: float = 0.08,
    radius_s: float = 0.25,
    radius_v: float = 0.25,
    peaks: List[Tuple[float, float]] | None = None,
):
    """High-level: find peaks and build masks."""
    if peaks is None:
        peaks = find_hs_peaks(hsv, mask, num_peaks=3)
    masks = build_peak_masks(hsv, mask, peaks, radius_h=radius_h, radius_s=radius_s, radius_v=radius_v)
    peaks_full = []
    for (hc, sc), m in zip(peaks, masks):
        center = (hc, sc, float(np.median(hsv[:, :, 2][m]) if m.any() else 0.5))
        peaks_full.append(ColorPeak(center=center, radius=0.0, mask=m))
    return peaks_full


def count_peak_components(mask: np.ndarray, min_area: int = 5) -> int:
    """Count connected components in a mask above min_area."""
    labeled, num = ndimage.label(mask)
    if num == 0:
        return 0
    sizes = ndimage.sum(mask, labeled, index=range(1, num + 1))
    return int((sizes >= min_area).sum())


def auto_shrink_peak_masks(
    hsv: np.ndarray,
    mask: np.ndarray,
    num_peaks: int,
    spacing_px: float,
    radii_start=(0.08, 0.25, 0.25),
    radii_min=(0.01, 0.05, 0.05),
    shrink_factor: float = 0.8,
    min_area: int = 5,
):
    """Iteratively shrink HSV radii until component counts stabilize or increase.

    Returns (peaks, (rh, rs, rv))
    """
    rh, rs, rv = radii_start
    best_masks = None
    best_counts = -1
    best_r = (rh, rs, rv)
    peaks = find_hs_peaks(hsv, mask, num_peaks=num_peaks)
    if not peaks:
        return [], best_r
    while rh >= radii_min[0] and rs >= radii_min[1] and rv >= radii_min[2]:
        masks = build_peak_masks(hsv, mask, peaks, radius_h=rh, radius_s=rs, radius_v=rv)
        total_components = sum(count_peak_components(m, min_area=min_area) for m in masks)
        if total_components > best_counts:
            best_counts = total_components
            best_masks = masks
            best_r = (rh, rs, rv)
        else:
            # If counts drop, break
            break
        rh *= shrink_factor
        rs *= shrink_factor
        rv *= shrink_factor
    peaks_full = []
    for (hc, sc), m in zip(peaks, best_masks if best_masks is not None else []):
        center = (hc, sc, float(np.median(hsv[:, :, 2][m]) if m.any() else 0.5))
        peaks_full.append(ColorPeak(center=center, radius=0.0, mask=m))
    return peaks_full, best_r
