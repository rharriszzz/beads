"""Simple CLI to run the pipeline on an image."""

import argparse
from pathlib import Path
from typing import Optional, Sequence

from PIL import Image

from . import pipeline, pov_patterns, segmentation


def parse_palette(case: Optional[int], palette: Optional[Sequence[str]]):
    if case is not None:
        pat = pov_patterns.get_pattern(case)
        # Fall back to basic RGB if palette not defined
        if pat.palette and all(c is not None for c in pat.palette):
            return [tuple(float(x) * 255 for x in c) for c in pat.palette]
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
    parser.add_argument("--case", type=int, help="Assume POV case for palette")
    parser.add_argument("--palette", nargs="+", help="Explicit palette colors as R,G,B triplets")
    parser.add_argument("--spacing", type=float, help="Bead spacing in pixels (auto if omitted)")
    parser.add_argument("--radius", type=float, help="Bead sampling radius in pixels (auto if omitted)")
    parser.add_argument("--offset", type=float, default=0.0, help="Starting offset along centerline")
    parser.add_argument("--brightness-threshold", type=int, default=230, help="Mask threshold (lower is darker)")
    args = parser.parse_args()

    palette_colors = parse_palette(args.case, args.palette)
    img = Image.open(args.image)
    # Build mask once so we can auto-tune geometry if needed.
    mask = segmentation.mask_bracelet(img, brightness_threshold=args.brightness_threshold)
    spacing = args.spacing
    radius = args.radius
    if spacing is None or radius is None:
        geom = segmentation.estimate_geometry(mask)
        spacing = spacing or geom.spacing_px
        radius = radius or geom.radius_px
        print(f"[auto] thickness={geom.thickness_px:.2f}px spacing={spacing:.2f}px radius={radius:.2f}px")

    res = pipeline.infer_pattern(
        img,
        palette_colors=palette_colors,
        spacing_px=spacing,
        radius_px=radius,
        brightness_threshold=args.brightness_threshold,
        offset_px=args.offset,
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
