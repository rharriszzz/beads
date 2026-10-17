# R309 reproduction

The primary workflow runs without an AI supervisor. From this checkout:

```bash
python3 photo2/phase2_competing_fit.py --preflight --output /tmp/r309-preflight
python3 photo2/phase2_competing_fit.py --output /tmp/r309-new --seconds 1200
python3 photo2/phase2_competing_fit.py --output /tmp/r309-new --seconds 1200 --resume
photo2/review/r309/launch.sh
```

The entry selects the repository .venv, one numerical thread, compiled R307 native
marcher and a fresh output. Budget includes all shared probes and four objective
branches; it is cumulative on restart. Cached published trials are reused. SIGTERM
saves progress without sealing; --resume checks scientific source and evidence
hashes. --no-review separates fitting from finalization; --review-only completes
export/diagnosis/verification for an existing run. Sealed results cannot resume.
The deterministic bounded schedule and physical gates need no maker decisions.
Wall-time cutoff paths can vary with hardware and concurrent load. No random seed
or hidden manual candidate selection is used. All locally varying historical fields
are frozen, with at most six globally acting scalars in a numerical block.

The delivered run uses the corrected unknown-ray rules from its first evaluation.
The smooth optical objective is an intensity-overlap positional surrogate; exact
thresholded-centroid Euclidean errors remain independent final outcomes. Full
residuals and all catalog reflections are saved, including missing/ambiguous pairs.
Native finalists include the complete visible body for each uncertain contour;
fit-window boundary statistics are separately retained, not passed off as full-body
measurements. Training/comparison splits are historically exposed.

```bash
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m unittest photo2.r309.tests
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r309.transaction_tests
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r309.verify photo2/r309/results/campaign
/home/rharris/.local/bin/beads-chromium-review photo2.r309.browser_check
```

Browser tests need a localhost socket; the trusted wrapper supplies Chromium.
Windows dispatch is mocked. The viewer also opens offline through index.html.
The geometric-error dashboard explains D, vector meanings and missing observations;
the atlas uses identical native coordinates for raw/R306/R309 panels, with50
consecutive conditional model bodies per neighborhood wherever available.

Start independent scientific review at r309/results/campaign/analysis-summary.json.
The source snapshot, pre-run preservation hashes, realized trials/checkpoints,
parameter response data, numerical controls and independent delivery receipt allow
replay without reconstructing decisions from this conversation. No Phase3/patterns.
