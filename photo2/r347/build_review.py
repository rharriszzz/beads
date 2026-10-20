"""Build a read-only evidence form and finite conditional period certificate."""
from pathlib import Path
from collections import defaultdict
from itertools import combinations
import gzip
import hashlib
import json

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = HERE / 'review'
BASE = ROOT / 'photo2/r344'
BASELINE_COMMIT = '8e9648b9c9e1379fc66f256bddae0851f1bef39f'
MISMATCHES = ['R332-R-0037-0040', 'REC266-P035619', 'R332-R-0197-0183']
BLACK_CHECKS = [
    (43, 'K-1171-1518'), (75, 'K-1069-1565'), (82, 'K-1037-1557'),
    (89, 'D40-K-1014-1544'), (140, 'K-1543-1467'),
    (147, 'K-0824-1612'), (186, 'D40-K-1384-1467'),
]


def read(path):
    path = Path(path)
    with gzip.open(path, 'rt') if path.suffix == '.gz' else path.open() as stream:
        return json.load(stream)


def save(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, allow_nan=False) + '\n')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    files = [ROOT/'beads-photo-2.jpg', BASE/'graph.json.gz', BASE/'pattern208.json',
             BASE/'corrections.json', BASE/'evaluation.json']
    seal = {str(p.relative_to(ROOT)): sha(p) for p in files}
    graph = read(BASE/'graph.json.gz')
    pattern = read(BASE/'pattern208.json')
    evaluation = read(BASE/'evaluation.json')
    ledger = read(BASE/'corrections.json')['authoritative_labels']
    observations = {r['id']: r for r in graph['observations']}
    coordinates = {r['id']: r['ab'] for r in graph['coordinates']}
    strong = {e['residue'] for e in pattern['entries'] if e['status'] == 'strong'}

    def authority(o):
        if o not in ledger:
            return 'native/software interpretation'
        if 'accepted' in ledger[o]['source']:
            return 'earlier approval of a displayed illustration'
        return 'explicit individual maker pigment'

    def record(o):
        ab = coordinates.get(o)
        k = (7*ab[0]+6*ab[1]) % 2704 if ab else None
        return dict(id=o, xy=observations[o]['xy'], color=observations[o]['color'],
                    ab=ab, index_A=k, position=k % 208 if k is not None else None,
                    occurrence=k//208 if k is not None else None,
                    region=evaluation['geographic_blocks'].get(o),
                    authority=authority(o), authority_source=ledger.get(o, {}).get('source'))

    def scan(hypothetical=False):
        trials = []
        rank = {'explicit individual maker pigment': 0,
                'earlier approval of a displayed illustration': 1,
                'native/software interpretation': 2}
        for family, total, weights in [('A', 2704, (7, 6)), ('B', 2691, (6, 7))]:
            for length in range(1, 400):
                if total % length:
                    continue
                bins = defaultdict(lambda: defaultdict(list))
                for o in sorted(coordinates):
                    a, b = coordinates[o]
                    k = (weights[0]*a + weights[1]*b) % total
                    color = 'yellow' if hypothetical and o in MISMATCHES else observations[o]['color']
                    bins[k % length][color].append(o)
                conflicts = [r for r, values in bins.items() if len(values) > 1]
                candidates = []
                for residue in conflicts:
                    for c1, c2 in combinations(sorted(bins[residue]), 2):
                        for o1 in bins[residue][c1]:
                            for o2 in bins[residue][c2]:
                                # Prefer witnesses independent of the three pending answers.
                                score = (int(o1 in MISMATCHES) + int(o2 in MISMATCHES),
                                         rank[authority(o1)] + rank[authority(o2)],
                                         int(record(o1)['position'] not in strong) +
                                         int(record(o2)['position'] not in strong), o1, o2)
                                candidates.append((score, residue, o1, o2, c1, c2))
                witness = None
                if candidates:
                    _, residue, o1, o2, c1, c2 = min(candidates)
                    witness = dict(residue=residue, observations=[record(o1), record(o2)],
                                   colors_in_this_hypothesis=[c1, c2])
                trials.append(dict(family=family, conditional_count=total, period=length,
                                   compatible=not conflicts, conflicting_residues=len(conflicts),
                                   observed_residues=len(bins), witness=witness))
        return trials

    recorded = scan()
    hypothetical = scan(True)
    assert not any(r['compatible'] for r in recorded)
    compatible = [r for r in hypothetical if r['compatible']]
    assert [(r['family'], r['period']) for r in compatible] == [('A', 208)]
    assert compatible[0]['observed_residues'] == 208
    word = pattern['provisional_sequence']
    primitive_witnesses = []
    for d in range(1, 208):
        if 208 % d:
            continue
        i, j = next((i, j) for i in range(208) for j in range(i+1, 208)
                    if i % d == j % d and i in strong and j in strong and word[i] != word[j])
        primitive_witnesses.append(dict(period=d, positions=[i, j], colors=[word[i], word[j]]))
    proof = dict(
        baseline_commit=BASELINE_COMMIT,
        input_sha256=seal,
        claim='Finite uniqueness conditional on the saved lattice/closure, a whole repeated string, period <400, and correct photographic colors.',
        excluded_claim='No proof of the physical lattice, count, unseen beads, or authenticity of a chart follows from this calculation.',
        current_recorded_labels=dict(compatible_periods=[], trials=recorded),
        hypothetical_three_yellows=dict(
            status='Unadopted hypothesis, not new pigment judgments', changed_ids=MISMATCHES,
            compatible_periods=[dict(family=r['family'], count=r['conditional_count'], period=r['period']) for r in compatible],
            uniquely_determined_residues=208, trials=hypothetical),
        candidate_primitive_period=208, strict_proper_divisor_witnesses=primitive_witnesses,
        logical_reason='An exact cyclic repeated block has a shortest period dividing the total count. All divisors 1..399 are enumerated for each of the two fixed family conventions. Two different colors in one residue reject that period. Every residue of the surviving 208 hypothesis is observed.',
    )
    save(HERE/'conditional-proof.json', proof)

    photo = ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB')
    entries = {e['residue']: e for e in pattern['entries']}
    questions = []
    targets = [(None, o) for o in MISMATCHES] + BLACK_CHECKS
    for number, (position, o) in enumerate(targets, 1):
        target = record(o)
        position = target['position'] if position is None else position
        assert position == target['position']
        # Previous approved bodies are references only, never fresh questions.
        assert o not in ledger
        x, y = map(round, target['xy'])
        box = [x-60, y-60, x+61, y+61]
        crop = photo.crop(box)
        filename = f'q{number:02d}-native.png'
        crop.save(OUT/filename, icc_profile=photo.info.get('icc_profile'))
        near = sorted((z for z in observations if z != o and
                       sum((a-b)**2 for a,b in zip(observations[z]['xy'], target['xy'])) < 100**2),
                      key=lambda z: (sum((a-b)**2 for a,b in zip(observations[z]['xy'], target['xy'])), z))
        key = [o] + near
        e = entries[position]
        questions.append(dict(number=number, id=o, stage='contradictions' if number <= 3 else 'completion',
                              position=position, target=target, crop_box=box, filename=filename,
                              key=key, same_position_sources=[record(z) for z in e['ids']],
                              existing_status=e['status']))
    meta = [record(o) for o in observations]
    data = dict(baseline_commit=proof['baseline_commit'], photo_sha256=seal['beads-photo-2.jpg'],
                input_sha256=seal, questions=questions, observations=meta, edges=graph['edges'],
                candidate=word, proof=proof)
    (OUT/'data.js').write_text('const DATA=' + json.dumps(data, separators=(',', ':')) + ';\n')
    save(OUT/'questions.json', questions)
    save(HERE/'input-seal.json', seal)
    # Independent crop decoding checks exact native RGB and retained ICC tag.
    checks = []
    for q in questions:
        with Image.open(OUT/q['filename']) as got:
            expected = photo.crop(q['crop_box'])
            assert got.convert('RGB').tobytes() == expected.tobytes()
            assert got.info.get('icc_profile') == photo.info.get('icc_profile')
        assert q['key'][0] == q['id']
        checks.append(dict(question=q['number'], id=q['id'], native_pixels_exact=True,
                           ICC_preserved=True, target_is_feature_1=True))
    assert seal == {str(p.relative_to(ROOT)): sha(p) for p in files}
    save(HERE/'artifact-checks.json', dict(passed=True, questions=checks,
                                         existing_approved_bodies_requestioned=0,
                                         scientific_inputs_unchanged=True,
                                         proof_periods_tested_per_epoch=len(recorded)))
    print('Built 10 questions; prior approvals retained; 22 divisor cases per proof epoch.')


if __name__ == '__main__':
    main()
