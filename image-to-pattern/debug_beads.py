"""Debug visualization for bead detection: mask, distance transform, and centers."""

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

from image_to_pattern import segmentation
from image_to_pattern.bead_detect import detect_bead_centers
from image_to_pattern.bead_graph import order_beads_by_mst


def save_overlay(img: Image.Image, centers, radius_px: float, out_path: Path):
    out = img.convert("RGB").copy()
    draw = ImageDraw.Draw(out)
    r = radius_px
    for (x, y) in centers:
        draw.ellipse([x - r, y - r, x + r, y + r], outline=(255, 0, 0), width=2)
        draw.point((x, y), fill=(0, 255, 0))
    out.save(out_path)


def save_distance(dist: np.ndarray, peaks, out_path: Path):
    norm = dist / (dist.max() + 1e-6)
    img = (255 * np.clip(norm, 0, 1)).astype(np.uint8)
    rgb = np.stack([img] * 3, axis=2)
    for (x, y) in peaks:
        xi, yi = int(round(x)), int(round(y))
        if 0 <= yi < rgb.shape[0] and 0 <= xi < rgb.shape[1]:
            rgb[yi, xi] = [255, 0, 0]
    Image.fromarray(rgb).save(out_path)


def main():
    parser = argparse.ArgumentParser(description="Debug bead detection visualization.")
    parser.add_argument("image", type=Path, help="Input image")
    parser.add_argument("--outdir", type=Path, default=Path("image-to-pattern/debug-output"), help="Output directory")
    args = parser.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)
    img = Image.open(args.image).convert("RGB")
    mask = segmentation.mask_bracelet(img)
    geom = segmentation.estimate_geometry(mask)

    dist = ndimage.distance_transform_edt(mask)
    detected = detect_bead_centers(mask, spacing_px=geom.spacing_px)
    ordered = order_beads_by_mst(detected)

    save_overlay(img, ordered.centers, radius_px=geom.radius_px, out_path=args.outdir / f"{args.image.stem}-beads-overlay.png")
    save_distance(dist, ordered.centers, out_path=args.outdir / f"{args.image.stem}-distance.png")
    print(f"Detected {len(ordered.centers)} beads. Outputs written to {args.outdir}")


if __name__ == "__main__":
    main()
