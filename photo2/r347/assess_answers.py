"""Validate the maker export and assess its explicit, separately recorded decisions.

No historical graph, colors, roles, sequence, or rendering is rewritten.
Run: python3 -m photo2.r347.assess_answers
"""
from collections import Counter, defaultdict
from pathlib import Path
import gzip
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = HERE / 'answers'
SOURCE = Path('/mnt/c/Users/rharr/Downloads/beads-pattern-answers.json')
RAW = OUT / 'maker-2026-10-20.json'
EXCLUDED = 'R332-R-0037-0040'
CORRECTED = ['REC266-P035619', 'R332-R-0197-0183']


def read(path):
    with gzip.open(path, 'rt') if str(path).endswith('.gz') else Path(path).open() as f:
        return json.load(f)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    OUT.mkdir(exist_ok=True)
    # Never replace an archived export with a later download under the same name.
    raw = RAW.read_bytes() if RAW.exists() else SOURCE.read_bytes()
    data = json.loads(raw)
    seal = read(HERE / 'input-seal.json')
    head = read(HERE / 'conditional-proof.json')['baseline_commit']
    assert data['schema'] == 1
    assert data['baseline_commit'] == head
    assert data['input_sha256'] == seal
    assert data['photo_sha256'] == seal['beads-photo-2.jpg']
    assert all(digest(ROOT / p) == h for p, h in seal.items())
    questions = read(HERE / 'review/questions.json')
    manifest = [dict(number=q['number'], id=q['id'], position=q['position'],
                     xy=q['target']['xy']) for q in questions]
    assert data['question_manifest'] == manifest
    answers = data['answers']
    assert set(answers) == {EXCLUDED, *CORRECTED}
    assert all(a['identity'] == 'distinct' and a['pigment'] == 'yellow'
               for a in answers.values())
    assert answers[EXCLUDED]['basis'] == 'other'
    assert 'reconstructed picture' in answers[EXCLUDED]['note']
    assert 'ignore it altogether' in answers[EXCLUDED]['note']
    assert all(answers[o]['basis'] == 'current_photo' for o in CORRECTED)
    assert data['independent'] == {'evidence': 'both_pending'}
    if not RAW.exists():
        RAW.write_bytes(raw)

    graph = read(ROOT / 'photo2/r344/graph.json.gz')
    obs = {o['id']: o for o in graph['observations']}
    coords = {o['id']: o['ab'] for o in graph['coordinates']}
    blocks = read(ROOT / 'photo2/r344/evaluation.json')['geographic_blocks']
    pattern = read(ROOT / 'photo2/r344/pattern208.json')

    def evaluate(exclude, correct):
        ids = sorted(set(coords) - ({EXCLUDED} if exclude else set()))
        colors = {o: 'yellow' if correct and o in CORRECTED else obs[o]['color'] for o in ids}
        entries = []
        for r in range(208):
            names = [o for o in ids if (7*coords[o][0] + 6*coords[o][1]) % 208 == r]
            counts = Counter(colors[o] for o in names)
            regions = sorted({blocks[o] for o in names})
            status = ('conflicting' if len(counts) > 1 else 'supported'
                      if len(names) >= 3 and len(regions) >= 3 else 'insufficient')
            entries.append(dict(position=r, status=status, counts=dict(counts),
                                geographic_blocks=regions, ids=names))
        trials = []
        for family, total, weights in [('A', 2704, (7, 6)), ('B', 2691, (6, 7))]:
            for period in range(1, 400):
                if total % period:
                    continue
                bins = defaultdict(dict)
                for o in ids:
                    a, b = coords[o]
                    residue = ((weights[0]*a + weights[1]*b) % total) % period
                    bins[residue].setdefault(colors[o], o)
                conflicts = [r for r in sorted(bins) if len(bins[r]) > 1]
                witness = None
                if conflicts:
                    r = conflicts[0]
                    pair = list(sorted(bins[r].items()))[:2]
                    witness = dict(residue=r, ids=[o for _, o in pair],
                                   colors=[c for c, _ in pair])
                trials.append(dict(family=family, count=total, period=period,
                                   compatible=not conflicts, observed_residues=len(bins),
                                   conflicting_residues=len(conflicts), witness=witness))
        mismatches = [o for o in ids if colors[o][0].upper() != pattern['provisional_sequence'][
            (7*coords[o][0] + 6*coords[o][1]) % 208]]
        return dict(indexed_color_observations=len(ids),
                    status_counts=dict(Counter(e['status'] for e in entries)),
                    candidate_agreements=len(ids)-len(mismatches), mismatching_ids=mismatches,
                    compatible_periods=[dict(family=t['family'], count=t['count'], period=t['period'])
                                        for t in trials if t['compatible']],
                    entries=entries, trials=trials)

    epochs = {name: evaluate(exclude, correct) for name, exclude, correct in [
        ('historical_R344', False, False), ('exclude_Q1_only', True, False),
        ('correct_Q2_Q3_only', False, True), ('maker_assessment', True, True)]}
    final = epochs['maker_assessment']
    assert final['status_counts'] == {'supported': 201, 'insufficient': 7}
    assert final['candidate_agreements'] == final['indexed_color_observations'] == 1040
    assert final['compatible_periods'] == [dict(family='A', count=2704, period=208)]
    assert all(not e['compatible_periods'] for name, e in epochs.items() if name != 'maker_assessment')
    result = dict(schema=1, baseline_commit=head, input_sha256=seal,
                  export_sha256=hashlib.sha256(raw).hexdigest(), source_path=str(SOURCE),
                  exported_at=data['exported_at'],
                  policy='Q1 pigment is withheld at maker request: reconstructed-image reliance and insufficient photographic evidence. Its identity, coordinates and links remain historical inputs. Q2/Q3 yellow are maker judgments from the original photo, not independent object or chart observations.',
                  excluded_from_color_evidence=[EXCLUDED], maker_photo_yellow_corrections=CORRECTED,
                  unanswered_questions=[q['number'] for q in questions if q['id'] not in answers],
                  independent_evidence=data['independent'], epochs=epochs,
                  unchanged_historical_inputs=True,
                  conclusion='Unique compatible A/208 within the fixed saved lattice, closure, complete-repeat and period<400 premises. All 208 residues observed. Not unconditional physical or original-chart proof; seven residues retain limited geographic support.')
    assert all(digest(ROOT / p) == h for p, h in seal.items())
    (OUT / 'assessment.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({name: {k: v for k, v in e.items() if k not in ['entries', 'trials']}
                      for name, e in epochs.items()}, indent=2))


if __name__ == '__main__':
    main()
