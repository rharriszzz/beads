# R308 reproduction and independent review

Run from the repository checkout on photo-2-strategy-v3. The entry point selects
the repository .venv, fixes numerical thread counts and uses the unchanged R307
compiled native marcher (g++ compiler, shared library cached by source hash in/tmp).
It does not need an AI supervisor or maker decisions.

```bash
python3 photo2/phase2_hierarchical_fit.py --output /tmp/r308-new --seconds 1200
python3 photo2/phase2_hierarchical_fit.py --output /tmp/r308-new --seconds 1200 --resume
python3 photo2/phase2_hierarchical_fit.py --output /tmp/r308-new --review-only
photo2/review/r308/launch.sh
```

Use a new output for a new campaign. The seconds budget is cumulative, not an
additional allowance on resume. SIGTERM checkpoints and exits without exporting;
resume uses unchanged scientific source/evidence hashes and cached completed
native transactions. Atomic unpublished results are recomputed; committed results
are byte-preserved. A sealed result cannot resume. `--no-review` separates fitting
from finalization. `--max-evaluations` is for small transaction contracts.

The delivered campaign used1200 seconds cumulatively with --no-review, followed by --review-only. A recorded pre-comparison adaptation adds shrinking final-joint trust radii after the initial large-scale linear models stagnated. The original scientific source/state is retained under evidence/before-adaptive-joint; evidence/adaptive-transition.json binds the old and new fingerprints and elapsed time. The final entry includes this adaptive stage automatically, inside the same budget.

A second recorded transition repaired unresolved-ray separator/contour/paper
treatment after1033.904 fitting seconds. The preceding source, checkpoint and logs
remain under evidence/before-unknown-ray-repair; evidence/unknown-ray-repair.json
binds the transition. Fresh runs use the repair from the start, so they do not
reproduce the delivered pre-repair trajectory. After sealing, all500 feasible saved
trials were rescored under the repair without generating new candidates. This audit
adds approximately105.776 seconds, estimated from log filesystem timestamps;
two leading cases were independently reproduced with the original Python kernel.
It did not change the selected model. Final implementation snapshots and hashes
are under evidence/final-source and evidence/final-source-manifest.json.

Elapsed fitting includes loading, initial representative benchmarks, both sides of
derivatives, free/fixed-owner native optics, hard contact gates and checkpointing.
Qualification/contracts, final exports, browser checks and verification are separate
from scientific fitting. New runs follow the same deterministic finite schedule,
but time cutoffs and native floating-point compilation can change the last trial.
The full realized history is under r308/results/campaign/trials; no seed is hidden.

Read R308_SPECIFICATION.md for pre-run bounds, residual weights, stage budgets and
acceptance rules. The original photographic reference is never fitted or overwritten.
R306's full-chain geometry, original physical shape and all-body visibility/contact
logic remain. Stage1 holds distributed fields fixed, Stage2 adjusts small Fourier
increments, Stage3 jointly refines; integer families stay discrete. Shared lighting
is frozen. Source fingerprints in checkpoint.json cover all fitting implementations.

```bash
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m unittest photo2.r308.tests
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r308.transaction_tests
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r308.verify photo2/r308/results/campaign
/home/rharris/.local/bin/beads-chromium-review photo2.r308.browser_check
```

The trusted Chromium wrapper supplies the repository browser environment. Browser
checks need a localhost socket; sandbox escalation may be required. The launcher
serves only localhost, opens a browser automatically, and falls back to a free
port. Windows browser dispatch is mocked in automated tests, not physically observed.
The complete viewer also works by opening results/campaign/review/index.html offline.

For independent AI/scientific review begin with results/campaign/analysis-summary.json.
It links the unchanged common-metric comparison, all32 geographic diagnostics,
response curves/grids and minima, full scaled Jacobians/SVDs, predicted versus actual
steps, complete stage models, correction amplitudes/effects and fixed-owner controls.
All missing lobes remain in their denominators. Historical comparison measurements
were exposed in earlier experiments and are not fresh validation. New weighted loss
is not an adoption criterion. The source photo, prior numerical artifacts and all
feedback are checked against the pre-run preservation manifest.

Scientific delivery hash and independent remote verification are recorded in
r308/results/delivery.json. Stop after this campaign; no Phase3, pattern or R309.
