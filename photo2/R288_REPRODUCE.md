# R288 reproduction and evidence map

Repository root, Python3.12 `.venv/bin/python`; branch photo-2-strategy-v3.
Baseline e46b2c23699332c4668532fc813c35dae24c82e3. Original photograph and all
historical experiments are preserved. The permanent PHASE1_MEASUREMENTS.md contract
is the explicitly authorized audit exception.

Chronology: requirements → completed J/M explanation/hash → frozen15-region
selection → original-M causal replay → E/W and H development → preserved first-W
narrow-bridge failure → central-route correction → frozen sources/parameters →
confirmation with no retuning. Do not refreeze against confirmation results.

```bash
.venv/bin/python -m photo2.r288.diagnose
.venv/bin/python -m photo2.r288.diagnosis_review
.venv/bin/python -m photo2.r288.run --output /tmp/beads-r288-replay
.venv/bin/python -m photo2.r288.run --stage confirmation --output /tmp/beads-r288-replay
.venv/bin/python -m photo2.r288.evaluate
.venv/bin/python -m photo2.r288.ownership
.venv/bin/python -m photo2.r288.mechanisms
.venv/bin/python -m photo2.r288.review
.venv/bin/python -m photo2.r288.review confirmation
.venv/bin/python -m photo2.r288.extras
.venv/bin/python -m photo2.r288.package
.venv/bin/python -m unittest photo2.r288.tests photo2.r287.tests photo2.r286.tests photo2.r285.tests photo2.r284b.tests photo2.r284.tests photo2.r283.tests photo2.r282.tests
.venv/bin/python -m photo2.r288.audit
/home/rharris/.local/bin/beads-chromium-review photo2.r288.browser_check
```

Use the exact standalone browser launcher, without wrappers or added arguments.
The existing permission is scoped to local review. The saved selection is reused
for reproduction; no network or physical model is used in inference.

## Sources and data

- `J_AND_M_EXPLAINED.md`: standalone mathematical/implementation explanation;
  initial word count/time/hash recorded in `results/explanation-checkpoint.json`.
- `fields.py`: unchanged M measurement-field adapter for controlled perturbations.
- `methods_EW_initial.py`: exact first E/W source, before adding diagnostic H.
- `methods_v1.py`: first corridor rule; retained narrow-bridge/shading false split.
- `methods.py`: final frozen E/W construction. `chromatic.py`: failed H diagnostic.
- `selector.py`: five-way interpreter, with independent-adequacy intent and preserved
  Q14 failure. `run.py` stores original J/M/B/R287 plus all new proposals.
- `selection.json`:15 regions/69 cues, exclusions/strata and unfilled red-flanking slot.
- `freeze.json`: exact source/selection hashes, parameters, pre-confirmation state.
- `diagnosis.json.gz`: six original-M anchors, all14 perturbations plus baseline,
  material floor, markers, interface pixels, saddle ratios and merged groups.
- `first-anchor-proposals.json.gz`, `chromatic-anchor-proposals.json.gz`,
  `development-EW-initial.json.gz`, `development-v1.json.gz`: preserved attempts.
- `development.json.gz`, `confirmation.json.gz`:21/69 cues with all six candidates,
  exact native run masks, contours, centroids, native Y,14 perturbation masks each,
  E inner ensembles, W marker/corridor/union evidence, H color parameters, R287 and
  R288 decisions and uncertainty. Native97 window origin=cue−48. Pixel axes x/y.
- `evaluation.json`: candidate metrics, diffuse proxy retention, centroid shifts,
  near/crossing/flanking/overlap accounting and per-case records.
- `mechanisms.json`: controlled deep valley, shallow shading, narrow bright neck,
  identical deep-texture ambiguity; mathematical fields, not physical renders.
- `black-preservation.json`: unchanged reflection-only source hash and earlier
  144-replay provenance; no claim of new R288 black measurements.
- `review/r288`: original97/145 crops, enlarged comparisons, exact fills, gains/losses,
  contours/centroids, intensity profiles, all-cue atlases and selected failure panels.
- `test-results.json`, `audit.json`, `browser-check.json`, `environment.json`,
  `delivery.json`: verification and scoped delivery receipts.

All six perturbation families are conditional: HSV/paper/palette/initial A stay
fixed. Seed offsets use a93px M window so the shifted computation fits the saved97px
field; computational-domain artifacts are flagged. E recomputes its five-member
ensemble inside each of14 outer perturbations. Profile lines sample smoothed Y;
dots sample original native Y. Review RGB is original decoded appearance, while
measurement RGB is ICC-converted sRGB. No generated or stock photograph is used.

Masks do not certify physical ownership; all Phase 1 observations remain important.
No calibrated real precision, recall, full-body size or complete centerline recovery
is claimed. No production adoption or later-phase reconstruction occurs here.
