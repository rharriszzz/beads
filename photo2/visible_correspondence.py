"""Assisted model correspondence: visible-region centers and positive pixels.

No image detector, curve fitting, bead identity promotion or recovered index.
The complete model supplies occluders, including hidden and black beads.
"""
import numpy as np
from scipy.spatial import cKDTree
from tangent_circles import RADIUS, first_hits, visible_anchors


def rays(model, xy, geometry, chunk=8000):
    xy = np.asarray(xy, float).reshape(-1, 2)
    parts = [first_hits(model, xy[i:i+chunk], geometry) for i in range(0, len(xy), chunk)]
    if not parts:
        return np.empty(0, int), np.empty(0), np.empty(0, int)
    return tuple(np.concatenate([p[j] for p in parts]) for j in range(3))


def region_bank(model, observations, step=2):
    """Rasterize COMPLETE conservative bounds of nearby candidate bodies.

    Global integer-pixel grid, no crop to a bead's observation-centered window.
    First-hit ownership always uses every model body. Unknown ray pairs prevent
    certification of affected candidate bounds. Means can lie in a hole/gap.
    """
    if type(step) is not int or step < 1:
        raise ValueError('Positive integer raster step required')
    geometry = model.geometry(np.arange(model.source.nbeads))
    projected = model.view.project(geometry['centers'])
    bound = RADIUS*np.sqrt(1+.7**2)*model.view.scale
    distance, _ = cKDTree(np.asarray(observations)).query(projected)
    candidate = np.flatnonzero(distance <= 3*bound)
    squares = []
    for center in projected[candidate]:
        lo = np.floor((center-bound)/step).astype(int)*step
        hi = np.ceil((center+bound)/step).astype(int)*step
        xx, yy = np.meshgrid(np.arange(lo[0], hi[0]+step, step),
                             np.arange(lo[1], hi[1]+step, step))
        squares.append(np.column_stack((xx.ravel(), yy.ravel())))
    xy = np.unique(np.concatenate(squares), axis=0) if squares else np.empty((0, 2))
    owner, _, unfinished = rays(model, xy, geometry)
    visibility = visible_anchors(model, geometry)
    records = []
    # Include all verified visible portions, regardless of whether their outward
    # anchor is exposed. The latter remains a separate central-fitting gate.
    for index in candidate:
        use = (owner == index) & (unfinished == 0)
        if not np.any(use):
            continue
        unknown = (unfinished > 0) & np.all(np.abs(xy-projected[index]) <= bound, axis=1)
        centroid = xy[use].mean(axis=0)
        # Any excluded uncertain ray in this body's conservative bound might
        # add one area sample. This bounds movement of the finite-grid mean,
        # not continuous-area quadrature error or maker marking uncertainty.
        possible_shift = (int(unknown.sum())/(int(use.sum())+int(unknown.sum())) *
            float(np.max(np.linalg.norm(xy[unknown]-centroid, axis=1)))) if unknown.any() else 0.
        records.append(dict(generator_index=int(index), pixels=int(use.sum()),
            sampled_area_pixels2=int(use.sum())*step**2,
            visible_centroid_xy=centroid.tolist(),
            projected_physical_center_xy=projected[index].tolist(),
            outward_xy=visibility['xy'][index].tolist(),
            outward_exposed=bool(visibility['exposed'][index]),
            ray_uncertainty_in_bound=bool(unknown.any()),
            unknown_samples_in_bound=int(unknown.sum()),
            finite_grid_centroid_unknown_shift_bound_pixels=possible_shift))
    return dict(step_pixels=step, conservative_radius_pixels=float(bound),
        candidate_bodies=len(candidate), sampled_rays=len(xy),
        unfinished_rays=int(np.sum(unfinished > 0)), records=records), geometry


def nearest_centers(records, bank, xy_key='visible_centroid_xy'):
    """Independent nearest proposals, with alternatives and duplicate warnings.

    No forced one-to-one allocation: different observation records may refer to
    the same body. No exact uncertainty model for the maker's center is supplied.
    """
    # Keep the same native area gate when refining the raster resolution.
    eligible = [r for r in bank['records'] if r['outward_exposed'] and r['sampled_area_pixels2'] >= 48]
    result = []
    for record in records:
        xy = np.array([record['x'], record['y']])
        ordered = sorted((r for r in eligible if np.linalg.norm(np.array(r[xy_key])-xy)
            <= 3*bank['conservative_radius_pixels']),
            key=lambda r: np.linalg.norm(np.array(r[xy_key])-xy))
        alternatives = [dict(generator_index=r['generator_index'],
            predicted_xy=r[xy_key], distance_pixels=float(np.linalg.norm(np.array(r[xy_key])-xy)),
            finite_grid_centroid_unknown_shift_bound_pixels=r['finite_grid_centroid_unknown_shift_bound_pixels'])
            for r in ordered[:2]]
        result.append(dict(observation_id=record['id'], number=record['number'],
            observed_xy=xy.tolist(), sector=min(7, int(record['approximate_image_arc_fraction']*8)),
            alternatives=alternatives,
            nearest_gap_pixels=(alternatives[1]['distance_pixels']-alternatives[0]['distance_pixels'])
                if len(alternatives) == 2 else None,
            bead_index=None, status='Tentative within this frozen model only'))
    return result


def center_score(matches):
    # Missing associations remain in the denominator and cannot improve a score.
    if any(not r['alternatives'] for r in matches):
        return dict(complete=False, missing=sum(not r['alternatives'] for r in matches),
                    sse_pixels2=None, rms_pixels=None, balanced_rms_pixels=None)
    squared = np.array([r['alternatives'][0]['distance_pixels']**2 for r in matches])
    sectors = np.array([r['sector'] for r in matches])
    means = [float(squared[sectors == s].mean()) for s in range(8) if np.any(sectors == s)]
    ids = [r['alternatives'][0]['generator_index'] for r in matches]
    return dict(complete=True, missing=0, sse_pixels2=float(squared.sum()),
        rms_pixels=float(np.sqrt(squared.mean())), balanced_rms_pixels=float(np.sqrt(np.mean(means))),
        occupied_sectors=len(means), sector_mse_pixels2=means,
        duplicate_nearest_associations=len(ids)-len(set(ids)),
        small_alternative_gap_under_2_pixels=sum(r['nearest_gap_pixels'] is not None and
            r['nearest_gap_pixels'] < 2 for r in matches))


def interior_membership(model, records, geometry):
    groups = [np.array([(x, y) for y, lo, hi in r['region']['pixel_runs']
                       for x in range(lo, hi+1)], float) for r in records]
    lengths = [len(p) for p in groups]
    all_xy = np.concatenate(groups)
    owner, _, unfinished = rays(model, all_xy, geometry)
    visibility = visible_anchors(model, geometry)
    rows = []; cursor = 0
    for record, length in zip(records, lengths):
        own = owner[cursor:cursor+length]; unknown = unfinished[cursor:cursor+length] > 0
        ids, counts = np.unique(own[~unknown], return_counts=True)
        histogram = {str(int(i)): int(c) for i, c in zip(ids, counts)}
        valid = [(int(c), int(i)) for i, c in zip(ids, counts) if i >= 0]
        dominant_count, dominant = max(valid) if valid else (0, -1)
        exposed = dominant >= 0 and bool(visibility['exposed'][dominant])
        rows.append(dict(observation_id=record['observation_id'],
            observation_number=record['observation_number'], source_xy=record['source_xy'],
            appearance_mode=record['appearance_mode'], pixels=length,
            owner_histogram=histogram, unresolved_pixels=int(unknown.sum()),
            dominant_generator_index=dominant if dominant >= 0 else None,
            dominant_fraction=dominant_count/length, outward_exposed=exposed,
            coherent_central_membership=bool(dominant_count/length >= .95 and exposed and not unknown.any()),
            bead_index=None, status='Conditional model membership, not confirmed photo ownership'))
        cursor += length
    return rows


def mode_conflicts(interiors):
    buckets = {}
    for row in interiors:
        if row['coherent_central_membership']:
            buckets.setdefault(row['dominant_generator_index'], []).append(row)
    return [dict(generator_index=index,
        observation_numbers=[r['observation_number'] for r in rows],
        modes=[r['appearance_mode'] for r in rows]) for index, rows in buckets.items()
        if len({r['appearance_mode'] for r in rows}) > 1]
