"""Geometry helpers for projecting bead centers and measuring angles."""

from __future__ import annotations

from typing import List, Sequence, Tuple

import numpy as np

from .segmentation import Centerline


def project_points_onto_centerline(points: Sequence[Tuple[float, float]], centerline: Centerline):
    """Project points onto centerline; returns arc lengths and projected points."""
    xs = np.array(centerline.xs, dtype=float)
    ys = np.array(centerline.ys, dtype=float)
    cl = np.stack([xs, ys], axis=1)
    segs = cl[1:] - cl[:-1]
    seg_len = np.linalg.norm(segs, axis=1)
    seg_len[seg_len == 0] = 1e-6
    seg_dir = segs / seg_len[:, None]
    cum_len = np.concatenate([[0.0], np.cumsum(seg_len)])

    arc_lengths = []
    projections = []
    tangents = []
    for px, py in points:
        p = np.array([px, py])
        # Find closest segment
        diffs = p[None, :] - cl[:-1]
        t = np.sum(diffs * seg_dir, axis=1) / seg_len
        t_clamped = np.clip(t, 0.0, 1.0)
        proj = cl[:-1] + (t_clamped[:, None] * segs)
        d2 = np.sum((proj - p) ** 2, axis=1)
        idx = int(np.argmin(d2))
        proj_point = proj[idx]
        arc = cum_len[idx] + t_clamped[idx] * seg_len[idx]
        arc_lengths.append(float(arc))
        projections.append((float(proj_point[0]), float(proj_point[1])))
        tangents.append(tuple(seg_dir[idx]))
    return arc_lengths, projections, tangents


def neighbor_angles(projections: Sequence[Tuple[float, float]], tangents: Sequence[Tuple[float, float]]):
    """Compute angles between consecutive projected beads relative to local tangents."""
    angles = []
    for i in range(len(projections) - 1):
        p0 = np.array(projections[i])
        p1 = np.array(projections[i + 1])
        d = p1 - p0
        t = np.array(tangents[i])
        n = np.array([-t[1], t[0]])
        angle = np.arctan2(d.dot(n), d.dot(t))
        angles.append(float(angle))
    return angles
