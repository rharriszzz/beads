# Reproduce R343

Base: R342 `4536b40341ed7151513d61b74c445ce6b6d4a4a8`, branch `photo-2-strategy-v3`. All active scientific work is under `photo2/r343/`. Historical results and stopped untracked R340 files remain untouched.

From the repository root:

```bash
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r343/reference_views.py
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/beads-r343-mpl .venv/bin/python photo2/r343/hsv.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r343/empirical.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r343/associate.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r343/provenance.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r343/position29.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r343/freeze.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r343/pattern.py
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/beads-r343-mpl .venv/bin/python photo2/r343/review.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r343/verify.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r343/replay.py
/home/rharris/.local/bin/beads-chromium-review photo2.r343.browser_check
```

`R343_RUN_ROOT` redirects generated artifacts. `replay.py` runs all ten scientific stages in a fresh `/tmp` directory, comparing20 decoded science products,26 exact images, the vector plot, CSV and offline HTML/data/JS/CSS. JSON comparison ignores only UTC and dependent SHA256 fields; fresh verification checks producer hashes and historical seals independently. SVG identifiers/date are deterministic. Browser checks use the delivery review separately.

`glass_regions.py` contains25 explicitly inspected material-core annotations and four deferred unsafe sources. These annotations are photographic scientific inputs, not automatic body segmentations. `sample.py` chooses the3×3 with greatest minimum clearance, requiring2pixels. `hsv.py` exports individual source RGB/HSV pixels at that same2pixel clearance; it keeps illustration/software labels separate from explicit maker pigments and excludes lowS/V hue interpretation. No pigment is inferred from the pattern. Black recognition is not modified or refitted.

`empirical.py` describes source-pixel/value strata and coarse joint-HSV overlap, without fitting a pigment classifier or lighting law. All five29 sources and the127 investigation are excluded from reference comparisons. `position29.py` saves all five body samples, authority sources, primitive-neighbor intersections and native fits.

`provenance.py` refines exactly one existing observation: NEW-1519-2976 remains protected red, with general approval preserved and individual pigment confirmation false. The calibration counterfactual removes only its reference influence, never its label. Legacy ledgers and all other authority entries remain intact.

`associate.py` evaluates one saved cue. Maker-yellow material is distinct from independent bead identity. Actual native body inspection, an empty unique site, three native neighbor links/two existing triangles, spacing, nonintervention and original-cache alias evidence support the working C62 admission. It does not forge a maker identity confirmation, recenter a cue, or use old dark-component growth. Existing R336 corridor checks are reused solely as exclusion gates, never as pigment or identity proof.

`freeze.py` applies Q101 yellow, appends the targeted authority annotation and C62 admission, then hashes the evidence before strict208 scoring. `pattern.py` separates unchanged common cohorts from the expanded cohort and keeps all11 unresolved sequence entries unknown. The CSV explicitly writes `?` for conflicts and insufficient positions. There is no new length/winding/renderer search.

`verify.py` independently converts every source RGB with scalar `colorsys`, derives clearance patches through brute-force pixel distances rather than the producer EDT, checks the alias/native geometry through normal equations and direct corridor interpolation, checks all old/new graph equations and unique sites, independently reconstructs strict consensus and all held-out probabilities, and validates literal crops. Native annotations/identity judgments are replayed inputs, not an independent second human inspection. Superseded initial label-ingestion and full-core-before-inset experiments remain under `development/`.
