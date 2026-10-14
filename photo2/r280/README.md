# R280 implementation and reproduction

[Report](../R280_PHASE2.md) · [Viewer](index.html) · [Protocol](PROTOCOL.md).
Open `index.html` directly; no server or package install is required for review.
All scene photographs, alternatives, failures and example panels are under `results`.

## API

```python
from photo2.r280.detector import infer
results = infer(rgb_uint8, predictions, method='C', thresholds=frozen_rules,
                phase1=frozen_observations)
```

A prediction is a dictionary with a unique `id`, `center: [x,y]` in original image
pixels, `diameter`, `visible` and `silhouette` raster runs `[y,x_start,x_end]`,
`uncertainty_px`, `scale_uncertainty`, and `angle_uncertainty_deg`. These surfaces
must be generated from the hypothesized geometry, never supplied from a truth
segmentation. Include nearby candidate surfaces so ownership can be contested.
Scale and angle variation are alternatives; translation may be searched alongside
one of them. There is no photometric/color-pattern model input.

Output `support` contains image-positive pixels within a registered model surface,
not a recovered full-body segmentation. `location` is their centroid;
`physical_center` is always null. Status is `strong`, `partial`, `ambiguous`,
`contradicted` or `insufficient`. `color` may be `unknown`. Preserve the initial
prediction, registration alternatives, competing IDs and uncertainty separately.
Predictions with no visible surface abstain. Frozen Phase 1 is comparison-only.

`P` in evaluation is frozen Phase 1 plus a nearest-observation query using A's
same aperture; the separate whole-image inventory association is also reported.
No observation is promoted or demoted by Phase 2.

## Reproduce

Use Python 3.12 with the repository `.venv` packages and POV-Ray 3.7; exact versions
are in `results/environment.json`. Commands run from the repository root. Use a
**disposable checkout** for regeneration: `results` is curated recorded evidence,
and `freeze` intentionally refuses to overwrite an existing freeze. Keep the
existing `development-v1`, original freeze, and dependency-repair records when
comparing a replay. The main numerical outputs are deterministic; render logs and
freeze timestamps need not be byte-identical.

```bash
export MPLCONFIGDIR=/tmp/r280-mpl
.venv/bin/python -m photo2.r280.synthetic dev
.venv/bin/python -m photo2.r280.run dev --baseline
.venv/bin/python -m photo2.r280.run dev --stage A1
.venv/bin/python -m photo2.r280.evaluate dev
# Inspect the easy A1 gate before increasing difficulty.
.venv/bin/python -m photo2.r280.run dev
.venv/bin/python -m photo2.r280.evaluate dev
# In a fresh output tree only; recorded freeze is immutable:
.venv/bin/python -m photo2.r280.freeze
.venv/bin/python -m photo2.r280.synthetic heldout
.venv/bin/python -m photo2.r280.run heldout --baseline
.venv/bin/python -m photo2.r280.run heldout
.venv/bin/python -m photo2.r280.evaluate heldout
.venv/bin/python -m photo2.r280.analysis
.venv/bin/python -m photo2.r280.supplemental
.venv/bin/python -m photo2.r280.real
.venv/bin/python -m photo2.r280.synthetic stress
.venv/bin/python -m photo2.r280.run stress
.venv/bin/python -m photo2.r280.evaluate stress
.venv/bin/python -m photo2.r280.absence
.venv/bin/python -m photo2.r280.review
.venv/bin/python -m unittest photo2.r280.tests
.venv/bin/python -m photo2.r280.audit
PLAYWRIGHT_BROWSERS_PATH=/tmp/beads-debugger-browsers .venv/bin/python -m photo2.r280.browser_check
```

The existing record can be verified without overwriting results via `tests` and
`audit`. The audit expects this recorded freeze and its documented import repair;
a fresh rerun should compare generated predictions with this reference rather
than pretending to reproduce wall-clock timestamps. `audit` regenerates one full
held-out scene's A1–A4 measurements, verifies all native support centroids, all scene
certificates, preserved inputs and the A5 dependency-repair replay hashes.

To reproduce the failed first detector in a disposable copy, replace `detector.py`
with `results/development-v1/detector.py` and rerun development A1–A4. The initial
empty-easy definition and correction are documented in `PROTOCOL.md`; current
strata intentionally differ from that first empty-stratum report. Never overwrite
historical outputs in the working branch to run this control.

## Evidence map

- `dev`, `heldout`: source POV scenes, appearance/identity PNGs, evaluator-only truth,
  independent geometric predictions, perturbations, frozen baseline decisions and
  **every** inference result. Truth physical addresses are only evaluator metadata.
- `stress`: source-pitch intersecting constructions, excluded from primary results.
- `absence`: easy bead removed from the render while the original model prediction
  is retained; newly exposed bodies test false confirmation.
- `development-v1`: original detector and failed/overconfident predictions.
- `*-evaluation.json.gz`: per-prediction truth associations, statuses, masks,
  errors, uncertainty coverage and difficulty/color labels for evaluation.
- `*-summary.json`, `analysis.json`, `supplemental.json`: tier/test/method tables,
  scene-cluster uncertainty, full-inventory comparison, true new recoveries and
  color/contamination summaries.
- `real`: six original native-pixel crops, automatic anchor selection, all local
  geometric alternatives, both retained helicities, immutable Phase 1 comparisons.
- `freeze.json`, `dependency-repair.json`, `dependency-audit.json`: operating rules,
  source hashes and the numerically neutral removal of historical import-time I/O.
- `preserved-input-hashes.json`, `audit.json`, `real-replay.json`: source/evidence
  preservation and exact replay results.
- `examples`: raw-versus-annotated panels; `viewer-data.js` serves the same evidence
  without requiring HTTP. Orange is a model; green is measured conditional support.

No current real-photo accuracy percentage, validated full-body ownership, recovered
string indexing, global fitting, pattern search or reconstruction growth is claimed.
