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

    # --- Filter out background‑like regions by image‑fraction threshold ---
    img_area = img.shape[0] * img.shape[1]
    # Drop any region larger than 5% of the entire image
    frac_thresh = 0.05
    area_thresh = img_area * frac_thresh
    large = [r for r in props if r.area > area_thresh]
    if large:
        warnings.warn(
            f"[WARN] Dropping {len(large)} region(s) >{frac_thresh*100:.1f}% "
            f"of image area ({area_thresh:.0f} px) as background"
        )
    props = [r for r in props if r.area <= area_thresh]

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
            # threshold ~200 (≈ half the full [0–255] RGB diagonal)
            if max_dist > 200:
                warnings.warn(
                    f"[WARN] Max RGB‑space distance between centroids = {max_dist:.1f} >200. "
                    "This means your clusters are very far apart, suggesting you "
                    "may be under‑clustering distinct bead colors. "
                    "Try increasing --n_colors."
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
    return palette, bead_data, p, rag, props

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
    parser.add_argument(
        "-s", "--show_colors", type=int, default=0,
        help="Show each bead's color index and certainty, N entries per line"
    )
    parser.add_argument(
        "-p", "--show_palette", action="store_true",
        help="Generate & display a vertical swatch image of palette colors"
    )
    parser.add_argument(
        "--palette_square_size", type=int, default=50,
        help="Pixel size for each color swatch square"
    )
    parser.add_argument(
        "--exclude_background", action="store_true",
        help="Exclude near-white or grey clusters from the palette and bead_data"
    )
    parser.add_argument(
        "--bg_threshold", type=int, default=250,
        help="RGB threshold above which a centroid is considered background"
    )
    parser.add_argument(
        "--grey_tol", type=int, default=10,
        help="Max‑minus‑min RGB tolerance under which a centroid is considered grey"
    )
    parser.add_argument(
        "--exact_beads_per_row", type=float, default=6.5,
        help="Exact beads_per_row value (default: 6.5)"
    )
    parser.add_argument(
        "--bg_frac", type=float, default=0.05,
        help="Fraction of image area to identify background regions"
    )
    parser.add_argument(
        "--calc_sequence", action="store_true",
        help="Recover bead_index sequence via shortest-path in the pruned RAG"
    )
    args = parser.parse_args()

    paths = glob.glob(args.image_glob)
    if not paths:
        parser.error(f"No files match '{args.image_glob}'")

    for image_path in paths:
        if not os.path.isfile(image_path):
            parser.error(f"File not found: {image_path}")

        palette, bead_data, period, rag, props = iterative_pipeline(
            image_path,
            n_colors=args.n_colors,
            expected_area=args.expected_area,
            max_iters=args.max_iters,
            n_segments=args.n_segments,
            verbose=args.verbose
        )
        # -- optionally filter out background/grey clusters
        if args.exclude_background:
            pal_arr = np.array(palette, dtype=int)
            # detect white‑like centroids
            is_bg   = np.all(pal_arr >= args.bg_threshold, axis=1)
            # detect grey centroids (R≈G≈B)
            is_grey = (pal_arr.max(axis=1) - pal_arr.min(axis=1)) < args.grey_tol
            bad_idxs = set(np.nonzero(is_bg | is_grey)[0])
            keep_idxs = [i for i in range(len(palette)) if i not in bad_idxs]
            # rebuild palette & remap bead_data
            new_palette = [palette[i] for i in keep_idxs]
            idx_map = {old: new for new, old in enumerate(keep_idxs)}
            bead_data = [
                (rid, idx_map[cidx], cert)
                for rid, cidx, cert in bead_data
                if cidx in idx_map
            ]
            palette = new_palette
            print("Filtered palette:", palette)
        print(f"\n=== Results for {image_path} ===")
        print("Recovered palette:", palette)
        print("Pattern length:", period)
        if args.calc_sequence:
            from pattern import prune_between_regions, label_edge_deltas, recover_bead_sequence_by_path
            # identify background regions by area > bg_frac * image_area
            H, W = img.shape[:2]
            img_area = H * W
            bg_labels = {r.label for r in props if r.area > args.bg_frac * img_area}
            if len(bg_labels) != 2:
                warnings.warn(f"[WARN] expected 2 background regions, found {len(bg_labels)}")
            # prune filler regions from RAG
            bead_labels = {lbl for lbl, *_ in bead_data}
            rag2 = prune_between_regions(rag, bead_labels, bg_labels)
            # build centroids map for visible beads
            centroids = {
                r.label: (r.centroid[1], r.centroid[0])
                for r in props if r.label in bead_labels
            }
            # label edge deltas via 3-cluster KMeans
            edge_delta = label_edge_deltas(rag2, centroids, args.exact_beads_per_row)
            # recover full bead_index path
            seq = recover_bead_sequence_by_path(rag2, props, bead_data, img.shape, bg_frac=args.bg_frac)
            print("\nRecovered bead_index sequence (visible beads in order):")
            print(seq)
        # optionally show the palette swatch
        if args.show_palette:
            # build a vertical swatch with margins and horizontal centering
            sw = args.palette_square_size
            margin = sw // 6
            n = len(palette)
            # total height = n squares + (n+1) margins
            h = n * sw + (n + 1) * margin
            # total width = square + left/right margins
            w = sw + 2 * margin
            # white background
            img = np.full((h, w, 3), 255, dtype=np.uint8)
            for i, (r, g, b) in enumerate(palette):
                top = margin + i * (sw + margin)
                left = margin
                # fill square with the palette color (in BGR)
                img[top:top+sw, left:left+sw] = (int(b), int(g), int(r))
            cv2.imshow("Palette Swatch", img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        # optionally show per-bead color & certainty
        if args.show_colors > 0:
            print("\nBead colors & certainty:")
            count = 0
            for _, color_idx, certainty, area in sorted(bead_data):
                print(f"{color_idx}[{area}px]({certainty:.2f})", end=" ")
                count += 1
                if count % args.show_colors == 0:
                    print()
            if count % args.show_colors != 0:
                print()

if __name__ == "__main__":
    main()
