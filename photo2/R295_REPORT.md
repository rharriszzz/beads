# R295 — joint correspondence and feasible geometry, with gains and regressions

R295 makes useful Phase 2 progress, particularly near conditional index **195**
and in two newly reserved large colored regions. It does **not** recover a unique
physical correspondence or solve the clear groups near **33 and 65**. A physically
feasible thinner, opposite-hand family now survives as a serious alternative,
but loses coverage within the requested index range. The selected model retains
R294's hand and reference origin. All variants and unsuccessful searches survive.

[Open the photographic review](review/r295/index.html) ·
[Selected full reconstruction](review/r295/R295-whole.png) ·
[221 positions](r295/results/R295-positions.csv) ·
[Surfaces, alternatives and uncertainty](r295/results/R295-positions.json.gz)

## What changed, and why

R294's failure was not simply a displaced centerline. Its objective rewarded many
small, correlated patches, allowed a wrong surface to contain them, and checked
physical feasibility after optimization. Large automatic interiors supplied more
useful extent information but were neither accepted contours nor verified owners.
Camera elevation, radial dimensions, axial thickness and pitch were coupled.
A smooth axis correction could not repair an incorrect local lattice.

R295 adds native photographic material coverage, paper contradictions, conflicting
red/yellow evidence on one modeled owner, predicted boundaries cutting bright
material, and agreement with measured image gradients/dark ridges. These are
**diagnostic photographic constraints**, not a new Phase 1 detector or certified
separator labels. Weak/dark pixels are not automatically classified as paper or
missing beads. The existing border-learned paper/palette machinery is reused.
No source support is moved, clipped, recolored, merged or replaced.

Bright patches remain separate measurements and may share an owner, but their
objective contributions are capped by conditional owner. Large automatic supports
remain fallible. A bounded integer beam allows unmatched regions and alternatives
including ±1, ±6 and ±7, with soft material, observed-valley and projected-neighbor
ordering penalties. This assignment search alternates with continuous geometry.
No repeating color sequence, manual screenshot correspondence, or per-bead repair
is used. Candidate first-hit surfaces and occlusion are computed from the actual
rounded hollow annulus, not spheres; bounding spheres only accelerate queries.

The beam's distinction between two regions and one owner remains a hypothesis:
internal shading can resemble a seam and automatic regions can be incomplete or
merged. The optimizer therefore cannot turn its preferred assignment into truth.

## Preserved baseline and evaluation design

The complete R294 search, evaluation, exports and PNGs replay exactly. The new
geometry reproduces its projected centers within 8×10⁻¹² pixels and agrees on all
2,365 eligible bright-patch pixel owners. The historical replay helper wrote its
own logs/receipt; those generated writes were archived under R295 and original
tracked bytes restored. Preservation checks cover every prior scientific file.

Before R295 fitting, freeze **123 patches and 36 substantial automatic colored
supports**, preserving exact native pixels and source records. Along the unchanged
image reference, validation intervals are 170–210 and 295–325px; final reserved
intervals are 410–455 and 575–620px. Supports touching an interval belong wholly
to it; a 15px exclusion buffer also removes adjacent training evidence.

| Evidence | Training | Development validation | Final reserved | Buffer |
|---|---:|---:|---:|---:|
| Independent bright patches |74|9|19|21|
| Larger automatic colored supports |21|5|5|5|

All fitting photo-grid cues obey the same geographic exclusions. Development
validation was exposed after the first local comparison; it is not the final
independent test. Final models were frozen before reserved evaluation. No geometry
or objective was tuned afterward. This is withholding within a repeatedly studied
photograph, not blind new-image validation or a calibrated accuracy estimate.

The exact R291–R293 accepted versions were inventoried. **None of the accepted
colored regions lies in this requested section.** They cannot honestly be claimed
as local accepted training/validation truth. The nearby automatic masks retain their
original status; accepted reflection regions never become physical black centers.

## Bounded development effort

1. **Controlled screen:** 80 hand/phase/elevation/dimension/spacing starts, 46 with
   positive contact certificates. Legacy radius, intended radius, thinner and
   thicker axial profiles were paired with spacing/scale controls.
2. **Local material fit:** six family/hand refinements on stations 50–290px. The
   training winner had intended radius, 0.85 axial thickness, pitch1.12, hand+.
   Local large-region training containment increased from about70% to83%. Adjacent
   validation regions improved 57.2%→61.1%, compatibility0/5→1/5; patches regressed.
3. **Full-run propagation:** the top three local training candidates and R294
   control were fitted to the full training window with smooth axis/spacing terms.
   The thinner family retained a training advantage but revealed index drift and
   material/visibility tradeoffs. Local improvement did not establish global success.
4. **Material/edge revision:** three candidates with stronger boundary/material
   weighting and capped region rewards; controlled axial thickness, progression,
   camera, perspective and slow phase corrections. Separate common-light refinement
   failed to improve the photographic model and is retained as a diagnostic.
5. **Joint discrete/continuous refinement:** both surviving hands, bounded ownership
   beam and further small phase/spacing/axis changes. The joint training objective
   selected hand−. The independently scored photometric objective still prefers
   the thin hand+ alternative: the choice depends on ownership assumptions.

There are **746 recorded continuous proposals** in the four refinement stages,
besides the initial screen and sensitivity/light controls. Checkpoints retain exact
source versions, candidates, trials, training scores and decisions. Search budgets
were bounded; final reserved outcomes did not trigger another repair.

## Quantitative comparisons

Compatibility means at least80% native support on one first-hit surface with a
20-point margin over the rival. It is not verified ownership. The same denominator
and compatibility rule are used for every model.

| Fixed evidence / diagnostic | R294 revised | R295 selected |
|---|---:|---:|
| New reserved large regions compatible |0/5|2/5|
| New reserved large-region mean containment |69.3%|68.6%|
| New reserved patches compatible |17/19|17/19|
| New reserved patch mean containment |89.9%|91.7%|
| Exposed development large-region mean |57.2%|54.6%|
| Exposed development regions compatible |0/5|0/5|
| Historical held patches compatible in −20…200 |22/31|23/31|
| Historical held large regions, original one-to-one rule |0/7|1/7|
| Historical held large-region mean, original rule |53.1%|60.0%|
| All123 patches compatible within requested run |105|105|
| All36 large regions compatible within requested run, many-to-one |12|15|
| Full bead-0 historical support containment |93.9%|90.3%|
| Predicted sites with some compatible photographic support |90/221|88/221|
| Sites without compatible support |131|133|
| Sites with modeled visibility below10% |66|62|

The reserved mean does not improve: two large gains coexist with losses elsewhere.
The larger historical comparison reuses **R294's exact one-to-one assignment**;
the new many-to-one evaluator gives different means (57.1%→63.8% on those seven).
Both ledgers are saved, and their definitions must not be mixed. Guard observations
beyond200 never count as requested-run successes.

The primary model's new reserved photographic diagnostics change as follows:
bright-material cuts38.1%→25.0%; predicted-boundary image-edge agreement0.502→0.569;
neighboring-color contradiction6.05%→5.77%; clear-color coverage77.0%→77.3%.
These are sampled 5px-grid proxies, not boundary precision or occlusion accuracy.
Paper contradiction is0 on these reserved grids for both, which says little about
shadowed/difficult paper; training is1.89% for both and development validation
worsens0.40%→0.80%. Correct front/back ownership still needs visual assessment.

### Specific photographed groups

- **Near195:** C-2038-0658 containment54.1%→96.7%, retaining conditional195.
  This is a training improvement, not an independent verification.
- **Reserved right bend:** P5-1994-0552 at163 improves72.1%→99.7%; C-1993-0580
  at169 improves78.1%→97.2%. These are the two new compatible reserved regions.
- **Near33:** E5-1633-0278 improves45.6%→50.5%, still clearly unresolved. The
  thin hand+ family offers a different division but does not resolve the entire run.
- **Near65:** C-1729-0337 regresses63.8%→61.9%. No correction is claimed.
- **Reserved regression:** C-1882-0479 at123 falls76.7%→54.7%, and C-1877-0445
  at117 falls79.8%→61.7%. The previously strong yellow at130 falls99.3%→81.1%.

[Native/photo/model comparisons](review/r295/index.html) show these failures as
prominently as the gains. Whole images show bead0 and the full requested sequence;
gray centers indicate unsupported geometric predictions, not measured missing beads.

## Geometry, indexing and physical feasibility

The primary keeps radius1.78453698, original axial proportions, minor radius4,
scale8.3px/unit and elevation60°. Progression changes slightly from6.5 to6.485
beads per turn. Pitch remains1.26, with small smooth log-spacing, planar axis and
phase corrections. Yaw and perspective remain zero in the selected fit. These
are fitted construction units and conditional camera parameters, not calibrated
physical dimensions. Bead0's projected center is(1503.23,272.53); its unchanged
observed region representative remains(1499.36,271.20). Bead200 projects to
(2025.09,698.81). No origin or global index shift is silently introduced.

The thin hand+ family uses axial thickness about0.83 of source and pitch1.12.
Changing thickness and spacing together is consequential: it produces a physically
feasible opposite hand, unlike R294's penetrating alternative. Its local successes
and full-run losses remain visible. It has only94/123 compatible patches within
−20…200 versus105 for the primary, and only78 supported sites versus88. Its two
historically compatible large held regions map beyond the requested run. This is
why a better-looking local surface or all-context score cannot determine the chain.

Controlled legacy-radius trials (2.11091575) have demonstrated overlaps in this
bounded geometry family, including a larger minor-radius/progression control.
This rejects those tested parameter combinations, **not every possible legacy-radius
construction**. Camera yaw/elevation, weak perspective, progression, minor radius,
shape and spacing sensitivities are retained. No independent evidence supports
adopting a changed camera calibration or universal new bead dimensions.

Every optimization proposal receives contact checking before acceptance. The R280
analytic support is affinely transformed for axial thickness. Positive separating
planes certify nonintersection of filled outer envelopes and therefore the hollow
beads. Failed certificates are labeled unresolved until additional evidence exists.
All34 failed screen cases ultimately show actual annular interpenetration. One
shallow32/38 overlap was missed by sampled surfaces; an independent Lipschitz
volume-subdivision audit found a point inside both annuli. That fallback can also
certify exclusion when hollow geometry resolves an envelope ambiguity; budget
exhaustion remains unresolved. No such unresolved primary is adopted.

The primary passes **874/874** independently recomputed separating planes, minimum
gap0.003456 source units. Dense bidirectional surface checks find no penetration
for any principal model. The positive margin is a floating-point geometric witness,
not an interval-arithmetic proof or photographic ownership certificate. Full records
and invalid controls are included; the earlier93-pair R294 failure remains unchanged.

114/123 patch assignments and148/159 combined patch/region assignments remain stable
between R294 and the primary, including unmatched states. Stability is conditional
on this model family. Competing hands change many indices. Each principal export
contains exactly221 positions, first-hit pixel runs, projected surfaces, centers,
visibility, correspondences/rivals, disagreements, physical status and parameters.
Primary finite-parameter sensitivity radii span approximately0.9–14.5px; these are
not confidence intervals and exclude hand/ownership uncertainty.

## Reflections, limits and next Phase 2 problem

One owner-balanced mirror-direction fit reduces training angular dispersion
66.5°→49.6°, but the two new reserved reflections worsen14.7°→27.9° median error
against the training direction. This split differs from R294's old neutral holdout
and must not be confused with its approximately50° result. Common-light fitting
still does not establish a reliable surface/owner interpretation. Diffuse maxima,
extended illumination, normals and wrong ownership remain confounded; no reflection
becomes a physical bead-center observation.

The strongest next Phase2 task is **joint local visible-surface/occlusion ownership
around33 and65 with independently supported material on both neighboring sides**,
including the two surviving dimension/hand families and explicit evidence against
splitting a coherent colored region. Add a richer but bounded local orientation/
packing model only if measured seams support it. Keep195 and the newly compatible
reserved bend regions as regression checks; freeze additional independent regions
before any new tuning. A camera/shape change needs stronger independent evidence
than another small loss reduction.

Future Phase1 recommendations only: retain larger coherent material and explicit
separator evidence; preserve multiple highlights with unknown shared ownership;
flag possible mergers or truncated supports without replacing them with model masks.
No Phase1 detector/data, beads.pov, previous experiment, production model or Phase3
was changed. No automatic R296.

## Reproducibility and delivery

[Reproduction commands](R295_REPRODUCE.md), [specification](R295_SPECIFICATION.md),
[checkpoints](r295/checkpoints), [search/assignment ledger](r295/results/joint.json),
[comparison](r295/results/comparison.json),
[exact historical-rule comparison](r295/results/historical-one-to-one.json).
Verification receipts are in `r295/results/audit.json`, `browser-check.json` and
`delivery.json` after execution/delivery. Two technical issues are preserved:
near-parallel cancellation in the independent support audit (repaired with the
algebraically equivalent cross-product norm), and an initially duplicated
`opposite` export after the selected hand switched (retained; the actual alternative
is explicitly named `hand-plus`). Neither changed fitted parameters after freeze.

Stop after scoped commit/push and independent remote verification for user review.
Use the requested GPT-6.1-Sol High setting for subsequent work; this report does not
assert that the agent can inspect or change the active model. No `/new` is required.

Completed verification: **10 analytic/real-data contracts**, all candidate/trial
parameters and scores from six replay stages, **35 byte-exact data/export files**,
**25 exact review PNGs**, eight native crops, **12886 unchanged prior
scientific files** and **69 unchanged feedback files**. Chromium loads
**11 images**, checks **50 links**, exercises view/toggle/zoom and passes
desktop and narrow layouts. No final-model parameters changed after evaluation.
