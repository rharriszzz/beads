"""One-pass image-only assignment of shared enclosed bright cavities."""
from __future__ import annotations

import heapq
import math

import numpy as np
from scipy import ndimage as ndi

from highlight_regions import PARAMETERS as BASE_PARAMETERS, fill_highlights

PARAMETERS = dict(base=BASE_PARAMETERS, connectivity=8, gradient_weight=1.,
                  tie_atol=1e-12, tie_rtol=1e-12, passes=1,
                  path_cost='step_length * (1 + weight * RMS(delta_RGB/255))')
METHODS = ('conservative', 'distance', 'gradient')
STEPS = [(dy, dx, math.hypot(dy, dx)) for dy in (-1, 0, 1)
         for dx in (-1, 0, 1) if dy or dx]


def path_costs(rgb, cavity, sources, gradient):
    """Shortest eight-connected paths; only cavity pixels may be traversed.

    Every adjacent pixel of the requested owner is a zero-cost source. Entering
    the cavity pays the first edge cost, including its RGB change. Other owners
    cannot be crossed. All owners are evaluated independently to retain ties.
    """
    costs = np.full(cavity.shape, np.inf)
    queue = []
    for y, x in zip(*np.nonzero(sources)):
        costs[y, x] = 0.
        heapq.heappush(queue, (0., int(y), int(x)))
    h, w = cavity.shape
    while queue:
        cost, y, x = heapq.heappop(queue)
        if cost > costs[y, x]:
            continue
        for dy, dx, length in STEPS:
            yy, xx = y+dy, x+dx
            if not (0 <= yy < h and 0 <= xx < w and cavity[yy, xx]):
                continue
            change = float(np.sqrt(np.mean((rgb[yy, xx]-rgb[y, x])**2))) if gradient else 0.
            candidate = cost+length*(1+PARAMETERS['gradient_weight']*change)
            if candidate < costs[yy, xx]:
                costs[yy, xx] = candidate
                heapq.heappush(queue, (candidate, yy, xx))
    return costs


def assign_shared(rgb, labels, method):
    if method not in METHODS:
        raise ValueError('Unknown shared-highlight method')
    output, base = fill_highlights(rgb, labels)  # also validates input
    records = []
    if method != 'conservative':
        neighbors = np.ones((3, 3), bool)
        holes = ndi.binary_fill_holes(labels > 0, structure=neighbors) & (labels == 0)
        cavities, _ = ndi.label(holes, structure=neighbors)
        for r in base['cavities']:
            if not r['all_bright'] or len(r['adjacent_labels']) < 2:
                continue
            x0, y0, x1, y1 = r['bbox_xyxy']
            sl = (slice(max(0, y0-1), min(labels.shape[0], y1+1)),
                  slice(max(0, x0-1), min(labels.shape[1], x1+1)))
            mask = cavities[sl] == r['cavity']
            boundary = ndi.binary_dilation(mask, structure=neighbors) & ~mask
            owners = np.asarray(r['adjacent_labels'], dtype=labels.dtype)
            colors = rgb[sl].astype(float)/255.
            costs = np.stack([path_costs(colors, mask, boundary & (labels[sl] == owner),
                                        method == 'gradient')[mask] for owner in owners])
            best = costs.min(axis=0)
            tied = np.isclose(costs, best[None, :], atol=PARAMETERS['tie_atol'],
                              rtol=PARAMETERS['tie_rtol']).sum(axis=0) > 1
            selected = owners[costs.argmin(axis=0)]
            selected[tied] = 0
            output[sl][mask] = selected
            records.append(dict(cavity=r['cavity'], pixels=r['pixels'],
                adjacent_labels=r['adjacent_labels'], tie_pixels=int(tied.sum()),
                assigned_pixels=int(np.count_nonzero(selected)),
                assignments={int(o): int(np.count_nonzero(selected == o)) for o in owners}))
    return output, dict(method=method, parameters=PARAMETERS, conservative=base,
        shared_cavities=records, added_pixels=int(np.count_nonzero(output != labels)),
        shared_added_pixels=sum(r['assigned_pixels'] for r in records),
        tie_pixels=sum(r['tie_pixels'] for r in records),
        preserved_existing_labels=bool(np.array_equal(output[labels > 0], labels[labels > 0])))
