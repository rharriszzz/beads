"""Curated distributed colored-patch review; truth/maker marks evaluator-only."""
import argparse
from collections import Counter
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR', '/tmp/beads-auto-mpl')

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
from scipy import ndimage as ndi
from scipy.spatial import cKDTree

import auto_label_beads as auto
from distributed_colored_interiors import detect_distributed_interiors
from colored_bead_centers import detect_colored_centers
from label_beads import atomic_json

ROOT = auto.ROOT


def patch_pixels(row):
    return np.array([(x, y) for y, lo, hi in row['region']['pixel_runs'] for x in range(lo, hi+1)])


def evaluate_known(data, labels):
    selected = [r for r in data['records'] if r['selected']]
    rows = []
    owners = []
    for r in selected:
        xy = patch_pixels(r)
        bodies, counts = np.unique(labels[xy[:, 1], xy[:, 0]], return_counts=True)
        single = len(bodies) == 1 and bodies[0] >= 0
        owner = int(bodies[0]) if single else None
        details = dict(observation_number=r['observation_number'], single_body=bool(single),
            pixel_owners=[dict(body=int(i), pixels=int(n)) for i, n in zip(bodies, counts)], owner=owner)
        if single:
            owners.append(owner)
            body = labels == owner
            distance = ndi.distance_transform_edt(body)
            coordinates = np.argwhere(body)[:, ::-1]
            visible_centroid = coordinates.mean(axis=0)
            details.update(true_minimum_pixel_margin=float(distance[xy[:, 1], xy[:, 0]].min()),
                visible_centroid_xy=visible_centroid.tolist(),
                patch_centroid_offset_from_visible_center=float(np.linalg.norm(visible_centroid-r['source_xy'])),
                on_black=owner % 3 == 2)
        rows.append(details)
    owned = Counter(owners)
    offsets = [r['patch_centroid_offset_from_visible_center'] for r in rows if r['single_body']]
    return dict(selected=len(rows), single_body=sum(r['single_body'] for r in rows),
        mixed_or_background=[r['observation_number'] for r in rows if not r['single_body']],
        on_black=[r['observation_number'] for r in rows if r.get('on_black')],
        duplicate_bodies={str(k): v for k, v in owned.items() if v > 1},
        minimum_true_pixel_margin=min([r['true_minimum_pixel_margin'] for r in rows if r['single_body']], default=None),
        patch_to_visible_centroid_offset_quantiles=np.quantile(offsets, [.5, .9, 1]).tolist() if offsets else None,
        details=rows, limitation='Known synthetic ownership only; interior centroids are not visible centers. No photo identity certification.')


def illustrations(image, data, output):
    selected = sorted((r for r in data['records'] if r['selected']), key=lambda r: r['route_fraction'])
    font = ImageFont.truetype('DejaVuSans.ttf', 16)
    pages = []
    for batch in range((len(selected)+19)//20):
        group = selected[batch*20:(batch+1)*20]
        sheet = Image.new('RGB', (4*320, ((len(group)+3)//4)*180), 'white')
        draw = ImageDraw.Draw(sheet)
        for j, row in enumerate(group):
            x, y = row['source_xy']
            box = [round(x)-38, round(y)-38, round(x)+38, round(y)+38]
            crop = image.crop(box).resize((152, 152), Image.Resampling.NEAREST)
            ox, oy = j % 4*320, j//4*180
            sheet.paste(crop, (ox, oy+25)); sheet.paste(crop, (ox+158, oy+25))
            loop = [(ox+158+(a-box[0])*2, oy+25+(b-box[1])*2) for a, b in row['region']['loop_xy']]
            draw.line(loop, fill='lime', width=1)
            draw.text((ox+4, oy+3), f"A{row['observation_number']}   raw | interior", fill='black', font=font)
        name = f'interiors-{batch+1:02d}.png'
        sheet.save(output/name); pages.append(dict(image=name, observations=[r['observation_number'] for r in group]))
    # Full-resolution overlay for zooming; photograph pixels remain unaltered.
    overview = image.copy()
    draw = ImageDraw.Draw(overview)
    for row in selected:
        draw.line([tuple(p) for p in row['region']['loop_xy']], fill='lime', width=1)
    overview.save(output/'whole-photo.png')
    pages.append(dict(image='whole-photo.png', observations=[r['observation_number'] for r in selected]))
    return pages


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'photo2/review/r201')
    parser.add_argument('--target', type=int, default=300)
    parser.add_argument('--brightness-quantile', type=float, default=.20)
    parser.add_argument('--spacing-factor', type=float, default=1.25)
    parser.add_argument('--skip-calibration', action='store_true')
    args = parser.parse_args()
    if not 1 <= args.target <= 1000:
        parser.error('Target must be 1–1000')
    args.output.mkdir(parents=True, exist_ok=True)
    protected_paths = json.loads((ROOT/'photo2/review/r200/summary.json').read_text())['preserved_inputs']
    protected = {p: auto.sha(ROOT/p) for p in protected_paths}
    photo = ROOT/'beads-photo-2.jpg'
    image = ImageOps.exif_transpose(Image.open(photo)).convert('RGB')
    data = detect_distributed_interiors(np.array(image), auto.sha(photo), args.target,
        args.brightness_quantile, args.spacing_factor)
    atomic_json(args.output/'interiors.json', data)
    print(json.dumps(dict(stage='photo', supported=sum(r['status']=='supported colored-interior proposal' for r in data['records']),
                         selected=len(data['selected_numbers']), bins=data['selected_per_bin'])), flush=True)
    pending = []
    fixture_dir = ROOT/'photo2/output/r167/calibration'
    if not args.skip_calibration:
        for name in ['hand+1-palette0-shift0', 'hand-1-palette0-shift0', 'hand+1-palette1-shift2']:
            path = fixture_dir/(name+'.png')
            rendered = np.array(Image.open(path).convert('RGB'))
            detected = detect_distributed_interiors(rendered, auto.sha(path), args.target,
                args.brightness_quantile, args.spacing_factor)
            pending.append((name, path, detected))
            routine = ROOT/'photo2/output/r201/calibration'; routine.mkdir(parents=True, exist_ok=True)
            atomic_json(routine/(name+'.json'), detected)
            print(json.dumps(dict(stage='fixture extraction', name=name, selected=len(detected['selected_numbers']))), flush=True)
    # No fixture ownership or saved manual reference is loaded until every
    # image-only extraction/selection is complete. No truth-based tuning here.
    calibration = []
    for name, path, detected in pending:
        ids = fixture_dir/(name+'-ids.png')
        rgb = np.array(Image.open(ids).convert('RGB'), dtype=int)
        labels = rgb[:, :, 0]+256*rgb[:, :, 1]-1
        calibration.append(dict(fixture=name, appearance_sha256=auto.sha(path), ids_sha256=auto.sha(ids),
                                result=evaluate_known(detected, labels)))
    atomic_json(args.output/'calibration.json', calibration)
    maker_path = ROOT/'photo2/review/r200/centers.json'
    maker = json.loads(maker_path.read_text())
    supported = [r for r in data['records'] if r['status']=='supported colored-interior proposal']
    selected = [r for r in supported if r['selected']]
    manual_checks = []
    trees = [cKDTree([r['source_xy'] for r in subset]) for subset in [supported, selected]]
    for point in maker['points']:
        neighbors = []
        for subset, tree in zip([supported, selected], trees):
            distance, i = tree.query([point['x'], point['y']])
            row = subset[i]
            neighbors.append(dict(observation_number=row['observation_number'], distance_pixels=float(distance),
                manual_point_inside_patch=any(y==round(point['y']) and lo<=round(point['x'])<=hi
                    for y, lo, hi in row['region']['pixel_runs']),
                identity='Nearest spatial proposal only; body association unconfirmed'))
        manual_checks.append(dict(maker_center=point['number'], maker_id=point['id'], supported=neighbors[0], selected=neighbors[1]))
    pages = illustrations(image, data, args.output)
    atomic_json(args.output/'pages.json', pages)
    atomic_json(args.output/'maker-reference-check.json', dict(source_sha256=auto.sha(maker_path), comparisons=manual_checks,
        role='Evaluator-only nearest interior distances, not center errors or supplied correspondences'))
    # Preserve the adverse exact-center experiment, not a claimed successful fit.
    first = detect_colored_centers(np.array(image))
    failure = dict(records=len(first['records']), stable=sum(r['status']=='stable colored-center candidate' for r in first['records']),
        bins=first['selected_per_bin'], reasons=dict(Counter(reason for r in first['records'] for reason in r['rejection_reasons'])),
        parameters=first['parameters'], role='Unadopted strict centroid attempt; touching regions/threshold sensitivity prevent a distributed few-hundred set')
    atomic_json(args.output/'center-attempt.json', failure)
    assert protected == {p: auto.sha(ROOT/p) for p in protected}
    sources = ['beads-photo-2.jpg', 'photo2/distributed_colored_interiors.py', 'photo2/colored_bead_centers.py',
        'photo2/review_distributed_interiors.py', 'photo2/bead_evidence_inventory.py', 'photo2/auto_label_beads.py',
        'photo2/review/r200/centers.json', 'photo2/test_colored_positions.py']
    digest = dict(request='R201/R202', source_sha256={p: auto.sha(ROOT/p) for p in sources},
        protected_inputs=protected, selected=len(selected), supported=len(supported), selected_per_bin=data['selected_per_bin'],
        calibration=[dict(fixture=c['fixture'], **{k:v for k,v in c['result'].items() if k!='details'}) for c in calibration],
        curated_sha256={name: auto.sha(args.output/name) for name in sorted(set(
            [p['image'] for p in pages]+['interiors.json', 'calibration.json', 'pages.json',
             'maker-reference-check.json', 'center-attempt.json']))},
        new_trusted_maker_facts=False, fit_performed=False, black_beads_included=False,
        reproduction='.venv/bin/python photo2/review_distributed_interiors.py')
    atomic_json(args.output/'summary.json', digest)
    print(json.dumps({k: v for k, v in digest.items() if k in ['selected', 'supported', 'selected_per_bin', 'calibration']}), flush=True)


if __name__ == '__main__':
    main()
