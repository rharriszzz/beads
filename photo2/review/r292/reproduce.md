# R292 launch and reproduction

From `/home/rharris/git/beads` with the existing `.venv`:

```bash
photo2/review/r292/launch.sh
```

Open **http://127.0.0.1:8292/**. Default Start Here has 11 cases. All 77 cases and
13 previous accepted references remain available. No repeat judgment is requested
for immaterial changes. Toggle Observed separators / Separators only to distinguish
measurement from optimization. Green arcs are constrained, pink arcs ambiguous,
open circles unresolved endings; cyan/orange outer segments supported/uncertain.
H hides all markings. Zoom/pan, arrows, answer keys1–6, optional diagnostics,
ownership reuse, undo, revision history, export and reopening are retained.

Feedback is separate in `photo2/r292/feedback/` (Git-ignored), with candidate/crop
snapshots and exact displayed separators. Use `--feedback PATH` or `--port PORT`
when needed. Tests never use the actual feedback directory. Prior R291 verdicts are
read-only evidence, not new answers. Historical red-worst ownership provenance remains.

Verify without replacing inference or feedback:

```bash
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/beads-r292-mpl .venv/bin/python -m unittest photo2.r292.tests -v
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/beads-r292-mpl .venv/bin/python -m photo2.r292.audit --replay
/home/rharris/.local/bin/beads-chromium-review photo2.r292.browser_check
```

The audit writes replay outputs into a temporary directory, checks byte-exact gzip
results and PNGs, then updates its own verification/coverage receipts. It does not
modify historical data or feedback. Chromium creates test answers only in `/tmp`.

Independent retained replay outputs:

```bash
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/beads-r292-mpl .venv/bin/python -m photo2.r292.run development --output /tmp/beads-r292-replay
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/beads-r292-mpl .venv/bin/python -m photo2.r292.run reserved --output /tmp/beads-r292-replay
```

Do not overwrite the frozen selection, source freeze or original results. Reserved
inference checks source hashes. New reserved cases were frozen before implementation;
all 68 R291 cases were already exposed. No tuning after new reserved outcomes.

To regenerate comparison summaries and CSV from the saved package, run
`.venv/bin/python -m photo2.r292.evaluate`; regenerate the package with
`.venv/bin/python -m photo2.r292.review`. Neither writes human judgments.

Artifact map:

- `R292_SPECIFICATION.md`: approved scope and pre-development selection/evaluation rules.
- `r292/evidence/collection.json`: exact features, native positions, image hashes,
  selection source, nine fresh targets and explicit unfilled unknown slot.
- `evidence/historical-hashes.json.gz`, `feedback-hashes.json`: preservation baseline.
- `graph.py`: R291 objective with independently controlled peer/darkness costs.
- `ablation.py`, `results/r291-B-ablation.json.gz`: exposed-case 2x2 causal comparison.
- `separators.py`: observed valley/edge paths, exterior/core contradictions and
  direct/both-bank crossing measurements.
- `continuation.py`: local interruption/replacement evidence; no region-size gate.
- `detector.py`: one-target assembly, alternate strict interpretation and sensitivity.
- `run.py`, `results/algorithm-frozen.json`: staged inference and source/parameter freeze.
- `checkpoints/`: full first development results and failed extension probe/sources.
- `results/{development,reserved}.json.gz`: exact masks, contour sides, all T1–T8,
  measured separator paths, unresolved ends, contradictions and perturbation results.
- `review.py`, `evaluate.py`, `results/comparison.json`, `case-comparison.csv`, `summary.json`:
  every-case comparisons, accepted-reference provenance and diagnostic counters.
- `results/start-here.json`, `review/r292/manifest.json`: transparent 11-case priority.
- `results/coverage.json`, `R292_COVERAGE.md`, `review/r292/coverage.html`: situation
  coverage, unresolved outcomes and missing physical truth/fresh strata.
- `gallery.py`, `results/*-comparison-*.png`: original-photo nearest-neighbor views.
- `serve.py`, `review/r292/`: durable review infrastructure and local launcher.
- `results/tests.log`, `replay.log`, `audit.json`, `browser-check.json`: verification.

Native x increases right, y down after EXIF orientation. Runs are
`[y,inclusive-x0,inclusive-x1]`; pixel-square contour sides are half-integer positions.
`box` uses exclusive upper bounds. Separator `path` is in original coordinates;
`local_path` is relative to the box. Measurements use ICC-managed sRGB/linear Y;
review crops preserve original decoded RGB. Graph search uses radius48, expanding
96/144 on frame contact; a frame never supports an accepted segment. Sensitivity
recomputes separators/continuation at unary strength±15% and with16px extra context.
These are sensitivity measurements, not calibrated accuracy intervals.

The live human ledger from R291 is untouched. Its full archived revisions and
13 selected references remain in `photo2/r291/evidence/`. Runtime inference never
loads that evidence. Stop for evaluation; no automatic R293 or holdout repairs.
