# R307 reproduction

Open the whole-circuit review:

```sh
photo2/review/r307/launch.sh
```

`--no-browser --port 0` starts localhost without opening a browser. The offline
entry is `photo2/r307/results/campaign/review/index.html`. Model changes preserve
the photographic viewport, because conditional bead indices differ. The initial
view is the required R306 −101 location, approximately (1110.23, 336.04).

The green/orange/red overlap layer displays unchanged positive photographic
interior pixels on their largest visible owner, competing owners, or unresolved
background respectively. Orange is competing ownership, not a photographed color.
The nearby support list gives all competing fractions and selectable owners.
Unobserved exterior is not labelled as background. Uncertain outer polygons,
original photographic reference, geometric axis, native visible boundaries,
reflection vectors, and raw photograph remain separate layers.

Run a new approximately twenty-minute fitting workflow in a **new output**:

```sh
OPENBLAS_NUM_THREADS=1 python3 photo2/phase2_guided_fit.py \
  --output photo2/output/r307-new --seconds 1140
```

The program automatically enters the repository `.venv`. A system C++ compiler
(`g++`) builds the literal rounded-annulus marching kernel in a hash-named `/tmp`
library. No dependency installation or network access is needed. The benchmark
checks original Python ownership/shadows and native saved reflection equivalence,
and compares two-pixel versus native reflection ranking. It precedes the fitting
clock. `--seconds` is cumulative elapsed fitting time, including sensitivities,
physical screening, native acceptance checks, and checkpoint I/O. Final rendering,
independent verification, controls and review construction are evaluation work
outside that fitting allocation. Exact measured times are saved separately.

Use `--no-review` to stop after fitting, `--benchmark-only` to profile, and
`--max-evaluations N` for a proposal cap. Continue a run before its selection seal:

```sh
python3 photo2/phase2_guided_fit.py --output photo2/output/r307-new \
  --resume --seconds 1140 --no-review
python3 photo2/phase2_guided_fit.py --output photo2/output/r307-new --review-only
```

SIGTERM stops after the active evaluation. Resume retains the committed incumbent,
restarts any unfinished numerical block, charges the additional time, and checks
scientific source/evidence hashes. Atomic trial/checkpoint writes and a writer
lock protect publication. An interrupted block can repeat derivative work;
wall-clock termination is not claimed to reproduce an identical uninterrupted
proposal sequence. A sealed run cannot resume. The original outputs are immutable
scientific records; do not reuse their directory for a new fit.

Main artifacts under `photo2/r307/results/campaign/`:

- `benchmark.json`: original/compiled timing, exact native equivalence and ranking.
- `checkpoint.json`, `trials/`, `sensitivity-*.json.gz`: every proposal, physical
  rejection, fixed conditional owners, measured residual Jacobians, couplings,
  damped steps, accepted improvements and timing/memory records.
- `selection.json`, `native-ranking.json.gz`: dense native training selection.
- `exports/`, `model-parameters.json`: every physical body, all native visible
  boundaries/owners, contact witnesses and unchanged historical alternatives.
- `comparison.json`, `metrics/`, `acceptance.json`: identical-evidence old and new
  measurements, distributions, retrospective comparison bands, regressions and
  the explicit decision on overall photographic improvement.
- `fixed-initial-assignment-control.json.gz`, `R306-original-owner-control.json.gz`:
  geometry versus rematching controls; missing lobes remain failures.
- `diagnosis.json`, `controlled-diagnosis.json.gz`, `corrective-groups.json`:
  geographic failure detection and frozen-owner competing perturbations.
- `required-location.json`, `review/before-after.png`: required photographic
  location before and after; gallery also includes ownership quantiles.
- `verification.json`, `numerical.json`, `browser-check.json`: independent original
  kernel, complete close-pair contact, arclength/grid convergence and UI checks.

Verification:

```sh
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/beads-r307-mpl \
  .venv/bin/python -m unittest photo2.r307.tests -v
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r307_transaction_tests
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/beads-r307-mpl \
  .venv/bin/python -m photo2.r307.verify photo2/r307/results/campaign
/home/rharris/.local/bin/beads-chromium-review photo2.r307.browser_check
```

No original photographic evidence, prior scientific output, `beads.pov`, detector,
color pattern, or Phase 3 is changed. There is no count-discovery claim. The four
R306 count/hand/topology families remain alternatives; earlier R297–R299 models
remain unchanged full-circuit baselines. The geometric axis is R306's coherent
periodic curve with true arclength and smooth bounded fields, never a set of
independent regional models.

The delivered campaign includes a documented correction before comparison
exposure. Its first stage stopped on stagnation at1027.99s. The initial .8
correlation-only coarse-predictor gate proved too weak (best-quartile recall .5),
and equal-number spline blocks used different geographic origins. Remaining time
up to the cumulative1200s cap used native derivatives with correctly aligned
geographic blocks. `evidence/before-native-correction/` preserves the first source,
checkpoint, benchmark and Jacobians; `evidence/native-correction.json` binds the
transition to the first new trial. No objective weights or observations changed.
A fresh run of the corrected workflow applies the stricter ranking gate from the
start; it is not a bitwise replay of the earlier defective scheduling decision.
