# Reproduce R327

Review `photo2/r327/results/index.html` directly; it works offline. Scientific JSON
banks and decision ledgers are gzip-compressed. Read with `gzip.open(path, 'rt')`.
The original image, R326 measurement pixels and every old candidate are preserved.

The initial diagnostic is reproduced in a NEW directory:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MPLCONFIGDIR=/tmp/r327-mpl .venv/bin/python -m photo2.r327.runner --output /tmp/r327-initial --budget 600
```

This entry intentionally reproduces the archived 20-pass diagnostic with the old
cycle-witness builder. The delivered continuation is `photo2.r327.continue_run`:
it starts from the preserved diagnostic bank under
`photo2/r327/development/cycle-prefix-run`, uses minimal conflicting cycle cuts,
and spends only the balance of the cumulative 600-second refinement allowance.
Always supply a fresh output directory:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MPLCONFIGDIR=/tmp/r327-mpl .venv/bin/python -m photo2.r327.continue_run --output /tmp/r327-continued
```

`--pilot /tmp/r327-initial` continues your own reproduced diagnostic instead.
The measured time budget
makes the final pass count host-dependent; compare specified bank states for exact
arithmetic instead of asserting identical wall-clock stopping.

The source of all scores is `evidence.py`. Models share geometry across bead colors;
only support-localization sigma differs. Black targets use colored anchors when at
least six are available. Affine and ridge-curved predictions exclude the target.
The native signal is linear white minimum for black, red excess for red, and
red/green minimum minus blue for yellow; each uses the same 3-pixel Gaussian.
The evidence objective combines target prediction, native response and supported
runs. Existing R325 cyclic overlap/triple factors remain. Whole-hypothesis selection
still uses the declared max-marginal-regret surrogate, not exact photographic MAP.

Checks:

```sh
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/r327-mpl .venv/bin/python -m photo2.r327.tests
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/r327-mpl .venv/bin/python -m photo2.r327.verify
/home/rharris/.local/bin/beads-chromium-review photo2.r327.browser_check
```

Verification writes only its new R327 receipt. `analyze.py` and `review.py` are
post-freeze analyses and write their R327 output locations; copy/change `OUT` before
rerunning them to preserve original analysis receipts. `analyze.py` is the only
new module that reads historical R161 labels, through retrospective evaluation.
No R161 labels, maker constraints, fitted 3D models, count or color period enter
candidate selection. Cross-prediction does not create independent ground truth.

The delivered primary also runs `python -m photo2.r327.select_working` after the
continuation. This compares all saved witnesses against R326 under a fixed objective
and chooses the strongest sampled compatible incumbent. It writes the default R327
results directory; preserve/copy that directory before repeating. The preselection
continuation graph and seal are archived under `development/continuation-final`.
The original diagnostic, continuation and incumbent comparison all precede R161
scoring. No graph selection depends on the subsequent reference result.

The final delivered epoch additionally runs `photo2.r327.shape_refine`, which reads
the preserved `development/before-shape` bank, and applies native shared geometry.
The first broad pigment mask and its failed native crop audit are preserved under
`development/broad-pigment-mask`. The final segmentation uses red/yellow chromaticity
to exclude pink paper and unlike neighboring pigment. `shape_refine`, `shape_review`
and `final_controls` write the delivered output directory: use a copied worktree or
change `OUT` before repeating. The final primitive-direction penalty and every
native pigment pixel/covariance are in `shared-shape-evidence.json.gz`.

Final checks also include:

```sh
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/r327-mpl .venv/bin/python -m photo2.r327.shape_review
PLAYWRIGHT_BROWSERS_PATH=/home/rharris/.cache/beads-playwright .venv/bin/python -m photo2.r327.shape_browser
```

`final_controls.py` is the final-mask causal test. `broad-mask-ablations.json.gz`
and the earlier controls in the development archive belong to their named epochs.
The eight alternative configurations retain their generation-epoch cyclic gaps;
all fixed working scores were recomputed with the final mask. Final primary states
are exactly unchanged by the mask correction, so position/native-response
consequences and reference recovery remain exact. No additional label-driven
selection was performed. The final report gives both measured refinement allowances.
