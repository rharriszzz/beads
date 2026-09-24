"""Evaluator-only truth matching; never imported by the image detector."""
from __future__ import annotations

import numpy as np


def score_instances(predicted, truth, objects, true_colors, thresholds=(12, 100)):
    """One-to-one IoU > .5 matching (strict > makes uniqueness guaranteed).

    Keep all truth IDs in the overlap table: small slivers cannot disappear from
    false-positive accounting by deleting their pixels before evaluation.
    """
    if predicted.shape != truth.shape or predicted.min() < 0 or truth.min() < 0:
        raise ValueError('Expected matching nonnegative label arrays')
    n, m = int(predicted.max()), len(true_colors)
    if truth.max() > m or len(objects) != n:
        raise ValueError('Metadata does not cover labels')
    table = np.bincount((predicted.ravel().astype(np.int64)*(m+1)+truth.ravel()),
                        minlength=(n+1)*(m+1)).reshape(n+1, m+1)
    pa, ta = table.sum(axis=1), table.sum(axis=0)
    intersection = table[1:, 1:]
    union = pa[1:, None]+ta[None, 1:]-intersection
    iou = np.divide(intersection, union, out=np.zeros_like(intersection, float), where=union>0)
    pi, ti = np.nonzero(iou > .5)
    if len(set(pi)) != len(pi) or len(set(ti)) != len(ti):
        raise AssertionError('IoU > .5 matching must be one to one')
    matches = [dict(detection_id=int(p+1), source_bead_index=int(t), iou=float(iou[p, t]),
                    predicted_color=objects[p]['color'], true_color=true_colors[t]) for p, t in zip(pi, ti)]
    # A split/merge requires >=10% of a truth bead in each contributing fragment.
    substantial = ((intersection >= .10*ta[None, 1:]) & (intersection >= 12))
    report = dict(matches=matches, zero_pixel_indices=np.flatnonzero(ta[1:]==0).tolist(),
                  pixels_per_truth_bead=ta[1:].tolist(), predicted_instances=n,
                  thresholds={}, merged_predictions=int(np.count_nonzero(substantial.sum(axis=1)>1)),
                  split_truth_beads=int(np.count_nonzero(substantial.sum(axis=0)>1)))
    foreground_tp = int(table[1:, 1:].sum())
    foreground_fp = int(table[1:, 0].sum())
    foreground_fn = int(table[0, 1:].sum())
    denominator = foreground_tp+foreground_fp+foreground_fn
    report['foreground_union'] = dict(tp_pixels=foreground_tp, fp_pixels=foreground_fp,
            fn_pixels=foreground_fn, iou=foreground_tp/denominator if denominator else None,
            meaning='Union of predicted instances, not independent bracelet-mask validation')
    for threshold in thresholds:
        eligible = ta[1:] >= threshold
        selected = [x for x in matches if eligible[x['source_bead_index']]]
        # Predictions matched only to a real, subthreshold sliver are ignored for
        # precision at this threshold, and counted explicitly instead of hidden.
        ignored = sum(not eligible[x['source_bead_index']] for x in matches)
        tp = len(selected)
        fn = int(eligible.sum())-tp
        fp = n-ignored-tp
        seen = {x['source_bead_index'] for x in selected}
        classes = {}
        for name in sorted(set(true_colors)):
            support = sum(eligible[t] and c == name for t, c in enumerate(true_colors))
            found = [x for x in selected if x['true_color'] == name]
            classes[name] = dict(visible=int(support), detected=len(found),
                                 color_correct=sum(x['predicted_color']==name for x in found))
        report['thresholds'][str(threshold)] = dict(tp=tp, fp=fp, fn=fn, ignored=ignored,
                precision=tp/(tp+fp) if tp+fp else None,
                recall=tp/(tp+fn) if tp+fn else None,
                color_correct=sum(x['predicted_color']==x['true_color'] for x in selected),
                color_unknown=sum(x['predicted_color']=='unknown' for x in selected),
                mean_iou=float(np.mean([x['iou'] for x in selected])) if selected else None,
                missed_indices=[int(t) for t in np.flatnonzero(eligible) if t not in seen],
                by_color=classes)
    return report
