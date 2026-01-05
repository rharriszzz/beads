"""Segment beads via saturation, smooth mask, extract inner/outer splines and centerline."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from PIL import Image
from scipy.interpolate import splprep, splev
from skimage import measure, morphology, filters


def otsu_threshold(values: np.ndarray) -> int:
    hist, _ = np.histogram(values, bins=256, range=(0, 256))
    total = values.size
    sum_total = np.dot(np.arange(256), hist)
    sum_b = 0.0
    w_b = 0.0
    max_var = 0.0
    threshold = 0
    for t in range(256):
        w_b += hist[t]
        if w_b == 0:
            continue
        w_f = total - w_b
        if w_f == 0:
            break
        sum_b += t * hist[t]
        m_b = sum_b / w_b
        m_f = (sum_total - sum_b) / w_f
        var_between = w_b * w_f * (m_b - m_f) ** 2
        if var_between > max_var:
            max_var = var_between
            threshold = t
    return threshold


def largest_component(mask: np.ndarray) -> np.ndarray:
    labeled = measure.label(mask, connectivity=2)
    if labeled.max() == 0:
        return np.zeros_like(mask, dtype=bool)
    largest_label = np.argmax(np.bincount(labeled.ravel())[1:]) + 1
    return labeled == largest_label


def extract_contour(mask: np.ndarray) -> np.ndarray:
    contours = measure.find_contours(mask.astype(float), level=0.5)
    if not contours:
        return np.zeros((0, 2))
    # pick longest contour
    longest = max(contours, key=lambda c: c.shape[0])
    # contours are (row, col) -> (y, x)
    return np.array([[p[1], p[0]] for p in longest])


def fit_spline(points: np.ndarray, smooth: float = 5.0, num: int = 400) -> np.ndarray:
    if points.shape[0] < 4:
        return points
    # Ensure points form a proper sequence for splprep
    tck, _ = splprep(points.T, s=smooth, per=False)
    u = np.linspace(0, 1, num)
    out = splev(u, tck)
    return np.stack(out, axis=1)


def skeleton_longest_path(skel: np.ndarray) -> np.ndarray:
    coords = np.argwhere(skel)
    if coords.size == 0:
        return np.zeros((0, 2))
    # Map to node ids
    id_for = {}
    for idx, (r, c) in enumerate(coords):
        id_for[(r, c)] = idx
    G = nx.Graph()
    for idx, (r, c) in enumerate(coords):
        G.add_node(idx, pos=(c, r))
    neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    for (r, c), idx in id_for.items():
        for dr, dc in neighbors:
            nr, nc = r + dr, c + dc
            nid = id_for.get((nr, nc))
            if nid is not None:
                G.add_edge(idx, nid, weight=1.0)
    # Find farthest pair via double BFS
    start = next(iter(G.nodes))
    far1 = max(nx.single_source_dijkstra_path_length(G, start).items(), key=lambda x: x[1])[0]
    far2 = max(nx.single_source_dijkstra_path_length(G, far1).items(), key=lambda x: x[1])[0]
    path_nodes = nx.shortest_path(G, far1, far2)
    coords_ordered = np.array([G.nodes[n]["pos"] for n in path_nodes])
    return coords_ordered


def process_image(img_path: Path, outdir: Path, erode_radius: int = 5):
    img_rgb = np.array(Image.open(img_path).convert("RGB"))
    img_hsv = np.array(Image.open(img_path).convert("HSV"))
    s = img_hsv[:, :, 1]

    thr = otsu_threshold(s)
    mask = s > thr
    mask = morphology.binary_opening(mask, morphology.disk(2))
    mask = morphology.binary_closing(mask, morphology.disk(2))
    mask = largest_component(mask)

    # Outer contour
    outer_pts = extract_contour(mask)
    outer_spline = fit_spline(outer_pts, smooth=20.0)

    # Inner contour via erosion
    inner_mask = mask.copy()
    for rad in [erode_radius, max(1, erode_radius // 2), 1]:
        inner_mask = morphology.binary_erosion(mask, morphology.disk(rad))
        inner_mask = largest_component(inner_mask)
        if inner_mask.any():
            break
    inner_pts = extract_contour(inner_mask)
    inner_spline = fit_spline(inner_pts, smooth=20.0)

    # Centerline via skeleton
    skel = morphology.skeletonize(mask)
    center_pts = skeleton_longest_path(skel)
    center_spline = fit_spline(center_pts, smooth=5.0)

    # Save mask and skeleton overlays
    outdir.mkdir(parents=True, exist_ok=True)
    mask_img = (mask.astype(np.uint8) * 255)
    Image.fromarray(mask_img, mode="L").save(outdir / f"{img_path.stem}-s-mask.png")
    skel_img = np.zeros_like(mask_img)
    skel_img[skel] = 255
    Image.fromarray(skel_img, mode="L").save(outdir / f"{img_path.stem}-s-skeleton.png")

    plt.figure(figsize=(10, 12))
    plt.imshow(img_rgb)
    if outer_spline.size:
        plt.plot(outer_spline[:, 0], outer_spline[:, 1], color="magenta", linewidth=1.5, label="Outer spline")
    if inner_spline.size:
        plt.plot(inner_spline[:, 0], inner_spline[:, 1], color="cyan", linewidth=1.5, label="Inner spline")
    if center_spline.size:
        plt.plot(center_spline[:, 0], center_spline[:, 1], color="yellow", linewidth=1.5, label="Centerline")
    plt.axis("off")
    plt.legend()
    plt.tight_layout()
    plt.savefig(outdir / f"{img_path.stem}-s-splines.png", dpi=200)
    plt.close()

    print(f"Otsu threshold S={thr}, mask ratio={mask.mean():.4f}")
    return {
        "thr": thr,
        "mask_ratio": float(mask.mean()),
        "outer_points": len(outer_pts),
        "inner_points": len(inner_pts),
        "center_points": len(center_pts),
    }


def main():
    parser = argparse.ArgumentParser(description="Saturation-based segmentation and spline extraction.")
    parser.add_argument("--image", required=True, type=Path, help="Input image")
    parser.add_argument("--outdir", type=Path, default=Path("image-to-pattern/debug-output"), help="Output directory")
    parser.add_argument("--erode-radius", type=int, default=5, help="Initial erosion radius for inner contour")
    args = parser.parse_args()
    process_image(args.image, args.outdir, erode_radius=args.erode_radius)


if __name__ == "__main__":
    main()
