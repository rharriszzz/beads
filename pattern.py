"""
pattern.py
----------
Detect repeating bead‐color patterns via signal processing and string algorithms.
"""

import numpy as np
from scipy.signal import correlate, find_peaks
import networkx as nx
from sklearn.cluster import KMeans

def autocorrelation_period(color_seq):
    """
    Compute autocorrelation (via FFT) and return lag peaks.

    Peaks at lags indicate candidate pattern lengths :contentReference[oaicite:10]{index=10}.
    """
    seq = np.array(color_seq) - np.mean(color_seq)
    acf = correlate(seq, seq, mode='full')[len(seq)-1:]
    peaks, _ = find_peaks(acf, distance=1)
    return peaks

def kmp_prefix(s):
    """
    Build KMP prefix‐function π for sequence s in O(N) time.

    π[i] = length of longest proper prefix of s[:i+1] which is also a suffix. :contentReference[oaicite:11]{index=11}
    """
    n = len(s)
    pi = [0] * n
    for i in range(1, n):
        j = pi[i-1]
        while j > 0 and s[i] != s[j]:
            j = pi[j-1]
        if s[i] == s[j]:
            j += 1
        pi[i] = j
    return pi

def minimal_period(color_seq):
    """
    Derive minimal period p from π such that len(seq) % p == 0, else None.
    """
    pi = kmp_prefix(color_seq)
    p = len(color_seq) - pi[-1]
    return p if len(color_seq) % p == 0 else None

def recover_bead_sequence_by_path(rag, props, bead_data, img_shape, bg_frac=0.05):
    """
    Find the bead‐index ordering of VISIBLE beads by:
    1) Identifying the two huge background regions (outer & inner) via area>bg_frac*image.
    2) Picking the "outer" bg as the one farthest from image center,
       and the "inner" bg as the one closest.
    3) Finding the shortest graph‐path in rag between those two background nodes.
    4) Dropping the first+last nodes (the backgrounds) and returning the list of bead labels
       in path‐order (i.e. bead_index order).
    """
    H, W = img_shape[:2]
    img_area = H * W
    center = np.array([W/2, H/2])

    # 1) find all big regions
    bg_labels = [r.label for r in props if r.area > bg_frac * img_area]
    if len(bg_labels) < 2:
        raise RuntimeError("Could not find two distinct background regions")

    # 2) pick outer & inner by centroid distance to center
    dists = {r.label: np.linalg.norm(np.array(r.centroid) - center)
             for r in props if r.label in bg_labels}
    outer = max(dists, key=dists.get)
    inner = min(dists, key=dists.get)

    # 3) shortest path in rag
    path = nx.shortest_path(rag, source=outer, target=inner)

    # 4) filter to beads only
    bead_labels = {lbl for lbl, _, _, _ in bead_data}
    bead_path = [lbl for lbl in path if lbl in bead_labels]

    return bead_path

def prune_between_regions(rag: nx.Graph,
                          bead_labels: set,
                          bg_labels: set) -> nx.Graph:
    """
    Remove all “filler” regions (dark/grey between beads) from the RAG
    while preserving adjacency between beads and backgrounds.

    Parameters
    ----------
    rag : nx.Graph
        Original region adjacency graph; nodes are region labels.
    bead_labels : set[int]
        Labels of regions identified as beads.
    bg_labels : set[int]
        Labels of the two background regions (outer & inner).
    
    Returns
    -------
    pruned : nx.Graph
        A copy of rag where any node not in bead_labels ∪ bg_labels
        has been removed, but its neighbors are fully connected
        (so adjacency “skips over” the filler node).
    """
    pruned = rag.copy()
    # Nodes to keep: beads + the two backgrounds
    keep = set(bead_labels) | set(bg_labels)
    # Iterate over all nodes; if not in keep, splice them out
    for node in list(rag.nodes()):
        if node not in keep:
            nbrs = list(pruned.neighbors(node))
            # connect every neighbor pair
            for u in nbrs:
                for v in nbrs:
                    if u != v:
                        pruned.add_edge(u, v)
            pruned.remove_node(node)
    return pruned

def label_edge_deltas(rag: nx.Graph,
                      centroids: dict,
                      exact_per_row: float):
    """
    For each edge (u,v) in rag, compute the pixel‐distance between centroids[u]/[v].
    Cluster those distances into 3 groups (ring, diag1, diag2).
    Then assign a Δ‐index to each edge:
      ring     → ±1
      diag1    → ±(exact_per_row - 0.5)
      diag2    → ±(exact_per_row + 0.5)

    Returns a dict edge_delta[(u,v)] = Δ (float, signed by direction of centroid‐difference
    projected onto the ring‐axis).
    """
    # 1) collect all distances
    edges = list(rag.edges())
    dist_vec = np.array([
        np.linalg.norm(np.array(centroids[v]) - np.array(centroids[u]))
        for u, v in edges
    ]).reshape(-1, 1)

    # 2) fit 3‑cluster KMeans
    km = KMeans(n_clusters=3, random_state=0).fit(dist_vec)
    labels = km.labels_
    centers = km.cluster_centers_.flatten()

    # 3) sort clusters by center size
    order = np.argsort(centers)
    # Geometry: ring‐neighbors (Δ=±1) are ~1.4× farther apart than diagonals.
    # Thus the largest‐distance cluster → ring steps, the smaller two → diagonals.
    mag = {
        # largest cluster center → ring neighbor (Δ=±1)
        order[2]: 1.0,
        # middle cluster → long diagonal (Δ=±(exact_per_row+0.5))
        order[1]: exact_per_row + 0.5,
        # smallest cluster → short diagonal (Δ=±(exact_per_row-0.5))
        order[0]: exact_per_row - 0.5
    }

    # 4) estimate “ring axis” direction in image‐space:
    # average direction of all ring‐edges
    ring_dirs = []
    for (u, v), cl in zip(edges, labels):
        if cl == order[0]:
            diff = np.array(centroids[v]) - np.array(centroids[u])
            ring_dirs.append(diff / (np.linalg.norm(diff) + 1e-8))
    ring_axis = np.mean(ring_dirs, axis=0)
    ring_axis /= np.linalg.norm(ring_axis)

    # 5) build edge→Δ mapping with sign
    edge_delta = {}
    for (u, v), cl in zip(edges, labels):
        d = mag[cl]
        # sign: positive if projection of (v−u) onto ring_axis > 0
        sign = np.sign(np.dot( np.array(centroids[v]) - np.array(centroids[u]),
                               ring_axis ))
        edge_delta[(u, v)] = d * sign
        edge_delta[(v, u)] = -d * sign

    return edge_delta
