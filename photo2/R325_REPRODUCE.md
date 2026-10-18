# Reproduce R325

Open `photo2/r325/results/index.html` directly from disk. It embeds the unchanged
original JPEG bytes so native canvas access/download works offline. Both diagonal
families, conditional identities, all 19 old breaks, the winding gap and colored
predictions can be inspected without generating a large crop collection. Pink
links are contested by changed-size photographic contexts. One candidate component
is not a certified physical reconstruction; conservative model use has 23 components.

From the repository root, use the existing Python 3.12 environment:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MPLCONFIGDIR=/tmp/r325-mpl .venv/bin/python -m photo2.r325.tests
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MPLCONFIGDIR=/tmp/r325-mpl .venv/bin/python -m photo2.r325.verify
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MPLCONFIGDIR=/tmp/r325-mpl .venv/bin/python -m photo2.r325.verify_supplement
/home/rharris/.local/bin/beads-chromium-review photo2.r325.browser_check
```

Verification rewrites only its receipts/logs. `verify` executes a complete guarded
replay in a fresh `/tmp/r325-guarded-*` directory. It permits measurement reads only
from `beads-photo-2.jpg`, `photo2/review/r275/inventory.json` and
`photo2/spline-seed-r175.json`. It compares graph decisions, alternatives, original
pixel supports and colored-first predictions exactly, excluding source/timer fields.
The detector never reads R161 labels, R324 graph identities or a 3D model.

For a separate full photographic pass:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MPLCONFIGDIR=/tmp/r325-mpl .venv/bin/python -m photo2.r325.tracker --output /tmp/r325-new
```

Do not omit `--output` when preserving the delivered scientific artifacts. The
module's default writes `photo2/r325/results`. The tracker exports the primary
**conditional global candidate**, not the post-freeze context-screened model interface.

`global_solver.py` implements cyclic second-order max-sum and exact max marginals;
`consistency.py` checks simultaneous integer equations with free holonomy;
`candidates.py` fits colored-only grids and reuses neighboring candidate geometry
bidirectionally. `observations.py`, `batched_fit.py` and `spectral.py` implement the
measured optimizations. All have unchanged-reference controls in the result files.

The following analysis/benchmark modules write the fixed R325 result directory:
`practice`, `fit_benchmark`, `practice_measured`, `spectral_benchmark`, `controls`,
`analyze`, `closure_analysis`, `context_check`, `screening`, `model_compare`, `review`
and `evaluate`. Copy/change `OUT` before rerunning them against a preserved delivery.
In particular, `analyze` produces the unscreened interface, and `screening` must run
**once afterward** to produce the delivered conservative interface. Do not apply
`screening` twice to an already screened export. `evaluate` is the historical R161
check and validates a freeze manifest; it is not a detector parameter search.

Practice generation uses cached window geography for windows 65–93, regenerates
original RGB spectra and candidates, and includes whole-image preprocessing in
each isolated run. The modes `reference`, `optimized_reference`, and `global` have
separate performance/science outputs. The exact reference control compares its
accepted and unresolved edge lists and coordinates, not just aggregate counts.

`context_check` is a post-freeze stress test with 63 windows at sizes160/240/280.
It reads the frozen global graph only to select comparisons; it does not alter or
train the solver. Those local alternatives are counterevidence, not ground truth.
`screening` excludes context-contested edges from default fixed model constraints
and rebases the remaining connected pieces. The global candidate is retained as a
separately named alternative. Do not treat any unknown gauge as a measured N.

`model_compare` reuses SHA-bound frozen R324 native support-owner ledgers for the
unchanged R321 N3000/N2800 models. Its one-origin comparisons are conditional
model/photo diagnostics, never detector inputs or new photographic labels.
`closure_analysis` exports all supported competing deltas for the unresolved
winding cut, their conditional counts and modular-collision witnesses. No count
or repeat is adopted. No expensive fitting process was launched.

The first global scientific epoch and source are preserved in
`photo2/r325/development/first-scientific/`, with JSON and source copies losslessly gzip-compressed.
Its R161 result predates performance-only changes. The final pass adds explicit
colored-anchor audit fields; every selected hypothesis/edge/index is unchanged.
See `performance-comparison.json`, `scientific-seal.json`, source bindings and
`delivery.json` for timing, preservation and publication details.

Stop after review; no automatic R326 or fitting is authorized by this reproduction.
