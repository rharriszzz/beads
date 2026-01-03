"""GUI for annotating bead/background colors via rectangles on an image.

Features
- Load an image and (optionally) an existing JSON config (same format as color_config.md).
- Manage colors (add/edit/delete, set background flag).
- Draw rectangles on the image to sample HSV values for a color.
- Live displays: original image, current color mask, current color overlay, and HSV swatch grid of sampled values.
- Panning/zooming on the image propagates to mask/overlay (shared axes).

Usage
  From repo root:
    XDG_CACHE_HOME=./image-to-pattern/debug-output/mpl-cache \
    MPLCONFIGDIR=./image-to-pattern/debug-output/mpl-cache \
    python3.11 image-to-pattern/color_config_gui.py --image beads-photo-2.jpg [--config beads-photo-2.json]

Env convenience (optional)
- Install direnv (`brew install direnv` or `port install direnv`), add to your shell rc (zsh):
    eval "$(direnv hook zsh)"
- In repo root, .envrc is provided; run `direnv allow` once to auto-set XDG_CACHE_HOME/MPLCONFIGDIR when entering the repo.

Notes
- Requires tkinter + matplotlib (TkAgg backend).
- Saves to the provided config path (or <image>.json if not given).
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import matplotlib

# Prefer TkAgg for interactivity; fall back to Agg in headless/test environments.
try:
    matplotlib.use("TkAgg")
except Exception:
    matplotlib.use("Agg")
import matplotlib.pyplot as plt
try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
except Exception:
    FigureCanvasTkAgg = None
from matplotlib.widgets import RectangleSelector
import numpy as np
try:
    import tkinter as tk
    from tkinter import messagebox, simpledialog
except Exception:
    tk = None
    messagebox = None
    simpledialog = None
from PIL import Image


def rectangles_to_hsv_set(img_hsv: np.ndarray, rectangles: List[List[int]]) -> Set[Tuple[int, int, int]]:
    """Collect HSV tuples from rectangles."""
    h_set: Set[Tuple[int, int, int]] = set()
    hgt, wdt, _ = img_hsv.shape
    for rect in rectangles:
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
            h_set.add(tup)
    return h_set


def mask_from_hsv_set(img_hsv: np.ndarray, hsv_set: Set[Tuple[int, int, int]]) -> np.ndarray:
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


def hsv_swatch_image(hsv_values: List[Tuple[int, int, int]], max_cells: int = 4000) -> np.ndarray:
    """Create an RGB image showing HSV values as a grid of swatches."""
    if not hsv_values:
        return np.ones((10, 10, 3), dtype=float)
    vals = hsv_values[:max_cells]
    n = len(vals)
    cols = int(np.ceil(np.sqrt(n)))
    rows = int(np.ceil(n / cols))
    grid = np.ones((rows, cols, 3), dtype=float)
    for idx, hsv in enumerate(vals):
        r = idx // cols
        c = idx % cols
        hsv_norm = np.array(hsv, dtype=float) / 255.0
        rgb = matplotlib.colors.hsv_to_rgb(hsv_norm)
        grid[r, c, :] = rgb
    return grid


class ColorConfigGUI:
    def __init__(self, image_path: Path, config_path: Optional[Path]):
        if tk is None or FigureCanvasTkAgg is None:
            raise RuntimeError("Tkinter/TkAgg backend not available; GUI cannot run in this environment.")
        self.image_path = image_path
        self.config_path = config_path or image_path.with_suffix(".json")
        self.img_rgb = np.array(Image.open(image_path).convert("RGB"))
        self.img_hsv = np.array(Image.open(image_path).convert("HSV"))
        self.cfg = self.load_config()
        self.current_idx: Optional[int] = 0 if self.cfg["colors"] else None
        self.rect_selector: Optional[RectangleSelector] = None
        self.pending_rects: List[List[int]] = []

        self.root = tk.Tk()
        self.root.title(f"Color Config Editor - {image_path.name}")
        self.build_ui()
        self.update_all()

    def load_config(self) -> Dict:
        if self.config_path.exists():
            with open(self.config_path, "r") as f:
                return json.load(f)
        return {"image_filename": self.image_path.name, "colors": []}

    def save_config(self):
        # Resolve overlaps automatically before saving
        if self.img_hsv is not None:
            try:
                from color_config_editor import resolve_overlaps
            except Exception:
                resolve_overlaps = None
            if resolve_overlaps:
                resolve_overlaps(self.cfg, self.img_hsv, prompt_user=True)
        with open(self.config_path, "w") as f:
            json.dump(self.cfg, f, indent=2)
        messagebox.showinfo("Saved", f"Config saved to {self.config_path}")

    # UI setup
    def build_ui(self):
        # Left control panel
        ctrl = tk.Frame(self.root)
        ctrl.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(ctrl, text="Colors").pack(anchor="w")
        self.listbox = tk.Listbox(ctrl, height=12)
        self.listbox.pack(fill=tk.X)
        self.listbox.bind("<<ListboxSelect>>", self.on_select_color)

        btn_frame = tk.Frame(ctrl)
        btn_frame.pack(fill=tk.X, pady=4)
        tk.Button(btn_frame, text="Add", command=self.add_color).pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Button(btn_frame, text="Edit", command=self.edit_color).pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Button(btn_frame, text="Delete", command=self.delete_color).pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.bg_var = tk.BooleanVar(value=False)
        tk.Checkbutton(ctrl, text="Background", variable=self.bg_var, command=self.set_background_flag).pack(anchor="w")

        tk.Button(ctrl, text="Add Rectangles", command=self.start_rect_mode).pack(fill=tk.X, pady=2)
        tk.Button(ctrl, text="Save Config", command=self.save_config).pack(fill=tk.X, pady=2)
        tk.Button(ctrl, text="Quit", command=self.root.quit).pack(fill=tk.X, pady=2)

        # Figure
        self.fig, axes = plt.subplots(2, 2, figsize=(10, 8))
        self.ax_img = axes[0, 0]
        self.ax_mask = axes[0, 1]
        self.ax_overlay = axes[1, 0]
        self.ax_swatches = axes[1, 1]
        for ax in [self.ax_mask, self.ax_overlay]:
            ax.sharex(self.ax_img)
            ax.sharey(self.ax_img)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Rectangle selector
        self.rect_selector = RectangleSelector(
            self.ax_img,
            self.on_select_rect,
            useblit=True,
            button=[1],
            minspanx=2,
            minspany=2,
            spancoords="pixels",
            interactive=True,
        )
        self.rect_selector.set_active(False)
        self.fig.canvas.mpl_connect("key_press_event", self.on_key_press)

        # Populate listbox
        self.refresh_listbox()

    def refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for c in self.cfg.get("colors", []):
            name = c.get("name", "unnamed")
            bg = c.get("background", False)
            self.listbox.insert(tk.END, f"{name}{' [bg]' if bg else ''}")
        if self.current_idx is not None and 0 <= self.current_idx < self.listbox.size():
            self.listbox.select_set(self.current_idx)

    # Event handlers
    def on_select_color(self, event=None):
        if not self.listbox.curselection():
            self.current_idx = None
            return
        self.current_idx = int(self.listbox.curselection()[0])
        self.bg_var.set(self.cfg["colors"][self.current_idx].get("background", False))
        self.update_all()

    def add_color(self):
        name = simpledialog.askstring("Add Color", "Color name:", parent=self.root)
        if not name:
            return
        bg = messagebox.askyesno("Background", "Is this a background color?", parent=self.root)
        self.cfg.setdefault("colors", []).append({"name": name, "background": bg, "rectangles": []})
        self.current_idx = len(self.cfg["colors"]) - 1
        self.refresh_listbox()
        self.on_select_color()

    def edit_color(self):
        if self.current_idx is None:
            return
        colors = self.cfg["colors"]
        name = simpledialog.askstring("Edit Color", "New name (leave blank to keep):", parent=self.root)
        if name:
            colors[self.current_idx]["name"] = name
        bg_answer = messagebox.askyesno("Background", "Set as background?", parent=self.root)
        colors[self.current_idx]["background"] = bg_answer
        self.refresh_listbox()
        self.on_select_color()

    def delete_color(self):
        if self.current_idx is None:
            return
        colors = self.cfg["colors"]
        if 0 <= self.current_idx < len(colors):
            colors.pop(self.current_idx)
            self.current_idx = None if not colors else 0
            self.refresh_listbox()
            self.on_select_color()

    def set_background_flag(self):
        if self.current_idx is None:
            return
        self.cfg["colors"][self.current_idx]["background"] = bool(self.bg_var.get())
        self.refresh_listbox()

    def on_select_rect(self, eclick, erelease):
        if not self.rect_selector.active:
            return
        x1, y1 = int(eclick.xdata), int(eclick.ydata)
        x2, y2 = int(erelease.xdata), int(erelease.ydata)
        x_min, x_max = sorted([x1, x2])
        y_min, y_max = sorted([y1, y2])
        self.pending_rects.append([x_min, x_max, y_min, y_max])
        self.ax_img.add_patch(
            matplotlib.patches.Rectangle((x_min, y_min), x_max - x_min, y_max - y_min, fill=False, edgecolor="red")
        )
        self.canvas.draw_idle()

    def on_key_press(self, event):
        if event.key == "enter" and self.rect_selector and self.rect_selector.active:
            self.finish_rect_mode()

    def start_rect_mode(self):
        if self.current_idx is None:
            messagebox.showinfo("Select color", "Select a color first.")
            return
        self.pending_rects = []
        self.rect_selector.set_active(True)
        self.ax_img.set_title("Drag to add rectangles; press Enter to finish")
        self.canvas.draw_idle()

    def finish_rect_mode(self):
        if self.current_idx is None:
            return
        colors = self.cfg["colors"]
        colors[self.current_idx].setdefault("rectangles", []).extend(self.pending_rects)
        self.pending_rects = []
        self.rect_selector.set_active(False)
        self.ax_img.set_title("Original")
        self.update_all()

    # Rendering
    def update_all(self):
        self.ax_img.clear()
        self.ax_mask.clear()
        self.ax_overlay.clear()
        self.ax_swatches.clear()

        self.ax_img.imshow(self.img_rgb)
        self.ax_img.set_title("Original")
        mask = None
        hsv_values: List[Tuple[int, int, int]] = []
        if self.current_idx is not None and self.cfg["colors"]:
            color_entry = self.cfg["colors"][self.current_idx]
            hsv_set = rectangles_to_hsv_set(self.img_hsv, color_entry.get("rectangles", []))
            hsv_values = sorted(hsv_set)
            mask = mask_from_hsv_set(self.img_hsv, hsv_set)
            self.ax_mask.imshow(mask, cmap="gray")
            self.ax_mask.set_title(f"Mask: {color_entry.get('name')}")
            overlay = np.full_like(self.img_rgb, 255, dtype=np.uint8)
            if mask.any():
                overlay[mask] = self.img_rgb[mask]
            self.ax_overlay.imshow(overlay)
            self.ax_overlay.set_title("Overlay")
        else:
            self.ax_mask.set_title("Mask (no color selected)")
            self.ax_overlay.set_title("Overlay")

        # Swatches
        swatch_img = hsv_swatch_image(hsv_values, max_cells=2000)
        self.ax_swatches.imshow(swatch_img)
        self.ax_swatches.set_title(f"HSV swatches ({len(hsv_values)} values, capped to 2000)")
        self.ax_swatches.axis("off")

        for ax in [self.ax_img, self.ax_mask, self.ax_overlay]:
            ax.axis("off")
        self.canvas.draw_idle()

    def run(self):
        self.root.mainloop()


def main():
    parser = argparse.ArgumentParser(description="GUI color config editor.")
    parser.add_argument("--image", required=True, help="Image filename")
    parser.add_argument("--config", help="Config JSON path (default: <image>.json)")
    args = parser.parse_args()

    # Ensure Matplotlib cache writable
    mpl_cache = Path("image-to-pattern/debug-output/mpl-cache")
    mpl_cache.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(mpl_cache))
    os.environ.setdefault("XDG_CACHE_HOME", str(mpl_cache))

    gui = ColorConfigGUI(Path(args.image), Path(args.config) if args.config else None)
    gui.run()


if __name__ == "__main__":
    main()
