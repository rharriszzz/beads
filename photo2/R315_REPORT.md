# R315 — causal geometric diagnosis; measurement repairs and partial local gains

**No convincing 200-bead reconstruction was obtained. No geometry is adopted.**
R315 establishes actual early occluders, repairs two demonstrated measurement
limitations, and tests independent registration and genuinely local smooth fields.
The selected narrow-field experiment improves several cores and separation evidence,
but does not satisfy the fixed photographic geometry requirements. It is retained
as a counterexample to both “occlusion alone explains everything” and “more local
phase freedom solves everything.”

[Static ledger](r315/results/index.html) · [same-region comparison](r315/results/review/before-after.png) · [protocol](R315_SPECIFICATION.md) · [reproduce](R315_REPRODUCE.md) · [verification](r315/results/verification.json) · [delivery](r315/results/delivery.json).

## Confirmed defects and limitations, versus physical hypotheses

1. **Overconservative ray aggregation and insufficient iteration budget.** R314
   marks a pixel unknown if *any* candidate solid's ray remains unfinished, even
   when that unfinished ray can no longer be in front of a certified hit. R315
   retains the remaining-depth bound and continues only unfinished rays. 29 unknown pixels are already decidable from depth bounds alone. All 70
   unknown R306 raster pixels resolve; 20 touch material, 14 touch a core, zero
   touch known paper, and 15 lie outside the geographic ROI. These are small grazing
   uncertainties, not an explanation of large coherent geometric errors. All 70
   independently agree with a separate depth-root calculation. R313-focused-3 and
   R312-local resolve 57 and 53 pixels respectively. No measurement pixels are dropped.
2. **Censored boundary measurements create false flat tails.** R306 originally has
   20 missing extended-scan brackets. Ray refinement resolves two within the old
   scan; 18 require looking farther. All 414 now have a correctly oriented boundary
   somewhere on the same raster line. The 18 farther excess distances are 13–57px,
   not a constant 50px. Comparison exterior p95 is **15.6px**, whereas R314 reports
   the 50px sentinel. This is a measurement correction, not geometry improvement.
   A distant boundary can belong to another bead or turn and is not accepted as a
   correct local reconstruction. Every endpoint, direction, interval, split,
   strength and missing/found classification is retained. The full-line search is
   still censored by raster extent, explicitly reported rather than assigned 50px.
3. **Registration omits two independent image freedoms.** The original measured
   anchor is a visible photographic feature, not a measured physical center.
   R315 adds a post-construction x/y image offset. Exact tests show unchanged 3D
   centers, frames, dimensions and contacts. Translation can cure one observed core
   while damaging others; its omission is a real restriction, not the sole cause.
4. **The search basis is locally coarse and redundant.** At N=2405, 32 full-loop
   nodes are 75.16 addresses apart. Near the reference, the existing cosine phase
   direction is almost identical to global phase (absolute scaled-state cosine
   0.9999999); tilt and trajectory-orientation mixing are similarly coupled.
   A 0.18rad compact phase bump of halfwidth20 leaves a 0.114rad maximum residual
   when approximated with the old nodes bounded to ±0.45rad. This is a concrete
   representational limitation, not proof that this bump is the real deformation.
   The inherited `pitch` key is inactive: mean advance is determined by loop extent
   and count. R314 did not search that inactive key, so this is not evidence that
   its 1,382 proposals were all ineffective. Actual trial ranges, discrete families
   and exact duplicate checks are in the coverage report.
5. **No simple camera convention bug was found.** Independent camera-frame
   determinant/orthogonality, ray reprojection and a separated near/far fixture pass.
   Larger ray parameter is correctly nearer the camera. Original-Python/native
   agreement is supplemented by these invariants, but neither calibrates the actual
   photograph. Orthographic and finite-perspective controls, elevations40/75/85°,
   and roll±20° do not establish a geometric cure.

The actual external glass profile, a mechanically settled crochet placement law,
true local phase/spacing and a verified physical correspondence remain hypotheses.
No uniquely dominant physical cause among shape, pose and placement has been proved.
The earliest negative failure requires more than corrected visibility alone.

## First failures, alternatives and actual occluders

The ledger uses the exact original fixed eroded pigment cores. They are correlated,
uncalibrated evidence, not full silhouettes or verified bead identities. “80% isolated
explanation” below is a diagnostic threshold; 60/70/80/90% first-failure controls are
retained. The photographed reference C-1497-0271 is at (1499.36,271.20), distinct from
its weak reflection and from any physical center.

| Photographic core / conditional R306 owner | Best isolated candidate / coverage | That candidate visible | Actual main occluders / removal effect |
|---|---:|---:|---|
| Reference C-1497-0271 / 0 | 0 / 84.8% | 84.8% | No loss of this candidate to occlusion. Candidate −4 overlaps55.0% in isolation but is hidden by0; it is not thereby a real alternative identity. |
| C-1477-0290 / −7 | −9 / 48.1% | 8.4% | −7 hides55 core pixels, −8 hides43; removing either raises −9 to16.1% or21.7%. No isolated candidate explains the whole core. |
| R282-1459-0316 / −8 | −8 / 57.3% | 57.3% | Main candidate has no occlusion loss. A secondary −15 candidate overlaps42.0%; occlusion is not sufficient to explain this failure. |
| R282-1536-0239 / +8 | +8 / 93.9% | 78.2% | +7 hides39 pixels and +14 hides20. Removing +7 alone gives88.6%; removing +14 alone gives83.6%. |
| R282-1537-0308 / +12 | +11 / 66.4% | 16.7% | +12 hides238 pixels. Removing it restores66.4%, still an incomplete explanation. The full-scene modal +12 covers58.2%. |
| C-1559-0252 / +14 | +15 / 70.4% | 2.4% | +20 and +14 hide119 and81 pixels. Removing them individually gives27.2% and29.9%, respectively. Other occluders remain. |

Every removal is **diagnostic only and physically invalid as a reconstruction**.
The ledger records all overlapping candidates, exact camera-ray depth differences,
physical centers/axes, projected centers, +1/+6/+7 neighbor positions and individual
occluder-removal outcomes. NPZ crops retain native coordinates, first-hit owners,
depths and isolated surfaces. White exterior, cyan bead-to-bead occlusion and magenta
bore boundaries are separate model layers; no complete black-bead contour is inferred.

At the historical70% single-owner criterion the first negative observed failure is
C-1477-0290, (1480.38,291.20), photographic arc−19.81px, conditional−7. Positive failure
first occurs at R282-1537-0308, (1538.95,309.95), arc+40.79px, conditional+12.
At80%, the earlier +8 core at arc+37.26px also fails. These are first **measured**
failures, not a uniquely established first physical error or an error-free prior
chain. Full-interval plots show fragmentation, recovery and renewed failure rather
than a demonstrated monotonically accumulating index error.

The four requested outcomes are distinguished: isolated shape/pose/registration
failure at the first negative core; a plausible isolated surface hidden at+8;
multiple isolated aliases in R312-local at the reference; and unresolved observation
or identity whenever these partial cores cannot discriminate candidates. The selected
narrow model still has no80% isolated explanation at the first negative core.

## Rigid packing and indexing

The physical-neighbor ledger contains **614 pairs** touching the target interval,
including +1/+6/+7 and additional spatially close bodies. All 200 target bodies and
all 2,405 full-necklace bodies remain in visibility and certification. Every candidate
uses one shared rigid glass shape; there are no independently moved or reshaped beads.

Support-plane gaps are explicitly **lower bounds**, not exact distances. Actual
solid boundary points supply upper bounds. Sixty closest pairs receive independent
normal refinement; 48 obtain primal/dual widths below1e−4 source units, with every
refined endpoint's actual-solid implicit residual below8e−9. Other pairs keep their
wider uncertainty intervals. R306 +1 lower bounds are0.293–0.303 units; +6 span
0.153–0.672; +7 span0.422–1.009. These gaps do not justify universal lattice contact.
The largest +7 gaps are a physical-model question, not a penetration defect.

Eleven target beads lie within0.03569 source units of the common horizontal support
plane. Across30 complete minor-turn bins, the lowest-body clearance has median0.115
and maximum0.468 units. Thus some turns float in this prescribed geometry. Upper
beads naturally have much greater paper clearance; paper is not a center plane.
A feasible support translation is not mechanical equilibrium. The certified model
can have the observed wrong visible ordering without violating nonintersection;
contact checks therefore do not certify that ordering as physically correct.

Uniform index relabeling is exactly rendering-invariant. R313-focused-3 differs
from R306 by no modal-owner shift in36/40 cores; other changes include±6 aliases.
R312-local's best global shift is−2 and explains only6/40 modal-owner differences.
A single integer relabel cannot reconcile these maps. Physical k±1/±6/±7 shifts
change both station and phase and are distinct from relabeling. No observed +1/+6/+7
adjacency chain is independently established, so no alternative outline overlap is
promoted to recovered physical identity.

## Targeted correction experiments and measured tradeoffs

The initial controlled epoch evaluates **239 distinct settings in146.78s**, including
72 nonzero translations on three saved families, explicit camera/phase/station
controls, 24 compact single-direction tests and128 coupled compact trials. There are
237 certified settings and two rate-bound exclusions. It is not another R314 global
search: count, hand, topology, shape and dimensions stay fixed within each parent;
only the new registration/compact basis and named controls are tested.

The broad compact fields use centers−35/0/35, phase halfwidth45 and station halfwidth65,
with added local phase and spacing rates bounded to2%. Their selected minimax ranking
improves some large errors by sacrificing the reference and other cores. This is
retained as a failed corrective experiment, not adopted.

Because that phase basis still spans many revolutions, a separate **141-setting,
82.04s** causal follow-up uses centers−13/0/13 and phase halfwidth18. Its declared
added phase-rate ceiling is5%, a plausible exploration hypothesis rather than measured
strain; station-rate ceiling remains2%. The selected added phase derivative is
0.02462rad/address (2.55% of2pi/6.5), and added station-rate maximum is0.314%.
All fields smoothly vanish outside the local interval.138 settings certify; three
exceed the rate bound. There is no uncontrolled twist or individual-bead motion.

| Fixed evidence / metric | Refined baseline | Translation −8,0px | Broad compact | Narrow compact |
|---|---:|---:|---:|---:|
| Development material explained % | 90.08 | 88.78 | 88.72 | 88.98 |
| Development known paper occupied % | 0.148 | 1.084 | 1.167 | 0.314 |
| Development mean single-owner core % | 69.78 | 66.67 | 64.22 | 70.47 |
| Development supported seam conflict % | 44.72 | 39.84 | 33.33 | 29.27 |
| Development finite exterior p95 px | 9.0 | 9.0 | 9.0 | 10.0 |
| Development worst-core p95 px | 13.60 | 10.77 | 9.22 | 13.14 |
| Comparison material explained % | 88.94 | 87.80 | 87.47 | 87.78 |
| Comparison known paper occupied % | 1.537 | 4.910 | 5.090 | 1.746 |
| Comparison mean single-owner core % | 55.87 | 50.34 | 52.96 | 57.66 |
| Comparison supported seam conflict % | 37.31 | 52.24 | 59.70 | 26.87 |
| Comparison finite exterior p95 px | 15.6 | 15.3 | 13.9 | 15.6 |

These use identical photographic evidence and new resolved rays. Small baseline
coverage changes relative to R314 are measurement refinement, not a fitting gain.
No illumination optimization or remeasurement of the photograph occurs.

For the narrow experiment, reference coverage is84.8→81.2%, first negative28.6→52.2%,
+12 core58.2→69.5%, and C-1559 core48.6→67.3%. But the next negative core57.3→41.0%
and +8 core78.2→74.5% regress. Mean six-core coverage rises59.3→64.3%. Modal identities
remain conditional and changed-owner cases are retained. The surface and separation
improvements are real diagnostic measurements; they are **not a substantial accepted
200-bead reconstruction**. Static inspection confirms visible misplacements.

Every exported target receives its complete native bounding-grid render:
84,369 /84,369 /84,281 /84,416 rays for baseline/translation/broad/narrow, all with
zero remaining unknown rays. Complete necklace occlusion/contact is retained.
Unsupported physical addresses remain unmeasured, never silently omitted.

## Acceptance, bright features and remaining obstacle

Exploration uses separately normalized material, paper, seam, exterior and core
violations without the historical two-percentage-point owner-loss veto. The new
readiness function applies conservative absolute requirements to fixed evidence;
unknown rays on unrelated raster pixels are reported but do not veto readiness.
Missing boundary count and finite-distance distribution remain separate. Historical
R314 acceptance is also retained as a diagnostic, not physical ground truth.
No candidate passes even the new absolute requirements. Better coverage cannot
purchase acceptance of wrong paper occupation, seams or fragmentation.

All811 inherited bright observations remain available, including black-bead features.
Geometric first-hit ownership at unchanged local observed bright coordinates is
recorded without claiming that owner has the corresponding specular peak. R314's
connected patches, faint lobes, peak/tie machinery and fixed peak-minimax API remain
unchanged. The reliable principal cohort is still unavailable, not a zero Emax.
No optical fitting was performed.

The most useful remaining obstacle is **joint local surface placement and visible
ordering under a mechanically credible shared orientation/profile**, constrained by
several neighboring material cores and independent paper brackets simultaneously.
A change that merely exposes an overlapping isolated bead cannot repair the first
negative red core. Registration freedom and a local basis are now available, but
this bounded test does not show that they suffice. The retained contact/depth ledger
makes a subsequent shared orientation/profile or packing-law test falsifiable;
it does not authorize another campaign or prove a specific physical law wrong.

## Verification and delivery

26 contracts pass, including inherited R314 bright-feature and shape contracts.
Independent replay checks9,620 positions,28,654 full-chain contact certificates and
39,155 original-Python sampled rays, plus independent root resolution of all70
previously uncertain R306 rays. All exported metrics and bracket records replay
exactly. Every refined contact upper witness lies on the actual solid. Photograph
and historical evidence hashes are preserved; no previous scientific source changes.
Static PNG/link checks and Chromium desktop/narrow/offline checks are recorded.

An initial test expected18 historical missing brackets, conflating the18 remaining
after ray refinement with the original20. The failed test log is preserved, and the
assertion now separately reflects the old20; no measurement was changed to pass it.
The report distinguishes initial controls, broader compact and narrow corrective
epochs rather than retroactively presenting all proposals as one successful search.

Work began21:52:09UTC on2026-10-17; hard deadline22:22:09UTC. New fitting concluded
before22:04UTC, leaving well over six minutes for independent review and delivery.
The final elapsed time and independently checked remote commit are in the receipt.
**Stop for scientific review. No adoption, Phase3, repeating pattern, beads.pov edit,
or automatic R316.**
