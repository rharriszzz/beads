# R279 frozen protocol v1

Frozen before neighbor predictions or synthetic evaluation. Seed 279013.
Inputs: original JPEG decoded through Pillow/EXIF, beads.pov bead macro, pure
photo2/bead_placement.py (Rope dimensions and analytic surface sampler only).
No historical observations, fitted poses, charts, ownership answers, or centerline
are runtime inputs. Historical reports inform exclusion decisions only.

Test 1 compares A peak Euclidean distance; B watershed interior centroids with
same-region grouping; C B plus native line-valley/color separation and scale
persistence. Nearest means distance between visible-body area centroids, not 3D
centers. Estimated interiors only approximate these; interval overlap is ambiguous.
Surface proximity is minimum supported-pixel distance, a partial-support upper
bound on full visible-surface proximity. The detector may miss bodies entirely.
Twenty-one anchors: cycle image-derived red/yellow/neutral appearance classes,
quality-filter then spatial farthest-point selection. No predictions enter selection.
All uncertain candidates survive. No geometry enters this test.

Synthetic scenes: 12 independently seeded POV-Ray photographs, both hands,
three camera inclinations, two lights/material conditions, randomized colors,
and same-color scenes. Fixed intended radius, pitches 1.00 and 1.10: intentionally
include packing failures, report these separately rather than correcting truth.
Identity render is a separate unlit render; IDs are evaluator-only. Membership-only
oracle supplies two visible masks, never physical indices. Evaluation is a separate
command, after all observations, pairs, parameters and C/D predictions are saved.
No parameter tuning from synthetic labels. Any bug fix must be documented.

Test 2: fresh straight-local construction, 6.5 beads/revolution. Both hands;
AB index hypotheses ±1/±6/±7, plus explicit non-neighbor/unmodeled alternative.
Uniform phase grid, camera inclination grid; translation/rotation/scale fit AB
only. A/B interior extent bounds scale; broad image structure estimates tangent
without observed C/D coordinates. Retain top two AB candidates per hand/family.
Predict C (+1,+6,+7 triangles, sign reversed for negative AB); store surface
samples and visibility before held-out scoring. Source pitch first; sensitivity
.95/1.05/1.10 only, never 1.30–1.45. No independent bead translations.
A collision rules out a physical interpretation, but preserve nominal predictions
as explicitly invalid diagnostic alternatives. No unique hand is inferred.
After C scoring, conditional ABC refinement may use C and must freeze D before D
scoring. Neither a close peak nor a surface overlap certifies a real correspondence.
All real results are proposals without accuracy labels. Stop before growth.

## v2 correction, before new-seed evaluation

First run preserved in review/r279/failed-hole-fill-control with executable source.
A topology bug filled the entire enclosed necklace-paper area as foreground, giving
12,560 observations and paper anchors. Remove binary_fill_holes; enclosed paper must
stay paper. Replace misleading fixed red/yellow reporting split with two learned
circular foreground hue clusters (no manual locations/identities). Correct unused
triangle metadata to [0, AB_delta, C_target]. No score or decision threshold changed.
Use fresh seed 279014; retain all v1 metrics and artifacts. This is a bug-corrected
second run, not an untouched first test set. B implements possible-same-body penalties,
not a verified merge; watershed labels are segmentation hypotheses, not bead IDs.
The flat-disk unit fixture lacked red highlight maxima; add highlights to exercise
deterministic detection, without changing detector thresholds or evaluated scenes.
