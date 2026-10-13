# R272 coverage evidence

[Scientific report](../../COVERAGE_R272.md) · [Simple viewer](../../coverage_inventory_r272/index.html).
Open the viewer directly; it uses the preserved ICC-corrected photograph from
`../r272/photo-srgb.png`. Accepted overlays are cyan. Exclusions are optional orange
dots with explanations; these are not included in size navigation.

- [Whole photograph](whole-photo.png).
- Original/accepted pairs: [S1](S1-comparison.png), [S2 paper control](S2-comparison.png),
  [S3](S3-comparison.png), [S4](S4-comparison.png), [S5](S5-comparison.png),
  [S6](S6-comparison.png), [S7](S7-comparison.png), [S8](S8-comparison.png).
- Familiar crops: [R00956](R00956.png), [R01284](R01284.png).
- Black size examples: [smallest](black-smallest.png), [median](black-median.png),
  [largest](black-largest.png); [red](red-median.png), [yellow](yellow-median.png).
  All three sizes are also saved separately for red and yellow.
- [Black signal additions](black-signal-additions.png),
  [excluded candidates with reasons](excluded-examples.png),
  [multiple glints](failure-multiple-glints.png),
  [color/ownership ambiguity](failure-color-ownership.png),
  [dim-yellow miss](failure-dim-yellow.png).
- [New synthetic examples](synthetic-examples.png),
  [mixed neighbors](synthetic-mixed-examples.png).

## Numerical files

`inventory.json` is the authoritative complete accepted inventory; `inventory.csv`
is a measurement summary and `inventory.js` is its direct-file viewer wrapper.
Exact masks use inclusive `[y,x_first,x_last]` native-pixel runs. Smoothed contours
are display-only. The photograph has2540×3182 pixels; integer x/y identify pixel
centers, with origin at the upper left.

`candidates.jsonl.gz` retains every raw and mean7 maximum, all plateau pixels,
measurements and rejection/suppression reasons. `all-maxima.npz` retains both
full-frame maximum masks. `search-traces.jsonl.gz` saves every5/7/9 guarded search
path and score. Missing late-stage fields mean the candidate failed earlier checks,
not that unmeasured requirements passed. Broad paper/noise failures are not loaded
into the optional viewer layer, but remain in this complete file.

`black-controls.json` and `black-control-*.jsonl.gz` retain the five signal/material
controls. `gate-ablations.json` isolates six colored cheap gates on a common final
downstream population. `r260-black-comparison.json` and `r271-comparison.json`
provide comparison-only nearest-coordinate matches, not verified identities.
`pilot-native-v/` preserves the initial743-location run and its exact source.

`photo-samples.json`, its SHA256 and `sample-*-blind.png` freeze the pre-detection
visual annotations. `photo-evaluation.json` retains automated association flags;
`photo-review-limitations.json` records later boundary interpretation explicitly.
These evaluation annotations are never imported by the detector.

`synthetic-inputs.npz`, `synthetic-truth.npz`, `synthetic-candidates.jsonl.gz` and
`synthetic-evaluation.json` contain52 new scenes and complete decisions.
`historical-synthetic-evaluation.json` and `historical-synthetic-candidates.jsonl.gz`
use the112 unchanged R270 input/truth arrays; no copied or modified historical truth.

`validation.json`, `unit-tests.txt`, `viewer-node-checks.json`, `skipped-actions.json`,
`source-hashes.json`, `preserved-hashes.json`, `summary.json` and `budget.json`
record verification, provenance, limitations and the bounded computation window.

## Reproduce

Use Python3.12 in the project environment. Run in a clean checkout or archive this
experiment directory first if retaining a new rerun side by side. The commands
write only `review/r272-coverage`; previous R259–R272 experiments stay unchanged.
Reset the experiment clock explicitly before rerunning:

```sh
.venv/bin/python -c 'import json,time; from pathlib import Path; Path("photo2/review/r272-coverage/budget.json").write_text(json.dumps({"start":time.time(),"seconds":1800}))'
MPLCONFIGDIR=/tmp/beads-r272-coverage-mpl .venv/bin/python -m photo2.bead_detection.experiment_coverage_r272
MPLCONFIGDIR=/tmp/beads-r272-coverage-mpl .venv/bin/python -m photo2.bead_detection.black_controls_r272
MPLCONFIGDIR=/tmp/beads-r272-coverage-mpl .venv/bin/python -m photo2.bead_detection.evaluate_coverage_r272
MPLCONFIGDIR=/tmp/beads-r272-coverage-mpl .venv/bin/python -m photo2.bead_detection.historical_coverage_r272
MPLCONFIGDIR=/tmp/beads-r272-coverage-mpl .venv/bin/python -m photo2.bead_detection.review_coverage_r272
MPLCONFIGDIR=/tmp/beads-r272-coverage-mpl .venv/bin/python -m unittest photo2.bead_detection.test_coverage_r272 photo2.bead_detection.test_inventory_r272
MPLCONFIGDIR=/tmp/beads-r272-coverage-mpl .venv/bin/python -m photo2.bead_detection.validate_coverage_r272
node photo2/coverage_inventory_r272/test_viewer.cjs
MPLCONFIGDIR=/tmp/beads-r272-coverage-mpl .venv/bin/python -m photo2.bead_detection.finalize_coverage_r272
```

The old native-V pilot is retained rather than overwritten by the final runner.
The black-control script uses its image-derived raw candidates, not review labels;
all candidate raw maxima are unchanged between those controls.

A real browser check is saved but **was not run successfully in this delivery**:

```sh
PLAYWRIGHT_BROWSERS_PATH=/tmp/beads-debugger-browsers .venv/bin/python -m photo2.bead_detection.browser_coverage_r272
```

Chromium requires a process-launch permission unavailable in this sandbox. Per the
user's instruction, new approval was not requested. Node checks exercise actual
viewer logic but do not establish rendered-browser layout or screenshot correctness.
