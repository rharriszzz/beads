"""Compute HSV neighbor sums using a Counter (no np.unique)."""

import argparse
from collections import Counter
from pathlib import Path
import time
from typing import Dict, Tuple

import numpy as np
from PIL import Image


def count_hsv(img_path: Path) -> Tuple[np.ndarray, np.ndarray, Dict[Tuple[int, int, int], int], float]:
    """Return (values array, counts array, dict, elapsed_seconds)."""
    img = Image.open(img_path).convert("HSV")
    arr = np.array(img, dtype=np.uint8)
    flat = arr.reshape(-1, 3)
    start = time.perf_counter()
    counter = Counter(map(tuple, flat))
    elapsed = time.perf_counter() - start
    values = np.array(list(counter.keys()), dtype=np.uint16)
    counts = np.array(list(counter.values()), dtype=np.int64)
    return values, counts, counter, elapsed


def neighbor_sums(
    counter: Dict[Tuple[int, int, int], int],
    h_tol: int,
    s_tol: int,
    v_tol: int,
    wrap_hue: bool = True,
    chunk_size: int = 5000,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    """For each HSV value, sum neighbors within tolerance and total neighbor count."""
    keys = list(counter.keys())
    counts = np.array([counter[k] for k in keys], dtype=np.int64)
    neighbor_counts = np.zeros(len(keys), dtype=np.int64)
    neighbor_sums = np.zeros((len(keys), 3), dtype=np.int64)
    start = time.perf_counter()
    # Precompute neighbor offsets to reduce per-key overhead
    offsets = []
    for dh in range(-h_tol, h_tol + 1):
        for ds in range(-s_tol, s_tol + 1):
            for dv in range(-v_tol, v_tol + 1):
                offsets.append((dh, ds, dv))
    offsets = np.array(offsets, dtype=int)

    total = len(keys)
    for start_idx in range(0, total, chunk_size):
        end_idx = min(total, start_idx + chunk_size)
        for idx in range(start_idx, end_idx):
            h_raw, s_raw, v_raw = keys[idx]
            h = int(h_raw)
            s = int(s_raw)
            v = int(v_raw)
            for dh, ds, dv in offsets:
                hh = (h + dh) % 256 if wrap_hue else h + dh
                if not (0 <= hh <= 255):
                    continue
                ss = s + ds
                if not (0 <= ss <= 255):
                    continue
                vv = v + dv
                if not (0 <= vv <= 255):
                    continue
                cnt = counter.get((hh, ss, vv))
                if cnt:
                    neighbor_counts[idx] += cnt
                    neighbor_sums[idx, 0] += cnt * hh
                    neighbor_sums[idx, 1] += cnt * ss
                    neighbor_sums[idx, 2] += cnt * vv
    elapsed = time.perf_counter() - start
    values = np.array(keys, dtype=np.uint16)
    return values, neighbor_counts, neighbor_sums, elapsed


def main():
    parser = argparse.ArgumentParser(description="Compute HSV neighbor sums with tolerances (Counter-based).")
    parser.add_argument("image", type=Path, help="Input image")
    parser.add_argument("--h-tol", type=int, default=2, help="Hue tolerance (0-255)")
    parser.add_argument("--s-tol", type=int, default=2, help="Saturation tolerance (0-255)")
    parser.add_argument("--v-tol", type=int, default=2, help="Value tolerance (0-255)")
    parser.add_argument("--no-wrap-hue", action="store_true", help="Disable hue wrap-around")
    parser.add_argument("--outdir", type=Path, default=Path("image-to-pattern/debug-output"), help="Output directory")
    args = parser.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)
    values, counts, counter, t_count = count_hsv(args.image)
    print(f"Unique HSV values: {values.shape[0]}")
    print(f"Counting time (Counter): {t_count:.3f}s")

    vals, neigh_counts, neigh_sums, t_neigh = neighbor_sums(
        counter, h_tol=args.h_tol, s_tol=args.s_tol, v_tol=args.v_tol, wrap_hue=not args.no_wrap_hue
    )
    print(f"Neighbor accumulation time: {t_neigh:.3f}s")

    out_path = args.outdir / f"{args.image.stem}-hsv-neighbors.npz"
    np.savez_compressed(
        out_path,
        values=vals,
        counts=counts,
        neighbor_counts=neigh_counts,
        neighbor_sums=neigh_sums,
        h_tol=args.h_tol,
        s_tol=args.s_tol,
        v_tol=args.v_tol,
    )
    print(f"Saved neighbor sums to {out_path}")


if __name__ == "__main__":
    main()
