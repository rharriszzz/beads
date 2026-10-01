"""R192: native-pixel interior regions and separate black-reflection evidence.

Automatic candidates, not a trusted complete inventory. No simulated placement,
old spline, hand labels or saved hue boxes enter detection or region extraction.
Confirmed maker evidence is incorporated only by the separate review curator.
"""
import argparse
import json
import os
import uuid
from pathlib import Path

os.environ.setdefault('MPLCONFIGDIR', '/tmp/beads-evidence-mpl')

import numpy as np
from PIL import Image, ImageOps
from matplotlib.colors import rgb_to_hsv
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from skimage.feature import peak_local_max
from skimage.measure import find_contours

import auto_label_beads as auto
from label_beads import atomic_json


def hue_distance(a, b):
    return abs((np.asarray(a)-b+180) % 360-180)


def connected_near(mask, xy, maximum_shift):
    labels, _ = ndi.label(mask)
    y, x = np.rint(xy[::-1]).astype(int)
    if 0 <= y < mask.shape[0] and 0 <= x < mask.shape[1] and labels[y, x]:
        return labels == labels[y, x]
    positions = np.argwhere(mask)
    if not len(positions):
        raise ValueError('No supported connected region')
    distance = np.linalg.norm(positions-xy[::-1], axis=1)
    closest = int(np.argmin(distance))
    if distance[closest] > maximum_shift:
        raise ValueError('Supported region is too far from the proposed seed')
    return labels == labels[tuple(positions[closest])]


def encode_pixels(mask, origin):
    """Native integer pixel centers as [y, x_start, x_end_inclusive] runs."""
    runs = []
    for y in np.flatnonzero(mask.any(axis=1)):
        x = np.flatnonzero(mask[y])
        groups = np.split(x, np.flatnonzero(np.diff(x) > 1)+1)
        runs.extend([[int(y+origin[1]), int(g[0]+origin[0]), int(g[-1]+origin[0])]
                     for g in groups])
    return runs


def region_record(support, point, origin, inset=2., footprint=None):
    # Pad with rejected pixels so crop edges never acquire an artificial margin.
    distance = ndi.distance_transform_edt(np.pad(support, 1))[1:-1, 1:-1]
    core = connected_near(distance >= inset+1, point, maximum_shift=3.)
    if footprint is not None:
        yy, xx = np.indices(core.shape)
        core &= np.hypot(xx-point[0], yy-point[1]) <= footprint
        core = connected_near(core, point, maximum_shift=3.)
    if core.sum() < 12:
        raise ValueError('Inset leaves fewer than 12 native pixels')
    if np.any(ndi.binary_fill_holes(core) & ~core):
        raise ValueError('Interior contains unresolved holes; no filling permitted')
    loops = [p for p in find_contours(np.pad(core, 1).astype(float), .5)
             if len(p) > 3 and np.allclose(p[0], p[-1])]
    if len(loops) != 1:
        raise ValueError('No single closed interior route')
    loop = loops[0][:, ::-1]-1+origin
    return dict(pixel_runs=encode_pixels(core, origin), pixels=int(core.sum()),
                loop_xy=loop.tolist(), minimum_support_margin=float(distance[core].min()),
                margin_role='Distance to rejected appearance/support pixels; true bead boundary remains unmeasured'), core


def extract_region(hsv, point, diameter, nearest, modes):
    seed = np.asarray(point['source_xy'])
    guard = min(.40*diameter, .44*nearest)
    if guard < 4:
        raise ValueError('Nearby competing observation leaves insufficient spatial guard')
    size = np.array(hsv.shape[1::-1])
    lo = np.maximum(0, np.floor(seed-guard-2)).astype(int)
    hi = np.minimum(size, np.ceil(seed+guard+3)).astype(int)
    local = hsv[lo[1]:hi[1], lo[0]:hi[0]]
    yy, xx = np.mgrid[lo[1]:hi[1], lo[0]:hi[0]]
    disk = np.hypot(xx-seed[0], yy-seed[1]) <= guard
    patch = np.hypot(xx-seed[0], yy-seed[1]) <= min(3., guard*.35)
    hue, sat, value = local[:, :, 0]*360, local[:, :, 1], local[:, :, 2]
    params = dict(spatial_guard_pixels=float(guard), support_inset_pixels=2.)
    reflection = None
    if point['kind'] == 'chromatic':
        mode = modes[point['appearance_mode']-1]
        useful = patch & (sat > .2)
        if not useful.any():
            raise ValueError('Proposed chromatic seed has no chromatic local evidence')
        saturation_floor = max(.2, float(np.quantile(sat[useful], .1)*.7))
        value_floor = float(np.quantile(value[useful], .5)*.72)
        support = disk & (hue_distance(hue, mode) <= 20) & (sat >= saturation_floor)
        support &= (value >= value_floor) & (value >= ndi.gaussian_filter(value, 2)*.75)
        params.update(hue_mode_degrees=mode, hue_halfwidth_degrees=20,
                      saturation_floor=saturation_floor, value_floor=value_floor)
    else:
        # Refine brightness within the accepted seed's immediate neighborhood.
        near = np.hypot(xx-seed[0], yy-seed[1]) <= min(guard*.65, diameter*.24)
        peak = float(value[near].max())
        surround = disk & ~patch
        baseline = float(np.median(value[surround]))
        bright = disk & near & (value >= max(peak*.72, baseline+(peak-baseline)*.6))
        bright = connected_near(bright, seed-lo, maximum_shift=diameter*.24)
        if bright.sum() < 2 or peak-baseline < .04:
            raise ValueError('No distinct native-pixel reflection above the local surround')
        weights = np.maximum(value[bright]-baseline, .001)**2
        reflection_xy = np.average(np.column_stack([xx[bright], yy[bright]]), axis=0, weights=weights)
        alternative_positions = []
        for threshold in [.66, .78]:
            alternative = near & (value >= max(peak*threshold, baseline+(peak-baseline)*.6))
            alternative = connected_near(alternative, seed-lo, maximum_shift=diameter*.24)
            alternative_positions.append(np.average(np.column_stack([xx[alternative], yy[alternative]]),
                axis=0, weights=np.maximum(value[alternative]-baseline, .001)**2).tolist())
        distance = ndi.distance_transform_edt(~bright)
        dark_limit = float(np.quantile(value[surround], .65))
        neutral_limit = min(.5, float(np.quantile(sat[bright], .9)+.18))
        support = disk & (distance <= min(7., diameter*.26))
        support &= ((value <= dark_limit) | (sat <= neutral_limit) | bright)
        dark = support & ~bright & (value <= dark_limit)
        if dark.sum() < 8:
            raise ValueError('Reflection has insufficient separate dark-body evidence')
        reflection = dict(xy=reflection_xy.tolist(), peak_value=peak, surround_value=baseline,
                          pixel_runs=encode_pixels(bright, lo), pixels=int(bright.sum()),
                          threshold_alternative_positions=alternative_positions,
                          threshold_sensitivity_pixels=float(np.max(np.linalg.norm(np.array(alternative_positions)-reflection_xy, axis=1))),
                          status='Localized bright reflection candidate; body identity not certified',
                          role='Specular appearance position, not a body center or boundary')
        params.update(dark_surround_limit=dark_limit, neutral_transition_limit=neutral_limit,
                      separate_dark_support_pixels=int(dark.sum()),
                      reflection_neighborhood_pixels=min(7., diameter*.26))
    support = connected_near(support, seed-lo, maximum_shift=3.)
    anchor = seed-lo if reflection is None else reflection_xy-lo
    footprint = min(5. if reflection is None else 4., diameter*(.14 if reflection is None else .12), guard*.65)
    params['maximum_core_footprint_radius_pixels'] = float(footprint)
    try:
        region, core = region_record(support, anchor, lo, footprint=footprint)
    except ValueError as exc:
        if reflection is None:raise
        return dict(region=None, reflection=reflection, parameters=params,
                    unresolved_region_reason=str(exc))
    params['core_value_p10_p50_p90'] = np.quantile(value[core], [.1, .5, .9]).tolist()
    return dict(region=region, reflection=reflection, parameters=params)


def additional_search(hsv, result, diameter):
    """Independent native chromatic peaks and unassociated dark areas for audit.

    Dark patches are not black-bead labels: seams and shadows can satisfy this
    diagnostic. Unmatched pixels/peaks must never be dropped from coverage claims.
    """
    height, width = hsv.shape[:2]
    band = np.array(Image.fromarray(result['band']).resize((width, height), Image.Resampling.NEAREST), bool)
    foreground = np.array(Image.fromarray(result['foreground']).resize((width, height), Image.Resampling.NEAREST), bool)
    clearance = ndi.distance_transform_edt(band)
    hue, sat, value = hsv[:, :, 0]*360, hsv[:, :, 1], hsv[:, :, 2]
    local_value = ndi.gaussian_filter(value, 4.)
    seeds = np.array([p['source_xy'] for p in result['points']])
    tree = cKDTree(seeds)
    extra = []
    for mode_number, mode in enumerate(result['parameters']['hue_modes_degrees'], 1):
        support = band & foreground & (hue_distance(hue, mode) < 20)
        support &= (sat > result['parameters']['saturation_floor']) & (value > local_value*.75)
        distance = ndi.distance_transform_edt(support)
        locations = peak_local_max(ndi.gaussian_filter(distance, .7),
                                  min_distance=max(3, int(diameter*.45)),
                                  threshold_abs=max(3., diameter*.12), labels=support)
        for y, x in locations:
            if clearance[y, x] < diameter*.7:
                continue
            nearest = float(tree.query([x, y])[0])
            if nearest <= diameter*.6:
                continue
            extra.append(dict(source_xy=[float(x), float(y)], kind='chromatic',
                              appearance_mode=mode_number, source='native unresolved-coverage search',
                              band_clearance=float(clearance[y, x]*np.sqrt(np.prod(result['scale']))),
                              station=None, baseline_nearest_pixels=nearest))
    dark_limit = float(np.quantile(value[foreground & band], .25))
    dark = band & (value < dark_limit)
    locations = peak_local_max(ndi.gaussian_filter(ndi.distance_transform_edt(dark), .7),
                              min_distance=max(3, int(diameter*.5)),
                              threshold_abs=max(2., diameter*.10), labels=dark)
    reflection_seeds = np.array([p['source_xy'] for p in result['points'] if p['kind']=='dark-reflection'])
    dark_tree = cKDTree(reflection_seeds) if len(reflection_seeds) else None
    unresolved = []
    for y, x in locations:
        if clearance[y, x] < diameter*.7:
            continue
        if dark_tree is not None and dark_tree.query([x, y])[0] < diameter*.65:
            continue
        unresolved.append(dict(xy=[int(x), int(y)], value=float(value[y, x]),
                               role='Unassociated dark region: possible body, seam or shadow; not a bead count'))
    return extra, unresolved


def inventory(image):
    result = auto.detect(image)
    hsv = rgb_to_hsv(np.asarray(image, float)/255)
    diameter = result['diameter']/np.sqrt(np.prod(result['scale']))
    extra, dark = additional_search(hsv, result, diameter)
    points = [dict(p, source='baseline image-only detector') for p in result['points']]+extra
    xy = np.array([p['source_xy'] for p in points])
    distances = cKDTree(xy).query(xy, k=2)[0][:, 1]
    records = []
    for i, (point, nearest) in enumerate(zip(points, distances), 1):
        row = dict(observation_number=i, seed_xy=point['source_xy'], kind=point['kind'],
                   appearance_mode=point['appearance_mode'], source=point['source'],
                   baseline_station=point.get('station'), confirmation='unreviewed',
                   eligibility='candidate central body', neighbors_close_pixels=float(nearest))
        if point['band_clearance'] < result['diameter']*.7:
            row.update(status='excluded-edge-uncertainty', reason='Close to approximate image search-band edge')
        else:
            try:
                evidence = extract_region(hsv, point, diameter, nearest,
                                          result['parameters']['hue_modes_degrees'])
                row.update(evidence, status='region-proposal' if evidence['region'] else 'reflection-only-proposal')
            except ValueError as exc:
                row.update(status='unresolved-region', reason=str(exc))
        records.append(row)
    return dict(records=records, unmatched_dark_areas=dark, native_extra_seeds=len(extra),
                parameters=dict(detector=result['parameters'], native_diameter=float(diameter),
                                central_guard_diameters=.7, minimum_core_pixels=12,
                                role='Input-only candidate evidence; no completeness/ownership trust from thresholds alone'),
                excluded_detector_features=result['excluded'],
                coverage='All extracted/proposed/excluded/unresolved observations retained. Not a complete or one-per-body inventory.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', type=Path, default=auto.ROOT/'beads-photo-2.jpg')
    parser.add_argument('--output', type=Path, default=auto.ROOT/'photo2/output/r192')
    args = parser.parse_args()
    if (args.output/'inventory.json').exists():
        parser.error('Existing inventory is protected; use a fresh output directory')
    args.output.mkdir(parents=True, exist_ok=True)
    image = ImageOps.exif_transpose(Image.open(args.image)).convert('RGB')
    data = inventory(np.array(image))
    digest = auto.sha(args.image)
    for row in data['records']:
        x, y = row['seed_xy']
        row['observation_id'] = str(uuid.uuid5(uuid.NAMESPACE_URL, f'{digest}:automatic:{x:.3f}:{y:.3f}'))
    data.update(request='R192', image_sha256=digest, source_size=list(image.size),
                sources={str(p.relative_to(auto.ROOT)):auto.sha(p) for p in
                         [Path(__file__), auto.ROOT/'photo2/auto_label_beads.py']})
    atomic_json(args.output/'inventory.json', data)
    print({s:sum(r['status']==s for r in data['records']) for s in
           ['region-proposal', 'reflection-only-proposal', 'unresolved-region', 'excluded-edge-uncertainty']},
          'extra colored seeds',data['native_extra_seeds'],'unassociated dark areas',len(data['unmatched_dark_areas']))


if __name__ == '__main__':
    main()
