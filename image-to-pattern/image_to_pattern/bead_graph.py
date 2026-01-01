"""Graph utilities for ordering detected beads along a chain."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
import networkx as nx

from .bead_detect import DetectedBead


@dataclass
class OrderedBeads:
    centers: List[Tuple[float, float]]
    distances: List[float]


def order_beads_by_mst(beads: List[DetectedBead]) -> OrderedBeads:
    """Order beads along a likely chain using MST + longest path heuristic."""
    if not beads:
        return OrderedBeads([], [])
    pts = np.array([b.center for b in beads])
    n = len(beads)
    # Build complete graph distances
    dist = np.linalg.norm(pts[:, None, :] - pts[None, :, :], axis=2)
    G = nx.Graph()
    for i in range(n):
        for j in range(i + 1, n):
            G.add_edge(i, j, weight=float(dist[i, j]))
    mst = nx.minimum_spanning_tree(G)
    # Find longest shortest path in MST (approximate diameter)
    lengths = dict(nx.all_pairs_dijkstra_path_length(mst))
    max_len = -1
    start = end = 0
    for i in range(n):
        for j, d in lengths[i].items():
            if d > max_len:
                max_len = d
                start, end = i, j
    path = nx.shortest_path(mst, source=start, target=end, weight="weight")
    ordered_centers = [tuple(pts[i]) for i in path]
    ordered_dists = [beads[i].distance for i in path]
    return OrderedBeads(centers=ordered_centers, distances=ordered_dists)
