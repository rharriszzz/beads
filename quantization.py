"""
quantization.py
---------------
Color‐quantization on bead regions and per‐region color & certainty assignment.
"""

import numpy as np
from sklearn.cluster import MiniBatchKMeans
import cv2

def fit_color_palette(image, props, n_colors):
    """
    Perform K‑Means color clustering over bead-region pixels.

    Uses MiniBatchKMeans for speed on large images :contentReference[oaicite:7]{index=7}.
    """
    # Build mask of all bead regions to ignore background :contentReference[oaicite:8]{index=8}
    mask = np.zeros(image.shape[:2], bool)
    for r in props:
        mask[r.coords[:,0], r.coords[:,1]] = True

    pixels = image[mask].reshape(-1, 3)
    kmeans = MiniBatchKMeans(n_clusters=n_colors, random_state=0)
    kmeans.fit(pixels)
    return kmeans.cluster_centers_.astype(int), kmeans

def assign_color_and_certainty(image, props, palette, expected_area):
    """
    For each bead region, compute:
      - color_index: nearest palette centroid (0..n_colors-1)
      - certainty   : area_ratio = region.area/expected_area (clamped to [0,1])
    """
    bead_data = []
    for r in props:
        minr, minc, maxr, maxc = r.bbox
        roi = image[minr:maxr, minc:maxc]
        mask = r.image  # boolean mask for this region
        colors = roi[mask]
        mean_color = colors.mean(axis=0)
        # nearest palette color by Euclidean distance :contentReference[oaicite:9]{index=9}
        dists = np.linalg.norm(palette - mean_color, axis=1)
        color_index = int(np.argmin(dists))
        # certainty based on observed vs. expected bead area 
        certainty = min(1.0, r.area / expected_area)
        bead_data.append((r.label - 1, color_index, certainty))
    return bead_data
