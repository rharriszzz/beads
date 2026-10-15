# R288 — understand J/M and distinguish instability from unsupported material

User-authorized isolated Phase 1 round on photo-2-strategy-v3, following R287.
Complete the J/M explanation BEFORE any new segmentation implementation. Preserve
all historical code/results/reviews and production inventory. No global physical
reconstruction, pattern search, manual neighbor labels or automatic R289.

## Permanent scientific context and reviewed evidence

Photographic brightness, color and contextual dark separations determine colored
interiors. Compactness, smoothness, thickness and area are not objectives. A narrow
bright continuation can be valid; a dark internal texture need not separate bodies;
a bright detour cannot automatically erase coherent seam evidence. Measure a
trustworthy interior and photographic centroid, not necessarily a full silhouette.

Latest decisions remain: P5 J/B good, S bad; P2 J too small, S/B equally good (B did
not improve S); C05 S/M/B acceptable but imperfect; C02 all bad and peripheral,
not worth substantial rescue effort. M=B on five original colored examples but
not elsewhere. B's internal-shading false split keeps M the preferred fuller
candidate. Earlier yellow J preferences, T rejection, edge/shadow tolerance and
all R285–287 failures survive. No reviewed answers/coordinates enter inference.

R287 lesson: unstable M does NOT certify adequate J. N07 and N11 retain visibly
undersized J despite substantial diffuse material supported by direct routes.
N06 M merges yellow neighbors while J separates them. P2 M/S 495 pixels, P5
J/repaired M and C05 acceptable imperfect support are preservation tests.

Attempt all visible centerline-crossing beads plus relevant near observations;
include both sides where the line passes between beads. Aim for two/three where
photography supports it, never a station quota. Difficult outer edges unresolved.
Use image-derived curve, support geometry, signed side and longitudinal interval,
not centroid alone. Compact interiors can understate complete-body crossings.
Black remains separate specular-reflection measurements only, R2 default with
R1/R4 alternatives; no new dark-body or reflection redesign. Physical ownership
and complete black-body crossing remain unknown.

## First deliverable: J_AND_M_EXPLAINED.md

Standalone approximately1500–2500 words or longer where clarity requires. Address
a technically sophisticated reader unfamiliar with implementation. Explain:

- Reflective packed surfaces, pigment/diffuse/specular variation, shading/seams,
  noise/blur/occlusion, connected same-color bodies and multiple maxima per body;
  distinguish photographed evidence from imposed assumptions.
- J's photo-only cue provenance, ICC/sRGB/HSV/linear luminance, learned material,
  inherited A-ring background, equations/parameters/units, local peak threshold,
  connectivity/substitution, fixed domain, contour, centroid and clipping/uncertainty.
  Explain good dark stopping and peak-driven diffuse red truncation.
- M's seed refinement, pigment/background/diffuse estimation, eligible domain,
  log-prominent maxima, context-supported marker repair, watershed mathematics,
  references/interfaces/maximum-saddle merger, final native support and uncertainty.
  Give a numerical valley versus bright-detour example; no marker=body assumption.
- Side-by-side assumptions, brightness/color/specular/diffuse, neighbors/maxima/
  valleys/shadows/same-color, seed/background/domain sensitivity, complexity and
  representable/unrepresentable uncertainty. Explain actual similarities/differences.
- Failures from R284B–287: J red peak truncation (P2/N07/N11), domain clipping,
  low-threshold mergers, inherited-background dependence; M/S missing markers P5,
  parameter instability, alternate routes, internal-shading false split (attribute
  demonstrated B failure correctly), N11 extension and selector failure. Shared bad
  cues, multiple features per body, pigment/seam/ownership ambiguity. Distinguish
  demonstrated root cause, hypothesis, segmentation, seed detection and correspondence;
  explain attempted fixes and regressions without declaring examples “solved.”
- Single-photo identifiability, justified abstention and later Phase 2 constraints
  that never manufacture Phase 1 observations. Concrete improvement experiments
  involving cues, boundaries, background, competing hypotheses, robust estimates,
  uncertainty and eventual physical interpretation. Link functions, original project
  photographs and numerical evidence; no external/stock imagery.

## Diagnosis and planned hypotheses before algorithm changes

N07: localize unstable pixels, inspect every perturbed marker/ref/reference/interface
and threshold; distinguish changed material eligibility from changed basin unions.
N11: examine upper extension with native intensity routes, competing markers and
basins; determine whether seam evidence supports removal or remains ambiguous.
N06: retain dark separation. Preserve P2/P5/C05 while changing N07/N11.

H1: parameter sensitivity may reside in a detachable extension while a substantial
interior remains stable; a whole-mask veto discards useful measurements.
H2: neighborhood-supported diffuse material can be retained without crossing a
coherent valley if construction starts from demonstrably stable native evidence.
H3: marker/basin union changes, not merely pixel thresholds, may explain abrupt
area changes. Joint marker interpretation should retain explicit alternatives.
H4: stable pixels alone can still be wrong; stability must be paired with independent
material and separation evidence. New masks cannot be naive J/M union/intersection.

Develop 2–3 mathematically distinct targeted alternatives, preserving failures:
A ensemble-stable core plus direct diffuse continuation; B fuller material with
independently supported seam/competition restrictions; optional C joint local feature
interpretations retaining uncertain unions. Exact design follows causal diagnosis,
not attractive outlines. Permit prefer J, prefer M, both alternatives, evidence-
supported new interior, or abstain. Record J inadequacy independently of M instability.

## Independent confirmation and evaluation

Freeze approximately12–20 new central regions (target16), before seeing new outputs,
using hash-ranked photo-only cues and exposure/centerline/neighbor strata. Include
red diffuse interiors, yellow seams, crossings, opposite-side and same-color groups,
uncertain ownership. Exclude prior reviewed centers and disclose feasible distances;
no difficult-edge tuning. Freeze methods and decision rules before confirmation.
No retuning after results; preserve failed frozen version if later work is proposed.

Compare original J/M, R287 selector, every new method and B diagnostic. Save native
supports, all perturbations, peak/seed/centroids, gained/lost material, profiles and
seams, marker ledger, basin/group events, uncertainty, and source hashes.
Measure diffuse retention (evidence proxy, not labeled truth), seam leakage, seed/
illumination/sigma/background/domain sensitivity, clipping, missing/redundant markers,
overlap/duplicates, centroid movement, near/crossing/flanking, abstention and new
DISTINCT recovery. Raw count is not bead count; no real precision/recall without
truth. Independent mathematical or physical controls may validate mechanisms;
physical truth, when used, is hidden from inference. Actual photos remain primary.

## Architecture, checkpoints and final review

Phase 1 independent colored interiors/black reflections; Phase 2 geometry/count/
helicity/camera/shared lighting/correspondence/visibility and measured color;
Phase 3 weighted pattern with >3 complete repeats, no partial repeat. No later-phase
inputs certify supports. Keep importance, measurement/color reliability, visibility,
physical identity confidence, discovery phase and provenance separate, unresolved
observations important. Production inventory remains unchanged.

Save six checkpoints: explanation; N07/N11 diagnosis; new design; development;
frozen independent confirmation; final evaluation/recommendation. Include code hashes,
parameters, evidence, failures, hypotheses and pending decisions. After compaction
reread this specification, explanation and latest checkpoint; do not weaken scope.

Compact original-photo review prioritizes N07/N11/N06/P2/P5/C05 and informative new
successes/failures. Each shows raw pixels, J/M/new masks, exact fills/contours,
centroid, gains/losses, brightness/seam evidence and uncertainty. Full archive stays
available. Deliver explanation, diagnoses, alternatives, controls, confirmation,
quantitative coverage/reliability limits, review, permanent contract/handoff/checklist,
reproduction/tests, failed methods and next bounded proposal. Commit/push scoped
work, verify remote and clean worktree; STOP for user review before adoption/R289.
Keep current model/reasoning; no /new needed.
