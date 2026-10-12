# R264 evidence

[Interpretation and limitations](../../HUE_COMPARISON_R264.md) ·
[optional question](../../HUE_REVIEW_QUESTIONS_R264.md).

Launch `.venv/bin/python -m photo2.bead_detection.server`, restart an older server,
and open http://localhost:8767/hue-comparison. Nine fixed original-photo crops show
all six settings, native supported coordinates, hover RGB/HSV and compact support
HSV summaries. Click a support to compare it; click its ID for that run's exact
pixel and stopped-edge replay. The saved 8° recommendation opens at
http://localhost:8767/?hue=8. The preserved detector default remains 10°.

Each of `5/`, `8/`, `10/`, `12/`, `15/`, `20/` contains a complete compressed region
and raw-maximum catalog, coordinates.csv, summary with parameters/source hashes,
all 1,595 growth traces in traces.tar, full native validation and overlap groups.
Traces are read directly from the archive by the viewer; no regeneration is needed.
The viewer's ordinary photo preparation uses the original repository JPEG.

- `metrics.json`: aggregate support/overlap/coordinate and leaf-control measurements.
- `overlap-pairs.json`: exact pair intersections/IoU; no inferred bead mergers.
- `coordinate-changes.json`: supported-coordinate movement and added/lost IDs vs 10°.
- `comparison.json` and nine named PNGs: identical crop bounds and all six candidates.
- `visual-review.json/png`: 12 likely duplicate pairs and six missing-location
  landmarks with confidence and applicable settings. Assistant judgments, not truth.
- `missing-seed-diagnostics.json`: nearest four raw maxima to each missing landmark.
- `hsv-routes.csv/json/png`: exact native RGB/HSV, within-body shading paths and
  shadowed red-to-yellow route, with original-photo context.
- `paper-window.json`: exact membership in a visually paper-dominated review window.
- `leaf-control.json`, `leaf-coordinate-control.png`: conservative diagnostic only;
  original production retreat remains unchanged.
- `browser-checks.json`, `baseline-browser/`: 60 new and 41 preserved real-browser checks.
- `8/isolation.json`: independent source/photo replay, exact exported arrays and traces.
- `detector-source.py`: exact unchanged bounded detector used for every setting.
- `manifest.json`: SHA-256 of curated files, detector and analysis/viewer sources.

Reproduce with Python 3.12:

```bash
.venv/bin/python -m photo2.bead_detection.hue_r264 --audit
MPLCONFIGDIR=/tmp/beads-r264-mpl .venv/bin/python -m photo2.bead_detection.analyze_r264
MPLCONFIGDIR=/tmp/beads-r264-mpl .venv/bin/python -m photo2.bead_detection.evidence_r264
.venv/bin/python -m unittest photo2.bead_detection.test_bounded photo2.bead_detection.test_tuning photo2.bead_detection.test_no_watershed photo2.bead_detection.test_pixels photo2.bead_detection.test_detection photo2.bead_detection.test_strict photo2.bead_detection.test_hue_r264 -v
PLAYWRIGHT_BROWSERS_PATH=/tmp/beads-debugger-browsers .venv/bin/python -m photo2.bead_detection.browser_hue
```

Run generation/archive before analysis, sequentially. Cached work is in ignored
`photo2/output/hue-r264/`. To force regeneration use a new work location in the
runner or remove only this experiment's generated cache deliberately. The previous
R263 timed parameter search is not invoked. The catalog's raw pixel convention is
integer x-right/y-down after EXIF orientation; display smoothing never changes masks.
