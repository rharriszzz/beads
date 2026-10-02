"""R200: assisted quality/coverage audit of saved maker visible-part centers.

No detection, correspondence, phase/count scan or centerline adjustment. Frozen
image-derived hue modes supply diagnostics; manual marks remain manual inputs.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path

os.environ.setdefault('MPLCONFIGDIR', '/tmp/beads-evidence-mpl')
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
from matplotlib.colors import rgb_to_hsv
from scipy.interpolate import splprep, splev
from scipy.spatial import cKDTree

from bead_evidence_inventory import hue_distance
from center_marks import validate_marks
from label_beads import atomic_json

ROOT = Path(__file__).resolve().parents[1]
# Seals the 41 manually saved positions actually inspected in this review.
# This is a curator constraint, never an image-only detection prior.
REVIEWED_CENTERS_SHA256 = '3d210bea246d9942cdb38e66600d71485561821f80594a3dfbd447ac8256c55d'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def coverage_stations(points, seed):
    """Image-arclength only, on the unchanged approximate seed; no physical fit."""
    curve = np.asarray(seed, float)
    if np.linalg.norm(curve[0]-curve[-1]) < 1e-6:
        curve = curve[:-1]
    if np.sum(curve[:, 0]*np.roll(curve[:, 1], -1)-curve[:, 1]*np.roll(curve[:, 0], -1)) < 0:
        curve = curve[::-1]
    closed = np.vstack([curve, curve[0]])
    tck, _ = splprep(closed.T, s=len(closed)*2**2, per=True, k=3)
    sample = np.array(splev(np.linspace(0, 1, 8193), tck)).T
    arc = np.r_[0, np.cumsum(np.linalg.norm(np.diff(sample, axis=0), axis=1))]
    distances, indices = cKDTree(sample).query(points)
    fractions = arc[indices]/arc[-1]
    order = np.argsort(fractions)
    gaps = np.diff(np.r_[fractions[order], fractions[order[0]]+1])
    bins = np.minimum((fractions*8).astype(int), 7)
    return fractions, distances, order, gaps, np.bincount(bins, minlength=8), sample


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--centers', type=Path, default=ROOT/'photo2/review/r186/centers.json')
    parser.add_argument('--output', type=Path, default=ROOT/'photo2/review/r200')
    args = parser.parse_args()
    previous = json.loads((ROOT/'photo2/review/r196/summary.json').read_text())
    protected = {p: sha(ROOT/p) for p in previous['preserved_inputs']}
    photo = ROOT/'beads-photo-2.jpg'
    image = ImageOps.exif_transpose(Image.open(photo)).convert('RGB')
    if sha(args.centers) != REVIEWED_CENTERS_SHA256:
        raise ValueError('Changed center set needs a new visual audit; existing dispositions cannot transfer')
    document = json.loads(args.centers.read_text())
    if document['source']['sha256'] != sha(photo) or document['source']['oriented_size'] != list(image.size):
        raise ValueError('Saved centers do not belong to this oriented photo')
    points = validate_marks(document['points'], image.size)
    inventory = json.loads((ROOT/'photo2/review/r192/candidates.json').read_text())
    if inventory['image_sha256'] != sha(photo):
        raise ValueError('Frozen appearance diagnostics belong to another photo')
    modes = inventory['parameters']['detector']['hue_modes_degrees']
    xy = np.array([[p['x'], p['y']] for p in points])
    seed_path = ROOT/'photo2/spline-seed-r175.json'
    fractions, distances, order, gaps, bins, curve = coverage_stations(xy, json.loads(seed_path.read_text())['points'])
    hsv = rgb_to_hsv(np.asarray(image, dtype=float)/255)
    candidate_records = inventory['records']
    proposal_distances, proposal_indices = cKDTree([p['seed_xy'] for p in candidate_records]).query(xy)
    records = []
    for i, point in enumerate(points):
        x, y = point['x'], point['y']
        lo = np.maximum(0, np.floor([x-4, y-4])).astype(int)
        hi = np.minimum(image.size, np.ceil([x+5, y+5])).astype(int)
        yy, xx = np.mgrid[lo[1]:hi[1], lo[0]:hi[0]]
        disk = np.hypot(xx-x, yy-y) <= 3
        values = hsv[lo[1]:hi[1], lo[0]:hi[0]][disk]
        # Saturation weights downweight white glints; no fixed color classifier.
        z = np.sum(values[:, 1]*np.exp(2j*np.pi*values[:, 0]))
        angle = float(np.degrees(np.angle(z)) % 360)
        errors = [float(hue_distance(angle, mode)) for mode in modes]
        mode = int(np.argmin(errors))+1
        proposal = candidate_records[proposal_indices[i]]
        records.append(dict(**point, evidence='maker-selected visible-part center',
            appearance_mode=mode, appearance_label={1: 'yellow', 2: 'red'}[mode],
            appearance_label_role='Semantic names from prior maker evidence, after input-derived mode selection',
            audit_status='Suitable assisted starting reference on visual inspection; no new exact surface-anchor measurement',
            diagnostic=dict(sample_radius_pixels=3, sample_pixels=len(values),
                saturation_weighted_hue_degrees=angle, hue_mode_error_degrees=min(errors),
                hue_resultant=float(abs(z)/np.sum(values[:, 1])),
                median_saturation=float(np.median(values[:, 1])), median_value=float(np.median(values[:, 2])),
                hue_within_20_degrees_fraction=float(np.mean(hue_distance(values[:, 0]*360, modes[mode-1]) <= 20))),
            approximate_image_arc_fraction=float(fractions[i]), seed_distance_pixels=float(distances[i]),
            nearest_automatic_proposal=dict(observation_id=proposal['observation_id'],
                observation_number=proposal['observation_number'], seed_xy=proposal['seed_xy'],
                seed_distance_pixels=float(proposal_distances[i]), kind=proposal['kind'],
                status=proposal['status'], appearance_mode=proposal.get('appearance_mode'),
                body_identity='Unresolved association; no merge, correspondence or region promotion'),
            uncertainty='Maker numeric error unspecified; visible-center to outward-point offset unmeasured',
            bead_index=None, correspondence=None))
    maximum = int(np.argmax(gaps))
    endpoint = [points[order[maximum]]['number'], points[order[(maximum+1) % len(points)]]['number']]
    report = dict(request='R200', scope='Sufficient reliable assisted positions, not complete bead inventory',
        coordinate_system='EXIF-oriented original photo pixels; x right, y down',
        methods=['raw center crops', 'local circular hue/S/V', 'frozen proposal context', 'unchanged-seed image-arclength coverage'],
        records=records, counts=dict(total=len(records), red=sum(r['appearance_label']=='red' for r in records),
            yellow=sum(r['appearance_label']=='yellow' for r in records), black=0),
        coverage=dict(image_arc_sectors=8, sector_counts=bins.tolist(), largest_gap_fraction=float(gaps[maximum]),
            largest_gap_endpoint_numbers=endpoint, cyclic_order=[points[i]['number'] for i in order],
            cyclic_gaps=gaps.tolist(), role='Approximate image-arclength coverage, not physical major-axis angle or corrected centerline'),
        position_basis='All saved maker positions retained as an assisted starting set; appearance labels visually audited',
        independent_unique_body_count_certified=False, exact_outward_anchors=False,
        fitting_performed=False, centerline_changed=False,
        limitations=['Three-pixel diagnostic disks are not new maker-confirmed safe regions.',
            'Nearby automatic records are not merged or promoted by proximity.',
            'Coverage alone does not prove count/helicity or stable correspondences.',
            'No black reflections need to be used for this saved colored set.'])
    args.output.mkdir(parents=True, exist_ok=True)
    atomic_json(args.output/'centers.json', document)
    atomic_json(args.output/'position-basis.json', report)
    font = ImageFont.truetype('DejaVuSans.ttf', 16)
    # Each tile has unmarked raw pixels beside a copy with a small center marker.
    for batch in range((len(points)+11)//12):
        group = records[batch*12:(batch+1)*12]
        sheet = Image.new('RGB', (3*360, ((len(group)+2)//3)*215), 'white')
        draw = ImageDraw.Draw(sheet)
        for j, record in enumerate(group):
            x, y = record['x'], record['y']
            box = (round(x)-44, round(y)-44, round(x)+44, round(y)+44)
            crop = image.crop(box).resize((176, 176), Image.Resampling.NEAREST)
            ox, oy = j % 3*360, j//3*215
            sheet.paste(crop, (ox, oy+30)); sheet.paste(crop, (ox+180, oy+30))
            mx, my = ox+180+(x-box[0])*2, oy+30+(y-box[1])*2
            draw.ellipse((mx-3, my-3, mx+3, my+3), outline='cyan', width=1)
            draw.text((ox+4, oy+4), f"{record['number']}: {record['appearance_label']}   raw | saved center", font=font, fill='black')
        sheet.save(args.output/f'centers-{batch+1}.png')
    overview = image.resize((1016, 1273), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(overview)
    scale = np.array(overview.size)/image.size
    for r in records:
        x, y = np.array([r['x'], r['y']])*scale
        draw.ellipse((x-2, y-2, x+2, y+2), outline='cyan', width=1)
        draw.text((x+4, y-8), str(r['number']), fill='cyan', font=font,
                  stroke_width=1, stroke_fill='black')
    overview.save(args.output/'whole-photo.png')
    sources = ['beads-photo-2.jpg', 'photo2/review/r192/candidates.json',
               'photo2/spline-seed-r175.json', 'photo2/audit_saved_centers.py',
               'photo2/position-basis-scope-r199.json']
    after = {p: sha(ROOT/p) for p in protected}
    if protected != after:
        raise ValueError('Protected inputs changed during read-only audit')
    summary = dict(request='R200', source_sha256={p: sha(ROOT/p) for p in sources},
        input_centers_path=str(args.centers.relative_to(ROOT)) if args.centers.is_relative_to(ROOT) else str(args.centers),
        input_centers_sha256=sha(args.centers), preserved_inputs=after,
        live_centers_equal_snapshot=sha(ROOT/'photo2/output/tangent-viewer/centers.json') == sha(args.centers),
        curated_sha256={p.name: sha(p) for p in sorted(args.output.iterdir()) if p.name != 'summary.json'},
        counts=report['counts'], coverage=report['coverage'], fitting_performed=False,
        reproduction='.venv/bin/python photo2/audit_saved_centers.py')
    atomic_json(args.output/'summary.json', summary)
    print(json.dumps(dict(counts=report['counts'], coverage=report['coverage'])))


if __name__ == '__main__':
    main()
