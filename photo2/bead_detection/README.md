# Native-pixel bead supports — R261

R261 replaces the default radial detector with an independent native-pixel detector.
Its goal is a reliable supported coordinate per visible bead. These results remain
candidate supports, with duplicate highlights and misses unresolved.

```bash
.venv/bin/python -m photo2.bead_detection.server
```

Open **http://localhost:8767**. Restart an older server first, or add `--port 8768`.
The first launch generates missing data in `photo2/output/detection-r261/` from the
original photograph. It does not read historical bead labels, curves or models.
The familiar `photo2.bead_debugger.server` launcher also opens this viewer.

Drag to pan; scroll to zoom. Cyan contours are smoothed for display only. Their
exact integer pixel runs determine area, area centroid and supported coordinate.
The bright-patch centroid is a separate measurement. No coordinate is called the
physical bead center. Pixel centers use integer x right / y down after EXIF orientation;
at high zoom the photograph uses nearest-neighbor display.

Click a region or enter its `P` ID (numeric input is accepted). **Largest, Smallest,
Median** and previous/next browse retained area. The median button selects the
middle ranked region, choosing the lower area for an even-sized inventory. Click
histogram bars to filter. Region IDs belong to this run, not the R260 `R` namespace
or a resolved bead index. Rejected grown supports can be selected by ID too.

**Growth replay:** Reset begins before the seed. `+1 pixel` accepts exactly one
recorded native pixel; Play advances at one pixel per 60 ms. The slider can inspect
any acceptance. Cyan fill shows pre-retreat growth; the contour remains the final
support. Pixel details identify acceptance order, predecessor, raw brightness,
HSV, and whether retreat later removed the pixel. **Final** hides the replay fill.
**Stop → / ← Stop**, or an exact stop event number, visits every stopped edge,
restores its exact acceptance time, and marks the destination pixel orange and
its predecessor edge white. Brightness is max(R,G,B) in 0–255; H is degrees, S/V
are 0–1. Traces are loaded on selection; Download full growth trace exports them.

All candidate maxima, coordinates, size ranks and histogram are downloadable.
147,218 below-prominence maxima have preserved plateau pixels and rejection
reasons but no expansion trace because no growth was attempted. All 7,543 grown
candidates, including rejected ones, have complete traces. Full compressed copies
are committed in [../review/r261](../review/r261/README.md).

Reproduce in Python 3.12 with the existing [requirements](requirements.txt):

```bash
.venv/bin/python -m unittest photo2.bead_detection.test_pixels -v
.venv/bin/python -m photo2.bead_detection.curate_r261 synthetic
.venv/bin/python -m photo2.bead_detection.pixel_detect
.venv/bin/python -m photo2.bead_detection.validate_pixels --isolation
.venv/bin/python -m photo2.bead_detection.curate_r261 compare
.venv/bin/python -m photo2.bead_detection.curate_r261 valley
PLAYWRIGHT_BROWSERS_PATH=/tmp/beads-debugger-browsers .venv/bin/python -m photo2.bead_detection.browser_pixels
.venv/bin/python -m photo2.bead_detection.curate_r261 archive
```

Retreat is configurable via `pixel_detect --retreat-fraction .30 --retreat-dn 2`;
other parameters are explicit in `pixel_detect.Parameters`. Save experiments to
different `--output` directories. Changing display contours never changes masks.
Playwright/Chromium is optional and needed only for browser tests.

**Preserved R260:** `python -m photo2.bead_detection.server_r260 --port 8768`
(with `.venv/bin/python`) uses the unchanged historical radial detector and copied
viewer assets. `detect.py`, R259/R260 results, strict comparisons and reviews remain
preserved. The old `browser_smoke` tests explicitly target this archived viewer.
The geometry debugger remains at `photo2.bead_debugger.server --legacy`.

[Algorithm, safeguards, evidence and limitations](../PIXEL_DETECTION_R261.md).
