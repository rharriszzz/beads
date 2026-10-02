"""R193: apply exact illustrated answers, then diagnose frozen evidence errors.

This is a curator/evaluator. It does not alter image-only detection, fit any
simulated positions, or turn proximity into confirmed bead ownership.
"""
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import json
import os
from pathlib import Path
import uuid

os.environ.setdefault('MPLCONFIGDIR', '/tmp/beads-evidence-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import rgb_to_hsv
import numpy as np
from PIL import Image, ImageOps
from scipy import ndimage as ndi
from scipy.spatial import cKDTree

import auto_label_beads as auto
from label_beads import atomic_json
from review_bead_evidence import draw, pixels


def confirmed_ledger(data, prior, answer, source_summary):
    """Promote only the pictured regions and locator ownership explicitly answered."""
    rows = {r['observation_number']: r for r in data['records']}
    facts = deepcopy(prior)
    accepted = []
    black = []
    for question, key in [('Q192.1', 'question_colored'), ('Q192.2', 'question_black')]:
        reply = answer['questions'][question]
        if reply['answer'] != 'yes':
            raise ValueError('This curator only applies the supplied affirmative answers')
        targets = source_summary[key]
        if [(r['label'], r['observation_number']) for r in reply['observations']] != [
                (r['label'], r['observation_number']) for r in targets]:
            raise ValueError('Reply does not name the exact pictured observations')
        for target in reply['observations']:
            row = rows[target['observation_number']]
            if target['observation_id'] != row['observation_id'] or row['status'] != 'region-proposal':
                raise ValueError('Reviewed observation changed or has no displayed region')
            expected = 'black' if question == 'Q192.2' else source_summary['color_names'][str(row['appearance_mode'])]
            if target['appearance'] != expected:
                raise ValueError('Appearance differs from the reviewed question')
            if question == 'Q192.2' and not row.get('reflection'):
                raise ValueError('Reviewed black observation has no reflection locator')
            fact = dict(observation_number=row['observation_number'], observation_id=row['observation_id'],
                        appearance=expected, region=deepcopy(row['region']),
                        confirmation=f'Maker yes, R193 / {question}',
                        source=answer['candidate_source'], supporting_image=reply['supporting_image'],
                        supporting_image_sha256=reply['supporting_image_sha256'],
                        limits=reply['limits'])
            facts['region_facts'].append(fact)
            accepted.append(row['observation_number'])
            if question == 'Q192.2':
                black.append(row['observation_number'])
                facts['black_reflection_point_facts'].append(dict(
                    observation_number=row['observation_number'], observation_id=row['observation_id'],
                    xy=row['reflection']['xy'], confirmation=f'Maker locator ownership yes, R193 / {question}',
                    threshold_sensitivity_pixels=row['reflection']['threshold_sensitivity_pixels'],
                    limits='Displayed cross inside this black body; not exact optical peak, center, boundary or outward anchor. Bright threshold pixels remain measured candidate support.'))
    facts['distinct_body_region_groups'] = [dict(
        observations=black, observation_ids=[rows[n]['observation_id'] for n in black],
        confirmation='Q192.2 / R193: three distinct black beads',
        limits='Distinct within this pictured group; no global alias resolution or string indices')]
    facts.update(request='R193', accepted_observations=accepted, complete=False,
                 stage='Eleven maker-confirmed positive regions plus inherited subsets; coverage still unverified')
    return facts


def lookup_owner(labels, point):
    x, y = np.rint(point).astype(int)
    if not (0 <= y < labels.shape[0] and 0 <= x < labels.shape[1]):
        return -1
    return int(labels[y, x])


def reflection_appearance(hsv, reflection, modes, saturation_floor):
    xy = pixels(reflection)
    samples = hsv[xy[:, 1], xy[:, 0]]
    chromatic = samples[:, 1] >= saturation_floor
    family = np.zeros(len(samples), bool)
    for mode in modes:
        family |= abs((samples[:, 0] * 360 - mode + 180) % 360 - 180) <= 20
    return dict(reflection_median_saturation=float(np.median(samples[:, 1])),
                reflection_median_value=float(np.median(samples[:, 2])),
                reflection_learned_color_fraction=float(np.mean(chromatic & family)))


def apply_ownership_answers(facts, data, answer, photo_audit):
    """Keep identity confirmation separate from region and reflection confirmation."""
    facts = deepcopy(facts)
    rows = {r['observation_number']: r for r in data['records']}
    for question, key, expected in [
            ('Q193.1', 'question_colored', 'Two different yellow beads'),
            ('Q193.2', 'question_dark', 'Different black bead')]:
        reply = answer['answers'][question]
        if reply['answer'] != expected:
            raise ValueError('Ownership answer differs from the supplied maker fact')
        points = reply['points']
        if [{k: v for k, v in p.items() if k != 'observation_id'} for p in points] != photo_audit[key]:
            raise ValueError('Ownership reply does not identify the pictured points')
        for point in points:
            if 'observation_number' in point and point['observation_id'] != rows[point['observation_number']]['observation_id']:
                raise ValueError('Ownership reply observation identity changed')
    colored = answer['answers']['Q193.1']
    group = []
    for point in colored['points']:
        fact = dict(observation_number=point['observation_number'], observation_id=point['observation_id'],
                    xy=point['xy'], appearance='yellow', confirmation='R194 / Q193.1: two different yellow beads',
                    limits='Body/point identity only; new loop seam clearance not confirmed')
        facts['other_point_facts'].append(fact)
        group.append(dict(observation_id=fact['observation_id'], observation_number=fact['observation_number']))
    dark = answer['answers']['Q193.2']; d, r = dark['points']
    x, y = d['xy']
    point_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{data['image_sha256']}:maker-dark-point:{x}:{y}"))
    dark_fact = dict(observation_id=point_id, xy=d['xy'], appearance='black',
                     confirmation='R195 / Q193.2: D inside a different black bead from R777',
                     source='photo2/ownership-answers-r194-r195.json',
                     limits='Point/body identity only; no positive region or reflection position established')
    facts['other_point_facts'].append(dark_fact)
    facts['distinct_body_point_groups'] = [
        dict(observations=group, confirmation='R194: two different yellow beads'),
        dict(observations=[dict(observation_id=point_id, xy=d['xy']),
                           dict(observation_id=r['observation_id'], observation_number=r['observation_number'])],
             confirmation='R195: D belongs to a different black bead from the bead at R777')]
    facts['confirmed_coverage_gaps'] = [dict(observation_id=point_id, xy=d['xy'], appearance='black',
        confirmation=dark_fact['confirmation'], region_status='not established', reflection_status='unresolved',
        other_existing_body_aliases='unresolved beyond the confirmed distinction from R777',
        limits='Visible body retained in coverage; do not use R777 reflection or invent pixels/string index')]
    facts.update(ownership_answer_requests=['R194', 'R195'], complete=False,
                 stage='Confirmed positive regions and separate body identities; confirmed black-body point with unresolved reflection/other aliases')
    return facts


def diagnose_records(records, labels, eligible, hsv=None, modes=(), saturation_floor=.2):
    """Truth used only here, after frozen candidate extraction is complete."""
    details = []
    owned = defaultdict(list)
    safe = set()
    seeds = defaultdict(list)
    distances = {}
    for row in records:
        seed_owner = lookup_owner(labels, row['seed_xy'])
        seeds[seed_owner].append(row)
        detail = dict(observation_number=row['observation_number'], seed_xy=row['seed_xy'],
                      source=row['source'], kind=row['kind'], status=row['status'], seed_owner=seed_owner)
        region = row.get('region')
        if region:
            xy = pixels(region)
            ids, counts = np.unique(labels[xy[:, 1], xy[:, 0]], return_counts=True)
            detail['region_owners'] = [{'body': int(i), 'pixels': int(n)} for i, n in zip(ids, counts)]
            single = len(ids) == 1 and ids[0] >= 0
            detail['single_body'] = bool(single)
            if single:
                owner = int(ids[0]); owned[owner].append(row['observation_number'])
                if owner not in distances:
                    distances[owner] = ndi.distance_transform_edt(labels == owner)
                margin = float(distances[owner][xy[:, 1], xy[:, 0]].min())
                correct_kind = (owner % 3 == 2) == (row['kind'] == 'dark-reflection')
                detail.update(owner=owner, true_pixel_margin=margin, appearance_kind_correct=correct_kind)
                if margin >= 3 and correct_kind:
                    safe.add(owner)
        reflection = row.get('reflection')
        if reflection:
            owner = lookup_owner(labels, reflection['xy'])
            detail.update(reflection_xy=reflection['xy'], reflection_owner=owner,
                          reflection_on_black=owner >= 0 and owner % 3 == 2)
            if hsv is not None:
                detail.update(reflection_appearance(hsv, reflection, modes, saturation_floor))
        details.append(detail)
    misses = []
    for owner in eligible:
        if owner in owned:
            continue
        present = seeds[owner]
        if not present:
            reason = 'no accepted seed on visible body'
        elif any(r['status'] == 'region-proposal' for r in present):
            reason = 'seed present; no single-body region'
        elif any(r['status'] in ['unresolved-region', 'reflection-only-proposal'] for r in present):
            reason = 'seed present; region unresolved or reflection-only'
        else:
            reason = 'only seed(s) excluded by provisional edge guard'
        misses.append(dict(body=owner, appearance='black' if owner % 3 == 2 else 'chromatic',
                           reason=reason, observations=[r['observation_number'] for r in present]))
    return dict(observations=details, eligible_bodies=list(eligible), misses=misses,
                miss_reasons=dict(Counter(m['reason'] for m in misses)),
                missed_by_kind=dict(Counter(m['appearance'] for m in misses)),
                duplicate_groups=[dict(body=o, observations=ns) for o, ns in owned.items() if len(ns) > 1],
                eligible_single_body_located=sum(o in owned for o in eligible),
                eligible_correct_kind_with_3px_pixel_margin=sum(o in safe for o in eligible),
                scope='Evaluator-only rendered body IDs; 3px test concerns recorded native pixel centers, not a certified continuous loop margin.')


def paired_question(image, records, points, destination, title, region_rows=()):
    xy = np.array([p['xy'] for p in points])
    lo = np.maximum(0, xy.min(axis=0) - 50)
    hi = np.minimum(image.size, xy.max(axis=0) + 50)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), layout='constrained')
    crop = [*lo, *hi]
    draw(axes[0], image, records, crop)
    draw(axes[1], image, region_rows, crop, True, False)
    for ax in axes:
        for point in points:
            ax.annotate(point['label'], point['xy'], xytext=np.array(point['xy']) + [12, -20],
                        color='white', fontsize=11, bbox=dict(facecolor='black', alpha=.8, pad=1),
                        arrowprops=dict(arrowstyle='->', color='cyan', lw=.8))
    axes[0].set_title('Raw photo')
    axes[1].set_title(title)
    fig.savefig(destination, dpi=170); plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=auto.ROOT / 'photo2/review/r193')
    args = parser.parse_args(); args.output.mkdir(parents=True, exist_ok=True)
    base = auto.ROOT / 'photo2/review/r192'
    answer_path = auto.ROOT / 'photo2/interiors-confirmed-r193.json'
    answer = json.loads(answer_path.read_text())
    source_summary = json.loads((base / 'summary.json').read_text())
    protected = {p: auto.sha(auto.ROOT / p) for p in source_summary['preserved_inputs']}
    candidate_path = auto.ROOT / answer['candidate_source']
    if auto.sha(candidate_path) != answer['candidate_sha256']:
        raise ValueError('Reviewed candidate pixels changed')
    for reply in answer['questions'].values():
        if auto.sha(auto.ROOT / reply['supporting_image']) != reply['supporting_image_sha256']:
            raise ValueError('Reviewed question image changed')
    if auto.sha(auto.ROOT / 'beads-photo-2.jpg') != answer['image_sha256']:
        raise ValueError('Reviewed source photo changed')
    data = json.loads(candidate_path.read_text())
    prior = json.loads((base / 'trusted-facts.json').read_text())
    facts = confirmed_ledger(data, prior, answer, source_summary)

    # No new extractor decisions. Frozen image-only fixture inventories precede
    # all ownership evaluation; none of these labels are detector inputs.
    diagnostics = []
    fixture_dir = auto.ROOT / 'photo2/output/r167/calibration'
    inventory_dir = auto.ROOT / 'photo2/output/r192/conservative/calibration'
    fixture_source_hashes = {}
    for check in source_summary['calibration']:
        name = check['fixture']; frozen = inventory_dir / (name + '.json')
        appearance = fixture_dir / (name + '.png'); ids = fixture_dir / (name + '-ids.png')
        if auto.sha(appearance) != check['appearance_sha256'] or auto.sha(ids) != check['ids_sha256']:
            raise ValueError('Known ownership fixture changed')
        inventory_data = json.loads(frozen.read_text())
        rgb = np.array(Image.open(ids).convert('RGB')).astype(int)
        labels = rgb[:, :, 0] + 256 * rgb[:, :, 1] - 1
        fixture_rgb = np.array(Image.open(appearance).convert('RGB'))
        detector = auto.detect(fixture_rgb)
        band_distance = ndi.distance_transform_edt(detector['band'])
        eligible = []
        for owner in np.unique(labels):
            if owner < 0:
                continue
            inset = ndi.distance_transform_edt(labels == owner) >= 3
            if inset.sum() >= 12 and np.max(band_distance[inset], initial=0) >= detector['diameter'] * .7:
                eligible.append(int(owner))
        diagnostic = diagnose_records(inventory_data['records'], labels, eligible,
            rgb_to_hsv(fixture_rgb / 255.), inventory_data['parameters']['detector']['hue_modes_degrees'],
            inventory_data['parameters']['detector']['saturation_floor'])
        if diagnostic['eligible_single_body_located'] != check['eligible_located'] or len(eligible) != check['eligible_body_count']:
            raise ValueError('Frozen audit no longer agrees with its recorded ownership baseline')
        diagnostic['fixture'] = name
        diagnostics.append(diagnostic)
        for path in [frozen, appearance, ids]:
            fixture_source_hashes[str(path.relative_to(auto.ROOT))] = auto.sha(path)
    atomic_json(args.output / 'ownership-audit.json', diagnostics)

    image = ImageOps.exif_transpose(Image.open(auto.ROOT / 'beads-photo-2.jpg')).convert('RGB')
    rows = data['records']; diameter = data['parameters']['native_diameter']
    # Flag close same-color pairs but preserve identities until illustrated review.
    colored = [r for r in rows if r['status'] == 'region-proposal' and r['kind'] == 'chromatic']
    xy = np.array([r['seed_xy'] for r in colored]); tree = cKDTree(xy)
    native_rgb = np.asarray(image, float) / 255
    native_hsv = rgb_to_hsv(native_rgb)
    modes = data['parameters']['detector']['hue_modes_degrees']
    saturation_floor = data['parameters']['detector']['saturation_floor']
    reflection_checks = [dict(observation_number=r['observation_number'],
        **reflection_appearance(native_hsv, r['reflection'], modes, saturation_floor))
        for r in rows if r.get('reflection')]
    pairs = []
    for i, j in tree.query_pairs(diameter * .8):
        a, b = colored[i], colored[j]
        if a['appearance_mode'] != b['appearance_mode']:
            continue
        mode = data['parameters']['detector']['hue_modes_degrees'][a['appearance_mode'] - 1]
        ratio, coherence = auto.line_evidence(native_rgb, xy[i], xy[j], mode)
        pairs.append(dict(observations=[a['observation_number'], b['observation_number']],
                          distance_pixels=float(np.linalg.norm(xy[i] - xy[j])),
                          value_bridge_ratio=ratio, hue_coherence=coherence,
                          role='Close same-color observations; not an automatic duplicate assignment'))
    pairs.sort(key=lambda p: (p['distance_pixels'], p['observations']))
    pair = pairs[0]; by_number = {r['observation_number']: r for r in rows}
    pair_rows = [by_number[n] for n in pair['observations']]
    pair_points = [dict(label=label, xy=r['seed_xy'], observation_number=r['observation_number'])
                   for label, r in zip('AB', pair_rows)]
    paired_question(image, rows, pair_points, args.output / 'close-colored-question.png',
                    'Two small patches; same bead or adjacent beads?', pair_rows)

    # First native unassociated dark area is a coverage question, not a new body.
    dark = data['unmatched_dark_areas'][0]
    black_rows = [r for r in rows if r.get('reflection')]
    nearby = min(black_rows, key=lambda r: np.linalg.norm(np.array(r['reflection']['xy']) - dark['xy']))
    dark_points = [dict(label='D', xy=dark['xy'], role='Unassociated dark area'),
                   dict(label='R', xy=nearby['reflection']['xy'], observation_number=nearby['observation_number'])]
    paired_question(image, rows, dark_points, args.output / 'dark-area-question.png',
                    'D: dark-area audit; R: nearest proposed reflection', [nearby])
    photo_audit = dict(close_same_color_pairs=pairs,
        question_colored=pair_points, question_dark=dark_points,
        reflection_appearance_checks=reflection_checks,
        unassociated_dark_count=len(data['unmatched_dark_areas']),
        limits='No photo aliases, new body identities or regions are inferred from these diagnostics')
    atomic_json(args.output / 'photo-audit.json', photo_audit)
    ownership_path = auto.ROOT / 'photo2/ownership-answers-r194-r195.json'
    ownership = json.loads(ownership_path.read_text())
    bound_sources = {ownership['question_source']: ownership['question_source_sha256'],
                     ownership['candidate_source']: ownership['candidate_sha256']}
    for reply in ownership['answers'].values():
        bound_sources[reply['supporting_image']] = reply['supporting_image_sha256']
    if ownership['image_sha256'] != data['image_sha256'] or any(
            auto.sha(auto.ROOT / path) != digest for path, digest in bound_sources.items()):
        raise ValueError('Ownership answer supporting data changed')
    facts = apply_ownership_answers(facts, data, ownership, photo_audit)
    atomic_json(args.output / 'trusted-facts.json', facts)

    # Illustrate one known wrong black association and one cross-body patch.
    first = diagnostics[0]; fixture = first['fixture']
    frozen_rows = json.loads((inventory_dir / (fixture + '.json')).read_text())['records']
    by_fixture_number = {r['observation_number']: r for r in frozen_rows}
    wrong = next(r for r in first['observations'] if r.get('reflection_on_black') is False)
    mixed = next(r for r in first['observations'] if r.get('single_body') is False)
    fixture_image = Image.open(fixture_dir / (fixture + '.png')).convert('RGB')
    selected = [by_fixture_number[r['observation_number']] for r in [wrong, mixed]]
    fig, axes = plt.subplots(2, 2, figsize=(10, 8), layout='constrained')
    for axes_row, row, label in zip(axes, selected, ['Colored fragment proposed as black reflection', 'Small patch crosses body ownership']):
        center = np.array((row.get('reflection') or {}).get('xy', row['seed_xy']))
        lo = center - 35; hi = center + 35; crop = [*lo, *hi]
        draw(axes_row[0], fixture_image, frozen_rows, crop)
        draw(axes_row[1], fixture_image, [row], crop, True, False)
        axes_row[0].set_title('Known render: raw')
        axes_row[1].set_title(label)
    fig.savefig(args.output / 'known-failures.png', dpi=150); plt.close(fig)

    source_paths = [candidate_path, base / 'trusted-facts.json', base / 'summary.json', answer_path, ownership_path,
                    auto.ROOT / 'photo2/audit_bead_evidence.py', auto.ROOT / 'photo2/auto_label_beads.py',
                    auto.ROOT / 'photo2/test_bead_evidence_audit.py',
                    auto.ROOT / 'photo2/review_bead_evidence.py', auto.ROOT / 'beads-photo-2.jpg']
    if any(auto.sha(auto.ROOT / p) != digest for p, digest in protected.items()):
        raise ValueError('A preserved input changed during this read-only audit')
    atomic_json(args.output / 'summary.json', dict(request='R193',
        accepted_observations=facts['accepted_observations'], trusted_region_records=len(facts['region_facts']),
        inherited_subsets=len(facts['derived_confirmed_subsets']),
        trusted_black_locator_records=len(facts['black_reflection_point_facts']),
        ownership_answer_requests=facts['ownership_answer_requests'],
        confirmed_coverage_gaps=facts['confirmed_coverage_gaps'],
        calibration=[dict(fixture=d['fixture'], eligible=len(d['eligible_bodies']),
                          located=d['eligible_single_body_located'], safe_typed=d['eligible_correct_kind_with_3px_pixel_margin'],
                          miss_reasons=d['miss_reasons'], missed_by_kind=d['missed_by_kind']) for d in diagnostics],
        sources={str(p.relative_to(auto.ROOT)): auto.sha(p) for p in source_paths},
        fixture_sources=fixture_source_hashes,
        preserved_inputs=protected,
        curated_sha256={p.name: auto.sha(p) for p in args.output.iterdir() if p.name != 'summary.json'},
        coverage_complete=False, fitting_performed=False))
    print(json.dumps(dict(trusted_regions=len(facts['region_facts']),
                         calibration=[{k:d[k] for k in ['fixture', 'miss_reasons', 'missed_by_kind',
                            'eligible_correct_kind_with_3px_pixel_margin']} for d in diagnostics],
                         photo_pair=pair, dark_question=dark_points), indent=2))


if __name__ == '__main__':
    main()
