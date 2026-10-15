# R289 reproduction and evidence map

From repository root, Python3.12 in `.venv`, NumPy/SciPy/scikit-image/Pillow,
Matplotlib and installed POV-Ray3.7.0.10. Set one BLAS thread for these small arrays.
The original ICC photo and all historical data are read-only. Baseline2b9c289.
No dependency installation, production replacement or external service is required.
Renderer logs/POV text have delivery-only whitespace normalization; exact original
bytes survive as strings in `results/renderer-raw-text.json.gz`. No image or
measurement is changed by that formatting.

```bash
export OPENBLAS_NUM_THREADS=1
export MPLCONFIGDIR=/tmp/beads-r289-mpl
.venv/bin/python -m photo2.r289.baseline
.venv/bin/python -m photo2.r289.detect_photo
.venv/bin/python -m photo2.r289.calibrate development
.venv/bin/python -m photo2.r289.calibrate evaluation
.venv/bin/python -m photo2.r289.diagnostics
.venv/bin/python -m photo2.r289.synthetic run
.venv/bin/python -m photo2.r289.synthetic_evaluate
.venv/bin/python -m photo2.r289.sensitivity
.venv/bin/python -m photo2.r289.review
.venv/bin/python -m photo2.r289.dark_review
.venv/bin/python -m photo2.r289.background_review
.venv/bin/python -m photo2.r289.audit
.venv/bin/python -m photo2.r289.report
.venv/bin/python -m unittest photo2.r289.tests photo2.test_reconstruct_r276 photo2.bead_debugger.test_surface -v
/home/rharris/.local/bin/beads-chromium-review photo2.r289.browser_check
```

Prefer the independent replay command, which writes regenerated data to `/tmp`
without replacing the saved scientific results:

```bash
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/beads-r289-mpl .venv/bin/python -m photo2.r289.replay
```

That command recomputes all photographic inference and historical observations,
then compares five byte-exact data files and four decoded native PNG arrays for a
fresh scene00 render. PNG render-date comments differ. It does not claim twelve
fresh replayed scenes. `--verify-only` checks those existing replay files.
For a new full render replay, copy the frozen `synthetic-plan.json` into a separate
output directory, assign `photo2.r289.synthetic.OUT` to it and call `run()`;
its code verifies the plan's source hashes. Default `run` resumes completed scenes.
Do not refreeze parameters or overwrite the original plan to hide a disagreement.

## Important files

- `results/historical-replay.json`: exact810/807checks and original-split metrics.
- `results/photo-landmarks.json.gz`: all147268thresholded local maxima,1545retained
  features; per-rejection reasons. Initial all-patch source retained in checkpoints.
- `results/associations.json.gz`: reference memberships, all missing/multiple/shared
  cases, geographic split, eligible-reference flags. These are evaluation data,
  never detector inputs. Peak-in-mask matching conditions the reported accuracy.
- `results/calibration-frozen.json`: hashes, train-only models, covariance and
  six-region/100px split. Core detector/evaluator unchanged after this freeze.
- `results/photo-evaluation.json`, `photo-residuals.json.gz`: full proxy results,
  per-region scores, every error, original paired baseline, all denominators.
- `results/diagnostics.json`: pooled patch correction, uncertainty coverage,
  old/new patch agreement, J/W disagreement, full-detection failure counts.
- `results/phase2-observations.json.gz`: experimental measurement contract;
  measured patch and optional interior proxy separate; no physical identities.
- `results/synthetic-plan.json`: seed2891703, twelve exact scene parameters and
  class arrays, source hashes. `synthetic/*`: POV sources/logs, on/off/specular/ID
  rasters, independent inference and known-owner evaluation. Truth is opened only
  after saved inference. Geometry is contact-certified with the existing checker.
- `results/synthetic-summary.json`, `synthetic-residuals.json.gz`: by-color metrics
  against visible and physical truth, multiplicity/missing counts, empirical and
  known-geometry predictions on paired cases. No photographic physical truth implied.
- `results/synthetic-oracle-landmarks.json.gz`: whole-known-body brightest pixels,
  connected bright patches and true centers for on/off, including dim features
  below the detector threshold; evaluation truth only, with tied-peak counts.
- `results/sensitivity.json`: two fixed scenes,+10°camera,+15°light,next-body identity.
- `results/audit.json`:10700+historical blob hashes checked, exact crops, **all**
  synthetic accepted proposals including background/tiny exposures, specular lobes.
- `results/failures.json`: interrupted initial implementation, absent border-hue
  NaN metadata, PNG timestamp hash failure. No scientific failure was retuned away.
- `results/replay.json`, `tests.log`, `browser-check.json`: separate verification.
- `review/r289/index.html`: compact report, expandable raw/marked photographic
  evidence, geographic locator, darkness profiles and paired synthetic successes/
  failures. Native source crops are linked and pixel-audited. No display contours.

## Definition and limitations

The pooled correction is (+4.9346366875,−0.3037864302)px from independent unweighted
patch to the historical R275 interior proxy. It is not a visible-surface or physical
center offset. Photo diameter30px is nominal. Synthetic diameter2R×scale32.12px
is known nominal projected outer diameter, not an occluded silhouette width.

Direct specular prediction uses the known camera/light half-vector, analytic source
normals, all-neighbor SDF shadows and `max(n·h,0)^(1/roughness)` on lit visible pixels.
Native brightest point and weighted85%-peak moments are compared to a separate POV
specular-only image. Multiple bright lobes/ties are recorded; the moment can span
separate lobes. Finite raster/grazing-ray differences remain explicit. Measurement
failures use total appearance; pose/light/identity stresses use fixed altered model
inputs and never retune observations. A full inverse solution is outside scope.

48missing and2multiple eligible heldout bodies plus11background false features
prevent claims of complete distinct-bead recovery. The context-color classifier
and background gate are not established as general. Scene05/08 have unavailable
border hue, represented as null without hiding the inactive paper gate. No new
manual labels or full necklace reconstruction were requested or created.
