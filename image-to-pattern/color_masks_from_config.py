"""Generate per-color masks and overlays from a color config file."""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from PIL import Image
from image_to_pattern.color_masks import mask_from_rect_ranges


def load_config(path: Path) -> Dict:
    with open(path, "r") as f:
        return json.load(f)


def build_masks(img_hsv: np.ndarray, colors: List[Tuple[str, List[Dict[str, int]]]]) -> Dict[str, np.ndarray]:
    masks = {}
    assigned = np.zeros(img_hsv.shape[:2], dtype=bool)
    for name, rects in colors:
        mask = mask_from_rect_ranges(img_hsv, rects)
        masks[name] = mask
        assigned |= mask
    masks["other"] = ~assigned
    return masks


def masks_from_config(cfg: Dict, img_rgb: np.ndarray, img_hsv: np.ndarray) -> Dict[str, np.ndarray]:
    """Convenience wrapper to build masks dict directly from config + images."""
    colors = []
    for color_entry in cfg.get("colors", []):
        name = color_entry.get("name") or "unnamed"
        rects = color_entry.get("rectangles", [])
        colors.append((name, rects))
    return build_masks(img_hsv, colors)


def save_masks(img_rgb: np.ndarray, masks: Dict[str, np.ndarray], outdir: Path, stem: str):
    for name, mask in masks.items():
        mask_img = (mask.astype(np.uint8) * 255)
        Image.fromarray(mask_img, mode="L").save(outdir / f"{stem}-mask-{name}.png")
        overlay = np.full_like(img_rgb, 255, dtype=np.uint8)
        overlay[mask] = img_rgb[mask]
        Image.fromarray(overlay, mode="RGB").save(outdir / f"{stem}-overlay-{name}.png")


def main():
    parser = argparse.ArgumentParser(description="Generate color masks from a JSON config.")
    parser.add_argument("config", type=Path, help="Path to color config JSON")
    parser.add_argument("--outdir", type=Path, default=Path("image-to-pattern/debug-output"), help="Output directory")
    args = parser.parse_args()

    cfg = load_config(args.config)
    img_path = Path(cfg["image_filename"])
    if not img_path.exists():
        raise FileNotFoundError(f"Image not found: {img_path}")
    img_rgb = np.array(Image.open(img_path).convert("RGB"))
    img_hsv = np.array(Image.open(img_path).convert("HSV"))

    colors = []
    for color_entry in cfg.get("colors", []):
        name = color_entry.get("name") or "unnamed"
        rects = color_entry.get("rectangles", [])
        colors.append((name, rects))

    masks = build_masks(img_hsv, colors)
    args.outdir.mkdir(parents=True, exist_ok=True)
    save_masks(img_rgb, masks, args.outdir, img_path.stem)
    print(f"Saved masks/overlays to {args.outdir}")


if __name__ == "__main__":
    main()
