# Reproduce R326

Open `photo2/r326/results/index.html` directly. Four fixed native-photo comparisons
show the upper bridge, inward-bend reconsideration, provisional black site and
lower-bend closure. No web service, generated image or large interactive viewer is
needed. The original photograph is unchanged.

Run a fresh complete detector into a NEW directory; never omit `--output` when
preserving the delivered result:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MPLCONFIGDIR=/tmp/r326-mpl .venv/bin/python -m photo2.r326.runner --output /tmp/r326-new
```

This regenerates the exact R325 baseline from original image measurements, then
executes three context/candidate/global refinement passes. It never reads R161,
old graph identities, 3D models or pattern constraints. Runtime is approximately
106s on this host, not a guarantee. The reported stop is the bounded three-pass
allowance; changes still occur in the final pass.

For 146-observation lower-bend practice, explicitly reuse the R325 measurement bank:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MPLCONFIGDIR=/tmp/r326-mpl .venv/bin/python -m photo2.r326.runner --practice --cached photo2/r325/results/graph.json --output /tmp/r326-practice-new
```

The cached bank saves initial measurements; all changed contexts and their fits
are freshly computed. This is not a cold-detector speed comparison.

Verification commands from the repository root:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MPLCONFIGDIR=/tmp/r326-mpl .venv/bin/python -m photo2.r326.tests
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MPLCONFIGDIR=/tmp/r326-mpl .venv/bin/python -m photo2.r326.verify
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MPLCONFIGDIR=/tmp/r326-mpl .venv/bin/python -m photo2.r326.verify_supplement
/home/rharris/.local/bin/beads-chromium-review photo2.r326.browser_check
```

`verify` checks the scientific seal and independent pixel/equation arithmetic,
then runs an approximately 108s fresh read-guarded replay in `/tmp`. Only the JPEG,
R275 appearance inventory and spline seed are permitted repository data reads.
Receipts/logs are rewritten; scientific detector artifacts are not. Timing and
source bookkeeping are excluded from exact replay comparison. Historical source
and results are never modified.

`global_solver.py` remains in R325, unchanged. R326 `contexts.py` measures and caches
sizes/offsets and transports selective proposals. `compatibility.py` jointly
selects whole hypotheses under all-overlap and cycle constraints. Its max-marginal
regret objective is explicitly a surrogate, not an exact full photographic MAP.
`black.py` and`black_contexts.py` preserve provisional native-pixel provenance and
colored-only fit witnesses. Existing no-addition candidates remain available.

`evaluate.py`, `analyze.py`, `compatibility_feasibility.py`, `alternatives.py`,
`practice_benchmark.py` and`review.py` write fixed R326 result locations. They are
post-freeze analyses, not detector imports. Copy/change their output constants
before repeating them against a preserved delivery. `alternatives.py` adds eight
explicit compatible counterfactuals to the root`model-input.json`; it does not
change the frozen primary graph or strict constraints. `verify_supplement` also
adds verified winding summaries to`closure-investigation.json`.

Large intermediate scientific JSON files in`development/` and iteration snapshots
are losslessly gzip-compressed for delivery. Read with`gzip.open(path, 'rt')` or
extract into a temporary directory. The primary graph, contexts, model interface,
iteration receipts and supporting source stay directly readable. Compression
receipts bind original and compressed bytes. Archived failed/prototype outputs
are evidence, not alternative adopted results.

The strict model interface contains only 17 links/30 indexed observations. The
1,833-link candidate remains conditional. All 174 historical disagreements remain
unresolved, all four old closure pairs remain context-contested, and neither N nor
a color period is established. Stop after scientific review; no automatic R327.
