# Automatic photographic regions — R259

From the repository root:

```bash
.venv/bin/python -m photo2.bead_detection.server
```

Open **http://localhost:8767**. Keep the terminal running; Ctrl+C stops it.
Restart an older server first, or use `--port 8768`. The first launch computes
missing/stale detection data; later launches reuse the saved run. Python 3.12
dependencies are in [requirements.txt](requirements.txt).

The familiar `.venv/bin/python -m photo2.bead_debugger.server` command also opens
this simplified interface. The previous debugger remains available explicitly:
`.venv/bin/python -m photo2.bead_debugger.server --legacy`. Its reviews, historical
models and old controls remain intact and are not loaded by the direct detection
launcher above. The new viewer is read-only.

Drag to pan, scroll to zoom, and click a cyan region. Enter `42` or `R00042` to
jump to a region. Largest/smallest/median and previous/next browse in descending
pixel-count order. The median button chooses the middle ranked region (the lower
of two middle regions for even counts); it need not equal the numeric median.
Click a histogram bar to restrict browsing to that size range; **Clear size filter**
restores all retained regions. Arrow keys browse when the photograph has focus;
F fits the photograph. Optional maxima, selected growth boundary and rejected
regions start hidden. Rejected IDs can also be entered directly.

Black-region growth stops at the **first complete dark perimeter surrounding the
reflection**, following the maker's R259 clarification. Its centroid and pixel
count describe that support region, not the full black bead. This difference
matters when comparing sizes to colored-body proposals.

Download links provide full JSON (including exact pixel runs, rejected candidates,
initial bright patches and provenance), histogram/rank plots and size-rank CSV.
The saved run is under `photo2/output/detection-r259/`; a compressed complete copy
and example figures are committed under [../review/r259](../review/r259/README.md).
IDs are stable within this detector/source/parameter run, not historical bead IDs
or identities guaranteed to persist across algorithm revisions.

Reproduce and validate:

```bash
.venv/bin/python -m photo2.bead_detection.detect
.venv/bin/python -m unittest photo2.bead_detection.test_detection -v
.venv/bin/python -m photo2.bead_detection.validate --isolation
PLAYWRIGHT_BROWSERS_PATH=/tmp/beads-debugger-browsers .venv/bin/python -m photo2.bead_detection.browser_smoke
```

The last command uses the existing optional Playwright/Chromium test installation
documented by the old debugger. No browser package is needed just to launch the
viewer. See the [scientific report](../AUTOMATIC_DETECTION_R259.md) for assumptions,
actual results, limitations and the stopping point.
