"""Debug: find HS peaks by prominence and save per-peak masks."""

import argparse
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from image_to_pattern import color_peaks, segmentation


def main():
    parser = argparse.ArgumentParser(description="Prominence-based HS peak detection debug.")
    parser.add_argument("image", type=Path, help="Input image")
    parser.add_argument("--prominence", type=float, default=0.05, help="Minimum peak prominence as fraction of max")
    parser.add_argument("--separation", type=float, default=0.05, help="Minimum hue/sat separation")
    parser.add_argument("--top", type=int, default=10, help="Number of peaks to show/keep")
    parser.add_argument("--outdir", type=Path, default=Path("image-to-pattern/debug-output"), help="Output directory")
    args = parser.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)
    img = Image.open(args.image).convert("RGB")
    img_arr = np.array(img)
    mask = segmentation.mask_bracelet(img)
    hsv = color_peaks.hsv_image(img_arr)
    peaks = color_peaks.hs_peaks_with_prominence(
        hsv, mask, min_prominence=args.prominence, min_separation=args.separation
    )
    # Sort by weight and keep top N
    peaks = sorted(peaks, key=lambda p: p[2], reverse=True)[: args.top]
    print("Peaks:", peaks)
    peak_centers = [(h, s) for h, s, _ in peaks]
    masks = color_peaks.build_peak_masks(hsv, mask, peak_centers, radius_h=0.08, radius_s=0.25, radius_v=0.25)
    for i, m in enumerate(masks):
        out = (m.astype(np.uint8) * 255)
        Image.fromarray(out).save(args.outdir / f"{args.image.stem}-peakprom-{i}.png")

    # Create a swatch image showing the peak colors (convert HS to RGB using median V)
    swatch_h = 50
    swatch_w = 200
    swatches = Image.new("RGB", (swatch_w, swatch_h * len(peaks)), color=(255, 255, 255))
    draw = ImageDraw.Draw(swatches)
    for i, (h, s, val) in enumerate(peaks):
        m = masks[i]
        v = float(np.median(hsv[:, :, 2][m])) if m.any() else 0.5
        rgb = np.array(color_peaks.color.hsv2rgb([[(h, s, v)]]))[0, 0]
        color_rgb = tuple(int(float(c) * 255) for c in rgb)
        y0 = i * swatch_h
        draw.rectangle([0, y0, swatch_w, y0 + swatch_h], fill=color_rgb)
        draw.text((5, y0 + 5), f"Peak {i} H={h:.3f} S={s:.3f} size={m.sum()}", fill=(0, 0, 0))
    swatch_path = args.outdir / f"{args.image.stem}-peakprom-swatches.png"
    swatches.save(swatch_path)
    print(f"Saved {len(masks)} masks and swatches to {args.outdir}")


if __name__ == "__main__":
    main()
