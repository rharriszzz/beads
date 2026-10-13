# R273 evidence

[Report](../../INTERIORS_R273.md) · [viewer](../../interior_inventory_r273/index.html).

`inventory.json`, `inventory.js`, `inventory.csv`: complete selected measurements.
`paired-regions.csv`: every old/new accepted or excluded decision.
`*-candidates.jsonl.gz`: all alternatives, exact mask runs, parameters and reasons.
`direction_stops` remain in the compressed diagnostic records, not the lightweight viewer inventory.
`red-failure-audit.json`: preserved pre-remedy failure counts and examples.
`red-remedies-comparison.json`: delivered gains/losses and optional background controls.
`selection.json`: globally selected parameters; no per-bead choice of method.
`summary.json`, `expansion-summary.json`, `black-controls.json`: all control summaries.
`review-stopping-comparison.csv`: exact cutoffs and stopping causes for review crops.
`review-direction-traces.jsonl.gz`: native Y/mean3 steps and stop/trigger coordinates.
`synthetic-*.json`, `historical-synthetic-*.json`: known-truth measurements and associations.
`black-fixture-*.npz`: new reproducible reflection input/truth arrays, evaluation only.
`validation.json`, `viewer-node-checks.json`: passing exact/native and JS checks.
`browser-checks.json`: explicit deferred rendered-browser check.
`preserved-hashes.json`: all148R272 evidence files/reports checked unchanged.
Original ICC-corrected photo is reused from `../r272/photo-srgb.png`.
Raw all-maxima/rejection history remains in `../r272-coverage/`.

Reproduce from repository root using Python3.12:

```sh
export MPLCONFIGDIR=/tmp/beads-r273-mpl
.venv/bin/python -m photo2.bead_detection.experiment_r273
.venv/bin/python -m photo2.bead_detection.expansion_r273
.venv/bin/python -m photo2.bead_detection.deliver_r273 remedy-shape
.venv/bin/python -m photo2.bead_detection.review_r273
.venv/bin/python -m photo2.bead_detection.diagnostics_r273
.venv/bin/python -m photo2.bead_detection.red_audit_r273
.venv/bin/python -m photo2.bead_detection.remedies_review_r273
.venv/bin/python -m photo2.bead_detection.evaluate_r273
.venv/bin/python -m photo2.bead_detection.historical_r273
.venv/bin/python -m photo2.bead_detection.validate_r273
.venv/bin/python -m unittest photo2.bead_detection.test_r273 photo2.bead_detection.test_coverage_r272 photo2.bead_detection.test_inventory_r272
node photo2/interior_inventory_r273/test_viewer.cjs
```

Runtime `interiors_r273.detect(native_rgb, icc_srgb)` starts from photograph pixels.
`refine` accepts automatically generated baseline records for paired experiments.
Review crop boxes are used only after detection to select diagnostic outputs.
