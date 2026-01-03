"""Helpers to load color configs and build masks for manual annotation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Set, Tuple

import numpy as np
from PIL import Image


def load_color_config(path: Path) -> Dict:
    with open(path, "r") as f:
        return json.load(f)


def rectangles_to_hsv_set(img_hsv: np.ndarray, rectangles: List[Dict[str, int]]) -> Set[Tuple[int, int, int]]:
    """Collect HSV tuples from rectangles (list of dicts)."""
    h_set: Set[Tuple[int, int, int]] = set()
    hgt, wdt, _ = img_hsv.shape
    for rect in rectangles:
        if not isinstance(rect, dict):
            continue
        x_min, x_max = int(rect.get("x_min", 0)), int(rect.get("x_max", 0))
        y_min, y_max = int(rect.get("y_min", 0)), int(rect.get("y_max", 0))
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


def rectangles_from_mask(mask: np.ndarray) -> List[List[int]]:
    """Convert a boolean mask to a list of rectangle dicts (runs per row)."""
    rects: List[Dict[str, int]] = []
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
                rects.append({"x_min": x_start, "x_max": x_end, "y_min": y, "y_max": y})
            x += 1
    return rects


def masks_from_config(cfg: Dict, img_rgb: np.ndarray, img_hsv: np.ndarray):
    """Build masks dict and metadata from config + images.

    Returns (masks, color_names, background_names)
    """
    masks: Dict[str, np.ndarray] = {}
    color_names: List[str] = []
    background_names: Set[str] = set()
    for color_entry in cfg.get("colors", []):
        name = color_entry.get("name") or "unnamed"
        color_names.append(name)
        if color_entry.get("background", False):
            background_names.add(name)
        rects = color_entry.get("rectangles", [])
        hsv_set = rectangles_to_hsv_set(img_hsv, rects)
        masks[name] = mask_from_hsv_set(img_hsv, hsv_set)
    # other is implicit; built later if needed
    return masks, color_names, background_names


def combined_bracelet_mask(masks: Dict[str, np.ndarray], color_names: List[str], background_names: Set[str]) -> np.ndarray:
    """Union of all non-background masks."""
    if not masks:
        return np.zeros((1, 1), dtype=bool)
    selected = [name for name in color_names if name in masks and name not in background_names]
    if not selected:
        selected = [name for name in color_names if name in masks]
    if not selected:
        # fall back to any mask
        selected = list(masks.keys())
    union = np.zeros_like(next(iter(masks.values())), dtype=bool)
    for name in selected:
        union |= masks[name]
    return union


def color_indices_from_masks(samples: List, masks: Dict[str, np.ndarray], color_names: List[str], other_name: str = "other") -> List[int]:
    """Assign each sample to a color index based on mask membership at the sample center."""
    indices: List[int] = []
    hgt, wdt = next(iter(masks.values())).shape if masks else (0, 0)
    for s in samples:
        if not hasattr(s, "center") or s.center is None:
            continue
        x, y = s.center
        xi, yi = int(round(x)), int(round(y))
        if not (0 <= xi < wdt and 0 <= yi < hgt):
            continue
        assigned_idx = None
        for idx, name in enumerate(color_names):
            m = masks.get(name)
            if m is not None and m[yi, xi]:
                assigned_idx = idx
                break
        if assigned_idx is None:
            # other
            if other_name in masks:
                idx_other = len(color_names) if other_name not in color_names else color_names.index(other_name)
                assigned_idx = idx_other
            else:
                assigned_idx = len(color_names)
        indices.append(assigned_idx)
    return indices
