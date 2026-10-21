"""R348: finite saved-graph sensitivity, with no photographic inference or refit.

Run python3 -m photo2.r348.analyze from the repository root. Outputs are derived
certificates under r348 only. Every older tracked scientific file is sealed.
"""
from collections import Counter, defaultdict, deque
from itertools import combinations
from math import gcd
from pathlib import Path
import gzip
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
TARGET = 'R332-R-0037-0040'
BASELINE = '5d6056634009310bd2d47744527f9db43f0809c9'


def read(path):
    path = ROOT / path
    with gzip.open(path, 'rt') if path.suffix == '.gz' else path.open() as f:
        return json.load(f)


def save(path, data):
    (HERE / path).write_text(json.dumps(data, indent=2, allow_nan=False) + '\n')


def add(a, b):
    return tuple(x+y for x, y in zip(a, b))


def sub(a, b):
    return tuple(x-y for x, y in zip(a, b))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def scientific_seal():
    names = subprocess.check_output([
        'git', 'ls-files', '-z', 'beads-photo-2.jpg', 'photo2/r344',
        'photo2/r345', 'photo2/r346', 'photo2/r347', 'photo2/r328', 'photo2/r332',
    ], cwd=ROOT).decode().split('\0')
    # This explanatory document is explicitly authorized for revision in R348.
    editable_document = 'photo2/r347/answers/ASSESSMENT.md'
    return {n: sha(ROOT/n) for n in sorted(names) if n and n != editable_document}


def adjacency(nodes, edges):
    adj = {n: [] for n in nodes}
    for i, e in enumerate(edges):
        u, v, d = e['source'], e['target'], tuple(e['delta_ab'])
        adj[u].append((v, d, i))
        adj[v].append((u, tuple(-x for x in d), i))
    return adj


def path_between(adj, start, end):
    parent = {start: None}
    queue = deque([start])
    while queue and end not in parent:
        u = queue.popleft()
        for v, d, i in adj[u]:
            if v not in parent:
                parent[v] = (u, d, i)
                queue.append(v)
    assert end in parent
    steps = []
    v = end
    while v != start:
        u, d, i = parent[v]
        steps.append(dict(source=u, target=v, delta_ab=d, edge_index=i))
        v = u
    return list(reversed(steps))


def graph_certificate(coords, edges, root):
    adj = adjacency(coords, edges)
    potential = {root: (0, 0)}
    parent = {root: None}
    queue = deque([root])
    while queue:
        u = queue.popleft()
        for v, d, i in adj[u]:
            if v not in potential:
                potential[v] = add(potential[u], d)
                parent[v] = (u, d, i)
                queue.append(v)
    assert len(potential) == len(coords), 'Removal disconnected the saved graph'
    residuals = []
    for i, e in enumerate(edges):
        r = sub(add(potential[e['source']], e['delta_ab']), potential[e['target']])
        if r != (0, 0):
            residuals.append((i, r))
    # Derive the subgroup of integer cycle displacements from edges, not saved H.
    assert residuals
    first = residuals[0][1]
    divisor = gcd(*map(abs, first))
    direction = tuple(x//divisor for x in first)
    if direction[0] < 0 or (direction[0] == 0 and direction[1] < 0):
        direction = tuple(-x for x in direction)
    j = 0 if direction[0] else 1
    coefficient_gcd = 0
    for _, r in residuals:
        assert r[j] % direction[j] == 0
        coefficient = r[j] // direction[j]
        assert r == tuple(coefficient*x for x in direction)
        coefficient_gcd = gcd(coefficient_gcd, abs(coefficient))
    generator = tuple(coefficient_gcd*x for x in direction)
    assert generator == (214, 201)
    for o, ab in coords.items():
        difference = sub(sub(ab, coords[root]), potential[o])
        assert difference[0] % generator[0] == 0
        assert difference[1] == difference[0]//generator[0]*generator[1]
    # A concrete closed walk, independent of the removed target, witnesses H.
    chosen, residual = next((i, r) for i, r in residuals if r in [generator, tuple(-x for x in generator)])
    e = edges[chosen]

    def root_path(o):
        steps = []
        while o != root:
            u, d, i = parent[o]
            steps.append(dict(source=u, target=o, delta_ab=d, edge_index=i))
            o = u
        return list(reversed(steps))

    left, right = root_path(e['source']), root_path(e['target'])
    cycle = left + [dict(source=e['source'], target=e['target'],
                         delta_ab=e['delta_ab'], edge_index=chosen)] + [
        dict(source=s['target'], target=s['source'],
             delta_ab=[-x for x in s['delta_ab']], edge_index=s['edge_index'])
        for s in reversed(right)]
    assert tuple(sum(s['delta_ab'][j] for s in cycle) for j in range(2)) == residual
    # Remove the shared tree prefix/suffix to give a simple fundamental cycle.
    common = 0
    while common < min(len(left), len(right)) and left[common] == right[common]:
        common += 1
    cycle = cycle[common:len(cycle)-common] if common else cycle
    return dict(nodes=len(coords), edges=len(edges), components=1,
                independent_graph_cycles=len(edges)-len(coords)+1,
                nonzero_fundamental_cycle_residuals=len(residuals),
                derived_cycle_subgroup_generator=generator,
                saved_coordinates_recovered_modulo_generator=True,
                cycle_witness=dict(delta_ab=residual, steps=cycle))


def period_certificate(coords, colors):
    trials = []
    for family, total, weights in [('A', 2704, (7, 6)), ('B', 2691, (6, 7))]:
        for period in range(1, 400):
            if total % period:
                continue
            bins = defaultdict(dict)
            for o in sorted(colors):
                a, b = coords[o]
                residue = ((weights[0]*a + weights[1]*b) % total) % period
                bins[residue].setdefault(colors[o], o)
            conflicts = [r for r in sorted(bins) if len(bins[r]) > 1]
            witness = None
            if conflicts:
                r = conflicts[0]
                pair = sorted(bins[r].items())[:2]
                witness = dict(residue=r, ids=[o for _, o in pair], colors=[c for c, _ in pair])
            trials.append(dict(family=family, count=total, period=period,
                               compatible=not conflicts, observed_residues=len(bins), witness=witness))
    return trials


def main():
    seal = scientific_seal()
    g = read('photo2/r344/graph.json.gz')
    coords = {o['id']: tuple(o['ab']) for o in g['coordinates']}
    obs = {o['id']: o for o in g['observations']}
    edges = g['edges']
    root = g['reference']
    incident = [e for e in edges if TARGET in (e['source'], e['target'])]
    reduced_coords = {o: v for o, v in coords.items() if o != TARGET}
    reduced_edges = [e for e in edges if TARGET not in (e['source'], e['target'])]
    full = graph_certificate(coords, edges, root)
    reduced = graph_certificate(reduced_coords, reduced_edges, root)
    assert len(incident) == 3
    neighbors = sorted({e['target'] if e['source'] == TARGET else e['source'] for e in incident})
    adj = adjacency(reduced_coords, reduced_edges)
    paths = [dict(endpoints=[a, b], steps=path_between(adj, a, b))
             for a, b in combinations(neighbors, 2)]
    for p in paths:
        a, b = p['endpoints']
        assert tuple(sum(s['delta_ab'][j] for s in p['steps']) for j in range(2)) == sub(coords[b], coords[a])
    colors = {o: obs[o]['color'] for o in reduced_coords}
    for o in ['REC266-P035619', 'R332-R-0197-0183']:
        colors[o] = 'yellow'
    trials = period_certificate(reduced_coords, colors)
    assert [(t['family'], t['period']) for t in trials if t['compatible']] == [('A', 208)]
    a347 = read('photo2/r347/answers/assessment.json')['epochs']['maker_assessment']
    assert [(t['family'], t['period'], t['compatible']) for t in trials] == [
        (t['family'], t['period'], t['compatible']) for t in a347['trials']]
    r328 = read('photo2/r328/results/graph.json.gz')
    assert TARGET not in {o['id'] for o in r328['observations']}
    assert read('photo2/r328/results/summary.json')['H'] == g['H']
    r332 = read('photo2/r332/results/graph.json.gz')
    dependencies = {}
    for field in ['accepted_additions', 'provisional_observations', 'remaining_candidates']:
        dependencies[field] = [r['id'] for r in r332[field]
                               if TARGET in r.get('anchor_ids', [])
                               or TARGET in r.get('colored_anchor_ids', [])]
    assert not dependencies['accepted_additions']
    summary = dict(baseline_commit=BASELINE, target=TARGET, target_observation=obs[TARGET],
                   incident_edges=incident, graph_before=full, hypothetical_graph_without_target=reduced,
                   alternate_neighbor_paths=paths,
                   color_only_R347=dict(recorded_observations=1059, indexed_nodes=1041,
                                        links=2290, usable_indexed_colors=1040),
                   identity_quarantined=dict(recorded_observations=1059, indexed_nodes=1040,
                                             links=2287, usable_indexed_colors=1040,
                                             explanation='Retain cue in archive, remove its identity-dependent constraints from the hypothetical active graph.'),
                   full_node_deletion=dict(recorded_observations=1058, indexed_nodes=1040,
                                           links=2287, usable_indexed_colors=1040),
                   pattern=dict(supported=201, conflicting=0, insufficient=7,
                                observed_positions=208, agreements=1040, observations=1040,
                                color_evidence_identical_to_R347=True, trials=trials),
                   historical_closure_predates_target=True,
                   saved_R332_anchor_dependencies=dependencies,
                   limitations=['Saved edge labels and other body identities are held fixed. Connected algebra does not prove photographic ownership.',
                                'R332 local fits can depend on all nearby admitted anchors; static deletion is not a counterfactual rerun of those proposals.',
                                'No new topology selection, camera/geometry fit, physical count or authentic-chart validation is performed.'])
    assert seal == scientific_seal()
    save('input-seal.json', seal)
    save('sensitivity.json', summary)
    print(json.dumps(dict(before={k: v for k, v in full.items() if k != 'cycle_witness'},
                          after={k: v for k, v in reduced.items() if k != 'cycle_witness'},
                          alternate_path_lengths=[len(p['steps']) for p in paths],
                          period_cases=len(trials), historical_files_sealed=len(seal)), indent=2))


if __name__ == '__main__':
    main()
