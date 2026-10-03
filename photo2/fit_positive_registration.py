"""R214: phase/origin registration from positive patches and visible centers.

Assisted diagnostic on a frozen centerline/view/count hypothesis. No complete
photo boundaries, dark-gap classifier, automatic bead IDs or pattern inputs.
"""
import copy
import numpy as np
from tangent_circles import load_model
from visible_correspondence import region_bank, nearest_centers, interior_membership, rays


def canonical_pose(phase_delta, origin_shift_beads, nrows, nbeads, hand):
    """One source-index interval is enough when phase can span a full turn.

    Removing k/N from origin and k*hand*360*nrows/N from phase relabels model
    index i as i-k. This is a geometric gauge, never a photo index assignment.
    """
    k = int(np.floor(origin_shift_beads+.5))
    shift = float(origin_shift_beads-k)
    phase = (phase_delta-k*hand*360*nrows/nbeads+180) % 360-180
    return float(phase), shift


def posed_config(seed, phase_delta, origin_shift_beads):
    config = copy.deepcopy(seed)
    p = config['parameters']
    p['phase'] = float(p['phase']+phase_delta)
    p['origin_fraction'] = float((p['origin_fraction']+origin_shift_beads/p['nbeads']) % 1)
    return config


def balanced(values, sectors):
    values = np.asarray(values, float); sectors = np.asarray(sectors, int)
    means = {str(int(s)): float(values[sectors == s].mean()) for s in sorted(set(sectors))}
    return float(np.mean(list(means.values()))), means


def metrics(matches, memberships, patch_sectors, diameter, patch_weight=1.):
    if diameter <= 0 or patch_weight < 0 or not matches or not memberships:
        raise ValueError('Positive scale and nonempty center/patch groups required')
    distances2 = [r['alternatives'][0]['distance_pixels']**2 if r['alternatives'] else 9*diameter**2
                  for r in matches]
    center_mse, center_sectors = balanced(distances2, [r['sector'] for r in matches])
    # Unknown pixels are excluded by the existing first-hit ownership routine,
    # but remain in each patch denominator. Hidden outward anchors do not count
    # as central matching support. All patches contribute, even under bad poses.
    support = [r['dominant_fraction'] if r['outward_exposed'] else 0. for r in memberships]
    patch_support, support_sectors = balanced(support, patch_sectors)
    missing = sum(not r['alternatives'] for r in matches)
    return dict(objective=center_mse/diameter**2+patch_weight*(1-patch_support),
        balanced_center_rms_pixels=float(np.sqrt(center_mse)), center_mse_by_sector=center_sectors,
        balanced_patch_support=patch_support, patch_support_by_sector=support_sectors,
        coherent_central_patches=sum(r['coherent_central_membership'] for r in memberships),
        total_patches=len(memberships), total_centers=len(matches), missing_centers=missing,
        uncertain_patches=sum(r['unresolved_pixels'] > 0 for r in memberships),
        patch_weight=patch_weight, diameter_pixels=diameter)


def same_body_memberships(model, geometry, groups):
    results = []
    for group in groups:
        owner, _, unfinished = rays(model, np.asarray(group['points_xy'], float), geometry)
        coherent = bool(np.all(owner >= 0) and len(set(owner.tolist())) == 1 and not unfinished.any())
        results.append(dict(name=group['name'], owner=owner.tolist(), unfinished=unfinished.tolist(), coherent=coherent))
    return results


def rank_trial(trial):
    # Supplied positive membership facts precede the soft alignment objective.
    # If none satisfy them, the returned diagnostic is explicitly infeasible.
    return (not trial['same_body_constraints_satisfied'], trial['metrics']['objective'],
            abs(trial['phase_delta_degrees']), abs(trial['origin_shift_beads']), trial['candidate'])


def evaluate(config, centers, patches, patch_sectors, diameter, same_body_groups=()):
    model = load_model(config, config['parameters'])
    bank, geometry = region_bank(model, [[r['x'], r['y']] for r in centers], step=2)
    matches = nearest_centers(centers, bank)
    members = interior_membership(model, patches, geometry)
    return dict(configuration=config, metrics=metrics(matches, members, patch_sectors, diameter),
        center_matches=matches, patch_memberships=members,
        region_bank=bank, geometry=geometry, model=model,
        same_body_memberships=same_body_memberships(model, geometry, same_body_groups))


def search(seed, centers, patches, patch_sectors, diameter, progress=None, same_body_groups=()):
    """Finite deterministic search; only the supplied training groups enter it."""
    source = load_model(seed, seed['parameters']).source
    trials = []; cache = {}
    def sample(phase, shift, stage):
        phase, shift = canonical_pose(phase, shift, source.nrows, source.nbeads, source.helicity)
        key = (round(phase, 9), round(shift, 9))
        if key in cache:
            return cache[key]
        result = evaluate(posed_config(seed, phase, shift), centers, patches, patch_sectors, diameter, same_body_groups)
        trial = dict(candidate=len(trials), stage=stage, phase_delta_degrees=phase,
            origin_shift_beads=shift, metrics=result['metrics'],
            same_body_memberships=result['same_body_memberships'],
            same_body_constraints_satisfied=all(g['coherent'] for g in result['same_body_memberships']))
        trials.append(trial); cache[key] = trial
        if progress:
            progress(trial)
        return trial
    # Historical alignment is included. Soft loss need not improve if the old
    # alignment violates an explicit maker-confirmed same-body constraint.
    sample(0., 0., 'baseline')
    for phase in np.arange(-160., 161., 40.):
        for shift in [-1/3, 0., 1/3]:
            sample(float(phase), shift, 'coarse')
    anchors = sorted(trials, key=rank_trial)[:2]
    for anchor in anchors:
        for dp in [-20., 0., 20.]:
            for ds in [-1/6, 0., 1/6]:
                sample(anchor['phase_delta_degrees']+dp, anchor['origin_shift_beads']+ds, 'refine')
    winner = min(trials, key=rank_trial)
    sensitivity = []
    for weight in [.5, 2.]:
        best = min(trials, key=lambda t:(not t['same_body_constraints_satisfied'],
                   (t['metrics']['balanced_center_rms_pixels']/diameter)**2+
                   weight*(1-t['metrics']['balanced_patch_support']), t['candidate']))
        sensitivity.append(dict(patch_weight=weight, candidate=best['candidate'],
            phase_delta_degrees=best['phase_delta_degrees'], origin_shift_beads=best['origin_shift_beads']))
    return dict(winner=winner, trials=trials, weight_sensitivity=sensitivity,
        configuration=posed_config(seed, winner['phase_delta_degrees'], winner['origin_shift_beads']),
        training_only=True, same_body_groups=list(same_body_groups),
        feasible_trials=sum(t['same_body_constraints_satisfied'] for t in trials),
        fit_dimensions=['minor phase', 'origin'],
        geometry_scope='Centerline, camera, physical sizes, count and stretch fixed')
