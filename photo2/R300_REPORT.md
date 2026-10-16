# R300 — approximately stable magnitudes, unresolved signed bias and indexing

**The saved reflections are compatible with approximate local geometric placement
around the necklace, but do not establish stable physical indexing over the entire
circuit.** Error magnitude does not progressively increase. Signed regional trends
remain, particularly in the R298 primary and R299 phase candidate. The proposed
join is poorly observed. Retain the approximate common-light model; further fitting
for absolute reflection precision is not justified. **The existing optimizer is not
ready for another whole-necklace run addressing the remaining structural problems.**

[Review and plots](review/r300/index.html) · [Reproduce](R300_REPRODUCE.md) ·
[Complete analysis](r300/results/analysis.json) · [Residual CSV](r300/results/residuals.csv)

Run `photo2/review/r300/launch.sh`. The interactive residual plot opens selected
observations in the unchanged R299 debugger, including its original R298 tab.
R297's debugger remains linked. Historical 3px/5px labels in those frozen viewers
are historical R299 criteria, **not current requirements**.

## Full-circuit evidence

All 19 saved native model/source exports, 52 observations, frozen owners and
competing owners are retained. Main summaries use the same 45 stronger candidates;
seven ambiguous yellow mixtures remain in separate all-observation results. Peaks,
centroids, all three light types, color subsets and unambiguous-owner subsets are
exported. Nothing is rematched to reduce error.

Position is the original photographic reference's arclength, starting at the bead-zero
reference and proceeding in increasing-index direction: one circuit is 9,235.59px.
This provides the **same geographic coordinate for every family**, independently of
its count or deprojected station parameter. Prediction minus observation is resolved
into the directed local tangent and normal `(-t_y,t_x)` in image coordinates. Using
each model's own tangent changes the three principal parallel slopes by only
0.03, 0.07 and 0.003px/circuit. Diameter normalization reuses R299's local projected
face-diameter convention; it is a conditional body scale, not reflection width or
an independently known physical diameter.

| Family, saved directional light | Predictions /45 | Finite median px / diameters | Parallel slope | Normal slope | Magnitude slope |
|---|---:|---:|---:|---:|---:|
| R297 hand− closed, N2337 | 45 | 10.53 / .39 | −3.18 | +0.19 | +0.60 |
| R298 primary hand− open, N2438 | 44 | 12.06 / .40 | −6.76 | +7.91 | −2.48 |
| R299 phase candidate, same family | 45 | 10.50 / .37 | −9.66 | +8.06 | −4.81 |
| R298 hand− closed, N2337 | 43 | 9.00 / .32 | +1.71 | −3.36 | −0.41 |
| R298 hand+ open, N2709 | 45 | 9.71 / .33 | −2.86 | −2.54 | −2.86 |
| R298 hand+ closed, N2709 | 44 | 9.74 / .35 | −3.14 | −5.90 | −3.84 |

Slopes are descriptive least-squares changes in **pixels per full circuit**, not
observed endpoint differences. Medians here use finite predictions; missing values
remain missing, never zero. This differs from R299's missing-as-infinity rank
convention, especially for its 43-prediction model. No new accuracy cutoff is used.

R297 and the opposite-hand open family have the least combined systematic trend
among the fully predicted directional families. R298 hand− closed also has a small
parallel slope but two missing predictions and stronger sensitivity to geography.
This is **not a unique geometry/hand ranking**: each family has its own previously
frozen local correspondence and fitted shared light. On the common 42 predicted
observations, parallel slopes for R297/R298-primary/R299 are −0.75/−5.71/−7.86;
the primary comparison persists without selectively dropping its missing case.
Across directional/finite/extended sources, hand+ open slopes are −2.86/−2.94/−0.33,
versus −6.76/−6.79/−5.24 for the R298 primary. No new light was fitted.

## Offsets, regional bias and actual accumulation

A global translation is insufficient: removing the mean image residual reduces
RMS only 10.27→10.23px (R297), 11.47→11.06px (R298), and 11.77→11.55px (R299).
The R299 mean is (+1.84,+1.32)px, much smaller than its typical residual.

R299's signed trend deserves attention. Its parallel slope is −9.66px/circuit;
Theil–Sen gives −9.94, and omitting any one occupied geographic bin gives
−12.74…−7.47. A 1,000-resample spatial-bin bootstrap gives −20.25…−1.19.
These are **sampling-sensitivity ranges, not calibrated physical confidence
intervals**. The corresponding R297 and R298 ranges are −13.61…+7.29 and
−16.77…+2.27. With only 15 occupied bins, uncertainty is substantial.

The R299 pattern is not a steadily growing error: early-bin parallel means reach
+8.7/+12.2/+9.2px, middle bins move near zero, bin12 reaches −5.3px, then bin14
returns to +7.8px. Magnitudes decrease weakly rather than increase. Black candidates
show a particularly strong parallel trend: −19.72px/circuit, versus red −4.10 and
yellow +3.16. Thus this is not merely yellow diffuse contamination. Restricting to
R299's ten unambiguous-owner cases leaves a −12.64px/circuit slope, but seven are
black and they cover only seven bins; this is not independent confirmation.

Changing the circuit origin across 16 cuts changes R299's fitted parallel slope
from −9.95 to +9.75; starting at its actual index seam gives +6.10. A circular
regional pattern and an unresolved seam reset can both produce this behavior.
**Origin sensitivity does not disprove drift.** It prevents interpreting one fitted
slope as a recovered count correction. Orientation harmonics explain 19.8% of
R299's image-vector variance in sample but only 5.1% relative predictive improvement
when leaving out geographic bins. Adding linear progression reduces that predictive
improvement to −2.5%. Bend-only and phase-only descriptions add little transferable
explanation. Neither a camera correction nor accumulating spacing error is isolated.
All coefficients, color results and regional means are retained.

Local parallel displacement divided by centerline advance per index gives R299
−3.82…+4.05 **index-equivalent units**, with a −2.66-unit/circuit trend. Its median
axis advance is 3.82px/index. This is not a measured integer error: a reflection can
move within a bead, and the +1 center vector also winds transversely. Consecutive
changes and their cumulative sum are exported; the sum telescopes to the difference
from the first reflection and supplies no independent evidence of accumulated
error. Summing location residuals themselves would manufacture accumulation.
There is no verified chain of adjacent identities from which to measure actual
cumulative indexing. A whole-turn slip can remain hidden by locally compatible
owners even though R300 never rematches them.

## Coverage and the proposed join

The 45 stronger observations occupy 15/16 equal photographic bins, with 1–7 per
occupied bin. The longest empty arc is **637px / 6.90% of the circuit**, increasing
to 1,063px when the R298 primary's missing prediction is included. Many modeled
sites between observations are unconstrained. The 35/45 ambiguous owners in the
R298/R299 primary are retained. A separate exhaustive reference-projection audit
finds the nearest distant branch at least 351.6px farther away, so the geographic
ordering itself is not being confused at a nearby return.

Actual index seams lie at 48.92–49.16%, **not at bead zero**. R299 has three stronger
observations in the 3% arc before its cut and none in the 3% after. The nearest after
is 5.20% / about480px away. Widening to ±6% gives only 3 versus1 observations and
an after-minus-before parallel change +0.37px; at ±10%, 5 versus5 give +1.75px.
These broad averages cannot exclude a sharp discontinuity in the unobserved interval.
R297's slightly different cut falls between two close reflections; its ±3% contrast
is −8.75px (2 versus1 observations), changing to −3.44px at ±10%. Moving the cut
changes which side owns those observations. Neither family has a proven join.
Saved endpoint/phase mismatches and all full-chain certificates remain explicit.

## Two bounded causal controls

R299 changed common phase .69→.54rad and roughness10.25→13.25°. We evaluated exactly
the two crossed combinations at native resolution with the same light direction,
all 52 observations, ownership-49, and all other geometry fixed. No search occurred.

| Phase / roughness | Finite centroid median | Parallel slope px/circuit |
|---|---:|---:|
| .69 / 10.25° — saved R298 | 12.06 | −6.76 |
| .69 / 13.25° — crossed control | 12.01 | −6.77 |
| .54 / 10.25° — crossed control | 10.61 | −9.51 |
| .54 / 13.25° — saved R299 | 10.50 | −9.66 |

**Phase, not roughness, causes most of this increase in systematic signed bias.**
It helps typical absolute error but is not an established structural correction.
Both unchanged geometries independently recertify all7,262 nearby pairs, with
minimum margins .262455/.251223 source units. Their saved native dimensions,
material, boundaries, transverse profiles and photographic contradictions apply
exactly; no geometric change was hidden by the optical control. These controls
justify stopping reflection optimization, not choosing a new correction.

## Remaining structure and next parameters

| Independent retrospective comparison | R297 | R298 primary | R299 phase |
|---|---:|---:|---:|
| Axial extent MAE, 4 visible contours, px | 3.99 | 2.34 | 2.34 |
| Native transverse width MAE, 26 profiles, px | 12.23 | 5.12 | 5.42 |
| Common edge MAE, px | 4.15 | 2.13 | 1.98 |
| Separator MAE, px | 3.05 | 5.34 | 4.45 |
| Paper-proxy occupation, % | 3.45 | 8.35 | 8.46 |
| Sampled positive-region containment, % | 62.57 | 56.73 | 59.45 |

1. **Axial width and +1 geometry:** retain the evidence for thinner axial proportions
   (.700→.582 thickness/face), but address shared helix phase and longitudinal
   rate/phase transport jointly with independently visible neighboring banks and
   separators. A good single bead extent does not certify its +1 neighbor. Existing
   conditional +1/+6/+7 vectors are exported, not relabeled as observed neighbors.
   Current reflections cannot identify a count correction separately from ownership.
2. **Centerline:** keep the explicit planar axis and camera image rotation in the
   structural model. R298 improved native common-edge error; R299 normal residuals
   correlate only .048 with nearby common-edge residuals (36 reflections linked to
   31 eligible profiles within96px). That weak, dependent association supplies no
   specific new axis displacement. Inspect both material edges through bends;
   neither their midpoint nor a highlight is a measured axis. No new out-of-plane
   deformation, elevation or perspective correction is justified here.
3. **Transverse width:** retain separate minor-radius and bead-face scale controls.
   Widening improved the rope envelope but worsened independent paper/material and
   separator constraints. Do not undo the measured width evidence to chase a
   reflection score. Resolve shared placement/occlusion conflicts while checking
   those constraints around the full circuit.

The unchanged R249 FFT peaks provide additional geometric disagreement. Mean
optimistic reciprocal-vector mismatch in resolution units is1.55 (R297),1.47
(R298 primary),1.55 (hand− closed),1.37/1.36 (hand+ open/closed). R297 and the primary
still fail T4-Y/T5-V at about3.2 units. Unassigned peaks, visible latitude and local
unrolled-surface approximations prevent hand/count identification; the slight
opposite-hand preference agrees with retaining that alternative. Fundamental-only
summaries are also saved; no peaks were reselected and no lighting explains them.

The standalone `phase2_autofit.py` still instantiates **R297** geometry/objectives.
It does not integrate R298's image rotation, 16-node axis calibration or independent
dimensional/profile objective, and it has no R300 signed-reflection diagnostic.
Its checkpoint/restart machinery remains useful, but a larger unchanged run would
not address this task's structural constraints. Next development should integrate
those shared geometric controls with material/separator preservation and full-chain
contact, retaining the approximate light and fixed-owner drift audits. Validate
that integration with bounded controls before another whole-loop run. No such
optimizer extension or large run is undertaken here.

Eight targeted contracts, deterministic analysis replay, 104 native crossed-control
reflection replays, exhaustive geographic-frame checks and browser checks accompany
the delivery. All16,599 protected prior files remain byte-identical. The first CSV
export failed on null vector fields; its source/log are preserved, and the schema
repair changes no numerical results. Full receipts are in `r300/results`.
No Phase3, repeating pattern or reconstruction adoption. **Stop for review.**
