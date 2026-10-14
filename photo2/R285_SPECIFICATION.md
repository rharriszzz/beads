# R285 — brightness-driven Phase 1 and Method J regression review

This is the active scientific specification, recorded before algorithm changes.
Repository rharriszzz/beads; branch photo-2-strategy-v3; work under photo2.
User request R285 supersedes the R284B recommendations. Preserve R284A/R284B
implementations, results, raw photographs, inventories and provenance.

## Governing principle and user decisions

For red/yellow photographic interiors, follow actual brightness and color evidence.
Stop at a meaningful dark separation between beads, seam/occlusion, or background.
Interpret darkness locally: ordinary shading, texture and weak reflections do not
by themselves establish another bead. A narrow bright continuation can be valid;
a wide region can leak; smoothness does not establish correctness. Shape
regularization assists intensity evidence, never replaces it. Neither an absolute
darkness threshold nor compactness/area/solidity/detection count is an objective.

Picture1: the user does NOT approve T thickness pruning. Its removal may discard
legitimate photographic material. Do not promote T. Explain why meaningful dark
separations were crossed; preserve substantial supported material. Test the lower
yellow, left red crossing the line, and right yellow independently. Distinguish
narrow genuine continuation from connection to a neighboring bead using pixels.

Picture2: all R284B reflection methods are acceptable to the user; smoother
contours are preferred. R2/R4 are reasonable candidates, R1 a reference. Compare
smoothness, localization, brightness agreement, centroid stability and separate
nearby features. Select a sensible experimental default with alternatives when
ambiguous. Black supports are specular-reflection regions only: no dark collars,
physical silhouettes, inferred centers or certified bead ownership.

Picture3: J is the ONLY satisfactory displayed method to the user. J is the primary
replacement candidate. The user is willing to switch subject to understanding and
addressing regressions; do not reject it for being less compact or unlike old masks.
No production replacement is authorized before this review and evaluation.

## Later user steering: edge and shadow disagreements

The user explicitly permits disregarding edge/shadow areas to obtain consistently
good results on the remaining visible material. Do not prioritize J disagreements
that arise from those already-excluded areas. Preserve their evidence, but classify
them as peripheral/low-priority controls rather than central regressions. Focus
development and recommendations on clearly visible interiors and centerline cases.
This is an evaluation priority, not permission to hide failures on clear material.

## Required diagnosis before replacements

Read permanent Phase1 contract, R284B explanation/report, R284A report, relevant
R282/R283 reports/code and original/saved photographic crops. Explain precise
roles of hue/saturation, luminance, local minima/saddles, gradient magnitude,
connectivity, opening/erosion, fixed radii, shape regularization and competing
photographic seeds. Locate where shape displaced image evidence and determine
whether dark stopping was lost, weakened or implemented incorrectly. Save a short
technical account before new algorithm code.

## J regressions and sample frozen before development

Run unchanged J and previous alternatives on the same photographic candidate set.
Automatically select approximately10–16 varied examples, balancing failures and
improvements, including:
1. Red interiors truncated by J.
2. Yellow supports potentially leaking to another bead.
3. Abnormally large regions.
4. Search-radius clipping.
5. Loss of previously convincing material.
6. Large centroid changes.
7. Genuine-looking improvements over old supports.

Review coordinates select evaluation panels only, never inference. Reproducible
selection scores are diagnostic flags, not ground truth. Do not call every old/J
difference a regression. For each example show raw native/enlarged photos, original
support, J and improved alternatives; gained/lost pixels, brightness/gradient
profiles and centroid. Explain selection reason, what changed, whether a plausible
brightness transition supports it, boundary defect versus ownership uncertainty
versus mere algorithm disagreement, and proposed correction or unresolved status.
Retain failed examples and uncertainty rather than replacing them with easy cases.

## Several targeted improvements

Investigate red truncation, weak-cue leakage/oversize, fixed-domain clipping,
same-color connections and centroid movements. Candidate directions:
- Local dark minima/saddles with photographic evidence on both sides.
- Adaptive illumination-aware contrast without unconstrained expansion.
- Competition between independent photographic features; multiple seeds alone
  must not imply multiple beads.
- Larger/adaptive domains and explicit clipped/unstable abstention. A search circle
  is a computational bound, never an accepted photographic boundary.
- Modest intensity-informed smoothing for noise/one-pixel instability; preserve
  genuine photographed narrow structures. No morphology-based tail deletion.

Keep J unchanged as the primary control. Preserve all alternative algorithms,
failed attempts, parameters and numerical results. Do not tune thresholds merely
until reviewed examples look attractive. Document hypotheses and mechanisms first.

## Evaluation and generalization

Develop on the frozen review sample plus the mandatory old observations. Freeze
candidate methods before opening additional photographic validation results.
Use additional automatically chosen regions not used for development. Evaluate:
boundary intensity/gradient agreement; dark-seam crossing; retention of supported
bright material; search-domain clipping; connectedness; false splitting; overlaps;
centroid movement; centerline crossing/near evidence. Separate direct native
measurements, photographic judgments, uncertainty and physical-body assumptions.

Use independently rendered synthetic scenes where possible, with identity truth
hidden from the detector. Test specific image-processing mechanisms, not replace
photographic inspection with synthetic precision/recall. Include normal shading,
texture, narrow bright continuation, dark separation, multiple highlights and
background controls. Do not optimize geometry, appearance or Phase2/3 scores.

## Centerline and shared records

Goal remains every visible crossing bead and often two/three relevant observations
at a station. Both sides are eligible when the line passes between beads; impose
no exact count. Use measured support geometry, signed side and longitudinal
station. Colored compact interiors can understate full-body crossing. Black
reflection position cannot establish whole-body extent: retain unknown crossing.
Look for previously missed visible colored features and material discarded by old
compact masks. Preserve all uncertain observations and source provenance.

Keep importance, phase origin, photographic reliability, color reliability,
visibility, physical identity reliability, native support, measured location,
uncertainty and evidence links separate. All Phase1 observations remain important.
No reliability inflation for larger area or smoother lines. No physical indices,
Phase2 centers/geometry/correspondence charts or Phase3 pattern guesses establish
Phase1 observations. Production integrated pipeline remains runnable and unchanged.

## Ordered checkpoints and deliverables

1. Record decisions; update permanent specification/handoff.
2. Diagnose drift before replacement code.
3. Freeze/classify the representative J sample.
4. Develop several targeted J improvements and preserve failures.
5. Compare on frozen development and mandatory examples.
6. Freeze then evaluate additional photographic regions and specific synthetic controls.
7. Compare methods, recommend rules and a reflection default, document limitations.
8. Build review package and stop.

Deliver diagnosis, revised permanent principle, unchanged J, several improvements,
10–16 representative examples, raw/annotated photos, separate reflection comparison,
quantitative failures, centerline diagnostics, recommendations, reproducibility,
scientific tests, intermediate evidence, updated handoff/checklist. Make routine
choices independently; no manual labeling request. Save checkpoint notes so context
compaction does not lose the intended science or unfinished experiments.

Commit/push scoped work to photo-2-strategy-v3, verify remote and final status.
STOP for the user's review of J regressions and improved boundaries. Do not adopt
a global Phase1 inventory or restart Phase2/global fitting/Phase3 pattern work.
Keep current model/reasoning; no /new required.
