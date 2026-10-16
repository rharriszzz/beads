# R306 — automatic full-circuit reconstruction

R306 delivers an executed, restartable whole-circuit workflow and four physically
certified hypotheses. **An overall improvement in photographic consistency is
not established.** The native-training winner improves several dimensional and
boundary measures, but retains serious material failures and comparison
regressions. It is a conditional reconstruction, not recovered physical truth.

Launch [the interactive review](review/r306/launch.sh), or open
[the offline viewer](r306/results/campaign/review/index.html).
[Reproduction](R306_REPRODUCE.md), [parameters](r306/results/campaign/model-parameters.json),
[complete comparison](r306/results/campaign/comparison.json), and
[computation ledger](r306/results/campaign/computation.json) accompany it.

## Achieved model and physical feasibility

The primary, candidate **2840**, has **2,405 bodies, hand−, an open string**, and
one closed planar geometric axis. All **7,166** spatial close pairs certify
separation, including nonlocal approaches and the open ends. The minimum
independently evaluated separating margin is **0.277876 source units**, about
**0.1557 bead radii**; this is a conservative support margin, not an exact nearest
surface distance. Every body participates in contact and visibility queries.
Ten bodies have no native visible samples and remain in the model.

The unchanged R293 photographic reference, stored in R282's centerline file, is
9,235.59 px long. The fitted axis projects to 9,260.19 px, departing from that
reference by median/max 2.81/8.37 px at modeled stations. One periodic spline has
32 adjustable normal-displacement nodes. Numerical true-arclength inversion uses
16,385 samples. The storage position and tangent gaps are zero; there is no
circular splice, registration restart, or phase/index reset. Geometric closure
does not assert a physical join.

The mean advance is 0.471558 source units; the shared rate is 6.485 beads/turn,
with 0.8558 extra turns relative to 6.5. Smooth spacing corrections are bounded
between knots to ±2%; periodic phase-rate corrections also stay within ±2%.
The fitted axial/face ratio is approximately 0.5913, camera elevation 60.41°,
and reference face diameter 31.12 px. These coupled quantities are conditional.
The historical 0.975 height/advance relation is not imposed. Out-of-plane freedom
was not added without independent supporting evidence.

| Retained R306 hypothesis | Count | Hand/string | Native training objective | Strong reflection RMS, all circuit |
|---|---:|---|---:|---:|
| Primary 2840 | 2405 | − / open | 8.086 | 9.08 px |
| Alternative 1857 | 2204 | + / closed | 9.646 | 10.53 px |
| Alternative 2665 | 2733 | − / closed | 10.209 | 8.83 px |
| Alternative 2433 | 2002 | + / open | 10.760 | 10.69 px |

All four certify. The lower reflection RMS of 2665 does not overcome its worse
combined training geometry/material result. Neither count, hand, nor string
topology is identified uniquely.

## Common photographic comparison

Five historical full-circuit alternatives are frozen and re-rendered with the
same evidence and measurement definitions. No historical geometry is refitted.
The table uses the retrospective comparison bands: 69 strong reflections,
four uncertain bead contours, 26 eligible envelope profiles, and the common
geographic material samples. Region containment here uses the search's bounded
samples per region; complete native support pixels are reported separately.

| Model | Reflection RMS | Visible-boundary MAE | Envelope-width MAE | Colored omission | Paper occupation | Region containment |
|---|---:|---:|---:|---:|---:|---:|
| R297 | 9.82 px | 5.83 px | 12.23 px | 34.03% | 3.45% | 62.57% |
| R298 primary | 8.80 px | 6.49 px | 5.12 px | 30.08% | 8.35% | 56.73% |
| R299 primary | 9.35 px | 6.01 px | 5.42 px | 30.08% | 8.46% | 59.45% |
| **R306 primary** | **10.02 px** | **5.51 px** | **6.92 px** | **29.58%** | **7.80%** | **57.51%** |

Compared with R297, comparison bead-extent MAE improves 3.04→2.04 px, but
separator error worsens 3.05→5.55 px. Across all **447 original frozen regions**,
complete native containment falls **65.60→60.27%**. The 1,543 frozen patches
improve 78.76→82.12% mean containment. Relative to R298, boundary error improves,
but envelope width, bead extent, separators, and comparison reflection RMS
regress. This is not a no-worse global reconstruction.

The comparison cases were exposed in prior studies and R306 qualification.
They are not fresh or independent validation. Current finalist comparison
outcomes were computed only after the native-training selection seal at
**2026-10-16 21:32:43 UTC**. See the
[exposure record](r306/results/campaign/comparison-exposure.json).

## Correspondence, residuals, and remaining failures

All 811 catalog observations retain their coordinates and provenance, including
all 316 R305 cases. Of 269 stronger observations, all are matched at the selected
24 px gap cost: RMS **9.08**, median **8.51**, p90 **12.94 px**; signed tangent/normal
means are **+0.16/−0.03 px**. There are **84 confident-conditional and 185 ambiguous**
strong assignments. All 542 weaker observations remain ambiguous. Another 1,132
predicted lobes have no assigned catalog observation; this does not imply extra
or absent physical beads.

Forty-nine strong assignments change under the gap-cost controls. A 12 px cost
reduces RMS to 7.71 px by leaving 49 observations unmatched; that is not an
improvement. For the same-count initialization, free matching improves
10.07→9.08 px, whereas retaining its mathematical owners produces **10.93 px and
11 missing predicted lobes**. Changing the open cut also affects this control.
These are not verified physical identities, and the free-matching gain cannot
be presented as geometric recovery.

The original starting-red supports remain problematic: old R305 indices −1 and
0 have only **12.0% and 52.1%** on their current reflection-assigned bodies;
all visible bodies together cover 84.6% and 77.5%. At the old crossing 103,
assigned coverage improves from R305's 37.4% to **80.2%**. These are uncertain
interior supports, not complete contours. The preserved geographic cohorts
30–79, 230–329, 760–859, and 910–959 have current strong RMS
9.27/5.08/7.77/8.32 px, with only 6/10/12/4 strong observations respectively.
Their current indices are independently assigned.

Errors fluctuate and recover: common sections 2→3→4 have RMS
6.13→12.01→7.91 px; section 3 also occupies 16.6% of paper samples.
Sections 7→8 recover 11.07→6.65 px while colored omission rises to 43.6%.
Descriptive tangent/normal slopes are −0.06/+3.20 px per circuit, and magnitude
slope +0.85 px per circuit. These do not demonstrate physical index drift.
Twelve two-sided phase/shape/camera/light/axis/spacing controls give coupled,
partial effects rather than a unique cause. Saved FFT and +1/+6/+7 relationships
remain explicitly uncertain diagnostics, not verified neighbors or count proof.

## Executed campaign and limits

The workflow reuses R297 checkpoint transactions, R298 material/dimension
measurements, R299 native first-hit optics, R302-style grouped sensitivities,
and R303–R305 starts and diagnostics. Search uses grouped robust evidence,
hard contact rejection, coarse reflections, native material queries, overlapping
smooth regional corrections, discrete count/cut alternatives, and global
reconciliation. No independent section axes or per-bead displacement fields exist.
Gross silhouette/background penalties exceed the maximum reflection reward.

| Stage | Proposals | Actual elapsed fitting time |
|---|---:|---:|
| Exploratory, archived source | 428 | 588.92 s |
| Main, seed 306, warm starts | 2942 | 3601.77 s |
| Independent, seed 307, cold starts | 684 | 900.64 s |
| Final native refinement | 12, eight distinct parameter sets | 175.51 s |

Aggregate fitting time is **5,266.84 s / 87.78 min**; main and independent runs
overlap in wall time. There are 2,541 eligible scored proposals, 1,082 structural
screens, 47 physical rejections, 43 bound rejections, and 341 duplicates in the
three substantive search stages. Saved rejected trials contain 5,176 sampled
penetrating pairs, repeated across trials. Actual proposed counts span
1,996–3,010 inside the allowed 1,800–3,200 range; the search does not establish
an exhaustive count optimum or warrant expansion from boundary pressure.

The exploratory stage's uniform envelope weighting was corrected to use stored
uncertainties before the main run; its source and outcomes remain archived.
Main/independent scientific sources stayed frozen. Native ranking evaluated
20 candidates in 289.19 s, full exports took 204.55 s, and residual controls
25.35 s. The native refinement did not improve the incumbent. The cold run's
best native objective was 9.217 versus 8.086 for the longer warm run; this is
initialization/budget sensitivity, not an equal-time method comparison.
Final native processing peaked at 1,212 MiB RSS; search peak RSS was not measured.

The fixed annular hole/rounding profile, planar axis, bounded camera/count ranges,
incomplete photographic catalog, uncertain contours, and unknown ownership
limit the result. There is no inextensible-thread reconstruction or physical
posterior. The preserved R293 curve is a spatial prior, not calibrated truth.

## Verification and handoff

Eight contracts pass, along with real SIGTERM, restart, post-write crash recovery,
and exact 43-proposal scientific replay. Candidate archives restore byte-exactly.
[Independent verification](r306/results/campaign/verification.json) passes for
**21,975 positions, 62,487 contact witnesses, 180,000 native rays, 178,416 exterior
probes, and 17,910 support replays**, in 108.51 s. Doubling arclength integration
changes projected centers by at most 0.000000788 px. At predetermined sampled
locations, 168 common lobes change by median/max **0.108/2.906 px** on the
half-pixel grid, which adds two marginal lobes. Primary native rendering records
726 uncertain camera rays and 58 uncertain shadow pairs; these are retained.
Verification/review rebuilding peaked at 2,382 MiB RSS.

[Chromium checks](r306/results/campaign/browser-check.json) pass nine models at
81 locations, with real recentering, variable limits, native picking, plots,
raw invariance, both axes, desktop/narrow/offline operation and the actual
launcher. Windows dispatch is mocked, not an observed Windows browser opening.
All 16 gallery illustrations load; every raw panel matches its original photo crop.
The [final preservation audit](r306/results/campaign/preservation-final.json)
checks all 17,192 pre-existing files: 17,188 byte-identical and four additive
handoffs, with zero changed historical science files. Commit and independent
remote verification are recorded in [the delivery receipt](r306/results/delivery.json).

**Another unchanged optimization campaign is not yet justified.** The next
useful change would need to address the unresolved visible-surface/ownership
and material contradictions with controlled structural tests, rather than
rewarding additional rematching. The best achieved alternatives are delivered
for inspection, without production adoption. Stop after verified delivery;
no automatic R307, Phase 3, or pattern inference.
