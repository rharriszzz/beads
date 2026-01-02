"""Segmentation helpers for bracelet images.

This module stays minimal (Pillow + numpy + optional scipy) and provides:
  - mask_bracelet: quick background separation via brightness threshold,
    with optional morphology cleanup.
  - centerline_from_mask: estimate centerline as the mean row per column.
  - band_widths: estimate bracelet thickness per column for spacing/radius.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple

import numpy as np
from scipy import ndimage
from skimage import morphology
from skimage import measure
import networkx as nx
from PIL import Image


def mask_bracelet(
    img: Image.Image,
    brightness_threshold: Optional[int] = None,
    min_component_area: Optional[int] = None,
) -> np.ndarray:
    """Return a boolean mask where bracelet pixels are True.

    Assumes light/white background; marks pixels darker than threshold.
    Optionally keeps only the largest connected component above a size
    threshold to drop speckle noise.
    """
    gray = np.array(img.convert("L"))
    thresh = brightness_threshold if brightness_threshold is not None else otsu_threshold(gray)
    mask = gray <= thresh

    if min_component_area:
        labeled, num = ndimage.label(mask)
        if num > 0:
            sizes = ndimage.sum(mask, labeled, index=range(1, num + 1))
            keep = sizes >= min_component_area
            # Map keep flags back to labels
            if keep.any():
                mask = keep[(labeled - 1).clip(min=0)]

    # Light morphology to close pinholes
    mask = ndimage.binary_closing(mask, iterations=1)
    return mask


@dataclass
class Centerline:
    xs: List[int]
    ys: List[float]


@dataclass
class GeometryEstimate:
    thickness_px: float
    spacing_px: float
    radius_px: float


def centerline_from_mask(mask: np.ndarray) -> Centerline:
    """Estimate centerline via medial axis and ordered skeleton.

    - Downscale large masks for speed.
    - Use medial_axis; if empty, fall back to column means.
    - Order skeleton points:
        * If the shape is elongated, sort along x (or y).
        * Otherwise, sort by polar angle around centroid to trace the loop.
    """
    if mask.ndim != 2:
        raise ValueError("Mask must be 2D boolean array")
    scale = 1.0
    max_pixels = 1_000_000
    if mask.size > max_pixels:
        scale = (max_pixels / mask.size) ** 0.5
        mask = ndimage.zoom(mask.astype(float), zoom=scale, order=0) > 0.5

    # Medial axis skeleton
    skel = morphology.medial_axis(mask.astype(bool))
    pts = np.column_stack(np.nonzero(skel))
    if pts.size == 0:
        # Fallback to column means
        height, width = mask.shape
        xs: List[int] = []
        ys: List[float] = []
        for x in range(width):
            ys_at_x = np.flatnonzero(mask[:, x])
            if ys_at_x.size == 0:
                continue
            xs.append(x)
            ys.append(float(np.mean(ys_at_x)))
        if not xs:
            raise ValueError("No mask columns with coverage; cannot compute centerline")
        return Centerline(xs=[x / scale for x in xs], ys=[y / scale for y in ys])

    pts_xy = np.array([[c, r] for r, c in pts], dtype=float)  # x,y
    min_r, min_c = pts.min(axis=0)
    max_r, max_c = pts.max(axis=0)
    bbox_h = max_r - min_r + 1
    bbox_w = max_c - min_c + 1
    if bbox_w > 1.2 * bbox_h:
        # Treat as horizontal band
        cols = np.nonzero(mask.sum(axis=0) > 0)[0]
        if cols.size == 0:
            raise ValueError("No mask columns with coverage; cannot compute centerline")
        xs = (cols / scale).tolist()
        y_center = float(np.mean(np.nonzero(mask)[0])) / scale
        ys = [y_center for _ in xs]
        return Centerline(xs=xs, ys=ys)
    elif bbox_h > 1.2 * bbox_w:
        # Vertical band
        rows = np.nonzero(mask.sum(axis=1) > 0)[0]
        if rows.size == 0:
            raise ValueError("No mask rows with coverage; cannot compute centerline")
        ys = (rows / scale).tolist()
        x_center = float(np.mean(np.nonzero(mask)[1])) / scale
        xs = [x_center for _ in ys]
        return Centerline(xs=xs, ys=ys)

    ordered = pts_xy
    cx = ordered[:, 0].mean()
    cy = ordered[:, 1].mean()
    ang = np.arctan2(ordered[:, 1] - cy, ordered[:, 0] - cx)
    idxs = np.argsort(ang)
    ordered = ordered[idxs]
    xs = (ordered[:, 0] / scale).tolist()
    ys = (ordered[:, 1] / scale).tolist()
    if len(xs) < 2:
        height, width = mask.shape
        cy = float((min_r + max_r) / 2.0) / scale
        xs = [0.0, float(width - 1)]
        ys = [cy, cy]
    return Centerline(xs=xs, ys=ys)


def centerline_rmse(centerline: Centerline, target_y: float) -> float:
    """Compute RMSE of centerline y-values vs a target y."""
    if not centerline.ys:
        return float("inf")
    diffs = np.array(centerline.ys) - target_y
    return float(np.sqrt(np.mean(diffs**2)))


def midline_between_background(mask: np.ndarray) -> Centerline:
    """Compute a midline equidistant between the two largest interior non-bead regions.

    Excludes any non-bead component touching the image border (outer background),
    then picks the two largest remaining components and computes the locus where
    their distance transforms are equal, thins it, and orders the path.
    """
    if mask.ndim != 2:
        raise ValueError("Mask must be 2D boolean array")
    inv = ~mask
    labeled, num = ndimage.label(inv)
    if num < 2:
        return centerline_from_mask(mask)
    # Filter out components touching border
    keep_labels = []
    for idx in range(1, num + 1):
        comp = labeled == idx
        if (
            comp[0, :].any()
            or comp[-1, :].any()
            or comp[:, 0].any()
            or comp[:, -1].any()
        ):
            continue
        keep_labels.append(idx)
    if len(keep_labels) < 2:
        return centerline_from_mask(mask)
    sizes = ndimage.sum(inv, labeled, index=keep_labels)
    largest_idx = [keep_labels[i] for i in np.argsort(sizes)[-2:]]
    comps = [(labeled == idx) for idx in largest_idx]
    compA, compB = comps
    distA = ndimage.distance_transform_edt(~compA)
    distB = ndimage.distance_transform_edt(~compB)
    diff = np.abs(distA - distB)
    thresh = np.percentile(diff, 1)
    mid = diff <= thresh
    mid = morphology.thin(mid)
    coords = np.column_stack(np.nonzero(mid))
    if coords.size == 0:
        return centerline_from_mask(mask)
    ordered = _order_coords(coords)
    xs = ordered[:, 1].tolist()
    ys = ordered[:, 0].tolist()
    return Centerline(xs=xs, ys=ys)


def _order_coords(coords: np.ndarray) -> np.ndarray:
    """Order coordinates along the longest path of an MST."""
    pts = np.array([[c, r] for r, c in coords], dtype=float)
    n = len(pts)
    if n <= 2:
        return pts
    G = nx.Graph()
    for i in range(n):
        G.add_node(i)
    k = min(8, n - 1)
    for i in range(n):
        d = np.linalg.norm(pts - pts[i], axis=1)
        idxs = np.argsort(d)[1 : k + 1]
        for j_idx in idxs:
            G.add_edge(i, int(j_idx), weight=float(d[j_idx]))
    mst = nx.minimum_spanning_tree(G)
    lengths = dict(nx.all_pairs_dijkstra_path_length(mst))
    max_len = -1
    start = end = 0
    for i in range(n):
        for j, d in lengths[i].items():
            if d > max_len:
                max_len = d
                start, end = i, j
    path = nx.shortest_path(mst, source=start, target=end, weight="weight")
    return pts[path]


def band_widths(mask: np.ndarray) -> np.ndarray:
    """Return per-column band thickness as the longest run of contiguous True."""
    if mask.ndim != 2:
        raise ValueError("Mask must be 2D boolean array")
    height, width = mask.shape
    widths = np.zeros(width, dtype=float)
    for x in range(width):
        col = mask[:, x]
        widths[x] = float(_longest_run(col))
    return widths


def estimate_geometry(
    mask: np.ndarray,
    spacing_scale: float = 1.05,
    radius_scale: float = 0.45,
) -> GeometryEstimate:
    """Estimate bead spacing/radius from mask thickness.

    Uses the median nonzero band width; spacing/radius scales are heuristic
    and can be tuned. spacing_scale > 1 gives slight separation.
    """
    widths = band_widths(mask)
    nz = widths[widths > 0]
    if nz.size == 0:
        raise ValueError("No mask coverage to estimate geometry")
    thickness = float(np.median(nz))
    spacing = float(thickness * spacing_scale)
    radius = float(thickness * radius_scale)
    return GeometryEstimate(thickness_px=thickness, spacing_px=spacing, radius_px=radius)


def otsu_threshold(gray: np.ndarray) -> int:
    """Compute Otsu's threshold for a grayscale image."""
    if gray.ndim != 2:
        raise ValueError("Expected 2D grayscale array")
    hist, bin_edges = np.histogram(gray.ravel(), bins=256, range=(0, 256))
    total = gray.size
    sum_total = np.dot(hist, np.arange(256))

    sum_b = 0.0
    w_b = 0.0
    max_var = -1.0
    threshold = 0
    for t in range(256):
        w_b += hist[t]
        if w_b == 0:
            continue
        w_f = total - w_b
        if w_f == 0:
            break
        sum_b += t * hist[t]
        m_b = sum_b / w_b
        m_f = (sum_total - sum_b) / w_f
        var_between = w_b * w_f * (m_b - m_f) ** 2
        if var_between > max_var:
            max_var = var_between
            threshold = t
    return int(threshold)


def _longest_run(col: np.ndarray) -> int:
    """Return length of the longest contiguous True run in a 1D boolean array."""
    if col.size == 0:
        return 0
    # Pad with False to flush any trailing run
    padded = np.concatenate([[False], col.astype(bool), [False]])
    diffs = np.diff(padded.astype(int))
    starts = np.flatnonzero(diffs == 1)
    ends = np.flatnonzero(diffs == -1)
    if starts.size == 0:
        return 0
    lengths = ends - starts
    return int(lengths.max())
