# Setup Guide

## Prerequisites
- Python 3.11 (used for tests/CLI here).
- pip (`python3.11 -m ensurepip` if missing).
- (Optional) virtual environment if you prefer isolation.
- Matplotlib cache paths should be writable to avoid fontconfig warnings.

## Install dependencies
From repo root:
```
python3.11 -m pip install -r image-to-pattern/requirements.txt
```
If using a venv:
```
python3.11 -m venv .venv
source .venv/bin/activate
python3.11 -m pip install -r image-to-pattern/requirements.txt
```

## Environment (Matplotlib cache)
To avoid font cache warnings, set:
```
export XDG_CACHE_HOME=$PWD/image-to-pattern/debug-output/mpl-cache
export MPLCONFIGDIR=$PWD/image-to-pattern/debug-output/mpl-cache
```
You can add these to your shell rc or use `direnv` with a `.envrc`.

## Running the pipeline CLI
From repo root:
```
python3.11 image-to-pattern/image_to_pattern/cli.py --image beads-photo-2.jpg \
  --expected-beads 672 \
  --color-config beads-photo-2.json
```
- `--color-config` (optional) uses manual masks/annotations.
- If omitted, palette inference/k-means path is used (not recommended).
- Spacing/radius auto-tune from geometry unless provided.

## Manual color annotation
### GUI (Tk + matplotlib)
```
XDG_CACHE_HOME=./image-to-pattern/debug-output/mpl-cache \
MPLCONFIGDIR=./image-to-pattern/debug-output/mpl-cache \
python3.11 image-to-pattern/color_config_gui.py --image beads-photo-2.jpg --config beads-photo-2.json
```
- Manage colors, draw rectangles, preview mask/overlay, swatches.
- Save to JSON; overlaps are checked on save.

### Terminal editor
```
python3.11 image-to-pattern/color_config_editor.py --image beads-photo-2.jpg --config beads-photo-2.json
```
- Menu-driven; draw rectangles in a matplotlib window.
- Optional overlap resolution command `(o)`.

### Generate masks/overlays from config
```
python3.11 image-to-pattern/color_masks_from_config.py beads-photo-2.json --outdir image-to-pattern/debug-output
```
- Writes per-color mask PNGs and overlays (`other` mask included).

## Tests
Run the full suite:
```
python3.11 -m unittest discover -s image-to-pattern/tests
```

## Notes / gotchas
- k-means color detection performs poorly on these images (merges bead colors with background); prefer manual masks or histogram/peak-based methods.
- GUI requires Tk; if unavailable, use the terminal editor and mask generator.
- Use the Matplotlib cache env vars for quiet, reliable runs.

## Tk/Tkinter setup for GUI
- The GUI (`color_config_gui.py`) needs a Python build with Tk support. If you see `RuntimeError: Tkinter/TkAgg backend not available`, install Tkinter for your Python:
  - MacPorts: `sudo port install py311-tkinter` (matching your Python version).
  - Homebrew Python usually bundles Tk; if not, reinstall `python@3.11` or `python-tk@3.11`.
- Recreate venv (if used) with the Tk-enabled Python:
  ```
  rm -rf .venv
  python3.11 -m venv .venv
  source .venv/bin/activate
  python3.11 -m pip install -r image-to-pattern/requirements.txt
  ```
- Verify Tk works:
  ```
  python3.11 - <<'PY'
  import tkinter
  print("Tk OK:", tkinter.TkVersion)
  PY
  ```
- If Tk isn’t available, use the terminal editor (`color_config_editor.py`) and `color_masks_from_config.py`.
