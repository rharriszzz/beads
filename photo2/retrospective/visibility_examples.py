"""Enumerate Draft 1's ideal visibility examples; no rendering or image inference.

Run .venv/bin/python photo2/retrospective/visibility_examples.py from repo root.
The phase mask models reliable color readings, not measured bead silhouettes.
"""
from collections import Counter
from math import cos, pi
from pathlib import Path
import gzip
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).with_name('visibility-example-checks.json')


def shortest(word):
    return next(d for d in range(1, len(word)+1) if len(word) % d == 0
                and all(word[i] == word[i % d] for i in range(len(word))))


def main():
    front = {r for r in range(13) if cos(4*pi*r/13) > .5}
    rear = {r for r in range(13) if cos(4*pi*r/13) < -.7}
    a = ''.join(('B' if q == 0 else 'Y') if r in rear else 'R'
                for q in range(2) for r in range(13))
    b = list(a)
    b[4], b[17] = b[17], b[4]  # Swap two hidden colors; preserve total counts.
    b = ''.join(b)
    c = a+'R'
    assert a == 'RRRBBRRRRBBRRRRRYYRRRRYYRR'
    assert b == 'RRRBYRRRRBBRRRRRYBRRRRYYRR'
    assert shortest(a) == shortest(b) == 26 and shortest(c) == 27
    assert Counter(a) == Counter(b)
    assert not any(b == word[j:]+word[:j] for word in [a, a[::-1]] for j in range(26))

    def readings(word, copies=13):
        return [dict(copy=q, position=i, phase=(i+q*len(word)) % 13, color=color)
                for q in range(copies) for i, color in enumerate(word)
                if (i+q*len(word)) % 13 in front]

    ra, rb, rc = readings(a), readings(b), readings(c)
    assert ra == rb and {r['color'] for r in ra} == {'R'}
    assert len({r['position'] for r in ra}) == 10
    assert len({r['position'] for r in rc}) == 27
    assert all({(p+q*27) % 13 for q in range(13)} == set(range(13)) for p in range(27))
    assert all(len({(p+q*26) % 13 for q in range(13)}) == 1 for p in range(26))
    assert all(sum(r['position'] == p for r in rc) == 5 for p in range(27))
    paths = [ROOT/'photo2/r344/graph.json.gz', ROOT/'photo2/r347/answers/assessment.json']
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    with gzip.open(paths[0], 'rt') as f:
        graph = json.load(f)
    assessment = json.loads(paths[1].read_text())
    coords = {r['id']: r['ab'] for r in graph['coordinates']}
    retained = sorted(set(coords)-set(assessment['excluded_from_color_evidence']))
    coverage = {p: [] for p in range(208)}
    for o in retained:
        a0, b0 = coords[o]
        k = (7*a0+6*b0) % 2704
        coverage[k % 208].append(dict(id=o, occurrence=k//208))
    assert len(retained) == 1040 and all(coverage.values())
    assert hashes == {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    result = dict(passed=True, observation_model='Ideal phase-only reliable color mask; not ray-traced visibility.',
                  readable_phases=sorted(front), changed_rear_phases=sorted(rear),
                  pattern_A=a, pattern_B=b, pattern_27=c,
                  shortest_periods=[26,26,27], A_counts=dict(Counter(a)), B_counts=dict(Counter(b)),
                  same_color_counts_A_B=True, distinct_up_to_rotation_and_reversal=True,
                  same_visible_measurements_A_B=True, copies_examined=13,
                  positions_read_26=10, positions_read_27=27,
                  clear_readings_per_27_position=5,
                  selected_position=3,
                  selected_position_phases=[(3+j*27) % 13 for j in range(4)],
                  actual_necklace_input_sha256=hashes,
                  actual_retained_observations=1040, actual_observed_pattern_positions=208,
                  actual_coverage=coverage,
                  scope='Constructed-example arithmetic and saved-assignment coverage only. No new physical visibility, identity or pigment claim.')
    OUT.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'actual_coverage'}, indent=2))


if __name__ == '__main__':
    main()
