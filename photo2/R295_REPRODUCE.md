# R295 reproduction

Run from the repository root with the existing Python3.12 `.venv`.

```bash
.venv/bin/python -m unittest photo2.r295.tests
.venv/bin/python -m photo2.r295.audit --replay
/home/rharris/.local/bin/beads-chromium-review photo2.r295.browser_check
git diff --check
```

`audit --replay` writes temporary outputs and replays the complete 80-start screen,
all six local/four global/three geometry/two joint candidates, every recorded trial
parameter and score, paired sensitivities and common-light refinement. It then
recomputes native evaluations, independent physical audits, all221-position exports,
visibility arrays and review PNGs. No original experiment is rewritten. Early fits
use their saved source checkpoint, before the additional volume-fallback classifier;
later stages use their final source. Source hashes/timestamps are provenance metadata,
not numerical result fields. Audit logs are kept under R295 checkpoints.

The immutable input freeze and final selection freeze are in `r295/evidence`.
`freeze.py` refuses overwrite. `finalize --resume-frozen` requires identical frozen
principal parameters and inputs. The separate `hand-plus` export comes from the
already fitted joint candidate; its label correction is documented, not a refit.
All original source rows are retained verbatim. R294's seven historical supports
are also evaluated with its exact original one-to-one rule for fair comparison.

For individual stages in a new destination, set `R295_OUTPUT=/tmp/<new-results>`
and `R295_REVIEW=/tmp/<new-review>`. The ordered modules are `fit screen`,
`fit local`, `fit global`, `fit revision`, `joint`, `sensitivity`,
`finalize --resume-frozen`, `complete_comparisons`, `review`. Prefer the complete
replay helper for original checkpoint fidelity. `physical_audit` additionally
reclassifies every failed screen; `contact_fallback.audit_pair` reproduces the
independent actual-volume overlap witness saved in `inconclusive-volume-audit.json`.

Open `photo2/review/r295/index.html`, or serve the checkout:

```bash
.venv/bin/python -m http.server 8295 --bind 127.0.0.1
```

Then visit `http://127.0.0.1:8295/photo2/review/r295/`. View selection, zoom,
original/model toggle, unobstructed native crops, and full native images work
without external services. The review creates no human feedback or new labels.

Only the original EXIF-oriented photograph is scientific image evidence. No POV-Ray
or synthetic photographs are used. The analytic surface sampler is an independent
geometry check, not photographic truth. Photo coordinates are native x-right/y-down;
physical dimensions use source construction units. Guard indices−45…250 provide
occlusion context; only−20…200 count as the requested run. No model-assigned material
colors or inferred repeating pattern appear in position exports.
