# Reproduce and inspect R323

Open `photo2/r323/results/index.html` directly from disk. All images use original
RGB. The full view includes fragments and uncertainties; the clean view has only
the two accepted diagonal families; indexed labels show component:A-index/color.
The failure comparison includes post-freeze maker labels. No internet is needed.

From repository root, using the existing `.venv`:

```sh
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/r323-mpl .venv/bin/python -m photo2.r323.verify
```

This checks all saved hypothesis arithmetic, supports, graph edges, indices and
raw R161 validation; it also runs the detector under a repository read guard into
a fresh `/tmp/r323-replay-*` directory. It updates only the R323 verification
receipt, not the frozen scientific graph. Timings vary; scientific outputs must
match exactly. Original R322 files are read, never rewritten.

For a fresh detector run **outside the frozen delivery**:

```sh
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/r323-mpl .venv/bin/python -m photo2.r323.tracker --output /tmp/r323-fresh
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/r323-mpl .venv/bin/python -m photo2.r323.review --output /tmp/r323-fresh
```

Runtime data inputs are `beads-photo-2.jpg` and
`photo2/review/r275/inventory.json`, plus source hashing. The catalog contributes
only bright supports, location/color cues and descriptive historical status;
station groups, physical identities and model geometry are ignored. R322's
preprocessing, spectral helper and observation extraction code are reused without
modifying its source. The new tracker sets that imported module's crop in memory;
it does not rewrite an R322 source/output file. Use a separate process per run.

`freeze.json` binds the primary source, output, observation export, local-winner
ablation, evaluator and inputs. The sole primary R161 scoring is in
`validation.json`. Do not tune the detector against it and continue describing
new scores as held out. The evaluator and diagnostic deliberately read the maker
chart; they are separate from detection:

```sh
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/r323-mpl .venv/bin/python -m photo2.r323.evaluate
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/r323-mpl .venv/bin/python -m photo2.r323.diagnose
/home/rharris/.local/bin/beads-chromium-review photo2.r323.browser_check
```

Re-running evaluation changes its timestamp, not the frozen graph. The diagnostic
adds maker numbers after freeze to the requested failure illustration. `review`
creates the generic image-only illustrations; `diagnose` should follow it to
restore the delivered labeled failure comparison. Run `python -m photo2.r323.uncertainty_review` to restore the delivered
side-by-side competing-hypothesis cards. The delivered HTML additionally
contains the measured held-out summary and links, recorded by `finalize_review.py`.

The predeclared joint-selection ablation can be regenerated with
`python -m photo2.r323.controls`; do this only in a copied experiment if preserving
the frozen receipt, since its measured timing changes. It uses the same candidate
bank with independent local winners, not a new fitted or chart-assisted detector.

Development archives retain the first serialization-failing source, the completed
single-spectral/60px-stride run, and the multiple-spectral/40px-stride run before
additional provenance/timing fields. These are exploratory sources/results, not
independent R161 validations. No historical photograph, maker graph or R322 result
was replaced. All finite bounds/thresholds are exploratory.

Stop for scientific review. No automatic R324, new3D optimization or color-pattern
completion follows reproduction.
