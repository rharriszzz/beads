# GUI Testing Checklist for `color_config_gui.py`

Manual steps (headless-friendly rendering uses Agg; Tk requires a display):

1) Launch
- Run `python3.11 image-to-pattern/color_config_gui.py --image beads-photo-2.jpg --config beads-photo-2.json`.
- Verify window opens, image loads, list is empty or shows existing colors.

2) Add color
- Click “Add”, enter a name (e.g., `bg`), choose background flag.
- Confirm color appears in list with `[bg]` marker when background.

3) Edit color
- Select a color, click “Edit”, change name and toggle background, verify list updates.

4) Delete color
- Select a color, click “Delete”, confirm it disappears and selection moves appropriately.

5) Add rectangles
- Select a color, click “Add Rectangles”, drag one or more boxes on the image, press Enter.
- Confirm rectangles draw in red and the mask/overlay update (mask shows white where selected).

6) Mask/overlay sync
- Pan/zoom on the image axes (mouse scroll/drag) and verify mask/overlay axes stay aligned.

7) Swatch grid
- After adding rectangles, check the swatch grid shows colored cells; title reports count.

8) Save/load config
- Click “Save Config” and confirm the JSON file is written.
- Restart the GUI with `--config` pointing to the saved file; verify colors, background flags, and rectangles reload correctly.

9) “Other” handling (via masks generator)
- Run `python3.11 image-to-pattern/color_masks_from_config.py beads-photo-2.json --outdir image-to-pattern/debug-output`.
- Confirm masks/overlays exist for each color plus `other`.

10) Error handling
- Launch with a missing image: confirm a useful error.
- Launch with an invalid JSON: confirm a readable error.

11) Performance sanity
- With multiple rectangles/colors, confirm UI remains responsive and mask updates complete quickly.
