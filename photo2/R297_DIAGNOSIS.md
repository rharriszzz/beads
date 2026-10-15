# R297 diagnosis before the final pilot

The full R296 model is a geometrically feasible arrangement along the whole
image-derived reference, with substantial local first-hit compatibility. It is
not an observed inventory: 1,574 of 2,337 sites lack compatible observations and
602 have modeled visibility below 10%. Patch/region counts are correlated,
reflection observations do not identify dark bead bodies, and weak support cannot
establish physical ownership. The reference's periodicity does not prove closure.

The paired native-support experiment is saved in
`r297/results/paired-diagnosis.json.gz`. It compares the same 36 larger supports,
including failed physical models, without using the old indices as targets:

| Intervention | Large-support mean | Physical status |
|---|---:|---|
| Original R295 local | 71.51% | certified |
| R296 selected | 63.11% | certified |
| R296 with R295 camera | 62.16% | certified |
| R296 with R295 shape | 62.91% | certified |
| R296 with R295 phase | 62.97% | certified |
| R296 without learned full-loop fields | 64.30% | certified |
| R295 extended N2337, original normalization | 62.83% | certified |
| N2337, restored local metric only | 74.51% | certified |
| N2337, restored local metric and phase | 71.52% | certified |
| N2438, restored local metric and phase | 71.52% | certified |
| N2540, restored local metric and phase | 71.52% | demonstrated collision elsewhere |

R296 normalizes integrated station increments to the full deprojected path length.
Its stored `pitch` is initializer metadata, not an independent local pitch control.
Changing total count therefore changes local spacing. Closed integer winding also
changes phase progression from the original 6.485 beads/turn. These are separate
mechanisms: restoring phase alone does not restore local containment. Camera and
shape affect visible extents and occlusion, but their paired interventions do not
explain the main regression. Reverting old strain/pitch/origin does nothing because
those values had not changed.

At C-2038-0658, the R295 conditional assignment195 has96.70% containment; R296
assigns182 at77.36%. Restoring the metric returns195 at95.16%, and restoring both
metric/phase returns96.70%. This is conditional label recovery, not certified
identity. At C-1729-0337 near65,61.86% falls to41.37%; metric restoration gives68.88%.
At E5-1633-0278 near33, R296's77.55% improves on R295's50.46%, but the restoration
returns53.24% or50.46%. Preserving one useful fit does not resolve all earlier
failures, and the comparison must retain this tradeoff.

The retained R296 open hand− candidate166 has55.73% local mean, closed hand+
94 has60.32%, and open hand+112 has72.14%. On the full R296 native evaluation,
selected closed hand− is stronger on validation/reserved large supports than these
alternatives, but different local successes favor retaining them. This evidence
ranks finite tested models; it does not prove hand, count or a physical join.

The first local-rate repair redistributed its compensation over the entire loop.
It restored old local supports but shifted the remaining station map. The retained
v2 repair blends a local cumulative physical station map into the existing one
with a compact taper, leaving the exterior unchanged. It rejects any reversed
station order. Local phase correction is also tapered; all candidate contact pairs
are rechecked. Tests compare actual projected centers and full-loop witnesses.
Failed transfer probes, colliding models and source versions remain archived.

The old objective has no direct region-containment term: its material contribution
comes through a beam with a positive null reward and a 90% cap. Its image-edge
term measures the average edge strength at predicted boundaries, not boundary
recall or precision against verified separators. Equal region weighting, conditional
owner balancing and a small patch coefficient already limit patch multiplicity,
but do not protect difficult geographic sections or an earlier useful fit.

Four identical-start,128-proposal development ablations precede the second repair:

| Objective | Native train large mean / compatible | Validation mean / compatible | R295-local mean |
|---|---|---|---:|
| Original |64.77% /90|73.99% /9|63.16%|
| Section-balanced material |65.04% /102|74.83% /8|64.37%|
| No patch reward |65.04% /102|74.83% /8|64.37%|
| No boundary/continuity terms |65.19% /98|74.14% /8|63.83%|

At this budget patch removal selects the identical model: no demonstrated benefit
from that term here. Removing boundary terms slightly improves training mean but
worsens validation mean, local preservation and continuity diagnostics. That is
limited development evidence to keep the terms, not an independent causal accuracy
test. Section balancing improves compatibility counts and reduces domination by
large observation clusters; it does not by itself solve local regression.

The second revision therefore adds a soft prior-fit preservation term. It compares
large-support means on the same eligible observations against R295's local and
R296's full fit, allowing a three-percentage-point tolerance before penalizing the
largest loss. No old index, ownership or pixel label becomes a constraint. The
reference means are retrospective development evidence; tolerance is an engineering
tradeoff, not an uncertainty interval. The objective still needs native region
comparisons and photographic review. There are no genuinely untouched final data
left in the eligible evidence; old reserved intervals remain excluded from new
optimization and are reported only as retrospective final checks.

The matched second-generation128-proposal control confirms the preservation
tradeoff: without the term, native training/validation large means are64.84/75.02%
and the R295 section63.15%; with it,62.63/72.89% and71.16%. The complete512-proposal
medium run recovers training mean to63.49% (R29663.25%), validation73.03%
(R29674.54%) and the local section69.64%. This is progress with a validation
regression, not a scalar-score success declaration. The run retains393 eligible,
33 physical rejections (28 demonstrated overlaps,5 inconclusive),52 coarse-screen
rejections,20 bound rejections and14 duplicate proposals.

A further development test at medium candidate311 transports part of the old
phase field through the station-correction transition, while leaving the restored
local core unchanged. At coefficient0.25, sampled training containment rises
62.84→63.41%, validation remains73.44%, and the full-chain certificate passes.
Coefficients0.5,0.75 and1.0 demonstrate actual interpenetration. The final program
therefore searches this bounded coefficient under the same physical gate; it does
not assume that transported phase is safe. Test records and the exact probe source
are preserved. This is a general compact-transition correction, not an observation
or old-index repair. The final pilot uses the corrected program with a768-proposal,
1800-second search cap, with no subsequent scientific tuning from final outcomes.
