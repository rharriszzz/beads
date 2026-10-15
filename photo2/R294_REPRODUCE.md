# R294 reproduction

Use the existing Python3.12 `.venv` from the repository root. Only native real-photo
pixels and preserved Phase1 records are used. No renderer or synthetic image/scenario
is required. The literal annular geometry is Python mathematics from prior rounds.

Review `photo2/review/r294/index.html` directly, or serve the repository:

```bash
.venv/bin/python -m http.server 8294 --bind 127.0.0.1
```

Open `http://127.0.0.1:8294/photo2/review/r294/`. All full-resolution images and CSVs
are static links. There is no new feedback ledger or manual-label requirement.

Verification, including independent full optimization and image reproduction:

```bash
.venv/bin/python -m photo2.r293.completed_review --check
.venv/bin/python -m unittest photo2.r294.tests
.venv/bin/python -m photo2.r294.physical_audit
.venv/bin/python -m photo2.r294.audit --replay
/home/rharris/.local/bin/beads-chromium-review photo2.r294.browser_check
git diff --check
```

`audit --replay` reruns both complete searches, physical selection, native visibility,
all correspondence/uncertainty exports and review generation in a temporary directory.
It compares every fit candidate/history scientifically, all ten evaluation/export/
visibility files byte-exact, all review PNGs and the manifest. Fit source-manifest
metadata differ because evaluation/review/test modules were added after the first
fit; no numeric scientific fields are excluded. It also verifies12766 historical
science files and69 live feedback files against the pre-fit hashes.

The existing `evidence/inputs.json.gz` is immutable: exact source objects, native
photo/source hashes, anchor candidates/selection and geographic split.
`freeze.py` refuses to overwrite it. Its original freeze was made before all fits.
Do not rerun `evaluate diagnose` in the historical directory: the original
training-only diagnosis and proposed change are preserved in `checkpoints/`.

To rerun a selected stage elsewhere, set `R294_OUTPUT=/tmp/<new-directory>` and
optionally `R294_REVIEW=/tmp/<new-review-directory>` for the module invocation:

```text
photo2.r294.fit initial
photo2.r294.fit revised
photo2.r294.evaluate compare
photo2.r294.review
```

Both fits use only training observations; `fit revised` also reads the original
recorded initial diagnosis and selects only candidates with contact certificates.
The first unconstrained revision, its exposed evaluation, correspondence exports
and images survive in `checkpoints/unconstrained-revision/`. The subsequent change
was a physical-feasibility selection among the existing four candidates, with no
optimization or holdout-based tuning. The failed light policy (no yellow reflection
candidates) is retained there; the final pooled mirror-direction diagnostic does
not change geometry or source observations.

Coordinates are EXIF-oriented original pixels, x right/y down; overlays are native
2540×3182. Enlarged crops use nearest-neighbor presentation and retain separate
unmarked native PNGs. XYZ uses source-construction units, z relative to the axis
plane; scale/elevation are conditional. Guard indices−45…250 provide occluders;
only−20…200 are exported as the requested run. An extended−65…270 guard test checks
ownership at requested indices. Model-only color is null. Source context colors
and pixel measurements remain unchanged in the frozen linked records.

Implementation checkpoints retain the initial technical parenthesis error in the
diagnosis notes, the unconstrained packing failure, the exact first optimization
logs and later replay logs. The report distinguishes primary from failed results,
requested run from end context, compatibility from accuracy, and sensitivity from
calibrated confidence. Stop after R294 delivery; no automatic R295.
