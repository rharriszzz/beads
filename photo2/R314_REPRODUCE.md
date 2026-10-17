# R314 reproduction

Use the repository Python 3.12 environment. The committed measurement arrays and
search epochs are sealed. Do not overwrite them to reproduce a fit. All old R313
sources, evidence and scores remain unchanged.

## Inspect

Open `photo2/r314/results/index.html` in a browser. This is an offline static review;
click PNGs for native-resolution exports. The original native photo crop is included.
The all-model JSON exports contain complete positions, frames, contact witnesses,
physical target -100..99, per-core metrics and all geographic splits. Complete target
rasters and visibility ledgers retain hidden/unmeasured beads and context occluders.

## Validate the delivered computation

```bash
MPLCONFIGDIR=/tmp/r314-mpl OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  .venv/bin/python -m unittest photo2.r314.tests photo2.r314.tests_extra
MPLCONFIGDIR=/tmp/r314-mpl OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  .venv/bin/python -m photo2.r314.verify
```

The verifier writes only its R314 receipt. It rebuilds the tiny C++ marcher under
`/tmp` if needed; the library filename binds its source hash. The original Python
marcher independently verifies saved rays. All positions and pair certificates are
checked, as are source hashes, selection, penetration witnesses and preserved history.
After subsequent commits, the historical-preservation test intentionally rejects
unrelated modifications to pre-R314 tracked files; use the delivered commit in an
isolated checkout for an exact verification.

## Original execution

```bash
MPLCONFIGDIR=/tmp/r314-mpl OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  .venv/bin/python -m photo2.r314.evidence
MPLCONFIGDIR=/tmp/r314-mpl OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  .venv/bin/python -m photo2.r314.run prepare
MPLCONFIGDIR=/tmp/r314-mpl OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  .venv/bin/python -m photo2.r314.run fit --seconds 540
MPLCONFIGDIR=/tmp/r314-mpl OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  .venv/bin/python -m photo2.r314.run finalize
```

Preparation/search refuse a sealed result. The `evidence` command is only for a
separate disposable checkout with the destination removed/redirected; it would
otherwise overwrite the R314 evidence freeze. No historical R313 artifact is written.
The initial rejected three-sample preflight is under `preflight-v0`. The interrupted
JSON-order ranking epoch is under `search-epoch0`, including sources and every saved
proposal. The valid epoch's source manifest is `results/search-plan.json`; an exact
source copy is retained under `source-epoch1`. Search duration is wall-clock bounded,
so the random proposal sequence is deterministic but its final truncation can differ
on another machine. This runner does not claim a tested resumable search protocol.

Post-selection exports were made with:

```bash
MPLCONFIGDIR=/tmp/r314-mpl OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  .venv/bin/python -m photo2.r314.diagnostics geometry
MPLCONFIGDIR=/tmp/r314-mpl OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  .venv/bin/python -m photo2.r314.diagnostics optics
MPLCONFIGDIR=/tmp/r314-mpl .venv/bin/python -m photo2.r314.boundary_audit
MPLCONFIGDIR=/tmp/r314-mpl .venv/bin/python -m photo2.r314.review
MPLCONFIGDIR=/tmp/r314-mpl .venv/bin/python -m photo2.r314.report
```

These commands reproduce diagnostics, not new fitting. The optical diagnostic uses
unchanged shared illumination and never chooses an assignment by reducing optical
error. No reliable physical correspondence cohort exists; its empty eligible maximum
is unavailable, not zero. Connected observed components, predicted components, faint
local maxima, multiple/tied peaks and sampling sensitivity remain in the gzip ledgers.

Numerical bounds, geometric readiness limits and lobe-tracking motion thresholds are
engineering controls, not measurements of the actual glass. The paper support plane
check does not prove mechanical equilibrium. See the report for all unfulfilled goals.
