"""R190: provisional periodic tube middle from image-derived colored bodies.

This fits paired local *interior quantiles*, never a paper/bead boundary or
physical outward anchor. Input-only proposals supply stations; the old spline
and maker centers are evaluator-only. Reviewed exclusions are explicitly an
optional assisted diagnostic, rather than undisclosed automatic priors.
"""
import argparse
import json
from pathlib import Path

import numpy as np

import auto_label_beads as auto
from colored_centerline_evidence import colored_subset
from label_beads import atomic_json


def fourier(u, harmonics, derivative=False):
    u = np.asarray(u)
    columns = [np.zeros_like(u) if derivative else np.ones_like(u)]
    for k in range(1, harmonics + 1):
        a = 2 * np.pi * k * u
        columns.extend([-2*np.pi*k*np.sin(a), 2*np.pi*k*np.cos(a)] if derivative
                       else [np.cos(a), np.sin(a)])
    return np.column_stack(columns)


def local_pairs(points, axis, diameter, excluded=(), window=6., quantile=.15):
    """Pair cross-strip tails at a shared station; retain unsupported stations.

    Both sides are required, with more than one observation supporting each
    tail. Missing sides never borrow a centerline point from the old curve.
    Positions are image-analysis pixels, not calibrated world coordinates.
    """
    length = len(axis['xy'])
    number = np.array([p['observation_number'] for p in points])
    station = np.array([p['station'] for p in points])
    cross = np.array([p['cross'] for p in points])
    radius = np.array([p['inset_support_radius'] for p in points])
    area = np.array([p['support_area'] for p in points])
    admitted = (~np.isin(number, list(excluded)) & (radius >= diameter*.16)
                & (area >= diameter**2*.12))
    count = max(48, int(np.ceil(length/(diameter*2))))
    records = []
    for s in np.linspace(0, length, count, endpoint=False):
        ds = (station-s+length/2) % length-length/2
        selected = np.flatnonzero(admitted & (abs(ds) <= window*diameter))
        row = dict(u=float(s/length), station=float(s), local_count=len(selected),
                   observation_numbers=number[selected].tolist(), supported=False)
        if len(selected) < 12:
            row['reason'] = 'Fewer than 12 substantial colored interiors'
        else:
            lo, hi = np.quantile(cross[selected], [quantile, 1-quantile])
            low = selected[cross[selected] <= lo]
            high = selected[cross[selected] >= hi]
            row.update(cross_limits=[float(lo), float(hi)],
                       low_numbers=number[low].tolist(), high_numbers=number[high].tolist())
            if min(len(low), len(high)) < 2 or hi-lo < diameter:
                row['reason'] = 'Opposite-side coverage insufficient'
            else:
                j = int(round(s)) % length
                center = axis['xy'][j]
                normal = axis['normal'][j]
                row.update(supported=True,
                           low_xy=(center+lo*normal).tolist(),
                           high_xy=(center+hi*normal).tolist(), normal=normal.tolist(),
                           # Overlapping windows are correlated, not independent errors.
                           weight=float(min(1., len(selected)/24)))
        records.append(row)
    return records, number[admitted].tolist(), number[~admitted].tolist()


def fit_pairs(records, harmonics=24, cutoff=12.):
    """Shared periodic middle and varying half-span, with robust side residuals.

    Half-span describes the colored *interior distribution*, not tube radius.
    Its low-frequency variation is a nuisance quantity, not a width measurement.
    """
    rows = [r for r in records if r['supported']]
    if len(rows) < 24:
        raise ValueError('Insufficient paired support for a periodic candidate')
    u = np.array([r['u'] for r in rows])
    basis = fourier(u, harmonics)
    width_basis = fourier(u, 4)
    normals = np.array([r['normal'] for r in rows])
    low = np.array([r['low_xy'] for r in rows])
    high = np.array([r['high_xy'] for r in rows])
    p = basis.shape[1]
    w = width_basis.shape[1]
    # C(u) +/- W(u)*n(u): two-dimensional paired support, no reference-curve term.
    matrix = np.zeros((len(rows)*4, p*2+w))
    target = np.empty(len(rows)*4)
    for i in range(len(rows)):
        for side, xy in enumerate([low[i], high[i]]):
            sign = -1 if side == 0 else 1
            for dimension in range(2):
                row = 4*i+2*side+dimension
                matrix[row, dimension*p:(dimension+1)*p] = basis[i]
                matrix[row, 2*p:] = sign*normals[i, dimension]*width_basis[i]
                target[row] = xy[dimension]
    frequency = np.repeat(np.arange(1, harmonics+1), 2)
    penalty = np.r_[0., np.where(frequency <= 2, 0., (frequency/cutoff)**2)]
    penalty *= np.sqrt(len(rows))
    width_penalty = np.r_[0., np.repeat(np.arange(1, 5), 2)**2/8] * np.sqrt(len(rows))
    regularizer = np.diag(np.r_[penalty, penalty, width_penalty])
    base_weight = np.repeat(np.sqrt([r['weight'] for r in rows]), 4)
    robust = np.ones(len(rows))
    for _ in range(8):
        weight = base_weight*np.repeat(np.sqrt(robust), 4)
        coef = np.linalg.lstsq(np.vstack([matrix*weight[:, None], regularizer]),
                               np.r_[target*weight, np.zeros(len(regularizer))], rcond=None)[0]
        residual = (matrix@coef-target).reshape(-1, 4)
        error = np.sqrt(np.mean(residual**2, axis=1))
        median = np.median(error)
        scale = max(.75, 1.4826*np.median(abs(error-median)))
        robust = np.minimum(1., 2.5*scale/np.maximum(error, 1e-8))
    sample_u = np.linspace(0, 1, 513)
    sample_basis = fourier(sample_u, harmonics)
    curve = np.column_stack([sample_basis@coef[:p], sample_basis@coef[p:2*p]])
    halfspan = fourier(sample_u, 4)@coef[2*p:]
    if np.any(halfspan <= 0):
        raise ValueError('Fitted colored half-span is nonpositive; retain failure')
    # Validate the generated closed route rather than trusting smoothness.
    delta = np.diff(curve, axis=0)
    if np.any(np.linalg.norm(delta, axis=1) < 1e-6):
        raise ValueError('Degenerate candidate route')
    for a in range(len(delta)):
        b = np.arange(a+2, len(delta))
        if a == 0:
            b = b[b != len(delta)-1]
        if not len(b):
            continue
        va = delta[a]
        vb = delta[b]
        cross = va[0]*vb[:, 1]-va[1]*vb[:, 0]
        safe = abs(cross) > 1e-10
        diff = curve[b]-curve[a]
        ta = np.divide(diff[:, 0]*vb[:, 1]-diff[:, 1]*vb[:, 0], cross,
                       out=np.zeros(len(b)), where=safe)
        tb = np.divide(diff[:, 0]*va[1]-diff[:, 1]*va[0], cross,
                       out=np.zeros(len(b)), where=safe)
        if np.any(safe & (ta >= -1e-9) & (ta <= 1+1e-9)
                  & (tb >= -1e-9) & (tb <= 1+1e-9)):
            raise ValueError('Self-intersecting candidate route')
        collinear = (~safe) & (abs(va[0]*diff[:, 1]-va[1]*diff[:, 0]) < 1e-9)
        projection = diff@va/np.dot(va, va)
        endpoint = (diff+vb)@va/np.dot(va, va)
        if np.any(collinear & (np.maximum(projection, endpoint) >= -1e-9)
                  & (np.minimum(projection, endpoint) <= 1+1e-9)):
            raise ValueError('Self-intersecting candidate route')
    return dict(points=curve.tolist(), u=sample_u.tolist(),
                colored_halfspan=halfspan.tolist(), cutoff=cutoff, harmonics=harmonics,
                paired_residual_rms=float(np.sqrt(np.mean(residual**2))),
                paired_robust_weights=robust.tolist(), coefficients=coef.tolist())


def nearest_distances(curve, targets):
    """Exact distances to a dense polyline, not to its discrete sample points."""
    curve = np.asarray(curve)
    targets = np.asarray(targets)
    start = curve[:-1]
    vector = np.diff(curve, axis=0)
    offset = targets[:, None, :]-start
    fraction = np.clip(np.sum(offset*vector, axis=2)/np.sum(vector**2, axis=1), 0, 1)
    projected = start+fraction[:, :, None]*vector
    distances = np.linalg.norm(projected-targets[:, None, :], axis=2)
    which = np.argmin(distances, axis=1)
    return distances[np.arange(len(targets)), which]


def from_detection(result, excluded=(), window=6., cutoff=32.):
    # Stations/normals are supplied by the image, not by the historical curve.
    points, _ = colored_subset(result, auto.adjacency(result))
    rows, admitted, rejected = local_pairs(points, result['axis'], result['diameter'],
                                          excluded, window=window)
    harmonics = min(48, max(4, (sum(r['supported'] for r in rows)-1)//2-2))
    fit = fit_pairs(rows, harmonics=harmonics, cutoff=cutoff)
    scale = np.asarray(result['scale'])
    fit['source_points'] = (np.array(fit['points'])/scale).tolist()
    for row in rows:
        for name in ['low_xy', 'high_xy']:
            if name in row:
                row['source_'+name] = (np.array(row[name])/scale).tolist()
    fit.update(local_pairs=rows, admitted_observations=admitted,
               rejected_observations=rejected, excluded_observations=list(excluded),
               window_diameters=window, diameter=result['diameter'],
               role='Provisional colored-interior tube middle; not a measured physical centerline or recovered lattice.')
    return fit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', type=Path, default=auto.ROOT/'beads-photo-2.jpg')
    parser.add_argument('--output', type=Path, default=auto.ROOT/'photo2/output/r190')
    parser.add_argument('--exclude', type=int, nargs='*', default=[],
                        help='Explicit assisted review exclusions in the colored observation namespace')
    args = parser.parse_args()
    if (args.output/'report.json').exists():
        parser.error('Existing report is protected; use a fresh output directory')
    args.output.mkdir(parents=True, exist_ok=True)
    from PIL import Image, ImageOps
    image = ImageOps.exif_transpose(Image.open(args.image)).convert('RGB')
    result = auto.detect(np.array(image))
    variants = []
    for window, cutoff in [(6., 32.), (4., 32.), (8., 32.), (6., 24.), (6., 48.)]:
        fit = from_detection(result, args.exclude, window=window, cutoff=cutoff)
        name = f'window{window:g}-cutoff{cutoff:g}'
        atomic_json(args.output/(name+'.json'), fit)
        variants.append(dict(name=name, file=name+'.json', sha256=auto.sha(args.output/(name+'.json')),
                             supported=sum(r['supported'] for r in fit['local_pairs']),
                             total=len(fit['local_pairs']), residual=fit['paired_residual_rms']))
        print(name, variants[-1], flush=True)
    # Capture pure input-only alternative when a review exclusion was supplied.
    if args.exclude:
        automatic = from_detection(result)
        atomic_json(args.output/'automatic.json', automatic)
    primary = json.loads((args.output/variants[0]['file']).read_text())
    seed = dict(points=primary['source_points'], smoothing_rms_target_pixels=0.,
                request='R190', status='Candidate only; not adopted by viewer',
                method='Robust paired colored-interior periodic tube fit',
                assisted_exclusions=args.exclude, image_sha256=auto.sha(args.image))
    atomic_json(args.output/'candidate-spline.json', seed)
    atomic_json(args.output/'report.json', dict(request='R190', variants=variants,
        image_sha256=auto.sha(args.image), detector_parameters=result['parameters'],
        source_sha256={str(p.relative_to(auto.ROOT)):auto.sha(p) for p in
                       [Path(__file__), auto.ROOT/'photo2/auto_label_beads.py',
                        auto.ROOT/'photo2/colored_centerline_evidence.py']},
        maker_input_role='Only explicit excluded observations; no saved centers/old curve/held body labels used.',
        limitations=['Interior quantiles are not physical edges.',
                     'Colored/palette coverage may be asymmetric.',
                     'Camera/height/width and N/helicity remain unresolved.',
                     'Overlapping local windows do not supply independent statistical confidence.']))


if __name__ == '__main__':
    main()
