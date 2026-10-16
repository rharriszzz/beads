# R304 — 350 consecutive top-section positions

[Open the graphical review](review/r304/index.html), or run
`photo2/review/r304/launch.sh`. Ten panels cover 35 consecutive addresses each,
with an untouched photograph, prediction-only view and combined overlay.

**The extended primary does not maintain its initial photographic agreement.**
Errors fluctuate and become appreciably worse in the final upper-right segment;
they do not grow monotonically. Physical collisions also invalidate this primary
as a feasible reconstruction of the whole requested interval. Keep it as an
inspectable forward hypothesis, not an adopted model.

## Construction

The primary is R303 `joint-independent-h1-S1`: radius 1, axial half-height
0.673076, minor radius 2.407217, nominal advance 0.229100 per address,
6.503354 addresses per turn, scale 15.675893 px/radius, elevation 79.707763°,
roll 33.767924°, hole-axis tilt −2.021326°, and the original shared directional
light (azimuth 158.950083°, elevation 72.363222°, roughness 10°).
The physically feasible R303 independent hand− and calibrated hand+ alternatives
are extended separately with their original parameters.

All models have **350 displayed addresses, −20 through 329**, plus 64 guards at
each end: 478 bodies each. The primary axis runs approximately from photo
(1059,358) through the top to (2081,751). Address zero is the fitted **S1**
registration at axis location (1127.467,337.948), not R294 bead zero.
The R294 red crossing (1499.36,271.20) is displayed only as a landmark.

The R293 image reference, stored in `r282/results/centerline.json`, is deprojected
onto one plane using the original R303 orthographic camera. Its nearest station
to the fitted S1 origin establishes the sole arc registration. The exact R303
circular axis is retained within 4 bead-radius units of this origin. A fixed
quintic blend joins it to the unmodified photographic curve by 12 radius units;
the resulting curve is reparameterized by true three-dimensional arclength.
There is no fitting of this splice or any later section. Primary centers at
addresses −16…16 change by less than 5×10⁻⁹ px. The hand− difference there is
0.00011 px, because its larger advance reaches just beyond the preserved circle.

Advance remains `pitch * (1 + spacing*tanh(k/14))`, integrated analytically;
primary `spacing=0.00973232345`. The correction therefore approaches +0.973%
ahead of S1. Phase remains `phase0 + hand*2π*k/turn`, with no panel or landmark
reset. Shapes, camera, pitch, twist, tilt and world illumination stay fixed.
This is the documented small effective stitch correction and conditional global
twist, not a reconstructed string path, measured strain or inferred total count.
The source relation in `beads.pov` remains row advance = 0.975 axial height for
the usual source dimensions; R304 extends the requested independent-pitch model.
No FFT information or constraints enter construction or analysis.

## Photographic comparison and error growth

All suitable saved R299/R276 catalog entries in this interval are recovered,
including unselected entries, plus R257-only candidates. There are **106 distinct
candidates, 41 strong and 39 black**, with 19 R257 cross-references retained at
their original coordinates. Strong, weak, diffuse and possibly merged/broad
candidates are distinguished. The catalog is adequate for visual inspection,
so no new detection was run; it is not a complete reflection or bead inventory.

All original S1 correspondences are held fixed. Outside S1, one global ordered,
one-to-one sequence alignment retains explicit skipped observations and
predictions. Squared spatial error and a fixed 24px gap penalty determine the
path; 12px and 48px controls expose assignment sensitivity. Local S1 projected
order reversals in the hand− model remain unchanged. No new S1 ownership is
invented for previously unassigned observations. Nearest competing owners are
shown only as alternatives, never substituted into the path.

“Confident conditional” requires a strong observation, error ≤8px, at least
8px advantage over every competing prediction, and the same owner in all three
gap-cost paths. **These are not independently verified physical identities.**
The primary has 19 such pairs, 86 ambiguous pairs and one unmatched observation;
23 observation assignments change under the gap-cost controls. It has 125
unassigned predicted reflections, not 125 proven extra real reflections.

Primary results below use only paired **strong** observations. Signed residuals
are prediction minus observation, tangent along increasing photographic arc,
normal to its left. Each row contains 50 modeled positions.

| Addresses | Strong pairs | RMS / median px | Tangent / normal mean px | Paper occupation / colored omission |
|---|---:|---:|---:|---:|
| −20…29 | 8 | 3.11 / 2.51 | +1.03 / −0.74 | 3.5% / 8.9% |
| 30…79 | 7 | 13.84 / 14.97 | −1.67 / −0.21 | 6.3% / 11.6% |
| 80…129 | 5 | 10.85 / 10.48 | −4.81 / −5.04 | 8.6% / 5.7% |
| 130…179 | 4 | 6.78 / 5.39 | −1.71 / −1.72 | 8.3% / 8.7% |
| 180…229 | 7 | 3.66 / 2.70 | +0.93 / +3.13 | 8.6% / 11.6% |
| 230…279 | 5 | 13.99 / 9.57 | +9.16 / +7.93 | 5.1% / 30.5% |
| 280…329 | 5 | 14.10 / 14.16 | +2.11 / −1.85 | 9.2% / 36.3% |

Overall strong-pair RMS is 10.19px primary, 12.53px hand− and 9.54px calibrated
hand+. This does not rank physical plausibility: only hand− certifies the entire
extension. Primary descriptive error slope is +1.83px per 100 addresses, or
+5.18px per 1000 photographic arc pixels. Signed tangent slope is +1.80px per
100 addresses. These are correlated, assignment-dependent descriptive slopes,
not confidence intervals or evidence for a uniquely wrong pitch.

The first substantial deterioration occurs around addresses 30–79, near the
transition from the local fit to the image curve. Agreement later recovers, so
a single gradual error-growth explanation is inadequate. The later bend segment
230–329 deteriorates again, with only five strong observations per 50-position
group. The largest strong-observation gap is 114.37px. Signed tangent displacement
changes sign; it is not a single constant phase displacement. The saved global
paths expose skips and assignment changes, but cannot establish a true integer
jump or rule out a whole-turn slip.

A separate **no-gap ordinal control** pairs successive catalog entries and
predicted reflections after the final S1 anchor without any skips. Its errors
become large, showing how heavily small spatial residuals depend on allowing
missing reflections. The catalog's incompleteness also makes that control
unsuitable for measuring actual pitch error. Consequently, these data show
uneven and ultimately worse photographic agreement, but **do not identify the
rate of error accumulation for a proven physical bead sequence**. Small
locally compatible errors do not establish stable indexing.

## Visible boundaries, centerline and physical failure

All surfaces use the existing rounded annulus and accurate native first-hit,
normal and shadow kernels. Individual visible boundaries are extracted from
the owner raster, including neighboring-bead occlusion and visible internal
holes. Complete pixel-cell edge segments and owner/intensity rasters are saved.
No circles or unobstructed convex outlines substitute for these boundaries.
The primary has 347 visible beads and 230 predicted reflection lobes; all 350
positions, including hidden beads and absent lobes, remain selectable.

The model axis departs from the saved photographic reference by at most 4.63px
in the S1 splice. After the splice it follows that reference to numerical
precision, so there is **no progressive departure of the modeled axis from the
chosen trace**. The trace itself is not an independently calibrated rope axis.
Fourteen eligible saved photographic envelope profiles give group edge MAEs
1.75–4.88px; modeled-minus-observed envelope midpoint errors range −6.75…+7.5px.
These are uncertain paper/material edge proxies, not exact bead boundaries.

Frozen paper and colored-material samples separately test occupation of obvious
background and unexplained material. The final two groups omit 30.5% and 36.3%
of sampled colored material despite remaining on the reference axis. This is
an envelope/phase/occlusion disagreement, not just misplaced highlights.
No color pattern is inferred or fitted.

| Model | Close pairs / separated | Uncertified | Demonstrated penetrating pairs | Minimum certificate objective |
|---|---:|---:|---:|---:|
| Primary hand+ | 1420 / 1391 | 29 | 27 | −0.137846 radii |
| Independent hand− | 1420 / 1420 | 0 | 0 | +0.121301 radii |
| Calibrated hand+ | 1420 / 1414 | 6 | 5 | −0.069538 radii |

A negative separating-plane objective alone is inconclusive. The penetration
counts above additionally use actual annular surface samples inside another
bead's implicit solid. Primary failures include the splice, addresses 20–50,
and the top/bend region 112–176; three unresolved pairs are before the displayed
range. Every bead is retained. The primary/calibrated images therefore describe
invalid physical hypotheses in these locations. These failures depend on the specified curve extension and do not invalidate the original local S1 fit. No repair or new fit was made.
The feasible hand− alternative has weaker photographic correspondence. Among successfully separated pairs, the minimum demonstrated margins are 0.002409 radii primary, 0.121301 hand− and 0.000354 calibrated; these positive subsets do not certify the failed models.

Expanding 64 guards to 96 at both ends changes **zero owner pixels and zero
reflection intensity values** for all three complete display rasters. Extended
contact certificates and failure witnesses are also retained. Camera grazing
rays and shadow uncertainty are explicitly recorded rather than silently
counted as valid surfaces.

## Verification and review

Native replay, half-pixel convergence diagnostics, contact witnesses, exact
visible-boundary checks and preservation results are recorded in
[`verification.json`](r304/results/verification.json). Per-bead half-pixel
centroid/peak differences, disconnected-lobe counts and centroid ownership
are retained separately; threshold sensitivity is not a statistical interval.
Browser results are recorded in [`browser-check.json`](r304/results/browser-check.json).
All three native exports and complete guard comparisons took **16.20s**. The recorded successful analysis pass took about **6s**; verification took **43.75s**, including preservation hashing (33.91s for the three numerical replays and half-pixel checks). A verification implementation mistake repeatedly decompressed an array and was interrupted after approximately **11.09s**; caching fixed it without changing predictions. These recorded passes total about **77s**, well below the approximate ten-minute allocation; development, derived-view rebuilds and browser testing are separate. No optimization evaluations were performed.

Half-pixel centroid changes (median / maximum) are **0.084 / 1.580px** primary, **0.155 / 2.256px** hand− and **0.081 / 1.352px** calibrated, with 2/4/3 marginal-lobe presence changes respectively. All original S1 reflection centroids are preserved within 2×10⁻⁹px. Native replay covers 1,773,046 pixels across the three models; the exact totals are in the verification receipt. All **17,011 protected historical files** are unchanged. Five construction/data contracts and all 30 model/panel browser views pass, including every layer’s raw-pixel invariance, desktop/narrow layouts, offline opening and actual localhost launcher. Windows browser dispatch was mocked; an actual Windows opening is not claimed.

The graphical review is the principal deliverable. Inspect the primary's
transition and final two panels alongside the feasible hand− model before
choosing a next step. No adoption, whole-necklace optimization, physical indexing,
color-pattern inference or Phase 3 follows. **Stop for maker review.**
