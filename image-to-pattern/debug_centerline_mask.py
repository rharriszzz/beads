"""Interactive HSV range debug tool (wxPython + Matplotlib).

Shows the original image and a mask-derived overlay where masked pixels are white.
As you move the mouse over the image, the x-position is projected onto the
horizontal centerline; the HSV at that centerline pixel defines a base color.
Sliders control symmetric tolerances for H, S, and V. The mask is recomputed
using those ranges.

Usage (from repo root):
  python3.11 image-to-pattern/debug_centerline_mask.py --image beads-photo-2.jpg
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

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
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
import numpy as np
from PIL import Image


class CenterlineMaskFrame(wx.Frame):
    def __init__(self, image_path: Path):
        wx.Frame.__init__(self, None, title=f"Centerline HSV Mask Debug - {image_path.name}", size=(1100, 800))
        self.image_path = image_path
        self.img_rgb = np.array(Image.open(image_path).convert("RGB"))
        self.img_hsv = np.array(Image.open(image_path).convert("HSV"))
        self.h, self.w, _ = self.img_rgb.shape
        self.center_y = self.h // 2
        self.current_hsv: Optional[np.ndarray] = None
        self.mask = np.zeros((self.h, self.w), dtype=bool)

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        panel.SetSizer(sizer)

        # Controls on the left
        ctrl_panel = wx.Panel(panel)
        ctrl_sizer = wx.BoxSizer(wx.VERTICAL)
        ctrl_panel.SetSizer(ctrl_sizer)

        ctrl_sizer.Add(wx.StaticText(ctrl_panel, label="Tolerances (symmetric)"), 0, wx.ALL, 4)
        self.h_slider, self.h_val = self._make_slider(ctrl_panel, "H tol (0-128)", 10, 0, 128, self.on_slider)
        self.s_slider, self.s_val = self._make_slider(ctrl_panel, "S tol (0-128)", 10, 0, 128, self.on_slider)
        self.v_slider, self.v_val = self._make_slider(ctrl_panel, "V tol (0-128)", 10, 0, 128, self.on_slider)
        ctrl_sizer.AddStretchSpacer()
        self.status = wx.StaticText(ctrl_panel, label="Move mouse over image")
        ctrl_sizer.Add(self.status, 0, wx.ALL | wx.EXPAND, 4)

        sizer.Add(ctrl_panel, 0, wx.EXPAND | wx.ALL, 6)

        # Matplotlib figure on the right
        self.fig, (self.ax_orig, self.ax_mask) = plt.subplots(1, 2, figsize=(8, 6))
        self.canvas = FigureCanvasWxAgg(panel, -1, self.fig)
        fig_sizer = wx.BoxSizer(wx.VERTICAL)
        fig_sizer.Add(self.canvas, 1, wx.EXPAND)
        sizer.Add(fig_sizer, 1, wx.EXPAND | wx.ALL, 6)

        # Initial draw
        self.ax_orig.imshow(self.img_rgb)
        self.ax_orig.axhline(self.center_y, color="yellow", linestyle="--", linewidth=1)
        self.ax_orig.set_title("Original")
        self.overlay_img = self.ax_mask.imshow(np.full_like(self.img_rgb, 255, dtype=np.uint8))
        self.ax_mask.set_title("Mask overlay")
        for ax in (self.ax_orig, self.ax_mask):
            ax.axis("off")
        self.canvas.draw()

        # Mouse move handling
        self.cid_motion = self.fig.canvas.mpl_connect("motion_notify_event", self.on_motion)

    def _make_slider(self, parent, label: str, value: int, minv: int, maxv: int, handler):
        box = wx.BoxSizer(wx.VERTICAL)
        row = wx.BoxSizer(wx.HORIZONTAL)
        lbl = wx.StaticText(parent, label=label)
        val_lbl = wx.StaticText(parent, label=str(value))
        row.Add(lbl, 0, wx.ALL, 2)
        row.Add(val_lbl, 0, wx.ALL, 2)
        box.Add(row, 0, wx.ALL, 0)
        slider = wx.Slider(parent, value=value, minValue=minv, maxValue=maxv, style=wx.SL_HORIZONTAL)
        slider.Bind(wx.EVT_SLIDER, handler)
        box.Add(slider, 0, wx.EXPAND | wx.ALL, 2)
        parent.GetSizer().Add(box, 0, wx.EXPAND | wx.ALL, 2)
        return slider, val_lbl

    def on_slider(self, event=None):
        self.update_tol_labels()
        self.update_mask()

    def on_motion(self, event):
        if not event.inaxes or event.xdata is None:
            return
        x = int(round(event.xdata))
        x = max(0, min(self.w - 1, x))
        y = self.center_y
        hsv = self.img_hsv[y, x, :]
        self.current_hsv = hsv
        self.set_status_from_hsv(hsv, x, y)
        self.update_mask()

    def set_status_from_hsv(self, hsv: np.ndarray, x: int, y: int):
        h, s, v = map(int, hsv)
        msg = f"Pos ({x},{y}) centerline HSV=({h},{s},{v})  tol H={self.h_slider.GetValue()} S={self.s_slider.GetValue()} V={self.v_slider.GetValue()}"
        self.status.SetLabel(msg)

    def update_tol_labels(self):
        self.h_val.SetLabel(str(self.h_slider.GetValue()))
        self.s_val.SetLabel(str(self.s_slider.GetValue()))
        self.v_val.SetLabel(str(self.v_slider.GetValue()))

    def update_mask(self):
        if self.current_hsv is None:
            return
        h0, s0, v0 = map(int, self.current_hsv)
        ht = self.h_slider.GetValue()
        st = self.s_slider.GetValue()
        vt = self.v_slider.GetValue()
        hmin, hmax = max(0, h0 - ht), min(255, h0 + ht)
        smin, smax = max(0, s0 - st), min(255, s0 + st)
        vmin, vmax = max(0, v0 - vt), min(255, v0 + vt)
        h = self.img_hsv[:, :, 0]
        s = self.img_hsv[:, :, 1]
        v = self.img_hsv[:, :, 2]
        self.mask = (h >= hmin) & (h <= hmax) & (s >= smin) & (s <= smax) & (v >= vmin) & (v <= vmax)
        overlay = np.full_like(self.img_rgb, 255, dtype=np.uint8)
        if self.mask.any():
            overlay[self.mask] = self.img_rgb[self.mask]
        self.overlay_img.set_data(overlay)
        self.ax_mask.set_title(f"Mask overlay (range H[{hmin}-{hmax}] S[{smin}-{smax}] V[{vmin}-{vmax}])", fontsize=9)
        self.canvas.draw_idle()


def main():
    parser = argparse.ArgumentParser(description="Centerline HSV mask debug tool (wxPython).")
    parser.add_argument("--image", required=True, help="Image file")
    args = parser.parse_args()
    if wx is None:
        raise RuntimeError("wxPython not available; install wxPython for your Python build to run this tool.")
    app = wx.App(False)
    frame = CenterlineMaskFrame(Path(args.image))
    frame.Show()
    app.MainLoop()


if __name__ == "__main__":
    main()
