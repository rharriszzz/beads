# Observed-region anchor robustness — R052

Follow-up R055 is complete in [HIGHLIGHT_REGIONS.md](HIGHLIGHT_REGIONS.md):
conservative highlight filling improves jitter tolerance without improving
detection counts or resolving helicity. The original protocol/results below
remain unchanged; the follow-up note defines the current next task.

## Frozen protocol (before scoring)

The maker confirms equal bead size/shape across colors, small gloss differences,
lengthwise hole axes, invisible holes and invisible white thread. The assistant
marks its own anchors from beauty images. No visible hole/thread cues are used.
Known legacy camera, rope geometry and scale remain supplied calibration.

Compare R047's unchanged eight-pixel click margin with this region rule:
clicks select independent gray-boundary watershed regions; each must have
at least 100 pixels, avoid the 12-pixel crop border, and match one predicted
bead at IoU >0.5. Require distinct regions and distinct supported predicted
beads. Their signed 1/6/7 neighbor graph must connect the three/four anchors
and contain at least two direction families. All three remain preferable,
not mandatory. Require the existing 60% contour-support fraction at 2.5 pixels.
No nearest-region snapping, click relocation or truth-corrected anchors.
Keep eligible candidates within the existing 0.5-pixel training-score tie.
The old gate keeps its original all-three-family requirement for comparison.

Development patch: unchanged R047 box (1900,650,2310,1060), clicks, four source
views and identity/translation/smooth warps. Reuse verified smooth fits and
actual-image segmentation outputs from R047; do not refit them for this rule.
Exclude the two grayscale-edge ablations. That supplies 12 conditions.

Second patch, chosen from beauty pixels before any scoring: (80,650,490,1060)
on the opposite side of the same ring. Positive-hand clicks in full-image
coordinates: (165,810), (220,835), (220,775), (280,810). Negative-hand clicks:
(170,770), (225,800), (225,740), (280,775). Transfer positive-hand clicks to
gray/black controls, explicitly supplying locations even when not discernible.
Use the same four appearances/hands, identity only. Reuse full independently
rendered candidate templates and the existing whole-image segmentation.
Fit eight smooth candidates per view with the unchanged R047 algorithm.
This is spatial transfer in the same scenes, not an independent rendered scene.

For each of 16 conditions test four anchors and the first three anchors.
Each group has 17 variants: nominal; common shifts of ±3 and ±6 pixels along
x and y; eight independent integer jitters in [-6,6] using RNG seed 5201.
Apply jitter after the known synthetic image warp. Neither gate refits contours
for a jitter variant. Score index origin against the nominal first anchor,
so moving to another bead cannot silently redefine success. Record which
observed regions and candidate bodies each jitter selects.

Controls for every condition/group: replace first click with corner background
(20,20), duplicate second click as first, and exclude phase-zero candidates.
Preserve all candidates, both hands, unknown colors, missing indices, failed
seed matches and optimization statuses. Report acceptance and index stability
separately; an accepted gate is not proof of correct helicity. Truth enters
evaluation after all predictions for the condition have been saved.

Stop after local seed/region/index evidence and checks, before whole-ring
growth, automatic geometry estimation, photo fitting or repeat recovery.

## Results and interpretation

The region rule removes the arbitrary margin failure in the original R/Y/black
patch, but **does not establish reliable seed selection or helicity**. Sixteen
conditions × two group sizes × 17 nominal/jitter variants give 544 positive
anchor trials. Another 96 trials are the three controls for each condition/group.
These share four rendered source images and two spatial patches, not 544
independent scenes. The old 96 smooth fits are reused; 32 new smooth fits are
computed. No model-fit, segmentation, click or gate settings changed after scoring.

| Group | Old gate accepted /272 | Region gate accepted /272 | Old accepted with a wrong matched index | Region accepted with a wrong matched index |
| --- | ---: | ---: | ---: | ---: |
| Three beads | 70 | 123 | 26 | 36 |
| Four beads | 59 | 100 | 19 | 36 |

An accepted trial counts once even if it retains multiple candidates; a trial
has a wrong index if **any** retained candidate misindexes a matched bead.
Thus greater acceptance is not automatically better recovery. False regions
are separately retained and are not included in these matched-index counts.
For four anchors, all retained hypotheses map all four intended anchor bodies
correctly in 85/100 region-gate acceptances versus 45/59 old-gate acceptances.
For three anchors the corresponding figures are 118/123 versus 52/70.
Correct anchor *bodies* still do not imply correct signed index differences.

Selected nominal four-anchor results (all alternatives remain in JSON):

| Condition | No-model matched / eligible | Region-gate result |
| --- | ---: | --- |
| Original R/Y/black, identity | 27/37 | 34/37 correct region/color/indices; no false regions |
| Original R/Y/black, translation | 25/34 | 32/34 correct region/color/indices; no false regions |
| Original R/Y/black, smooth warp | 26/38 | Correct hand: 34/38 correct region/color/indices, one false region; two wrong-hand alternatives also retained |
| Second gray patch | 30/35 | 35/35 correct region/color/indices, no false regions, but one intended anchor is misidentified |
| Second R/Y/black patch | 13/35 | No retained hypothesis |
| All-black, both patches/all tested warps | 0 matched | No retained hypothesis |

The original R/Y/black group is accepted for **17/17** four-anchor variants in
each of identity, translation and smooth warp, versus **6/17, 8/17, 10/17** for
the old rule. Identity/translation preserve the correct hand and seed origin
throughout. In the smooth condition, both wrong-hand alternatives survive at
nominal clicks: 25 and 27 matched bodies have only six correct indices each,
with 19 and 21 wrong matched indices and seven false regions apiece. All four
anchor *bodies* match correctly for these candidates. Both wrong hands and the
correct hand span all three families, so restoring the all-three-family rule
would not fix this example. The same anchor edges receive different 1/6/7 signs
and families under the competing templates. Do not silently select by truth.

The original opposite-hand RGB smooth case likewise retains the true hand
(35/37 correct indices, one false region) and a wrong-hand phase-.75 alternative
(26 matches, only five correct indices, nine false regions). Both map the
four intended anchor bodies correctly. The new RGB patch's nominal group
rejects, while three jitter variants accept wrong-index alternatives.

The gray results reveal a different problem. Original gray nominal clicks
0/1/3 fall in pixels the foreground detector leaves unassigned; jitter can
move them into regions. The nominal second-gray group accepts but its second
click selects source bead **761 instead of 767**. All 35 output indices are
nevertheless correct because the first anchor/origin is correct and the fitted
template is well aligned. This is not four correct anchor identifications.
Four-anchor acceptance there is 11/17 versus old 2/17. The three-anchor group
accepts only 5/17: the misidentified second bead needs the fourth to connect.
The second R/Y/black patch has poor independent region matches (nominal true-
candidate IoUs .369, .174, .850, .422). It rejects all 17 variants with either
group size. These saved visual clicks were not repaired after truth inspection.

Background and duplicate-click controls reject for both rules in all 32
condition/group combinations each. Excluding phase zero retains alternatives
in **10/32** region-gate controls (six three-anchor, four four-anchor), versus
2/32 old-gate controls. Many have wrong indices; some preserve matched indices
but add false regions. This is a failure to reject an inadequate template bank,
not proof that every phase exclusion must change every relative index.
All-black remains a failed detection/fitting control; supplied anchor locations
do not create missing image evidence. Legacy pure Black is not fitted photo black.

This compares two complete gates: observed-region matching, seed contour support
and at least two families versus the original margin/all-three-family gate.
It is not a factorial experiment isolating each changed requirement. Whole-
patch fitted outputs still use R047's contour support, not full observed-region
matching. Known camera/rope/scale and visually supplied seeds remain assistance.
No new photo, geometry, gloss, thread or hole fitting is claimed.

## Reproduce and checks

```sh
.venv/bin/python photo2/region_anchor_audit.py --output photo2/output/region-anchors-new
.venv/bin/python -m unittest discover -s photo2 -p 'test_*.py' -v
```

The runner verifies R047's `local-patch-r047-verified` predictions/masks, its
`local-patch-templates-r047-final` full renders, R045's fixture/detection reports
and the neighbor baseline. If absent, follow LOCAL_PATCH.md's prerequisites
and reproduce those runs first; `--previous`, `--templates`, `--fixtures`,
`--detection`, `--baseline` accept their recreated locations. Outputs must be
new or empty. No new candidate renders are needed when those verified inputs
exist. Every condition saves beauty input, observed/predicted masks, all
prediction gates before truth evaluation, evaluator details and a context panel.
The report binds commands, parameters, clicks/jitters, sources and input hashes.

After initial scoring, reporting added per-anchor identity diagnostics and
corrected a panel overlap/added false-region counts. All original fit/gate/
index scores were checked unchanged. No post-score threshold or click tuning.
All **69 tests pass**, including eight new tests covering jitter, merges/splits,
unsupported/background/duplicate seeds, old-gate parity, preserved origins and
anchor slips. Compilation, dependency consistency and whitespace checks pass.
The three historical 60-evaluation optimizer stops remain recorded and none
is retained by either gate, including controls. All 32 new optimizations converge.
No failed runtime test or audit. Existing small renderer tests ran; full legacy
regression skipped because tracked POV sources are unchanged.

Two final runs reproduce **all 80 artifacts byte for byte**, with reports equal
except command output path. Both runs verify ten current sources and five bound
input reports. R047's 11 sources/70 artifacts, its six template sources/34 artifacts,
R045 fixtures and detections, and the baseline verifier pass. All 16 initial
panels were inspected in a contact sheet; selected final success, ambiguous-hand
and failed-region panels were inspected at full size. Generated artifacts and
environments remain outside Git.

Final report: `output/region-anchors-r052-final/report.json`, SHA-256
`5ed1ae8545799d2ff7beec46676b7f1bbfe52a0dda77203e9ab071a4aa933d48`.

## One next task

Diagnose and test a highlight-tolerant observed-region extraction rule on these
two frozen patches. Compare current foreground/segmentation with a fixed rule
that keeps bright surface reflections inside bead regions without merging
adjacent bodies; retain black, shadow, missing-region and click-jitter controls.
Use the unchanged candidate bank and preserve both helicities; do not tune
clicks using truth. Stop after region/anchor/index comparison and checks, before
whole-ring growth or photo fitting. Recommend gpt-6-astra / High with fresh `/new`.
