"""Independent saved-edge checks and documentation/link/preservation validation.

Run python3 -m photo2.r348.validate; no historical scientific outputs are written.
"""
from collections import Counter
from math import gcd
from pathlib import Path
from urllib.parse import unquote, urlparse
import gzip
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
TARGET = 'R332-R-0037-0040'
DOCS = [ROOT/'photo2'/p for p in ['RETROSPECTIVE.md', 'FUTURE_PROJECT_METHODS.md',
        'R347_PATTERN_CONFIRMATION.md', 'r347/answers/ASSESSMENT.md', 'r348/SENSITIVITY.md']]


def read(path):
    with gzip.open(path, 'rt') if str(path).endswith('.gz') else Path(path).open() as f:
        return json.load(f)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def vector(a, b, sign=1):
    return tuple(x+sign*y for x, y in zip(a, b))


def union_check(nodes, edges):
    # A weighted disjoint-set calculation, independent of analyze.py's BFS tree.
    parent = {o: o for o in nodes}
    offset = {o: (0, 0) for o in nodes}

    def find(o):
        if parent[o] != o:
            old = parent[o]
            root, extra = find(old)
            offset[o] = vector(offset[o], extra)
            parent[o] = root
        return parent[o], offset[o]

    residuals = []
    for e in edges:
        u, v, d = e['source'], e['target'], tuple(e['delta_ab'])
        ru, du = find(u)
        rv, dv = find(v)
        if ru != rv:
            parent[ru] = rv
            offset[ru] = vector(vector(dv, du, -1), d, -1)
        else:
            residuals.append(vector(vector(d, du), dv, -1))
    assert len({find(o)[0] for o in nodes}) == 1
    nonzero = [r for r in residuals if r != (0, 0)]
    ga = gb = 0
    for a, b in nonzero:
        ga, gb = gcd(ga, abs(a)), gcd(gb, abs(b))
        assert a*201 == b*214
    assert (ga, gb) == (214, 201)
    return len(residuals)


def check_paths(certificate, edges, allowed, closed=False):
    for c in certificate:
        steps = c['steps']
        for j, s in enumerate(steps):
            assert s['source'] in allowed and s['target'] in allowed
            e = edges[s['edge_index']]
            if s['source'] == e['source'] and s['target'] == e['target']:
                expected = e['delta_ab']
            else:
                assert s['source'] == e['target'] and s['target'] == e['source']
                expected = [-x for x in e['delta_ab']]
            assert s['delta_ab'] == expected
            if j:
                assert steps[j-1]['target'] == s['source']
        if closed:
            assert steps[-1]['target'] == steps[0]['source']
            assert [sum(s['delta_ab'][j] for s in steps) for j in range(2)] == c['delta_ab']
        else:
            assert [steps[0]['source'], steps[-1]['target']] == c['endpoints']


def check_links():
    errors, local, github = [], set(), set()
    repos = {name: ROOT.parent/name for name in ['beads', 'bead_map', 'hsv_tools']}
    for doc in DOCS:
        raw = doc.read_text()
        text = re.sub(r'^```.*?^```\s*$', '', raw, flags=re.M | re.S)
        definitions = {m.group(1).casefold(): m.group(2) for m in re.finditer(
            r'^\[([^\]]+)\]:\s*(\S+)', text, re.M)}
        targets = [m.group(1) for m in re.finditer(r'\]\(([^)]+)\)', text)] + list(definitions.values())
        for m in re.finditer(r'\[[^\]\n]+\]\[([^\]\n]+)\]', text):
            if m.group(1).casefold() not in definitions:
                errors.append(f'{doc.relative_to(ROOT)}: undefined [{m.group(1)}]')
        for target in targets:
            target = target.strip('<>')
            url = urlparse(target)
            if url.scheme in ['http', 'https']:
                if url.netloc != 'github.com':
                    continue
                parts = url.path.strip('/').split('/')
                if len(parts) < 4 or parts[0] != 'rharriszzz' or parts[1] not in repos:
                    continue
                if parts[2] in ['blob', 'tree']:
                    spec = parts[3] + (':' + unquote('/'.join(parts[4:])) if len(parts) > 4 else '')
                elif parts[2] == 'commit':
                    spec = parts[3]
                else:
                    continue
                key = (parts[1], spec)
                if key in github:
                    continue
                result = subprocess.run(['git', 'cat-file', '-e', spec], cwd=repos[parts[1]], capture_output=True)
                if result.returncode:
                    errors.append(f'{doc.relative_to(ROOT)}: missing Git object {key}')
                github.add(key)
            elif not url.scheme:
                path = (doc.parent/unquote(url.path)).resolve() if url.path else doc
                # This receipt is created after the audit completes.
                if not path.exists() and path != HERE/'validation.json':
                    errors.append(f'{doc.relative_to(ROOT)}: missing {target}')
                local.add(str(path))
    assert not errors, '\n'.join(errors)
    return dict(local_targets_checked=len(local), immutable_GitHub_objects_checked=len(github), errors=errors)


def main():
    d = read(HERE/'sensitivity.json')
    g = read(ROOT/'photo2/r344/graph.json.gz')
    co = {o['id']: o['ab'] for o in g['coordinates']}
    obs = {o['id']: o['color'] for o in g['observations']}
    edges = g['edges']
    remain = set(co)-{TARGET}
    reduced_edges = [e for e in edges if TARGET not in (e['source'], e['target'])]
    assert union_check(co, edges) == 1250
    assert union_check(remain, reduced_edges) == 1248
    check_paths([d['graph_before']['cycle_witness']], edges, set(co), closed=True)
    check_paths([d['hypothetical_graph_without_target']['cycle_witness']], reduced_edges, remain, closed=True)
    check_paths(d['alternate_neighbor_paths'], reduced_edges, remain)
    r347 = read(ROOT/'photo2/r347/answers/assessment.json')
    colors = {o: obs[o] for o in remain}
    for o in r347['maker_photo_yellow_corrections']:
        colors[o] = 'yellow'
    blocks = read(ROOT/'photo2/r344/evaluation.json')['geographic_blocks']
    counts = Counter()
    word = read(ROOT/'photo2/r344/pattern208.json')['provisional_sequence']
    for r in range(208):
        ids = [o for o in remain if (7*co[o][0]+6*co[o][1]) % 208 == r]
        assert ids
        palette = {colors[o] for o in ids}
        assert len(palette) == 1 and next(iter(palette))[0].upper() == word[r]
        strong = len(ids) >= 3 and len({blocks[o] for o in ids}) >= 3
        counts['supported' if strong else 'insufficient'] += 1
    assert counts == {'supported': 201, 'insufficient': 7}
    for t in d['pattern']['trials']:
        w = (7, 6) if t['family'] == 'A' else (6, 7)
        bins = {}
        for o in remain:
            residue = ((w[0]*co[o][0]+w[1]*co[o][1]) % t['count']) % t['period']
            bins.setdefault(residue, set()).add(colors[o])
        assert t['compatible'] == all(len(c) == 1 for c in bins.values())
        witness = t['witness']
        if witness:
            assert len(set(witness['colors'])) == 2
            for o, c in zip(witness['ids'], witness['colors']):
                assert o in remain and colors[o] == c
                assert ((w[0]*co[o][0]+w[1]*co[o][1]) % t['count']) % t['period'] == witness['residue']
    seal = read(HERE/'input-seal.json')
    assert all(sha(ROOT/p) == h for p, h in seal.items())
    preservation = Path('/tmp/beads-r348-preservation.json')
    if preservation.exists():
        original = read(preservation)
    else:
        original = None  # The local pre-round dirty hashes are intentionally not published.
    count = 0
    if original is not None:
        for root, rows in original.items():
            for p, h in rows.items():
                assert sha(Path(root)/p) == h
                count += 1
    links = check_links()
    receipt = dict(passed=True, baseline_commit=d['baseline_commit'],
                   independent_weighted_union_find=True, target_free_cycle_and_paths_checked=True,
                   pattern_positions_recomputed=208, finite_period_cases_recomputed=22,
                   support=dict(counts), scientific_files_sealed=len(seal),
                   preexisting_dirty_files_checked=count if original is not None else 'Local pre-round snapshot unavailable',
                   documents={str(p.relative_to(ROOT)): sha(p) for p in DOCS}, links=links,
                   analysis_sha256=sha(HERE/'analyze.py'), sensitivity_sha256=sha(HERE/'sensitivity.json'),
                   scope='Static saved-data analysis only; no original-image inference, physical validation or optimization.')
    (HERE/'validation.json').write_text(json.dumps(receipt, indent=2)+'\n')
    assert (HERE/'validation.json').is_file()
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
