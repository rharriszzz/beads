"""Plot HSV-derived bar charts along the image centerline using log-scaled counts."""

import argparse
from collections import Counter
from pathlib import Path
from typing import Dict, Tuple

import matplotlib

matplotlib.use("Agg")  # headless backend
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors as mcolors
from PIL import Image


def load_counts(img: np.ndarray) -> Dict[Tuple[int, int, int], int]:
    """Count distinct HSV tuples using Counter."""
    flat = img.reshape(-1, 3)
    return Counter(map(tuple, flat))


def load_neighbor_counts(npz_path: Path) -> Dict[Tuple[int, int, int], int]:
    """Load neighbor_counts mapping from a saved npz (values, neighbor_counts)."""
    data = np.load(npz_path)
    values = data["values"]
    neighbor_counts = data["neighbor_counts"]
    mapping: Dict[Tuple[int, int, int], int] = {}
    for val, cnt in zip(values, neighbor_counts):
        mapping[tuple(int(x) for x in val)] = int(cnt)
    return mapping


def plot_bars(
    img_hsv: np.ndarray,
    counts_map: Dict[Tuple[int, int, int], int],
    title: str,
    out_path: Path,
):
    """Plot bars along center row with heights = counts (log-scale y-axis)."""
    h, w, _ = img_hsv.shape
    y = h // 2
    row = img_hsv[y, :, :]  # shape (w,3), uint8
    heights = []
    colors = []
    for pix in row:
        key = tuple(int(x) for x in pix)
        cnt = counts_map.get(key, 1)
        heights.append(cnt)
        hsv_norm = np.array([pix[0] / 255.0, pix[1] / 255.0, pix[2] / 255.0])
        rgb = mcolors.hsv_to_rgb(hsv_norm)
        colors.append(rgb)
    x = np.arange(w)
    plt.figure(figsize=(12, 3))
    plt.bar(x, heights, color=colors, width=1.0, edgecolor=None)
    plt.yscale("log")
    plt.xlabel("Pixel index (x)")
    plt.ylabel("Count (log scale)")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()
    print(f"Saved {out_path}")


def plot_centerline_metric(img_hsv: np.ndarray, img_rgb: np.ndarray, metric: str, out_path: Path):
    """Plot centerline bars colored by HSV with height from a chosen metric (gray/h/s/v)."""
    h, w, _ = img_hsv.shape
    y = h // 2
    hsv_row = img_hsv[y, :, :]  # uint8
    rgb_row = img_rgb[y, :, :].astype(float)
    if metric == "gray":
        # luminance approximation from RGB
        heights = (0.299 * rgb_row[:, 0] + 0.587 * rgb_row[:, 1] + 0.114 * rgb_row[:, 2])
        label = "Grayscale (0-255)"
    elif metric == "h":
        heights = hsv_row[:, 0].astype(float)
        label = "Hue channel (0-255)"
    elif metric == "s":
        heights = hsv_row[:, 1].astype(float)
        label = "Saturation channel (0-255)"
    elif metric == "v":
        heights = hsv_row[:, 2].astype(float)
        label = "Value channel (0-255)"
    else:
        raise ValueError(f"Unknown metric {metric}")
    colors = []
    for pix in hsv_row:
        hsv_norm = np.array([pix[0] / 255.0, pix[1] / 255.0, pix[2] / 255.0])
        colors.append(mcolors.hsv_to_rgb(hsv_norm))
    x = np.arange(w)
    plt.figure(figsize=(12, 3))
    plt.bar(x, heights, color=colors, width=1.0, edgecolor=None)
    plt.ylim(0, 255)
    plt.xlabel("Pixel index (x)")
    plt.ylabel(label)
    plt.title(f"Centerline bars colored by HSV, height = {label}")
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()
    print(f"Saved {out_path}")


def save_centerline_overlay(img_rgb: np.ndarray, out_path: Path):
    """Save the original image with the sampled centerline overlaid in black."""
    import matplotlib.pyplot as plt

    h, w, _ = img_rgb.shape
    y = h // 2
    plt.figure(figsize=(12, 8))
    plt.imshow(img_rgb)
    plt.axhline(y, color="black", linewidth=1.0)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches="tight", pad_inches=0)
    plt.close()
    print(f"Saved {out_path}")


def fmt_tol(tol: int) -> str:
    """Format tolerance as absolute value and percent of 0-255 scale."""
    pct = 100.0 * tol / 255.0
    return f"{tol} ({pct:.2f}%)"


def main():
    parser = argparse.ArgumentParser(description="Centerline HSV bar chart with log-scaled counts.")
    parser.add_argument("image", type=Path, help="Input image")
    parser.add_argument("--neighbors", type=Path, help="NPZ with neighbor_counts to use instead of raw counts")
    parser.add_argument("--outdir", type=Path, default=Path("image-to-pattern/debug-output"), help="Output directory")
    parser.add_argument("--h-tol", type=int, default=0, help="Hue tolerance to report in titles")
    parser.add_argument("--s-tol", type=int, default=0, help="Saturation tolerance to report in titles")
    parser.add_argument("--v-tol", type=int, default=0, help="Value tolerance to report in titles")
    args = parser.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)
    img = Image.open(args.image).convert("HSV")
    img_arr = np.array(img, dtype=np.uint8)
    img_rgb = np.array(img.convert("RGB"))

    # Raw counts map
    counts_map = load_counts(img_arr)
    plot_bars(
        img_arr,
        counts_map,
        title="Centerline HSV bars (raw counts, log scale; h_tol=0 (0.00%) s_tol=0 (0.00%) v_tol=0 (0.00%))",
        out_path=args.outdir / f"{args.image.stem}-centerline-bars-raw.png",
    )
    save_centerline_overlay(img_rgb, args.outdir / f"{args.image.stem}-centerline-overlay.png")

    # Metric-based centerline plots
    plot_centerline_metric(img_arr, img_rgb, "gray", args.outdir / f"{args.image.stem}-centerline-bars-gray.png")
    plot_centerline_metric(img_arr, img_rgb, "h", args.outdir / f"{args.image.stem}-centerline-bars-hue.png")
    plot_centerline_metric(img_arr, img_rgb, "s", args.outdir / f"{args.image.stem}-centerline-bars-sat.png")
    plot_centerline_metric(img_arr, img_rgb, "v", args.outdir / f"{args.image.stem}-centerline-bars-val.png")

    if args.neighbors and args.neighbors.exists():
        neigh_map = load_neighbor_counts(args.neighbors)
        plot_bars(
            img_arr,
            neigh_map,
            title=(
                "Centerline HSV bars (neighbor counts, log scale; "
                f"h_tol={fmt_tol(args.h_tol)} s_tol={fmt_tol(args.s_tol)} v_tol={fmt_tol(args.v_tol)})"
            ),
            out_path=args.outdir / f"{args.image.stem}-centerline-bars-neighbors.png",
        )


if __name__ == "__main__":
    main()
