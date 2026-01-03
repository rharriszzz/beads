"""GUI for annotating bead/background colors via rectangles on an image (wxPython + Matplotlib WXAgg).

Features
- Load an image and an optional JSON config (see color_config.md).
- Manage colors (add/edit/delete, background flag).
- Draw rectangles on the image to sample HSV values for a color.
- Live displays: original image, current color mask, current color overlay, HSV swatch grid.

Usage (from repo root)
  python3.11 image-to-pattern/color_config_gui.py --image beads-photo-2.jpg [--config beads-photo-2.json]

Direnv convenience: install direnv, add `eval "$(direnv hook zsh)"` to ~/.zshrc, run `direnv allow` in repo to auto-set cache vars (see .envrc).

Tk/TkAgg is no longer used; this GUI uses wxPython + WXAgg. Ensure wxPython is installed for your Python build.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import matplotlib

try:
    import wx  # type: ignore
except Exception:
    wx = None

if wx:
    matplotlib.use("WXAgg")
else:
    matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
if wx:
    from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg, NavigationToolbar2WxAgg
import numpy as np
from PIL import Image

from image_to_pattern.color_masks import (
    rectangles_to_hsv_set as _rectangles_to_hsv_set,
    mask_from_hsv_set as _mask_from_hsv_set,
    rectangles_from_mask,
    load_color_config,
)


# Re-export helpers for tests/backward compatibility
def rectangles_to_hsv_set(img_hsv: np.ndarray, rectangles: List[List[int]]) -> Set[Tuple[int, int, int]]:
    return _rectangles_to_hsv_set(img_hsv, rectangles)


def mask_from_hsv_set(img_hsv: np.ndarray, hsv_set: Set[Tuple[int, int, int]]) -> np.ndarray:
    return _mask_from_hsv_set(img_hsv, hsv_set)


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


if wx:
    class ColorConfigGUI(wx.Frame):
        def __init__(self, image_path: Path, config_path: Optional[Path]):
            wx.Frame.__init__(self, None, title=f"Color Config Editor - {image_path.name}", size=(1200, 900))
            self.image_path = image_path
            self.config_path = config_path or image_path.with_suffix(".json")
            self.img_rgb = np.array(Image.open(image_path).convert("RGB"))
            self.img_hsv = np.array(Image.open(image_path).convert("HSV"))
            self.cfg = load_color_config(self.config_path) if self.config_path.exists() else {"image_filename": image_path.name, "colors": []}
            self.current_idx: Optional[int] = 0 if self.cfg["colors"] else None
            self.pending_rects: List[List[int]] = []
            self.last_range_values: Optional[List[Tuple[int, int, int]]] = None
            self.last_range_summary: Optional[str] = None
            self.rect_mode: Optional[str] = None
            self.edit_rect_idx: Optional[int] = None

            self.build_ui()
            self.update_all()

        def build_ui(self):
            panel = wx.Panel(self)
            sizer = wx.BoxSizer(wx.HORIZONTAL)
            panel.SetSizer(sizer)

            # Left controls
            ctrl_panel = wx.Panel(panel)
            ctrl_sizer = wx.BoxSizer(wx.VERTICAL)
            ctrl_panel.SetSizer(ctrl_sizer)

            ctrl_sizer.Add(wx.StaticText(ctrl_panel, label="Colors"), 0, wx.ALL, 4)
            self.listbox = wx.ListBox(ctrl_panel)
            self.listbox.Bind(wx.EVT_LISTBOX, self.on_select_color)
            ctrl_sizer.Add(self.listbox, 0, wx.EXPAND | wx.ALL, 4)

            grid = wx.GridSizer(3, 3, 4, 4)
            add_btn = wx.Button(ctrl_panel, label="Add Color")
            edit_btn = wx.Button(ctrl_panel, label="Edit Color")
            del_btn = wx.Button(ctrl_panel, label="Delete Color")
            rect_btn = wx.Button(ctrl_panel, label="Add Rect")
            edit_rect_btn = wx.Button(ctrl_panel, label="Edit Rect")
            del_rect_btn = wx.Button(ctrl_panel, label="Delete Rect")
            save_btn = wx.Button(ctrl_panel, label="Save")
            quit_btn = wx.Button(ctrl_panel, label="Quit")
            for b in [add_btn, edit_btn, del_btn, rect_btn, save_btn, quit_btn]:
                grid.Add(b, 0, wx.EXPAND)
            for b in [edit_rect_btn, del_rect_btn]:
                grid.Add(b, 0, wx.EXPAND)
            ctrl_sizer.Add(grid, 0, wx.EXPAND | wx.ALL, 4)
            add_btn.Bind(wx.EVT_BUTTON, self.add_color)
            edit_btn.Bind(wx.EVT_BUTTON, self.edit_color)
            del_btn.Bind(wx.EVT_BUTTON, self.delete_color)
            rect_btn.Bind(wx.EVT_BUTTON, self.start_add_rect)
            edit_rect_btn.Bind(wx.EVT_BUTTON, self.start_edit_rect)
            del_rect_btn.Bind(wx.EVT_BUTTON, self.delete_rect)
            save_btn.Bind(wx.EVT_BUTTON, self.save_config)
            quit_btn.Bind(wx.EVT_BUTTON, lambda evt: self.Close())

            self.bg_checkbox = wx.CheckBox(ctrl_panel, label="Background")
            self.bg_checkbox.Bind(wx.EVT_CHECKBOX, self.set_background_flag)
            ctrl_sizer.Add(self.bg_checkbox, 0, wx.ALL, 4)

            ctrl_sizer.Add(wx.StaticText(ctrl_panel, label="Rectangles"), 0, wx.ALL, 4)
            self.rect_list = wx.ListBox(ctrl_panel)
            self.rect_list.Bind(wx.EVT_LISTBOX, self.on_select_rect_list)
            ctrl_sizer.Add(self.rect_list, 0, wx.EXPAND | wx.ALL, 4)

            self.status = wx.StaticText(ctrl_panel, label="")
            status_font = self.status.GetFont()
            status_font.PointSize = max(status_font.PointSize - 2, 8)
            self.status.SetFont(status_font)
            ctrl_sizer.Add(self.status, 0, wx.ALL | wx.EXPAND, 4)

            sizer.Add(ctrl_panel, 0, wx.EXPAND | wx.ALL, 4)

            # Figure
            self.fig, axes = plt.subplots(2, 2, figsize=(8, 6))
            self.ax_img = axes[0, 0]
            self.ax_mask = axes[0, 1]
            self.ax_overlay = axes[1, 0]
            self.ax_swatches = axes[1, 1]
            for ax in [self.ax_mask, self.ax_overlay]:
                ax.sharex(self.ax_img)
                ax.sharey(self.ax_img)
            self.canvas = FigureCanvasWxAgg(panel, -1, self.fig)
            fig_sizer = wx.BoxSizer(wx.VERTICAL)
            # Custom pan/zoom buttons (no save)
            tool_row = wx.BoxSizer(wx.HORIZONTAL)
            pan_btn = wx.Button(panel, label="Pan/Zoom On")
            pan_btn.SetToolTip("Left-drag to pan, scroll to zoom")
            pan_off_btn = wx.Button(panel, label="Pan/Zoom Off")
            reset_btn = wx.Button(panel, label="Reset View")
            zoom_in_btn = wx.Button(panel, label="Zoom In")
            zoom_out_btn = wx.Button(panel, label="Zoom Out")
            pan_l_btn = wx.Button(panel, label="Pan Left")
            pan_r_btn = wx.Button(panel, label="Pan Right")
            pan_u_btn = wx.Button(panel, label="Pan Up")
            pan_d_btn = wx.Button(panel, label="Pan Down")
            tool_row.Add(pan_btn, 0, wx.ALL, 2)
            tool_row.Add(pan_off_btn, 0, wx.ALL, 2)
            tool_row.Add(reset_btn, 0, wx.ALL, 2)
            tool_row.Add(zoom_in_btn, 0, wx.ALL, 2)
            tool_row.Add(zoom_out_btn, 0, wx.ALL, 2)
            tool_row.Add(pan_l_btn, 0, wx.ALL, 2)
            tool_row.Add(pan_r_btn, 0, wx.ALL, 2)
            tool_row.Add(pan_u_btn, 0, wx.ALL, 2)
            tool_row.Add(pan_d_btn, 0, wx.ALL, 2)
            pan_btn.Bind(wx.EVT_BUTTON, lambda evt: self.toggle_nav(True))
            pan_off_btn.Bind(wx.EVT_BUTTON, lambda evt: self.toggle_nav(False))
            reset_btn.Bind(wx.EVT_BUTTON, lambda evt: self.reset_view())
            zoom_in_btn.Bind(wx.EVT_BUTTON, lambda evt: self.zoom(factor=0.8))
            zoom_out_btn.Bind(wx.EVT_BUTTON, lambda evt: self.zoom(factor=1.25))
            pan_l_btn.Bind(wx.EVT_BUTTON, lambda evt: self.pan(dx_frac=-0.1, dy_frac=0))
            pan_r_btn.Bind(wx.EVT_BUTTON, lambda evt: self.pan(dx_frac=0.1, dy_frac=0))
            pan_u_btn.Bind(wx.EVT_BUTTON, lambda evt: self.pan(dx_frac=0, dy_frac=-0.1))
            pan_d_btn.Bind(wx.EVT_BUTTON, lambda evt: self.pan(dx_frac=0, dy_frac=0.1))
            fig_sizer.Add(tool_row, 0, wx.EXPAND)
            fig_sizer.Add(self.canvas, 1, wx.EXPAND)
            sizer.Add(fig_sizer, 1, wx.EXPAND | wx.ALL, 4)

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

            self.refresh_listbox()
            self.refresh_rect_list()
            panel.Layout()
            self.Layout()

        def refresh_listbox(self):
            self.listbox.Clear()
            for c in self.cfg.get("colors", []):
                name = c.get("name", "unnamed")
                bg = c.get("background", False)
                self.listbox.Append(f"{name}{' [bg]' if bg else ''}")
            if self.current_idx is not None and 0 <= self.current_idx < self.listbox.GetCount():
                self.listbox.SetSelection(self.current_idx)
            self.refresh_rect_list()

        def on_select_color(self, event=None):
            if self.listbox.GetSelection() == wx.NOT_FOUND:
                self.current_idx = None
                return
            self.current_idx = self.listbox.GetSelection()
            self.bg_checkbox.SetValue(self.cfg["colors"][self.current_idx].get("background", False))
            self.update_all()
            self.refresh_rect_list()

        def refresh_rect_list(self):
            self.rect_list.Clear()
            if self.current_idx is None or not self.cfg.get("colors"):
                return
            rects = self.cfg["colors"][self.current_idx].get("rectangles", [])
            for idx, r in enumerate(rects):
                desc = f"{idx}: x[{r.get('x_min')}..{r.get('x_max')}] y[{r.get('y_min')}..{r.get('y_max')}]"
                if all(k in r for k in ("h_min", "h_max", "s_min", "s_max", "v_min", "v_max")):
                    desc += f" H[{r['h_min']}-{r['h_max']}] S[{r['s_min']}-{r['s_max']}] V[{r['v_min']}-{r['v_max']}]"
                self.rect_list.Append(desc)

        def on_select_rect_list(self, event=None):
            pass

        def add_color(self, event=None):
            dlg = wx.TextEntryDialog(self, "Color name:", "Add Color")
            if dlg.ShowModal() != wx.ID_OK:
                return
            name = dlg.GetValue().strip()
            dlg.Destroy()
            if not name:
                return
            bg = wx.MessageBox("Is this a background color?", "Background", wx.YES_NO | wx.ICON_QUESTION) == wx.YES
            self.cfg.setdefault("colors", []).append({"name": name, "background": bg, "rectangles": []})
            self.current_idx = len(self.cfg["colors"]) - 1
            self.refresh_listbox()
            self.on_select_color()

        def edit_color(self, event=None):
            if self.current_idx is None:
                return
            colors = self.cfg["colors"]
            dlg = wx.TextEntryDialog(self, "New name (leave blank to keep):", "Edit Color")
            if dlg.ShowModal() == wx.ID_OK:
                new_name = dlg.GetValue().strip()
                if new_name:
                    colors[self.current_idx]["name"] = new_name
            dlg.Destroy()
            bg_choice = wx.MessageBox("Set as background?", "Background", wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
            if bg_choice in (wx.YES, wx.NO):
                colors[self.current_idx]["background"] = (bg_choice == wx.YES)
            self.refresh_listbox()
            self.on_select_color()

        def delete_color(self, event=None):
            if self.current_idx is None:
                return
            colors = self.cfg["colors"]
            if 0 <= self.current_idx < len(colors):
                colors.pop(self.current_idx)
                self.current_idx = None if not colors else 0
                self.refresh_listbox()
                self.on_select_color()

        def set_background_flag(self, event=None):
            if self.current_idx is None:
                return
            self.cfg["colors"][self.current_idx]["background"] = bool(self.bg_checkbox.GetValue())
            self.refresh_listbox()

        def on_select_rect(self, eclick, erelease):
            if not self.rect_selector.active:
                return
            x1, y1 = int(eclick.xdata), int(eclick.ydata)
            x2, y2 = int(erelease.xdata), int(erelease.ydata)
            x_min, x_max = sorted([x1, x2])
            y_min, y_max = sorted([y1, y2])
            self.pending_rects.append({"x_min": x_min, "x_max": x_max, "y_min": y_min, "y_max": y_max})
            self.ax_img.add_patch(
                matplotlib.patches.Rectangle((x_min, y_min), x_max - x_min, y_max - y_min, fill=False, edgecolor="red")
            )
            self.canvas.draw()

        def toggle_nav(self, enable: bool):
            nav = self.canvas.toolbar
            if nav:
                nav.pan() if enable else nav.pan()
                nav.zoom() if enable else nav.zoom()

        def reset_view(self):
            nav = self.canvas.toolbar
            if nav:
                nav.home(None)

        def set_status(self, msg: str):
            self.status.SetLabel(msg)

        def _sync_limits(self, xlim, ylim):
            for ax in [self.ax_img, self.ax_mask, self.ax_overlay]:
                ax.set_xlim(xlim)
                ax.set_ylim(ylim)
            self.canvas.draw()

        def zoom(self, factor: float):
            """Zoom relative to current view; factor <1 zooms in, >1 zooms out."""
            ax = self.ax_img
            x0, x1 = ax.get_xlim()
            y0, y1 = ax.get_ylim()
            cx = 0.5 * (x0 + x1)
            cy = 0.5 * (y0 + y1)
            width = (x1 - x0) * factor
            height = (y1 - y0) * factor
            new_xlim = (cx - 0.5 * width, cx + 0.5 * width)
            new_ylim = (cy - 0.5 * height, cy + 0.5 * height)
            self._sync_limits(new_xlim, new_ylim)

        def pan(self, dx_frac: float, dy_frac: float):
            """Pan by fraction of current view width/height."""
            ax = self.ax_img
            x0, x1 = ax.get_xlim()
            y0, y1 = ax.get_ylim()
            dx = (x1 - x0) * dx_frac
            dy = (y1 - y0) * dy_frac
            new_xlim = (x0 + dx, x1 + dx)
            new_ylim = (y0 + dy, y1 + dy)
            self._sync_limits(new_xlim, new_ylim)

        def on_key_press(self, event):
            if event.key == "enter" and self.rect_selector and self.rect_selector.active:
                self.finish_rect_mode()

        def start_add_rect(self, event=None):
            if self.current_idx is None:
                wx.MessageBox("Select a color first.", "Info")
                return
            self.pending_rects = []
            self.rect_mode = "add"
            self.edit_rect_idx = None
            self.rect_selector.set_active(True)
            self.set_status("Drag one rectangle; press Enter to finish")
            self.canvas.draw()

        def start_edit_rect(self, event=None):
            if self.current_idx is None:
                wx.MessageBox("Select a color first.", "Info")
                return
            sel = self.rect_list.GetSelection()
            if sel == wx.NOT_FOUND:
                wx.MessageBox("Select a rectangle to edit.", "Info")
                return
            self.pending_rects = []
            self.rect_mode = "edit"
            self.edit_rect_idx = sel
            self.rect_selector.set_active(True)
            self.set_status("Drag replacement rect; press Enter to finish")
            self.canvas.draw()

        def delete_rect(self, event=None):
            if self.current_idx is None or not self.cfg.get("colors"):
                return
            sel = self.rect_list.GetSelection()
            if sel == wx.NOT_FOUND:
                wx.MessageBox("Select a rectangle to delete.", "Info")
                return
            rects = self.cfg["colors"][self.current_idx].get("rectangles", [])
            if 0 <= sel < len(rects):
                rects.pop(sel)
                self.refresh_rect_list()
                self.update_all()

        def finish_rect_mode(self):
            if self.current_idx is None:
                return
            colors = self.cfg["colors"]
            rects = colors[self.current_idx].setdefault("rectangles", [])
            # Summarize HSV range for the added rect(s)
            if self.pending_rects:
                hmins, hmaxs, smins, smaxs, vmins, vmaxs = [], [], [], [], [], []
                values: List[Tuple[int, int, int]] = []
                for rect in self.pending_rects:
                    x_min, x_max = rect["x_min"], rect["x_max"]
                    y_min, y_max = rect["y_min"], rect["y_max"]
                    region = self.img_hsv[y_min : y_max + 1, x_min : x_max + 1, :]
                    hmins.append(int(region[:, :, 0].min()))
                    hmaxs.append(int(region[:, :, 0].max()))
                    smins.append(int(region[:, :, 1].min()))
                    smaxs.append(int(region[:, :, 1].max()))
                    vmins.append(int(region[:, :, 2].min()))
                    vmaxs.append(int(region[:, :, 2].max()))
                    uniq = np.unique(region.reshape(-1, 3), axis=0)
                    values.extend([tuple(map(int, u)) for u in uniq])
                hmin, hmax = min(hmins), max(hmaxs)
                smin, smax = min(smins), max(smaxs)
                vmin, vmax = min(vmins), max(vmaxs)
                self.last_range_summary = f"H {hmin}-{hmax} S {smin}-{smax} V {vmin}-{vmax}"
                self.last_range_values = values
                for idx in range(len(self.pending_rects)):
                    self.pending_rects[idx].update(
                        {"h_min": hmin, "h_max": hmax, "s_min": smin, "s_max": smax, "v_min": vmin, "v_max": vmax}
                    )
                self.set_status(f"Last rect HSV ranges: {self.last_range_summary}")
                if self.rect_mode == "edit" and self.edit_rect_idx is not None and 0 <= self.edit_rect_idx < len(rects):
                    rects[self.edit_rect_idx] = self.pending_rects[0]
                else:
                    rects.extend(self.pending_rects)
            self.pending_rects = []
            self.rect_selector.set_active(False)
            self.rect_mode = None
            self.edit_rect_idx = None
            self.update_all()
            self.refresh_rect_list()

        def resolve_overlaps_gui(self):
            colors = self.cfg.get("colors", [])
            hsv_sets = []
            for c in colors:
                rects = c.get("rectangles", [])
                hsv_sets.append(rectangles_to_hsv_set(self.img_hsv, rects))
            for i in range(len(colors)):
                for j in range(i + 1, len(colors)):
                    overlap = hsv_sets[i].intersection(hsv_sets[j])
                    if not overlap:
                        continue
                    count = len(overlap)
                    choices = ["Keep (first wins)", "Drop from first", "Drop from second", "Drop from both"]
                    dlg = wx.SingleChoiceDialog(
                        self,
                        f"Overlap between '{colors[i].get('name')}' and '{colors[j].get('name')}' ({count} HSV values). Choose resolution:",
                        "Resolve Overlap",
                        choices,
                    )
                    if dlg.ShowModal() != wx.ID_OK:
                        dlg.Destroy()
                        continue
                    sel = dlg.GetSelection()
                    dlg.Destroy()
                    if sel == 1:
                        hsv_sets[i] = hsv_sets[i] - overlap
                    elif sel == 2:
                        hsv_sets[j] = hsv_sets[j] - overlap
                    elif sel == 3:
                        hsv_sets[i] = hsv_sets[i] - overlap
                        hsv_sets[j] = hsv_sets[j] - overlap
                    for idx in (i, j):
                        mask = mask_from_hsv_set(self.img_hsv, hsv_sets[idx])
                        colors[idx]["rectangles"] = rectangles_from_mask(mask)

        def save_config(self, event=None):
            if wx:
                self.resolve_overlaps_gui()
            with open(self.config_path, "w") as f:
                json.dump(self.cfg, f, indent=2)
            wx.MessageBox(f"Config saved to {self.config_path}", "Saved")

        def update_all(self):
            title_kwargs = {"fontsize": 8}
            self.ax_img.clear()
            self.ax_mask.clear()
            self.ax_overlay.clear()
            self.ax_swatches.clear()

            self.ax_img.imshow(self.img_rgb)
            self.ax_img.set_title("Original", **title_kwargs)
            mask = None
            hsv_values: List[Tuple[int, int, int]] = []
            if self.current_idx is not None and self.cfg["colors"]:
                color_entry = self.cfg["colors"][self.current_idx]
                hsv_set = rectangles_to_hsv_set(self.img_hsv, color_entry.get("rectangles", []))
                hsv_values = sorted(hsv_set)
                mask = mask_from_hsv_set(self.img_hsv, hsv_set)
                self.ax_mask.imshow(mask, cmap="gray")
                self.ax_mask.set_title(f"Mask: {color_entry.get('name')}", **title_kwargs)
                overlay = np.full_like(self.img_rgb, 255, dtype=np.uint8)
                if mask.any():
                    overlay[mask] = self.img_rgb[mask]
                self.ax_overlay.imshow(overlay)
                self.ax_overlay.set_title("Overlay", **title_kwargs)
                # draw rectangles overlay
                for r in color_entry.get("rectangles", []):
                    x_min, x_max = r.get("x_min", 0), r.get("x_max", 0)
                    y_min, y_max = r.get("y_min", 0), r.get("y_max", 0)
                    rect_patch = matplotlib.patches.Rectangle(
                        (x_min, y_min), x_max - x_min, y_max - y_min, fill=False, edgecolor="lime", linewidth=1
                    )
                    self.ax_img.add_patch(rect_patch)
                    self.ax_overlay.add_patch(
                        matplotlib.patches.Rectangle(
                            (x_min, y_min), x_max - x_min, y_max - y_min, fill=False, edgecolor="lime", linewidth=1
                        )
                    )
            else:
                self.ax_mask.set_title("Mask (no color selected)", **title_kwargs)
                self.ax_overlay.set_title("Overlay", **title_kwargs)

            swatch_source = self.last_range_values if self.last_range_values is not None else hsv_values
            swatch_img = hsv_swatch_image(swatch_source, max_cells=2000)
            self.ax_swatches.imshow(swatch_img)
            title_suffix = f"{'range' if self.last_range_values is not None else 'vals'}"
            self.ax_swatches.set_title(f"HSV ({len(swatch_source)} {title_suffix}, cap 2000)", **title_kwargs)
            self.ax_swatches.axis("off")

            for ax in [self.ax_img, self.ax_mask, self.ax_overlay]:
                ax.axis("off")
            self.canvas.draw()


def main():
    parser = argparse.ArgumentParser(description="GUI color config editor (wxPython).")
    parser.add_argument("--image", required=True, help="Image filename")
    parser.add_argument("--config", help="Config JSON path (default: <image>.json)")
    args = parser.parse_args()

    # Ensure Matplotlib cache writable
    mpl_cache = Path("image-to-pattern/debug-output/mpl-cache")
    mpl_cache.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(mpl_cache))
    os.environ.setdefault("XDG_CACHE_HOME", str(mpl_cache))

    if wx is None:
        raise RuntimeError("wxPython not available; install wxPython for your Python build to run the GUI.")
    app = wx.App(False)
    gui = ColorConfigGUI(Path(args.image), Path(args.config) if args.config else None)
    gui.Show()
    app.MainLoop()


if __name__ == "__main__":
    main()
