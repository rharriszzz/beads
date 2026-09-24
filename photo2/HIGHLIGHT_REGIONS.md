# Enclosed-highlight region repair — R055

## Frozen protocol before truth scoring

R054: beads are smoothly rounded, usually with one bright patch depending on
lighting. There is no one-highlight-per-bead constraint. R052's image-only
diagnostic finds enclosed unassigned bright cavities in the gray patch; some
nominal clicks land there. These are gaps in segmentation, not bead holes.

Compare saved R052 observed regions with **one fixed conservative repair**:
find zero-label cavities with no eight-connected path to the crop exterior.
Fill a cavity only if its eight-neighbor boundary touches exactly one nonzero
region label and every cavity pixel has saturation <.20 and value >=.75. These
are R045's existing foreground-exclusion thresholds. Assign the enclosing label;
never alter an already assigned pixel or create a new region. Multiple glints
are permitted. Cavities shared by regions, dark/saturated missing areas and
open or diagonally open gaps remain unresolved. No size/shape or truth-based
threshold tuning. This rule cannot repair merged/split regions or recover a
missing bead; a bright background cavity enclosed by one mistaken region can
still be filled incorrectly, so added background pixels must be measured.

Reuse all 16 R052 conditions on the original/right and second/left frozen
patches, all 128 saved smooth candidate fits/masks and both helicities. Keep
the three/four-anchor groups, 17 variants (R052 RNG seed 5201), background,
duplicate and excluded-phase controls unchanged. Apply repair to each actual
observed image/mask, never to a truth image or warped repaired output. Compare
the same observed-region gate for both methods; no legacy-margin change.
Write predictions before loading evaluator truth. Require old gates, retained
hypotheses, scores and baseline evaluation to reproduce R052 exactly.

Evaluate region IoU >.5 at the existing >=100-pixel/12-pixel-border policy,
color/unknowns, missed indices, splits/merges and foreground errors. Separately
score anchor identity, accepted hypotheses, conditional relative indices and
wrong-index alternatives. Count added pixels by truth foreground/background;
preserving segmentation labels does not prove the original regions were right.
Whole-patch model outputs, contour support, fit scores and colors stay fixed;
only observed-region correspondence and the anchor gate can change.

Focused schematic controls cover multiple reflections, dark/saturated gaps,
missing regions, shared cavities, open/diagonal exits, empty black/white images
and idempotence. Saved black scenes and shadows remain in the rendered audit.
An additional ablation deletes the region at the first nominal click (if any)
before repair and records whether any deleted pixels are filled. A zero-label
click makes that ablation inapplicable, not a successful deletion control.
Stop after local region/anchor/index evidence and checks, before ring growth,
photo segmentation/fitting or repeat inference. Keep the provisional 2,698
photo count without divisor filtering, repeat bound <400 and unknown colors.

## Results

The repair improves gray-anchor jitter tolerance but does not find additional
beads or resolve helicity. All **70 filled cavities / 4,672 added pixels** belong
to the correctly matched surrounding bead; none belongs to background or another
bead, and none has unresolved ownership under the evaluator's IoU >.5 match.
These totals sum paired perturbations of shared scenes, not independent beads.
Every previously assigned pixel retains its label. Foreground false-positive
pixels, region match/false counts, split/merge counts and missing-bead sets remain
unchanged in all 16 conditions. Existing shadow mistakes remain; none is added.

| Anchors | Old accepted /272 | Repaired accepted /272 | Accepted with any wrong index, old → repaired | All retained seed bodies correct, old → repaired |
| --- | ---: | ---: | ---: | ---: |
| Three | 123 | 134 | 36 → 36 | 118 → 129 |
| Four | 100 | 115 | 36 → 36 | 85 → 99 |

Each accepted trial counts once even when several candidates survive. Wrong-index
counts flag any retained candidate with a wrong matched index; false regions and
wrong seed identities are recorded separately. Higher acceptance is not proof of
correct seeds or hand. Region-gate baseline, retained hypotheses, baseline
evaluation and every prior score reproduce R052 exactly.

| Gray condition | Filled pixels | Observed matched / eligible, unchanged | Four-anchor acceptance, old → repaired |
| --- | ---: | ---: | ---: |
| Original identity | 1,072 | 31/37 | 6 → 11 of 17 |
| Original translation | 1,072 | 27/34 | 6 → 11 of 17 |
| Original smooth | 1,074 | 31/38 | 5 → 9 of 17 |
| Second identity | 1,222 | 30/35 | 11 → 12 of 17 |

The remaining fills are second-patch R/Y/black (75 pixels) and opposite-hand RGB
(157 pixels), with no acceptance change. All other masks remain identical,
including all-black. Original R/Y/black retains 17/17 acceptance in every warp;
second R/Y/black still rejects every variant. Neither new detection nor black
contrast recovery is claimed.

Original gray nominal groups still fail: their first click lies in a bright
cavity touching **two** observed regions, so the conservative rule abstains.
Clicks 1 and 3 now acquire their surrounding labels. The pre-existing common
shift (-3,0), for example, becomes accepted with 37/37, 34/34 and 38/38 correct
model region/color/indices across identity/translation/smooth; all four seed
bodies are correct and there are no false model outputs. This is the fixed
jitter test, not a suggestion to relocate the nominal click after scoring.

Second-gray `independent-4` becomes accepted with 35/35 correct model output
indices but the same wrong second seed seen in R052: source 761 instead of 767.
It supplies the one additional four-anchor seed failure. The nominal second-gray
group and the warped wrong-hand alternatives are unchanged. Conditional model
output can be correct despite incorrect seed identification.

Background and duplicate controls reject in all 32 group/condition combinations
each, before and after repair. Phase exclusion retains alternatives in 10/32
with both methods; that unresolved rejection failure remains. Deleting the first
clicked region is applicable in 13/16 conditions; none of its removed pixels is
restored and the seed stays unassigned. In the three original-gray conditions,
the first nominal click was already unassigned, so deletion is inapplicable.
The schematic dark/saturated, shared-cavity, open/diagonal-exit and empty-image
controls also pass. No threshold, click, geometry or fit was tuned after scoring.

## Reproduce and checks

```sh
.venv/bin/python photo2/highlight_region_audit.py --output photo2/output/highlight-regions-new
.venv/bin/python -m unittest discover -s photo2 -p 'test_*.py' -v
```

`--previous` selects the R052 result directory (default
`output/region-anchors-r052-final`). If absent, reproduce REGION_ANCHORS.md and
its prerequisites first. The runner verifies that report's 10 sources/80
artifacts, all five bound input reports and their source/artifact manifests,
including the historical-source-aware baseline verifier. Input reports retain
absolute local paths; prerequisites must be present at their recorded locations.
No new model fitting or rendering is needed. Existing candidate masks, fit
scores and model colors remain unchanged, so whole-patch index changes can only
come from the gate/seed, not better contour fitting.

The final report binds 13 sources, package versions, fixed parameters, inputs,
commands and 80 artifacts. Predictions include the missing-region ablation
before truth loading. Evaluations retain all unknown colors, misses, competing
hands, seed failures and added-pixel ownership. After the first run, reporting
added ownership diagnostics and moved the already image-only deletion control
ahead of truth loading; all original metrics, gates and control results are
identical. Nine focused tests include independent foreground/merge/split metric
checks. All **78 tests pass**, as do compilation, dependency consistency and
whitespace checks. Two final runs reproduce **all 80 artifacts byte for byte**;
reports agree except command output path. All 13 current sources and bound
inputs verify. Small renderer tests ran; unchanged POV sources need no full
legacy regression. The 16 panels were reviewed in a contact sheet, original and
second gray panels at full size, and final R/Y/black failure/black panels at full
size. Generated output and environments stay ignored.

Final report: `output/highlight-regions-r055-final/report.json`, SHA-256
`00cb9976af8fce21d82d1407fe872e0b985e6bc13d7c2523e75eeb9e401b4054`.

## Follow-up completed in R057

[SHARED_HIGHLIGHTS.md](SHARED_HIGHLIGHTS.md) records the comparison below. Both
extensions improve acceptance but introduce wrong ownership and weaken phase
rejection; conservative R055 repair remains the baseline. See that note for the
current next task.

## Original next task

Compare fixed distance-based and image-gradient-based assignment of enclosed
bright cavities touching multiple observed regions. Preserve every already
assigned pixel and region identity, retain abstention on ties, and compare with
R055's conservative abstention on these two patches. Keep the same fits, both
hands, fixed clicks/jitter and black/shadow/missing-region controls; measure
added-pixel ownership as well as region/anchor/index outcomes. Stop after local
comparison and checks, before whole-ring growth or photo fitting. Recommend
gpt-6-astra / High with a fresh `/new` for that distinct step.
