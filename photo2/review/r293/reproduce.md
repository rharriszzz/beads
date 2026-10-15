# R293 review and reproduction

From `/home/rharris/git/beads`:

```bash
photo2/review/r293/launch.sh
```

Open **http://127.0.0.1:8293/**. The first panel shows the whole original photograph
and centerline-centered evidence map. Wheel zoom/drag pan; priority/source-color/window
modes and hide-all leave the raw pixels accessible. Select any reference window for
an unmarked native crop and nearby available proposals. Window IDs are image-curve
inspection IDs, never physical bead indices. Green indicates illumination proxies,
not accepted segmentation or complete bead coverage.

Start Here asks8 new central questions; old24 judged cases are read-only. All125 cases
remain available. Judge the photographed material/reflection region, not a full body
silhouette. Raw photo, target, supported/uncertain edges, separators-only, original
patch versus candidate centroid, zoom/pan, keys1–6, H, arrows, optional diagnostics,
undo/history/export and reopening remain. Feedback is separately fsynced under
`photo2/r293/feedback/` (Git-ignored); `--feedback PATH` and `--port PORT` are available.
No test writes actual human feedback. Back up that folder and immutable snapshots.

```bash
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/beads-r293-mpl .venv/bin/python -m unittest photo2.r293.tests -v
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/beads-r293-mpl .venv/bin/python -m photo2.r293.audit --replay
/home/rharris/.local/bin/beads-chromium-review photo2.r293.browser_check
```

Replay uses a temporary directory, compares byte-exact gzip results and48 PNGs, and
updates only R293 audit/evaluation/coverage receipts. It does not refreeze selection,
change source pixels or modify older outputs/feedback. Chromium uses temporary answers.

To retain independent inference replays:

```bash
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/beads-r293-mpl .venv/bin/python -m photo2.r293.run development --output /tmp/beads-r293-replay
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/beads-r293-mpl .venv/bin/python -m photo2.r293.run reserved --output /tmp/beads-r293-replay
```

Source/selection freezes must not be overwritten. R293 reuses frozen R292 inference
unchanged; reserved results check its source hashes. All old cases were already exposed.
No inference repair followed the new reserved outcomes.

Derived presentation/measurement outputs can be regenerated with
`python -m photo2.r293.coverage`, then `.review`, `.export`, and `.audit` using the
repository `.venv/bin/python`. These write only R293 artifacts. `gallery development`,
`gallery reserved`, `gallery start`, and `gallery r292-feedback` generate original-photo
comparison sheets. The full source photograph and every crop remain native decoded RGB;
measurements use ICC-managed sRGB/linear luminance. All coordinates are EXIF-oriented
native x-right/y-down; pixel runs use inclusive horizontal endpoints, boxes exclusive
upper bounds, contour sides half-integer coordinates.

Artifact map:

- `R293_SPECIFICATION.md`, `R293_PRIORITY_POLICY.md`: scope and corrected priorities.
- `R293_R292_REVIEW_ANALYSIS.md`, `evidence/completed-r292-review.jsonl.gz`,
  `r292-review-analysis.json`: full original events/history and verified snapshots.
- `evidence/collection.json`:48 new independent targets,24/24 allocation, selection
  rules, exact locations/hashes and pre-outcome freeze.
- `evidence/historical-hashes.json.gz`, `feedback-hashes.json`: preservation baseline.
- `results/feature-population.json.gz`:1545 original feature records plus photometric
  priority, signed curve coordinates, uncertainty and border-distance descriptors.
- `results/algorithm-frozen.json`, `{development,reserved}.json.gz`: source freeze and
  all new unchanged-R292 masks, contours, separator arcs, T1–T8 and sensitivity.
- `results/coverage.json`, `stations.csv`, `evaluation.json`, `case-evaluation.csv`:
  exact coverage accounting and separate new-population diagnostics, not accuracy.
- `checkpoints/arc-window-initial/`: preserved false-gap metric and source before
  correcting coverage to actual photographic window footprints.
- `results/phase1-observations.json.gz`, `export-summary.json`: experimental linked
  photographic evidence; accepted exact visible measurements versus separate masks;
  physical identities/centers unknown; no production replacement.
- `review/r293/original.png`, `stations/`, `crops/`, `data/`, `coverage.json`: raw native
  overview/window/case pixels and versioned automatic evidence for the browser.
- `results/start-here.json`, `review/r293/manifest.json`: eight new central questions,
  known judgments read-only and transparent selection rules.
- `results/tests.log`, `replay.log`, `audit.json`, `browser-check.json`, `delivery.json`:
  validation and verified remote delivery receipts.

A feature count, green station, signed-side pair or stable/supported mask is not
physical bead count, exact ownership, full visibility or calibrated precision.
All original observations remain available for later conditional interpretation.
Stop for user review; no Phase 2/3 or automatic R294.
