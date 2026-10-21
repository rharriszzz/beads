"""Check the draft's visibility examples and full target; no image inference.

Run .venv/bin/python photo2/retrospective/visibility_examples.py from repo root.
The phase mask models reliable color readings, not measured bead silhouettes.
"""
from collections import Counter
from math import cos, pi
from pathlib import Path
import gzip
import hashlib
import json
import re

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
    chunks52 = ['RRRRYYYYBBBBR', 'YYYYBBBBRRRRY', 'BBBBRRRRYYYYB', 'RYBRYBRYBRYBR']
    word52 = ''.join(chunks52)
    assert len(word52) == shortest(word52) == 52
    views52 = []
    for angle in [0, 120, 240]:
        phases = [r for r in range(13) if cos(4*pi*r/13-angle*pi/180) > .5]
        positions = [p for p in range(52) if p % 13 in phases]
        views52.append(dict(view_degrees=angle, readable_phases=phases,
                            positions=positions, count=len(positions)))
    assert [v['count'] for v in views52] == [20, 16, 16]
    assert set.union(*(set(v['positions']) for v in views52)) == set(range(52))
    assert sum(v['count'] for v in views52) == 52
    # Coverage generalizes to arbitrary colors and any multiple of 13 because
    # the three masks partition all thirteen phase classes.
    assert sorted(r for v in views52 for r in v['readable_phases']) == list(range(13))
    paths = [ROOT/'photo2/r344/graph.json.gz', ROOT/'photo2/r347/answers/assessment.json',
             ROOT/'photo2/r344/pattern208.json']
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    with gzip.open(paths[0], 'rt') as f:
        graph = json.load(f)
    assessment = json.loads(paths[1].read_text())
    target = json.loads(paths[2].read_text())['provisional_sequence']
    assert len(target) == shortest(target) == 208
    statuses = assessment['epochs']['maker_assessment']['entries']
    weak = [r['position'] for r in statuses if r['status'] != 'supported']
    assert weak == [43,75,82,89,140,147,186]
    assert all(target[p] == 'B' for p in weak)
    strict = ''.join('?' if p in weak else c for p, c in enumerate(target))
    marked = ''.join('b' if p in weak else c for p, c in enumerate(target))
    assert Counter(target) == {'R':62, 'Y':62, 'B':84}
    assert Counter(strict) == {'R':62, 'Y':62, 'B':77, '?':7}
    draft = (ROOT/'photo2/PATTERN_VISIBILITY_EXPLAINED.md').read_text()
    table = draft.split('<!-- BEGIN_CURRENT_208_TABLE -->')[1].split('<!-- END_CURRENT_208_TABLE -->')[0]
    table_rows = re.findall(r'\| (\d+)–(\d+) \| `([RYB?]+)` \| `([RYBb]+)` \|', table)
    assert len(table_rows) == 16
    for j, (first, last, strict_row, marked_row) in enumerate(table_rows):
        start = j*13
        assert (int(first), int(last)) == (start, start+12)
        assert strict_row == strict[start:start+13] and marked_row == marked[start:start+13]
    assert ''.join(r[3] for r in table_rows).upper() == target
    assert all(chunk in draft for chunk in chunks52)
    coords = {r['id']: r['ab'] for r in graph['coordinates']}
    original_colors = {r['id']: r['color'] for r in graph['observations']}
    retained = sorted(set(coords)-set(assessment['excluded_from_color_evidence']))
    coverage = {p: [] for p in range(208)}
    for o in retained:
        a0, b0 = coords[o]
        k = (7*a0+6*b0) % 2704
        color = 'yellow' if o in assessment['maker_photo_yellow_corrections'] else original_colors[o]
        assert color[0].upper() == target[k % 208]
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
                  middle_example=dict(word=word52, shortest_period=52, views=views52,
                                      combined_positions_read=52,
                                      masks_partition_all_13_phases=True,
                                      coverage_independent_of_color_choices=True),
                  actual_necklace_input_sha256=hashes,
                  actual_retained_observations=1040, actual_observed_pattern_positions=208,
                  actual_candidate_sequence=target, actual_current_strict_sequence=strict,
                  actual_marked_candidate_sequence=marked, actual_insufficient_positions=weak,
                  all_208_document_entries_verified=True,
                  actual_coverage=coverage,
                  scope='Constructed-example arithmetic and saved-assignment coverage only. No new physical visibility, identity or pigment claim.')
    OUT.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'actual_coverage'}, indent=2))


if __name__ == '__main__':
    main()
