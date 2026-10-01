"""R190: raw/candidate comparison, withheld centers and known-render checks.

Ground-truth geometry and maker locations are read only after image-derived
curve fits. None is used to rank settings, change parameters or fit the photo.
"""
import argparse
import json
import os
from pathlib import Path

os.environ.setdefault('MPLCONFIGDIR', '/tmp/beads-r190-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageOps
from scipy.interpolate import splev
from scipy.spatial import cKDTree

import auto_label_beads as auto
from fit_bead_centerline import from_detection, nearest_distances
from label_beads import atomic_json


def known_render_checks():
    directory = auto.ROOT/'photo2/output/r167/calibration'
    pending = []
    for hand, palette, shift in [(1, 0, 0), (-1, 0, 0), (1, 1, 2)]:
        name = f'hand{hand:+d}-palette{palette}-shift{shift}'
        appearance = directory/(name+'.png')
        detection = auto.detect(np.array(Image.open(appearance).convert('RGB')))
        fitted = []
        for cutoff in [32., 48.]:
            try:
                fitted.append(dict(cutoff=cutoff, fit=from_detection(detection, cutoff=cutoff)))
            except ValueError as exc:
                fitted.append(dict(cutoff=cutoff, failure=str(exc)))
        pending.append((name, appearance, shift, fitted))
    # Source-model dimensions/camera truth enter the evaluator after every fit.
    from bead_placement import Rope, unit
    source = Rope(312)
    angle = np.linspace(0, 2*np.pi, 4097)
    origin = np.array([0., 0., 8.])
    forward = unit(origin-np.array([0., -40., 65.]))
    right = unit(np.cross([0., 1., 0.], forward))
    up = unit(np.cross(forward, right))
    rows = []
    for name, appearance, shift, fitted in pending:
        world = np.column_stack([source.chain_major*np.cos(angle)+shift,
                                 source.chain_major*np.sin(angle),
                                 np.full(len(angle), source.chain_minor+2*source.bead_radius)])
        delta = world-origin
        truth = np.column_stack([delta@right, -delta@up])*(800/72)+399.5
        checks = []
        for entry in fitted:
            if 'failure' in entry:
                checks.append(entry)
                continue
            fit = entry['fit']
            curve = np.array(fit['source_points'])
            errors = nearest_distances(curve, truth)
            inverse = nearest_distances(truth, curve)
            checks.append(dict(cutoff=entry['cutoff'], rms_curve_to_truth=float(np.sqrt(np.mean(errors**2))),
                               max_curve_to_truth=float(np.max(errors)),
                               rms_truth_to_curve=float(np.sqrt(np.mean(inverse**2))),
                               supported=sum(r['supported'] for r in fit['local_pairs']),
                               total=len(fit['local_pairs'])))
        rows.append(dict(fixture=name, appearance_sha256=auto.sha(appearance), checks=checks,
                         limitation='Known circle with different palette/placement/hand; not photo accuracy or a noncircular/perspective guarantee.'))
    return rows


def curve_metrics(curve, marks):
    distance = nearest_distances(curve, marks)
    return dict(rms=float(np.sqrt(np.mean(distance**2))), mean=float(distance.mean()),
                maximum=float(distance.max()), distances=distance.tolist())


def raw_crop(image, old, primary, variants, crop, path, marks=None):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.8), layout='constrained')
    for ax in axes:
        ax.imshow(image)
        ax.set_xlim(crop[0], crop[2]); ax.set_ylim(crop[3], crop[1]); ax.axis('off')
    axes[0].set_title('Raw photo')
    axes[1].plot(*old.T, color='cyan', lw=1.2)
    axes[1].set_title('Existing boundary-derived curve')
    for variant in variants:
        axes[2].plot(*np.array(variant['source_points']).T, color='deepskyblue', lw=.7, alpha=.65)
    axes[2].plot(*primary.T, color='lime', lw=1.2)
    if marks is not None:
        for ax in axes:
            for label, xy in zip('ABC', marks):
                ax.annotate(label, xy, xytext=xy+[10, -18], color='white', fontsize=10,
                            bbox=dict(facecolor='black', alpha=.75, pad=1),
                            arrowprops=dict(arrowstyle='->', color='white', lw=.7))
    axes[2].set_title('Green: candidate; blue: settings variation')
    fig.savefig(path, dpi=160); plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, default=auto.ROOT/'photo2/output/r190/checked')
    parser.add_argument('--output', type=Path, default=auto.ROOT/'photo2/review/r190')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    run = json.loads((args.run/'report.json').read_text())
    variants = [json.loads((args.run/v['file']).read_text()) for v in run['variants']]
    for row, fit in zip(run['variants'], variants):
        assert row['sha256'] == auto.sha(args.run/row['file'])
    primary = np.array(variants[0]['source_points'])
    image = ImageOps.exif_transpose(Image.open(auto.ROOT/'beads-photo-2.jpg')).convert('RGB')
    assert auto.sha(auto.ROOT/'beads-photo-2.jpg') == run['image_sha256']
    # Freeze all input-only known-render fits before importing prior photo geometry.
    checks = known_render_checks()
    from tangent_circles import SplineRope, View
    old_seed = json.loads((auto.ROOT/'photo2/spline-seed-r175.json').read_text())
    old_model = SplineRope(old_seed['points'], View(elevation=89.), smoothing=2.)
    old = np.array(splev(np.linspace(0, 1, 4097), old_model.tck)).T
    delta = np.roll(primary, -1, axis=0)-np.roll(primary, 1, axis=0)
    delta[0] = primary[1]-primary[-2]; delta[-1] = delta[0]
    normal = np.column_stack([-delta[:, 1], delta[:, 0]])/np.linalg.norm(delta, axis=1)[:, None]
    offsets = np.array([np.sum((np.array(v['source_points'])-primary)*normal, axis=1) for v in variants])
    spread = offsets.max(axis=0)-offsets.min(axis=0)
    automatic = json.loads((args.run/'automatic.json').read_text())
    assisted_shift = nearest_distances(primary, np.array(automatic['source_points']))
    # Saved centers are evaluator-only visible-area centers, not physical-axis truth.
    center_path = auto.ROOT/'photo2/output/tangent-viewer/centers.json'
    centers = json.loads(center_path.read_text())
    marks = np.array([[p['x'], p['y']] for p in centers['points']])
    mark_results = dict(count=len(marks), revision=centers['revision'], source_sha256=auto.sha(center_path),
                        old=curve_metrics(old, marks), candidate=curve_metrics(primary, marks),
                        variants=[dict(name=v['name'], **curve_metrics(fit['source_points'], marks))
                                  for v, fit in zip(run['variants'], variants)],
                        meaning='Distances to axis proxy, not bead-prediction SSE. Marks not used to select/fill/rank curves; they need not lie exactly on a physical axis.')
    old_dist = nearest_distances(old, primary)
    biggest = int(np.argmax(old_dist))
    center = primary[biggest]
    crop = [float(center[0]-190), float(center[1]-190), float(center[0]+190), float(center[1]+190)]
    raw_crop(image, old, primary, variants, crop, args.output/'bend-question.png')
    diagonal = json.loads((auto.ROOT/'photo2/diagonal-confirmed-r189.json').read_text())
    diag_xy = np.array([p['source_xy'] for p in diagonal['observations']])
    lo = diag_xy.min(axis=0)-95; hi = diag_xy.max(axis=0)+95
    raw_crop(image, old, primary, variants, [*lo, *hi], args.output/'confirmed-diagonal.png', marks=diag_xy)
    tree = cKDTree(primary[:-1]); _, loc = tree.query(diag_xy)
    tangent = delta[loc]/np.linalg.norm(delta[loc], axis=1)[:, None]
    displacement = np.diff(diag_xy, axis=0)
    diag_angles = np.degrees(np.arctan2(tangent[:-1, 0]*displacement[:, 1]-tangent[:-1, 1]*displacement[:, 0],
                                       np.sum(tangent[:-1]*displacement, axis=1)))
    # Settings with shorter windows disclose gaps that the main windows bridge.
    sparse = variants[1]['local_pairs']
    u = np.array(variants[0]['u'])
    station_tree = cKDTree(np.array([[np.cos(2*np.pi*r['u']), np.sin(2*np.pi*r['u'])] for r in sparse]))
    _, local = station_tree.query(np.column_stack([np.cos(2*np.pi*u), np.sin(2*np.pi*u)]))
    inferred = np.array([not sparse[i]['supported'] for i in local])
    fig, ax = plt.subplots(figsize=(10, 12), layout='constrained'); ax.imshow(image)
    for fit in variants[1:]:
        ax.plot(*np.array(fit['source_points']).T, color='deepskyblue', lw=.6, alpha=.55)
    ax.plot(*old.T, color='cyan', ls='--', lw=.65, label='Existing curve')
    ax.plot(*primary.T, color='lime', lw=.8, label='Candidate tube middle')
    bridge = primary.copy(); bridge[~inferred] = np.nan
    ax.plot(*bridge.T, color='orange', lw=1.3, ls='--', label='Weak short-window support')
    ax.plot([], [], color='deepskyblue', label='Settings alternatives; not confidence bounds')
    ax.legend(fontsize=9); ax.axis('off'); ax.set_title('Provisional centerline; no bead contours or new count inference')
    fig.savefig(args.output/'whole-context.png', dpi=150); plt.close(fig)
    fig, axes = plt.subplots(2, 1, figsize=(11, 6), layout='constrained')
    axes[0].plot(u, old_dist, color='teal', label='Distance from old curve')
    axes[0].plot(u, spread, color='royalblue', label='Normal spread across settings')
    axes[0].set_ylabel('Source pixels'); axes[0].legend()
    axes[0].set_xlabel('Fraction of learned search-route station')
    numbers = [p['number'] for p in centers['points']]
    axes[1].plot(numbers, mark_results['old']['distances'], 'o-', ms=3, label='Old curve')
    axes[1].plot(numbers, mark_results['candidate']['distances'], 'o-', ms=3, label='Candidate')
    axes[1].set_ylabel('Mark-to-curve pixels'); axes[1].set_xlabel('Saved visible-center observation number'); axes[1].legend()
    fig.savefig(args.output/'diagnostics.png', dpi=150); plt.close(fig)
    answer_path = auto.ROOT/'photo2/centerline-review-answer-r191.json'
    answer = json.loads(answer_path.read_text()) if answer_path.exists() else None
    if answer:
        assert answer['supporting_image_sha256'] == auto.sha(args.output/'bend-question.png')
    seed = json.loads((args.run/'candidate-spline.json').read_text())
    if answer:
        seed['maker_review'] = answer
        seed['status'] = 'Rejected candidate at reviewed bend; old curve retained, no viewer replacement'
    atomic_json(args.output/'candidate-spline.json', seed)
    atomic_json(args.output/'fit.json', variants[0])
    for row, fit in zip(run['variants'][1:], variants[1:]):
        atomic_json(args.output/(row['name']+'.json'), fit)
    # Capture exact inputs/outputs without overwriting the editable live center file.
    inputs = ['beads-photo-2.jpg', 'beads.pov', 'photo2/fit_bead_centerline.py',
              'photo2/review_bead_centerline.py', 'photo2/test_bead_centerline.py',
              'photo2/auto_label_beads.py', 'photo2/colored_centerline_evidence.py',
              'photo2/spline-seed-r175.json', 'photo2/diagonal-confirmed-r189.json',
              'photo2/colored-review-answers-r188.json', str(center_path.relative_to(auto.ROOT))]
    if answer:
        inputs.append(str(answer_path.relative_to(auto.ROOT)))
    preserved = json.loads((args.run.parent/'preserved-inputs.json').read_text())
    assert all(auto.sha(auto.ROOT/p) == digest for p, digest in preserved.items())
    atomic_json(args.output/'saved-centers.json', centers)
    atomic_json(args.output/'summary.json', dict(request='R190', fit_run=run,
        inventory=dict(admitted=len(variants[0]['admitted_observations']),
                       rejected=len(variants[0]['rejected_observations']),
                       excluded=variants[0]['excluded_observations']),
        settings_spread=dict(maximum=float(spread.max()), median=float(np.median(spread)),
                             meaning='Sensitivity to five settings; not a statistical confidence interval or total error bound'),
        old_difference=dict(maximum=float(old_dist.max()), rms=float(np.sqrt(np.mean(old_dist**2)))),
        exclusion_sensitivity=dict(maximum=float(assisted_shift.max()), rms=float(np.sqrt(np.mean(assisted_shift**2)))),
        known_renders=checks, saved_centers=mark_results,
        maker_review=answer,
        confirmed_diagonal=dict(observations=diagonal['observations'], candidate_image_angles=diag_angles.tolist(),
                                role='Consecutive body topology preserved; no signed6/7, exact tangent, phase or helicity inferred'),
        question=dict(id='Q190.1', crop=crop, largest_difference_xy=center.tolist(),
                      text='Which curve places the middle of the rope better here?'),
        supported_fraction=len([r for r in variants[0]['local_pairs'] if r['supported']])/len(variants[0]['local_pairs']),
        short_window_inferred_fraction=float(np.mean(inferred)),
        sources={p:auto.sha(auto.ROOT/p) for p in inputs}, preserved_inputs=preserved,
        curated_sha256={p.name:auto.sha(p) for p in sorted(args.output.glob('*')) if p.name != 'summary.json'},
        status='Candidate rejected at reviewed bend; viewer/score/model seed unchanged; full lattice/camera refinement still needed.'))
    print(json.dumps(dict(old_difference=dict(maximum=float(old_dist.max())), settings_spread=float(spread.max()),
                          old_mark_rms=mark_results['old']['rms'], candidate_mark_rms=mark_results['candidate']['rms'],
                          exclusion_shift=float(assisted_shift.max()), known_renders=checks), indent=2), flush=True)


if __name__ == '__main__':
    main()
