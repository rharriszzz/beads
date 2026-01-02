"""Simple CLI to run the pipeline on an image."""

import argparse
from pathlib import Path
from typing import Optional, Sequence

from PIL import Image

from . import pipeline, segmentation
from .color_masks import load_color_config, masks_from_config, combined_bracelet_mask
import numpy as np


def parse_palette(case: Optional[int], palette: Optional[Sequence[str]]):
    # We no longer rely on POV patterns for palette inference; case is ignored
    # and only retained for CLI compatibility.
    if palette:
        def parse_color(s: str):
            parts = s.split(",")
            if len(parts) != 3:
                raise argparse.ArgumentTypeError("Palette colors must be R,G,B")
            return tuple(float(p) for p in parts)
        return [parse_color(c) for c in palette]
    # Default basic palette
    return [(255, 0, 0), (0, 255, 0), (0, 0, 255)]


def main():
    parser = argparse.ArgumentParser(description="Run bead image → pattern pipeline.")
    parser.add_argument("image", type=Path, help="Path to input image")
    parser.add_argument("--case", type=int, help="(Deprecated) POV case; ignored for palette inference")
    parser.add_argument("--palette", nargs="+", help="Explicit palette colors as R,G,B triplets")
    parser.add_argument("--spacing", type=float, help="Bead spacing in pixels (auto if omitted)")
    parser.add_argument("--radius", type=float, help="Bead sampling radius in pixels (auto if omitted)")
    parser.add_argument("--expected-beads", type=int, help="If set, derive spacing from centerline length / expected_beads")
    parser.add_argument("--offset", type=float, default=0.0, help="Starting offset along centerline")
    parser.add_argument("--brightness-threshold", type=int, help="Mask threshold (lower is darker); auto if omitted")
    parser.add_argument("--min-coverage", type=float, default=0.3, help="Minimum mask coverage to keep a bead sample")
    parser.add_argument("--detect-beads", action="store_true", help="Use bead detection instead of uniform spacing sampling")
    parser.add_argument("--color-config", type=Path, help="Optional color config JSON (rectangles -> masks)")
    args = parser.parse_args()

    img = Image.open(args.image)
    mask = None
    color_masks = None
    color_names = None
    background_names = set()
    palette_colors = parse_palette(args.case, args.palette)
    if args.color_config:
        cfg = load_color_config(args.color_config)
        if cfg.get("image_filename") and cfg["image_filename"] != str(args.image):
            print(f"[warn] config image_filename {cfg['image_filename']} does not match input {args.image}")
        img_rgb = np.array(img.convert("RGB"))
        img_hsv = np.array(img.convert("HSV"))
        color_masks, color_names, background_names = masks_from_config(cfg, img_rgb, img_hsv)
        mask = combined_bracelet_mask(color_masks, color_names, background_names)
        # when using explicit color masks, palette colors are ignored for index assignment

    # Build mask once so we can auto-tune geometry if needed.
    if mask is None:
        mask = segmentation.mask_bracelet(img, brightness_threshold=args.brightness_threshold)
    spacing = args.spacing
    radius = args.radius
    if spacing is None or radius is None:
        geom = segmentation.estimate_geometry(mask)
        if spacing is None and args.expected_beads:
            from image_to_pattern.sampling import centerline_length

            cl = segmentation.centerline_from_mask(mask)
            arc_len = centerline_length(cl)
            spacing = arc_len / args.expected_beads if args.expected_beads > 0 else geom.spacing_px
        spacing = spacing or geom.spacing_px
        radius = radius or geom.radius_px
        extra = f" (expected_beads={args.expected_beads})" if args.expected_beads else ""
        print(f"[auto] thickness={geom.thickness_px:.2f}px spacing={spacing:.2f}px radius={radius:.2f}px{extra}")

    res = pipeline.infer_pattern(
        img,
        palette_colors=palette_colors,
        spacing_px=spacing,
        radius_px=radius,
        brightness_threshold=args.brightness_threshold,
        offset_px=args.offset,
        min_coverage=args.min_coverage,
        use_bead_detection=args.detect_beads,
        color_masks=color_masks,
        color_names=color_names,
        background_names=background_names,
    )
    print(f"Samples: {len(res.indices)}")
    print(f"Estimated period: {res.period}")
    print(f"Pattern (first period): {res.pattern}")
    # If we know the case, print best match offset/mismatch
    from . import matching

    match = matching.best_pattern_match(res.pattern)
    print(f"Best match: case {match.pattern.case}, offset {match.offset}, match_rate {match.match_rate:.3f}")


if __name__ == "__main__":
    main()
