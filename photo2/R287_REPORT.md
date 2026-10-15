# R287 — can photographic evidence choose J or M?

**Sometimes, but the frozen selector is not ready for production.** Direct color
and intensity continuity identifies diffuse material that J discards, while
multi-path seams and perturbations expose several M mergers. These mechanisms
transfer to new regions of the same photograph. However, rejecting M does not establish that J is a
good enough substitute: the selector still chooses undersized red cores in N07
and N11. That failure and the resulting coverage losses prevent adoption.

Open the [visual review](review/r287/index.html). Start with
[P2 diffuse red](review/r287/P2-choice.png), [P5 stability](review/r287/P5-stability.png),
[new yellow merger N06](review/r287/N06-choice.png), and
[false fallback N07](review/r287/N07-evidence.png).
Every candidate, both policy versions, failed choice, raw crop and perturbation
is preserved. No production inventory, physical reconstruction or pattern changed.

## Latest user decisions and what they mean here

|Case|User assessment|R287 interpretation|
|---|---|---|
|P5 three yellows|J good, S bad, B good|M equals B nominally here; either J/M can be supported, but stability may distinguish them|
|P2 red centerline|J too small, S good, B equally good|M/B reproduce S; no claimed B improvement over S|
|C05 central red|S/M/B acceptable, not great; others very bad|M can be preferred without claiming its whole boundary correct|
|C02 edge region|All bad; too peripheral for substantial effort|Keep weak-edge abstention and broader context separately; no C02 rescue/tuning|

M and B were identical on the five original colored examples and differ elsewhere.
B has a demonstrated internal-shading false split; M is the fuller candidate, B
only a diagnostic control. The permanent [Phase 1 contract](PHASE1_MEASUREMENTS.md)
and [R287 specification](R287_SPECIFICATION.md) preserve these judgments. No reviewed
coordinate, user answer, physical identity or color-only preference enters selection.

## Evidence and selector design

J and M/B controls are unchanged. All 78 control masks on 26 development observations
replay exactly. J uses the historical A-ring background, local peak contrast and
radius 24 domain; M uses diffuse 60 pigment intensity, local dark baseline and
context-supported maxima with the original maximum-saddle watershed merger rule.
B adds protected interfaces. Inherited A affects J's background, but is not truth.

The selector takes their photographic evidence and returns prefer J, prefer M,
both comparably supported, or neither reliable/abstain. Both retains two original
supports with unknown ownership; it does not create their union or intersection.
No hybrid was justified. Every observation remains important and unrated, including
abstentions; measured coordinates never become physical centers.

1. **Boundary evidence:** sample brightness 2/4 native pixels inside and outside
   local contour normals; save ratios and connected bright-continuation stretches.
   Isolated dark pixels cannot certify a whole separation. These measurements are
   diagnostic, not an objective to maximize gradient or roundness.
2. **Coherent seams:** context-supported markers supply candidate feature pairs,
   not bead identities. Five parallel routes at offsets−3,−1.5, 0, 1.5, 3 pixels sample
   the sigma 0.65 linear-luminance field. Four routes must have an interior trough
   below 55% of the weaker diffuse reference, with consistent trough position and
   supported pigment around both ends. A support containing both native marker
   cores is flagged. The brightest detour does not erase this evidence.
3. **Diffuse continuation:** for M-only pigment, test three nearby direct routes
   from the nearest J material. A decreasing brightness profile is allowed. A
   deep valley followed by renewed brightness fails; pigment must persist along
   the route. At least two of three routes must pass. A preference needs at least
   50 supported added pixels, 30% of J area, and 85% of eligible added pigment
   supported. These are explicit engineering significance criteria, not calibrated
   probabilities or optimization for area. Neighbor/seam/stability vetoes still apply.
4. **Stability and eligibility:** test brightness gain 0.9/1.1, contrast 0.9/1.1,
   sigma 0.5/0.8, background±2% of local intensity reference, seed±2 pixels in four
   directions, J radius 20/32 and M domain 32/48. Flag minimum IoU<0.70, centroid
   shift>4 pixels, domain IoU<0.90 or M window contact. Also require native cue
   exposure/material, connected evidence, pigment/background consistency, and
   the inherited 12–870 pixel operational bounds.

The masks and results of every perturbation are saved, for **both J and M and B**.
These are conditional sensitivity tests: HSV, paper labels, learned palette and
initial A are held fixed. Seed changes keep A fixed and use a 93px M window to fit
the offset. Common gains do not simulate physical relighting. Enlarging J's domain
can reveal artificial circular clipping, but a modest-radius test cannot prove
complete domain independence. NativeY is saved separately; plotted lines use the
smoothed fields and plotted dots sample original native-coordinate luminance.

The simple decision order is: veto candidates with explicit defects; prefer the
sole survivor; if both survive, prefer M when diffuse continuation is supported;
otherwise retain both when IoU≥0.65, or abstain on unexplained large disagreement.
The sole-survivor branch is precisely where independent confirmation exposed a
failure. No learned classifier, fitted weights or physical geometry are used.

## First policy failed; why the revision was needed

V1 required outside brightness to remain≥70% of inside at J's contour. It abstained
on P2 despite 295 genuine, pigment-consistent added pixels. The test confused a
monotonic transition from highlight to diffuse red with a separation. A stronger
boundary gradient did not identify the better photographic interior.

V2 changes the *measurement*, not just that threshold: direct color/intensity
routes distinguish normal decreasing brightness from a valley and renewed surface.
It prefers M for P2, with 295/295 added pigment pixels supported. The old source and
all v1 results remain in `selector_v1.py`, `evidence_v1.py` and
`development-v1.json.gz`. V2 was frozen after development and before confirmation;
no parameter was changed after seeing the new 16 regions.

## Reviewed development and central failures

|Example|J / M pixels|Frozen selector|Measured evidence and limits|
|---|---:|---|---|
|P5|511 / 664|Prefer J|Nominal M/B good, but small perturbations merge it into 1270–1297 pixels; J stable|
|P2|200 / 495|Prefer M|295/295 added pigment pixels follow supported diffuse routes; preserves the good S measurement|
|C05 anchor|248 / 527|Prefer M|279/279 added pigment pixels supported; still acceptable-but-imperfect, not certified boundary truth|
|C02 weak edge|484 / 1475|Abstain|Seam conflict, instability and clipping/area defects; no extra edge optimization|
|C02 other context anchor|364 / 577|Prefer M|A different cue in the same crop; this does not satisfy the user's broad rejection of C02 and is not counted as a review success|
|C04 fresh unresolved merger|555 / 885|Abstain|Weak native cue plus domain/area evidence; no invented new bead|
|C07 anchor|105 / 384|Prefer M|279/279 supported diffuse pixels; overlapping neighboring cues remain alternatives, not four distinct beads|

The P5 perturbation failure is new evidence: nominal M is good, but sigma 0.5,
background-high, seed-left or seed-up change its competition and produce a large
connection. The full masks are shown; no threshold patch hides it. P1 returns both.
P3 prefers M because J is background-sensitive, despite the user's earlier preference
for J's nominal outline. Stability is informative but does not settle every visual
boundary preference. Tiny tinted features can still receive a colored J/M choice;
selection does not solve upstream feature/color identity.

## Independent confirmation:16 new regions, 63  cues

Selection happened before new outputs:8 red/8 yellow anchor strata comprising
8 crossing, 4 same-color-neighbor, 2 opposite-side and 2 additional near examples.
Hash-ranked image-only high-status anchors must be support-near and have native
11×11 medianY>0.025. Their centers are>100 pixels from previous reviewed centers
and>80 pixels from one another. All existing colored cues within 36 pixels are
retained, including rejected/unresolved cues:63 total. These are center-separation
criteria, not a claim that every context pixel is disjoint. No fresh-cue detector
or manually supplied correspondence is introduced.

[Selection](r287/results/selection.json) and [freeze](r287/results/freeze.json)
record the criteria, exact IDs, source hashes and absence of confirmation output
at freeze time. No empty strata or result-driven fallback selection was needed.

|Choices|Prefer J|Prefer M|Both|Abstain|
|---|---:|---:|---:|---:|
|16 anchors|5|8|3|0|
|All 63  cues|18|29|6|10|
|32 red cues|11|15|0|6|
|31 yellow cues|7|14|6|4|

The rule can prefer J for red and M for yellow. Mean J/M IoU is 0.515; 43/63 pairs
have IoU<0.65. The 29 M choices retain 6322 route-supported pigment pixels absent
from J; this is not 6322 independently verified true-body pixels.

New photographic evidence supporting the idea:

- N01/N03/N05/N09/N15: M retains diffuse red that J cuts back toward a highlight.
- N04/N14: fuller yellow material supports M. This is not a red-only preference.
- N06/N08: M joins two yellow regions; multi-path seam and perturbation evidence
  favor J. N13 similarly avoids an M merger of neighboring reds.
- N10: J extends to lower neighboring material; M is smaller and separated. The
  selector chooses M, demonstrating that it does not always favor larger masks.
- N02/N16: both contours remain plausible measurement alternatives.

Failures and unresolved explanations are equally important:

- **N07:** nominal M 515 pixels looks materially preferable to J 288. All 227 added
  pigment pixels pass direct continuation. But background-low makes M 1325 pixels
  and seed-right 1275, so the selector falls back to J. That choice discards visibly
  legitimate red material. Rejecting M's instability did not prove J adequate.
- **N11:** M has a questionable upper extension and becomes 2018 pixels under one
  background perturbation. The selector chooses J 167 pixels, although 525/527
  M-only pigment pixels have direct continuity. Abstention or a better-evidenced
  interior may be preferable; this confirmation is preserved without retuning.
- **N08/N13:** avoiding the large merger does not prove the selected J support is
  sufficiently representative; considerable photographed material remains excluded.
- **N12:** both is returned despite a questionable lower M appendage. IoU and no
  detected seam conflict do not establish equal quality.
- **N06 weak neighboring cue:** a 52 pixel tinted highlight receives a red J
  preference. It visually resembles a reflection on dark material; this is an
  upstream color/feature ambiguity, not a newly established red bead.

All 63  cues are shown in the atlases, including ten abstentions and high-source
cues that now abstain. Source status never overrides the photographic rules.
These visual assessments are review evidence, not a calibrated accuracy dataset.

## Quantitative diagnostics and coverage

|All 63  cues|Always J|Always M|B|
|---|---:|---:|---:|
|Nonempty within 870 pixels|63|52|54|
|Detected coherent-seam conflicts|1|7|6|
|Minimum perturbation IoU<0.70|2|19|19|
|Domain IoU<0.90|5|7|5|
|Mean minimum perturbation IoU|.895|.784|.790|

For M, seed changes flag 12  cues and background changes 11; sigma 5, contrast 3,
common gain 0. J's corresponding counts are 0, 2, 1, 0, 0. These counts overlap. Domain flags
use 0.90, unlike the 0.70 instability threshold. Zero detected conflicts among retained
selector alternatives is a consequence of its own veto, not independent precision.
Native supports remain connected; connectedness does not prove single ownership.

|Coverage, all proposals unless selector abstains|J|M|B|Selector|
|---|---:|---:|---:|---:|
|Retained observations|63|63|63|53|
|Support-near|39|44|42|36|
|Measured support-crossings|25|30|29|24|
|Near overlap groups|39|42|40|36|
|Overlapping pairs|1|7|4|1|
|Near-duplicate pairs, IoU≥0.5|0|2|2|0|
|Opposite-side flanking pairs|1|2|2|1|

Always-method rows include their flagged proposals to show the full tradeoff, not
an acceptance comparison. Both counts one observation with two alternatives;
robust near/crossing requires all retained alternatives to agree. Groups joined at support IoU ≥ 0.5
are not verified bead counts. Signed support extent and arc intervals, rather
than nearest centroid alone, determine near/flanking evidence. All observations
and unresolved alternatives remain saved even when selector coverage excludes them.

**Complete centerline recovery has not improved demonstrably.** The selector removes
merger/overlap warnings but loses near/crossing evidence and one flanking pair.
Compact supports can understate full-body crossing, and a black reflection cannot
establish body extent. No fixed station quota is imposed. This round changes the
choice of existing interiors; it certifies **zero new distinct physical beads**.
Real precision/recall remain unknown. Full per-case metrics, routes, overlaps and
coverage are in [evaluation.json](r287/results/evaluation.json).

## Mechanisms, black measurements and validation

Mathematical controls retain 100% of added monotone diffuse/narrow bright material,
but only 31.25% when a dark stripe precedes a new bright surface. Identical pixels
interpreted as internal dark texture yield identical evidence: no algorithm can
recover different physical ownership from identical pixels alone. These controls
test the measurement mechanism, not real precision or physical rendering quality.
Fresh physical renders were optional and were not needed for this narrow selector
experiment; actual photographs and preserved failures remain decisive.

Black R2/R1/R4 outputs and source code are unchanged. R287 records their hashes and
links R286's 144 exact reflection replays; it does not claim a new black re-estimation.
Separate primary/secondary observations and unknown physical ownership remain intact.
Phase 2/3 implementations and all historical scientific files remain unchanged,
except the explicitly revised permanent Phase 1 specification.

108 tests pass (17 new + 91 historical). Both independent rerun files match exactly;
10,480 historical scientific blobs and 45 native crops are unchanged. Chromium
checks pass for 82 images, 26 tables, 28 sections and 133 local links, including
desktop and narrow layouts. Verification records are saved in `r287/results`. [Reproduction](R287_REPRODUCE.md),
[checklist](R287_CHECKLIST.md), and [checkpoints](r287/checkpoints) preserve the work.

## Recommendation and required stop

Keep the evidence ledger and direct diffuse-continuation mechanism as promising
research directions. They explain useful J/M choices beyond the original examples.
**Do not adopt the frozen v2 selector unchanged.** Its automatic sole-survivor
fallback is not a sufficient reliability rule; no hybrid or full inventory is adopted.
B remains diagnostic because of its shading false split. R2 remains reflection-only.

After the user's assessment, the proposed next bounded task is to distinguish
“J is adequate” from “M is unstable,” retaining both or abstaining when those two
claims conflict, then test on a newly frozen central set. That is a proposal only.
Stop here for review: no automatic R288, production replacement, global physical
fit or pattern inference. Keep current model/reasoning; no `/new` needed.
