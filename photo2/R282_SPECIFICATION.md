# R282 specification — integrated three-phase reconstruction

This document records the complete requirements of the user's next integrated
task before implementation. Work in `rharriszzz/beads`, branch
`photo-2-strategy-v3`, under `photo2`. R282 supersedes earlier prohibitions on
global physical fitting, indexing and pattern analysis for this bounded task.
It does not authorize manufacturing certainty or silently changing old evidence.

## Objective and order of work

Build and test an actual, usable three-phase pipeline for `beads-photo-2.jpg`:

1. **Phase 1:** reliable bead identification from the photograph alone.
2. **Phase 2:** fit a physical bead model to reliable photographic beads, then
   determine visibility and image-derived color evidence for every model bead.
3. **Phase 3:** determine repeating-pattern candidates from the Phase 2 inventory.

Keep the phases conceptually distinct. Implement and exercise all three before
iterative problem-solving aimed at making the answer look good. A phase can
produce qualified alternatives or fail a scientific acceptance gate while still
being a working, tested implementation. Do not substitute more local diagnostics
for the integrated pipeline. Report strengths and weaknesses, especially Phase 1.

Maintain [a requirement checklist](R282_CHECKLIST.md) linking every requirement
to its implementation, tests, results and review evidence. Update it during work;
distinguish implemented/tested from scientifically established.

## Priorities and exclusions

- Prioritize real-photo Phase 1 quality, real-photo centerline coverage, compact
  believable supports, black beads, and a useful inventory with importance,
  reliability, visibility, origin phase, color confidence and identity confidence.
- Start with easy, central, substantially visible, reasonably illuminated beads,
  including beads crossing or near the centerline. Do not start with necklace
  edges, deep shadows, tiny fragments, marginal slivers or ambiguous reflections.
- Do not ignore difficult issues: retain their records, unresolved status and
  reasons while prioritizing easy central observations.
- Synthetic absent-bead worlds are not the real task and must not dominate this
  round. Wrong-neighbor/identity synthetic work is justified only if a comparable
  real-photo failure is observed. Use small synthetic checks only when they test
  something relevant to the photographed pipeline or its mathematical contracts.
- Do not ask the user to label beads manually. Make routine technical choices.
- Preserve prior reports, measurements, supports, controls and uncertainty.

## Shared per-bead record and provenance

Use one schema capable of representing a photographic observation, a conditional
physical bead and a later pattern inference. Each record contains at least:

| Field | Requirement |
|---|---|
| `record_id` | Stable identifier; observation IDs are not physical/string indices. |
| `phase_origin` | `phase1`, `phase2`, `phase3`, or an explicit combination when later evidence strengthens a record. |
| `importance` | High/medium/low or an explained numeric score. All Phase 1 beads matter. |
| `phase1_reliability` | Explicit reliability of independent photographic evidence. |
| `phase2_identity_reliability` | Reliability of correspondence to a physical bead. |
| `visibility` | 0 for invisible model beads; clarify measured versus predicted visibility. |
| `color` | Red, yellow, black or unknown. |
| `color_reliability` | Reliability of that color interpretation. |
| `measured_photo_location` | Photographic centroid when available; nullable otherwise. |
| `measured_support` | Native pixel mask, runs, region or explicit support summary; nullable without observation. |
| `physical_model_index` | Conditional model bead index after assignment; nullable before. |
| `physical_model_confidence` | Reliability of the physical model/assignment, with reasons. |
| `notes` | Uncertainty, rejection reasons, limitations and provenance. |

Also retain physical-identity reliability (with a clearly defined relation to
`phase2_identity_reliability`), source-observation links, model-hypothesis IDs,
predicted physical centers, visible-support centroids, evidence paths, and an
append-only phase history where needed. Keep independent photographic evidence,
geometry-assisted detection and pattern-consistency inference easy to distinguish.
Never retroactively call Phase 2/3 evidence a Phase 1 detection. Never overwrite a
measured color with a pattern guess or identify a model center as a measured point.

## Phase 1 — reliable photographic bead identification

### Goal and independence

Identify pretty many beads reliably, aiming to include all beads crossing or near
the centerline. The intended standard is extremely high reliability for almost
all Phase 1 observations. Do not claim completeness without evidence. Physical
geometry, total-count assumptions, string indexing and repeating patterns must
not create or certify Phase 1 detections. An image-derived centerline is permitted
for coverage accounting; distinguish it from a fitted physical model.

### Required support repairs

**Problem A:** recent yellow/orange boundaries wandered, with a green support
nearly splitting into two pieces and a bad lower-right region. Explicitly address
that behavior, not merely redraw a smooth outline around an unchanged bad mask.

**Problem B:** black beads require appropriate dark-object evidence. A broad
yellow model boundary around a poorly defined region is not an acceptable black
measurement. Black beads must not be treated as yellow beads with darker pixels.

Select a small set of representative real-photo cases: at least a yellow bead
with the reported bad/wandering support, a black bead, and preferably a red bead.
Show several alternative repairs for each, e.g. A/B/C, retaining failures.
For every case/attempt provide:

- Raw context crop and enlarged original.
- Exact support mask/measured interior and measured centroid.
- Before/after comparison, easy to compare on the real photograph.
- Short explanation of what improved or worsened and the preferred attempt.

Black logic may differ. Consider dark-body coherence, silhouette/enclosure,
reflection ownership only as supporting evidence, compactness, connectedness,
local shape consistency and dark-object visible-surface evidence. A highlight
must not define the entire bead. Prevent wandering into neighbors/background.
Compact reliable interiors are acceptable; do not invent full bead boundaries.

### Inventory and tests

Deliver a revised photographic inventory containing reliable locations,
supports/support summaries, centerline/near-centerline coverage, unresolved
candidates and rejected candidates with reasons. Give Phase 1 reliability for
every observation and explicit counts of high, medium and unresolved observations;
report rejected candidates separately. Reliability categories are not measured
accuracy without independent truth. No count optimization or manual coordinate
selection in runtime inference.

Phase 1 tests have highest priority. Show the representative real-photo repairs,
before/after support quality, coverage and gaps, black handling, and reliability
summaries. Preserve the user-reported troublesome case as review evidence rather
than a hardcoded runtime identity or acceptance rule.

## Phase 2 — fit a physical model to reliable photographic anchors

Fit the model to reliable Phase 1 observations, not the observations to the model.
Estimate total bead count, helicity, visibility of every bead, probable color and
color/identity reliability. Retain competing count/hand/pose alternatives if
evidence is weak. Do not pretend uncertain or hidden beads are solved.

### Fit and physical checks

- Use reliable Phase 1 anchors; separately retain measured photo centroid,
  predicted visible-support centroid, and predicted physical center.
- Compare total-count/helicity combinations. Report fit quality, anchor
  consistency, coverage, competing alternatives and identifiability limits.
- Respect source bead geometry and the planar necklace centerline. Physical
  dimensions and pose assumptions must be explicit; do not silently accept
  interpenetration or claim a unique count from a score alone.
- For visible beads with usable highlights, check that the reflection lies on
  the expected side under the model/shared lighting. This is a consistency check,
  not the sole identity evidence. Use Python and POV-Ray for analysis/appearance.

### Image-derived colors and visibility

For each predicted bead, determine visible pixels after occlusion. Estimate color
from the actual image at/near its visible-pixel centroid and other trustworthy
interior pixels (HSV or similar). Do not read the pattern to assign color. Never
sample the projected physical center as though it were necessarily visible.

Every physical bead gets visibility, color reliability and physical identity
reliability. Invisible -> visibility0; poorly illuminated -> low reliability;
visible black without a usable reflection -> low reliability; clean supported
red/yellow -> higher reliability. Unknown remains a valid color. Model-only
visibility/identity must remain conditional on the candidate model.

### Deliverable and tests

Export a full per-model bead inventory, including model index, predicted
visibility, image-derived or explicitly inferred color, color reliability,
identity reliability and Phase 1 links. Show competing fits, anchor consistency,
visible supports/color extraction, reliability tables, good agreement and uncertain
examples. Linkage must not duplicate a photographic observation across multiple
beads within a model without explicit ambiguity.

## Phase 3 — weighted repeating-pattern inference

Implement the pattern search after Phases 1/2 produce usable schema-compliant
inventories. Low-confidence geometry must propagate into the pattern confidence;
executing the search does not imply an accepted physical reconstruction.

### Supplied global constraint

There are **more than three complete repeats** and **no partial appearances**.
For a closed model with N beads and a candidate period L, require integer
`N % L == 0` and `N // L >= 4`. Use this as a strong consistency rule. Preserve
the earlier supplied fact that the photo-2 repeat length is not divisible by13,
if used, as a separately stated maker constraint rather than inferred evidence.
Do not confuse total count with period. Preserve rotational/reversal ambiguity
and unknown slots where photographic evidence does not resolve them.

### Evidence and alternatives

Use Phase 2 visibility, colors, color reliability and identity reliability to
weight evidence. Preserve leading period/sequence alternatives, disagreements,
weakly supported positions and why weaker candidates fail. Do not force a unique
exact pattern. Test sensitivity to uncertain beads (e.g. strict-only versus all
weighted evidence), including dependence on count/hand alternatives.

Never feed Phase 3 guesses back into Phase 1/2 measurements. Pattern inferences
have Phase 3 provenance and separate confidence. Invisible positions may receive
a conditional inferred color only in the Phase 3 result, never a photographic
measurement or a retroactive Phase 2 measured color.

### Deliverable and tests

Provide candidate patterns, weighted evidence, conflict witnesses, explanations
for weaker alternatives, sensitivity results, and an explicit repeat-rule check.
Show sequence/pattern views with uncertain positions highlighted. Tests must
exercise the complete-repeat constraint, weighted evidence and uncertainty.

## Real-photo review package

Provide compact static outputs that already show the important issues, optionally
with an interactive browser review:

1. Phase 1 raw/enlarged crops, several alternatives, masks and centroids, preferred
   attempt/reasons, geographic/centerline coverage and unresolved gaps.
2. Phase 2 reliable anchors, fitted model overlays, visible beads, color/reliability
   examples, competing count/hand fits and good/uncertain correspondence.
3. Phase 3 sequence/pattern alternatives with uncertain positions highlighted.

Keep photos separate from predicted surfaces. Display smoothing must not alter
measured masks. Preserve failed attempts and alternatives visibly, not just a
best-looking final illustration. Real-photo failure inspection takes priority
over synthetic edge-case optimization.

## Implementation approach recorded before coding

Phase 1 will compare three photograph-only families: A native seed-connected
appearance support, B compact connected interior cores, C boundary/neck-constrained
connected support. Black variants use reflection-plus-dark-body/enclosure evidence
separately from colored pigment. Prefer a uniform criterion for the whole image;
case-specific figures are review-only. Existing image-only inventories may provide
preserved baseline candidates, but geometry-assisted records cannot be promoted.

Phase 2 will compare (A) shared rigid/global pose, (B) planar image-centerline
registration with constrained source placement, and (C) bounded smooth corrections
if justified by the integrated first pass. Retain equal-budget count/hand choices,
physical validity and held-out anchor checks. Start with A/B; no fit-until-success.

Phase 3 will compare (A) strict reliable-only consensus, (B) weighted consensus,
and (C) uncertainty sensitivity/held-out consistency across divisor periods.
Choose by documented evidence/complexity and leave unresolved positions unknown.

First milestone: one working end-to-end invocation producing all three inventories,
tests and preliminary review. Only then refine identified Phase 1 failures within
this task, preserving the first pass and rerunning dependent phases explicitly.

## Delivery and stopping point

Deliver the implemented three-phase plan, revised Phase 1 inventory, Phase 2 fitted
inventories, Phase 3 pattern candidates, tests for all phases, a picture review
package, and a report saying what works, what remains weak and the next bounded
task. Update the checklist with concrete code/test/result links and honest
limitations. Preserve hashes, parameters, seeds and reproduction commands.
Update plan, append-only request log, handoff, methods and applicable instructions.
Commit/push scoped R282 work to `photo-2-strategy-v3`, verify the remote tip and
working-tree status, then stop. Keep current model/reasoning; no `/new` required.
