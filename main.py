# main.py

import cv2
import numpy as np
from segmentation import slic_superpixels, build_rag, merge_regions, extract_regions
from quantization import fit_color_palette, assign_color_and_certainty
from pattern import autocorrelation_period, minimal_period

import argparse
import glob
import os
import warnings
from scipy.spatial.distance import pdist

def iterative_pipeline(image_path, n_colors, expected_area, max_iters=5,
                       n_segments=200, verbose=False):
    img = cv2.imread(image_path)[:,:,::-1]
    # estimate how many beads you expect
    est_beads = (img.shape[0]*img.shape[1]) / expected_area
    # generate superpixels
    segments = slic_superpixels(img, n_segments=n_segments)
    seg_count = segments.max()+1
    if verbose:
        print(f"[DEBUG] Generated {seg_count} superpixels (est_beads={est_beads:.1f})")
    # warn if too few superpixels
    if seg_count < est_beads * 1.2:
        warnings.warn(
            f"[WARN] only {seg_count} superpixels <1.2× your est_beads ({est_beads:.1f}); "
            "try raising --n_segments"
        )
    rag = build_rag(img, segments)
    if verbose:
        print(f"[DEBUG] Built RAG with {len(rag.nodes)} nodes")
    labels = merge_regions(img, segments, rag)
    if verbose:
        print(f"[DEBUG] First merge_regions → {labels.max()+1} labels")
    props = extract_regions(labels)

    for i in range(1, max_iters+1):
        if verbose:
            print(f"[DEBUG] Iter {i}/{max_iters} – fitting palette")
        palette, kmeans = fit_color_palette(img, props, n_colors)
        labels = merge_regions(img, segments, rag, thresh=20)
        props = extract_regions(labels)
        if verbose:
            print(f"[DEBUG]   → palette={palette}, regions={len(props)}")

        # --- Detect if n_colors is too low ---
        if len(palette) > 1:
            dists = pdist(palette, metric='euclidean')
            max_dist = dists.max()
            if max_dist > 200:    # 200≈half the max RGB‑space diameter
                warnings.warn(
                    f"[WARN] palette colors spread too far apart ({max_dist:.1f}); "
                    f"n_colors={n_colors} may be too low."
                )

    # --- Check expected_area against actual region sizes ---
    areas = np.array([r.area for r in props])
    if areas.size:
        med = np.median(areas)
        if expected_area > med * 1.5:
            warnings.warn(
                f"[WARN] expected_area={expected_area} >1.5× median region area ({med:.1f}); "
                "most beads will be low‑certainty."
            )
        elif expected_area < med * 0.5:
            warnings.warn(
                f"[WARN] expected_area={expected_area} <0.5× median region area ({med:.1f}); "
                "you may pick up spurious tiny regions."
            )
    bead_data = assign_color_and_certainty(img, props, palette, expected_area)
    if verbose:
        print(f"[DEBUG] Assigned color & certainty to {len(bead_data)} beads")

    # Part 3: Pattern Recovery
    color_seq = [cd[1] for cd in sorted(bead_data)]
    periods = autocorrelation_period(color_seq)
    if verbose:
        print(f"[DEBUG] Autocorrelation periods: {periods}")
    p = minimal_period(color_seq)
    if verbose:
        print(f"[DEBUG] Minimal period: {p}")
    print("Candidate periods:", periods)
    print("Minimal period:", p)
    return palette, bead_data, p

def main():
    parser = argparse.ArgumentParser(
        description="Bead‑pattern recovery pipeline"
    )
    parser.add_argument(
        "image_glob",
        help="Path or glob pattern to input image(s), e.g. 'beaded-example.jpg' or '*.jpg'"
    )
    parser.add_argument(
        "--n_colors", type=int, default=3,
        help="Number of colors to quantize to"
    )
    parser.add_argument(
        "--expected_area", type=int, default=500,
        help="Expected bead area (pixels)"
    )
    parser.add_argument(
        "--max_iters", type=int, default=5,
        help="Number of quantization‑merge iterations"
    )
    parser.add_argument(
        "--n_segments", type=int, default=200,
        help="Number of superpixels to generate"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="Show debug progress messages"
    )
    args = parser.parse_args()

    paths = glob.glob(args.image_glob)
    if not paths:
        parser.error(f"No files match '{args.image_glob}'")

    for image_path in paths:
        if not os.path.isfile(image_path):
            parser.error(f"File not found: {image_path}")

        palette, bead_data, period = iterative_pipeline(
            image_path,
            n_colors=args.n_colors,
            expected_area=args.expected_area,
            max_iters=args.max_iters,
            n_segments=args.n_segments,
            verbose=args.verbose
        )
        print(f"\n=== Results for {image_path} ===")
        print("Recovered palette:", palette)
        print("Pattern length:", period)

if __name__ == "__main__":
    main()
