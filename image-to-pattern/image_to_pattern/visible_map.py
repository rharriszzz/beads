"""Construct visibility and center map for beads along the chain."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

import numpy as np
from PIL import Image

from . import color_peaks, segmentation
from .bead_detect import detect_bead_centers
from .bead_graph import order_beads_by_mst
from .sampling import centerline_length


@dataclass
class BeadVisibility:
    visible: bool
    center: Optional[Tuple[float, float]] = None
    color_id: Optional[int] = None


def build_visibility_map(
    img: Image.Image,
    expected_beads: int,
    num_peaks: int = 3,
    min_coverage: float = 0.3,
) -> List[BeadVisibility]:
    """Derive per-bead visibility and centers using color peaks and detection."""
    mask = segmentation.mask_bracelet(img)
    geom = segmentation.estimate_geometry(mask)
    hsv = color_peaks.hsv_image(np.array(img))
    peaks, _ = color_peaks.auto_shrink_peak_masks(
        hsv,
        mask,
        num_peaks=num_peaks,
        spacing_px=geom.spacing_px,
    )
    # Combine masks and keep color ids
    combined = np.zeros_like(mask, dtype=bool)
    colored_masks: List[Tuple[int, np.ndarray]] = []
    for idx, p in enumerate(peaks):
        combined |= p.mask
        colored_masks.append((idx, p.mask))

    detected = detect_bead_centers(combined, spacing_px=geom.spacing_px)
    ordered = order_beads_by_mst(detected)

    # Map detected centers to bead_index grid by nearest arc-length
    cl = segmentation.centerline_from_mask(mask)
    arc_len = centerline_length(cl)
    if expected_beads <= 0 or arc_len <= 0:
        return [BeadVisibility(False) for _ in range(expected_beads or 0)]
    ideal_spacing = arc_len / expected_beads

    # Compute arc-length for detected centers
    xs = np.array(cl.xs, dtype=float)
    ys = np.array(cl.ys, dtype=float)
    cl_pts = np.stack([xs, ys], axis=1)
    segs = cl_pts[1:] - cl_pts[:-1]
    seg_len = np.linalg.norm(segs, axis=1)
    seg_len[seg_len == 0] = 1e-6
    seg_dir = segs / seg_len[:, None]
    cum_len = np.concatenate([[0.0], np.cumsum(seg_len)])

    def project_point(pt: Tuple[float, float]) -> float:
        p = np.array(pt)
        diffs = p[None, :] - cl_pts[:-1]
        t = np.sum(diffs * seg_dir, axis=1) / seg_len
        t_clamped = np.clip(t, 0.0, 1.0)
        proj = cl_pts[:-1] + (t_clamped[:, None] * segs)
        d2 = np.sum((proj - p) ** 2, axis=1)
        idx = int(np.argmin(d2))
        return float(cum_len[idx] + t_clamped[idx] * seg_len[idx])

    detected_arc = [project_point(c) for c in ordered.centers]

    vis = [BeadVisibility(False) for _ in range(expected_beads)]
    for center, arc in zip(ordered.centers, detected_arc):
        bead_idx = int(round(arc / ideal_spacing))
        if 0 <= bead_idx < expected_beads:
            vis[bead_idx].visible = True
            vis[bead_idx].center = center

    # Assign color ids by which peak mask contains the center
    for b in vis:
        if b.visible and b.center:
            x, y = b.center
            xi, yi = int(round(x)), int(round(y))
            for color_id, m in colored_masks:
                if 0 <= yi < m.shape[0] and 0 <= xi < m.shape[1] and m[yi, xi]:
                    b.color_id = color_id
                    break
    return vis
