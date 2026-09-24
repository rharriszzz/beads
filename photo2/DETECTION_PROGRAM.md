# Visible beads first, indexed beads second — R045

R057 follow-up: [SHARED_HIGHLIGHTS.md](SHARED_HIGHLIGHTS.md) completes the fixed
distance/gradient shared-cavity test. Both improve gray-anchor acceptance but
introduce wrong ownership and worsen excluded-phase rejection. Keep R055 repair
as the baseline. Next: a second separated validation group within each crop,
with fixed fits, to test surviving wrong-helicity/phase alternatives.

R055 follow-up: [HIGHLIGHT_REGIONS.md](HIGHLIGHT_REGIONS.md) tests conservative
bright-cavity filling with existing labels fixed. Added pixels have correct
ownership in this audit; anchor jitter tolerance improves, but detection counts,
seed slips and wrong-hand alternatives remain. R057 completes the shared-cavity
comparison above without adopting its less conservative assignments.

R052 follow-up: [REGION_ANCHORS.md](REGION_ANCHORS.md) measures three/four-region
anchors under fixed jitter on two patches. The original R/Y/black patch improves;
wrong-hand alternatives, highlight-related region gaps and second-patch failures
remain. R055 completes the bounded highlight-tolerant region comparison above.

R047 follow-up: [LOCAL_PATCH.md](LOCAL_PATCH.md) implements a first calibrated
local contour/index comparison with both hands and smooth corrections. It exposes
a brittle click-margin gate and remaining black failure; image-derived geometry,
automatic seeds and whole-ring growth remain unimplemented. The R045 program and
results below remain the original baseline, not a claim all stages are complete.

The maker identifies neighbors from visible edges without locating bead centers,
and can separate adjacent beads even when every bead has the same color. The
computer has not yet matched that ability. The objective is now two separately
measured capabilities: **find the visible bead regions and their colors**, then
**assign consistent bead indices to those observations**. Colors can supply
anchors; they are not a prerequisite for separating instances.

This supersedes the next centroid/body-center diagnostic in JOINT_INFERENCE.md.
That diagnostic remains useful as an ablation, not the main route. Earlier
oracle-mask graph results do not establish segmentation from an ordinary image.
The model-guided procedure below is a proposed experiment, not a working solver.

## Recovered prior work

- `photo2/centerline.json` already contains **303 points** for photo 2. Its
  source is `fft-image-explorer/beads-photo-2_splines.json`, whose SHA-256 is
  `1e5f0d985be2dfb44b9fa3eac6ad54a0f1345c2ae9a6ed0a8bc3ca510b07dac7`.
  The source has 303 centerline, 907 outer-boundary and 847 inner-boundary
  samples (152/142 outer/inner controls). The copied centerline differs only
  by rounding, at most 0.0000500000001 pixel. The saved photo hash matches
  `beads-photo-2.jpg`. This is available geometry, not an independently validated
  bead map or exact local diameter. The original extraction mode is
  `image_only_hsv`; `find_splines.py` and `notes.md` explain its outline tracing.
- `hsv_tools/hsv_picker.py` implements the remembered two-click line sampler.
  It buckets HSV samples using adjustable H/S/V tolerances, handles hue wrap,
  and ORs the tolerance boxes around sampled colors. It does **not** compute a
  convex hull. Current source SHA-256:
  `26f1062c3024f3ecb7fc8fd33fb42136cece66d83aeee2f65de1a74c41b64537`;
  sibling checkout commit `3e70fe304bd586b160caf12e45b657f33d8141ea`.
  A hull in raw HSV would need special treatment of circular hue, especially red.
- `bead_map/bead_map.py` already explores connected color masks, region areas,
  blob detection and distance information. Its selected-pixel convention is
  black, which must be made explicit when importing its JPEG masks. Existing
  masks are manually assisted evidence, not automatic truth labels.
- The all-branch Markdown inventory remains in BRANCH_REVIEW.md. This round
  used that inventory plus targeted source/data reads, without redoing unrelated
  branch history or editing sibling checkouts. `fft-image-explorer` was at
  `2caf0707c2b63a0d7540e2cac447d2f1b883d8c1`, clean on main.

## Outputs and independent success measures

**Detection:** give each observation an anonymous ID, visible-region mask,
bounding box, color probabilities or explicit unknown, and boundary confidence.
Record a fitted body position only when a shape fit supports it. A region's
centroid is a descriptive statistic; it is not assumed to be the physical center.
Keep touching-instance merges, splits, missed slivers and background/shadow
false positives. Do not label everything left after red/yellow removal as black:
that remainder can include shadows, highlights and uncertain background.
R049–R051 clarify that photo bead holes and the white crochet thread are never
visible; hole axes run lengthwise. Beads share size/shape with small gloss differences.

**Indexing:** attach signed ±1/±6/±7 edges to those observations, retain competing
sign/family assignments, and propagate indices from a declared seed. Preserve
disconnected offsets and missing positions. The maker permits any consistent
origin/direction; exact synthetic source indices are used afterward to evaluate
the chosen convention. Photo indices are only determined up to those allowed
conventions unless an external origin is supplied. Never apply modulo 2,698 or
a divisor test to that provisional photo count. Unknown color and unknown index
are independent. A consistent cycle alone is not evidence that an edge is right.

Primary measurements:

| Capability | Measurements | Prevents a misleading success |
| --- | --- | --- |
| Bracelet/background | Mask IoU; shadow and hole false positives; outline distance | A good outer outline hiding failed bead separation |
| Individual visible regions | One-to-one IoU >0.5 precision/recall; boundary distance; merges/splits | Counting fragments or a color blob as beads |
| Color | Confusion/unknowns, by true color; correct color **and** correct detection | High color accuracy on only easy detections |
| Position | Visible-boundary error; separately, fitted body-center error | Comparing occluded centroids to physical centers |
| Neighbors/indices | Correct signed edges, coverage, component offsets, seed-relative index errors | A sparse or internally consistent but wrong graph |
| Combined task | Beads with correct region, color and relative index / all eligible visible beads | Good individual scores on incompatible subsets |

Report visible-size strata (1–11, 12–99, >=100 pixels or scale-normalized
equivalents), same-color contacts, black bodies, front/side edge, bend/straight,
both hands, shadows and crossing regions separately. The first baseline below
reports T12/T100 instance metrics, colors, splits/merges and missing indices;
the other measurements are required in their corresponding later stages.
Use an evaluator-only source match. Detector input must exclude ID images,
source indices, exact layouts and true visibility lists. Record all parameters,
manual clicks, hashes, random seeds and renderer commands.

## Test ladder

| Stage | Increasing difficulty | Fixed comparison / stopping point |
| --- | --- | --- |
| 0 | Two separate beads, then touching same-color beads; empty background; dark shadow distractor | Evaluator and detector unit controls; no claims from circles alone |
| 1 | Existing full legacy RGB renders: two patterns, two phases, both hands | Four image-input baselines on the eight saved beauty views, with exact masks only for scoring |
| 2 | Matched R/Y/black, all gray and all black, retaining original glossy shading | Re-render identical geometry with pigment changes only; expose color dependence and black merges |
| 3 | Blur/noise, smaller beads in pixels, light changes, magenta paper and shadows, stronger partial occlusion | Freeze parameters on development views; score separate held-out renders; change one nuisance at a time before combinations |
| 4 | Model-guided local patch: estimated rope width/centerline, one seed; then deliberate spline/phase errors | Compare boundary fit with and without a model, and fixed model versus fitted smooth corrections; test capture range and wrong-phase rejection |
| 5 | Grow around a whole ring, both directions; bends, seam, missing observations and true rendered crossings | Correct relative indices and boundary alignment on held-out views; no truth-based re-seeding; report drift and stopping points |
| 6 | Small photo crops before the whole photograph | Blind predictions then maker-reviewed boundaries/indices; compare automatic and recorded-click assistance; no synthetic-truth access |

R045 implements stage 1, palette controls in stage 2, and a single mild blur/noise
pair from stage 3. It does not claim completion of the full ladder. Test panels
use the same predetermined crop and whole-image context for every method; do
not select only successful beads. The existing 13-repeat weak-slot views and
R041 false-shortcut region remain useful challenge cases. Later holdouts must
be chosen **before** tuning; R045's scored scenes are now development evidence.

## Competing approaches

1. **Color selection and connected components.** Start with red/yellow samples
   and a separate background sample, reproduce the line-picker behavior, retain
   circular hue and unknowns. Vary the amount of manual input explicitly: zero,
   one line per class, multiple lines. Evaluate transfer of the same samples to
   other beads/patches. R045 uses fixed palette hue/value rules, not claimed
   human samples. Components are a baseline; a same-color run can merge.
2. **Distance watershed.** Split connected color regions using automatically
   detected interior markers. This is a standard touching-object baseline;
   its markers need not equal physical centers. R045 uses scikit-image's
   [documented distance/marker construction](https://scikit-image.org/docs/stable/auto_examples/segmentation/plot_watershed.html).
3. **Boundary watershed without hue seeds.** Find interior markers between
   grayscale edges and grow regions to those edges. This tests the maker's
   same-color observation. Highlights may create extra edges; weak boundaries
   may merge beads. R045 uses grayscale gradients, not learned boundaries.
   The [marker/gradient example](https://scikit-image.org/docs/stable/auto_examples/segmentation/plot_marked_watershed.html)
   documents the underlying approach; the bead-specific settings are hypotheses.
4. **Color/boundary hybrid.** Use colored interiors to seed boundary-based
   growth. Let confident colored detections anchor scale/orientation, then use
   geometry and actual boundaries to search the rest. R045 tests only the first
   watershed part; black recovery from a geometric model is still future work.
5. **Local rendered-shape fitting and growth.** Predict a small neighborhood
   using the legacy bead shape and compare visible contours with observed
   boundaries, allowing occlusion. Add a bead only when image evidence supports
   a unique match. Compare edge distance, region overlap and a robust shading
   residual; do not rely solely on color or center distance. Use POV-Ray for
   appearance/visibility, Python for geometry, fitting and graph constraints.

Foreground graph cuts with foreground/background scribbles are another sensible
comparison for difficult shadows, but [GrabCut's documented output](https://docs.opencv.org/4.12.0/d8/d83/tutorial_py_grabcut.html)
is a foreground mask, not a solution to splitting beads. Keep it at that stage.
Training a boundary/instance model on randomized POV renders is a later candidate
if classical boundary/model methods plateau. It would need separate geometry,
lighting and real-image holdouts; synthetic training accuracy would not suffice.

## Concrete local prediction and correction experiment

1. Use the saved 303-point centerline for photo 2, or an image-estimated centerline
   in synthetic tests. Sample it uniformly by arc length. Estimate apparent
   local width from both outlines, retaining a shadow uncertainty band. Keep an
   exact synthetic centerline only as a clearly labeled diagnostic control.
2. Choose a confidently separated bead as seed index 0. A manually selected
   seed is an allowed, recorded assistance condition; compare with an automatic
   seed. Fit a patch's scale, row phase, pose and both helicities against visible
   boundaries using the fixed legacy body shape. Keep alternate fits if tied.
3. Render/project where ±1, ±6 and ±7 neighbors would be visible. Search a bounded
   region for their actual edges, jointly penalizing duplicate use of a region,
   implausible overlap and inconsistent 1+6=7 loops. Include unknown and absent
   observations as outcomes. A model prediction alone is not a detected bead.
4. Store accepted residuals in local tangent/normal coordinates. Fit smooth
   correction functions along centerline arc length, with a separate small
   phase correction if supported. Penalize curvature and overly large changes;
   prevent arbitrary per-bead displacement from hiding an index slip. In an
   initial 2-D experiment these are image-alignment corrections, not recovered
   3-D deformation. Bounds/regularization must be fixed before scoring.
5. Predict the next patch with the updated correction field, retain overlapping
   anchor beads, and grow in both directions. Revisit earlier overlaps and
   compare closure. Stop or branch when several matches remain plausible;
   retain their scores instead of forcing a choice. Fitted data and withheld
   residual checks must remain separate so drift is measurable.

For this stage's comparison, use identical observations for: no model, fixed
model, model plus smooth correction, and an explicitly oracle-assisted ceiling.
Perturb seed position/phase, width, spline position and smooth local warp one at
a time. Test wrong helicity, a one-bead slip and false shadow seeds. Measure the
range of errors from which it recovers, not just a perfectly initialized case.
The primary stopping point is a correctly indexed **local visible patch** with
measured contour residuals; whole-ring growth follows after that works.

## First executable baseline

```sh
.venv/bin/python -m pip install -r photo2/requirements.txt
.venv/bin/python photo2/detection_audit.py --fixtures photo2/output/detection-fixtures-r045-final --output photo2/output/detection-audit-new
.venv/bin/python -m unittest discover -s photo2 -p 'test_*.py' -v
```

The default verified input is `output/neighbor-audit-final/`; recreate it with
the command in NEIGHBORS.md if absent. First invocation renders eight paired
2400×1800 beauty images in the selected fixture directory: two RGB identity
checks and six palette controls. Source changes require a fresh `--fixtures`
directory; subsequent runs verify and reuse its manifest. Baseline sources are
validated against current/historical Git by the existing input verifier.

`detect_beads.py` accepts only RGB pixels, method and palette. `detection_metrics.py`
alone matches source IDs. `detection_audit.py` saves each predicted mask, region
records with null `bead_index`, evaluator matches/missed indices, per-color
counts, T12/T100 scores, whole-image and fixed-detail panels, commands and hashes.
Output masks use anonymous labels, not source IDs. A high overlap match is
evaluator evidence, not an inferred source index.

All initial settings are fixed in `PARAMETERS`: at 2400 pixels wide, 12-pixel
minimum region size, 12-pixel seed separation, 2.5-pixel seed depth, closing
radius 2, grayscale smoothing sigma 0.8 and edge threshold 0.025. Saturation
threshold 0.20, dark foreground value 0.75, black value 0.35, hue distance 0.10
turn and 60% region color agreement. The legacy white-floor foreground rule
can include shadows and omit bright highlights. It is **not** calibrated to
the photo's magenta paper. Distance/color baselines leave unselected highlights
unassigned; hybrid growth may cover them. No setting is tuned after these runs.
The mild corruption is Gaussian blur sigma 1 pixel plus RGB noise sigma 2/255,
PCG64 seed 45, rounded/clipped to bytes.

At each visibility threshold, precision excludes only predictions correctly
matched to a real subthreshold bead, counted separately as `ignored`. All
unmatched predictions count as false positives. IoU must be strictly >0.5,
which makes matches one-to-one without a greedy tie choice. Split/merge counts
require a contributing overlap of at least 12 pixels and 10% of that truth
bead. These diagnostics may overlap; they are not an exhaustive error partition.
ID truth is un-antialiased while beauty is antialiased, so pixel boundaries have
a raster mismatch. Gray/all-black controls are actual rerenders, not desaturated
RGB pictures, and share geometry rather than being independent samples.

## R045 results

The four baselines were run on all 16 views (64 trials), without changing their
settings after scoring. This table reports **precision / recall** of complete
visible-region matches at IoU >0.5, using truth beads with >=100 visible pixels.
These thresholds define a reproducible synthetic comparison, not a human
readability threshold. T12 scores and every missed index are also saved.

| Views | Color components | Color distance | Gray boundary | Hybrid boundary |
| --- | --- | --- | --- | --- |
| Eight original RGB | 76.45% / 22.57% | 40.01% / 54.59% | 67.22% / 80.40% | 74.88% / 78.19% |
| Two R/Y/black | 64.51% / 22.72% | 31.55% / 46.33% | 46.07% / 61.11% | 47.43% / 60.42% |
| Two all-gray | 0% / 0% | 0.95% / 0.89% | 70.92% / 87.60% | 62.41% / 34.42% |
| Two all-black | 0% / 0% | 1.59% / 1.49% | 3.00% / 2.88% | 3.36% / 2.98% |
| Two R/Y/black blur/noise | 69.03% / 23.21% | 33.60% / 42.36% | 57.38% / 58.23% | 62.06% / 53.08% |

The strongest direct evidence for a boundary approach is the all-gray result:
883/1,008 visible beads are matched, with 362 unmatched predictions and 125
missed beads. Color components merge the same scene into one region per image.
This is useful progress toward same-color separation, not exact bead recovery.
All-black fails badly. Exact legacy `Black` has zero pigment reflectance and
mainly specular highlights; many boundaries visible in gray lose contrast.
This is an extreme appearance control, not a fitted model of the photo's black
beads and not evidence that the maker cannot distinguish them. The failure
motivates model/outline constraints and dark-material/lighting tests.

Mixed R/Y/black shows the remaining black-specific deficit:

| Method | Red matched /199 | Yellow matched /379 | Black matched /430 |
| --- | ---: | ---: | ---: |
| Color components | 101 | 103 | 25 |
| Color distance | 145 | 190 | 132 |
| Gray boundary | 173 | 321 | 122 |
| Hybrid boundary | 179 | 287 | 143 |

For hybrid, 605/609 matched R/Y/black regions also have correct colors; four
remain unknown. This high conditional color accuracy does not erase the 399
missed beads or 675 unmatched predictions. Color classification and separation
of bead instances are different bottlenecks. Blur/noise sometimes reduces false
regions, but also removes correct detections; the two paired variants do not
establish robust performance. No algorithm is selected solely by recall.

Use the per-trial `foreground_union` to compare coverage of the rope with actual
instance separation. It scores the union of predicted regions, including shadow
false positives, and is not a separate validated background extractor.
For example, all-black phase 0 with grayscale boundaries has foreground-union
IoU **95.22%**, yet matches only **18/515** eligible beads. A nearly complete
silhouette does not establish correct individual bead locations.

Final evidence: `output/detection-audit-r045-final/`, with input controls under
`output/detection-fixtures-r045-final/`. Report SHA-256:
`a788689beecd55253a3cf7c79e9052af2f663ce440977a5125754a469e62a65e`.
See the [all-gray detail](output/detection-audit-r045-final/gray-phase-0-detail.png),
[R/Y/black detail](output/detection-audit-r045-final/ryb-phase-0-detail.png) and
[whole all-black scene](output/detection-audit-r045-final/black-phase-0-whole.png).
Figures label their counts as whole-image scores, including in the detail panels.

All 54 repository tests passed, including seven new detection/evaluation checks.
Compilation, dependency consistency and whitespace checks passed. The additional
foreground-union checks were then added to the existing metric tests; those
seven tests passed again. Eleven current source hashes, 163 final artifacts and
24 fixture artifacts verify; the runner also checks all eleven current/historical
baseline sources and 148 baseline artifacts. Both RGB identity renders reproduce
the original saved beauty pixels exactly. No tracked POV scene changed.
After the initial scored run, only a foreground-union metric and panel title
clarification were added; final aggregate detection scores are unchanged.
No failed runtime test/audit and no threshold tuning. The initial local pip
installation failed on sandbox DNS; approved network access installed
scikit-image 0.26.0 and its dependencies in beads' .venv. No sibling environment
was modified. Generated development/final/reproduced files stay ignored.
Two final runs produce all **163 artifacts byte for byte identically**; reports
agree except the command's output path. Every trial's indices remain unassigned.
Visual review covered the gray/R/Y/black phase-0 details and whole black scene,
then six final detail panels in a contact sheet (opposite-hand RGB, weak-slot
view, half-phase palette controls and noisy R/Y/black), plus the final whole
R/Y/black figure. Development and final fixture runs each rendered eight images;
the reproduced segmentation run reused verified final fixtures. No full legacy
eight-case rerender was needed; identity renders and existing renderer tests ran.

The next experiment should implement **local model-guided visible-boundary
fitting and indexing**, starting with a small patch in these existing renders.
Use separated red/yellow regions or same-gray boundaries as anchors, compare
fixed and smoothly corrected predictions, and include a black run and wrong-phase
control. Freeze the patch selection and perturbations before fitting; stop after
the local contour/index report, before whole-ring propagation or photo claims.
Recommend gpt-6-astra / High in a fresh `/new` for that distinct implementation.
