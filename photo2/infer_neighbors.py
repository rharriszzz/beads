"""Experimental image-space neighbor proposals; no source indices or colors.

The annular frame is estimated from all centroids. This is a deliberately simple
baseline for one roughly elliptical ring, not a general rope tracker. Every output
retains both diagonal/sign conventions; consistency does not certify an edge.
"""
from __future__ import annotations

import numpy as np

PARAMETERS = dict(nearest_count=12, reach_factor=1.6, axial_fraction=.32,
                  ambiguity_ratio=1.15, shape_anisotropy=1.3,
                  shape_max_angle_degrees=30.)


def image_frames(xy, covariance=None):
    """Return oriented tangents from a centroid ellipse, optionally steered by masks.

    The covariance ellipse is an image-only reference, not a recovered 3-D curve.
    Mask eigenvectors have no intrinsic sign and no guaranteed physical-axis name.
    Choose the axis closest to the reference only when anisotropic and within 30°.
    """
    xy = np.asarray(xy, float)
    centered = xy - xy.mean(axis=0)
    scatter = centered.T @ centered / len(xy)
    values, vectors = np.linalg.eigh(scatter)
    if values[0] <= 1e-10:
        raise ValueError('Centroid cloud must span two dimensions')
    gradient = centered @ np.linalg.inv(scatter)
    tangent = np.column_stack((-gradient[:, 1], gradient[:, 0]))
    norms = np.linalg.norm(tangent, axis=1)
    valid = norms > 1e-10
    tangent[valid] /= norms[valid, None]
    tangent[~valid] = (1., 0.)
    steered = np.zeros(len(xy), bool)
    if covariance is not None:
        covariance = np.asarray(covariance, float)
        if covariance.shape != (len(xy), 2, 2) or not np.isfinite(covariance).all():
            raise ValueError('Expected finite per-mask 2x2 covariance')
        for i, cov in enumerate(covariance):
            ev, axes = np.linalg.eigh(cov)
            if ev[0] <= 0 or ev[1] / ev[0] < PARAMETERS['shape_anisotropy']:
                continue
            axis = axes[:, np.argmax(np.abs(axes.T @ tangent[i]))]
            alignment = float(axis @ tangent[i])
            if abs(alignment) < np.cos(np.deg2rad(PARAMETERS['shape_max_angle_degrees'])):
                continue
            tangent[i] = axis if alignment >= 0 else -axis
            steered[i] = True
    return tangent, valid, steered


def infer(xy, covariance=None):
    """Nearest reciprocal proposals in six signed sectors, preserving ambiguities.

    Inputs are anonymous image centroids and optional mask second moments only.
    No N, helicity, camera, bead body axes, index, palette or source layout enters.
    Label rule: transverse positive is +1, forward lower diagonal +6, upper +7.
    The other convention reverses transverse sign and swaps 6/7. Global reversal
    remains an equivalent presentation and is evaluated explicitly downstream.
    """
    xy = np.asarray(xy, float)
    if xy.ndim != 2 or xy.shape[1] != 2 or len(xy) < 4 or not np.isfinite(xy).all():
        raise ValueError('Expected at least four finite image positions')
    tangent, valid, steered = image_frames(xy, covariance)
    normal = np.column_stack((-tangent[:, 1], tangent[:, 0]))
    displacement = xy[None, :, :] - xy[:, None, :]
    distance = np.linalg.norm(displacement, axis=2)
    np.fill_diagonal(distance, np.inf)
    order = np.argsort(distance, axis=1, kind='stable')
    # A local third-neighbor scale limits bridges across large missing regions.
    reach = PARAMETERS['reach_factor'] * np.take_along_axis(distance, order[:, 2:3], axis=1)[:, 0]
    variants = []
    for hand in (1, -1):
        choices, ambiguous, candidates, boundary_ambiguous = {}, [], [], []
        for i in range(len(xy)):
            if not valid[i]:
                continue
            bins = {}
            for j in order[i, :min(PARAMETERS['nearest_count'], len(xy)-1)]:
                j = int(j)
                r = float(distance[i, j])
                if r <= 1e-8 or r > reach[i]:
                    continue
                x = float(displacement[i, j] @ tangent[i])
                y = float(displacement[i, j] @ normal[i]) * hand
                if abs(x) <= PARAMETERS['axial_fraction'] * r:
                    delta = 1 if y >= 0 else -1
                else:
                    sign = 1 if x >= 0 else -1
                    if abs(y) <= 1e-10*r:
                        boundary_ambiguous.append([i, j, [sign*6, sign*7]])
                        continue
                    delta = sign * (7 if sign*y >= 0 else 6)
                bins.setdefault(delta, []).append((r, j))
            for delta, entries in sorted(bins.items()):
                entries.sort()
                candidates.append([i, delta, [[j, r] for r, j in entries]])
                if len(entries) > 1 and entries[1][0] <= PARAMETERS['ambiguity_ratio'] * entries[0][0]:
                    ambiguous.append([i, delta, [j for r, j in entries
                                               if r <= PARAMETERS['ambiguity_ratio']*entries[0][0]]])
                    continue
                choices[i, delta] = entries[0][1]
        edges, nonreciprocal = [], []
        for (i, d), j in sorted(choices.items()):
            if choices.get((j, -d)) == i:
                if i < j:
                    edges.append([i, j, d])
            else:
                nonreciprocal.append([i, j, d])
        variants.append(dict(convention=hand, edges=edges, ambiguous=ambiguous,
                             boundary_ambiguous=boundary_ambiguous,
                             nonreciprocal=nonreciprocal, candidates=candidates))
    return dict(parameters=PARAMETERS, tangent=tangent.tolist(), valid_frame=valid.tolist(),
                shape_steered=steered.tolist(), variants=variants)
