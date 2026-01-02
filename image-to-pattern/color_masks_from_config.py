"""Generate per-color masks and overlays from a color config file."""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from PIL import Image


def load_config(path: Path) -> Dict:
    with open(path, "r") as f:
        return json.load(f)


def rectangles_to_hsv_set(img_hsv: np.ndarray, rectangles: List[List[int]]) -> set:
    h_set = set()
    for rect in rectangles:
        if len(rect) != 4:
            continue
        x_min, x_max, y_min, y_max = rect
        x_min = max(0, x_min)
        y_min = max(0, y_min)
        x_max = min(img_hsv.shape[1] - 1, x_max)
        y_max = min(img_hsv.shape[0] - 1, y_max)
        if x_min > x_max or y_min > y_max:
            continue
        region = img_hsv[y_min : y_max + 1, x_min : x_max + 1, :]
        flat = region.reshape(-1, 3)
        for tup in map(tuple, flat):
            h_set.add(tup)
    return h_set


def build_masks(img_hsv: np.ndarray, color_sets: List[Tuple[str, set]]) -> Dict[str, np.ndarray]:
    h, w, _ = img_hsv.shape
    masks = {}
    flat = img_hsv.reshape(-1, 3)
    assigned = np.zeros(flat.shape[0], dtype=bool)
    for name, hsv_set in color_sets:
        hits = np.array([tuple(px) in hsv_set for px in flat], dtype=bool)
        mask = hits.reshape(h, w)
        masks[name] = mask
        assigned |= hits
    masks["other"] = (~assigned).reshape(h, w)
    return masks


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

    color_sets = []
    for color_entry in cfg.get("colors", []):
        name = color_entry.get("name") or "unnamed"
        rects = color_entry.get("rectangles", [])
        hsv_set = rectangles_to_hsv_set(img_hsv, rects)
        color_sets.append((name, hsv_set))

    masks = build_masks(img_hsv, color_sets)
    args.outdir.mkdir(parents=True, exist_ok=True)
    save_masks(img_rgb, masks, args.outdir, img_path.stem)
    print(f"Saved masks/overlays to {args.outdir}")


if __name__ == "__main__":
    main()
