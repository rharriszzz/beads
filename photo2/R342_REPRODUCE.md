# Reproduce R342

Base: R341 `ef3a8137`, branch `photo-2-strategy-v3`. All active R342 work is under `photo2/r342/`; earlier untracked stopped R340 experiments remain untouched and unused.

From the repository root, use `.venv/bin/python` with `OPENBLAS_NUM_THREADS=1`:

```bash
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r342/maker.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r342/experiment.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r342/native_panels.py
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/beads-r342-mpl .venv/bin/python photo2/r342/hue_diagnostic.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r342/coverage.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r342/candidate_checks.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r342/consistency.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r342/native_review.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r342/excluded_controls.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r342/freeze.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r342/pattern.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r342/review.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r342/verify.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r342/replay.py
/home/rharris/.local/bin/beads-chromium-review photo2.r342.browser_check
```

`R342_RUN_ROOT` redirects generated outputs. `replay.py` runs all13 scientific stages in a fresh `/tmp` directory and compares28 decoded science products,31 exact images and offline HTML. It ignores only UTC and dependent producer SHA256 fields in cross-run JSON comparison; fresh verification independently validates the producer graph hash and historical input seal. Browser checks use the delivery directory separately.

`recognize.py` is the complete fixed-pixel black measurement. Three predeclared fixed-size alternatives are compared on development only; the64 reserved maker labels do not select a variant. The selected offset core has no spacing/orientation fit and no neighbor clipping. Native safety judgments are separately explicit in `native_review.py`; they are not extra hidden black rules. Raw output, fixed18pixel outline eligibility and native vetoes remain separate. All three raw disagreements are documented. The four maker corrections are the only accepted changes.

`hue_diagnostic.py` supplies the separate circular HSV hue comparison. No red/yellow automatic recoloring is adopted. The abandoned channel-ratio experiment and the initial rejected false-positive-first selection are preserved under `development/`; neither is in the selected pipeline. Hue never influences blackness or identity.

`coverage.py` and `candidate_checks.py` inspect saved cues only, preserve R338/R336 duplicate vetoes and admit no bodies. `consistency.py` enumerates the complete same-neighbor primitive-cell intersections of the six red conflict sources. One actual two-link patch substitution is saved and rejected for occupied-site duplication plus a49.29px native error. It is not applied to the active overlay. No growth engine, color-voting detector, physical renderer or winding search is invoked.

`freeze.py` writes the maker overlay and native evidence hashes before `pattern.py`. Pattern scoring keeps identical cohorts, geographic guards and held-out occurrences, including matched1036 unchanged targets. Optional Q102/Q169 exclusions are separately named. The partial sequence keeps all13 unresolved entries unknown. Proper-divisor witnesses establish only conditional primitivity of the partial208 block.

`verify.py` independently enumerates all candidate3×3 native maxima and masks without calling the detector; recomputes hue via scalar `colorsys`; checks unchanged geometry, maker protections, all strict entries without `motif/metrics`, and all held-out probabilities without `predict`. Its native annotations are replayed inputs, not a second human review. The offline review has two questions and16 literal native panels, each with target1 and its own stable-ID key; candidate links are visibly separate from accepted links.
