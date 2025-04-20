# main.py

import cv2
import numpy as np
from segmentation import slic_superpixels, build_rag, merge_regions, extract_regions
from quantization import fit_color_palette, assign_color_and_certainty
from pattern import autocorrelation_period, minimal_period

def iterative_pipeline(image_path, n_colors, expected_area, max_iters=5):
    img = cv2.imread(image_path)[:,:,::-1]  # BGR → RGB
    # Part 1+2: Integrated Segmentation & Quantization
    segments = slic_superpixels(img)
    rag = build_rag(img, segments)
    labels = merge_regions(img, segments, rag)
    props = extract_regions(labels)

    for _ in range(max_iters):
        palette, kmeans = fit_color_palette(img, props, n_colors)
        labels = merge_regions(img, segments, rag, thresh=20)
        props = extract_regions(labels)

    bead_data = assign_color_and_certainty(img, props, palette, expected_area)

    # Part 3: Pattern Recovery
    color_seq = [cd[1] for cd in sorted(bead_data)]
    periods = autocorrelation_period(color_seq)
    p = minimal_period(color_seq)
    print("Candidate periods:", periods)
    print("Minimal period:", p)
    return palette, bead_data, p

if __name__ == "__main__":
    palette, bead_data, period = iterative_pipeline(
        "beaded-example.jpg", n_colors=3, expected_area=500
    )
    print("Recovered palette:", palette)
    print("Pattern length:", period)
