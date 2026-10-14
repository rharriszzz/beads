# R282 integrated reconstruction

[Specification](../R282_SPECIFICATION.md), [requirement checklist](../R282_CHECKLIST.md),
[results report](../R282_INTEGRATED.md), [static review browser](../review/r282/index.html).

Run from repository root with Python3.12 `.venv`. Dependencies are the existing
NumPy/SciPy/scikit-image/Pillow/matplotlib environment; appearance checks use POV-Ray,
and browser checks use Playwright Chromium. No historical model fit is loaded.

```bash
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r282.tests
R282_OUTPUT=/tmp/beads-r282-replay OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r282.run
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r282.audit
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r282.pov
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/beads-r282-mpl .venv/bin/python -m photo2.r282.review
PLAYWRIGHT_BROWSERS_PATH=/tmp/beads-debugger-browsers .venv/bin/python -m photo2.r282.browser_check
```

The run target must be fresh: completed runs are deliberately never overwritten.
The audit compares the independent `/tmp/beads-r282-replay` against `results`, and
8916 historical files against base `e6a6d4c`. Rendering/review commands target the
saved delivery results unless `R282_OUTPUT` is set. Browser launch may require the
local sandbox permission. `results/browser-check.json` records actual execution.

`first-pass/` preserves the first full three-phase run and its algorithm source,
before any answer-improving repair. `second-pass/` preserves the complete run after
Phase1 palette/black repairs, before Phase2 color sampling repair. `results/` is the
final run. Each has a completion manifest, full fits, rejected alternatives and
inventories. Routine Python caches are ignored. All A/B/C support proposals remain
in compressed JSON, including rejected/overlapping alternatives.

Shared records are dictionaries validated in `common.py`. Native masks are inclusive
row runs `[y,x_start,x_end]`; coordinates are native pixel centers, x right/y down.
Phase1 visibility is null (unmeasured), not zero. Phase2 visibility is a conditional
native first-hit/isolated projection ratio. An index is conditional on its named
model hypothesis, never a resolved whole-necklace identity. `phase_origin` records
actual contributors; Phase3 adds separate `pattern_color` fields and preserves all
photographic color, support and location fields. Reliability numbers are engineering
weights, not calibrated probabilities.

Photographic measurement uses ICC-managed sRGB. Review crops preserve original
JPEG-decoded RGB and are enlarged by nearest-neighbor. Green is measured support,
cyan its native edge, white a measured centroid; orange in model examples is a
conditional predicted first-hit surface. These are distinct from physical centers.
