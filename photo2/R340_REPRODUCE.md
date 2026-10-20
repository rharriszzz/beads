# R340 reproduction — automatic material regions

Authoritative scientific output: `photo2/r340/autoregion/`. The completed manual diagnostics under `quick-diagnostic/` and `material-diagnostic/` are inputs and remain unchanged. Earlier stopped untracked R340 development files are unused.

From the repository root:

```
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r340/autoregion/explore.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r340/autoregion/panels.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r340/autoregion/run.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r340/autoregion/evaluate.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r340/autoregion/freeze.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r340/autoregion/pattern.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r340/autoregion/review.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r340/autoregion/verify.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r340/autoregion/replay.py
/home/rharris/.local/bin/beads-chromium-review photo2.r340.browser_check
```

`explore.py` preserves the rejected disk geometry, not the selected classifier. `run.py` selects the single final rectangle from only the odd24 manual geometric annotations. `recognize.py` is the complete selected pigment computation. All thresholds/patch sizes stay fixed. `freeze.py` contains explicit native ownership judgments for the four accepted corrections and separate diagnostic witness rectangles for the four error cases. Those witnesses never enter automatic decisions. The complete active inventory and earlier maker-authority ledger are inherited from R339.

`R340_MATERIAL_RUN_ROOT` redirects generated selected-round outputs, keeping all historical inputs fixed. `replay.py` creates a fresh `/tmp` directory, runs run/evaluate/freeze/pattern, and compares eight decoded scientific artifacts. Only `seconds`, `utc`, `classification_sha256` and `freeze_sha256` are excluded: exact producer hashes include variable runtimes, and current hashes are independently verified. Graphs, all pixels, region bounds, labels, model coefficients, evaluations and strict pattern entries compare exactly. See `replay-verification.json`.

`verify.py` separately recomputes all candidate3×3 maxima with explicit loops against the original JPEG, all1058 common spacings directly from native primitive links, all2287 modulo-H equations, all2496 strict208 cohort entries and all historical input hashes. No full old classifier regression, physical-rendering or broad pattern/winding search is required.

The offline review uses only local files. Its complete inventory viewer derives local photograph numbers anew for the currently selected target, always target1, and uses the same key in the matching current-color adjacency diagram.
