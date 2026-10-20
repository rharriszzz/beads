# Reproduce R346 whole-necklace cast shadows

The final scene changes lighting only. The R345 camera, paper, glass materials, all 2,704 bead transforms, color pattern and helicity remain unchanged. Source baseline: `79a7a8ebd6b3484d0592bf63c0c7bbdca0cab412`, branch `photo-2-strategy-v3`.

From the repository root:

```bash
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r346.deliver
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r346.verify
```

The first command checks the sealed R344/R345 inputs, generates the final scene from the saved configuration, runs POV-Ray at 2540×3182, renders unshadowed-paper reference passes, and produces the comparisons, crops, shadow fields, paper profiles and numerical tables. The second independently checks the seals, unchanged scene components, all 2,704 pattern assignments, one global lighting setup, metrics, actual PNG paper samples, feature units and area-light convergence. POV-Ray 3.7, NumPy, SciPy, Pillow and Matplotlib are used; there is no network or GUI requirement. Full-resolution soft-shadow rendering is substantially slower than R345's small, sharp light.

A quicker preview is available:

```bash
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r346.deliver --size 1270 1591 --output /tmp/r346-preview
```

Distances in the analysis always use native 2540×3182 photograph pixels. A preview changes raster resolution, not camera projection or scene geometry. The independent verifier is intended for the delivered full-resolution artifacts.

The scene can be rendered directly:

```bash
povray +Iphoto2/r346/output/scene.pov +Lphoto2/r345/output +O/tmp/r346.png +W2540 +H3182 +FN -D -J +WT4 +A0.15 +AM2 +R2
```

Its `shape.inc` and `beads.inc` deliberately resolve to the original R345 files. The Python command is preferable because it also generates unshadowed reference passes, strips nondeterministic PNG date chunks, refreshes receipts and calculates diagnostics.

`--analyze-only` refreshes figures and measurements from existing renders. The unshadowed `clear.png` and `R345-clear.png` are generated caches excluded from git; run the normal pipeline once in a fresh checkout before using this option. The final rendered necklace, scene, tables, diagnostic images and provenance are committed.

## Measurement regeneration

The final frozen observations are in `photo2/r346/output/observations.json`, `background.json`, and `profiles.json.gz`. To regenerate them:

```bash
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r346.shadows measure
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r346.shadows background
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r346.shadows profiles
```

Observation selection uses only image geometry and grayscale edge energy. All96 arclength stations and both sides are retained. There is no pigment-based selection. The exact whole-necklace model mask is a diagnostic POV-Ray pass through the complete original rounded, hollow geometry, independent of lighting and color. Grayscale boundary sensitivity determines eligibility; paper sampling starts outside the conservative boundary band. The global background fit uses only a fixed spatial grid farther than 260pixels from the full traced necklace, with a held-out control-grid subset. This prevents extended shadows from being mislabeled as unobstructed paper.

The narrow local-reference experiment is preserved under `photo2/r346/development/` and rejected. Do not substitute its profile values for the final global-reference measurements. Profiles clipped by the image border retain null/censored extents rather than a fabricated toe position.

## Lighting search and calibration

The selected configuration is `photo2/r346/config.json`. A normal render does not refit it. For the lighting candidate searches:

```bash
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r346.sweep all
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r346.camera_controls
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r346.fit_light
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r346.sampling_check
```

The deterministic candidate scenes are cached under `/tmp/r346-shadow-trials`. Each candidate renders the **entire necklace** as one shared shadow caster. Paper-only passes use `no_image` to hide bodies from primary camera rays while all original glass objects still block shadow rays; these passes are fitting diagnostics, not the final colored reconstruction. Every trial uses one key source and one global room-fill contribution. The broad grid uses a circular source facing receivers as a preview approximation; the final fit uses one fixed tilted planar diffuser, entirely above the paper. The camera controls are rejected and never enter the final scene.

A single global room/direct RGB balance is fitted to paper pixels. No bead material or color is changed. A separate global unshadowed-paper brightness fit sets common intensity. Positions, area diameter, intensity and fill parameters are saved explicitly. Absolute lamp power/distance, room illumination and absorption are not uniquely identified by one photograph.

Three quarters of the fixed geographic stations fit lighting; every fourth station supplies the reported comparison set. Both sides and weak/no-shadow controls remain in the denominator. This is retrospective validation on the same photograph, not a new independent photographic experiment. The final analysis also compares exactly the same image-coordinate paper samples outside both the conservative photographic body band and the exact rendered silhouette; it does not rely only on contour-relative alignment.

[Report](R346_REPORT.md) explains the operational displacement/falloff definitions, source uncertainty, background sensitivity and remaining discrepancies. All R344/R345 files and unrelated stopped R340 work remain unchanged.

The primary relative-RGB convention follows R345. `python -m photo2.r346.color_profile_check` repeats the embedded-ICC-to-sRGB sensitivity control without fitting new lighting. It also runs during the default delivery pipeline.
