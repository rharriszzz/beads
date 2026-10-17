# R313 — geometric evidence and structural diagnosis; no adoption

**No substantially better reconstruction has been established.** The new objective
recognizes gross geometric failures and exposes local improvements, but its numerical
winner still has visibly wrong surfaces. It is an experimental candidate, not an
adopted reconstruction. All beads have one identical, rigid glass shape and size;
`beads.pov` dimensions are hypotheses, not measured constraints.

[Static photographic review](r313/continuation/index.html) ·
[Reference and first-40 comparisons](r313/continuation/review/reference-first40-both-directions.png) ·
[20 worst measured regions](r313/continuation/review/worst20-geometric-mismatches.png) ·
[Reproduction](R313_REPRODUCE.md) · [Verification](r313/continuation/verification.json).

## What replaces the earlier objective?

Sixteen uncertain, sparse annotated contours could neither describe the widespread
surface errors nor establish correct bead ownership. Nearby unrelated transitions
and internal holes could substitute for external boundaries. Improved specular
positions did not validate shape. Those contours remain historical records and are
excluded from R313 fitting and acceptance.

R215, R265, R275, R285–R290 and Phase 1 informed frozen image measurements:
**31,679 colored-material pixels, 38,540 confident paper pixels, 1,441 persistent
photographic transitions and 40 interior cores**. Additional weak transitions remain
uncertain. Dark valleys with pigment on both sides are candidate separations, not
verified complete bead contours. No black silhouettes are inferred. The maps and
original 426 evaluations are byte-preserved. The fixed photographic region does
not move with a candidate. Exactly −100…99 physical bodies are the target; all
necklace bodies remain in occlusion and contact computations. Geographic context
outside that interval is reported separately, never silently discarded.

The replacement scores material omission, paper occupation, supported transitions
in both directions, fragmentation, incompatible color ownership and individual
worst errors. A separately frozen second scoring epoch adds distances from each
core to one visible body and owner-specific exterior-envelope transitions. A 3px
uncertainty band and supported-edge neighborhoods avoid demanding imaginary
complete contours. The added envelope diagnostic fills enclosed holes, including
closed occlusion holes; it is not an independently observed silhouette.

## Does it recognize wrong surfaces?

**Grossly wrong ones, yes; reliable ranking of plausible alternatives, not yet.**
The initial all-owner merging loophole was repaired and its failed control retained.
Second-epoch R306 score 2.838 rises to 11.444 for one owner everywhere, 6.727 when
alternate bodies disappear, 4.758 for full-background occupation, and 7.231 after
7px erosion. Pure owner permutation leaves the score exactly unchanged. However,
3px dilation improves it to 2.736, and deletion of bodies without pigment support
has almost no cost. Such surfaces are insufficiently observed, especially black
beads. Physical fitting cannot delete bodies, but these controls expose the limits
of the evidence and the aggregate loss. See [all controls](r313/continuation/objective-controls-v2.json).

The limited search was a structural diagnostic under those explicit limitations,
not a declaration that the objective had become a validated acceptance test.
No further search followed its sealed seven-minute allowance.

## Are the outlines better?

The table uses identical frozen evidence and the second-epoch score. Development
and comparison are distinct photographic regions; comparison regions were excluded
from fitting but historically exposed, so are **not a statistically fresh holdout**.

| Model / region | Score ↓ | Material explained ↑ | Known paper occupied ↓ | Mean one-body core ↑ | Transition p95 ↓ | Worst core p95 ↓ |
|---|---:|---:|---:|---:|---:|---:|
| R306 / development | 2.838 | 90.02% | 0.15% | 69.77% | 8.01px | 13.60px |
| R313 focused-1 / development | 2.476 | 97.18% | 2.16% | 68.36% | 9.06px | 8.60px |
| R313 focused-3 / development | 2.501 | 92.01% | 0.35% | 74.02% | 9.06px | 11.00px |
| R306 / comparison | 3.172 | 88.90% | 1.54% | 55.87% | 8.03px | 9.85px |
| R313 focused-1 / comparison | 3.433 | 96.41% | 4.04% | 61.35% | 10.00px | 17.00px |
| R313 focused-3 / comparison | 2.649 | 91.51% | 2.15% | 64.86% | 9.00px | 8.54px |

R297/R306/R309/R312-final development scores are 2.913/2.838/3.152/2.764;
all baselines and initial R313 incumbents are in the [complete table](r313/continuation/summary-table.json).
Unexplained material is the complement of explained material; raw counts, both
boundary directions, maxima, ownership conflicts and fragmentation are retained
per region in every model export.

Focused-1 increases development paper occupation from **41 to 597 pixels**, and
same-owner crossings of candidate seams from **43.15% to 54.31%**. Comparison seam
crossings rise 51.49%→61.19%. Its enlarged surface coverage defeats the intended
balance of the loss. Static inspection shows lower surfaces extending into paper
and persistent misplaced separations. Focused-2 has conspicuously flattened,
rectangular outlines; its low score is also not success. Focused-3 is a less
disruptive partial alternative, but retains conspicuous first-neighbor errors.

There is a genuine local coverage gain with unchanged owners: reference core
C-1497-0271 rises **84.75%→99.65%** in focused-1, and the first negative red core
C-1477-0290 rises **28.57%→75.47%**. These are measured interiors, not complete
outlines. Across all 40 cores, 17 modal owners change; [fixed-parent comparisons](r313/continuation/ownership-changes.json)
prevent presenting assignment changes as recovered physical identities.

The worst remaining measured core is near **(1239,313)**: p95/max material miss
17.0/19.7px, owner-specific transition p95 20.2px. Near **(1787,384)** these are
13.2/15.5px and 21.4px. The atlas includes 20 regions with locations and distances.
Historical cores can overlap (notably two records near 1239,313); they are correlated
measurements, not 40 proven distinct beads. No post-fit deduplication or observation
change was used to improve scores.

## Shape, orientation, paper and contact

Seventy-six explicit structural cases tested shared hole diameter, annular rounding,
axial thickness, old tilt and orientations interpolated toward the actual local
helical trajectory. Thirty-four certified separation; 42 demonstrated penetration.
The approximately 82° neighbor-center direction is **not** evidence for an 82° hole
axis. Fully trajectory-aligned alternatives did not provide a certified cure.

The numerical winner couples thinner beads, hole/outer-diameter ratio 0.494
(inherited 0.14), rounding 0.673 (0.8), altered orientation and registration.
Its hole axis is about 10.8° from the major tangent, not 83°. Focused-3 stays much
closer to the inherited shape. Profile, orientation and positioning reversions
interact; reverting the winner's profile causes actual penetration, while reverting
position/camera substantially worsens score. **Neither the annular family nor the
orientation law has been uniquely falsified or established as the primary cause.**
Secondary frozen-owner strong-reflection RMS worsens 9.92→16.13px in focused-1
(one missing lobe), consistent with a structural tradeoff rather than a solved fit.
No arbitrary per-bead distortion, illumination compensation or nonplanar major
centerline was introduced. Independent face-curvature parameters were not tested;
the shared rounded-annular profile remains restrictive. Absolute millimeter size
is unidentified. Glass transmission/refraction is not calibrated by the inherited
first-hit geometric renderer; reflections remain approximate secondary diagnostics.

Convex filled-envelope separation is sufficient, not necessary. Actual hollow-solid
checks demonstrate penetration in all 12 selected previously unresolved R312 cases;
that is not an audit of all 1,301. A separate interlinked-ring fixture certifies
actual-solid separation despite convex-envelope failure. Three promising new
near-contact candidates remain unresolved after higher-budget checks and are
preserved without adoption. See [contact audit](r313/continuation/historical-contact-audit.json.gz).

Every exported model can be placed above one common horizontal supporting plane
using exact support extrema. This is a necessary geometric check, not equilibrium:
per-minor-turn lowest clearances still reach about 0.43 source units in focused-1.
Some turns therefore float above the common paper plane. The paper is not the
plane through bead centers. Prescribed crochet frames/contact separation do not
establish a mechanically settled necklace.

## First disagreement and next experiment

At a 70% single-owner interior threshold, R306's earliest measured negative failure
is C-1477-0290 at **(1480.38,291.20)**, photographic arc **−19.81px**, conditional
owner **−7**, with four substantial owners. The first positive failure is near
(1538.95,309.95), +40.79px, conditional +12. Focused-1 improves both, but fails next
near (1459.74,313.26), −42.25px, and (1563.76,250.54), +62.43px. Threshold sensitivity
is saved. Sparse observations and unverified identities prevent claiming a unique
first erroneous physical bead or an error-free preceding chain.

Solved here: fixed evidence, retirement of annotated contours, reproducible native
shared-shape rendering, explicit three-way contact classification, and exposure of
coverage/ownership tradeoffs. Unresolved: complete outlines, trustworthy relative
ranking, physical indexing, settled contact geometry, shared profile/orientation
identification and a substantially better reconstruction.

**The single next experiment should be a local joint falsification around bead 0
and its two negative red neighbors:** freeze independently supported boundary-side
and separation measurements there, then compare a small set of identical-glass
profiles and coherent orientation/contact laws, including the common paper plane.
Require simultaneous interior, exterior and separation improvement before any
larger search. This is a recommendation for scientific review, not authorization
or an automatic R314.

## Budget, verification and delivery

The interrupted 11m33s session and all 426 trials are preserved. The fresh allowance
started 20:17:01 UTC on 2026-10-17; delivery must finish before 20:47:01 UTC.
The continuation used **808 proposals in 420.18s**: 739 certified, 42 demonstrated
penetrations, 20 numerical-bound exclusions and seven unresolved. Median feasible
evaluation was **0.532s** (render 0.409s, measurement 0.054s, geometry 0.008s,
contact 0.006s). The R312 native kernel was generalized without approximate
predictions; no additional speedup is claimed or old profiling campaign repeated.

Twelve contracts pass. Independent final verification checks 29,172 positions,
86,615 complete contact-pair witnesses, 106,908 stratified original-Python rays,
all exported metrics, all 426 old trial hashes, unchanged photographic maps and
fitting-source manifests. Forty-two structural overlap witnesses are independently
recomputed. Static PNGs and local links pass; the missing report link is repaired.
Numerical verification does not certify photographic correctness. Exact delivery
UTC, total fresh wall time and remote commit receipt are recorded in
[delivery.json](r313/continuation/delivery.json). **Stop for scientific review; no adoption.**
