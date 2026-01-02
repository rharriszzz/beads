"""Overlay mask on image: keep masked pixels, invert HSV for others."""

import argparse
from pathlib import Path
import numpy as np
from PIL import Image
from skimage import color

from image_to_pattern import segmentation


def invert_hsv(img_arr):
    hsv = color.rgb2hsv(np.clip(img_arr / 255.0, 0, 1))
    hsv[..., 0] = (hsv[..., 0] + 0.5) % 1.0  # rotate hue
    hsv[..., 1] = 1.0 - hsv[..., 1]  # invert saturation
    hsv[..., 2] = 1.0 - hsv[..., 2]  # invert value
    rgb = color.hsv2rgb(hsv)
    return np.clip(rgb * 255.0, 0, 255).astype(np.uint8)


def main():
    parser = argparse.ArgumentParser(description="Show mask overlay with inverted HSV for background.")
    parser.add_argument("image", type=Path, help="Input image")
    parser.add_argument("--outdir", type=Path, default=Path("image-to-pattern/debug-output"), help="Output directory")
    args = parser.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)
    img = Image.open(args.image).convert("RGB")
    mask = segmentation.mask_bracelet(img)
    img_arr = np.array(img)
    inv = invert_hsv(img_arr)
    out = np.where(mask[..., None], img_arr, inv)
    out_path = args.outdir / f"{args.image.stem}-mask-overlay.png"
    Image.fromarray(out).save(out_path)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
