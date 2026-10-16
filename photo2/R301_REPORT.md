# R301 — randomized local inverse geometry

Broad search finds a **shared, locally nonintersecting hand+ candidate** with better reflection predictions: pooled training RMS **8.72→5.98px** and withheld RMS **7.93→5.20px** versus R299, with all 30 observations matched. Against R298, withheld RMS improves **5.86→5.20px**. However, dimensions and material agreement regress, independent solutions disagree and synthetic geometry recovery fails. **Convincing physical reconstruction is not established.** No global count, physical index origin, repeating pattern or production model is adopted.

[Open the graphical comparison](review/r301/index.html) · [Search progress](r301/results/search-progress.png) · [Reproduce](R301_REPRODUCE.md)

## Evidence and construction constraints

The maker clarified that beads per minor turn is nearly 6.5 and essentially constant, with only a small closure twist. The final minimum count preference is **2,000**, superseding interim 6,000 and 2,698 minima. Allowing up to about ten bead positions of twist at 2,000 gives approximately 6.468–6.533; the search uses **6.465–6.535**, constant along each model and shared across sections in the joint fit. Total count is not an optimization parameter. These are construction priors, not a recovered count.

Three automatically selected, geographically separated 104px reference-arc windows each retain ten original R299 photographic measurements. They have different centerline orientations and include black reflections. Each has 7 training and 3 withheld reflections; all weaker/ambiguous measurements remain with weight 0.2. All 810 earlier records, 52 historical selections, R257 cross-references and rejected/uncertain observations remain preserved. Selection used photographic strength, black evidence and geographic separation, never fitted residuals or bead owners. These withheld observations are excluded from R301 fitting but have historical exposure in earlier studies; this is retrospective within-photo validation, not blind new-image generalization.

At the minimum/old approximate count the windows nominally span roughly 23–30 physical positions. Each local model has 25 central addresses plus 32 guard positions on each side. Dense hypotheses can put more than 30 axis positions in the frozen photographic window; this is explicitly recorded, not called a verified 25-bead inventory. Native export additionally checks 64 guards per side. No free per-bead displacement, rotation, light or material is allowed.

The common radius is fixed to one as a unit gauge. The rounded rectangular annulus is revolved about its hole axis and axially stretched; the historical surface is exactly within this family. A planar quadratic centerline, tangent-consistent frames and shared circumferential hole-axis tilt generate all beads. Camera yaw is a planar gauge; elevation and image roll are fitted. The model uses orthographic projection and one shared distant source. Perspective, finite lamps and extra optical degrees of freedom were not added to an already underidentified inversion. Roughness remains 10° in this bounded study.

## Search and positional objective

The bounded search uses scrambled Sobol initialization, population differential evolution, periodic global injections and joint mutation of the geometric/light variables. Both hands and two random seeds are retained independently in every section. The coordinate control starts from the same adapted historical dimensions and pose and receives the same 1,536 candidate evaluations. Accurate refinement retains distinct normalized parameter vectors, not only copies of one winner. Two accurate starts per section/hand each receive 384 evaluations. Reflection-only ablations use the identical initial candidate, seed and 384-evaluation budget as their secondary-constrained controls. The joint fit gives each hand 768 accurate evaluations with common physical/camera/light variables and six local variables per section.

Primary loss uses native-pixel squared distances passed through 576 d²/(576+d²). Hungarian assignment includes 400-weighted-squared-pixel unmatched-observation costs, a 4-squared-pixel unused-prediction cost and a bounded second-component slot costing 64. A bead can own at most two nearby components, separated by at most 12px; no unlimited dropping or duplicate ownership is possible. This sharing heuristic is not an exhaustive enumeration of every merged-lobe hypothesis. Competing assignments and their costs are exported. Withheld assignment cannot reuse owners already consumed by training.

Secondary terms are small penalties for paper occupation, missing colored material, approximate measured bead dimensions and envelope edges. They do not dominate via positive-region containment. Sixteen-pixel material bands are withheld. Existing R298 separator selections do not intersect these small windows; 23 additional image-only dark-valley profiles were frozen separately and used solely for withheld diagnostics, never training. A dark valley is not automatically a physical bead separator.

## Native reflection results

The following rows are chosen by the accurate training score before native withheld evaluation. Baselines use the unchanged historical geometry/light, evaluated anew against the identical local observations and assignment rules; these numbers are not the old fixed-owner R299 table. RMS is for finite matches. Unmatched counts remain explicit and count as infinite for median/p90; a dash therefore need not mean a small error.

| Section/model | Train matched | Train median / RMS px | Withheld matched | Withheld median / RMS px | All p90 px |
|---|---:|---:|---:|---:|---:|
| S1-h-1-accurate0 † | 7/7 | 3.70 / 4.44 | 3/3 | 7.78 / 8.06 | 7.78 |
| S1-h1-accurate0 | 7/7 | 2.31 / 2.71 | 3/3 | 3.90 / 4.96 | 4.04 |
| joint-h-1-S1 † | 7/7 | 6.82 / 7.44 | 3/3 | 8.02 / 10.43 | 13.09 |
| joint-h1-S1 | 7/7 | 3.50 / 3.85 | 3/3 | 4.60 / 4.01 | 5.17 |
| R297-S1 | 7/7 | 8.09 / 9.15 | 3/3 | 3.04 / 7.85 | 13.23 |
| R298-S1 | 7/7 | 8.31 / 8.03 | 3/3 | 5.98 / 5.05 | 9.55 |
| R299-S1 | 7/7 | 5.53 / 6.71 | 3/3 | 5.56 / 5.86 | 9.98 |
| S2-h-1-accurate0 | 7/7 | 6.01 / 5.84 | 3/3 | 4.23 / 6.48 | 9.10 |
| S2-h1-accurate1 | 7/7 | 1.50 / 7.22 | 3/3 | 5.30 / 7.64 | 11.63 |
| joint-h-1-S2 | 7/7 | 6.01 / 5.84 | 3/3 | 4.23 / 6.48 | 9.10 |
| joint-h1-S2 | 7/7 | 5.19 / 7.15 | 3/3 | 5.02 / 6.98 | 9.96 |
| R297-S2 | 7/7 | 7.58 / 10.94 | 3/3 | 5.61 / 6.82 | 15.18 |
| R298-S2 | 7/7 | 10.38 / 11.04 | 3/3 | 5.80 / 7.15 | 12.91 |
| R299-S2 | 7/7 | 8.19 / 9.71 | 3/3 | 8.28 / 7.75 | 12.25 |
| S3-h-1-accurate0 | 7/7 | 3.94 / 4.52 | 3/3 | 6.42 / 8.47 | 8.54 |
| S3-h1-accurate0 † | 7/7 | 5.32 / 8.49 | 3/3 | 10.91 / 14.23 | 18.06 |
| joint-h-1-S3 | 7/7 | 4.05 / 4.78 | 3/3 | 5.48 / 6.81 | 7.06 |
| joint-h1-S3 | 7/7 | 5.43 / 6.44 | 3/3 | 2.82 / 4.04 | 8.29 |
| R297-S3 | 7/7 | 8.00 / 11.10 | 3/3 | 14.92 / 15.13 | 16.31 |
| R298-S3 | 7/7 | 8.42 / 9.25 | 3/3 | 2.10 / 5.12 | 11.24 |
| R299-S3 | 7/7 | 9.37 / 9.43 | 3/3 | 10.02 / 9.70 | 10.86 |

† These three candidates are **not physically accepted** after extending from 32 to 64 guards per side. S1 hand− independent and S3 hand+ independent each have 15 demonstrated sampled penetrating pairs in the extended section; joint hand− S1 has one unresolved pair. Joint hand+ certifies all three 153-position extended sections. Eighteen of the 21 new local exports certify with extended guards. These are finite-section certificates only, never a necklace certificate. Guard extension changes the joint hand− S1 highlight set, with a maximum common-prediction movement of 6.35px; that alternative is rejected. Every failure remains available.

The shared hand+ solution has axial/face ratio 0.593, minor-radius/bead-radius 3.061, pitch/bead-radius 0.276, 6.50374 beads/turn, hole-radius/outer-radius 0.112, rounding fraction 0.948, shared hole-axis tilt −13.64°, camera elevation 62.50°, roll −0.68°, face diameter 23.80px and light azimuth/elevation 49.52°/54.53°. These values are one compatible family, not recovered measurements. It places 32/36/32 model axis positions in the photographic windows, slightly exceeding the original 15–30 target; guard context is therefore essential.

For this shared candidate the full-observation RMS is 3.89/7.10/5.82px across S1/S2/S3 (0.164/0.298/0.245 face diameters). Mean signed tangent errors are +1.88/+2.17/+1.27px, and normal errors −0.55/+0.86/+0.85px. Tangent slopes are −7.11/−8.15/−1.74px per 100px of photographic reference, so a claim of no systematic local drift is unwarranted. Red, yellow and black evidence all has matched predictions, but yellow RMS is still 9.16px in S2.

All color-specific, signed tangent/normal, local-diameter-normalized and unmatched-inclusive summaries are in `results/analysis.json.gz` and the debugger. Signed slopes over these short, sparsely observed spans are descriptive; local reassignment can hide phase slips, so bounded local errors cannot certify full-loop indexing or closure.

## Does the inversion recover known geometry?

[Synthetic geometry comparison](r301/results/synthetic-recovery.png). Native implicit-surface tracing generated known targets; the coarse predictor uses a separate surface quadrature. Four compact runs used 2,048 broad evaluations plus 256 accurate refinements each, with known correspondence and with 1.5px feature noise, a false feature and uncertain correspondence. They ran before the real-photo experiment, during the count clarifications; both regimes and all failed hypotheses are preserved.

| Synthetic regime | Owners | True → recovered axial/face | Training matched | Finite training RMS px |
|---|---|---:|---:|---:|
| before-maker-count | known | 0.58 → 0.69 | 14/14 | 5.71 |
| before-maker-count | uncertain | 0.58 → 0.49 | 14/14 | 6.12 |
| interim-6000-minimum | known | 0.18 → 0.54 | 21/26 | 11.21 |
| interim-6000-minimum | uncertain | 0.18 → 0.21 | 26/26 | 5.33 |

At the exact generating parameters, native predicted coordinates replay with zero positional error. The two-pixel predictor has approximately 0.53/0.73px finite RMS in the two regimes, with one missing thin-case lobe; the coarse predictor has approximately 5.94/1.98px finite RMS, with one/three missing lobes. Thus the cheap forward approximation can reorder hypotheses, and the search itself does not reliably reach a known solution. Allowing unknown ownership can improve the score while concealing wrong physical geometry. This is a failed recovery validation, not evidence that the real photograph is insufficient or that the surface model is universally wrong. It limits every real-photo inference in this report.

## Equal-budget method comparison

| Region / hand | DE seed 3011 | DE seed 3012 | Coordinate control | Best DE beats coordinate? |
|---|---:|---:|---:|---|
| S1 / -1 | 49.09 | 50.92 | 48.62 | no |
| S1 / +1 | 49.16 | 43.42 | 82.03 | yes |
| S2 / -1 | 70.91 | 61.30 | 69.17 | yes |
| S2 / +1 | 70.05 | 63.41 | 48.70 | no |
| S3 / -1 | 75.95 | 76.59 | 87.88 | yes |
| S3 / +1 | 73.59 | 71.82 | 68.77 | no |

Each column has 1,536 evaluations; the two DE seeds are separate experiments, not a 3,072-versus-1,536 budget claim. Broad search beats the coordinate strategy in three of six section/hand comparisons and loses in three. This does not establish a uniformly better search strategy. Exact fixed-compute-time comparisons, including initialization sensitivity, are in `results/analysis.json.gz`; compute-time excludes checkpoint overhead, which is separately recorded.

## Independent geometry and initialization

| Selected family | Axial/face | Minor radius / bead radius | Pitch / bead radius | Beads/turn | Tilt° | Elevation° | Roll° | Face diameter px |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| S1-h-1-accurate0 | 0.43 | 2.39 | 0.22 | 6.53 | -11.54 | 58.83 | 37.66 | 29.50 |
| S1-h1-accurate0 | 0.66 | 3.04 | 0.29 | 6.51 | 2.49 | 83.53 | -27.54 | 23.10 |
| S2-h-1-accurate0 | 0.51 | 3.01 | 0.22 | 6.53 | -1.74 | 66.17 | -30.67 | 24.69 |
| S2-h1-accurate1 | 0.58 | 2.69 | 0.22 | 6.50 | -4.97 | 70.27 | 40.93 | 26.29 |
| S3-h-1-accurate0 | 0.10 | 3.01 | 0.23 | 6.52 | 1.87 | 72.25 | 70.93 | 28.71 |
| S3-h1-accurate0 | 0.65 | 2.99 | 0.28 | 6.51 | -13.27 | 74.09 | -65.26 | 23.00 |

Physical/camera/light parameters are compared explicitly rather than averaged into a supposedly common geometry. The joint fits initialize common parameters from each independent section in turn; each local centerline/phase remains separate. Agreement within the narrowly prescribed turn range is primarily imposed by maker knowledge, not evidence that the photograph recovered that value. Radius and absolute units cannot be identified independently of camera scale. Hole size, roundedness, light direction and axial tilt remain coupled.

## Which photographic constraints help, and why stop?

Reflection agreement improves at the expense of other measured evidence. Relative to R299, shared hand+ S1 bead-extent MAE rises **1.20→5.90px**; S2 envelope-edge MAE **1.80→6.32px**; S3 edge MAE **5.62→11.34px**. Training colored-material omission rises from about **20–21% to 32–33%**. Withheld colored-material omission is **32/45/38%** in S1/S2/S3. The smaller 23.8px face diameter and altered packing can place highlights well while failing to cover visible material. This is a geometric contradiction, not an acceptable trade for a lower reflection loss.

Matched reflection-only ablations leave S1 and S2 unchanged. In S3, dropping secondary constraints worsens native training RMS **4.52→5.17px**, withheld RMS **8.47→9.85px**, and the secondary penalty **9.88→29.12**. The constrained fit therefore helps in that case, but these three controls do not identify a universally sufficient objective. Native dimensions/material boundaries are useful veto evidence; positive containment still must not substitute for reflection geometry.

This step stops because the maker has a new plan and explicitly requested complete closure of R301 with the reasons recorded. The scientific reason not to adopt or expand this reconstruction is that reflection improvements coexist with dimensional/material regressions, initialization/section disagreement, guard failures in several alternatives and unsuccessful known-geometry recovery. A successful synthetic fit at the true parameters shows the optimizer/approximation can fail even when a solution exists. None of this proves the photograph intrinsically lacks enough information. The new plan is not implemented here.

## Measured computational cost

| Resolution | Evaluations | Feasible | Evaluation seconds | Geometry | Contact | Reflections | Assignment | Secondary |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| accurate | 5760 | 4663 | 243.59 | 1.25 | 44.05 | 180.73 | 1.17 | 16.18 |
| coarse | 27648 | 20486 | 462.13 | 6.04 | 76.99 | 351.79 | 6.49 | 19.67 |
| joint-section-calls | 4608 | 3728 | 196.49 | 1.10 | 37.45 | 143.74 | 0.93 | 13.27 |

The coarse surface quadrature is only a screening approximation. Final evidence uses native first-hit rays, surface normals and shadow rays against the actual implicit annuli. Contact screening checks every spatially close pair, including nonadjacent and guard positions, using analytic separating planes for a filled outer envelope. Failure of this sufficient certificate means unresolved/rejected, not automatically demonstrated penetration. The certificate covers only the exported finite section.

The saved timing tables separate evaluation work from checkpoint/driver overhead. Equal-time comparisons use measured candidate-computation seconds, not estimated wall-clock allocation; both equal-evaluation and equal-compute-time outcomes are retained. Checkpoints are atomic every 16 proposals and at graceful termination; uncommitted work after a hard kill is deterministically replayed. Source/evidence fingerprints and a writer lock protect resume. A complete-necklace extension would multiply visibility/contact work and introduce global phase/closure constraints that these local fits do not solve. No scaling benefit or complete-chain feasibility is claimed from simply multiplying bead counts.

## Bounds and limitations

| Parameter | Allowed interval | Actually sampled interval |
|---|---|---|
| axial | 0.08 … 0.95 | 0.080032 … 0.94928 |
| round | 0.3 … 0.95 | 0.3 … 0.95 |
| hole | 0.05 … 0.36 | 0.050025 … 0.36 |
| minor | 1.35 … 3.5 | 1.3509 … 3.5 |
| pitch | 0.035 … 0.4 | 0.035113 … 0.4 |
| turn | 6.465 … 6.535 | 6.465 … 6.535 |
| tilt | -28 … 28 | -27.975 … 28 |
| elevation | 35 … 88 | 35 … 88 |
| roll | -85 … 85 | -85 … 85 |
| scale | 10 … 21 | 10 … 20.998 |
| light_az | -180 … 180 | -180 … 180 |
| light_el | 18 … 88 | 18 … 88 |
| dx | -42 … 42 | -42 … 42 |
| dy | -42 … 42 | -41.993 … 41.988 |
| angle | -35 … 35 | -34.991 … 35 |
| curve | -0.045 … 0.045 | -0.045 … 0.044998 |
| phase | -3.1416 … 3.1416 | -3.1416 … 3.1416 |
| spacing | -0.12 … 0.12 | -0.12 … 0.12 |

The broader search can produce alternative local geometries, but a score reduction is not geometric discovery. Only a handful of independently localized reflections occur per window, while dimensions, camera, illumination and unknown correspondence are coupled. Sparse black highlights are useful surface evidence but supply no complete black-body outline. Training failures cannot alone decide between geometry error, optical displacement, wrong ownership and non-specular contamination. The debugger reports physical-center and predicted-highlight errors for the same owner plus alternative-owner costs, without turning those diagnostics into ground-truth causal labels.

All original R297–R300 scientific files, live feedback and `beads.pov` are protected by a before/after hash manifest. Prior selections and synthetic diagnostics during the maker’s count clarifications remain in `checkpoints`; no real-photo fitting occurred under those interim minimum-count assumptions. The final fit seal precedes native evaluation. No Phase 3, color-pattern inference, adopted reconstruction, automatic R302 or full-necklace optimization follows. **Stop for review.**

## Verification

Nine contracts pass, including exact legacy-shape equivalence, analytic normal/support checks, bounded correspondence ownership, deterministic resume and actual process-kill recovery. Native replay covers all 21 new exports, 1,869 positions, 2,372 original and 4,128 extended contact witnesses. All 16,595 protected historical files are unchanged. Chromium checks all 30 models, raw-image invariance, localhost launch, offline operation and desktop/narrow layouts; Windows browser dispatch is mocked, not claimed physically opened. The metrics-table overflow was repaired without changing science.

[Scientific verification](r301/results/verification.json) · [Browser checks](r301/results/browser-check.json) · [Full analysis](r301/results/analysis.json.gz).

Scientific delivery: `10105ca16b77b41411af2bb56db1bf7220733303`, pushed to `origin/photo-2-strategy-v3` and independently verified with `git ls-remote`. [Delivery receipt](r301/results/delivery.json).
