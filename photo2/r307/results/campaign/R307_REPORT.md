# R307 — faster guided fitting, measured photographic limits

**No: R307 does not establish a substantially better photographic reconstruction of the entire necklace.** It executes
20.00 minutes of fitting versus R306's 87.78 aggregate minutes,
retains a physically feasible full necklace, and delivers the best achieved
native-training candidate. Small objective gains do not overcome the remaining visible-body failures and photographic regressions.
The baseline remains preserved; no production adoption, Phase 3 or pattern follows.

[Launch review](../../../review/r307/launch.sh) · [Offline viewer](review/index.html) ·
[Reproduce](../../../R307_REPRODUCE.md) · [Before/after](review/before-after.png) ·
[Complete metrics](comparison.json) · [Acceptance checks](acceptance.json).

## Required location and the objective defect

At R306 −101, (1110.23,336.04), fresh original-kernel ownership and all saved
viewer boundary segments agree exactly. The isolated projection has **591 pixels**;
only **169** remain visible and **422** are hidden by neighbors.
Pixel stair-steps are raster sampling; larger cutouts include modeled occlusion and the annular hole. It is
not a display error. The raw crop also shows the lower modeled row extending
into background. Yellow denotes selection, never photographed bead color.
[Isolated/visible/observed diagnostic](../../evidence/R306-minus101.png).

R306 sampled24 pixels per region, measured contour distances mainly at polygon
vertices, used a .35-weighted reflection term, and omitted local ownership and
reflection residuals from its sensitivity vector. Those measurements could
reward material/envelope averages while tolerating bodies spread across several
photographic interiors. A contact certificate cannot detect that mismatch.

Within90 pixels of the required location, complete positive-region modal coverage
changes **58.27% → 57.57%**.
Strong nearest-assignment RMS changes **10.62 → 10.68px**.
These are the same photographic supports, not the same conditional indices.
The images and [individual supports](required-location.json)
retain competing owners. No independently measured complete external contour
exists for every bead in this crop; interior coverage is not silhouette truth.

## Common photographic measurements

The following are identical historical comparison evidence and legacy metric
definitions, except coherent ownership uses all nonreflection interior pixels
(an unweighted mean of modal fractions; confidence weights affect fitting). These cases were exposed previously;
**they are retrospective comparisons, not fresh independent validation**.

| Model | Legacy visible boundary MAE px | Dense coherent ownership | Strong reflection RMS px | Paper occupation | Envelope width MAE px | Separator MAE px |
|---|---:|---:|---:|---:|---:|---:|
| primary | 5.65 | 56.56% | 10.10 | 7.80% | 6.81 | 5.59 |
| R306-primary | 5.51 | 56.62% | 10.02 | 7.80% | 6.92 | 5.55 |
| R297 | 5.83 | 62.57% | 9.82 | 3.45% | 12.23 | 3.05 |
| R298-primary | 6.49 | 57.59% | 8.80 | 8.35% | 5.12 | 5.34 |
| R299-primary | 6.01 | 59.33% | 9.35 | 8.46% | 5.42 | 4.45 |

The new bidirectional boundary metric applies a3px uncertainty band before
averaging dense boundary distances. Its numerical values cannot be compared
directly with legacy vertex MAE. New reflection associations include compatible
positive-surface evidence; legacy nearest-only scores above remain separate.

| Model / evidence | Dense modal ownership | Banded boundary forward/reverse px | Region-balanced paper | Compatible-owner reflection RMS px | Missing strong lobes |
|---|---:|---:|---:|---:|---:|
| R306-primary / development | 61.11% | 1.16/1.56 | 6.58% | 8.76 | 0 |
| primary / development | 61.45% | 1.21/1.60 | 6.53% | 8.67 | 0 |
| R306-primary / comparison | 56.62% | 2.54/3.12 | 7.60% | 10.06 | 0 |
| primary / comparison | 56.56% | 2.64/3.13 | 7.59% | 10.15 | 0 |

The explicit acceptance checks record **1 component failures**
and **0 large regional regressions**. Distributions,
worst-decile means, all32 geographic regions, and good/median/poor ownership
quantile examples are retained. Low-reflection/high-body-error regions are
flagged automatically. The gallery includes the required location and historical
problem cohorts; it is not a selection of only attractive fits.

## What was implemented and executed

Positive interiors use up to256 spatially distributed original pixels per region
in fitting and every original pixel at final evaluation. Qualitative accepted
regions carry full coherence weight, compact automatic interiors half weight,
and possible same-color mergers .12 weight. These are engineering uncertainty
weights, not verified single-bead labels. Every region still contributes positive
material evidence. Red/yellow conflicts and preserved separator-bank mergers test
the reverse mapping; same-color masks without separation evidence are not forced
to be distinct bodies. Background cues and uncertain external contours remain
separate from positive interiors, highlights, and complete isolated projections.

Residual vectors include per-region ownership, material/background contradiction,
dense two-sided visible-contour error, separator mismatch, envelope edges, and
signed tangent/normal reflection displacement under one shared light. Reflection
outliers use a Huber tail rather than disappearing; missing lobes incur a48px
penalty and remain in the denominator. Native training acceptance disallows
additional missing assigned lobes and substantial structural deterioration.

Measured finite differences drive damped block Gauss–Newton and bounded line
search. All32 geometric-axis,32 phase and32 spacing coefficients participate,
alongside shared shape/camera/phase/light parameters. Global derivatives are
two-sided; local derivatives are forward with a backward feasibility fallback.
Every trial retains the entire coherent chain for occlusion and hard contact
screening. No independent bead shifts, curve splices or phase resets are added.
Fields retain R306's bounds and true geometric arclength. Cache reuse is limited
to unchanged geometry inputs and fixed photographic structures; local spacing
can affect global arclength, so unaffected residuals are not assumed unchanged.

Executed **1052 trials**, **37 complete numerical blocks**,
and **13 native accepted improvements**. Small accepted
finite-difference steps are retained alongside coupled proposals; they are not
all Gauss–Newton successes. The full Jacobians, singular values, right vectors,
step predictions, actual reductions and rejections are saved. Strongest measured
couplings include local_spacing:28 / local_spacing:27 (+0.999); local_spacing:25 / local_spacing:24 (+0.999); local_spacing:23 / local_spacing:22 (+0.999); local_spacing:27 / local_spacing:26 (+0.999); local_spacing:1 / local_spacing:0 (+0.999). These scaled responses are not statistical ranks
or confidence intervals. No broad new count search was needed or performed;
four R306 count/hand/topology families remain available with earlier feasible
R297/R298/R299 controls.

## Speed, physical validity and limitations

Compiled marching preserves the existing shape,450-iteration limit and tolerances.
At the full R306 start it reproduces all **1943 native lobes exactly**.
Original versus compiled trace timings were 0.282s versus
0.135s for62,795 rays. Full compiled native prediction took
5.13s. Two-pixel/native trial ranking correlation was
0.893; it **did not select the same best small perturbation**.
The initial .8-correlation-only gate was inadequate: native best-quartile recall was .5. After 17.13 minutes the first stage stagnated; the remaining 2.87 minutes used native sensitivities. A scheduling defect also grouped equal coefficient numbers despite different geographic origins. Both decisions and all earlier source/state/Jacobians are preserved in the explicit source transition. Geometry, evidence and objective weights did not change.
The corrected gate requires correlation .9, best-quartile recall .8, and no extra
missing assigned lobes before using a coarse predictor. Native checks protected
accepted models throughout. Corrected blocks project phase/spacing knot stations
to photographic geography before combining them with axis coefficients.


| Evaluation type | Calls | Median seconds | Total seconds |
|---|---:|---:|---:|
| initialize | 4 | 4.491 | 17.90 |
| linearization-base | 38 | 1.007 | 41.87 |
| sensitivity | 898 | 1.008 | 970.83 |
| Gauss-Newton | 69 | 1.010 | 68.93 |
| native-acceptance | 42 | 1.959 | 81.42 |
| correspondence-control | 1 | 4.930 | 4.93 |

Cumulative fitting time includes sensitivities, physical gates, native acceptance
and checkpointing. The preflight benchmark adds an estimated 28.71s, or 20.48 minutes including profiling; timing provenance is in computation.json. Final export, post-seal diagnostic controls,
verification and browser checks are additional work, not hidden fitting runs.
Fitting peak RSS was **389.9MiB**; finalization peak was
**2822.5MiB**. The fitting-time ratio to R306 is
**0.228**. Initialization from R306 supplies substantial
prior work; this is not a cold-start speed comparison.

The primary has **2405 bodies, hand-1, open string**,
a closed periodic geometric axis, and **7166 certified close pairs**.
Independent minimum support margin is **0.260692 source units**.
Every body, hidden surface, weak observation, missing lobe and ambiguity is retained.
Native/half-pixel centroid changes at prespecified observations have median 0.109px and maximum 5.646px, with 3 extra marginal half-pixel lobes. These sampling effects limit interpretation of tiny optical gains. True-arclength refinement is recorded in verification.

The immediate demonstrated obstacle is **native, jointly compatible body ownership
and geometry**, not insufficient evidence proved by this experiment. Most of this campaign used an inadequate approximation gate and geographically misaligned blocks. The corrected 2.87-minute stage did not improve the primary; this is not a full-budget test of the corrected method.


The smallest remaining scientific test is whether a native coupled step can
improve fixed-owner visible interiors and their independent boundary/background
constraints together at the required location while preserving the rest of the
circuit. Existing same-color mergers, sparse dark-body boundaries and uncertain
physical identities complicate that test; this run does **not** prove that new
maker labels are necessary. Frozen-owner shape/phase/spacing/axis/camera controls
have partial, competing effects and do not establish a unique physical cause.
No further fitting is authorized automatically by this negative result.

## Verification and stopping point

Six scientific contracts and real SIGTERM/resume/publication-recovery tests pass.
Independent original Python verification checks all exported physical positions,
complete spatial close pairs, native ownership samples, full support denominators,
required-location pixels, **138480 primary boundary segments**,
and **361900 dense evidence rays**.
The original photograph and historical scientific files are preserved.
The [verification receipt](verification.json) records
17570 protected start-of-R307 files.
The [browser receipt](browser-check.json) records the actual
UI checks: eight models at80 locations, geographic model switching, overlap/competing-owner controls, raw invariance, desktop/narrow/offline operation and the actual launcher. Windows browser dispatch is mocked, not physically observed.
An initialization shadowed-name defect was fixed before fitting; source/log retained.

Deliver the achieved candidate and unchanged baseline for review. Stop after
verified commit/push. No automatic R308, further campaign, Phase3 or adoption.

Fixed initial fitting owners: RMS 8.757 → 8.732px, missing 0 → 0. Correspondence refresh trials: 0.

R306's original nearest-owner control: initial RMS 9.084px; final fixed RMS 9.053px on 267 surviving lobes, with 2 missing. RMS including a24px penalty for each missing original-owner lobe is 9.254px. The surviving-only decrease is not a complete fixed-owner improvement; these remain conditional mathematical owners, not physical identities.
