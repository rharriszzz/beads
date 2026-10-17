# R309 — competing whole-necklace measurements

**No convincing whole-photograph improvement under the predeclared component, worst-error and regional checks.** The experiment ran automatically on Python/compiled CPU code for 19.79 fitting minutes after a 45.2s preflight. Native reevaluation of already completed finalist settings adds 69.6s, before comparison; no new proposals. It retains the historical alternatives and every failed trial. No Phase3 or color-pattern inference.

[Interactive viewer](../../../review/r309/launch.sh) · [Geometric error dashboard](review/science.html) · [JSON summary](analysis-summary.json) · [Reproduce](../../../R309_REPRODUCE.md).

## One photographic length

**D=36.878px**, the longest major-axis/Feret chord among16 independently digitized R298 visible contours, B14 at(550.375,602.75). Each end is uncertain by3px, so the conservative length uncertainty is±6px. This is a fixed reference, **not an established maximum over every photographed bead**. No fitted bead dimensions or pixel areas determine it. The [original-photo/endpoints image](../preflight/D-reference.png) and all16 measurements are retained. All linear results use this identicalD; area measures are percentages.

## Common outcomes

Each distance cell is **pixels / bead-reference diameters**. Strong-reflection distances are Euclidean observed-coordinate to predicted0.5-peak-centroid distances; smooth fitting intensity is a separate surrogate. Boundary distances cover both directions against16 uncertain external observed contours, using the complete modeled visible silhouette at final evaluation. Internal hole edges lack independent photographic annotations and remain unmeasured; actual holes remain visible in the viewer. Other bead exteriors remain unmeasured. Individual distances, maxima locations/IDs, color groups, uncertainty counts, training/comparison and missing cases remain in the full residual files. Paper/foreground percentages average frozen cue fractions over geographic bands; ownership averages observed regions, not pixel area. Boundary sample counts are correlated points across16 contours. All comparison evidence was exposed historically.

| Model | Reflection RMS | Reflection max | Reflection P95 | Boundary RMS | Boundary max | Boundary P95 | Ownership% | Paper% | Foreground omitted% | Missing strong |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R309-reflection | 8.84/0.240 | 22.26/0.604 | 14.21/0.385 | 6.04/0.164 | 16.38/0.444 | 11.42/0.310 | 61.28 | 4.53 | 31.61 | 0 |
| R309-boundary | 9.06/0.246 | 17.80/0.483 | 14.25/0.386 | 5.07/0.137 | 13.00/0.353 | 9.57/0.259 | 60.23 | 6.80 | 29.87 | 0 |
| R309-ownership | 9.79/0.265 | 17.35/0.471 | 15.25/0.413 | 7.75/0.210 | 19.77/0.536 | 13.31/0.361 | 60.88 | 8.63 | 28.04 | 0 |
| R309-balanced | 8.96/0.243 | 22.63/0.614 | 14.09/0.382 | 6.12/0.166 | 16.38/0.444 | 11.60/0.315 | 61.95 | 4.54 | 30.84 | 0 |
| R309-global-control | 9.03/0.245 | 17.82/0.483 | 14.25/0.386 | 5.03/0.136 | 13.00/0.353 | 9.56/0.259 | 60.25 | 6.79 | 29.86 | 0 |
| R309-reflection-zeroheight | 8.84/0.240 | 22.27/0.604 | 14.34/0.389 | 6.05/0.164 | 16.38/0.444 | 11.43/0.310 | 61.29 | 4.53 | 31.61 | 0 |
| R309-balanced-zeroheight | 8.89/0.241 | 22.63/0.614 | 14.18/0.384 | 6.09/0.165 | 16.29/0.442 | 11.56/0.314 | 62.06 | 4.67 | 30.79 | 0 |
| R306-primary | 9.11/0.247 | 17.93/0.486 | 14.14/0.383 | 4.97/0.135 | 13.00/0.353 | 9.44/0.256 | 59.98 | 6.84 | 29.94 | 0 |
| R306-alternative-2665 | 8.87/0.240 | 22.24/0.603 | 13.98/0.379 | 6.04/0.164 | 16.38/0.444 | 11.41/0.309 | 61.18 | 4.52 | 31.72 | 0 |
| R306-alternative-1857 | 10.56/0.286 | 17.88/0.485 | 16.38/0.444 | 6.93/0.188 | 22.51/0.610 | 14.01/0.380 | 56.54 | 7.70 | 31.79 | 0 |
| R307-primary | 9.07/0.246 | 17.80/0.483 | 14.25/0.386 | 5.06/0.137 | 13.00/0.353 | 9.55/0.259 | 60.22 | 6.79 | 29.88 | 0 |
| R308-primary | 9.03/0.245 | 17.82/0.483 | 14.25/0.386 | 5.03/0.136 | 13.00/0.353 | 9.56/0.259 | 60.25 | 6.79 | 29.86 | 0 |

The balanced candidate's reliable maximum is **22.63px / 0.614D**, observation C-0314-1551 at(314.96,1550.41). The absolute matched catalog maximum is **23.42px / 0.635D**, C-1019-2846 at(1019.81,2846.51), classified weak/diffuse/uncertain. There are269 reliable observations and1 unmatched catalog observations in this model. Missing observations have no measurable positional distance: they remain counted and penalized, never zeroed or silently removed. Physical identities are conditional even for reliable reflection locations. The preflight's old `uncertain_correspondences` field measures close alternative margins only; final tables count all unverified physical identities separately from close alternatives.

Balanced candidate by reliable reflection color (pixels / D; all physical owners conditional):

| Color | N | RMS | Maximum | P95 | Missing |
|---|---:|---:|---:|---:|---:|
| black | 200 | 8.79/0.238 | 16.63/0.451 | 13.87/0.376 | 0 |
| red | 35 | 8.96/0.243 | 15.54/0.421 | 14.64/0.397 | 0 |
| yellow | 34 | 9.92/0.269 | 22.63/0.614 | 15.80/0.429 | 0 |

## Controlled objective comparison

All objectives use the same starts and shared probes, including2405/hand−/open and2733/hand−/closed;2204/hand+/closed and R307/R308 are also preserved. Remaining allowances are equal; cache reuse and actual branch seconds are in computation.json. Single-emphasis objectives retain a small material/missingness cost; balanced includes all four. Fourth-moment tails emphasize large reliable errors while exact maxima remain independent acceptance quantities. All local spline/phase/spacing fields stay frozen. There are no regional optimization variables or independent bead motions.

Component-improvement counts versus R306: reflection 3/5, boundary 4/5, ownership 2/5, balanced 3/5. **boundary** has the largest count (ties and magnitudes remain in the tables), which is descriptive rather than proof of best reconstruction. Combining measurements does not establish a globally superior model. A low mean with large residual maxima remains incomplete. Most balanced-versus-primary gains come from selecting the already-retained2733 family. Against that R306 alternative, balanced reflection RMS worsens 8.87→8.96px and boundary RMS 6.04→6.12px; ownership rises 61.18→61.95%.

Fixed R306-family owner controls expose the cost of reassignment (pixels / D):

| Objective | RMS | Maximum | P95 | Missing |
|---|---:|---:|---:|---:|
| reflection | 8.87/0.240 | 22.26/0.604 | 14.24/0.386 | 2 |
| boundary | 9.05/0.245 | 17.80/0.483 | 14.15/0.384 | 2 |
| ownership | 25.08/0.680 | 48.74/1.322 | 37.70/1.022 | 38 |
| balanced | 8.94/0.243 | 22.63/0.614 | 14.32/0.388 | 5 |

The campaign's largest measured fixed-control displacement is 48.74px / 1.322D, reliable-location observation K-2299-1896 at(2300.74,1895.86); its physical owner is conditional. These controls do not assert that R306 identities were correct. They show why low rematched errors are not identity recovery.

At the required(1110,336) location, mean positive-interior ownership improves **52.81→69.09%** and reliable reflection RMS **0.288→0.180D**. This location was never optimized separately. The50-body before/after atlas still shows overextended lower boundaries; this local gain does not represent the entire circuit.

## Four possible causes

1. **Correspondence / phase drift.** Full-cycle phase and registration response curves, global turn/count alternatives, signed tangent/normal circuit plots and fixed-owner controls were tested. Errors fluctuate; recovery alone is not accumulating index drift. No verified adjacent-owner chain supports unwrapped physical phase, so integer slips remain explicitly unresolved. All periodic trials and alternative assignments survive.
2. **Numerical reflection instability.** Native/original centroids agree exactly, and finite-source shadow intensities agree to machine precision. Changing threshold0.25→0.75 changes baseline strong training RMS only 8.778→8.755px. Half-pixel sampling changes it 8.757→8.778px. But perturbation derivatives can change sign and lose lobes. Unthresholded overlap does **not** eliminate visibility discontinuity. Gradient steps are rejected when local linearity fails; bounded coordinate brackets remain. R308's corrected unknown-ray treatment is used from the beginning.
3. **Top-to-bottom variation.** Left/right photo-half residuals are compared at the same six height bands. Global linear minor-radius, linear/quadratic orientation, perspective and finite-distance shared lighting are tested separately in the shared pool and jointly in small parameter blocks. The balanced fit uses a 2.94% minor-radius gradient per normalized image height and 1.00° linear tilt, with zero quadratic tilt/perspective and directional lighting. These modest whole-photo laws remain conditional; image-height trends cannot uniquely separate physical geometry, camera and ownership. The finite source never becomes per-bead lighting.
4. **Inadequate combined objective.** Four competing objectives are fitted, then all are measured against all outcomes. Their disagreements, ownership conflicts, largest errors and geographic regressions are explicit. Final supported external-boundary distances use whole-body native outlines and exclude unannotated internal holes; fitting's smaller all-visible-edge contour windows remain separately labeled in the residuals, avoiding a hidden claim of complete observed boundary evidence.

Height ablations hold fitted globals fixed. R309-reflection: retaining height terms changes reflection RMS by +0.002px, boundary RMS by -0.002px, ownership by -0.008pp and paper occupation by +0.000pp. R309-balanced: retaining height terms changes reflection RMS by +0.072px, boundary RMS by +0.029px, ownership by -0.112pp and paper occupation by -0.132pp. These changes do not establish a material photographic gain from height variation. Fixed-owner derivative predictions agree in direction with native bracket outcomes for 80.5% of nonzero comparisons; 0 gradient proposals passed the local numerical gate. The gate required every column of a block to be reliable; therefore this run tests bounded coordinate refinement, not a successful coupled Gauss–Newton method. The saved matrices do not prove that every derivative direction is unusable.

## Physical construction, performance and limits

The balanced full model has 2733 physical bodies, hand-1, closed string, and one periodic geometric centerline distinct from the photograph. All8199 spatial close pairs certify, minimum support margin0.188827 source units. Full native visibility includes every body; the +1/+6/+7 predictions are conditional, not independently measured bead identities. All811 catalog observations survive.

Executed454 native trials. Peak fitting memory424.6MiB; finalization/independent checks541.4s separately from fitting, including the ranking audit above. Browser and subsequent segment/report audits are additional verification, not fitting. The standalone program schedules probes, rejects unstable gradients, checkpoints/resumes, exports and verifies without AI optimization decisions. It deliberately uses one numerical process to keep the20-minute aggregate fitting allowance interpretable.

The principal unresolved obstacle is simultaneous visible-body ownership, complete boundary placement and optical correspondence under a nonsmooth native visibility model. The controlled measurements constrain explanations but do not establish unique physical indexing, projection or lighting. See causes.json for the test/outcome ledger and acceptance.json for each failed gate. Keep historical baselines; no adoption based on weighted loss. Stop after verified commit/push.
