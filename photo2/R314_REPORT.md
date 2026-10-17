# R314 — geometry gates repaired; no convincing 200-bead reconstruction

**The requested geometric reconstruction was not achieved. No model is adopted and
no highlight optimization was performed.** The maximum peak-to-peak objective and
connected-feature machinery are implemented and tested, but a scientifically usable
maximum remains unestablished: geometry and physical correspondence are not verified.

[Static review](r314/results/index.html) · [reference neighbors](r314/results/review/reference-neighbors.png) · [full geography](r314/results/review/whole-geography.png) · [protocol](R314_SPECIFICATION.md) · [reproduce](R314_REPRODUCE.md).

## What changed before fitting

The original R313 boolean persistence expression included the center pixel and was
therefore tautological. R314 requires supporting responses on both neighboring
tangent rows, with ±1 normal-pixel drift. 1429 ridge
samples before that requirement become 1137. The old
material, paper, core, photo and geographic arrays are byte-identical. This does not
turn photometric transitions into verified complete contours.

The first preflight retained only three paper-supported exact transition samples.
That was insufficient; its complete source/evidence/results are preserved in
`r314/preflight-v0`. Before fitting, the frozen R314-v1 protocol instead establishes
**414 material-to-paper brackets**, each 2..12px wide, with
both neighboring tangent rows supporting its endpoints. Any boundary inside the
bracket is allowed. There are **211 color-supported seam
samples**. Dark valleys remain uncertain diagnostics, not mandatory physical seams.
The brackets are correlated local constraints, not complete observed bead silhouettes.

Acceptance is a conjunction: paper, exterior, seams and worst-core error may not
increase; no individual core may lose more than two ownership percentage points;
material and mean single-owner coverage must each gain at least one point. Absolute
readiness additionally requires the declared 95% material / 80% every-core coverage,
0.5% paper, 3px exterior/worst-core and 10% seam limits on both geographic sets.
These are engineering criteria, not calibrated confidence intervals. A scalar
coverage benefit cannot pay for a failed gate. Search merit is a maximum of normalized
geometric violations; it is not itself an acceptance decision.

The exact **3px dilation** decreases omission from
9.98% to
3.55%, but fails
paper, seam. Seven-pixel dilation,
all-owner and adjacent-pair merging, four 12px displacements, physical phase +1.2rad,
and ±18% scale controls also fail. Owner permutation is invariant. These controls
close the demonstrated compensation loophole; they do not prove perfect ranking
of plausible real geometries or certify unmeasured black surfaces.

## Bounded search and outcome

The valid epoch evaluates **1382 proposals in 540.41s**:
{'certified-separation': 925, 'demonstrated-interpenetration': 218, 'numerical-bound': 231, 'unresolved': 8}. Broad coupled exploration uses the first half; a multibasin
population with differential/coupled refinement uses the second half. Six retained
starts include R306, R312 whole/local alternatives (including opposite handedness
and count), R313 focused-3, focused-1 as a diagnostic, and R309's 2733 basin.
No new topology census, tiny single-basin simplex campaign, per-bead deformation,
per-bead lighting or repeating color inference was performed.

A short initial epoch of 120 proposals was stopped after detecting a ranking
helper that paired JSON-sorted dictionary values with positional normalization
scales. Its full sources/trials/log remain in `r314/search-epoch0`; no valid outcome
is claimed from its ranking. Named scales and a JSON-round-trip regression test fix
that error. Photographic metrics and conjunctive gates were unchanged. The valid
epoch restarted from original basins; the 30-minute overall clock was never reset.

**0 proposals pass the fixed development acceptance
conjunction.** No exported finalist passes the combined readiness requirements.
Every physical address −100…99 remains, including hidden/unmeasured bodies. Complete
necklace bodies participate in contact and occlusion. All 200 targets additionally
have complete bounding-box native rendering and individual visibility ledgers.
Geographic measurements are frozen, not recentered around a winner; context-body
material contributions are separately retained. This is evidence across the interval,
not a claim that 200 individual photographed beads have been identified.

| Model / set | Material explained % | Paper % | One-body core % | Exterior bracket p95* | Seam conflict % | Worst core p95 px |
|---|---:|---:|---:|---:|---:|---:|
| R306-2405 / development | 90.02 | 0.15 | 69.77 | 9.00 | 44.72 | 13.60 |
| R306-2405 / comparison | 88.90 | 1.54 | 55.87 | 50.00 | 37.31 | 9.85 |
| R313-focused-1 / development | 97.18 | 2.16 | 68.36 | 4.00 | 65.04 | 8.60 |
| R313-focused-1 / comparison | 96.41 | 4.04 | 61.35 | 9.00 | 62.69 | 17.00 |
| R313-focused-3 / development | 92.01 | 0.35 | 74.02 | 8.00 | 50.41 | 11.00 |
| R313-focused-3 / comparison | 91.51 | 2.15 | 64.86 | 23.40 | 32.84 | 8.54 |
| R314-basin-1 / development | 86.79 | 0.06 | 58.30 | 10.00 | 33.33 | 10.44 |
| R314-basin-1 / comparison | 85.60 | 0.36 | 50.08 | 50.00 | 40.30 | 15.81 |
| R314-basin-2 / development | 88.84 | 0.03 | 73.35 | 10.70 | 32.52 | 10.63 |
| R314-basin-2 / comparison | 90.27 | 0.90 | 62.74 | 50.00 | 37.31 | 9.00 |
| R314-basin-3 / development | 91.18 | 0.03 | 67.54 | 10.00 | 28.46 | 10.01 |
| R314-basin-3 / comparison | 91.68 | 0.72 | 56.18 | 50.00 | 23.88 | 12.65 |
| R314-basin-4 / development | 87.13 | 0.15 | 62.40 | 10.70 | 35.77 | 10.63 |
| R314-basin-4 / comparison | 84.74 | 1.15 | 44.01 | 50.00 | 41.79 | 14.00 |
| R314-basin-5 / development | 91.46 | 0.23 | 63.19 | 10.00 | 32.52 | 10.27 |
| R314-basin-5 / comparison | 92.30 | 1.24 | 60.95 | 22.70 | 35.82 | 18.36 |
| R314-basin-6 / development | 88.65 | 0.29 | 57.33 | 10.00 | 30.08 | 9.99 |
| R314-basin-6 / comparison | 90.44 | 1.81 | 49.87 | 50.00 | 43.28 | 18.03 |

*Exterior bracket p95 is distance beyond a supported interval along its normal scan.
A missing correctly oriented boundary within the 12px extension receives an explicit
**50px penalty**, not an asserted measured 50px displacement. See the detailed
boundary audit for missing counts. Comparison geography is historically exposed,
not fresh validation. All 40 cores are retained; some are overlapping/correlated.

## First failures, ownership and occlusion

The illustrated candidate is **R314-basin-6**, a diagnostic tradeoff rather than an accepted
reconstruction. It changes 40/40 modal core owners
relative to R306. Fixed R306-owner fractions prevent calling those changes geometry
recovery. Physical centers and a verified ±1/±6/±7 chain remain unknown.

| Frozen core | R306 modal % / index | Candidate modal % / index | Candidate fixed R306 owner % | Best isolated % / its full-visible % |
|---|---:|---:|---:|---:|
| C-1559-0252 | 48.6 / 14 | 40.5 / 17 | 0.0 | 81.3 / 40.5 |
| C-1497-0271 | 84.8 / 0 | 52.5 / 2 | 0.0 | 63.1 / 13.1 |
| C-1477-0290 | 28.6 / -7 | 55.0 / -5 | 18.6 | 92.9 / 18.6 |
| R282-1536-0239 | 78.2 / 8 | 53.3 / 10 | 0.0 | 61.5 / 53.3 |
| R282-1537-0308 | 58.2 / 12 | 75.4 / 14 | 0.0 | 85.2 / 75.4 |
| R282-1459-0316 | 57.3 / -8 | 63.7 / -12 | 0.0 | 95.6 / 11.9 |


For every early core, the ledger retains competing visible owners and up to eight
isolated candidates. When best isolated coverage is poor, changing occlusion alone
cannot restore that material. When isolated coverage is high but full-scene coverage
is low, relative depth/pose/occlusion matters. Neither condition uniquely identifies
camera, helix phase, bead shape or orientation. Geographic progression plots retain
abrupt failures and recoveries; no smooth, convincing 200-bead fit is established.

## What the controlled comparisons establish

1. **Photographic objective:** demonstrated failure mechanism in R313. Dilation can
   buy coverage while worsening known paper and seams. R314 rejects that tradeoff.
2. **Correspondence:** demonstrated confound. R312's unchanged-geometry reassignment
   changed maxima enormously; R314 never calls relabeling a geometric improvement.
   Current core owner changes and competing patch overlaps remain explicit.
3. **Shape and dimensions:** R313's hole parameter changed external rounding. R314
   adds a shared rounded-cylinder exterior with independent radial rounding, axial
   face rounding, thickness and cylindrical thread bore. Bore changes leave exterior
   support and external zero sets unchanged, verified by contracts. Legacy annuli
   remain a separate family. Both produce feasible and failed candidates; neither
   has been identified as the true glass profile.
4. **Orientation / helix / spacing:** coupled camera, phase, registration, minor
   radius, tilt, trajectory-related orientation and periodic spacing/phase fields
   were tested. Broad and local gains retain regional regressions. Existing near-6.5
   winding/count laws are preserved; no independent bead correction is introduced.
   Global turn/count was not continuously refitted, and no mechanical crochet solver
   was developed in this budget. Registration uses the inherited arclength s0 law;
   an independent two-axis image translation was not added.
5. **Packing:** actual solid penetration is distinct from an inconclusive convex
   envelope. All admitted candidates carry full-chain separating witnesses or actual
   solid certification. Failed variants retain penetration points; unresolved cases
   are not called collisions. Positive margins are conditional numerical clearance
   bounds, not measured real gaps or proof that all +1/+6/+7 pairs should touch.
6. **Camera / depth:** first-hit and isolated comparisons expose wrong visible
   surfaces, but no camera calibration or uniquely correct depth ordering is recovered.
7. **Support plane:** a single horizontal plane can be placed below the exact lowest
   solid support. Candidate per-turn lowest-clearance maximum is
   0.6984 source
   units. Floating turns remain; this is no equilibrium claim or calibrated table pose.

The following new controls keep the external envelope fixed while changing the
bore, or revert a selected parameter group. Infeasible combinations cannot establish
an independent photographic preference; parameters interact.

| Parent | Intervention | Actual-solid classification | Development material % | One-body % | Paper % |
|---|---|---|---:|---:|---:|
| R306-2405 | same_external_envelope_simple_bore 0.08 | certified-separation | 90.02 | 69.77 | 0.15 |
| R306-2405 | same_external_envelope_simple_bore 0.25 | certified-separation | 90.02 | 69.77 | 0.15 |
| R313-focused-1 | same_external_envelope_simple_bore 0.08 | certified-separation | 97.21 | 68.39 | 2.16 |
| R313-focused-1 | same_external_envelope_simple_bore 0.25 | certified-separation | 97.21 | 68.39 | 2.16 |
| R313-focused-3 | same_external_envelope_simple_bore 0.08 | certified-separation | 92.02 | 74.02 | 0.35 |
| R313-focused-3 | same_external_envelope_simple_bore 0.25 | certified-separation | 92.02 | 74.02 | 0.35 |
| R314-basin-6 | revert_profile  | demonstrated-interpenetration | not evaluated | not evaluated | not evaluated |
| R314-basin-6 | revert_orientation  | certified-separation | 88.55 | 57.63 | 0.29 |
| R314-basin-6 | revert_placement_camera  | certified-separation | 86.40 | 62.89 | 0.10 |

The bore-only 0.08→0.25 controls leave all six development metric values exactly
unchanged for all three parents. Within these visible configurations, the central
bore is not the cause of the material/boundary failure. This does not identify the
correct exterior profile. Two of three higher-budget unresolved-contact follow-ups
remain unresolved; one obtains an actual penetration witness. No candidate is adopted.

## Connected bright patches and the proper maximum

R289's native maxima and small connected observations are preserved, including
localization sensitivity and diffuse/specular ambiguity. **118
local historical bright observations** are retained with 40/50/60% local-contrast
components; their original measurements are never moved. Predicted components keep
individual peaks, all tied maximum pixels, unweighted and weighted centroids,
near-maximum supports, thresholds and sampling steps. Every sampled local maximum
above the existing 1e-4 numerical floor is also retained, including secondary peaks
below half the bead's global maximum. Overlapping local supports are marked as merged,
not converted to invented distinct physical beads.

| Fixed geometry | Beads with multiple half-global-max patches /200 | Beads with a fainter local maximum | Halfpixel tracked lobes (-20..20) | Largest tracked peak shift px | Unresolved tracking |
|---|---:|---:|---:|---:|---|
| R306-2405 | 7 | 23 | 28 | 3.5355339059327378 | True |
| R313-focused-3 | 7 | 24 | 26 | 3.5355339059327378 | True |
| R314-basin-6 | 15 | 80 | 35 | 1.118033988749895 | False |


Native diagnostics cover all 200 bodies; half-pixel controls use predeclared
−20…20, not a cherry-picked low-error set. Component ordinals are not identities:
tracking uses bead-local peak surface coordinates and records missing, merged and
ambiguous cases. Its numerical motion bounds are not physical correspondence proof.
Observed-patch surface overlap supplies alternative owner lists; optical nearest-error
rematching is not used to certify an identity. Physical adjacency/color do not yet
establish a unique correspondence cohort.

All 811 inherited observations remain in `observation-catalog.json.gz`; 67 lie in
the fixed geographic interval, including 27 historically strong observations. They
are distinct from the 118 R289 component records and are not silently discarded.

The public fixed-epoch entry `correspondence.evaluate_fixed` validates both the
stored assignment map and predeclared cohort, in addition to measurement hashes. It supports several
features on one bead, forbids reusing one predicted lobe for two distinct features,
and computes **maximum Euclidean peak-to-peak displacement** as principal; connected
patch centroid max/RMS/P95 are separate. Missing predictions make the maximum
infinite (JSON null plus `maximum_is_infinite`), never a reduced-denominator success.
Ambiguous observations remain separately listed. The current eligible cohort is
empty, explicitly **not a zero maximum**. No illumination optimization was run;
there is no achieved principal Emax to report. Glass transmission, refraction,
photographic PSF and diffuse/specular separation remain uncalibrated.

## Verification, limitations and stop

Sixteen contracts pass. Independent replay checks 29,236 positions, 86,379 contact
witnesses, 83,952 original-Python rays, all 1,382 valid proposals and 218 stored
penetration witnesses. Complete target rendering contains 994,098 rays across 12
models. Chromium desktop/narrow/offline image loading passes.

[Independent verification](r314/results/verification.json) replays every exported
position and contact witness, stratified original-Python rays (including complete
200-body grids), all reported geometric arithmetic, valid search selection, penetration
points, frozen source hashes, historical preservation, raw pixels and static links.
[Tests](r314/results/tests.log) include independent bore/exterior invariance,
Lipschitz-safe marching for sharp profiles, support gradients, persistence,
serialization-safe ranking, connected/faint lobes, tied maxima, missingness,
assignment immutability, component reorder and merge controls.

A postprocessing variable-shadowing error and a first-run self-link check error
were corrected before delivery; both failed logs and prior sources are preserved
in `results/failures`. They did not alter fitting or photographic measurements.

The delivered scientific gain is a stricter, reviewable measurement/acceptance
protocol and a decoupled shared-solid/connected-peak implementation, not recovered
necklace geometry. The search remains finite and the accepted exterior evidence
incomplete; failure does not prove the real shape lies outside these families.

**Stop for scientific review.** Next, inspect the fixed boundary brackets and the
reference/negative-neighbor isolated-versus-visible comparisons before authorizing
another fit. No automatic R315, adoption, Phase 3 or pattern inference. Keep the
user-supplied GPT-6 Astra High session for review; no `/new` is needed. Scientific
commit/push and total elapsed time are recorded in [delivery](r314/results/delivery.json).
