"""Observed-region seed gates. Inputs contain no observed truth or truth indices."""
from __future__ import annotations

import numpy as np
from scipy import ndimage as ndi

from local_patch import PARAMETERS

REGION_PARAMETERS = dict(min_iou=.5, min_families=2, min_anchors=3, max_anchors=4)


def clicked_labels(labels, anchors):
    result = []
    for x, y in anchors:
        x, y = int(round(x)), int(round(y))
        result.append(int(labels[y, x]) if 0 <= y < labels.shape[0]
                      and 0 <= x < labels.shape[1] else 0)
    return result


def topology(labels, min_families):
    edges = [[i, j, b-a] for i, a in enumerate(labels) for j, b in enumerate(labels)
             if i < j and a and b and abs(b-a) in (1, 6, 7)]
    families = sorted({abs(e[2]) for e in edges})
    reached = {0}
    for _ in labels:
        for i, j, _ in edges:
            if i in reached or j in reached:
                reached.update((i, j))
    valid = bool(all(labels) and len(set(labels)) == len(labels)
                 and len(reached) == len(labels) and len(families) >= min_families)
    return dict(anchor_labels=labels, anchor_edges=edges, anchor_families=families,
                topology_ok=valid)


def correspondence(observed, predicted, objects):
    """Independent region-to-model IoU; >.5 prevents ambiguous equal-size splits.

    Only observed region identity comes from clicking. Candidate indices and
    shape masks come from the calibrated forward model, not observed ID images.
    """
    support = {o['model_label']: o['supported'] for o in objects}
    model_sizes = dict(zip(*np.unique(predicted, return_counts=True)))
    records = {}
    b = PARAMETERS['border']
    for label in np.unique(observed):
        if not label:
            continue
        mask = observed == label
        yy, xx = np.nonzero(mask)
        values, counts = np.unique(predicted[mask], return_counts=True)
        scores = [(float(n/(len(xx)+model_sizes[v]-n)), int(v))
                  for v, n in zip(values, counts) if v]
        iou, model = max(scores, default=(0., 0))
        touches = bool(xx.min() < b or yy.min() < b or xx.max() >= mask.shape[1]-b
                       or yy.max() >= mask.shape[0]-b)
        records[int(label)] = dict(observed_label=int(label), pixels=len(xx),
            touches_crop=touches, model_label=model, iou=iou,
            supported=bool(support.get(model, False)),
            valid=bool(len(xx) >= PARAMETERS['min_pixels'] and not touches
                       and iou > REGION_PARAMETERS['min_iou'] and support.get(model, False)))
    return records


def region_gate(observed, anchors, records):
    if not REGION_PARAMETERS['min_anchors'] <= len(anchors) <= REGION_PARAMETERS['max_anchors']:
        raise ValueError('Expected three or four anchors')
    selected = clicked_labels(observed, anchors)
    matches = [records.get(label, dict(observed_label=label, model_label=0,
                                      iou=0., valid=False)) for label in selected]
    result = topology([r['model_label'] for r in matches], REGION_PARAMETERS['min_families'])
    result.update(observed_labels=selected, matches=matches,
                  anchor_ok=bool(all(r['valid'] for r in matches)
                                 and len(set(selected)) == len(selected) and result['topology_ok']))
    return result


def interior_distances(labels):
    result = np.zeros(labels.shape, float)
    for label in np.unique(labels):
        if label:
            mask = labels == label
            result[mask] = ndi.distance_transform_edt(mask)[mask]
    return result


def legacy_gate(labels, anchors, interiors):
    result = topology(clicked_labels(labels, anchors), 3)
    margins = []
    for label, (x, y) in zip(result['anchor_labels'], anchors):
        margins.append(float(interiors[round(y), round(x)]) if label else 0.)
    result.update(anchor_margins=margins,
                  anchor_ok=bool(result['topology_ok'] and min(margins) >= PARAMETERS['anchor_margin']))
    return result


def apply_gate(objects, gate):
    seed = gate['anchor_labels'][0]
    return dict(gate, objects=[dict(o,
        candidate_relative_index=o['model_label']-seed if seed else None,
        relative_index=o['model_label']-seed if seed and gate['anchor_ok'] and o['supported'] else None)
        for o in objects])
