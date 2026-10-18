# R319 — the 12px stall is conditional, coupled and numerically noisy

**No local-optimum certificate or excellent reconstruction was obtained. No geometry
is adopted.** The original 22-observation, provisional epoch-2 map is unchanged.
The best diagnostic candidate passing the declared geometry non-regression screen
reduces Emax **11.995236 → 11.824207px** (1.43%; **0.353 photographic diameters**).
The screen permits small stated tolerances; this is not proof of correct geometry.
All candidates still fail absolute geometric readiness. The best reflection-only
candidate reaches 11.695714px but is rejected for boundary/core regressions.

[Compact photographic review](r319/results/index.html) ·
[Every reflection response](r319/results/all-reflection-responses.csv) ·
[Every candidate outcome](r319/results/trial-ledger.csv) ·
[Independent verification](r319/results/verification.json) ·
[Reproduction](R319_REPRODUCE.md)

## Why moving the worst bead transfers the error

The conflicts are measurable. At the R318 endpoint, increasing image y translation
by 1px changes the **linearized error** of conditional 58 by **+0.954px**, but 65 by
**−0.999px**. The same change helps 33 by −0.906px and hurts 38 by +0.537px.
A +0.04rad global phase change likewise changes errors 58/65 by
**+1.070/−1.229px**. A +3° light-azimuth change reverses that pair, approximately
−0.194/+0.201px. These are measured scaled secants, not physical identities or
exact derivatives. Shared translation, phase and light cannot independently move
these reflections. [Four-bead response table](r319/results/worst-four-sensitivities.csv).

That does **not** mean no coordinated correction exists. In the 41-column native
secant model, a one-scale trust box predicts 11.474838px. A supporting-hyperplane
linear-program dual gives the same lower bound to numerical precision; **10px is
unattainable in that affine model and box**. The four-scale box has a lower bound
10.6670px. Other beads become limiting: at one scale, dual weights are approximately
32: .24, 33: .34, 38: .19, 46: .03, 53: .08, 58: .09, 65: .03.
Thus reducing the original four exposes neighboring constraints. These certificates
concern measured affine models only, not nonlinear geometry or all possible models.
[Saved bounds and active constraints](r319/results/linear-target-certificates.json).

An eight-scale model with linearized full-chain separating planes predicts
**9.855956px** for all22. Its actual parameters violate exploratory spacing/phase
bounds. Removing only that numerical rate veto still produces **demonstrated glass
interpenetration**. The below-10 prediction therefore does not survive nonlinear
physical validation. This is stronger evidence than repeatedly shrinking a failed
step, but it is not a proof that another feasible nonlinear direction cannot work.

## 1–3. Search coverage, unexplored dimensions and conditioning

The audit reads **all 9,666 serialized R318 settings and 235 saved Jacobians**,
including failed proposals. It also inspects R312–R317 geometry/evaluation code,
R315's saved sensitivity analysis and R317's twelve saved local matrices. R318
varied exactly **26 scalar coordinates**: fourteen global/light/registration
coordinates and twelve coefficients at compact centers 25,55,85. Its matrices
contained only 8–14 columns at a time, predominantly positive one-sided probes.
All 32-node fields, count=2405, hand=−1, open topology, turn=6.485, camera scale,
perspective, compact widths/locations and inherited compact coefficients remained
fixed. This was extensive local sampling of one family, not broad search coverage.

[Every serialized parameter's actual min/max/distinct count](r319/results/parameter-ranges.md)
and [family interpretations/bounds](r319/results/search-space-audit.json) separate
bounds actually enforced from older `valid()` routines that R318 never called.

| Family | Meaning and units | R318 coverage / important restriction |
|---|---|---|
| Major axis, 32 nodes | Image-normal displacement, photo px; planar spline deprojected through camera | All fixed; ~75.16 addresses/node |
| Distributed phase / spacing, 32 nodes each | Radians / fractional longitudinal rate, integrated and normalized | Fixed; derivative/rate caps 2%, numerical regularization |
| Compact phase / spacing | Radians / fractional station correction | Three new coefficients each; supports 36/70 addresses, centers30 apart; phase5%, spacing2% caps are not measured strain |
| Compact orientation | Tangent–circumferential tilt and inward radial cant, degrees | Three new coefficients each; 20° tilt,12° cant and3°/address combined slope are numerical bounds |
| Camera / registration | Elevation,roll degrees; scale px/unit; perspective inverse units; translation,s0 px | Scale/perspective fixed; camera and deprojected axis coupled |
| Minor helix / topology | Minor radius units; phase radians; turn beads/revolution; count,hand,closure discrete | Phase/minor varied; count/hand/turn/gap/topology fixed |
| Shared rigid shape | Radius units, axial ratio, hole/rounding fractions; optional independent edge/face/bore | Only radius/axial varied; R318 shadow acceleration asserts legacy profile |
| Hole axis / depth | Global tilt/cant, height tilt degrees; trajectory mixing fraction; minor-height fraction | Shared radial cant, height laws and trajectory mixing not varied; no independent major-axis height field |
| Illumination | Shared azimuth/elevation/roughness angular width degrees; inverse distance; source width degrees | Global light searched,144 extra finite/extended controls; no calibrated refraction model |

The serialized legacy `pitch`, `yaw`, `bend`, `strain`, `phase_knots`, `local_bend`,
`local_metric`, `local_turn`, `phase_transport` and `local_phase_bias` do not control
this placement path. `winding` is inactive for the open topology; independent
edge/face/bore parameters are inactive for the legacy profile. They must not be
counted as missing active local freedoms. Tests confirm representative inactive
scalar keys leave centers unchanged. Global constant phase is redundant with a
constant distributed phase. Uniform spacing normalization has a gauge-like mode.

R319 measures **163 continuous coordinates** independently at ±0.25 and ±1 declared
scales: every node/coefficient, formerly fixed camera/helix/orientation variables,
compact centers/widths and shared illumination. Twenty additional bilateral profile
controls cover legacy hole/rounding and independent exterior edge/face/bore, with a
separate exterior parent. Eight discrete/end controls test count±1/±13, opposite
hand, closed topology and seam location. These controls do not refit alternative
families and cannot eliminate them physically. Independent bore changes leave all
22 reflection positions unchanged in these controls; exterior profile does matter.

At quarter scale, 55 coordinates are locally negligible (<.03px scaled vector
norm), 9 active columns pass the declared bilateral/multiscale smoothness screen,
and 99 active columns fail it. “Locally negligible” is not globally inactive.
The 41-column larger-secant matrix has 7/15/27 retained singular directions at
10%/3%/1% relative cutoffs. Distant axis nodes13/14 have cosine .999989;
gap_steps versus axis14 is −.999967; adjacent compact centers26/25 give phase
columns of cosine .997539. These are nearly duplicate local motions, not independent
local shape control. [Matrices, SVD and projections](r319/results/wide-secant-minimax.json.gz).

## 4–8. Nonlinear tests, numerical defects and physical limitations

There are **1,018 primary serialized evaluations**: 948 certified,36 demonstrated
interpenetrations,32 numerical/model bounds and2 unresolved separation outcomes.
All feasible evaluations retain all22 observations and all2405 bodies. Rejected
physical proposals retain exact parameters/failure records; unavailable optical
responses are not filled with fabricated values. Separate controls are not silently
added to this count:29 profile/discrete, five relaxed-rate, four geometry/light,
40 bilateral half-grid directions plus baseline, and correspondence controls.

Native connected half-maximum centroids have sampling discontinuities even when
there is no principal-lobe exchange. A half-pixel lattice makes both translation
columns exactly bilateral in the tested ±.5-scale probes; global phase asymmetry
falls to .12. Other orientation/shape columns remain noisy. The half-grid baseline
is 12.074459px, agreeing with R318's archived control. Using this independent
Jacobian does not remove the conflict: its one-scale prediction is 11.507511px;
that proposal intersects glass. Its half-scale prediction11.642695 becomes
11.918368px but fails seam/core gates.

Every trial saves principal peak/area/ties/secondary-component information. All
per-bead peak shifts are in the CSV; large peak jumps are explicitly diagnostics,
not automatically called lobe switches. Selected final models retain all connected
lobes and half-pixel comparisons. The accepted final maximum shifts by .022858px
under half-pixel evaluation; the largest per-bead centroid shift is .119329px.
No large lobe switch is needed to explain this endpoint's approximately12px error.
Lobe tracking across every discontinuous rejected proposal is not established;
those cases are not forced into a smooth derivative claim.

The improved procedure uses bilateral secants, explicit scaling, SVD, local Euclidean
minimax, actual geometric vetoes, and fixed-normal full-chain support constraints.
New or rotated contact pairs are always checked in the actual nonlinear scene.
At trust1, adding those planes changes a previously intersecting full step into a
certified setting: predicted11.483270, actual11.938970px; its outline gate still
fails. At larger steps, inherited compact rate limits become active. A controlled
relaxation proves these are not physical facts: a spacing rate of2.0041% is feasible
but yields12.113200px; the larger target steps produce actual intersections.
[Rate controls](r319/results/relaxed-rate-controls.json.gz).

Four fresh linearizations at successive accepted states improve11.929187→11.824207.
The selected intervening changes are scale−.04, roughness+1° twice, then compact
spacing coefficient6+.002. These were measured probes, not a claim that every
coupled minimax step worked. The final accepted gains include illumination:

| Frozen geometry / light | Emax px |
|---|---:|
| R318 / R318 | 11.995236 |
| R318 / final light | 12.085218 |
| Final geometry / R318 light | 11.909583 |
| Final geometry / final light | 11.824207 |

These nonadditive controls prevent describing all of the improvement as geometric.
There is evidence of an inadequate derivative/search procedure and conditional
packing/basis restrictions. There is **no demonstrated strict nonlinear local
minimum**, no proof that the mathematical family is incapable, and no independently
verified correspondence chain.

## 9–10. Visible outline and ownership constraints

The evidence is frozen R314/R315 pigment interiors,76 supported color-seam samples
and material-to-paper uncertainty brackets within the original-coordinate patch.
The bracket's entire2–12px localization interval is allowed. Model rays trace actual
visible surfaces with every body present; isolated silhouettes are used only to
quantify occlusion, never compared to a hidden photographic outline.

The new ledger reports modal core support, internal visible boundaries crossing
2px-eroded cores, same-owner claims across supported chromatic separators, and one
body claiming >=25% and >=20 pixels of two **different-color** cores. Same-color
fragments and dark valleys alone never establish separate beads. This conservative
cross-color dual-claim test fires zero times at baseline/final; that is absence of
this particular detected contradiction, not proof of correct ownership. It detects
54 contradictory pairs after deliberately merging all visible owners, and one after
a12px shift; both controls fail. Actual neighboring owner identities/occluders are
saved, but true physical front/back ordering cannot be recovered from every ambiguous
photographic separator.

Every feasible primary trial has an additional **per-body visible-boundary and
occlusion ledger**: visible/isolated pixels, actual occluding owners, boundary changes
and symmetric boundary distances relative to the baseline model. Those latter
distances are model-to-model; they are not mislabeled photographic contour errors.
The photograph supplies only supported partial segments/brackets and positive cores.
[948-model outline ledger](r319/results/per-body-outline-response.json.gz) ·
[Short contradiction ledger](r319/results/geometry-ledger.md).

Of132 settings with a better full reflection maximum, **52 (39.4%) fail geometric
non-regression**. Forty-one of these fail exterior-bracket preservation. The
reflection-only winner11.695714 fails exterior and three individual-core gates.
The diagnostic winner's seam conflicts remain25%; core-crossing fraction changes
15.33→14.78%; material omission9.12→9.40%; bracket p95 **7.0→7.2px**, within the
explicit .5px tolerance. Paper occupation stays0% on these fixed paper samples.
No weighted sum conceals these values. All selected settings still fail absolute
readiness; no candidate is presented as a valid reconstruction merely because it
passes a baseline-relative screen. Exact thresholds/reasons are in the protocol.

## 7,11. Correspondence and genuinely compact patch

The original maps remain immutable. At identical R318-best geometry, a coherent
−6 shift of the provisional51–66 block yields35.564628px; −1/+1 shifts lose one/two
predictions, and several alternatives violate one-to-one assignment at block edges.
The diagnostic single58→52 map gives16.131814px. Internal address differences are
preserved in the coherent block controls; block interfaces remain uncertain.
Observed-support overlap, isolated/full visibility, projected neighbors at±1/±6/±7,
and all reflected positions are saved. Thus body52 occupying the observed point is
important evidence, but does not justify an optical-nearest reassignment. No map
change or correspondence-only score difference is counted as geometry improvement.

The small interval is **27–46 inclusive:20 consecutive conditional addresses,
about3.08 minor revolutions**, with seven reliable retained reflections and all three
pigment cues. Selection maximizes available observations among such three-color
intervals, then uses photo-only localization uncertainty; modeled error never enters.
The complete detected-candidate support audit finds no additional eligible unselected
reflection overlapping this interval. All exclusions and alternatives remain visible.
Physical contiguity is conditional on the provisional map, not newly established.

Its maximum improves **11.986900→11.709021px** while retaining all22 outside guards.
A two-node narrower coherent phase/spacing/orientation basis is tested separately:
20-address support instead of changing all inherited widths. A bounded old-basis
approximation of a .08rad/20-address phase bump leaves .02177rad maximum residual;
this demonstrates limited localization, not measured missing strain. Zero added
fields reproduce the original geometry exactly; orientation-only fields preserve
centers. The new basis's best tested small-patch contact proposal reaches11.561450px,
but its all22 maximum12.257061 and outline regressions reject it. The narrower basis
is not adopted. The patch is not excellent and is **not expanded**.

## 12. Remaining obstacle and verification

The clearest remaining obstacle is obtaining a coherent placement/orientation and
provisional identity hypothesis that explains **both neighboring colored interiors
and opposing reflection vectors while staying nonintersecting**. Finer numerical
sampling fixes a real derivative limitation; it does not solve that coupled physical
and correspondence problem. More random trials near the same point would not answer
it. A targeted physically coherent depth/packing or correspondence hypothesis still
needs independent local evidence; none is asserted true here.

Verification reconstructs22 observed centroids from original RGB pixels, checks all
1018 trial cohorts/maxima, bilateral arithmetic and SVD reconstructions, and replays
five models including the rejected reflection and narrow-field candidates. Independent
support formulas check36,030 full-chain witnesses. Original Python rays check4,630
camera samples and4,630 shadow samples; two unresolved Python camera samples and
sampled uncertain shadow pairs are explicitly retained. Known rays/points/normals and
shadow intensities agree. All five models have zero missing half-pixel predictions.
Eight focused contracts pass. An additional20,856 per-body records satisfy
visible+occluded=isolated exactly on the fixed crop, and20,856 CSV vectors/errors
are independently recomputed against explicit parent trials. Raw pixels, static links and desktop/narrow/offline
Chromium checks accompany the delivery. Historical tracked files and the photo are
unchanged. Initial serialization/review failures are retained rather than concealed.

Start02:35:07UTC Oct18; scientific seal in `r319/results/scientific-seal.json`;
hard deadline03:05:07UTC. [Delivery receipt](r319/results/delivery.json) records
commit/push and independent remote verification. **STOP for scientific review.
No R320, whole-necklace expansion, pattern inference or beads.pov edit.**
