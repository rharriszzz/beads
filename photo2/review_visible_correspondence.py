"""R210: frozen-model correspondence pilot; no registration or curve update."""
import argparse
import copy
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR', '/tmp/beads-correspondence-mpl')
import numpy as np
from PIL import Image, ImageOps
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from tangent_circles import ROOT, load_model, visible_anchors
from check_placement import sha
from visible_correspondence import (region_bank, nearest_centers, center_score,
    interior_membership, mode_conflicts, rays)


def save(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False)+'\n')


def known_check(config, name):
    """Existing independent POV ID fixture, never a photo-input body map."""
    folder = ROOT/'photo2/output/r179'/name
    path = folder/(name+'-ids.png')
    actual_config = json.loads((folder/'parameters.json').read_text())
    assert actual_config == config
    model = load_model(config, config['parameters'])
    geometry = model.geometry(np.arange(model.source.nbeads))
    vis = visible_anchors(model, geometry)
    pixels = np.array(Image.open(path).convert('RGB'), int)
    labels = pixels[..., 0]+256*pixels[..., 1]-1
    factor = np.array([pixels.shape[1]/2540, pixels.shape[0]/3182])
    available = [int(i) for i in np.flatnonzero(vis['exposed']) if np.sum(labels == i) >= 30]
    chosen = np.array(available)[np.linspace(0, len(available)-1, 8).astype(int)]
    observed = []; records = []
    for k, index in enumerate(chosen):
        yy, xx = np.where(labels == index)
        native = (np.column_stack((xx, yy))+.5)/factor-.5
        centroid = native.mean(axis=0); observed.append(centroid)
        records.append(dict(id=f'known-{index}', number=k+1, x=float(centroid[0]),
            y=float(centroid[1]), approximate_image_arc_fraction=k/8))
    bank, _ = region_bank(model, observed, step=2)
    bank_by_index = {r['generator_index']: r for r in bank['records']}
    matches = nearest_centers(records, bank)
    # Actual source-pixel rays across complete conservative candidate bounds.
    bound = bank['conservative_radius_pixels']
    projected = model.view.project(geometry['centers'][chosen])
    test_pixels = []
    for xy in projected:
        lo = np.maximum(0, np.floor((xy-bound+.5)*factor-.5).astype(int))
        hi = np.minimum([pixels.shape[1]-1, pixels.shape[0]-1],
                        np.ceil((xy+bound+.5)*factor-.5).astype(int))
        xx, yy = np.meshgrid(np.arange(lo[0], hi[0]+1), np.arange(lo[1], hi[1]+1))
        test_pixels.append(np.column_stack((xx.ravel(), yy.ravel())))
    pp = np.unique(np.concatenate(test_pixels), axis=0)
    owner, _, unfinished = rays(model, (pp+.5)/factor-.5, geometry)
    truth = labels[pp[:, 1], pp[:, 0]]
    verified = unfinished == 0
    disagreement = verified & (owner != truth)
    checks = []
    for i, index in enumerate(chosen):
        prediction = matches[i]['alternatives'][0]
        estimate = bank_by_index[int(index)]
        checks.append(dict(expected_generator_index=int(index),
            proposed_generator_index=prediction['generator_index'],
            known_visible_centroid_xy=observed[i].tolist(),
            estimated_centroid_xy=estimate['visible_centroid_xy'],
            centroid_grid_difference_pixels=float(np.linalg.norm(np.array(estimate['visible_centroid_xy'])-observed[i])),
            physical_center_difference_pixels=float(np.linalg.norm(np.array(estimate['projected_physical_center_xy'])-observed[i])),
            outward_difference_pixels=float(np.linalg.norm(np.array(estimate['outward_xy'])-observed[i])),
            unknown_shift_bound_pixels=estimate['finite_grid_centroid_unknown_shift_bound_pixels']))
    assert not disagreement.any(), (name, pp[disagreement].tolist())
    assert all(r['expected_generator_index'] == r['proposed_generator_index'] for r in checks), checks
    return dict(fixture=name, config=config, ids_sha256=sha(path),
        parameters_sha256=sha(folder/'parameters.json'), report_sha256=sha(folder/'report.json'),
        evaluated_rays=len(pp), verified_rays=int(verified.sum()),
        unverified_rays=int((~verified).sum()), verified_disagreements=int(disagreement.sum()),
        checks=checks, role='Forward geometry/association check; known ID centroids are evaluator inputs, not image detection')


def plot_context(image, centers, cases, crop, out, name):
    x0, y0, x1, y1 = crop
    selected = [r for r in centers if x0 < r['x'] < x1 and y0 < r['y'] < y1]
    fig, axes = plt.subplots(2, 4, figsize=(16, 4 if name == 'top-context' else 7), constrained_layout=True)
    for ax in axes.ravel():
        ax.imshow(image, interpolation='nearest')
        ax.set_xlim(x0, x1); ax.set_ylim(y1, y0); ax.axis('off')
    axes.ravel()[0].set_title('Raw photo')
    axes.ravel()[1].set_title('Saved maker centers (orange +)')
    for r in selected:
        ax = axes.ravel()[1]
        ax.scatter(r['x'], r['y'], marker='+', color='orange', s=55)
        ax.annotate(str(r['number']), (r['x'], r['y']), xytext=(4, 5),
                    textcoords='offset points', color='white', fontsize=8)
    for ax, case in zip(axes.ravel()[2:], cases):
        ax.set_title(case['name']+'; frozen pose')
        for row in case['center_matches']:
            x, y = row['observed_xy']
            if not x0 < x < x1 or not y0 < y < y1:
                continue
            ax.scatter(x, y, marker='+', color='orange', s=55)
            if row['alternatives']:
                q = np.array(row['alternatives'][0]['predicted_xy'])
                ax.plot([x, q[0]], [y, q[1]], color='cyan', lw=.7, alpha=.8)
                ax.scatter(*q, facecolors='none', edgecolors='cyan', s=28)
    fig.suptitle('Orange: your visible-part center; cyan: predicted visible-region centroid.\n'
                 'Short connectors show residuals, not bead boundaries. No correspondence accepted.', fontsize=11)
    fig.savefig(out/(name+'.png'), dpi=160); plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'photo2/review/r210')
    args = parser.parse_args(); out = args.output; out.mkdir(parents=True, exist_ok=True)
    old = json.loads((ROOT/'photo2/review/r208/summary.json').read_text())
    protected = {p: sha(ROOT/p) for p in old['protected_inputs']}
    assert protected == old['protected_inputs'], 'A protected live input changed; inspect before proceeding'
    center_path = ROOT/'photo2/review/r200/position-basis.json'
    interior_path = ROOT/'photo2/review/r201/interiors.json'
    centers = json.loads(center_path.read_text())['records']
    inventory = json.loads(interior_path.read_text())
    interiors = [r for r in inventory['records'] if r['selected']]
    assert len(centers) == 41 and len(interiors) == 208
    assert inventory['image_sha256'] == sha(ROOT/'beads-photo-2.jpg')
    configurations = {hand: json.loads((ROOT/f"photo2/review/r179/{'plus' if hand == 1 else 'minus'}-2698/parameters.json").read_text())
                      for hand in [-1, 1]}
    cases = []
    for count in [2698, 2833, 3592]:
        for hand in [-1, 1]:
            config = copy.deepcopy(configurations[hand]); config['parameters']['nbeads'] = count
            name = f"{'plus' if hand == 1 else 'minus'}-{count}"
            model = load_model(config, config['parameters'])
            bank, geometry = region_bank(model, [[r['x'], r['y']] for r in centers])
            matches = nearest_centers(centers, bank)
            members = interior_membership(model, interiors, geometry)
            conflicts = mode_conflicts(members)
            proposals = dict(visible_centroid=center_score(matches),
                physical_center=center_score(nearest_centers(centers, bank, 'projected_physical_center_xy')),
                outward_point=center_score(nearest_centers(centers, bank, 'outward_xy')))
            case = dict(name=name, configuration=config, scale_pixels_per_unit=model.view.scale,
                scores=proposals, center_matches=matches, interior_memberships=members,
                membership_summary=dict(total=len(members),
                    coherent_central=sum(r['coherent_central_membership'] for r in members),
                    coherent_unexposed=sum(r['dominant_fraction'] >= .95 and not r['outward_exposed'] for r in members),
                    split_or_background=sum(r['dominant_fraction'] < .95 for r in members),
                    uncertain_patches=sum(r['unresolved_pixels'] > 0 for r in members)),
                appearance_conflict_witnesses=conflicts,
                region_bank_metadata={k: v for k, v in bank.items() if k != 'records'},
                region_bank_file=name+'-regions.json')
            save(out/case['region_bank_file'], bank)
            cases.append(case)
            print(json.dumps(dict(name=name, scores=proposals['visible_centroid'],
                memberships=case['membership_summary'], mode_conflicts=len(conflicts))), flush=True)
    # Model/evaluator truth comes after all real-photo measurements.
    calibration = [known_check(configurations[h], f"{'plus' if h == 1 else 'minus'}-2698") for h in [-1, 1]]
    save(out/'calibration.json', calibration)
    # Numerical resolution check on the SAME frozen pose and observations; no
    # selection by better-looking raster or changed ownership.
    config = copy.deepcopy(configurations[-1]); config['parameters']['nbeads'] = 3592
    model = load_model(config, config['parameters'])
    bank1, _ = region_bank(model, [[r['x'], r['y']] for r in centers], step=1)
    fine = nearest_centers(centers, bank1)
    coarse = next(c for c in cases if c['name'] == 'minus-3592')
    convergence = []
    fine_bank = {r['generator_index']: r for r in bank1['records']}
    coarse_bank = json.loads((out/coarse['region_bank_file']).read_text())
    for row in coarse['center_matches']:
        if not row['alternatives']:
            continue
        p = row['alternatives'][0]; f = fine_bank[p['generator_index']]
        convergence.append(dict(number=row['number'], generator_index=p['generator_index'],
            same_nearest_at_step1=fine[row['number']-1]['alternatives'][0]['generator_index'] == p['generator_index'],
            centroid_shift_pixels=float(np.linalg.norm(np.array(f['visible_centroid_xy'])-p['predicted_xy'])),
            step1_unknown_shift_bound_pixels=f['finite_grid_centroid_unknown_shift_bound_pixels']))
    save(out/'resolution.json', dict(case='minus-3592', step2=2, step1=1,
        step1_score=center_score(fine), records=convergence))
    report = dict(request='R210', purpose='Small assisted frozen-model correspondence pilot',
        model_indices_role='Tentative source-loop coordinates within each model; not inferred photo bead_index',
        center_definition='Unweighted area centroid of the predicted visible bead region, after all occlusion',
        interior_definition='Every saved positive integer pixel; no demand that an outward point lies in the patch',
        original_centers=len(centers), original_interior_references=len(interiors),
        count_hypotheses=[2698, 2833, 3592], phase_and_origin='Historical hand-specific seed, fixed; not optimized',
        geometry_changed=False, fitted=False, stretch_applied=False, accepted_correspondences=0,
        cases=cases, limitations=['Each reference need not be a different bead.',
            'A visible-region centroid is a geometric proxy for a hand-picked visible center, not an exact surface anchor.',
            'Scores depend on fixed centerline, projection, phase, origin and count; no helicity or exact-N inference.',
            'Unfinished ray pairs remain explicit, with a conservative finite-grid centroid shift bound.',
            'Patch coherence alone can occur under a wrong pose; same-body appearance contradictions are retained.',
            'The central-fitting gate requires exposed outward anchors, but these are not the center-scoring points.'])
    save(out/'report.json', report)
    image = np.array(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'))
    original = next(c for c in cases if c['name'] == 'minus-2698')
    dense = next(c for c in cases if c['name'] == 'minus-3592')
    candidates = [(a, b) for a, b in zip(original['interior_memberships'], dense['interior_memberships'])
        if a['coherent_central_membership'] and not b['unresolved_pixels'] and b['dominant_fraction'] < .95]
    a, b = max(candidates, key=lambda pair: pair[0]['dominant_fraction']-pair[1]['dominant_fraction'])
    record = next(r for r in interiors if r['observation_number'] == a['observation_number'])
    xy = np.array([(x, y) for y, lo, hi in record['region']['pixel_runs'] for x in range(lo, hi+1)])
    x, y = record['source_xy']
    fig, axes = plt.subplots(1, 3, figsize=(11, 4.5), constrained_layout=True)
    for ax in axes:
        ax.imshow(image, interpolation='nearest'); ax.set_xlim(x-40, x+40); ax.set_ylim(y+40, y-40); ax.axis('off')
    axes[0].set_title(f"Raw: automatic interior {record['observation_number']}")
    owner_rows = []
    for ax, case, membership in zip(axes[1:], [original, dense], [a, b]):
        config = case['configuration']; model = load_model(config, config['parameters'])
        geometry = model.geometry(np.arange(model.source.nbeads))
        owner, _, unfinished = rays(model, xy, geometry)
        labels = sorted(set(owner.tolist()))
        for j, label in enumerate(labels):
            use = owner == label
            color = 'magenta' if label < 0 else ['cyan', 'lime', 'orange', 'white'][j % 4]
            ax.scatter(xy[use, 0], xy[use, 1], s=8, color=color,
                marker='x' if label < 0 else '.', label=f"{'No model body' if label < 0 else 'Model '+str(label)}: {int(use.sum())}")
        ax.legend(fontsize=7, loc='upper left')
        ax.set_title(case['name']+f"; largest-body fraction {membership['dominant_fraction']:.0%}")
        owner_rows.append(dict(model=case['name'], membership=membership,
            pixel_xy=xy.tolist(), owners=owner.tolist(), unfinished_pairs=unfinished.tolist()))
    fig.suptitle('The same saved positive pixels under two frozen models.\n'
                 'Colors label model ownership only; no bead outline or photo identity is inferred.', fontsize=11)
    fig.savefig(out/'membership-contrast.png', dpi=170); plt.close(fig)
    save(out/'membership-contrast.json', dict(observation_id=record['observation_id'],
        observation_number=record['observation_number'], source_xy=record['source_xy'],
        selection='Largest membership-fraction difference: coherent minus2698 versus resolved split/background minus3592',
        cases=owner_rows))
    for name, crop in [('top-context', [1180, 220, 1730, 360]),
                       ('right-context', [1990, 590, 2110, 710]),
                       ('bend-context', [1160, 1420, 1310, 1570])]:
        plot_context(image, centers, cases, crop, out, name)
    fig, ax = plt.subplots(figsize=(10, 12), constrained_layout=True)
    ax.imshow(image)
    for r in interiors:
        ax.scatter(*r['source_xy'], s=8, facecolors='none', edgecolors='lime', linewidths=.5)
    ax.scatter([r['x'] for r in centers], [r['y'] for r in centers], color='orange', marker='+', s=35)
    for r in centers:
        ax.annotate(str(r['number']), (r['x'], r['y']), xytext=(5, 4), textcoords='offset points', fontsize=6)
    ax.set_title('Unchanged evidence: 41 maker visible centers (+), 208 colored interiors (green)')
    ax.axis('off'); fig.savefig(out/'whole-photo.png', dpi=170); plt.close(fig)
    # A small geometric-semantics query, not approval to continue the pilot.
    reference = next(r for r in centers if r['number'] == 5)
    lookup = {r['generator_index']: r for r in coarse_bank['records']}
    match = next(r for r in coarse['center_matches'] if r['number'] == 5)
    prediction = lookup[match['alternatives'][0]['generator_index']]
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.5), constrained_layout=True)
    x, y = reference['x'], reference['y']
    for ax in axes:
        ax.imshow(image, interpolation='nearest'); ax.set_xlim(x-45, x+45); ax.set_ylim(y+45, y-45); ax.axis('off')
    axes[0].set_title('Raw photo around saved center 5')
    axes[1].set_title('M = your mark; V = model visible centroid')
    axes[2].set_title('M = your mark; O = minor-outward point')
    points = dict(M=[x, y], V=prediction['visible_centroid_xy'], O=prediction['outward_xy'])
    for ax, other in zip(axes[1:], ['V', 'O']):
        for label in ['M', other]:
            xy = points[label]
            color = {'M': 'orange', 'V': 'cyan', 'O': 'magenta'}[label]
            ax.annotate(label, xy, xytext=((26, -24) if label == 'M' else (-24, 26)),
                textcoords='offset points', color=color, fontsize=14,
                arrowprops=dict(arrowstyle='->', color=color))
            ax.scatter(*xy, s=16, color=color)
    fig.suptitle('Q210.1: Which model points are inside the yellow photo bead containing M?\n'
                 'V and O are shown separately. Frozen minus-3592 proposal; no curve fit.', fontsize=11)
    fig.savefig(out/'question.png', dpi=170); plt.close(fig)
    save(out/'question-proposal.json', dict(question_id='Q210.1', model='minus-3592',
        center_number=5, center_id=reference['id'], points=points,
        tentative_generator_index=prediction['generator_index'],
        status='Unreviewed photo association; no promotion',
        region_record=prediction))
    source_paths = ['beads-photo-2.jpg', 'beads.pov', 'photo2/tangent_circles.py',
        'photo2/visible_correspondence.py', 'photo2/review_visible_correspondence.py',
        'photo2/test_visible_correspondence.py', 'photo2/bead_placement.py',
        'photo2/curved_surface_fit.py', 'photo2/local_surface_fit.py',
        'photo2/spline-seed-r175.json', 'photo2/review/r200/position-basis.json',
        'photo2/review/r201/interiors.json', 'photo2/review/r208/summary.json',
        'photo2/review/r179/minus-2698/parameters.json', 'photo2/review/r179/plus-2698/parameters.json']
    assert {p: sha(ROOT/p) for p in protected} == protected
    outputs = [c['region_bank_file'] for c in cases]+['report.json', 'calibration.json', 'resolution.json',
        'top-context.png', 'right-context.png', 'bend-context.png', 'whole-photo.png', 'question.png', 'question-proposal.json',
        'membership-contrast.png', 'membership-contrast.json']
    save(out/'summary.json', dict(request='R210', protected_inputs=protected,
        source_sha256={p: sha(ROOT/p) for p in source_paths},
        curated_sha256={p: sha(out/p) for p in outputs},
        reproduction='.venv/bin/python photo2/review_visible_correspondence.py',
        accepted_correspondences=0, centerline_changed=False, no_pending_old_questions=True))


if __name__ == '__main__':
    main()
