# Reproduce R285

Run from repository root on photo-2-strategy-v3 using Python3.12 `.venv`.
Dependencies already installed: NumPy, SciPy, scikit-image, Pillow, Matplotlib,
POV-Ray and Playwright/Chromium. See results/environment.json for exact versions.
No later-phase model, historical correspondence chart or manual bead labels are
inputs to the detector. Rendered identity masks are evaluation-only.

```
.venv/bin/python -m photo2.r285.select
.venv/bin/python -m photo2.r285.sample_review
.venv/bin/python -m photo2.r285.run
.venv/bin/python -m photo2.r285.run --stage confirmation
.venv/bin/python -m photo2.r285.reflections
.venv/bin/python -m photo2.r285.mechanisms
.venv/bin/python -m photo2.r285.synthetic
.venv/bin/python -m photo2.r285.assess
.venv/bin/python -m photo2.r285.review
.venv/bin/python -m photo2.r285.review confirmation
.venv/bin/python -m photo2.r285.package
.venv/bin/python -m unittest photo2.r285.tests photo2.r284b.tests photo2.r284.tests photo2.r283.tests photo2.r282.tests
.venv/bin/python -m photo2.r285.run --output /tmp/beads-r285-replay
.venv/bin/python -m photo2.r285.audit
/home/rharris/.local/bin/beads-chromium-review photo2.r285.browser_check
```

Keep results/candidate-freeze.json: confirmation asserts its method-source hash;
never regenerate it to hide post-confirmation changes. The initial extreme-only
selection survives in selection-first-ranking.json. Final select.py reproduces
the balanced16, including four mandatory observations; no manual coordinates enter
methods.py. Checkpoints document the empty fresh-cue stratum and revised selector.
The first selection is a historical failed sampling experiment, not overwritten
by the final reproducible selection. All D/G failures and S confirmation failures
remain in the measured results. No new production inventory is exported.

`development.json.gz` contains203 fixed colored cues, all five methods, exact native
supports/centroids, native ICC luminance, seed refinement, threshold values, all
basin interfaces and saddle decisions,32/48-domain sensitivity and overlap pairs.
`confirmation.json.gz` contains eight spatially disjoint colored cues.
`reflections.json.gz` contains46 preserved cues plus two new confirmation anchors,
R1/R2/R4 native supports and separate subpixel contours, levels/peaks/stability.
`diagnostics.json.gz` separates full bank,74 old-high-source cues,10 prioritized
review cases and confirmation. The old-high label is not verified truth.
`synthetic/scene-*` saves POV source, raw linear PNG, converted analysis-sRGB PNG,
inference before identity rendering, truth/certificate and evaluation. No physical
fitting is run. Four scenes use new seed285501. Synthetic scene parameters are
benchmark inputs only and never enter real-photo inference.

Open `photo2/review/r285/index.html`. Top-level J/S panels keep the review small;
expand each case for original A, failed D/G, exact masks, brightness profiles,
saddle route and metrics. Native thumbnails are unmodified pixels. Review labels
and captions are evaluation evidence only. Source hashes and preservation audit
explicitly allow the requested permanent PHASE1_MEASUREMENTS.md edit.
