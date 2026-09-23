"""Exact relative indices from supplied signed crochet-neighbor edges.

No geometry, color, source index or edge inference enters this solver.
"""
from collections import defaultdict, deque

OFFSETS = (-7, -6, -1, 1, 6, 7)


def propagate(vertices, edges, modulus=None):
    """Retain independent component origins; report contradictions, never repair.

    Edges are directed (u, v, index(v)-index(u)); require explicit reciprocals.
    Raw tree potentials expose winding; residues handle a known closed chain.
    """
    vertices = list(vertices)
    if len(set(vertices)) != len(vertices):
        raise ValueError('Duplicate vertices')
    if modulus is not None and (type(modulus) is not int or modulus <= 14):
        raise ValueError('Known integer modulus must exceed twice the largest offset')
    edges = [tuple(e) for e in edges]
    adjacency = {v: [] for v in vertices}
    for u, v, delta in edges:
        if u not in adjacency or v not in adjacency or u == v:
            raise ValueError('Invalid edge endpoint')
        if type(delta) is not int or delta not in OFFSETS:
            raise ValueError('Invalid neighbor offset')
        adjacency[u].append((v, delta))
        adjacency[v].append((u, -delta))
    edge_set = set(edges)
    missing_reciprocals = [list(e) for e in sorted(edge_set)
                           if (e[1], e[0], -e[2]) not in edge_set]
    labels, components = {}, []
    for seed in vertices:
        if seed in labels:
            continue
        labels[seed] = 0
        queue, members = deque([seed]), []
        while queue:
            u = queue.popleft()
            members.append(u)
            for v, delta in adjacency[u]:
                if v not in labels:
                    labels[v] = labels[u] + delta
                    queue.append(v)
        components.append({'seed': seed, 'vertices': members, 'offset': 'unknown'})
    conflicts, windings = [], []
    for u, v, delta in sorted(edge_set):
        residual = labels[u] + delta - labels[v]
        if residual and (modulus is None or residual % modulus):
            conflicts.append([u, v, delta, residual])
        elif residual:
            windings.append([u, v, delta, residual // modulus])
    duplicates = []
    for component in components:
        by_index = defaultdict(list)
        for v in component['vertices']:
            by_index[labels[v] if modulus is None else labels[v] % modulus].append(v)
        duplicates.extend(group for group in by_index.values() if len(group) > 1)
    return {'components': components, 'labels': labels, 'modulus': modulus,
            'missing_reciprocals': missing_reciprocals,
            'conflicts': conflicts, 'winding_edges': windings,
            'duplicate_indices': duplicates,
            'consistent': not (missing_reciprocals or conflicts or duplicates)}


def reciprocal(edges):
    return [edge for u, v, d in edges for edge in ((u, v, d), (v, u, -d))]
