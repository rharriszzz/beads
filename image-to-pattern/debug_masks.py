"""Debug: save bracelet mask and background mask."""

import argparse
from pathlib import Path
from PIL import Image
import numpy as np

from image_to_pattern import segmentation


def main():
    parser = argparse.ArgumentParser(description="Save bracelet mask and background mask.")
    parser.add_argument("image", type=Path, help="Input image")
    parser.add_argument("--outdir", type=Path, default=Path("image-to-pattern/debug-output"), help="Output directory")
    args = parser.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)
    img = Image.open(args.image).convert("RGB")
    mask = segmentation.mask_bracelet(img)
    mask_img = (mask.astype(np.uint8) * 255)
    bg_img = ((~mask).astype(np.uint8) * 255)
    Image.fromarray(mask_img).save(args.outdir / f"{args.image.stem}-mask.png")
    Image.fromarray(bg_img).save(args.outdir / f"{args.image.stem}-background.png")
    print(f"Saved masks to {args.outdir}")


if __name__ == "__main__":
    main()
