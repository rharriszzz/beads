# Reproduce R345

From the repository root, using the existing Python environment (NumPy, SciPy and Pillow) and POV-Ray3.7:

```bash
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r345/render.py
```

This loads the saved configuration, frozen R344 pattern and coordinates, and image-derived spline; emits all2,704 bead transforms and the reusable original rounded CSG shape; independently diagnoses geometric contact candidates; runs POV-Ray; then creates the side-by-side image, transparent geometry layer, photographic alignment overlay, four enlarged comparison crops, repeat-index overview and signed-neighbor detail. Default rendering is2540×3182, with four POV-Ray threads and antialias jitter disabled. No network, image-generation service or GUI is required.

Run a fresh full render and exact19-artifact replay comparison:

```bash
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r345/replay.py
```

The renderer’s PNG date chunks are removed without recompressing pixels or changing gamma/sRGB tags. All scene, data and image artifacts compare byte-for-byte; runtime logs/command receipts are excluded.

Run the independent checks separately:

```bash
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r345.verify
```

This recomputes emitted count/color/matrix checks and separation certificates, checks both helicities, renders original-macro bore/surface trace tests and camera markers, renders all eight legacy examples with both radius settings, and compares every R344 file with baseline `d6c4cdb7aab209e53ca32488c43e45f1e12901ad`. The verification scenes are temporary. Its receipt and legacy montage are saved alongside the main render.

Primary paths:

| File | Purpose |
|---|---|
| `photo2/r345/config.json` | Saved count, period inputs, centerline, camera, shared dimensions, handedness, periodic placement fields, glass/paper/light parameters and source baseline. |
| `photo2/r345/render.py` | Geometry, generation, rendering and comparisons. |
| `photo2/r345/verify.py` | Independent count, surface, contact, projection, legacy and preservation checks. |
| `photo2/r345/output/scene.pov` | Entry point; declares R345 and includes the repository's `beads.pov`. |
| `photo2/r345/output/scene.inc` | Generated camera, paper, light, shared glass definitions and bead include. |
| `photo2/r345/output/shape.inc` | Verbatim original bead macro extracted from `beads.pov`. |
| `photo2/r345/output/beads.inc` | Exactly2,704 physical bead object statements. |
| `photo2/r345/output/beads.json` | Transforms, indices, provisional/strict colors and tentative flags. |
| `photo2/r345/output/provenance.json` | Source hashes, saved configuration and complete R344 uncertainty metadata. |
| `photo2/r345/output/contacts.json` | All candidate-pair separation certificates and constructive gap bounds. |

Direct POV-Ray command after generation:

```bash
povray +Iphoto2/r345/output/scene.pov +L. +Lphoto2/r345/output +Ophoto2/r345/output/render.png +W2540 +H3182 +FN -D +A0.18 +AM2 +R2 -J +WT4
```

All include paths must be present. The complete Python pipeline is preferable because it also refreshes diagnostics and receipts. `render.py --generate-only` skips ray tracing. `--width 1270 --height 1591` makes a faster preview at the same aspect ratio. `--output /tmp/r345-replay` runs into a fresh destination without changing the source or scientific ledger. The input coefficient configuration is fixed during a normal replay. Renderer timings/log paths are runtime metadata, not scientific inputs.

`--config /path/to/config.json` selects another configuration. To render another recovered necklace in the same6.5-bead/A-coordinate family, change the pattern and indexed-graph paths, centerline data, total count, integer minor turns and saved frame/placement/camera parameters. Pattern length is read from its JSON; complete-repeat and winding consistency are asserted. The independent verifier is intentionally a fixed R345 regression contract, not an automatic physical validator of other necklaces. The current diagnostic crops and native-image metadata are specific to photo2.

`--calibrate` explicitly refits and overwrites the selected configuration's broad periodic station/phase coefficients using only frozen indexed XY supports. It performs degree0/3/5 fits with a robust loss and penalties; no colors are consumed or changed. This is optional geometry fitting and is **not** needed to reproduce the delivered scene. The saved primary uses `helicity=-1`; changing it to+1 reverses winding and retains closure, but is a diagnostic alternative rather than an equally good photographic association. The field G is an additive phase field; sign reversal reverses the carrier rather than mirroring every point exactly.

Legacy example controls:

```bash
povray +Ibeads.pov +O/tmp/beads-example5.png +W640 +H480 +FN -D Declare=bead_pattern=5 Declare=LegacyRadius=1 Declare=helicity=1
```

Omit `LegacyRadius=1` to use the corrected `sin(pi/6.5)` radius. The default example selection still follows `clock`. Legacy example5 now has a material for its formerly undefined index4. For literal historical Python placement parity, the extracted parameter block retains the legacy radius unless an enclosing scene specifies otherwise. No historical scientific input seals are rewritten: seals recording the old `beads.pov` remain historical and naturally differ from this explicitly authorized scene edit.

The count2704, thirteen repeats,6.5 beads per turn,416 turns, camera elevation, bead thickness and glass optics retain the conditional/approximate status explained in [R345_REPORT.md](R345_REPORT.md). R344 pattern, graph and scientific results are not regenerated or modified.
