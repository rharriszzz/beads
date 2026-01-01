"""Find dominant color peaks in HSV and build adaptive masks around them."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
from skimage import color
from skimage.feature import peak_local_max


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


def build_peak_masks(hsv: np.ndarray, mask: np.ndarray, peaks: List[Tuple[float, float]], radius_h: float = 0.08, radius_s: float = 0.25):
    """Build masks around HS peaks using elliptical thresholds."""
    h = hsv[:, :, 0]
    s = hsv[:, :, 1]
    masks = []
    for (hc, sc) in peaks:
        dh = np.minimum(np.abs(h - hc), 1.0 - np.abs(h - hc))  # wrap hue
        ds = np.abs(s - sc)
        band = (dh <= radius_h) & (ds <= radius_s) & mask
        masks.append(band)
    return masks


def adaptive_peak_masks(hsv: np.ndarray, mask: np.ndarray, num_peaks: int = 3):
    """High-level: find peaks and build masks."""
    peaks = find_hs_peaks(hsv, mask, num_peaks=num_peaks)
    masks = build_peak_masks(hsv, mask, peaks)
    peaks_full = []
    for (hc, sc), m in zip(peaks, masks):
        center = (hc, sc, float(np.median(hsv[:, :, 2][m]) if m.any() else 0.5))
        peaks_full.append(ColorPeak(center=center, radius=0.0, mask=m))
    return peaks_full
