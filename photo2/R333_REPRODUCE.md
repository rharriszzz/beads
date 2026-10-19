# Reproduce R333

Use the repository Python3.12 `.venv`, NumPy/SciPy/Pillow and installed Playwright.
No package installation, network scientific source, detector or renderer is needed.
Read R333_REPORT.md and R333_SPECIFICATION.md for thresholds and limitations.

The delivered inference is deterministic with fixed seeds333/33301/33302/33303.
A fresh end-to-end replay runs every scientific stage, including all control
selections, measures each process's wall time/peak RSS and compares parsed results
with delivery (only `seconds` excluded):

```sh
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r333.replay --output /tmp/r333-replay-new
```

The output must not exist. The replay takes roughly one minute on this machine.
The receipt is `/tmp/r333-replay-new/replay.json`; stdout/stderr and complete
fresh scientific outputs remain beside it. `R333_RUN_ROOT` selects the R333 stage
root for independent manual execution; it never redirects historical R332 inputs:

```sh
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export MPLCONFIGDIR=/tmp/r333-mpl
export R333_RUN_ROOT=/tmp/r333-manual-new
.venv/bin/python -m photo2.r333.spirals --output "$R333_RUN_ROOT/spirals"
.venv/bin/python -m photo2.r333.staircases --output "$R333_RUN_ROOT/staircases"
.venv/bin/python -m photo2.r333.periods --output "$R333_RUN_ROOT/periods-selected"
.venv/bin/python -m photo2.r333.diagnose --output "$R333_RUN_ROOT/diagnosis"
.venv/bin/python -m photo2.r333.followup --output "$R333_RUN_ROOT/followup"
.venv/bin/python -m photo2.r333.viewer --output "$R333_RUN_ROOT/review"
.venv/bin/python -m photo2.r333.motifs
```

Each output directory must be new. Manual figure generation uses delivered CSS/JS
sources. Offline relative photograph/report links assume the repository depth;
a `/tmp` scientific replay does not require these links. Use a matching checkout
layout to inspect a fresh viewer. The delivered standalone SVG panels and native
crops are usable directly. Scientific code never writes into R332 or older rounds.

Independently coded verification reads the delivered results by default:

```sh
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r333.verify --output /tmp/r333-independent-check.json
```

`--run /tmp/r333-manual-new` also checks a fresh complete output including crops.
The independent verifier does not call the fitting/tracing/classification code.
It recalculates every main period score and staircase-template score, graph
arithmetic, actual path links, motif uncertainty, guarded-copy rules, coherent
patch consequences, appearance votes and exact native crop pixels. It checks
historical hashes and scoped differences from the R332 delivery. It cannot
certify physical body identity or a complete maker-compatible repeat.

The actual browser check uses the existing approved local Chromium launcher:

```sh
/home/rharris/.local/bin/beads-chromium-review photo2.r333.browser_check
```

This checks file links, both canvases, real hit testing, zoom/pan/recenter, raw
photo, direction/palette/status layers, maps/conventions/reversal, all native
assets and desktop/narrow/offline layouts. Screenshots and receipt are in
`r333/review/`. No server or remote service is required.

Principal machine-readable outputs:

- `r333/input-seal.json`:111 immutable historical input hashes.
- `r333/spirals/spirals.json.gz`:all six cone comparisons, flexible paths,
  components/branch counts,241 translations, spatial predictors and controls.
- `r333/staircases/staircases.json.gz`:216 exhaustive template scores,59 regular
  measured traces, distant copy evidence and all selected/null alternatives.
- `r333/periods-selected/periods.json.gz`:40×201 cached-map rankings,404 expanded
  fits, sensitivities,18 compatible-divisor fits,176 G fits, motifs, alias pairs,
  phase inference, cyclic-cut controls and38 full-selection null trials.
- `r333/diagnosis/diagnosis.json.gz`:19 observed breaks,128 unknown sites, original
  colors/coordinates/A/B indices, all photographic votes, source IDs, neighboring
  comparisons,40 patch translations, hypotheses and bounded feedback history.
- `r333/followup/followup.json.gz`:widths,236 regular endpoint alternatives,
  simple baselines, weak-penalty phase diagnostics and old-motif/R332 checks.
- `r333/review/`:interactive canvases,16 detailed problems,48 exact native crops,
  annotated photo/lattice comparisons, complete marker keys and eight SVG panels.
- `r333/verification.json`, `performance.json`, `manifest.json`, `delivery.json`:
  independent checks, fresh replay, scoped file hashes and push confirmation.

`r333/development/` preserves the first lattice/path exploration, the missing
full-residue-pad period failure and the duplicate-key cyclic-cut export failure and the set-order-only replay comparison failure.
Those sources are historical snapshots, not selected analysis modules. Empty
failed output directories contain no scientific result. The rejected controls
and nonselected models are retained in selected result ledgers as well.
