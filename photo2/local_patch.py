"""Calibrated local contour registration. Observed truth never enters this module.

Candidate label images are forward model predictions, not observed ID passes.
Index assignments remain conditional on candidate helicity and accepted image support.
"""
from __future__ import annotations

import numpy as np
from scipy import ndimage as ndi
from scipy.optimize import least_squares
from skimage.color import rgb2gray, rgb2hsv
from skimage.filters import sobel
from skimage.segmentation import find_boundaries

PARAMETERS = dict(edge_threshold=.035, sigma=1., distance_cap=12., support_distance=2.5,
                  support_fraction=.60, min_pixels=100, max_points=1500,
                  coefficient_bound=16., regularization=.20, max_nfev=60,
                  tie_pixels=.5, anchor_margin=8, border=12)


def image_evidence(rgb, mode='sv'):
    """SV keeps hue wrap out of the edge metric; highlights also change value."""
    if mode not in ('sv', 'gray'):
        raise ValueError('Unknown evidence mode')
    channels = (np.moveaxis(rgb2hsv(rgb)[..., 1:], -1, 0) if mode == 'sv'
                else rgb2gray(rgb)[None])
    strength = np.max([sobel(ndi.gaussian_filter(c, PARAMETERS['sigma'])) for c in channels], axis=0)
    edge = strength >= PARAMETERS['edge_threshold']
    distance = (ndi.distance_transform_edt(~edge) if edge.any()
                else np.full(edge.shape, PARAMETERS['distance_cap']))
    return edge, np.minimum(distance, PARAMETERS['distance_cap'])


def basis(y, height):
    q = (np.asarray(y)-(height-1)/2)/(height/2)
    return np.stack([np.ones_like(q), q, q*q-1/3], axis=-1)


def displace(xy, coefficients, height):
    return np.asarray(xy)+basis(np.asarray(xy)[..., 1], height) @ np.asarray(coefficients).reshape(3, 2)


def inverse_grid(shape, coefficients):
    yy, xx = np.indices(shape, dtype=float)
    target = np.stack([xx, yy], axis=-1)
    source = target.copy()
    for _ in range(15):
        source = target-basis(source[..., 1], shape[0]) @ np.asarray(coefficients).reshape(3, 2)
    return source[..., 1], source[..., 0]


def warp(array, coefficients, *, order=0, background=0):
    coords = inverse_grid(array.shape[:2], coefficients)
    if array.ndim == 2:
        return ndi.map_coordinates(array, coords, order=order, mode='constant', cval=background)
    return np.stack([ndi.map_coordinates(array[..., i], coords, order=order,
                     mode='constant', cval=background) for i in range(array.shape[2])], axis=-1)


def contour_points(labels):
    boundary = find_boundaries(labels, mode='inner') & (labels > 0)
    b = PARAMETERS['border']
    boundary[:b] = False; boundary[-b:] = False
    boundary[:, :b] = False; boundary[:, -b:] = False
    yy, xx = np.nonzero(boundary)
    return np.column_stack([xx, yy])


def distances(distance, xy):
    return ndi.map_coordinates(distance, np.asarray(xy).T[::-1], order=1,
                               mode='constant', cval=PARAMETERS['distance_cap'])


def fit(labels, distance, method):
    """Top 2/3 contour coordinates fit; bottom 1/3 are a spatial holdout.

    q is the vertical local tangent approximation on this fixed right-side patch.
    Coefficients describe normal(x)/tangent(y) displacement, not 3-D deformation.
    """
    if method not in ('fixed', 'translation', 'smooth'):
        raise ValueError('Unknown alignment method')
    points = contour_points(labels)
    train = points[points[:, 1] < labels.shape[0]*2/3]
    hold = points[points[:, 1] >= labels.shape[0]*2/3]
    if len(train) > PARAMETERS['max_points']:
        train = train[np.linspace(0, len(train)-1, PARAMETERS['max_points']).astype(int)]
    if not len(train):
        raise ValueError('Candidate has no fitting contour')
    n = 2 if method == 'translation' else 6
    def expand(p):
        c = np.zeros(6); c[:len(p)] = p
        return c
    def residual(p):
        c = expand(p)
        d = distances(distance, displace(train, c, labels.shape[0]))
        # Regularization scaled by sample count, independent of contour density.
        return np.r_[d, np.sqrt(len(d))*PARAMETERS['regularization']*c[2:]]
    initial = np.zeros(n)
    if method != 'fixed':
        # Deterministic bounded capture search; independent of synthetic truth warp.
        choices = []
        for dx in (-12., -6., 0., 6., 12.):
            for dy in (-12., -6., 0., 6., 12.):
                p = np.zeros(n); p[:2] = dx, dy
                choices.append((float(np.mean(residual(p)**2)), dx, dy))
        _, initial[0], initial[1] = min(choices)
        solved = least_squares(residual, initial, bounds=(-PARAMETERS['coefficient_bound'],
                    PARAMETERS['coefficient_bound']), diff_step=.02, max_nfev=PARAMETERS['max_nfev'])
        c = expand(solved.x)
        optimizer = dict(success=bool(solved.success), status=int(solved.status), nfev=int(solved.nfev))
    else:
        c = np.zeros(6)
        optimizer = None
    moved = displace(points, c, labels.shape[0])
    train_d = distances(distance, displace(train, c, labels.shape[0]))
    hold_d = distances(distance, displace(hold, c, labels.shape[0]))
    return dict(coefficients=c.tolist(), train_mean=float(train_d.mean()),
                holdout_mean=float(hold_d.mean()) if len(hold_d) else None,
                all_mean=float(distances(distance, moved).mean()),
                train_points=len(train), holdout_points=len(hold), optimizer=optimizer)


def assess(labels, distance, anchors, palette, rgb):
    """Support is an image test, not proof: retain failures and hypothesis indices."""
    from detect_beads import color_classes, PALETTES
    classes, _ = color_classes(rgb, PALETTES[palette])
    anchor_labels = []
    for x, y in anchors:
        x, y = int(round(x)), int(round(y))
        anchor_labels.append(int(labels[y, x]) if 0 <= x < labels.shape[1] and 0 <= y < labels.shape[0] else 0)
    nonzero = all(anchor_labels)
    distinct = len(set(anchor_labels)) == len(anchor_labels)
    edges = [[i, j, b-a] for i, a in enumerate(anchor_labels) for j, b in enumerate(anchor_labels)
             if i < j and a and b and abs(b-a) in (1, 6, 7)]
    families = sorted({abs(e[2]) for e in edges})
    reached = {0}
    for _ in anchors:
        for i, j, _ in edges:
            if i in reached or j in reached:
                reached.update((i, j))
    anchor_ok = bool(nonzero and distinct and len(reached) == len(anchors) and families == [1, 6, 7])
    # Distance from click to candidate boundary is a separate diagnostic.
    margins = [float(ndi.distance_transform_edt(labels == a)[int(round(y)), int(round(x))])
               if a else 0. for a, (x, y) in zip(anchor_labels, anchors)]
    anchor_ok = anchor_ok and min(margins) >= PARAMETERS['anchor_margin']
    seed = anchor_labels[0]
    objects = []
    boundary = find_boundaries(labels, mode='inner')
    for label in np.unique(labels):
        if label == 0:
            continue
        mask = labels == label
        yy, xx = np.nonzero(mask)
        if len(xx) < PARAMETERS['min_pixels']:
            continue
        touches = bool(xx.min() < PARAMETERS['border'] or yy.min() < PARAMETERS['border'] or
                       xx.max() >= labels.shape[1]-PARAMETERS['border'] or
                       yy.max() >= labels.shape[0]-PARAMETERS['border'])
        d = distance[boundary & mask]
        fraction = float(np.mean(d <= PARAMETERS['support_distance'])) if len(d) else 0.
        supported = fraction >= PARAMETERS['support_fraction'] and not touches
        votes = np.bincount(classes[mask], minlength=len(PALETTES[palette])+1)
        best = int(np.argmax(votes[1:]))+1
        color = PALETTES[palette][best-1] if votes[best]/len(xx) >= .6 else 'unknown'
        objects.append(dict(model_label=int(label), pixels=len(xx), support_fraction=fraction,
                            mean_boundary_distance=float(d.mean()) if len(d) else None,
                            touches_crop=touches, supported=supported, color=color,
                            candidate_relative_index=int(label-seed) if seed else None,
                            relative_index=int(label-seed) if seed and supported and anchor_ok else None))
    return dict(anchor_labels=anchor_labels, anchor_edges=edges, anchor_families=families,
                anchor_margins=margins, anchor_ok=anchor_ok, objects=objects)


def retained_hypotheses(candidates):
    """Keep both hands unless a valid anchor and fitted contour score distinguish them.

    No ground truth, holdout score or color pattern is used to select a hypothesis.
    """
    eligible = [c for c in candidates if c['assessment']['anchor_ok']]
    if not eligible:
        return []
    best = min(c['fit']['train_mean'] for c in eligible)
    return [c['name'] for c in eligible if c['fit']['train_mean'] <= best+PARAMETERS['tie_pixels']]
