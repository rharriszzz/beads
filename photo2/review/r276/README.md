# R276 evidence and reproduction

[Main report](../../RECONSTRUCTION_R276.md)

- `observations.json`: unchanged R275 measurements plus documented photo-only gates and fixed sector splits; all810 records,807 exact masks. The295 uncertain source candidates remain separate in R275.
- `neutral-only-observations-control.json`: failed initial yellow-neutrality selection, preserved before fitting.
- `protocol.json`: bounds, priors, four methods and assumptions.
- `MODEL.json`: complete base spline, count/hand/camera, parameters, shared light and fit trace.
- `MODEL-audit.json.gz`: all810 individual predictions, alternatives, uncertainties, exact native ownership, shape/brightness residuals and maximum errors.
- `MODEL-surfaces.npz`: exact first-hit samples on the full2px grid, owner, world normals, specular and diffuse response. Hidden beads remain in the scene, not fabricated surfaces.
- `MODEL-prediction.png`, `MODEL-highlights.png`, `MODEL-worst-*.png`: full photo prediction, cyan observed/magenta predicted peaks, and raw/marked native worst crops. White dots are predicted surface samples; cyan contours are conservative interiors.
- `yellow-calibration-*.png`: distributed raw photographic evidence; native brightest pixels,85%-bright-patch centroids and interior centroids kept distinct.
- `*-collisions.json`, `packing-*-screen.json`, `metric-calibration-screen.json`: sampled exact-surface interpenetration tests. A zero sampled violation does not prove global noninterpenetration.
- `maker-B-positive-audit.json`: the preserved maker-confirmed seven yellow B pixels, audited separately without inserting legacy index2 into fitting.
- `*-unfinished-rays.json`: native positive-pixel and full-grid grazing rays left unknown; no fabricated completed ownership.
- `*-full-profile-collisions.json`: denser 16,384-point contact checks including flat faces, plus all bounding-sphere pair families.
- `*-fixed-correspondence.json`: performance with frozen owner hypotheses from the same count/hand. Contact uses its N1950/h−1 screen, never N2696 indices. The invalid first cross-count diagnostic is archived and superseded; a regression test guards the correction. Improvements from rematching remain visible.
- `*-implied-light.json`: mirror-normal diagnostic at observed peaks, conditional on geometry and source ownership.
- `*-native-convergence.json.gz`:1px versus2px highlights and visible surfaces on a deterministic distributed subset.
- `*-empirical.json`: normalized tangent/radial control, singular-frame exclusions and paired physical scores.
- `*-diffuse-control.json`, `*-shape-brightness.json`: shared yellow diffuse-mixture control, width/orientation discrepancies, material-normalized intensity errors.
- `*-light-sensitivity.json`: training objective under direction/roughness perturbations. Local sensitivity is not a confidence interval.
- `preserved-hashes.json`, `validation.json`, `provenance.json`: preservation, test results, native replay, source and artifact hashes.

The fit loss uses positive-support squared distance after raster-quantization allowance, divided by16; yellow brightness displacement squared, divided by36; and independent deformation priors. Support costs clip at144px², light costs at900px² during fitting. Mixed controls add half-weight black training reflection cost. Final ledgers retain untrimmed distances and explicit missing cases. Assignment is one-to-one within each split and based on positive support only, with unmatched alternatives; it is not photographic identity. Cross-split owner/color conflicts are reported.

Engineering uncertainty:2px for selected specular candidates,4px otherwise; neither is a calibrated posterior error. Bright-patch shapes use the same connected85%-of-peak convention as R275. Sharp lobes are sampling-sensitive; convergence controls quantify that limitation. Original unweighted patch centroids remain in bright_patch. Fitting uses a separately derived centroid weighted by ICC luminance minus the interior 30th-percentile floor, on the same preserved 85% patch. Material gains are one shared gain per color, trained without held-out brightness; they do not recover physical exposure/albedo.

Reproduce the complete dependency-ordered experiment with `OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.reproduce_r276`. The original neutral-only failed selection remains an archived control. Individual stages and cheap saved-model replay are available below. Python3.12, existing environment, no downloads:

```bash
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.reconstruct_r276 --stage fit
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.reconstruct_r276 --stage alternatives
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.diagnose_r276 correction
OPENBLAS_NUM_THREADS=1 .venv/bin/python -c 'from photo2.diagnose_r276 import mixed_correction,packing_fits; mixed_correction(); packing_fits()'
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.reconstruct_r276 --stage audit --names initial light_only interior_geometry joint joint_refined uniform_before uniform_joint uniform_refined mixed_light mixed_joint
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.diagnose_r276 diagnostics --name mixed_joint
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.diagnose_r276 contact
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.diagnose_r276 checks --name contact_joint
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.validate_r276
OPENBLAS_NUM_THREADS=1 .venv/bin/python -c 'from photo2.diagnose_r276 import fixed_and_normals,convergence,material_control; fixed_and_normals("mixed_joint"); convergence("mixed_joint"); material_control("light_only")'
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m unittest photo2.test_reconstruct_r276 photo2.bead_debugger.test_surface
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.report_r276
povray +Iphoto2/review/r276/light_only.pov +Ophoto2/review/r276/light_only-pov.png +W1016 +H1273 +FN -D +A0.2 +WT2
```

Saved models can be replayed directly with `--stage audit --names MODEL`; this does not rerun optimization. POV-Ray uses the literal source bead macro. Its display material differs from the quantitative Blinn-lobe diagnostic and is not a radiometric validation. Browser rendering was not needed for these standalone photographic/POV artifacts.

| Saved model | N | hand | focal px | held-out yellow RMS | held-out black RMS |
|---|---:|---:|---:|---:|---:|
| [alternative_N2674_h+1_f0](alternative_N2674_h+1_f0.json) | 2674 | +1 | 0 | 9.823 | 9.507 |
| [alternative_N2674_h-1_f0](alternative_N2674_h-1_f0.json) | 2674 | -1 | 0 | 13.320 | 9.821 |
| [alternative_N2681_h+1_f0](alternative_N2681_h+1_f0.json) | 2681 | +1 | 0 | 11.554 | 11.986 |
| [alternative_N2681_h-1_f0](alternative_N2681_h-1_f0.json) | 2681 | -1 | 0 | 13.071 | 11.164 |
| [alternative_N2696_h+1_f0](alternative_N2696_h+1_f0.json) | 2696 | +1 | 0 | 10.929 | 11.028 |
| [alternative_N2696_h+1_f9598](alternative_N2696_h+1_f9598.json) | 2696 | +1 | 9598.0 | 10.948 | 11.210 |
| [alternative_N2696_h-1_f0](alternative_N2696_h-1_f0.json) | 2696 | -1 | 0 | 11.517 | 11.411 |
| [alternative_N2700_h+1_f0](alternative_N2700_h+1_f0.json) | 2700 | +1 | 0 | 10.803 | 8.038 |
| [alternative_N2700_h-1_f0](alternative_N2700_h-1_f0.json) | 2700 | -1 | 0 | 11.664 | 10.679 |
| [contact_joint](contact_joint.json) | 1950 | -1 | 0 | 11.252 | 11.493 |
| [contact_light](contact_light.json) | 1950 | -1 | 0 | 12.176 | 11.244 |
| [initial](initial.json) | 2696 | +1 | 0 | 13.435 | 10.445 |
| [interior_geometry](interior_geometry.json) | 2696 | +1 | 0 | 11.332 | 10.099 |
| [joint](joint.json) | 2696 | +1 | 0 | 10.771 | 10.918 |
| [joint_refined](joint_refined.json) | 2696 | +1 | 0 | 10.548 | 11.287 |
| [light_only](light_only.json) | 2696 | +1 | 0 | 11.694 | 9.505 |
| [metric_before](metric_before.json) | 2696 | +1 | 0 | 10.423 | 12.124 |
| [metric_refined](metric_refined.json) | 2696 | +1 | 0 | 9.854 | 11.244 |
| [mixed_joint](mixed_joint.json) | 2696 | +1 | 0 | 9.862 | 11.102 |
| [mixed_light](mixed_light.json) | 2696 | +1 | 0 | 9.918 | 11.621 |
| [packing_N1950_h+1](packing_N1950_h+1.json) | 1950 | +1 | 0 | 15.200 | 16.635 |
| [packing_N1950_h-1](packing_N1950_h-1.json) | 1950 | -1 | 0 | 11.947 | 11.273 |
| [packing_N2696_h+1](packing_N2696_h+1.json) | 2696 | +1 | 0 | 9.910 | 10.310 |
| [uniform_before](uniform_before.json) | 2696 | +1 | 0 | 10.341 | 12.285 |
| [uniform_joint](uniform_joint.json) | 2696 | +1 | 0 | 10.908 | 12.018 |
| [uniform_refined](uniform_refined.json) | 2696 | +1 | 0 | 10.619 | 12.488 |
