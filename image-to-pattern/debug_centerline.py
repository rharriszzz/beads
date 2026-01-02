"""Overlay centerline spline on an image for debugging."""

import argparse
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np

from image_to_pattern import segmentation


def main():
    parser = argparse.ArgumentParser(description="Overlay centerline on image.")
    parser.add_argument("image", type=Path, help="Input image")
    parser.add_argument("--outdir", type=Path, default=Path("image-to-pattern/debug-output"), help="Output directory")
    parser.add_argument("--max-dim", type=int, default=1200, help="Resize longest side for speed if larger")
    parser.add_argument("--show-midline", action="store_true", help="Also draw midline between background components")
    args = parser.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)
    img = Image.open(args.image).convert("RGB")
    if max(img.size) > args.max_dim:
        img.thumbnail((args.max_dim, args.max_dim), Image.LANCZOS)
    mask = segmentation.mask_bracelet(img)
    cl = segmentation.centerline_from_mask(mask)
    mid = segmentation.midline_between_background(mask) if args.show_midline else None

    out = img.copy()
    draw = ImageDraw.Draw(out)
    points = list(zip(cl.xs, cl.ys))
    draw.line(points, fill=(255, 0, 0), width=2)
    if mid:
        mid_points = list(zip(mid.xs, mid.ys))
        draw.line(mid_points, fill=(0, 255, 0), width=2)

    out_path = args.outdir / f"{args.image.stem}-centerline.png"
    out.save(out_path)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
