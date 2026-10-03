"""R214: six phase/origin trials with positive evidence and withheld sectors."""
import argparse
import copy
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR', '/tmp/beads-registration-mpl')
import numpy as np
from PIL import Image, ImageOps
from scipy.ndimage import distance_transform_edt
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from audit_saved_centers import coverage_stations
from tangent_circles import ROOT, load_model, visible_anchors, draw_circles, RADIUS
from check_placement import sha
from fit_positive_registration import search, evaluate, metrics, posed_config


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, allow_nan=False)+'\n')


def partition(centers, patches, patch_sectors):
    train_c = [r for r in centers if min(7, int(r['approximate_image_arc_fraction']*8)) % 2 == 0]
    train_p = [r for r, s in zip(patches, patch_sectors) if s % 2 == 0]
    train_s = [s for s in patch_sectors if s % 2 == 0]
    return train_c, train_p, train_s


def grouped_scores(matches, members, patch_sectors, diameter):
    result = {}
    for name, parity in [('training', 0), ('held_out', 1)]:
        mm = [r for r in matches if r['sector'] % 2 == parity]
        pp = [r for r, s in zip(members, patch_sectors) if s % 2 == parity]
        ss = [s for s in patch_sectors if s % 2 == parity]
        result[name] = metrics(mm, pp, ss, diameter)
    result['all'] = metrics(matches, members, patch_sectors, diameter)
    return result


def controlled_check(config, known):
    """Assisted inverse check using EXISTING independent POV-ID observations."""
    folder = ROOT/'photo2/output/r179'/known['fixture']
    ids_path = folder/(known['fixture']+'-ids.png')
    if sha(ids_path) != known['ids_sha256']:
        raise ValueError('Known fixture changed')
    encoded = np.asarray(Image.open(ids_path).convert('RGB'), int)
    labels = encoded[..., 0]+256*encoded[..., 1]-1
    factor = np.array([encoded.shape[1]/2540, encoded.shape[0]/3182])
    centers = []; patches = []; expected = []
    for k, check in enumerate(known['checks']):
        index = check['expected_generator_index']; expected.append(index)
        center = check['known_visible_centroid_xy']
        centers.append(dict(id=f'known-center-{index}', number=k+1, x=center[0], y=center[1],
                            approximate_image_arc_fraction=(k+.1)/8))
        mask = distance_transform_edt(labels == index) >= 1.5
        yy, xx = np.where(mask)
        native = np.unique(np.rint((np.column_stack((xx, yy))+.5)/factor-.5).astype(int), axis=0)
        assert len(native) > 0
        # Evaluator-only mask inset; rounding moves <=sqrt(.5) native pixels,
        # less than the ~3.8px inset. It is not a photo detector or color prior.
        patches.append(dict(observation_id=f'known-patch-{index}', observation_number=k+1,
            source_xy=native.mean(axis=0).tolist(), appearance_mode=None,
            region=dict(pixel_runs=[[int(y), int(x), int(x)] for x, y in native])))
    sectors = list(range(8))
    diameter = 2*RADIUS*load_model(config, config['parameters']).view.scale
    seed = posed_config(config, 40., 1/3)
    tc, tp, ts = partition(centers, patches, sectors)
    runs = tp[0]['region']['pixel_runs']
    group = dict(name='known-training-body', points_xy=[[r[1], r[0]] for r in [runs[0], runs[len(runs)//2], runs[-1]]])
    result = search(seed, tc, tp, ts, diameter, same_body_groups=[group])
    assert result['winner']['same_body_constraints_satisfied']
    baseline = evaluate(seed, centers, patches, sectors, diameter)
    final = evaluate(result['configuration'], centers, patches, sectors, diameter)
    before = grouped_scores(baseline['center_matches'], baseline['patch_memberships'], sectors, diameter)
    after = grouped_scores(final['center_matches'], final['patch_memberships'], sectors, diameter)
    assert after['training']['objective'] < before['training']['objective']
    assert after['held_out']['objective'] < before['held_out']['objective']
    recovered = [r['alternatives'][0]['generator_index'] for r in final['center_matches']]
    # Index numbers may change under an equivalent global relabeling; compare
    # physical prediction positions and exact expected-owner associations below.
    known_model = load_model(config, config['parameters'])
    expected_geometry = known_model.geometry(np.arange(known_model.source.nbeads))
    predicted_geometry = final['geometry']
    xyz = predicted_geometry['centers'][recovered]
    errors = np.linalg.norm(xyz-expected_geometry['centers'][expected], axis=1)*known_model.view.scale
    assert float(errors.max()) < 2., errors
    return dict(fixture=known['fixture'], ids_sha256=sha(ids_path),
        known_configuration=config, perturbed_start=seed, fitted_configuration=result['configuration'],
        assistance='Known POV visible centroids, inset ID-mask pixels and one training same-body group; no automatic appearance detection or hand/count recovery claim',
        baseline=before, registered=after, max_known_center_geometry_error_pixels=float(errors.max()),
        expected_indices=expected, tentative_fitted_indices=recovered, same_body_groups=[group], trials=result['trials'])


def crop_comparison(image, centers, cases, crop, out, name):
    x0, y0, x1, y1 = crop
    fig, axes = plt.subplots(2, 4, figsize=(16, 4 if name == 'top' else 7), constrained_layout=True)
    for ax in axes.ravel():
        ax.imshow(image, interpolation='nearest'); ax.set_xlim(x0, x1); ax.set_ylim(y1, y0); ax.axis('off')
    axes.ravel()[0].set_title('Raw photo')
    axes.ravel()[1].set_title('Your centers; orange=train, white=held out')
    for r in centers:
        if x0 < r['x'] < x1 and y0 < r['y'] < y1:
            color = 'orange' if min(7, int(r['approximate_image_arc_fraction']*8)) % 2 == 0 else 'white'
            axes.ravel()[1].scatter(r['x'], r['y'], marker='+', color=color, s=45)
            axes.ravel()[1].annotate(str(r['number']), (r['x'], r['y']), xytext=(4, 5),
                                   textcoords='offset points', color=color, fontsize=8)
    for ax, case in zip(axes.ravel()[2:], cases):
        ax.set_title(case['name']+'; registered')
        for r in case['center_matches']:
            x, y = r['observed_xy']
            if not x0 < x < x1 or not y0 < y < y1:
                continue
            color = 'orange' if r['sector'] % 2 == 0 else 'white'
            ax.scatter(x, y, marker='+', color=color, s=45)
            if r['alternatives']:
                q = r['alternatives'][0]['predicted_xy']
                ax.scatter(*q, s=24, facecolors='none', edgecolors='cyan')
                ax.plot([x, q[0]], [y, q[1]], color='cyan', lw=.6)
    fig.suptitle('Only minor phase and origin fitted; centerline/view/count fixed.\n'
                 'Cyan markers are model visible-region centroids; short connectors are residuals, not bead boundaries.', fontsize=11)
    fig.savefig(out/(name+'-comparison.png'), dpi=160); plt.close(fig)


def whole_overlay(image, patches, case, out):
    config = case['configuration']; model = load_model(config, config['parameters'])
    geometry = model.geometry(np.arange(model.source.nbeads)); vis = visible_anchors(model, geometry)
    fig, axes = plt.subplots(1, 2, figsize=(15, 10), constrained_layout=True)
    for ax in axes:
        ax.imshow(image); ax.axis('off')
    axes[0].set_title('Raw photo')
    axes[1].set_title(case['name']+' — registered minor-outward circles')
    draw_circles(axes[1], model, geometry, vis, .18*RADIUS)
    for r in patches:
        loop = np.asarray(r['region']['loop_xy'])
        axes[1].plot(loop[:, 0], loop[:, 1], color='lime', lw=.45)
    fig.suptitle('Cyan: exposed minor-outward tangent circles. Green: unchanged positive interior patches.\n'
                 'Fit tests bead ownership of patch pixels; it does not force cyan points into the tiny green patches.', fontsize=10)
    fig.savefig(out/(case['name']+'-whole.png'), dpi=165); plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'photo2/review/r214')
    parser.add_argument('--skip-known-checks', action='store_true', help='Repeat photo outputs without the separate controlled fixtures')
    args = parser.parse_args(); out = args.output; out.mkdir(parents=True, exist_ok=True)
    previous = json.loads((ROOT/'photo2/review/r210/summary.json').read_text())
    protected = {p: sha(ROOT/p) for p in previous['protected_inputs']}
    assert protected == previous['protected_inputs']
    centers = json.loads((ROOT/'photo2/review/r200/position-basis.json').read_text())['records']
    inventory = json.loads((ROOT/'photo2/review/r201/interiors.json').read_text())
    patches = [r for r in inventory['records'] if r['selected']]
    seed = json.loads((ROOT/'photo2/spline-seed-r175.json').read_text())
    fractions, *_ = coverage_stations(np.array([r['source_xy'] for r in patches]), seed['points'])
    sectors = np.minimum(7, (fractions*8).astype(int)).tolist()
    diameter = inventory['parameters']['inventory']['native_diameter']
    tc, tp, ts = partition(centers, patches, sectors)
    frozen = json.loads((ROOT/'photo2/review/r210/report.json').read_text())
    facts = json.loads((ROOT/'photo2/review/r211/confirmed-point-facts.json').read_text())
    confirmed_xy = np.array(list(facts['confirmed_same_bead_points'].values()))
    confirmed_fractions, *_ = coverage_stations(confirmed_xy, seed['points'])
    confirmed_sectors = np.minimum(7, (confirmed_fractions*8).astype(int)).tolist()
    assert len(set(confirmed_sectors)) == 1 and confirmed_sectors[0] % 2 == 0
    group = dict(name='R211 M V O same photo bead', points_xy=confirmed_xy.tolist(),
                 sector=confirmed_sectors[0], source='photo2/review/r211/confirmed-point-facts.json')
    cases = []; payloads = []
    for old in frozen['cases']:
        name = old['name']; config = old['configuration']
        def progress(trial):
            if trial['candidate'] % 9 == 0:
                print(json.dumps(dict(model=name, candidate=trial['candidate'], stage=trial['stage'],
                    objective=round(trial['metrics']['objective'], 6))), flush=True)
        fit = search(config, tc, tp, ts, diameter, progress, same_body_groups=[group])
        scan_file = name+'-scan.json'; save(out/scan_file, fit); payloads.append(scan_file)
        final = evaluate(fit['configuration'], centers, patches, sectors, diameter, [group])
        baseline = grouped_scores(old['center_matches'], old['interior_memberships'], sectors, diameter)
        scores = grouped_scores(final['center_matches'], final['patch_memberships'], sectors, diameter)
        case = dict(name=name, configuration=fit['configuration'], chosen_trial=fit['winner'],
            weight_sensitivity=fit['weight_sensitivity'], baseline=baseline, registered=scores,
            center_matches=final['center_matches'], patch_memberships=final['patch_memberships'],
            confirmed_M_V_O_model_owners=final['same_body_memberships'][0],
            feasible_trials=fit['feasible_trials'],
            source_loop_indices_role='Tentative within fitted model, not recovered photo bead_index',
            scan_file=scan_file)
        cases.append(case)
        routine = ROOT/'photo2/output/r214'/name
        save(routine/'regions.json', final['region_bank'])
        print(json.dumps(dict(model=name, phase_shift=fit['winner']['phase_delta_degrees'],
            origin_shift_beads=fit['winner']['origin_shift_beads'],
            training_objective=scores['training']['objective'],
            held_out_rms=scores['held_out']['balanced_center_rms_pixels'],
            held_out_support=scores['held_out']['balanced_patch_support'],
            same_M_V_O_owner=case['confirmed_M_V_O_model_owners']['coherent'])), flush=True)
    # Nothing in held-out scores changes the chosen training candidate or count.
    splits = dict(training_sectors=[0, 2, 4, 6], held_out_sectors=[1, 3, 5, 7],
        training_center_numbers=[r['number'] for r in tc],
        held_out_center_numbers=[r['number'] for r in centers if r not in tc],
        training_patch_numbers=[r['observation_number'] for r in tp],
        held_out_patch_numbers=[r['observation_number'] for r, s in zip(patches, sectors) if s % 2 == 1],
        patch_sector_records=[dict(observation_id=r['observation_id'], observation_number=r['observation_number'], sector=s,
                                  unchanged_source_xy=r['source_xy']) for r, s in zip(patches, sectors)],
        center_sector_counts=np.bincount([min(7, int(r['approximate_image_arc_fraction']*8)) for r in centers], minlength=8).tolist(),
        patch_sector_counts=np.bincount(sectors, minlength=8).tolist(),
        additional_training_same_body_groups=[group],
        caveat='Held out from this registration only; seed/count hypotheses and earlier reviews used these photo sections')
    save(out/'splits.json', splits); payloads.append('splits.json')
    report = dict(request='R214', cases=cases, fit_dimensions=['minor phase', 'origin'],
        centerline_changed=False, camera_changed=False, counts_optimized=False, local_stretch_applied=False,
        original_centers=41, original_positive_patches=208, fit_performed=True,
        objective='Mean occupied-sector center squared distance / apparent diameter² + mean occupied-sector positive-patch ownership deficit',
        patch_definition='Verified dominant-body fraction over ALL original patch pixels, zero when outward anchor not exposed; unknown pixels retained in denominator',
        candidate_selection='Training same-body constraint first, then training objective; 27 coarse and up to16 refinement candidates including historical baseline',
        confirmed_same_body_groups=[group],
        origin_gauge='One source-index interval [-0.5,0.5); full-turn minor phase; equivalent whole-model relabeling is tested',
        accepted_photo_bead_indices=0, live_model_replaced=False, no_boundary_classifier=True,
        limitations=['Finite sampled registration, not a certified global minimum.',
            'Both hands/counts and historical projection/centerline assumptions remain unresolved.',
            'Positive patches/visible centers have different meanings; no exact outward point is measured from a patch centroid.',
            'Held-out sectors are unused for current phase/origin ranking but not independent of historical hypothesis selection.',
            'R213 easier-evidence policy retained; difficult bodies unresolved, no complete outline prerequisite.'])
    save(out/'report.json', report); payloads.append('report.json')
    if not args.skip_known_checks:
        known = json.loads((ROOT/'photo2/review/r210/calibration.json').read_text())
        calibration = [controlled_check(k['config'], k) for k in known]
        save(out/'calibration.json', calibration); payloads.append('calibration.json')
    image = np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'))
    for name, crop in [('top', [1180, 220, 1730, 360]), ('right', [1990, 590, 2110, 710]),
                       ('bend', [1160, 1420, 1310, 1570])]:
        crop_comparison(image, centers, cases, crop, out, name); payloads.append(name+'-comparison.png')
    for case in cases:
        if case['configuration']['parameters']['nbeads'] == 2698:
            whole_overlay(image, patches, case, out); payloads.append(case['name']+'-whole.png')
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)
    for ax, metric, title in [(axes[0], 'balanced_center_rms_pixels', 'Held-out visible-center RMS (px)'),
                              (axes[1], 'balanced_patch_support', 'Held-out positive-patch support')]:
        before = [c['baseline']['held_out'][metric] for c in cases]
        after = [c['registered']['held_out'][metric] for c in cases]
        x = np.arange(len(cases)); ax.bar(x-.18, before, .36, label='Historical pose'); ax.bar(x+.18, after, .36, label='Registered')
        ax.set_xticks(x, [c['name'] for c in cases], rotation=45, ha='right'); ax.set_title(title); ax.legend()
    axes[1].set_ylim(0, 1); fig.savefig(out/'held-out-scores.png', dpi=170); plt.close(fig)
    payloads.append('held-out-scores.png')
    sources = ['beads-photo-2.jpg', 'beads.pov', 'photo2/spline-seed-r175.json',
        'photo2/fit_positive_registration.py', 'photo2/review_positive_registration.py',
        'photo2/test_positive_registration.py', 'photo2/visible_correspondence.py',
        'photo2/tangent_circles.py', 'photo2/audit_saved_centers.py', 'photo2/bead_placement.py',
        'photo2/curved_surface_fit.py', 'photo2/local_surface_fit.py',
        'photo2/review/r200/position-basis.json', 'photo2/review/r201/interiors.json',
        'photo2/review/r210/report.json', 'photo2/review/r210/calibration.json',
        'photo2/review/r211/confirmed-point-facts.json', 'photo2/positive-patch-scope-r212.json',
        'photo2/easy-evidence-priority-r213.json']
    assert {p: sha(ROOT/p) for p in protected} == protected
    save(out/'summary.json', dict(request='R214', source_sha256={p: sha(ROOT/p) for p in sources},
        protected_inputs=protected, curated_sha256={p: sha(out/p) for p in payloads},
        reproduction='.venv/bin/python photo2/review_positive_registration.py',
        no_live_model_or_saved_locations_changed=True))


if __name__ == '__main__':
    main()
