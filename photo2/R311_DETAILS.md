# R311 — a broader test of existing global parameter basins

**The broader search found missed basins with strong first-error repairs and partial whole-necklace gains. No finalist provides a substantial improvement across the whole circuit; no adoption.** The conclusion is limited to the recorded finite boxes, inherited fields and discrete hypotheses. It is not proof that the existing geometry is inadequate, or that every permitted basin has been searched.

[Photographic review](review/r311/index.html) · [Response/coverage maps](review/r311/maps.html) · [Reproduce](R311_REPRODUCE.md) · [Protocol](R311_SPECIFICATION.md) · [Machine-readable acceptance](r311/results/campaign/acceptance.json).

The strongest partial candidate is **R306-2733-first-errors (trial 663)**: first-error coverage reaches **85.9/81.4%**, reflection RMS improves **0.240→0.231D**, ownership **61.18→61.92%**, and paper occupation **4.52→4.41%**. However, boundary RMS worsens **6.04→6.76px**, and section 13 loses **18.9 ownership points**. This is a promising missed basin with a measured global tradeoff, not a completed repair. [Full partial-result ledger](r311/results/campaign/partial-basin.json).

## What earlier searches actually covered

The audit reads **6,075 original trial records**: R306's 4,054 proposals plus 12 native trials, R307's 1,052, R308's 503 and R309's 454. Checkpoint/source copies and replays are excluded. R306's 1,082 structure-screened proposals did not receive its optical score; its broad numeric envelope is therefore not broad native joint coverage. R306 converted R297 starts by resetting/limiting inherited fields. The unchanged R297 anchor was absent as a principal start from R308/R309. R309 had **58 shared trials**; **all 41 derivative blocks failed the all-column gate**, with zero coupled gradient proposals. Its later work mainly tested coordinate brackets.

| Saved run | Trials | Recorded bounds rejections | Physical/separation rejections | Exact repeated full vectors |
|---|---:|---:|---:|---:|
| R306-cold | 684 | 8 | 15 | 51 |
| R306-initial | 428 | 5 | 16 | 11 |
| R306-main | 2942 | 30 | 16 | 279 |
| R306-native | 12 | 0 | 0 | 4 |
| R307 | 1052 | 10 | 0 | 347 |
| R308 | 503 | 0 | 3 | 184 |
| R309 | 454 | 25 | 1 | 31 |

R307 recorded 355/884 feasible derivative sides with more missing lobes than their base, and 56/65 trust predictions below its acceptance ratio. R308 recorded 233/290 such sides, 23 explicitly unavailable derivative columns, and 51/52 trust predictions below threshold. These are recorded overlapping diagnostics, not exclusive rejection causes.

Repeated vectors can use different objectives or fixed owners and are not automatically wasted computation. Dense clusters of tiny perturbations appear in the actual parameter-space plots. R306 primarily used3px optical screening; most R307 fitting used2px sampling before its native correction. Every feasible R311 discovery proposal uses native1px optics. R308's unknown-ray repair arrived late in its budget. [Full audit](r311/results/audit/coverage.json) records families, starts, optical evaluation/sampling, bound flags, additional-missing-lobe derivative sides and trust-gate outcomes. These causes overlap; no exclusive rejection count is invented. [Per-family ranges](r311/results/audit/ranges.csv) preserve the combinations that a union range hides.

Exact physical intervals are unmeasured for most globals. Phase is periodic 2π; registration is a circuit gauge coupled to indexing; camera elevation above a plane lies in(0,90]°; scale, axial factor and minor radius are positive, further restricted by joint contacts/camera validity. Roll and the unoriented body axis are periodic. Numerical limits are **exploration boxes**, not calibrated physical restrictions. The maker's count minimum is 2,000; principal closed periodic transport uses N/winding. R297 also retains its frozen legacy turn correction. Radius fixes the unit gauge; fixed count plus true total arclength determines mean advance.

| Global | R306–R309 actual union | Earlier numerical box | R311 attempted union | R311 finite box |
|---|---|---|---|---|
| phase | -2.929…5.587 | [-3.141592653589793, 3.141592653589793] | -3.120…3.100 | [-3.141592653589793, 3.141592653589793] |
| s0 | -12.000…18.716 | [-40, 40] | -40.000…41.238 | [-40.0, 40.0] |
| elevation | 51.319…79.708 | [40, 88] | 30.000…88.000 | [20.0, 89.5] |
| roll | 0.000…40.183 | [-70, 70] | -70.000…70.000 | [-90.0, 90.0] |
| tilt | -5.604…2.750 | [-12, 12] | -30.000…30.000 | [-45.0, 45.0] |
| minor | 3.845…4.485 | [3.5, 5.4] | 3.000…6.000 | [2.5, 6.5] |
| scale | 8.238…9.198 | [7, 10.5] | 6.500…11.000 | [5.5, 12.0] |
| axial | 0.775…1.000 | [0.45, 1.12] | 0.451…1.225 | [0.3, 1.4] |

Union endpoints come from different starts/families; they do not imply joint coverage. [Allowed domains and limitations](r311/results/audit/coverage.json) include light, perspective, turn/twist, seam and existing height laws. R311 freezes those quantities and every inherited axis/phase/spacing/legacy correction field within its parent. It tests existing globals broadly, not all existing degrees of freedom. Both handedness controls and both string topologies remain distinct; broad maps prioritize three hand-minus hypotheses. Hand-plus controls are 2,204/closed and 2,002/open and are not exhaustively mapped. [Label provenance](r311/results/campaign/family-labels.json) retains the immutable trial keys while correcting two swapped descriptive aliases in publication names; counts/topologies/physical calculations never changed.

## Executed search and distinct basins

Executed **911 unique parameter/implementation vectors**, 562 certified feasible. Types: `{'basin-sobol': 155, 'map': 464, 'refine': 128, 'sobol': 158, 'start': 6}`. Statuses: `{'bounds-rejected': 2, 'feasible': 562, 'unresolved-separation': 15, 'witnessed-penetration': 332}`. Cumulative search time **50.10min**; initial allowance 40 min, contingent basin-centered4D allowance at most 10 min. Preflight, audit, recovery tests and final dense verification are separate. Broad schedule completed 639/849 planned slots; time-limited blank cells are untested. Exact duplicate evaluations avoided:11. Stop reason: **600-second contingent limit**.

The five pair maps span a full sampled phase cycle, registration −40…40px, elevation 30…88°, roll −70…70°, tilt −30…30°, minor radius 3…6 units and scale 6.5…11 px/unit. Every joint proposal is evaluated directly: invalid intervening states do not block a distant feasible island. Scrambled Sobol designs explore four globals together. Adaptive joint cell subdivision refines distinct whole-score and constrained first-error basins; a contingent four-variable Sobol stage explores selected promising basins. No derivative calculation or missing-highlight veto restricts discovery. Unknown rays never earn paper credit. Missing lobes stay scored.

| Pair | Evaluated planned cells (three principal starts) | Certified feasible |
|---|---:|---:|
| phase/s0 | 84/105 | 72 |
| phase/elevation | 111/147 | 66 |
| roll/elevation | 106/147 | 62 |
| minor/scale | 104/147 | 39 |
| tilt/elevation | 75/105 | 19 |

The response surfaces distinguish rejected cells from unevaluated cells. [Basin ledger](r311/results/campaign/basins.json), [all vectors](r311/results/campaign/trial-vectors.csv), [native trial records](r311/results/campaign/trials/) and [predicted-versus-measured changes](review/r311/predicted-measured.png) survive. Forecasts are weak neighbor/center estimates and never gate evaluation. Failed separating-plane certificates are inconclusive unless original solid surface samples witness penetration. Feasible models with bad photographic scores remain separately labeled.

| Distinct finalist basin | Count / hand / topology | Changed globals relative to its parent | Complete contact certificate |
|---|---|---|---|
| R306-2405-global (trial 796) | 2405 / -1 / open | phase=-1.509 (Δ-1.722); s0=8.900 (Δ+3.184); elevation=56.184 (Δ-4.224); roll=-43.795 (Δ-74.978); tilt=0.336 (Δ+0.349); minor=4.071 (Δ-0.094); scale=8.670 (Δ-0.049); axial=0.930 (Δ+0.086) | 7143 pairs; minimum margin 0.034371units |
| R306-2405-first-errors (trial 163) | 2405 / -1 / open | phase=-1.582 (Δ-1.795); s0=20.000 (Δ+14.284) | 7166 pairs; minimum margin 0.277093units |
| R306-2733-global (trial 43) | 2733 / -1 / closed | minor=4.000 (Δ-0.203); scale=9.500 (Δ+1.095) | 8199 pairs; minimum margin 0.007235units |
| R306-2733-first-errors (trial 663) | 2733 / -1 / closed | phase=0.144 (Δ-2.301); s0=33.771 (Δ+33.771); elevation=55.467 (Δ+2.147); roll=-52.359 (Δ-76.654) | 8190 pairs; minimum margin 0.067869units |
| R309-2733-global (trial 750) | 2733 / -1 / closed | minor=4.078 (Δ-0.125); scale=8.986 (Δ+0.562) | 8199 pairs; minimum margin 0.026550units |
| R309-2733-first-errors (trial 755) | 2733 / -1 / closed | minor=4.328 (Δ+0.125); scale=8.986 (Δ+0.562) | 8199 pairs; minimum margin 0.016844units |
| R306-2204-plus-closed-global (trial 690) | 2204 / 1 / closed | tilt=7.500 (Δ+7.500) | 5623 pairs; minimum margin 0.253738units |
| R306-2204-plus-closed-first-errors (trial 691) | 2204 / 1 / closed | elevation=67.129 (Δ+5.000); tilt=7.500 (Δ+7.500) | 6087 pairs; minimum margin 0.183658units |
| R306-2002-plus-open-first-errors (trial 696) | 2002 / 1 / open | s0=14.250 (Δ+10.000) | 3912 pairs; minimum margin 0.374385units |

Each row is a distinct parameter vector relative to its own unchanged hypothesis; coarse sampled minima/components are not proof of isolated continuous basins. Counts, hands, topology, winding and inherited fields were never merged or relabeled across these rows.

## First-error and adjacent-body comparison

All six original photographic interiors retain every native pixel. At(1480,291), poor isolated overlap diagnoses a different failure from an isolated body hidden by neighbors near(1613,253). Best isolated and best visible owners can differ. The unchanged R297 anchor already explains these two interiors comparatively well, while failing elsewhere. No interior centroid or reflection is treated as a physical center; no physical+1/+6/+7 chain is verified.

A **pure phase/registration move** (trial 163) changes negative overlap 31.7→81.0%, positive overlap 79.0→98.8%, and reference overlap 80.2→97.7%. Its whole-development score is +7.9% relative to baseline (positive is worse). This demonstrates a missed, locally promising joint basin within the existing geometry, while retaining its global cost. [Native before/after figure](r311/evidence/phase-registration-example.png); the complete necklace occludes both crop renders.


| Model | Reference visible% | Negative visible / best isolated% | Positive visible / best isolated% |
|---|---:|---:|---:|
| R297-2337-baseline | 94.7 | 85.7 / 85.7 | 96.6 / 96.9 |
| R306-2405-baseline | 80.2 | 31.7 / 46.5 | 79.0 / 94.0 |
| R306-2405-global | 39.7 | 76.1 / 84.5 | 92.5 / 98.8 |
| R306-2405-first-errors | 97.7 | 81.0 / 81.0 | 98.8 / 100.0 |
| R306-2733-baseline | 92.1 | 67.6 / 67.6 | 36.5 / 98.6 |
| R306-2733-global | 97.7 | 73.0 / 73.0 | 52.7 / 99.3 |
| R306-2733-first-errors | 89.8 | 85.9 / 85.9 | 81.4 / 81.4 |
| R309-2733-baseline | 92.6 | 70.4 / 70.4 | 35.7 / 100.0 |
| R309-2733-global | 95.7 | 74.2 / 74.2 | 43.2 / 100.0 |
| R309-2733-first-errors | 95.2 | 70.2 / 70.2 | 48.6 / 96.9 |
| R306-2204-plus-closed-baseline | 87.5 | 49.1 / 49.1 | 96.4 / 96.4 |
| R306-2204-plus-closed-global | 87.5 | 46.0 / 46.0 | 97.6 / 97.6 |
| R306-2204-plus-closed-first-errors | 92.4 | 58.2 / 58.2 | 97.8 / 99.8 |
| R306-2002-plus-open-baseline | 82.7 | 30.0 / 35.2 | 68.6 / 71.0 |
| R306-2002-plus-open-first-errors | 88.5 | 81.2 / 81.2 | 31.4 / 65.7 |

[Raw/native before-after atlas](review/r311/index.html) and per-model exports retain competing owners, isolated/visible/occluded fractions, reference and adjacent red/yellow bodies, including wholly hidden alternatives. A patch-directed finalist must have whole-development score≤115% of its own baseline and lose at most5 coverage points at the trusted reference; it still must pass every global measurement. Poor-reference local tradeoffs remain in trial records and can seed coupled exploration. No patch was detached or fitted independently.

## Independent whole-necklace measurements

Fixed **D=36.878px** is R309's uncertain B14 contour reference (±6px conservative length uncertainty), not a measured largest bead. Dense metrics use all original positive-interior pixels and both retrospective partitions. Paper/color percentages are means of regional frozen-cue fractions, not fractions of the entire photograph; interior ownership is region-balanced modal coverage, not verified per-bead accuracy. Supported external-boundary metrics use complete native outlines against 16 uncertain photographic contours; other complete bead boundaries are unmeasured. Measurement pathways are distinct but their pixels/evidence are correlated. Reflection associations remain conditional. All 811 catalog observations survive, including weak/missing evidence.

| Model | Reflection RMS / P95 / max(D) | Boundary RMS / max(D) | Interiors% | Paper / color omission% | Missing strong | Fixed-owner penalized RMS(D) / missing |
|---|---|---|---:|---|---:|---|
| R297-2337-baseline | 0.276 / 0.416 / 0.681 | 0.208 / 0.519 | 65.47 | 2.69 / 33.98 | 0 | 0.276 / 0 |
| R306-2405-baseline | 0.247 / 0.383 / 0.486 | 0.135 / 0.353 | 59.98 | 6.84 / 29.94 | 0 | 0.247 / 0 |
| R306-2405-global | 0.251 / 0.398 / 0.481 | 0.202 / 0.513 | 64.63 | 5.88 / 28.43 | 0 | 3.454 / 58 |
| R306-2405-first-errors | 0.253 / 0.390 / 0.461 | 0.170 / 0.451 | 59.91 | 7.08 / 29.92 | 0 | 1.229 / 53 |
| R306-2733-baseline | 0.240 / 0.379 / 0.603 | 0.164 / 0.444 | 61.18 | 4.52 / 31.72 | 0 | 0.240 / 0 |
| R306-2733-global | 0.265 / 0.411 / 0.612 | 0.189 / 0.522 | 65.41 | 10.08 / 24.57 | 0 | 0.493 / 29 |
| R306-2733-first-errors | 0.231 / 0.363 / 0.619 | 0.183 / 0.444 | 61.92 | 4.41 / 30.38 | 0 | 5.602 / 66 |
| R309-2733-baseline | 0.243 / 0.382 / 0.614 | 0.166 / 0.444 | 61.95 | 4.54 / 30.84 | 0 | 0.243 / 0 |
| R309-2733-global | 0.255 / 0.402 / 0.662 | 0.178 / 0.490 | 64.45 | 6.98 / 27.14 | 0 | 0.391 / 15 |
| R309-2733-first-errors | 0.264 / 0.408 / 0.558 | 0.189 / 0.522 | 64.03 | 9.86 / 25.02 | 0 | 0.402 / 15 |
| R306-2204-plus-closed-baseline | 0.286 / 0.444 / 0.485 | 0.188 / 0.610 | 56.54 | 7.70 / 31.79 | 0 | 0.286 / 0 |
| R306-2204-plus-closed-global | 0.286 / 0.438 / 0.524 | 0.183 / 0.584 | 56.93 | 7.64 / 31.18 | 0 | 0.344 / 6 |
| R306-2204-plus-closed-first-errors | 0.282 / 0.425 / 0.515 | 0.204 / 0.500 | 57.83 | 7.67 / 31.64 | 0 | 0.761 / 25 |
| R306-2002-plus-open-baseline | 0.290 / 0.447 / 0.544 | 0.191 / 0.529 | 55.82 | 7.20 / 34.71 | 0 | 0.290 / 0 |
| R306-2002-plus-open-first-errors | 0.286 / 0.460 / 0.553 | 0.202 / 0.531 | 55.88 | 7.24 / 34.79 | 0 | 0.432 / 5 |

Fixed controls retain each parent's original conditional owners and 48px missing-lobe penalties. These prevent a rematching-only decrease from being called recovered geometry; they do not certify those original identities. Free and fixed scores, development/comparison results, P95/max, boundary missingness, color, regional material outcomes and all physical witnesses are in [metrics](r311/results/campaign/metrics/). [Whole-circuit optical plots](review/r311/whole-circuit-reflections.png) expose geographic tradeoffs; nearest-only legacy plots are distinguished from the surface-compatible table above.

The requested first-error interiors enter search directly, including old comparison geography; the reference enters a preservation guard. Their local scores are not withheld. Additional dense whole-circuit comparison measurements are computed after finalist selection, but this is retrospective, partly target-exposed evidence, never a fresh holdout. [Exposure ledger](r311/results/campaign/exposure.json).

The acceptance ledger also separates material/photographic checks from the raw fixed-index control. A fixed-index regression alone cannot disprove better physical placement when identities are unknown. Conversely, reassignment alone cannot improve unchanged native interior ownership and material occupation. [Regional ownership/material plots](review/r311/regional-outcomes.png) expose whole-circuit regressions independently of index labels.

- **R306-2405-global**: fails boundary_RMS_no_point02D_regression, fixed_owners_no_point02D_regression, negative_first_error_repaired_or_preserved, reference_no5pp_regression, reflection_RMS_improves5percent.
- **R306-2405-first-errors**: fails boundary_RMS_no_point02D_regression, fixed_owners_no_point02D_regression, reflection_RMS_improves5percent, whole_ownership_plus2pp.
- **R306-2733-global**: fails background_no1pp_regression, boundary_RMS_no_point02D_regression, fixed_owners_no_point02D_regression, negative_first_error_repaired_or_preserved, positive_first_error_repaired_or_preserved, reflection_RMS_improves5percent.
- **R306-2733-first-errors**: fails fixed_owners_no_point02D_regression, reflection_RMS_improves5percent, whole_ownership_plus2pp.
- **R309-2733-global**: fails background_no1pp_regression, fixed_owners_no_point02D_regression, negative_first_error_repaired_or_preserved, positive_first_error_repaired_or_preserved, reflection_RMS_improves5percent.
- **R309-2733-first-errors**: fails background_no1pp_regression, boundary_RMS_no_point02D_regression, fixed_owners_no_point02D_regression, negative_first_error_repaired_or_preserved, positive_first_error_repaired_or_preserved, reflection_RMS_improves5percent.
- **R306-2204-plus-closed-global**: fails fixed_owners_no_point02D_regression, negative_first_error_repaired_or_preserved, reflection_RMS_improves5percent, whole_ownership_plus2pp.
- **R306-2204-plus-closed-first-errors**: fails fixed_owners_no_point02D_regression, negative_first_error_repaired_or_preserved, reflection_RMS_improves5percent, whole_ownership_plus2pp.
- **R306-2002-plus-open-first-errors**: fails fixed_owners_no_point02D_regression, positive_first_error_repaired_or_preserved, reflection_RMS_improves5percent, whole_ownership_plus2pp.

The earlier mechanism was restrictive: limited shared global trials, derivative-gated coupled proposals, coarse structural rejection and repeated local neighborhoods were not a broad native basin test. R311 tests a wider finite design and retains distant feasible islands. A lower weighted score or strong local repair alone does not answer the central question affirmatively. Remaining unsampled combinations, frozen fields/light, discrete starts and finite-map resolution limit any negative inference.

## Verification and stopping point

Five scope/recovery contracts pass, including real SIGTERM/resume and a process exit after trial publication but before checkpoint update. Independent original-Python verification checks **36566 positions, 102635 spatial contact witnesses, 560584 native rays, 338795 optical rays and 2040274 native boundary segments**. Original local isolated controls, normalized residual arithmetic, raw photograph/atlas pixels and exact frozen fields pass. 20668 prior tracked files are checked; historical science is unchanged. [Verification receipt](r311/results/campaign/verification.json). Browser/launcher checks and remote-delivery status are recorded separately, never implied by this numerical receipt.

**Stop for maker review.** No geometry adoption, new bead shape, arbitrary local correction, Phase 3 or automatic R312. Review the first-error/global tradeoff and coverage gaps before choosing any next experiment. Keep the current model/session for review; no `/new` is needed and no model switch is required.
