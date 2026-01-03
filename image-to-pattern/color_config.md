Color annotation file format (per image)
----------------------------------------

- Store alongside the image; same basename, different extension (e.g., `beads-photo-2.json` for `beads-photo-2.jpg`).
- JSON structure:
```json
{
  "image_filename": "beads-photo-2.jpg",
  "colors": [
    {
      "name": "background",
      "background": true,
      "rectangles": [
        {
          "x_min": 0,
          "x_max": 10,
          "y_min": 0,
          "y_max": 5,
          "h_min": 200,
          "h_max": 220,
          "s_min": 10,
          "s_max": 30,
          "v_min": 180,
          "v_max": 210
        }
      ]
    },
    {
      "name": "red",
      "background": false,
      "rectangles": [...]
    }
  ]
}
```
- Rectangles are objects with fields:
  - `x_min`, `x_max`, `y_min`, `y_max`: integers (pixel indices, 0-based inclusive).
  - Optional `h_min`, `h_max`, `s_min`, `s_max`, `v_min`, `v_max`: summary of HSV range for that rect (auto-added by GUI).
- Semantics: collect all HSV values from each rectangle for a color; any pixel whose HSV matches any of those values is assigned that color. Pixels matching no color are assigned the implicit color `"other"`.
- Coordinate system: pixel indices into the image (0-based), inclusive ranges for x and y.

Tools
-----
- `color_masks_from_config.py CONFIG.json --outdir image-to-pattern/debug-output`
  - Reads the config, loads the image, builds per-color masks and an `"other"` mask.
  - Writes `<image>-mask-<color>.png` (white=True, black=False) and `<image>-overlay-<color>.png` (original pixels where mask is true, white elsewhere).
- `color_config_editor.py --image beads-photo-2.jpg [--config beads-photo-2.json]`
  - Minimal interactive editor (matplotlib) to add/delete colors, mark rectangles, and save the JSON. Use keyboard prompts in the terminal; draw rectangles with click-and-drag.
