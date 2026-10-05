"""R220: compare conservative rims on image-derived R218 colored proposals.

Only input appearance and the frozen automatic extractor determine the masks.
All methods remove pixels; reflections and unresolved/missing bodies stay explicit.
Retaining a fraction of a candidate does not measure actual visible-bead coverage.
"""
import argparse
import copy
import json
import os
import uuid
from pathlib import Path

os.environ.setdefault('MPLCONFIGDIR', '/tmp/beads-segmentation-mpl')
import numpy as np
from PIL import Image, ImageOps
from scipy import ndimage as ndi

from auto_label_beads import ROOT, sha
from refine_colored_masks import refine


METHODS = ('inset', 'diffuse', 'radial', 'stable')
PARAMETERS = {
    'inset_diameters': .055,
    'diffuse_floor_fraction': .45,
    'radial_step_pixels': .5,
    'radial_angles': 180,
    'radial_inset_diameters': .025,
    'stable_sigmas_diameters': [.025, .05, .075],
    'stable_required_votes': 2,
    'stable_inset_diameters': .045,
    'stable_weak_rim_fraction': .15,
}


def connected_to_seed(mask, seed):
    """Do not cross a rejected pixel bridge to keep a separate bright neighbor."""
    y, x = seed
    labels, _ = ndi.label(mask)
    if not (0 <= y < mask.shape[0] and 0 <= x < mask.shape[1]) or not labels[y, x]:
        return np.zeros_like(mask)
    return labels == labels[y, x]


def diffuse_fields(image, arrays, diameter):
    value = np.asarray(image, np.float32).max(axis=2) / 255
    median = ndi.median_filter(value, size=max(3, int(.20 * diameter) // 2 * 2 + 1))
    diffuse = np.where(arrays['reflections'] > 0, median, value)
    smooth = [ndi.gaussian_filter(diffuse, max(.5, s * diameter))
              for s in PARAMETERS['stable_sigmas_diameters']]
    return diffuse, smooth


def radial_interior(candidate, smooth, seed, reference, diameter):
    """Keep only points reached before the first support/brightness drop.

    This is a conservative interior test, not an inferred physical boundary.
    Its fixed angular/radial resolution is retained as a limitation.
    """
    y, x = seed
    yy, xx = np.indices(candidate.shape)
    radius = np.hypot(xx - x, yy - y)
    extent = float(radius[candidate].max())
    step = PARAMETERS['radial_step_pixels']
    distances = np.arange(0, extent + step, step)
    angles = np.arange(PARAMETERS['radial_angles']) * (2 * np.pi / PARAMETERS['radial_angles'])
    sample_y = y + np.sin(angles)[:, None] * distances
    sample_x = x + np.cos(angles)[:, None] * distances
    values = ndi.map_coordinates(smooth, [sample_y, sample_x], order=1, mode='constant', cval=0)
    support = ndi.map_coordinates(candidate.astype(np.uint8), [sample_y, sample_x], order=0, mode='constant', cval=0) > 0
    good = support & (values >= PARAMETERS['diffuse_floor_fraction'] * reference)
    stops = np.sum(np.logical_and.accumulate(good, axis=1), axis=1) * step
    stops = np.maximum(0, stops - step - PARAMETERS['radial_inset_diameters'] * diameter)
    angle = np.mod(np.arctan2(yy-y, xx-x), 2*np.pi)
    index = np.rint(angle * len(angles) / (2*np.pi)).astype(int) % len(angles)
    return candidate & (radius <= stops[index])


def trim_region(candidate, old_core, diffuse, smooth, seed, diameter, method, stable_rim_rule='rank', valley=None, stable_raw_floor=True):
    if method not in METHODS:
        raise ValueError('Unknown trimming method')
    distance = ndi.distance_transform_edt(np.pad(candidate, 1))[1:-1, 1:-1]
    reference = float(np.quantile(diffuse[candidate], .90))
    if method == 'inset':
        support = candidate & (distance >= PARAMETERS['inset_diameters'] * diameter)
    elif method == 'diffuse':
        support = connected_to_seed(candidate & (diffuse >= PARAMETERS['diffuse_floor_fraction'] * reference), seed)
    elif method == 'radial':
        support = radial_interior(candidate, smooth[1], seed, reference, diameter)
    else:
        votes = np.zeros(candidate.shape, np.uint8)
        for values in smooth:
            local_reference = float(np.quantile(values[candidate], .90))
            votes += connected_to_seed(candidate & (values >= PARAMETERS['diffuse_floor_fraction'] * local_reference), seed)
        if stable_rim_rule == 'inset':
            rim = distance >= PARAMETERS['stable_inset_diameters'] * diameter
        elif stable_rim_rule == 'rank':
            # Fractional ranking avoids an entire one-pixel shell disappearing
            # at once. Its 85% candidate preference is not actual photo recall.
            confidence = distance + .25 * diffuse / max(reference, .02)
            if valley is not None:
                confidence -= .25 * valley
            rim = ((distance >= max(.5, .018 * diameter))
                   & (confidence >= np.quantile(confidence[candidate], PARAMETERS['stable_weak_rim_fraction'])))
        else:
            raise ValueError('Unknown stable rim rule')
        support = candidate & (votes >= PARAMETERS['stable_required_votes']) & rim
        if stable_raw_floor:
            # Smoothing must not certify a dark appendage merely because it
            # borrows brightness from an adjacent supported colored face.
            support &= diffuse >= PARAMETERS['diffuse_floor_fraction'] * reference
    # A new trim cannot inherit an earlier confirmation of a larger extent.
    return connected_to_seed(support & old_core, seed)


def trim(image, digest, method='stable', base=None, stable_rim_rule='rank', stable_raw_floor=True):
    report, arrays = refine(image, digest) if base is None else base
    if report['image_sha256'] != digest or arrays['retained'].shape != image.shape[:2]:
        raise ValueError('Cached extraction does not match input image')
    if method not in METHODS:
        raise ValueError('Unknown trimming method')
    diameter = report['parameters']['native_diameter']
    diffuse, smooth = diffuse_fields(image, arrays, diameter)
    retained = np.zeros_like(arrays['retained'])
    central = np.zeros_like(retained)
    records, omitted = [], []
    by_number = {r['region_number']: r for r in report['records']}
    signature = json.dumps(dict(method=method, stable_rim_rule=stable_rim_rule,
                                stable_raw_floor=stable_raw_floor, **PARAMETERS), sort_keys=True)
    for ident, sl in enumerate(ndi.find_objects(arrays['candidate']), 1):
        if sl is None or ident not in by_number:
            continue
        row = copy.deepcopy(by_number[ident])
        candidate = arrays['candidate'][sl] == ident
        old_core = arrays['retained'][sl] == ident
        x, y = row['seed_xy']
        local_seed = (round(y)-sl[0].start, round(x)-sl[1].start)
        core = trim_region(candidate, old_core, diffuse[sl], [v[sl] for v in smooth], local_seed, diameter,
                           method, stable_rim_rule, arrays['valley'][sl], stable_raw_floor)
        row['source_observation_id'] = row['observation_id']
        row['observation_id'] = str(uuid.uuid5(uuid.NAMESPACE_URL, f'{digest}:R220:{signature}:{row["source_observation_id"]}'))
        row['source_retained_pixels'] = row['retained_pixels']
        row['retained_pixels'] = int(core.sum())
        row['removed_pixels'] = row['source_retained_pixels'] - row['retained_pixels']
        row['retained_fraction_of_candidate'] = float(core.sum() / candidate.sum())
        row['retained_fraction_of_source_mask'] = float(core.sum() / max(1, old_core.sum()))
        row['retained_components'] = int(ndi.label(core)[1])
        row['retained_centroid_xy'] = None
        row['status'] = 'Unreviewed trimmed automatic extent; not a confirmed bead or physical center'
        if core.any():
            retained[sl][core] = ident
            if row['central_candidate']:
                central[sl][core] = ident
            coords = np.argwhere(core)[:, ::-1] + [sl[1].start, sl[0].start]
            row['retained_centroid_xy'] = coords.mean(axis=0).tolist()
        else:
            omitted.append(dict(region_number=ident, source_observation_id=row['source_observation_id'],
                                seed_xy=row['seed_xy'], reason='No seed-connected pixels after conservative trimming'))
        records.append(row)
    result = copy.deepcopy(report)
    result['request'] = 'R220'
    result['source_request'] = report['request']
    result['records'] = records
    result['trimming_parameters'] = dict(method=method, stable_rim_rule=stable_rim_rule,
        stable_raw_floor=stable_raw_floor, **PARAMETERS,
        appearance_and_scale='Learned by frozen R215/R218 from each input',
        no_new_pixels=True, reflection_masks_unchanged=True, prior_confirmations_inherited=False)
    result['omitted_by_trimming'] = omitted
    result['source_counts'] = report['counts']
    result['counts'] = dict(report['counts'], regions=len(records),
        nonempty_regions=sum(r['retained_pixels'] > 0 for r in records),
        retained_pixels=int((retained>0).sum()),
        removed_source_pixels=int(((arrays['retained']>0)&(retained==0)).sum()),
        boundary_band_pixels=int(((arrays['candidate']>0)&(retained==0)).sum()),
        central_candidate_regions=sum(r['central_candidate'] and r['retained_pixels']>0 for r in records),
        central_candidate_pixels=int((central>0).sum()))
    result['actual_photo_visible_pixel_coverage'] = None
    result['status'] = 'Image-derived trimmed proposals; no complete trusted inventory or physical bead centers'
    new_arrays = dict(arrays, retained=retained, boundary_band=(arrays['candidate']>0)&(retained==0),
                      diffuse_retained=np.where(arrays['reflections']>0,0,retained), central_candidates=central,
                      removed_source=(arrays['retained']>0)&(retained==0))
    return result, new_arrays


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', type=Path, default=ROOT/'beads-photo-2.jpg')
    parser.add_argument('--output', type=Path, default=ROOT/'photo2/output/r220')
    parser.add_argument('--method', choices=METHODS, default='stable')
    parser.add_argument('--stable-rim-rule', choices=('rank','inset'), default='rank', help='Inset reproduces the earlier development comparison')
    parser.add_argument('--no-stable-raw-floor', action='store_true', help='Diagnostic ablation that permits blur-supported dark extensions')
    args = parser.parse_args()
    image = np.asarray(ImageOps.exif_transpose(Image.open(args.image)).convert('RGB'))
    report, arrays = trim(image, sha(args.image), args.method, stable_rim_rule=args.stable_rim_rule,
                          stable_raw_floor=not args.no_stable_raw_floor)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output/'regions.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    np.savez_compressed(args.output/'pixel-masks.npz', **arrays)
    print(json.dumps(dict(method=args.method, counts=report['counts'])), flush=True)


if __name__ == '__main__':
    main()
