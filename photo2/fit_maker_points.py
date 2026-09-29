"""Assisted R149 diagnostic: positive visible-point ownership, not bead centers.

G's location is evaluator-only. No image colors, body outlines or background
labels enter fitting. The straight-tube model and camera gauge are local limits.
"""
import argparse
import json
import os
from pathlib import Path
import time

os.environ.setdefault('MPLCONFIGDIR', '/tmp/beads-matplotlib')
import numpy as np
from PIL import Image, ImageOps
from scipy.optimize import least_squares, minimize
from scipy.ndimage import distance_transform_edt, map_coordinates
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from local_surface_fit import ROOT, RADIUS, PITCH, centers, outward, trace, INDICES
from check_local_surface_fit import render
from check_placement import sha

PATCH = (16, 17, 19, 20, 21, 22, 23)
TRAIN = PATCH[:-1]
FREE = np.array([0, 1, 2, 3, 5, 6])


def mappings(report):
    chart = report['conditional_charts'][0]
    result = {}
    for name, weights in [('A', (1, 7, 6)), ('B', (-1, 6, 7))]:
        candidate = next(c for c in chart['relative_index_candidates']
                         if tuple(c['weights'][d] for d in ('d1', 'd2', 'd3')) == weights)
        origin = candidate['offsets']['20']
        result[name] = {n: candidate['offsets'][str(n)] - origin for n in PATCH}
    return result


def training_setup(points):
    """Only the six training points determine bounds, crop and initialization."""
    target = np.array([points[n] for n in TRAIN], float)
    span = np.ptp(target, axis=0)
    size = max(float(span.max()), 20.)
    crop = [*np.floor(target.min(axis=0)-size*.65).astype(int),
            *np.ceil(target.max(axis=0)+size*.65).astype(int)]
    midpoint = target.mean(axis=0)
    scale = max(np.linalg.norm(target[TRAIN.index(22)]-target[TRAIN.index(16)])/(13*PITCH), 1.)
    axis = target[TRAIN.index(22)]-target[TRAIN.index(16)]
    roll = np.degrees(np.arctan2(axis[1], axis[0]))
    lo = np.array([*(midpoint-size), scale*.35, roll-80, 55, -65, -540])
    hi = np.array([*(midpoint+size), scale*2.1, roll+80, 55, 65, 540])
    return target, crop, midpoint, scale, roll, lo, hi


def proposal_seeds(points, mapping, hand):
    target, crop, midpoint, scale, roll, lo, hi = training_setup(points)
    indices = np.array([mapping[n] for n in TRAIN])
    proposals = []
    for phase in (-150, -60, 30, 120):
        for az in (-35, 0, 35):
            start = np.array([*midpoint, scale, roll, 55, az, phase])
            def unpack(v):
                p = start.copy(); p[FREE] = v
                return p
            # Proposal convenience only; maker points are NOT outward anchors.
            fit = least_squares(lambda v: (outward(unpack(v), indices, hand)-target).ravel(),
                                start[FREE], bounds=(lo[FREE], hi[FREE]), max_nfev=180)
            proposals.append((float(np.mean(fit.fun**2)), unpack(fit.x)))
    return sorted(proposals, key=lambda x: x[0]), crop, lo, hi


def grid(crop, spacing):
    x0, y0, x1, y1 = crop
    yy, xx = np.mgrid[y0:y1:spacing, x0:x1:spacing]
    return np.column_stack((xx.ravel(), yy.ravel())), xx.shape


def distance_loss(p, hand, mapping, points, crop, spacing):
    point_labels, _, point_unfinished = trace(p, np.array([points[n] for n in TRAIN]), hand)
    correct = point_labels == np.array([mapping[n] for n in TRAIN])
    if correct.all():
        return 0., [0.]*len(TRAIN), point_unfinished
    xy, shape = grid(crop, spacing)
    labels, _, unfinished = trace(p, xy, hand)
    labels = labels.reshape(shape)
    total = []
    for n, already_correct in zip(TRAIN, correct):
        mask = labels == mapping[n]
        if already_correct:
            total.append(0.)
        elif not mask.any():
            total.append(float(np.hypot(crop[2]-crop[0], crop[3]-crop[1])))
        else:
            distances = distance_transform_edt(~mask)*spacing
            x, y = points[n]
            total.append(float(map_coordinates(distances, [[(y-crop[1])/spacing],
                                [(x-crop[0])/spacing]], order=1, mode='nearest')[0]))
    return float(np.mean(np.square(total))), total, unfinished+point_unfinished


def ownership(p, hand, mapping, points):
    labels, _, unfinished = trace(p, np.array([points[n] for n in PATCH]), hand)
    return {str(n): dict(expected=mapping[n], actual=int(label), correct=bool(label==mapping[n]),
                        held_out=n==23) for n, label in zip(PATCH, labels)}, unfinished


def fit_case(points, name, mapping, hand, maxfev=250):
    start_time = time.monotonic()
    proposals, crop, lo, hi = proposal_seeds(points, mapping, hand)
    # Rank by actual training visibility, never by G, after loose proposals.
    ranked = sorted(((distance_loss(p, hand, mapping, points, crop, 3)[0], mse, p)
                    for mse, p in proposals), key=lambda item: item[:2])
    candidates = []
    for seed_loss, mse, start in ranked[:2]:
        p = start.copy()
        stages = []
        for spacing in (3, 1):
            if distance_loss(p, hand, mapping, points, crop, spacing)[0] == 0:
                stages.append(dict(spacing=spacing, evaluations=0, success=True,
                                   message='All six exact training rays have expected ownership; feasible stop'))
                continue
            def unpack(v):
                value = p.copy(); value[FREE] = v
                return value
            fit = minimize(lambda v: distance_loss(unpack(v), hand, mapping, points, crop, spacing)[0],
                           p[FREE], method='Powell', bounds=list(zip(lo[FREE], hi[FREE])),
                           options=dict(maxfev=maxfev, maxiter=12, xtol=.02, ftol=.001))
            trial = unpack(fit.x)
            # Powell can leave a better start on a discontinuous raster objective.
            if distance_loss(trial, hand, mapping, points, crop, spacing)[0] < distance_loss(p, hand, mapping, points, crop, spacing)[0]:
                p = trial
            stages.append(dict(spacing=spacing, evaluations=int(fit.nfev),
                               success=bool(fit.success), message=str(fit.message)))
        loss, distances, unfinished = distance_loss(p, hand, mapping, points, crop, 1)
        own, point_unfinished = ownership(p, hand, mapping, points)
        correct = sum(own[str(n)]['correct'] for n in TRAIN)
        candidates.append(dict(parameters=p.tolist(), training_loss_px2=loss,
                               training_distances_px=distances, training_correct=correct,
                               ownership=own, unfinished_grid_ray_pairs=unfinished,
                               unfinished_point_ray_pairs=point_unfinished,
                               proposal_outward_mse_px2=mse, stages=stages))
    # Holdout fields are deliberately absent from this selection key.
    best = min(candidates, key=lambda c: (-c['training_correct'], c['training_loss_px2']))
    result = dict(family=name, hand=hand, mapping=mapping, crop=[int(v) for v in crop],
                  selected=best, seed_results=candidates, seconds=time.monotonic()-start_time)
    print(json.dumps(dict(family=name, hand=hand, training_correct=best['training_correct'],
                         held_out_correct=best['ownership']['23']['correct'],
                         loss=best['training_loss_px2'], seconds=result['seconds'])), flush=True)
    return result


def parity(case, out, stem):
    p = case['selected']['parameters']; crop = case['crop']; hand = case['hand']
    actual, provenance = render(p, hand, crop, out, stem)
    xy, shape = grid(crop, 1)
    predicted, _, unfinished = trace(p, xy, hand)
    mismatches = int(np.sum(actual != predicted.reshape(shape)))
    result = dict(mismatches=mismatches, pixels=actual.size, fraction=mismatches/actual.size,
                  unfinished_ray_pairs=unfinished, **provenance)
    if result['fraction'] >= .001:
        raise AssertionError(result)
    return result


def synthetic_points(mapping, out):
    p = [200, 180, 9, -6, 55, 18, 35]
    crop = [100, 90, 300, 270]
    actual, provenance = render(p, 1, crop, out, 'synthetic-truth')
    points = {}
    for n, index in mapping.items():
        inside = distance_transform_edt(actual == index)
        if inside.max() < 2:
            raise AssertionError(f'Synthetic bead {n} has no substantial visible body')
        y, x = np.unravel_index(inside.argmax(), inside.shape)
        points[n] = [int(x+crop[0]), int(y+crop[1])]
    return points, dict(parameters=p, hand=1, mapping=mapping, crop=crop,
                        point_rule='Maximum visible-mask interior distance; exact supplied calibration points',
                        **provenance)


def review(points, cases, crop, output):
    raw = ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB')
    fig, axes = plt.subplots(1, 3, figsize=(13, 5.5), constrained_layout=True)
    x0, y0, x1, y1 = crop
    chosen = [min((c for c in cases if c['family']==name),
                  key=lambda c: (-c['selected']['training_correct'], c['selected']['training_loss_px2']))
              for name in ('A', 'B')]
    colors = plt.get_cmap('tab10')(np.arange(len(PATCH)))
    for ax in axes:
        ax.imshow(raw, origin='upper'); ax.set_xlim(x0, x1); ax.set_ylim(y1, y0)
        for n, color in zip(PATCH, colors):
            x, y = points[n]
            ax.scatter(x, y, c=[color], s=27, marker='x' if n==23 else 'o', edgecolors=None)
            ax.text(x+2, y-3, str(n)+(' G' if n==23 else ''), color='white', fontsize=9,
                    bbox=dict(facecolor='black', alpha=.65, pad=1))
        ax.set_xlabel('Source x (pixels)'); ax.set_ylabel('Source y (pixels)')
    axes[0].set_title('Raw photo + maker surface points\nG=23 held out; points are not centers')
    xy, shape = grid(crop, 1)
    for ax, case in zip(axes[1:], chosen):
        labels, _, _ = trace(case['selected']['parameters'], xy, case['hand'])
        labels = labels.reshape(shape)
        for n, color in zip(PATCH, colors):
            mask = labels == case['mapping'][n]
            if mask.any():
                ax.contour(np.arange(x0,x1), np.arange(y0,y1), mask, levels=[.5],
                           colors=[color], linewidths=1.2, linestyles='--')
        best = case['selected']
        ax.set_title(f"Family {case['family']}, helicity {case['hand']:+d}\n"
                     f"Training {best['training_correct']}/6; G {'passes' if best['ownership']['23']['correct'] else 'misses'}")
    fig.savefig(output, dpi=160); plt.close(fig)
    # Wider raw context, preserving all maker points but highlighting this patch.
    fig, ax = plt.subplots(figsize=(6, 6.5), constrained_layout=True)
    ax.imshow(raw); ax.set_xlim(1180,1540); ax.set_ylim(520,130)
    for n in PATCH:
        x,y=points[n]; ax.scatter(x,y,c='white',s=12); ax.text(x+3,y-3,str(n),color='white',
                                 bbox=dict(facecolor='black',alpha=.65,pad=1))
    ax.set_title('Unaltered wider context — C=20, B=22, G=23')
    fig.savefig(output.with_name('wider-context.png'), dpi=160); plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'photo2/output/r149')
    parser.add_argument('--review', type=Path, default=ROOT/'photo2/review/r149')
    parser.add_argument('--maxfev', type=int, default=250)
    args = parser.parse_args(); args.output.mkdir(parents=True, exist_ok=True); args.review.mkdir(parents=True, exist_ok=True)
    annotations = ROOT/'photo2/manual-labels-r146.json'
    graph = ROOT/'photo2/review/r144/corrected-report.json'
    labels = json.loads(annotations.read_text())
    points = {a['number']: [a['x'],a['y']] for a in labels['annotations'] if a['number'] in PATCH}
    families = mappings(json.loads(graph.read_text()))
    synthetic, truth = synthetic_points(families['A'], args.output)
    results = {}
    for dataset, locations in [('synthetic', synthetic), ('photo', points)]:
        cases = []
        for name, mapping in families.items():
            for hand in (-1, 1):
                case = fit_case(locations, name, mapping, hand, args.maxfev)
                case['independent_pov_check'] = parity(case, args.output, f'{dataset}-{name}-{hand}')
                cases.append(case)
                (args.output/f'{dataset}-partial.json').write_text(json.dumps(cases, indent=2)+'\n')
        results[dataset] = cases
    report = dict(scope='Assisted positive surface-point ownership; no automatic detection or recovered full indices',
                  training_numbers=TRAIN, held_out_number=23, origin_number=20,
                  projection='Orthographic local straight planar-centerline limit',
                  camera_elevation_gauge_deg=55, gauge_is_measurement=False,
                  radius=RADIUS, pitch=PITCH, latent_indices=INDICES.tolist(),
                  synthetic_points=synthetic, evaluator_truth=truth, photo_points=points,
                  maxfev_per_stage=args.maxfev, results=results,
                  provenance={str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'beads-photo-2.jpg', ROOT/'beads.pov', annotations, graph, Path(__file__), ROOT/'photo2/local_surface_fit.py',ROOT/'photo2/check_local_surface_fit.py']})
    (args.review/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    _, crop, *_ = training_setup(points)
    review(points, results['photo'], [int(x) for x in crop], args.review/'comparison.png')
    print('Saved '+str(args.review/'report.json'),flush=True)


if __name__ == '__main__':
    main()
