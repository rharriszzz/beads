"""Unwrap bracelet band via saturation mask and run 2D FFT to estimate spacing/helicity."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Tuple, List

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.interpolate import splprep, splev
from skimage import measure, morphology


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


def skeleton_longest_path(skel: np.ndarray) -> np.ndarray:
    coords = np.argwhere(skel)
    if coords.size == 0:
        return np.zeros((0, 2))
    id_for = {(int(r), int(c)): idx for idx, (r, c) in enumerate(coords)}
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
    start = next(iter(G.nodes))
    far1 = max(nx.single_source_dijkstra_path_length(G, start).items(), key=lambda x: x[1])[0]
    far2 = max(nx.single_source_dijkstra_path_length(G, far1).items(), key=lambda x: x[1])[0]
    path_nodes = nx.shortest_path(G, far1, far2)
    coords_ordered = np.array([G.nodes[n]["pos"] for n in path_nodes])
    return coords_ordered


def fit_spline(points: np.ndarray, smooth: float = 5.0, num: int = 600) -> np.ndarray:
    if points.shape[0] < 4:
        return points
    tck, _ = splprep(points.T, s=smooth, per=False)
    u = np.linspace(0, 1, num)
    out = splev(u, tck)
    return np.stack(out, axis=1)


def unwrap_strip(img: np.ndarray, mask: np.ndarray, centerline: np.ndarray, strip_height: int = 128) -> np.ndarray:
    """Sample a rectangular strip (arc-length x normal) from img using centerline and mask distance."""
    h, w = img.shape
    dt = ndimage.distance_transform_edt(mask)
    if centerline.shape[0] < 2:
        return np.zeros((strip_height, 1), dtype=np.float32)
    # Fit spline to centerline for smooth tangents
    spline = fit_spline(centerline, smooth=5.0, num=centerline.shape[0] * 3)
    # Derivatives along spline for normals
    tck, _ = splprep(centerline.T, s=5.0, per=False)
    us = np.linspace(0, 1, strip_height * 4)  # we'll resample along length later
    coords = np.stack(splev(us, tck), axis=1)
    derivs = np.stack(splev(us, tck, der=1), axis=1)

    # Resample to fixed width (strip_width samples along length)
    strip_width = 512
    us_fixed = np.linspace(0, 1, strip_width)
    coords = np.stack(splev(us_fixed, tck), axis=1)
    derivs = np.stack(splev(us_fixed, tck, der=1), axis=1)

    normals = []
    for d in derivs:
        dx, dy = d
        norm = np.hypot(dx, dy)
        if norm == 0:
            normals.append((0.0, 0.0))
        else:
            nx, ny = -dy / norm, dx / norm
            normals.append((nx, ny))
    normals = np.array(normals)

    # Determine local half-width using distance transform
    widths = []
    for (x, y) in coords:
        xi, yi = int(np.clip(round(x), 0, w - 1)), int(np.clip(round(y), 0, h - 1))
        widths.append(dt[yi, xi])
    widths = np.array(widths)
    max_width = np.percentile(widths, 90)

    strip = np.zeros((strip_height, strip_width), dtype=np.float32)
    for i in range(strip_width):
        cx, cy = coords[i]
        nx, ny = normals[i]
        halfw = min(max_width, widths[i])
        for j in range(strip_height):
            # j spans [-1, 1] across the height
            frac = (j / (strip_height - 1)) * 2 - 1
            offset = frac * halfw
            sx = cx + nx * offset
            sy = cy + ny * offset
            strip[j, i] = ndimage.map_coordinates(img, [[sy], [sx]], order=1, mode="nearest")[0]
    return strip


def fft_peaks(fft_mag: np.ndarray, topk: int = 5, exclude_radius: int = 5) -> List[Tuple[int, int, float]]:
    """Return top-k peaks (y,x,val) excluding center low-frequency area."""
    H, W = fft_mag.shape
    cy, cx = H // 2, W // 2
    mask = np.ones_like(fft_mag, dtype=bool)
    yy, xx = np.ogrid[:H, :W]
    mask[(yy - cy) ** 2 + (xx - cx) ** 2 <= exclude_radius ** 2] = False
    vals = fft_mag.copy()
    vals[~mask] = 0
    flat_idx = np.argpartition(vals.ravel(), -topk)[-topk:]
    peaks = []
    for idx in flat_idx:
        y, x = np.unravel_index(idx, vals.shape)
        peaks.append((int(y), int(x), float(vals[y, x])))
    peaks.sort(key=lambda p: p[2], reverse=True)
    return peaks


def process_image(img_path: Path, outdir: Path, strip_height: int = 128):
    img_rgb = np.array(Image.open(img_path).convert("RGB"))
    img_hsv = np.array(Image.open(img_path).convert("HSV"))
    s = img_hsv[:, :, 1]

    thr = otsu_threshold(s)
    mask = s > thr
    mask = morphology.binary_opening(mask, morphology.disk(2))
    mask = morphology.binary_closing(mask, morphology.disk(2))
    mask = largest_component(mask)

    skel = morphology.skeletonize(mask)
    center_pts = skeleton_longest_path(skel)
    strip = unwrap_strip(s.astype(float), mask, center_pts, strip_height=strip_height)

    # Window and FFT
    wy = np.hanning(strip.shape[0])
    wx = np.hanning(strip.shape[1])
    window = wy[:, None] * wx[None, :]
    strip_win = strip * window
    fft = np.fft.fftshift(np.fft.fft2(strip_win))
    mag = np.log1p(np.abs(fft))
    mag_norm = (mag - mag.min()) / (mag.max() - mag.min() + 1e-8)

    outdir.mkdir(parents=True, exist_ok=True)
    stem = img_path.stem
    Image.fromarray((mask.astype(np.uint8) * 255)).save(outdir / f"{stem}-fft-mask.png")
    skel_img = np.zeros_like(mask, dtype=np.uint8)
    skel_img[skel] = 255
    Image.fromarray(skel_img).save(outdir / f"{stem}-fft-skel.png")
    Image.fromarray(np.clip(strip, 0, 255).astype(np.uint8)).save(outdir / f"{stem}-fft-strip.png")
    Image.fromarray((mag_norm * 255).astype(np.uint8)).save(outdir / f"{stem}-fft-magnitude.png")

    peaks = fft_peaks(mag_norm, topk=8, exclude_radius=5)

    # Save overlay with centerline
    plt.figure(figsize=(10, 12))
    plt.imshow(img_rgb)
    if center_pts.size:
        plt.plot(center_pts[:, 0], center_pts[:, 1], color="yellow", linewidth=1.0, label="Centerline")
    plt.axis("off")
    if center_pts.size:
        plt.legend()
    plt.tight_layout()
    plt.savefig(outdir / f"{stem}-fft-centerline.png", dpi=200)
    plt.close()

    print(f"Otsu S threshold: {thr}, mask ratio: {mask.mean():.4f}")
    print("Top FFT peaks (y,x,val):")
    for p in peaks:
        print(f"  {p}")
    return peaks


def main():
    parser = argparse.ArgumentParser(description="Unwrap bracelet via saturation mask and run 2D FFT.")
    parser.add_argument("--image", required=True, type=Path, help="Input image")
    parser.add_argument("--outdir", type=Path, default=Path("image-to-pattern/debug-output"), help="Output directory")
    parser.add_argument("--strip-height", type=int, default=128, help="Height of unwrapped strip in pixels")
    args = parser.parse_args()
    process_image(args.image, args.outdir, strip_height=args.strip_height)


if __name__ == "__main__":
    main()
