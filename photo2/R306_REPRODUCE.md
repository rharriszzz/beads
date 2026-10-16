# R306 reproduction

Open the delivered whole-circuit review from any directory:

```sh
/home/rharris/git/beads/photo2/review/r306/launch.sh
```

The launcher uses the repository environment, serves localhost on port 8306
(with an available-port fallback), and reuses the existing WSL browser dispatch.
Use `--no-browser --port 0` for a server without browser launch. The standalone
viewer is `photo2/r306/results/campaign/review/index.html`; it also works offline.
The original photographic reference and fitted geometric axis have separate
toggles. Native visible boundaries include holes and occlusion. Follow, index
box/slider, ±1/10/50, owner picking, plot clicks and diagnostic crops recenter the
same raw/annotated viewport. Indices differ between models and remain conditional.

Run a new bounded experiment; use a new destination to preserve this delivery:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 photo2/phase2_global_fit.py \
  --output photo2/output/r306-new --seconds 3600 --seed 306 --no-review
```

`--seconds` is the **cumulative fitting budget**, including evaluation/checkpoint
overhead, but excluding export, verification and browser checks. `--max-evaluations`
provides an additional cap. Every candidate is physical-gated before selection.
The output retains rejected contacts, actual penetration witnesses, unmatched
reflections, competing assignments and every physical body.

The delivered main run instead used
`--initialize-from photo2/r306/results/campaign-initial --seconds 3600 --seed 306`.
The separate cold run used `--seconds 900 --seed 307`. The 428-proposal exploratory
stage and its earlier source are retained; its uniform envelope weighting differs
from the main stage. No comparison feedback caused that correction. A main-run
`additional-runs.json` lists relative sibling run directories whose best feasible
hand/topology candidates should enter native ranking. All listed runs must finish
with identical scientific sources/evidence before joint selection.

Wall-time limits can stop at different proposal numbers on different hardware.
For deterministic sequence replay, use the recorded seed, initialization,
environment and `next_id` as `--max-evaluations`, with an ample `--seconds` limit.
The delivered parameter/visibility verifier checks saved geometry independently
of timing-dependent search termination. Earlier source snapshots are for an
isolated replay checkout; do not overwrite the delivered implementation.

Resume an unsealed run with the same scientific source and evidence:

```sh
python3 photo2/phase2_global_fit.py --output photo2/output/r306-new \
  --resume --seconds 5400 --no-review
```

Source/evidence/environment checks and a writer lock prevent incompatible or
concurrent continuation. Atomic candidate transactions recover after interruption,
including a crash between result publication and checkpoint advancement. A
SIGTERM requests a graceful stop after the current candidate; a hard tool kill
may leave a pending transaction, which resume replays or incorporates.

Generate the native finalist ranking, seal the training selection, evaluate
comparison bands, diagnose residuals, and create the viewer:

```sh
python3 photo2/phase2_global_fit.py --output photo2/output/r306-new --review-only
```

With the default options this performs no parameter optimization. Add
`--native-seconds 180` to request a separately timed final native refinement before
the first selection seal; this option is used in the delivered campaign. It tests
small paired phase, axis, shape and light changes on training evidence only.
Native candidate evaluation, full contact
auditing, controlled residual interventions, rendering and independent verification
still take computation. The entry point runs the independent verifier after export.
Omitting `--no-review` on a fitting command performs this step automatically.
After comparison exposure the run is sealed and cannot resume. A later campaign
can reevaluate its population in a new directory using
`--initialize-from photo2/output/r306-new`; those exposed comparisons remain
retrospective, not fresh validation. The delivered main stage uses this mechanism
to retain the exploratory stage while correcting envelope uncertainty weights.

Verification commands:

```sh
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m unittest photo2.r306.tests -v
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r306.transaction_tests
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r306.verify photo2/r306/results/campaign
/home/rharris/.local/bin/beads-chromium-review photo2.r306.browser_check
git diff --check
```

The verifier checks every exported center, all spatial contact witnesses against
the independent support formula, native visibility samples, complete original
support denominators, half-pixel reflection sensitivity, doubled arclength
integration resolution, original photo pixels and historical-file preservation.
Browser tests cover all models, variable count limits, both axes, raw invariance,
native picking, interactive plots, desktop/narrow layouts and offline operation.
Windows dispatch is mocked; an actual Windows browser opening is not claimed.

Main artifacts under `photo2/r306/results/campaign/`:

- `checkpoint.json`, `candidates/`, `sensitivity-*.json`: actual proposals,
  source/evidence hashes, timings, rejections, population and measured responses.
  Git transports candidate files in lossless `candidate-archive/` JSONL chunks;
  the entry point restores and checks their exact gzip bytes automatically.
- `selection.json`, `native-ranking.json.gz`: native training-only selection.
- `exports/*.json.gz`: all positions, physical witnesses, native boundaries,
  reflections, assignments, measurements, uncertainty and common-geography metrics.
- `exports/*-raster.npz`: native owner/address/unknown arrays and specular samples;
  owner is an array offset, address is the conditional index, background address
  is −32768. No body is removed for missing photographic evidence.
- `exports/*-neighbor-predictions.json.gz`: conditional +1/+6/+7 vectors and
  directional support margins, kept separate from measured neighbor evidence.
- `model-parameters.json`, `computation.json`: selected parameters and actual
  timing/proposal ledger. Aggregate fitting time counts the overlapping main
  and independent runs separately; it is not CPU time or end-to-end wall time.
- `comparison.json`, `common-support-deltas.json.gz`, `identity-sensitivity.json.gz`:
  common observations and component metrics, without changing historical models.
- `diagnosis.json`, `controlled-diagnosis.json.gz`,
  `fixed-initial-assignment-control.json.gz`, `R305-problem-cohorts.json`:
  automatic triage, fixed-owner interventions and historical geographic cohorts.
- `whole-circuit-trends.json`, `rejected-contact-clusters.json.gz`: descriptive
  signed slopes, sparse gaps, regional recoveries and rejected collision clusters.
- `verification.json`, `numerical.json`, `browser-check.json`: numerical and UI checks.

All R293 photographic coordinates, prior models, previous viewers and Phase 1
evidence are read-only. The model is one adjustable planar periodic geometric
curve with numerical true arclength, bounded smooth spacing/phase fields and one
shared camera/illumination. The historical 0.975 relationship is not imposed.
No new image detector, synthetic fitting campaign, color pattern or Phase 3 is used.
