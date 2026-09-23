"""Experimental joint triangle and three-family trace inference from image features.

No source index, color, camera, helicity, true body axis or ring modulus enters.
Local consistency is a filter, not proof that a physical neighbor was recovered.
"""
from __future__ import annotations

from collections import defaultdict
from itertools import combinations, product

import numpy as np

from infer_neighbors import PARAMETERS as BASE, image_frames

PARAMETERS = dict(sector_margin_degrees=12., continuation_turn_degrees=35.,
                  continuation_length_ratio=1.8, minimum_triangle_sine=.08,
                  distance_ratio=BASE['ambiguity_ratio'],
                  nearest_count=BASE['nearest_count'], reach_factor=BASE['reach_factor'])


def canonical(u, v, delta):
    return (u, v, delta) if u < v else (v, u, -delta)


def sector(angle):
    x, y = np.cos(angle), np.sin(angle)
    if abs(x) <= BASE['axial_fraction']:
        return 1 if y >= 0 else -1
    sign = 1 if x >= 0 else -1
    return sign*(7 if sign*y >= 0 else 6)


def candidate_edges(xy, tangent, valid):
    """Reciprocal, short candidates with adjacent-sector labels retained."""
    delta = xy[None, :, :]-xy[:, None, :]
    distance = np.linalg.norm(delta, axis=2)
    np.fill_diagonal(distance, np.inf)
    normal = np.column_stack((-tangent[:, 1], tangent[:, 0]))
    margin = np.deg2rad(PARAMETERS['sector_margin_degrees'])
    pools = defaultdict(list)
    for u in range(len(xy)):
        if not valid[u]:
            continue
        distances = np.sort(distance[u])
        # Include ties at the kth-neighbor distance, independent of vertex IDs.
        reach = min(PARAMETERS['reach_factor']*distances[2],
                    distances[min(PARAMETERS['nearest_count'], len(xy)-1)-1])
        for v in np.flatnonzero((distance[u] <= reach+1e-9) & (distance[u] > 1e-8)):
            angle = np.arctan2(delta[u, v] @ normal[u], delta[u, v] @ tangent[u])
            labels = {sector(angle+shift) for shift in (-margin, 0., margin)}
            for d in labels:
                pools[u, d].append((int(v), float(distance[u, v])))
    near = set()
    sectors = []
    for (u, d), entries in sorted(pools.items()):
        nearest = min(r for _, r in entries)
        eligible = [(v, r) for v, r in entries
                    if r <= PARAMETERS['distance_ratio']*nearest+1e-9]
        near.update((u, v, d) for v, _ in eligible)
        sectors.append([u, d, sorted([[v, r] for v, r in entries]),
                        sorted(v for v, _ in eligible)])
    reciprocal = {canonical(u, v, d) for u, v, d in near if (v, u, -d) in near}
    nonreciprocal = sorted(e for e in near if (e[1], e[0], -e[2]) not in near)
    return sorted(reciprocal), sectors, nonreciprocal


def motifs(xy, edges):
    """Enumerate signed 1+6=7 triangles and smooth two-edge continuations."""
    neighbors = defaultdict(dict)
    outgoing = defaultdict(list)
    for index, (u, v, d) in enumerate(edges):
        neighbors[u].setdefault(v, []).append((d, index))
        neighbors[v].setdefault(u, []).append((-d, index))
        outgoing[u, d].append((v, index))
        outgoing[v, -d].append((u, index))
    triangles = []
    for u in sorted(neighbors):
        for v, w in combinations(sorted(n for n in neighbors[u] if n > u), 2):
            if w not in neighbors[v]:
                continue
            a, b = xy[v]-xy[u], xy[w]-xy[u]
            cross = a[0]*b[1]-a[1]*b[0]
            sine = abs(cross)/(np.linalg.norm(a)*np.linalg.norm(b))
            if sine < PARAMETERS['minimum_triangle_sine']:
                continue
            for (d, e1), (e, e2), (f, e3) in product(
                    neighbors[u][v], neighbors[u][w], neighbors[v][w]):
                if d+f == e and {abs(d), abs(e), abs(f)} == {1, 6, 7}:
                    triangles.append([e1, e2, e3])
    continuations = []
    cosine = np.cos(np.deg2rad(PARAMETERS['continuation_turn_degrees']))
    for v in range(len(xy)):
        for d in (1, 6, 7):
            for (u, e1), (w, e2) in product(outgoing[v, -d], outgoing[v, d]):
                if u == w:
                    continue
                a, b = xy[v]-xy[u], xy[w]-xy[v]
                la, lb = np.linalg.norm(a), np.linalg.norm(b)
                if a @ b >= cosine*la*lb-1e-9 and max(la, lb) <= PARAMETERS['continuation_length_ratio']*min(la, lb)+1e-9:
                    continuations.append([e1, e2, v])
    return triangles, continuations


def trace_families(edges):
    """Maximal directed paths/cycles for each family; offsets stay unspecified."""
    traces = []
    for family in (1, 6, 7):
        following, previous = {}, {}
        for u, v, d in edges:
            if abs(d) != family:
                continue
            u, v = (u, v) if d > 0 else (v, u)
            assert u not in following and v not in previous
            following[u], previous[v] = v, u
        unseen = set(following)
        seeds = sorted(set(following)-set(previous))
        while unseen:
            start = seeds.pop(0) if seeds else min(unseen)
            if start not in unseen:
                continue
            path = [start]
            current = start
            while current in unseen:
                unseen.remove(current)
                current = following[current]
                path.append(current)
            traces.append(dict(family=family, vertices=path, closed=path[-1] == path[0],
                               offset='unknown', status='unvalidated_image_trace'))
    return traces


def infer_joint(xy, covariance=None):
    xy = np.asarray(xy, float)
    if xy.ndim != 2 or xy.shape[1] != 2 or len(xy) < 4 or not np.isfinite(xy).all():
        raise ValueError('Expected at least four finite image positions')
    tangent, valid, steered = image_frames(xy, covariance)
    edges, sectors, nonreciprocal = candidate_edges(xy, tangent, valid)
    triangles, continuations = motifs(xy, edges)
    sides, ends = [set() for _ in edges], [set() for _ in edges]
    for triangle in triangles:
        vertices = {v for e in triangle for v in edges[e][:2]}
        for e in triangle:
            u, v, _ = edges[e]
            w, = vertices-{u, v}
            a, b = xy[v]-xy[u], xy[w]-xy[u]
            sides[e].add(1 if a[0]*b[1]-a[1]*b[0] > 0 else -1)
    for a, b, middle in continuations:
        ends[a].add(middle)
        ends[b].add(middle)
    scores = [2*len(sides[e])+len(ends[e]) for e in range(len(edges))]
    slots = defaultdict(list)
    for e, (u, v, d) in enumerate(edges):
        if sides[e] and ends[e]:
            slots[u, d].append(e)
            slots[v, -d].append(e)
    choices, ambiguous = {}, []
    for slot, options in sorted(slots.items()):
        best = max(scores[e] for e in options)
        winners = [e for e in options if scores[e] == best]
        if len(winners) == 1:
            choices[slot] = winners[0]
        else:
            ambiguous.append([*slot, winners])
    selected = {e for e, (u, v, d) in enumerate(edges)
                if choices.get((u, d)) == e and choices.get((v, -d)) == e}
    # Two labels for one pair are competing explanations, never two accepted edges.
    pairs = defaultdict(list)
    for e in selected:
        pairs[edges[e][:2]].append(e)
    label_ambiguities = [sorted(options) for options in pairs.values() if len(options) > 1]
    selected -= {e for options in label_ambiguities for e in options}
    selected_before_pruning = sorted(selected)
    pruning = []
    while selected:
        triangle_supported = {e for motif in triangles if set(motif) <= selected for e in motif}
        trace_supported = {e for a, b, _ in continuations if a in selected and b in selected for e in (a, b)}
        removed = selected-(triangle_supported & trace_supported)
        if not removed:
            break
        pruning.append(sorted(removed))
        selected -= removed
    chosen = [list(edges[e]) for e in sorted(selected)]
    variants = []
    for hand in (1, -1):
        converted = [[u, v, d if hand == 1 else -d if abs(d) == 1 else (1 if d > 0 else -1)*(13-abs(d))]
                     for u, v, d in chosen]
        # Alternatives below refer to convention +1 candidate IDs, explicitly.
        variants.append(dict(convention=hand, edges=converted, ambiguous=ambiguous,
                             boundary_ambiguous=label_ambiguities, nonreciprocal=nonreciprocal,
                             diagnostics_convention=1, traces=trace_families(converted)))
    return dict(parameters=PARAMETERS, tangent=tangent.tolist(), shape_steered=steered.tolist(),
                variants=variants, candidates=[list(e) for e in edges], candidate_sectors=sectors,
                triangles=triangles, continuations=continuations, scores=scores,
                selected_before_pruning=selected_before_pruning,
                selected_candidate_ids=sorted(selected), pruning_rounds=pruning,
                status='experimental_local_constraints_not_validated_indexing')
