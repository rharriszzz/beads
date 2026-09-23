# Reconstruction experiments

Append results; preserve failed attempts and limitations.

## 2026-09-23 — Initial forward model and diagnostic baseline

Started at `402663e` on new branch `photo-2-reconstruction`. All eight sibling
repository pulls reported already up to date. Existing `beads-render.png` and
`image-to-pattern/pattern_from_photo/` were present before work and preserved.

The saved FFT-explorer centerline visually follows the full nonconvex necklace
shape. A periodic cubic fit has arc length 9,235.5869 source pixels. The first
POV render exposed a horizontal reflection caused by `look_at` rotating the
camera basis. Explicit `direction -z`, `right x` and `up y` correct it. A
color-mask overlap check now records ordinary and reflected comparisons.

The first prototype ran on system Python 3.10.12. After the user's Python 3.12
instruction, created beads' own environment, installed NumPy/SciPy/Pillow, and
reran the baseline with CPython 3.12.14. No other environment was changed.

Five focused numerical tests pass: closed-path spacing/frame continuity;
handedness reflection and height; photo-specific paper/shadow rejection;
synthetic 271-bead repeat recovery with 55% hidden and 6% randomized labels;
preservation of unknown residues. A test initially exposed palette-ID-dependent
tie breaking in held-out scoring; fractional tie credit fixes it and makes
the candidate ordering invariant to color renumbering. These tests validate
parts of the machinery, not synthetic-image round trips or the real pattern.

Legacy regression: rendered original HEAD and modified `beads.pov`, both at
320x240 and clock 0.32 with two threads. PNG pixel arrays match exactly, maximum
channel difference zero. Evidence: `output/legacy-check.json` and render logs.

Baseline photo preview: 800x1002, 2,698 model beads, 415 turns, effective pitch
22.2544 pixels, all positions finite. Rough color-mask IoU is 0.4731 versus
0.1044 for a horizontally reflected render. This checks broad registration;
it is not a bead segmentation accuracy score. Visually the lattice remains
too regular and square, with mismatched highlights, local bead orientation,
color boundaries and shadow softness. Paper color/texture are initial proxies.

For negative sign: 1,047 retained color observations; top-ranked period 202,
held-out accuracy 0.4497, majority baseline 0.4315. For positive sign: 1,018
retained observations; top-ranked period 311, accuracy 0.4555, baseline 0.4064,
held-out coverage 0.9614. The hypotheses have different sampled positions;
their accuracies are not a controlled handedness comparison. **Both helicity
and repeat remain unresolved.** A visually fitting observation render is not
evidence for the inferred period. No scientific acceptance gate is passed.

Next: label bead centers/colors in several separated sections of the unwrapped
rope, then fit pitch, circumference count, phase, local twist and hole-axis tilt
against those observations before ranking repeat lengths again.

## 2026-09-23 — R014 fixed-label geometry comparison

On daisy, clean `photo-2-reconstruction` at `f6fb3b3`, fetch verified 0/0 with
upstream after retrying outside the read-only .git sandbox. Python 3.12.14.
The supplied session/status and continuation request are retained under R014.

Created 103 provisional visual center/color annotations across six 160-pixel
unwrapped patches (three bends, three straights), before fitting model overlays.
Colors and unknown original chain indices are retained. Dark bead/glint boundaries
are uncertain; four pixels is only a typical visual annotation-error estimate.
The dataset is not complete or human verified. See `GEOMETRY.md` for equations,
parameters, result tables and reproduction commands.

Fit both hands to the exact same 51 training centers. Three separate validation
patches use 25 left-half centers only for local alignment; 27 right-half centers
are withheld. This is partial patch holdout, not fully unseen-patch prediction.
Unwrapped withheld RMSE: negative 6.2728 px, positive 6.4124 px. Original-photo
withheld RMSE: 6.2698 versus 6.4141 px. Training prefers positive (3.9479 versus
5.9696 px), and withheld patch preferences disagree. All four seed searches
converge numerically, but the positive seeds find distinct radius/count solutions.
No hand or fitted dimension is accepted; high density is favored by the incomplete
point-set objective, which does not penalize unmatched model beads.

Resolved an identifiability question algebraically and numerically: pitch,
circumference count and unconstrained linear twist have an exact gauge freedom.
The conditional numerical fits therefore fix twist to zero. Center-only data
also cannot constrain hole-axis tilt, body dimensions or perspective; no hole
rims were confidently labeled. Removing assumed front-half visibility yields
an exact projected-hand ambiguity. Keep all these limitations explicit.

Two full deterministic runs reproduced the same numerical results; the second
updated source/data provenance and identifiability fields after documentation of
annotation uncertainty. Enlarged source, label and positive-fit panels were
inspected for bend_b and straight_b. The original full centerline/unwrap and all
six source patches were inspected before labeling. No annotation was adjusted
using fit residuals. Nine focused tests passed, including four new numerical
checks; the known-lattice test does not validate synthetic-image recovery.
No POV-Ray source changed; legacy render rerun, material fitting, camera model
comparison, whole-necklace fit, synthetic-image round trip and repeat search were
not performed. Generated images/reports and .venv remain ignored.

Next bounded task: occlusion-aware synthetic patch benchmark in POV-Ray, with
Python center/outline scoring, testing both hands, bead density and missing labels.
Stop at measured recovery or ambiguity on known geometry before real-photo refit.

R014 final-run SHA-256 provenance:

- `photo2/geometry-labels.json`: `c8f2f5c34dd72a661e7cd30b03633585d5a837a31254f0cc38eb0d4df561626a`
- `photo2/fit_geometry.py`: `b64fcdceb43512cbca21e06cdebeb4ff1457ea30dd2a947ee26ed473b762870a`
- `photo2/reconstruct.py`: `35322da2ed21c39f5b1c1cd68401377b811a53e2786fa1b11288e61079d901f9`
- `photo2/centerline.json`: `49c59cc6049815e9cac9fd94e097e0aaf1d9f647d287d7920793aca2acfd9f36`
- `beads-photo-2.jpg`: `eb7c9edb62f5580ef56632872da48da92556d62b758295137068cc2404dc8fbb`
- Generated `output/geometry-fit/report.json`: `1c6c18da6944541e566689d8efe0c98c3e5ea0f911ad7bf92c171fee3e9ab705`

## 2026-09-23 — R015 synthetic occlusion benchmark

Started on daisy at clean `01dd173`, tracking `photo-2-reconstruction`; fetch
confirmed 0/0 after escalation for read-only .git. User's old usage/current
session status are separately attributed in R015. Python 3.12.14, NumPy 2.5.3,
SciPy 1.18.1, Pillow 12.3.0, POV-Ray 3.7.0.10.unofficial.

Added `synthetic_benchmark.py`, `synthetic-patch.pov` and four focused tests.
Each complete run renders 84 images: 24 candidate ID masks, two beauty images
and 58 isolated reference beads. Ground truth has 29 visible centers per hand;
12 per hand are behind the cylinder's front half. Reference bodies are certified
non-intersecting by enclosing spheres. Partial occlusion affects 15/19 beads;
centroid-to-center RMS shifts are 1.5336/1.4347 units (negative/positive hand).
Exact parameters, equations, metrics and limitations are in `SYNTHETIC.md`.

Both-hand density stress candidates win all 24 full-label trials at sigma=2
coordinate noise. Center scores also cannot distinguish body size, tilt or depth
reflection. Internal boundaries distinguish these particular alternatives under
perfect segmentation, including tested 75%-missing instance subsets; silhouette
alone leaves reflection exactly ambiguous. Pitch/count/twist-equivalent geometry
has pixel-identical ID masks. No geometry accepted for the real photo.

First run: `output/synthetic-benchmark/`. After adding recorded trial IDs/protocol,
source-test hash and runtime image-invariant/visibility assertions, second full
run: `output/synthetic-benchmark-verified/`. All candidate scores and every prior
trial score reproduce exactly. All 86 common decoded image arrays match, as do
24 include files byte for byte. An initial raw-hash assertion failed: POV-Ray's
84 PNGs contain changing render timestamps in tIME/tEXt chunks. Pixel comparison
and metadata inspection resolved this; actual per-run file hashes are retained.
All final report source/artifact hashes match their files. Final report SHA-256:
`398b9424a9b8acb4efb33b8eb4c22745ed2b9b4caaadf545471a685d88043a66`.

Inspected negative-hand beauty and both-hand ID/boundary comparison panels.
Thirteen tests pass, including a real POV-Ray front/rear occlusion integration
test; py_compile passes. Final diff/whitespace checks precede publication. No
legacy scene changes, so no repeat legacy pixel test. No photo refit, material
optimization, curved/perspective test, segmentation from beauty images or repeat
inference. Outlines stay exact when centers are noisy; no robustness claim follows.
No sub-agent work, model change, remote messaging or computer transfer.

Next: shaded synthetic boundary extraction with controlled blur/noise and local
alignment fitting; validate errors/ambiguities against hidden mask truth before
photo refit. Step 2 remains open. Generated outputs and .venv stay ignored.
