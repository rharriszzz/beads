# Photo 2 reconstruction

Start with the [overall plan and methods](../METHODS_AND_PLAN.md) for direct
answers about background removal, saved outer/inner/centerline curves and the
current limits of individual-bead identification.

**Latest completed step (R073/R074):** [black-region geometry and HSV diagnostics](BLACK_REGION_METHODS.md)
implement the maker's geometry-first recommendation. [Interactive outline inspection](review/r073/review.html)
and four plots show local predictions, position errors, contour sensitivity and
HSV profiles for 122/405. Geometry needs calibration; neither region is split.
Beads1/2/3 remain at 313/318/304 observations. Next calibrate projected centers
and outlines on clearer neighbors, then validate withheld predictions before
indexing. No new questions needed. Beads4 review is temporarily deferred.
The earlier [photo image-edge candidate](IMAGE_EDGES.md) remains rejected.

**Underlying reconstruction priority (R059): generated JPEGs first.** The
[blind beads1.jpg–beads7.jpg test](BLIND_GENERATED.md) produces reviewable bead
candidate maps without reading source patterns, but has not recovered a complete
pattern from any of the seven images. Visible-bead inventories need correction
before further indexing or photograph work. Reproduction commands and the
interactive observation gallery are described in that note.

This is an initial, reproducible forward model of `beads-photo-2.jpg`, with
diagnostics for later inverse fitting. It is **not a recovered necklace pattern**.
The broad arrangement is matched by a closed spline; bead layout, camera,
materials and illumination are provisional. See `../SESSION_HANDOFF.md`.

The selected next approach uses the maker's ±1/±6/±7 neighbor graph to assign
bead indices, then tests repeating colors while preserving unknown observations.
See [method review and synthetic test plan](METHODS.md) and the
[synthetic neighbor/index audit](NEIGHBORS.md). Supplied signed edges now support
checked relative indexing. The [known-index sequence audit](SEQUENCES.md) now
validates strong-period testing with missing colors, preserving alternative
completions and unsupported slots. Automatic image-neighbor identification and
photo pattern recovery remain unvalidated. The confirmed palette is red, yellow
and black.

The [image-space neighbor baseline](INFERENCE.md) now compares anonymous mask
centroids with mask-outline orientation on eight synthetic views. At T12 the
shape cue improves pair precision from 90.85% to 95.45%, with lower recall;
signed-label errors still make every tested full graph inconsistent. Oracle
masks, disconnected offsets and false crossing links remain explicit.
The [joint triangle/trace test](JOINT_INFERENCE.md) now rejects the known false
bridges but loses most correct rendered-view edges: T12 shape recall falls to
16.73%. It does not validate indexing. The maker's **R045 request supersedes
the planned centroid/body-center diagnostic** with visible-boundary detection
and local model-guided indexing. See the [new staged test program](DETECTION_PROGRAM.md)
for the recovered 303-point centerline, HSV picker, competing segmentation
methods, first beauty-image comparison and proposed smooth local corrections.

The [local calibrated contour/index test](LOCAL_PATCH.md) implements fixed,
translation and smooth fitting with both helicities. Two warped patches yield
34/38 and 38/38 correct region/color/index matches, but the anchor gate rejects
the unwarped inputs and all-black fitting fails. Camera/rope geometry is supplied;
these are conditional synthetic results, not recovered photo indices.
The [observed-region anchor test](REGION_ANCHORS.md) now removes the margin failure
on original R/Y/black identity/translation (34/37 and 32/34 correct indices for
all 17 jitter variants). It also admits wrong-hand alternatives in warped cases
and fails on the second R/Y/black patch. New gray outputs can be correct despite
a misidentified anchor. The [highlight-region repair](HIGHLIGHT_REGIONS.md) assigns
4,672 omitted pixels to their correct enclosing beads and improves four-anchor
acceptance from 100 to 115/272 without increasing wrong-index trials. It does
not improve bead detection or resolve helicity. The [shared-cavity comparison](SHARED_HIGHLIGHTS.md)
raises four-anchor acceptance to 140/272 with both distance and gradient paths,
but adds 137/151 wrong-owner pixels and worsens phase rejection. Keep conservative
abstention as the baseline. Next: test a second separated observed-region group
against surviving helicity/phase alternatives, holding the current fits fixed.

## Run with Python 3.12

From the beads repository:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r photo2/requirements.txt
.venv/bin/python -m unittest discover -s photo2 -p 'test_*.py' -v
.venv/bin/python photo2/reconstruct.py --render --width 800
```

POV-Ray must be on PATH. The script invokes it with `-D` for headless rendering
and four worker threads. No GUI packages or neighboring checkouts are required.
The tested environment is CPython 3.12.14, NumPy 2.5.3, SciPy 1.18.1,
Pillow 12.3.0 and POV-Ray 3.7.0.10.unofficial on PC/WSL. Other hosts are untested.
The R045 segmentation comparison also uses scikit-image 0.26.0.
Dependency ranges express minimum compatibility, not a frozen environment.

The command produces `photo2/output/comparison.png`, `render.png`,
`centerline-overlay.png`, `unwrap-sections.png`, `unwrap.png`,
`observations.npz`, `scene-data.inc`, `analysis.json`, and render command/log
files. Output is ignored by Git. Use `--output photo2/output/attempt-02` to
preserve one run while trying another; reusing an output directory replaces its
generated files. Reports bind image and source checksums and record settings.

For direct rendering after generation:

```sh
povray +Ibeads.pov Declare=Photo2=1 +Lphoto2/output +Ophoto2/output/render.png +W800 +H1002 +FN -D +A0.2 +WT4
```

Without `Declare=Photo2=1`, `beads.pov` retains its original eight animated
patterns. `bead-shape.inc` contains its shared rounded bead macro unchanged.
The legacy scene now accepts `Declare=Helicity=-1` for the opposite winding;
omitting it or using `Declare=Helicity=1` preserves the original hand.
The sign multiplies the bead-index contribution to the small-radius angle, keeping
the clock phase, large-circle traversal, colors and tangent hole axes fixed.
Only +1 and -1 are accepted. These are equation signs, not a measured photo hand.
Photo2 mode continues to use `settings.json` / Python's `--handedness` instead.

```sh
povray +Ibeads.pov Declare=Helicity=-1 +K0 +W800 +H600 +FN -D +WT2 +Ophoto2/output/legacy-opposite.png
.venv/bin/python photo2/neighbor_audit.py --output photo2/output/neighbor-audit-final
```

The audit renders both hands at the four R023 configurations and checks graph
indices at three visibility thresholds. It also renders the historical Git source
to verify that the default stays pixel-identical. Generated panels and reports
are ignored by Git; the script recreates them without requiring older outputs.
Previously generated practice reports have stale source hashes after this change:
rerun `practice_legacy.py` into a new output directory before using it as input
to a fresh `legacy_visibility.py --practice ...` run. Preserve older evidence.

## Coordinates and adjustable parameters

The saved centerline comes from the `fft-image-explorer` main branch's
`beads-photo-2_splines.json`. `centerline.json` retains the centerline coordinates,
source checksum, target-image checksum and dimensions. It includes the closing
point. Python fits a periodic cubic spline, smooths it by 4 square pixels per
control point and tabulates arc length on 20,001 points before uniform sampling.
The camera is an orthographic approximation. One model unit is one source pixel;
no physical necklace dimensions or camera calibration are available.

In image space x points right and y down; z points above the paper. For tangent
`T=(tx,ty)`, the normal is `N=(-ty,tx)`. Bead i uses
`theta = handedness * 2*pi*turns*i/count + phase` and position
`C(s) + rope_radius*sin(theta)*N`, with height
`rope_radius + bead_radius + rope_radius*cos(theta)`.
Only the POV export flips image y. Handedness +/- is defined by this equation,
not yet assigned to the photographed object. The starting point is marked in
white on the centerline overlay. Hole axes currently follow the rope tangent;
crochet tilt, local twist, bead-size variation and local stretch are not fitted.

`settings.json` exposes dimensions, helix phase/sign, beads per turn, turn pitch,
colors, light position/extent/intensity and surface finish. The initial 6.5
beads/turn comes from the old forward model, **not a measurement of this photo**.
The 22.26-pixel pitch uses a longitudinal texture peak as a starting hypothesis;
the diagnostic warns about harmonics and color motifs. Integer turns enforce
geometric closure; the count is derived from those assumptions, not bead counting.
The current 2,698 beads and 415 turns are therefore provisional.

The paper uses a magenta pigment with procedural bump texture; it does not use
the photograph as a texture. An upper-left area light and shadowless fill give
directional shadows and highlights. Near-black, red and yellow/orange glossy
opaque POV-Ray materials are initial settings. "Material" here specifically means
pigment, finish, normal and interior properties: color, diffuse response,
specular/phong highlights, roughness, reflection, filter/transmit and IOR where
applicable. The objective is to fit these rendering properties to the photo.
The current palette and material values have not yet been fitted systematically.

## Color observations and repeat hypotheses

The default render samples colors at predicted bead centers and fills remaining
unknown preview colors with black. Even a perfect-looking preview would not
establish the underlying repeat. Hidden and uncertain indices stay `-1` in
inverse analysis; preview fills are never used as evidence.

Conservative color boxes separate red/yellow/black from magenta paper, using five
interior samples to reduce isolated glints. They need validation against labeled
photo beads. Only centers with `cos(theta)>0.25` and at least three agreeing
samples vote. Boundary and partially occluded beads are intentionally uncertain.

Both signs are evaluated across every integer period 200–400. Five contiguous
arc blocks supply holdout folds. Training votes are grouped by **original bead
index modulo period**; missing indices are never removed. Tied votes earn
fractional validation credit, independent of arbitrary color numbering. Missing
or tied pattern slots stay unknown. Candidates are ranked by accuracy times
held-out coverage. The report includes the majority-color baseline, coverage,
per-slot support and confidence. These are conditional geometry diagnostics,
not calibrated probabilities or validation on independently labeled photo beads.
Searching 201 lengths and both signs also creates selection bias.

To inspect a candidate explicitly, keeping it separate from the default:

```sh
.venv/bin/python photo2/reconstruct.py --period 311 --output photo2/output/candidate-311 --render
.venv/bin/python photo2/reconstruct.py --handedness -1 --output photo2/output/opposite-hand --render
```

These are illustrative commands, not recommendations to accept period 311 or a
sign. The current best scores (~0.45 versus majority baselines ~0.41–0.43) do
not establish recovery. Resolve bead-center correspondence and local twist
before refining repeat inference. Unseen parts may remain unidentifiable from
one view even with better fitting.

## Fixed-observation geometry comparison (R014)

Run `.venv/bin/python photo2/fit_geometry.py` for the six labeled-patch comparison.
See [GEOMETRY.md](GEOMETRY.md) for annotations, equations, holdout protocol,
results and exact ambiguities. The 103 provisional labels are shared by both
hands; 27 centers are withheld after partial calibration of three validation
patches. Withheld RMSE is 6.27 versus 6.41 source pixels, insufficient to choose
handedness. Pitch/count/twist and hole-axis tilt remain underdetermined. This
experiment leaves the original render settings and unknown chain indices intact.

## Synthetic occlusion benchmark (R015)

Run `.venv/bin/python photo2/synthetic_benchmark.py` for the both-hand, known-geometry
POV-Ray experiment. [SYNTHETIC.md](SYNTHETIC.md) describes its exact ID/visibility
masks, center and outline scores, missing-label/noise trials and reproduction.
Center-only scores favor dense alternatives; perfect internal boundaries distinguish
tested shape/tilt/depth alternatives, while the pitch/count/twist equivalence stays
pixel-identical. This is discrete synthetic discrimination with fixed registration,
not extraction from shaded images or an accepted photo geometry. Generated reports,
images, include files and logs remain under ignored `output/`.

## Legacy repeat visibility (R023)

Run `.venv/bin/python photo2/practice_legacy.py`, then
`.venv/bin/python photo2/legacy_visibility.py`. [VISIBILITY.md](VISIBILITY.md)
records known bead/slot traces in the original scene for 40- and 13-color repeats.
Every 40-repeat slot has substantial coverage; the 13-repeat case includes a slot
exposed only through small gaps in one phase. Reports retain all missing indices,
per-view and quarter-ring support, exact-mask checks and annotated beauty views.
This is visibility measurement with known source indices, not automatic recovery.
