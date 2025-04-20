# quantization.py

import numpy as np
from sklearn.cluster import MiniBatchKMeans
import cv2

def fit_color_palette(image, props, n_colors):
    """
    Perform quantization on the union of all bead-region pixels.
    """
    # Collect pixels from bead regions
    mask = np.zeros(image.shape[:2], bool)
    for r in props:
        coords = r.coords
        mask[coords[:,0], coords[:,1]] = True

    pixels = image[mask].reshape(-1, 3)  # :contentReference[oaicite:5]{index=5}
    kmeans = MiniBatchKMeans(n_clusters=n_colors, random_state=0)  # :contentReference[oaicite:6]{index=6}
    kmeans.fit(pixels)
    return kmeans.cluster_centers_.astype(int), kmeans

def assign_color_and_certainty(image, props, palette, expected_area):
    """
    For each bead region, assign nearest palette index and compute certainty.
    """
    bead_data = []
    for r in props:
        # Sample mean color in region
        minr, minc, maxr, maxc = r.bbox
        roi = image[minr:maxr, minc:maxc]
        mask = (r.image)
        colors = roi[mask]
        mean_color = colors.mean(axis=0)
        # Find nearest palette color
        dists = np.linalg.norm(palette - mean_color, axis=1)
        color_index = int(np.argmin(dists))
        # Certainty = min(1, area/expected_area)
        certainty = min(1.0, r.area / expected_area)
        bead_data.append((r.label-1, color_index, certainty))
    return bead_data
