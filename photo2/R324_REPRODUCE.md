# Reproduce R324

Open `photo2/r324/results/index.html` directly from disk. Eight compact figures
cover the whole photo, conditional indices, coverage, frozen projection, bridge,
before/after fit, error versus index and timings. Original bridge RGB is included.
All delivered model maps are conditional; read `bridge-use-policy.json` first.

From the repository root:

```sh
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/r324-mpl .venv/bin/python -m photo2.r324.verify
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/r324-mpl .venv/bin/python -m photo2.r324.verify_physical
/home/rharris/.local/bin/beads-chromium-review photo2.r324.browser_check
```

These update verification receipts, not frozen scientific results. The first
command independently checks the graph and executes a read-guarded complete
fast replay into a fresh `/tmp/r324-guarded-*` directory. Expected scientific
outputs are exact; timers/RSS/source bindings differ. Original source executed
for the primary graph is archived in `development/tracker-executed.py`; the
frozen `tracker.py` differs only by an explanatory beam comment. `fast_tracker.py`
adds two measured caches. Primary graph, freeze and R161 evaluation remain intact.

For a new isolated photo pass, without overwriting the delivery:

```sh
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/r324-mpl .venv/bin/python -m photo2.r324.fast_tracker --output /tmp/r324-new-photo
```

Runtime inputs are only `beads-photo-2.jpg`, R275 appearance pixels/colors and
`spline-seed-r175.json`, regenerated with R250's geographic spline procedure.
No R161 graph, model positions or rendering code enter detection. The full-photo
mask fills only holes smaller than600 pixels; filling the whole necklace's
central paper would be incorrect. The detector remains photograph/palette specific.

The delivered experiment entry points are `bridge`, `coupled`, `fit`, `expand`,
`benchmark`, `optical_speed`, `analyze`, `finalize_metrics` and `review` under `photo2.r324`.
**They write their fixed R324 result directory: copy the experiment and change
`OUT` before rerunning them if preserving the delivery.** They were run in that
order except that the bridge ran before frozen comparison, and the final
strict-bridge fitting epoch superseded the preserved initial exploratory epoch.
`coupled` never changes a frozen model; it verifies saved positions first.
`fit` excludes graph correspondences beyond x1510; `expand` inherits that cohort.
Both retain all physical bodies and independently measured surface guards.

Reusable physical interfaces in `coupled.py`:

* `support_ledger(scene, observations, pixels)` traces actual first-hit ownership.
* `correspond(scene, nodes, observations, fractions)` compares all origins,
  two family assignments and reversals; it does not establish physical truth.
* `optical(scene, targets, reflections, mapping, scope, grouped=True)` evaluates
  native visibility, full-chain contact/shadows and connected reflection centroids.
  Missing predictions are not dropped. `grouped=True` is the exactly checked
  whole-array scan replacement.

The native `benchmark`/`optical_speed` outputs measure costs, not convergence.
The final runtime plan additionally uses observed fit Jacobian costs and a measured
local-guard overhead; scenario iteration counts and overhead factors are explicit
planning assumptions. The complete observed loop remains disconnected, so no
modular N equation or final pattern can be inferred from this reproduction.

Do not rerun maker evaluation to tune the detector and describe the result as a
fresh holdout. The existing reference partition and score are frozen. Browser
checks cover local links, image loading, narrow layout and offline operation.
Review/documentation generation uses original RGB; native measurements never
use downsampled review images. No original scene or old scientific files change.

Stop after review. No automatic R325 or larger optimization is part of reproduction.
