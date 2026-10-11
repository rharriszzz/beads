# R239 — bounded Stage 1 body ownership

R252 now [consolidates these overlapping observations and audits trusted coverage](COLORED_OBSERVATION_CONSOLIDATION.md). Historical evidence and original statuses below remain unchanged.

**The filter removes all confirmed errors in this six-section audit, but loses
18 previously covered bodies and retains nine unresolved proposals.** It is a
useful conservative observation subset, not a completed automatic identity map.
**There is enough reliable local evidence to begin a small Stage 2 correspondence
experiment; further global segmentation work is not a prerequisite.** No Stage 2
fit, indexing, helicity inference or repeating-pattern recovery was performed.

User-authorized scope: one ownership experiment, accuracy before recall, explicit
abstention, fresh transfer, comparison with unchanged [R238](STAGE1_RECOVERY.md),
records/commit/push and a recommendation. Started at `7359bbd` on
`photo-2-strategy-v3`; clean daisy checkout, no stashes, fetched origin agreed.
The user reports **GPT-6 Astra / High** and will report changes.

## Evidence to inspect

The [black-reflection cards](review/r239/black-evidence.png) show paper rim versus
true reflection, a highlight belonging to yellow, a lost true black reflection,
and an accepted but unresolved weak feature. The
[colored-ownership cards](review/r239/color-evidence.png) show two successful
duplicate removals and two harmful same-color merges. Each has untouched raw RGB
beside measured evidence. [Exact measurements](review/r239/measurement-cards.json)
include native coordinates, sampling paths and decisions.

| Section | Raw / R238 / R239 comparison | Raw-only inventory |
| --- | --- | --- |
| D3, familiar | [Comparison](review/r239/D3-comparison.png) | [Existing reference](review/r235/D3-numbered.png) |
| D4, familiar | [Comparison](review/r239/D4-comparison.png) | [Existing reference](review/r235/D4-numbered.png) |
| H1, familiar | [Comparison](review/r239/H1-comparison.png) | [Existing reference](review/r235/H1-numbered.png) |
| H4, familiar | [Comparison](review/r239/H4-comparison.png) | [Existing reference](review/r235/H4-numbered.png) |
| T1, fresh transfer | [Comparison](review/r239/T1-comparison.png) | [Raw](review/r239/T1-raw.png), [numbered](review/r239/T1-references.png) |
| T2, fresh transfer | [Comparison](review/r239/T2-comparison.png) | [Raw](review/r239/T2-raw.png), [numbered](review/r239/T2-references.png) |

Green means retained, red means abstained; it does not mean visually correct or
incorrect. White rectangles bound the scored sections. Cyan boundaries on cards
are provisional **image-support boundaries, not physical bead outlines**. Black
cards show rays: green reaches dark support first, orange reaches colored support,
red lacks either qualifying run. Points remain observed colored samples or
specular features, never inferred physical centers or measured visible centroids.
B IDs are reference observations, P/A IDs proposals, neither string indices.

## Design, selection and isolation

Four approaches were considered before implementation: (1) angular dark enclosure
around reflections; (2) colored shape lobes independent of brightness maxima;
(3) pairwise neck/seam evidence; (4) projected bead templates. Selected 1–3 as one
conservative post-filter of **already accepted R238 proposals**. Templates belong
in the proposed next geometric experiment. This filter cannot recover bodies
whose candidates R238 already discarded, including H4-B27's suppressed reflection.

The [protocol](review/r239/protocol.json) fixes T1 `[1990,740,2150,890]` and T2
`[2180,2070,2340,2220]`, with 30px halos, before code/tuning. They are smaller
sections within R233's proposed H2/H3, unused by R235/R238 detector development or
transfer. Historical overview inspection and full-photo appearance estimation
mean they are **fresh local transfer sections, not wholly unseen images**.
D3/D4/H1/H4 all count as development here; H1/H4 have no independence claim.

Raw-only [references](review/r239/references.json) were
[frozen](review/r239/reference-freeze.json) before ownership implementation or
transfer detector overlays: 22 eligible bodies per fresh section, three uncertain
references and one deferred no-obvious-reflection black body. References are
provisional agent photographic judgments, not independent maker truth. No fresh
reference was subsequently added/deleted. The unchanged approximately 10% colored
visibility guideline and obvious-reflection plus dark-body black requirement apply.
Width/height area brackets follow R235's heuristic, not exact segmented areas.

Two development versions were run. Shape-only necks retained just 57/109 correct
bodies because merged color supports were much too large. Adding local diffuse
brightness seam cuts before shape analysis retained 96/109. Both versions and
rules survive in [history](review/r239/development-history.json),
[v1 results](review/r239/development-v1.json), and the hash-matching
[v1 source](review/r239/development-v1-source.txt). The selected
[detector/input/rule freeze](review/r239/freeze.json) precedes transfer execution.
No transfer-driven detector tuning occurred. Later runs only verify reproduction.

## Ownership method and measurement paths

Input: original native RGB, R238's full-photo learned hue modes/scale, unchanged
R238 accepted proposals and fixed crop halos. No body IDs, manual color boxes,
reference coordinates or geometric slots enter the detector. Learned diameter is
27.19px. Color semantics name the learned modes; paper is not defined as magenta.
Final generality across palettes/backgrounds/placements is **not established**.

1. **Colored supports and seams.** Starting from R238's learned family masks,
   normalize sigma-1px value smoothing within each mask. Cut pixels below 0.68 of
   the local diffuse maximum in a 0.85-diameter window. Close by one pixel and fill
   holes, then watershed the distance-to-support-edge field using shape maxima
   of prominence 0.04 diameter. These are shape lobes after photometric seam cuts,
   not one brightness maximum per assumed bead.
2. **Colored ownership.** Associate an existing sample with its lobe (or nearest
   support within 0.14 diameter for a highlight hole). Require area between
   0.10 and 1.65 diameter² and maximum inset between 0.13 and 0.55 diameter.
   These are certification heuristics, **not the eligibility/10% area rule**.
   Keep one sample per lobe, preferring an existing baseline sample, then stable
   source ID; retain the other proposal as an explicit abstention. For different
   same-color lobes within 0.95 diameter, sample 31 points over the interior
   15–85% of their connecting segment. Require minimum depth divided by the
   smaller lobe's maximum depth ≤0.60; otherwise abstain on both. A narrow neck
   supports separation; shared support still does not prove physical identity.
3. **Black feature ownership.** Start at the unchanged R238 reflection coordinate;
   do not recenter it as a bead center. Sample 24 radii from 0.09 to 0.48 diameter
   along 16 evenly spaced rays. A qualifying run has three samples darker than
   both V=0.40 and 0.82×peak V, without colored support. Count dark runs that occur
   before colored runs. Require at least 12 dark rays and at most four rays
   reaching color first. This angular enclosure rejects features supported only
   by a neighboring dark quadrant; competing color rejects colored-bead glints.
4. **Multiple black features.** For two accepted reflections within 0.70 diameter,
   require a separating colored run on their interior connecting segment;
   otherwise abstain on both. Distance merely selects a pair for an ownership
   test; it never certifies sameness or selects the brighter maximum. This is
   deliberately conservative and fails on some real adjacent black faces.

Each proposal preserves all input fields, evidence, retain/abstain reason and any
competing candidate. No manual audit decision changes the automatic output.
The [complete audit](review/r239/candidate-audit.md) includes every proposal,
including halo context. The detector is [stage1_ownership.py](stage1_ownership.py);
scoring and figures are separate modules.

## Measured results

Counts are conditional on the frozen provisional photographic references. The
original four-section denominator and all R235/R238 boundary credits remain.
Fresh T2-P03 is explicitly credited to border-crossing T2-B01; T1-P12 remains
unresolved despite its halo coordinate. T2-P14 is an unresolved new rear-face
proposal, not an unannounced denominator addition. No in-box proposal is excluded
as context. [Transfer adjudications](review/r239/transfer-adjudication.json).

| Sections / method | Body coverage | False positives | Duplicates | Wrong colors | Accepted unresolved |
| --- | ---: | ---: | ---: | ---: | ---: |
| Familiar, R238 | 103/109 | 9 | 3 | 1 | 14 |
| Familiar, R239 | **96/109** | **0** | **0** | **0** | **7** |
| Fresh, R238 | 41/44 | 0 | 3 | 0 | 3 |
| Fresh, R239 | **30/44** | **0** | **0** | **0** | **2** |

R239 abstains on 27 scored familiar proposals and 15 scored fresh proposals.
These abstentions are separate from accepted unresolved proposals and reference
uncertainty. Original 13 uncertain references/six deferred black hypotheses and
fresh three uncertain/one deferred remain unchanged. All 18 lost bodies remain
eligible misses. Totals must not be interpreted as precision=100%: nine accepted
proposals still lack resolved ownership. Fresh sections have no confirmed R238
false positives, so they **do not independently establish paper-rim rejection**;
they test duplicate removal and expose the coverage cost.

| Section | R238 → R239 body coverage | Lost correct bodies |
| --- | --- | --- |
| D3 | 22 → 22 / 22 | None |
| D4 | 29 → 24 / 32 | B07, B26, B27, B29, B30 |
| H1 | 26 → 26 / 27 | None |
| H4 | 26 → 24 / 28 | B13, B16 |
| T1 | 20 → 17 / 22 | B07, B12, B17 |
| T2 | 21 → 13 / 22 | B02, B06, B09, B12, B13, B16, B19, B24 |

[Every lost observation, prior proposal and reason](review/r239/lost-correct.md).
Of the original R235 76 correct detections, 74 remain covered; D4-B27 and H4-B16
are lost. Of R238's 27 successful additions, 22 remain. No new body is recovered.
Full [summary](review/r239/summary.json) and [both reports](review/r239/report.json)
preserve color breakdowns, misses and proposal-level accounting.

**What worked:** enclosure distinguishes familiar H1-A04's paper rim (8 dark
rays) from H1-A07's reflection (16). H4-A13 reaches yellow before dark on 10 rays,
so the wrong black label is withheld. Shape lobes remove all three old duplicates
and all three fresh duplicates; T1-A08 and P15 correctly share a red face.

**What failed:** a true T1-B07 reflection has only 10 dark rays, so it is lost.
T2-A15 has 15 dark rays yet only a weak diffuse feature: dark enclosure does not
make the reflection obvious. Several merged yellow regions survive seam cutting;
T2-A06 is incorrectly grouped with halo A01 on a different bead. D4-B27/B30 are
both withheld when their merged lobe slightly exceeds the area limit. Close black
pairs cause the loss of H4-B13/B16. Threshold choices affect these decisions;
there was no sweep after transfer. Pixel geometry alone has not resolved ownership.

Retained unresolved: D4-P03/A11/A12, H1-P02, H4-P01/P03/A16, T1-P12 and T2-A15.
Keep these out of any *reviewed* geometry seed subset, explicitly labeling that
subset as assisted selection rather than claiming a fully automatic clean map.

## Stage 2 readiness and stopping point

**Yes—start a small, separately authorized geometric-correspondence experiment.**
D3 retains all 22 eligible bodies, with zero confirmed errors and zero accepted
unresolved proposals (its uncertain reference regions still exist). The already
identified **D3-B09–B14, B18, B19, B21** core provides nine distinct observations:
five yellow, three black, one red, spanning neighboring rows. All nine survive
R239. This is enough to test correspondence hypotheses, not to guarantee a unique
answer or generalize around the necklace.

The concrete next task is to use the existing `beads.pov`-consistent forward
geometry and planar centerline on that 5–12-body-scale patch, compare both
helicities and alternative local correspondences, and reserve other clear D3
bodies for predictions not used in fitting. First check the observation-to-surface
likelihood on known synthetic examples. Colored samples constrain visible-surface
membership; black reflections need lighting-aware treatment or uncertainty, not
exact projected-center residuals. Predicted slots are hypotheses, never detections.
If ambiguity survives, identify differing assignments and test a second section
orientation; do not force a unique helicity or globally compress missing indices.
No repeating-pattern search or full-necklace indexing belongs in that first test.

Recommendation: stop further broad segmentation tuning for now. Geometry can test
whether apparently merged regions have plausible separate visible owners, while
Stage 1 evidence can reject geometric hallucinations. This experiment has reached
its authorized stop; **Stage 2 was not started**. Retain the user-reported
**GPT-6 Astra / High** for that work; recommend `/new` before its implementation,
using this report and the handoff. The user controls switching and authorization.

## Reproduction and verification

Python 3.12.14. All **17 tests pass**: 12 existing plus five new enclosure,
translation/rotation, one-body/two-maxima versus two-body/seam, ambiguous-black-pair,
and frozen-output/accounting checks. These owner-known synthetic controls are
simple arrays, not POV-Ray appearance validation or proof of photo generality.
The source photo SHA-256 remains
`eb7c9edb62f5580ef56632872da48da92556d62b758295137068cc2404dc8fbb`.
The archived [transfer inputs](review/r239/transfer-inputs.json) include hashes of
all source pools; reproduction does not need ignored historical caches.

```bash
.venv/bin/python -m unittest photo2.test_stage1_pilot photo2.test_stage1_recovery photo2.test_stage1_ownership
.venv/bin/python -m photo2.stage1_ownership development --output photo2/output/r239/reproduce-development
.venv/bin/python -m photo2.stage1_ownership transfer --output photo2/output/r239/reproduce-transfer
.venv/bin/python -m photo2.evaluate_stage1_ownership score --output photo2/output/r239/reproduce-review
.venv/bin/python -m photo2.evaluate_stage1_ownership render --output photo2/output/r239/reproduce-review
.venv/bin/python -m photo2.illustrate_stage1_ownership --output photo2/output/r239/reproduce-review
```

`prepare` is archival input construction and requires the old ignored caches; do
not overwrite frozen inputs. [Verification](review/r239/verification.json) records
byte-identical reproduction, unchanged historical artifacts and source seals.
No production detector, original photo, existing reference or geometry changed.
