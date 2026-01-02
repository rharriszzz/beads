"""Minimal interactive color config editor using matplotlib rectangle selection.

Usage:
  python color_config_editor.py --image beads-photo-2.jpg [--config beads-photo-2.json]

Keyboard commands (terminal prompts):
  - l : list colors
  - a : add color
  - e : edit color (rename/background flag)
  - d : delete color
  - r : add rectangles for selected color (draw with mouse; press Enter when done)
  - s : save config
  - q : quit
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List

import matplotlib

# Prefer TkAgg for interactivity; fall back to Agg in headless/test environments.
try:
    matplotlib.use("TkAgg")
except Exception:
    matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
import numpy as np
from PIL import Image


def load_config(path: Path, image_filename: str) -> Dict:
    if path and path.exists():
        with open(path, "r") as f:
            return json.load(f)
    return {"image_filename": image_filename, "colors": []}


def save_config(cfg: Dict, path: Path):
    with open(path, "w") as f:
        json.dump(cfg, f, indent=2)
    print(f"Saved {path}")


def add_color(cfg: Dict, name: str, background: bool):
    cfg["colors"].append({"name": name, "background": background, "rectangles": []})


def list_colors(cfg: Dict):
    for idx, c in enumerate(cfg.get("colors", [])):
        print(f"{idx}: {c.get('name')} (background={c.get('background')}, rects={len(c.get('rectangles', []))})")


def edit_color(cfg: Dict, idx: int, new_name: str = None, new_bg: bool = None):
    colors = cfg.get("colors", [])
    if 0 <= idx < len(colors):
        if new_name is not None:
            colors[idx]["name"] = new_name
        if new_bg is not None:
            colors[idx]["background"] = new_bg


def delete_color(cfg: Dict, idx: int):
    colors = cfg.get("colors", [])
    if 0 <= idx < len(colors):
        colors.pop(idx)


def collect_rectangles(img_rgb: np.ndarray) -> List[List[int]]:
    rects: List[List[int]] = []
    fig, ax = plt.subplots()
    ax.imshow(img_rgb)
    ax.set_title("Drag to draw rectangles, press Enter when done")

    def onselect(eclick, erelease):
        x1, y1 = int(eclick.xdata), int(eclick.ydata)
        x2, y2 = int(erelease.xdata), int(erelease.ydata)
        x_min, x_max = sorted([x1, x2])
        y_min, y_max = sorted([y1, y2])
        rects.append([x_min, x_max, y_min, y_max])
        ax.add_patch(matplotlib.patches.Rectangle((x_min, y_min), x_max - x_min, y_max - y_min, fill=False, edgecolor="red"))
        fig.canvas.draw()

    rect_selector = RectangleSelector(ax, onselect, drawtype="box", useblit=False, button=[1])

    def on_key(event):
        if event.key == "enter":
            plt.close(fig)

    fig.canvas.mpl_connect("key_press_event", on_key)
    plt.show()
    rect_selector.set_active(False)
    return rects


def rectangles_from_mask(mask: np.ndarray) -> List[List[int]]:
    """Convert a boolean mask to a list of rectangles (runs per row)."""
    rects: List[List[int]] = []
    h, w = mask.shape
    for y in range(h):
        row = mask[y]
        x = 0
        while x < w:
            if row[x]:
                x_start = x
                while x < w and row[x]:
                    x += 1
                x_end = x - 1
                rects.append([x_start, x_end, y, y])
            x += 1
    return rects


def mask_from_hsv_set(img_hsv: np.ndarray, hsv_set: set) -> np.ndarray:
    """Fast mask: pixels whose HSV is in hsv_set."""
    if not hsv_set:
        return np.zeros(img_hsv.shape[:2], dtype=bool)
    arr = img_hsv.reshape(-1, 3)
    dtype = np.dtype((np.void, arr.dtype.itemsize * arr.shape[1]))
    arr_view = arr.view(dtype).reshape(-1)
    set_array = np.array(list(hsv_set), dtype=arr.dtype)
    set_view = set_array.view(dtype).reshape(-1)
    hits = np.isin(arr_view, set_view)
    return hits.reshape(img_hsv.shape[:2])


def resolve_overlaps(cfg: Dict, img_hsv: np.ndarray, prompt_user: bool = True):
    """Detect overlapping HSV sets between colors and interactively resolve them.

    If prompt_user is False, overlaps are left as-is.
    """
    colors = cfg.get("colors", [])
    hsv_sets = []
    for c in colors:
        rects = c.get("rectangles", [])
        hsv_set = set()
        hgt, wdt, _ = img_hsv.shape
        for rect in rects:
            if len(rect) != 4:
                continue
            x_min, x_max, y_min, y_max = rect
            x_min = max(0, x_min)
            y_min = max(0, y_min)
            x_max = min(wdt - 1, x_max)
            y_max = min(hgt - 1, y_max)
            if x_min > x_max or y_min > y_max:
                continue
            region = img_hsv[y_min : y_max + 1, x_min : x_max + 1, :]
            flat = region.reshape(-1, 3)
            for tup in map(tuple, flat):
                hsv_set.add(tup)
        hsv_sets.append(hsv_set)

    for i in range(len(colors)):
        for j in range(i + 1, len(colors)):
            overlap = hsv_sets[i].intersection(hsv_sets[j])
            if not overlap:
                continue
            count = len(overlap)
            print(
                f"Overlap between '{colors[i].get('name')}' and '{colors[j].get('name')}' of {count} HSV values."
            )
            if not prompt_user:
                continue
            choice = input(
                "Keep overlap (k, first wins), drop from first (f), drop from second (s), drop from both (b)? [k/f/s/b]: "
            ).strip().lower()
            if choice == "k":
                continue  # first wins, do nothing
            if choice == "f":
                hsv_sets[i] = hsv_sets[i] - overlap
            elif choice == "s":
                hsv_sets[j] = hsv_sets[j] - overlap
            elif choice == "b":
                hsv_sets[i] = hsv_sets[i] - overlap
                hsv_sets[j] = hsv_sets[j] - overlap
            else:
                print("Unknown choice, keeping overlap.")
                continue
            # Rebuild rectangles for affected colors
            for idx in (i, j):
                mask = mask_from_hsv_set(img_hsv, hsv_sets[idx])
                colors[idx]["rectangles"] = rectangles_from_mask(mask)


def main():
    parser = argparse.ArgumentParser(description="Minimal interactive color config editor.")
    parser.add_argument("--image", required=True, help="Image filename")
    parser.add_argument("--config", help="Existing config JSON to load/save", default=None)
    args = parser.parse_args()

    cfg_path = Path(args.config) if args.config else Path(Path(args.image).with_suffix(".json").name)
    cfg = load_config(cfg_path, Path(args.image).name)
    img = Image.open(args.image)
    img_rgb = np.array(img.convert("RGB"))
    img_hsv = np.array(img.convert("HSV"))

    while True:
        cmd = input("(l)ist, (a)dd, (e)dit, (d)elete, add (r)ectangles, (o)verlap resolve, (s)ave, (q)uit: ").strip().lower()
        if cmd == "l":
            list_colors(cfg)
        elif cmd == "a":
            name = input("Color name: ").strip()
            bg = input("Is background? (y/n): ").strip().lower().startswith("y")
            add_color(cfg, name, bg)
        elif cmd == "o":
            resolve_overlaps(cfg, img_hsv)
        elif cmd == "e":
            idx = int(input("Index to edit: "))
            new_name = input("New name (blank to keep): ").strip()
            bg_in = input("Change background? (y/n/blank to keep): ").strip().lower()
            new_bg = None
            if bg_in in ("y", "n"):
                new_bg = bg_in == "y"
            edit_color(cfg, idx, new_name if new_name else None, new_bg)
        elif cmd == "d":
            idx = int(input("Index to delete: "))
            delete_color(cfg, idx)
        elif cmd == "r":
            idx = int(input("Index to add rectangles to: "))
            colors = cfg.get("colors", [])
            if 0 <= idx < len(colors):
                rects = collect_rectangles(img_rgb)
                colors[idx].setdefault("rectangles", []).extend(rects)
        elif cmd == "s":
            save_config(cfg, cfg_path)
        elif cmd == "q":
            break
        else:
            print("Unknown command.")


if __name__ == "__main__":
    main()
