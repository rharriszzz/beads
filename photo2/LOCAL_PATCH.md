# Local calibrated contour/index experiment — R047

R052 follow-up: [REGION_ANCHORS.md](REGION_ANCHORS.md) replaces the click-margin
gate with observed-region correspondence and measures fixed jitter/spatial
transfer. It improves some cases but exposes wrong-hand alternatives and region
selection errors. The R047 protocol/results below remain historical evidence.

Protocol frozen before the first scored run. This first test supplies the legacy
camera, global rope geometry and scale as calibration. It tests local boundary
alignment and conditional indexing, **not** image-derived centerline/width/pose.
Candidate ID renders are newly generated forward predictions. Observed ID masks
are read only for evaluation after fitting. This calibration is an explicit
assistance condition; an automatic geometry/seed condition remains future work.

The maker uses specular reflections, otherwise periodic saturation/value changes,
for black beads. The first image evidence is a union of saturation/value gradient
edges; grayscale is an ablation. This does not yet model highlight placement or
measure periodic signals. Anchors have four recorded clicks, preferably spanning
±1, ±6, ±7. Both helicities survive until the fitting evidence separates them.

Frozen patch: full-image box (1900,650,2310,1060), chosen from beauty images before
scoring. Positive-hand clicks: (2160,830), (2190,850), (2225,815), (2225,885).
Negative-hand clicks: (2160,850), (2190,870), (2225,820), (2240,880).
Clicks are an assistant-recorded visual assistance condition, not maker-reviewed.
Their success/failure is measured; no truth-based correction is permitted.

Eight independent model renders: both hands, cross-section phases 0, .25, .5,
.75 turns added to the original row-angle equation. Shapes, hole axes, camera
and ring dimensions are unchanged. Candidate labels provide relative indices
only conditional on their hand/phase/anchor, never an observed absolute origin.

Four source views: R/Y/black, all-gray, all-black (positive hand, phase 0), and
negative-hand RGB phase 0. Three target conditions: identity; translation
(dx=8,dy=-6); smooth 2-D warp dx=8(q²-1/3), dy=-4q where
q=(y-204.5)/205 in the patch. These are paired alignment perturbations, not
independent scenes or physically rendered deformations. Preserve all misses.
Add false-background-anchor controls and a one-click slip control. A global
index-origin shift is allowed and is not itself an error.

Compare saved gray-boundary watershed without a model, fixed candidate contours,
translation fit, smooth quadratic corrections, and exact-hand/phase/warp oracle
alignment. Freeze all thresholds in local_patch.PARAMETERS: gradient .035,
smoothing sigma 1 pixel, distance cap 12 pixels, support distance 2.5 pixels,
required supported contour fraction .60, minimum area 100 pixels, border 12.
Fit at most 1500 deterministic contour samples from top 2/3 of each template;
bottom 1/3 is withheld. Translation search grid ±12 by 6 pixels, coefficient
bounds ±16 pixels; smooth-fit penalty .20; at most 60 optimizer evaluations.
Retain train-score ties within .5 pixel among candidates whose four clicks
land at least 8 pixels inside distinct bodies, form a connected neighbor graph,
and span all three families. Record every rejected anchor and every hypothesis.
A forward model alone does not detect a bead: require contour support and
exclude clipped bodies. Acceptance remains an unvalidated hypothesis, measured
against evaluator-only truth. Report unresolved alternatives without choosing
by truth, and keep unknown colors separate from index uncertainty.

Report region IoU >.5 matches, contour residuals, withheld residuals, missing
indices, relative-index errors, colors, anchor topology and both-hand alternatives.
The oracle gives a calibrated alignment ceiling. Incorrect-family assignments
and failures of the anchor protocol are results, not permission to edit clicks
or score settings. Stop after this local comparison, before ring growth/photo fit.

## Results and limits

All thresholds, click coordinates and candidate phases remained unchanged after
scoring. The initial implementation incorrectly warped earlier segmentation
masks for the no-model comparison. Before the final runs this was corrected to
rerun segmentation on the perturbed beauty pixels (full-image scale preserved;
only the boxed patch is warped). Identity cases reuse verified original masks.
This changed baseline scores, not model fits. After reviewing the first final
pair, reporting gained conditional index labels, a corrected generic edge-panel
caption, and the same wrong-seed/phase controls on all three R/Y/black conditions.
The latter includes an accepted positive condition, avoiding a solely vacuous
negative test. None of these changes alters fitting or acceptance settings.

The experiment comprises 14 paired trials: four appearance/hand cases × three
warps, plus grayscale-evidence ablations for unwarped R/Y/black and black.
There are 336 candidate/alignment fits, 224 of them optimized. These are one
patch with shared geometry, not 14 independent holdouts. The lower third of
**template contour coordinates** is withheld from the objective; the image
edge field is shared. These are spatial residual checks, not independent images.
The 3-D pose, diameter, scale and centerline were supplied, not estimated.

Two smooth-fit trials retain a conditional index hypothesis:

| Target patch | Eligible truth beads | No-model matches / false predictions | Fixed accepted matches / false predictions | Smooth accepted matches / false predictions | Correct region + color + relative index |
| --- | ---: | ---: | ---: | ---: | ---: |
| R/Y/black, smooth target warp | 38 | 26 / 17 | 33 / 1 | 34 / 1 | 34 |
| All-gray, smooth target warp | 38 | 31 / 3 | 36 / 1 | 38 / 0 | 38 |

Both retain positive hand, phase zero. The R/Y/black fit makes 35 accepted
region/index proposals: 34 match truth with correct color/index, one region is
false. Missing true source indices are 418, 428, 429, 435. Gray has 38 correct
region/color/index proposals and no eligible misses. The source-relative origin
is the first supplied click; the absolute source origin remains evaluator-only.
These exact synthetic matches are conditional calibrated results, not a recovered
photo pattern or validated general indexer.

The **anchor gate is brittle**: smooth fitting retains no candidate in the other
12 trials, including all four unwarped appearance/hand inputs. Both manually
chosen groups really span 1/6/7 and are connected, but some clicks are too near
candidate boundaries for the arbitrary eight-pixel interior requirement. For the
best positive-hand unwarped gray fit, click 0 has a 6.4-pixel margin; for the
negative-hand RGB fit, clicks 2/3 have 5.0/2.2-pixel margins. A small target warp
moves the positive-hand group across this threshold. This is a failure of this
implementation's acceptance rule, not of the maker's three/four-bead advice.
All-three-family and eight-pixel requirements were our conservative choices;
the maker said all three directions are *best*, not universally required.
The experiment has not validated automatic seed selection or anchor robustness.

Without silently bypassing that gate, useful contour diagnostics remain:

- Translating the positive-hand R/Y/black target by (8,-6) pixels makes fixed
  placement rank the wrong hand first. Translation/smooth fitting ranks the
  correct hand/phase first and supports 32/34 eligible true regions with zero
  false supported regions. The anchor still fails, so **no indices are accepted**.
- For the smoothly warped gray patch, fixed-to-smooth supported matches improve
  36→38 and false regions 1→0. Withheld mean edge distance improves 1.32→1.20 px.
  R/Y/black improves 33→34 matches with one false region in both, but its withheld
  distance does not improve (1.59→1.60 px). Negative-hand RGB likewise gives no
  smooth-fit holdout advantage (.32→.56 px); do not claim general correction gains.
- On the unwarped R/Y/black image, smooth contour-only scores put positive hand /
  phase 0 at 0.4493 px and negative hand / phase .5 at 0.9329 px, within the
  preset .5-pixel tie tolerance. Before applying the failed anchor gate, the
  former supports 34 matched regions with 34 correct candidate relative indices;
  the latter supports 26 matches but only 6 correct candidate indices, plus seven
  false regions. Contour similarity is insufficient to discard competing hands.
  Neither receives an accepted index in this trial.
- Every all-black smooth fit fails to recover a supported true region; the
  lowest-training-score candidates propose two false supported regions per trial.
  The anchor gate prevents indexing them. Even the exact alignment oracle has
  image support for only three eligible black beads. Exact geometry alone would
  reproduce all visible masks, but must not be counted as detecting those beads.
  A fixed model accepts two correct indices in the smooth-black condition; that
  isolated result does not rescue automatic fitting.
- S/V gradients include specular-highlight edges, but they are not a specular
  forward model or a periodic-signal detector. All-black S/V and grayscale scores
  coincide in the identity case. Preserve the maker's saturation/value-periodicity
  suggestion for a later explicit test rather than claiming it has been exhausted.

Three smooth optimizations reach the 60-evaluation cap: opposite hand / phase .5
on translated R/Y/black, and positive hand / phase 0 on translated/smooth black.
Their returned parameters and non-success statuses remain in the reports. None
is retained. No global optimum or exhaustive phase/capture-range claim is made.
The oracle's independently rendered zero-phase candidate matches the observed
ID geometry exactly for both hands and every tested warp; truth never repairs
fitted parameters, clicks, colors or indices.

## Reproduce and inspect

```sh
.venv/bin/python photo2/local_patch_audit.py --templates photo2/output/local-patch-templates-r047-final --output photo2/output/local-patch-new
.venv/bin/python -m unittest discover -s photo2 -p 'test_*.py' -v
```

Defaults require the verified R045 fixture/detection directories and
`neighbor-audit-final`; recreate the baseline with NEIGHBORS.md, then run the
DETECTION_PROGRAM.md command if missing. Template generation uses eight actual
POV-Ray model renders; subsequent runs verify and reuse them. Their manifest
preserves the generator source snapshot, generated scene sources, commands and
hashes. New tracked scene sources require a new template directory. No tracked
POV source changed. The audit refuses nonempty output directories.

Each trial saves prediction JSON **before** reading observed ID truth, all 24
candidate/alignment masks plus the no-model mask, separate evaluator JSON, input
pixels and a whole-image/detail panel. Predictions retain both hands/all phases,
unsupported objects, unknown colors and conditional indices. Evaluations retain
eligible misses and every match/error. All model masks in panels are predictions;
white-on-black numeric labels appear only for accepted conditional smooth-fit
indices. No truth-based choice of display candidate: panels use the lowest
training score even when its anchor is rejected.

Next bounded task: replace the brittle click-interior gate with evidence from
three/four **observed bead regions**, preserve both hands, and test prescribed
click jitter and a separately frozen patch. Use image-derived interiors/region
support; do not fix anchors using source masks or merely lower the margin after
seeing these scores. Stop after local detection/index/seed-robustness evidence,
before ring growth or photo fitting. Recommend gpt-6-astra / High, fresh `/new`.

Final evidence: `output/local-patch-r047-verified/report.json`, SHA-256
`825ad517d0b4a970c6f1d2462e9815e8ae4c8c543485917caae9780d3139f9ec`.
The false-background, duplicate-neighbor click and excluded-true-phase controls
retain no candidate in all three R/Y/black conditions, including the successful
smooth-warp positive. These are limited controls, not measured general capture.

All **61 tests pass**, including seven new local-fit tests. Compilation, dependency
consistency and whitespace checks pass. Eleven current source hashes, 70 output
artifacts, 34 template artifacts (including generator snapshot), 24 R045 fixtures,
163 R045 detection artifacts and 148 baseline artifacts verify, with all four
input report hashes bound. Two final runs reproduce all 70 artifacts byte for
byte; reports agree except command output path. Numerical fit/index results
remain unchanged by the final reporting/control additions. No failed unit test
or audit; three optimizer budget stops are recorded above. Existing small render
tests ran, but unchanged tracked POV source did not need a full legacy rerender.

Visual review covered all 14 initial final panels in contact sheets, then the
final indexed [gray](output/local-patch-r047-verified/gray-phase-0-smooth-sv-panel.png),
[R/Y/black](output/local-patch-r047-verified/ryb-phase-0-smooth-sv-panel.png), and
[black failure](output/local-patch-r047-verified/black-phase-0-identity-sv-panel.png)
figures at full size. Generated figures, masks, template scenes and environments
remain outside Git. No automatic photo seed/centerline/geometry inference, real
photo segmentation, material fitting, whole-ring growth or repeat recovery ran.
