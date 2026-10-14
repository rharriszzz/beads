# R279 — independent neighbor discovery and blind local prediction

**Neither prerequisite is established.** The fresh photographic pipeline fragments
bodies, misses neighbors, and understates localization uncertainty. The local geometric
search produces many incompatible predictions; none of its fixed-shape, limited-pitch
constructions passes the contact check. Do not grow an arrangement from these results.

[Evidence/reproduction index](review/r279/README.md) ·
[21-anchor overview](review/r279/real/anchors-overview.jpg) ·
[synthetic results](review/r279/synthetic-summary.json) ·
[packing sections](review/r279/packing-sections.png)

## Independence and inputs

The implementation is isolated in [r279](r279/PROTOCOL.md). It does **not** reuse any
R275/R278 observation, reviewed coordinate, manual ownership answer, numbered chart,
±1/±6/±7 correspondence, centerline, historical fit or warm start. Excluding R278's
historically initialized spline/camera avoids an unresolved provenance dependency.
Earlier reports/code were inspected to identify exclusions, not to select patches,
rank candidates, establish correctness, or select a hand.

| Input | Permitted use and provenance |
|---|---|
| `beads-photo-2.jpg` | Original pixels, Pillow EXIF orientation; native decoded RGB/HSV and encoded-RGB luminance proxy. No old calibration or palette. This is not ICC-managed physical radiometry. |
| `beads.pov` | Only the original `bead` macro is extracted; no pattern, photograph coordinates, fitted camera or construction identities. Roundedness .8, half-height .7 radius, hole radius .14 radius. |
| `photo2/bead_placement.py` | Pure `Rope` radius and independent analytic annular surface sampler. No historical surface-fitting module is imported. |
| Supplied construction principles | 6.5 beads/turn; ±1/±6/±7 alternatives; intended radius; source row-spacing formula. |
| New synthetic scenes | Independent seed 279014, randomized phase, roll and palette; both hands, three inclinations and two light/specular conditions. Physical indices and membership rasters stay outside inference. |
| Oracle pair | Provider exposes exactly two anonymous visible-body masks, centroids and image peaks, selected by visible area then image distance. No physical index, hand, camera, phase or remaining memberships. |
| Third/fourth evidence | Independent automatic observations, read for scoring only after the corresponding prediction file has been written and hashed. |

[Source hashes](review/r279/source-manifest.json), [environment](review/r279/environment.json),
[frozen protocol](r279/PROTOCOL.md), and [freeze audit](review/r279/audit.json) record the
inputs and versions. Ground truth is read by separate generator/evaluator code, never
by `photographic.py`, `geometry.py` or `predict.py`. The generator's camera validation
and membership-only oracle are separate from inference. Evaluation is an explicit
command after all inference outputs exist. This is an auditable code/API separation,
not an OS security sandbox hiding files from the process owner.

## Preliminary geometry checks

The intended radius is exactly `.96*4*sin(pi/6.5) = 1.784536980648071`.
The unchanged legacy default remains 2.1109157489. Local axial increment is
`.65*2*radius*1.05/6.5 = .374752765936095`. Changing hand reverses minor winding
while leaving axial traversal fixed; tests exercise both signs and 1+6=7 closure.
The forward model is a fresh straight-centerline limit, not a global necklace fit.
A fixed 29-site context supplies nearby occluders; these sites are not a grown,
fitted or recovered 29-bead arrangement.

The Python implicit surface agrees with the existing analytic surface sampler to
floating-point precision. Independent POV renders use the literal hole-bearing macro.
On 96,300 audit rays from the final 12 scenes, all 96,236 resolved ownership results
agree exactly with POV; 64 grazing rays remain unknown. An initial `look_at` camera
convention mismatch was caught before neighbor evaluation; those renders are preserved
under `failed-camera-control`. Explicit direction/right/up vectors fix the mismatch.
No surface or camera parameter was adjusted to improve neighbor-label scores.

## Test 1: definition, methods and frozen photo sample

“Nearest” means Euclidean distance between **visible-body area centroids** in the
image plane. Synthetic truth uses the full independently rendered visible surface.
The real-photo interiors only estimate that representative; they are not full bodies
or physical centers. Synthetic nearest distances within 2 pixels are ties. A true body
must expose at least 50 synthetic pixels to enter evaluation; this visibility cutoff
is explicit, not a completeness claim.

| Method | Evidence and ranking | Main limitation |
|---|---|---|
| A: detection point | Euclidean distance between sigma-2 local brightness-feature coordinates | Forces a baseline answer; a second peak on A can win. |
| B: body support | Native watershed-interior centroid distance, support spread and peak offset; penalty for potentially shared body | Watershed regions are not established identities. Partial interiors bias centroids. |
| C: multicue | B plus native line valley, hue difference, supported-pixel separation and persistence at three scales | Correlated/weak cues; penalties do not establish independent bodies. |

All candidates retain distances, uncertainty intervals, line-valley strength, hue
separation, possible-same-body flag and minimum supported-pixel distance. B/C return
competing candidates when their uncertainty intervals overlap. Those intervals are
engineering estimates, **not calibrated confidence intervals**. The eight closest
feature observations form the candidate pool; a missed or ninth candidate cannot win.
Candidate lists and abstentions are preserved, not retrospectively filtered by truth.

Minimum distance between supported interiors is reported separately as surface
proximity. It is an upper bound on full visible-surface proximity only when the
interiors are pure and correctly assigned. Synthetic full-mask comparisons are in
[surface-distance-evaluation.json](review/r279/surface-distance-evaluation.json).
Touching surfaces need not have a unique nearest centroid neighbor.

The corrected detector produces 1,714 **observations**, not beads. Twenty-one anchors
are selected before neighbor prediction by support quality and spatial farthest-point
sampling, cycling seven each from learned red/yellow/neutral appearance classes.
All lie on the necklace in the overview; this visual check does not verify ownership
or adjacency. No anchor was replaced based on its predicted neighbors.
The first six frozen anchors supply the real Test 2 pairs.

Each [raw/annotated crop](review/r279/README.md#real-photo-cases) shows the anchor,
nearby interiors, candidate numbers/IDs, method ranking, distance interval and
same-body warning. [Coordinate records](review/r279/real/coordinate-types.json.gz)
separate the sigma-2 feature location, all brightest native support pixels, interior
centroid, and explicitly unknown physical center. Highlights are not center labels.

On the real photograph A makes 21 forced proposals; B and C each return 20 ambiguous
cases and one single proposal. **There is no real-photo accuracy statistic.** The
synthetic failures below give no basis for treating either single proposal as reliable.

## Synthetic Test 1 results

The final 12 POV photographs contain 293 bodies exposing at least 50 pixels; the
pipeline detects 139 distinct qualifying bodies in 159 observations, including 17
extra same-body observations and three low-purity/background observations. These
are scene totals, not independent estimates of general accuracy. One scene has zero
detections. Only 59 of 72 planned anchor slots meet automatic eligibility; the other
13 are explicit availability failures, not removed successful trials.

| Method | Correct top rank / 59 | Same-body top rank | Wrong-body top rank | False/low-purity top rank | Ambiguous | Correct single answers / all single answers |
|---|---:|---:|---:|---:|---:|---:|
| A | 15 | 8 | 33 | 3 | 0 | 15 / 59 |
| B | 15 | 7 | 34 | 3 | 48 | 1 / 11 |
| C | 17 | 7 | 32 | 3 | 47 | 1 / 12 |

The multicue top-rank increase is small and does not establish reliability. Its
remaining single-answer errors are two same-body, seven wrong-body and two false
candidates. Abstention helps expose uncertainty but does not repair detection.

Interior localization has median error **7.18 pixels** across 156 qualifying
observation/body comparisons; only **36.5%** of errors lie inside the declared radius.
For large visible bodies the median error is 8.04px and coverage 26.4%, versus 4.91px
and 78.3% for medium visible bodies. The fixed 13px support aperture truncates large
bodies, contributing to this failure; reflected/occluded interiors contribute too.
These bins measure visible area, not a causal isolation of occlusion.

A's correct counts by true pigment are red 2/12, yellow 8/29 and black 5/18.
The higher-specular/light condition yields 5/23 correct versus 10/36 in the other
condition; lighting and pitch are confounded in this small design. Same-color scenes
still have mostly wrong or ambiguous answers. Full color, hand, pitch, lighting,
visibility and same-color breakdowns survive in the numerical evaluation files.
No threshold was tuned using those labels. In particular, bright neutral highlight
holes can be excluded by the foreground rule, and black detections remain fragile.

## Test 2: prediction discipline and results

For every proposed AB pair, the solver tries both hands and signed 1/6/7 assignments
with identical grids: 12 phases × five viewing inclinations × six assignments,
**360 starts per hand**. Scale bounds derive from A/B support areas; image-only
foreground PCA supplies a broad tangent cue. Translation, in-plane rotation and scale
initially align physical-center projections to the observed centroids. This is only
an initialization proxy: those centroids are not known physical centers. AB positive
interior ownership under all-neighbor surface occlusion ranks candidates, retaining
up to two per hand/family. This is a finite-grid screen, not a globally optimized
inverse problem; surface centroids are not jointly optimized in that screen.

The non-neighbor/unmodeled possibility is always retained with no invented C location.
C is the remaining 1/6/7 triangle member. Every alternative's parameters, visible
surface samples, unknown rays, centroid and uncertainty are saved in `before-C`.
Only then are held-out observations compared for positive support and background
contradiction. Unassigned pixels are uncertain. “Known background” in the JSON is
an operational image-hue estimate, not externally verified real-photo truth.
A nearby peak alone is not sufficient: conditional matches require supported-surface
overlap as well as centroid proximity. Different alternatives can match different Cs.

The end-to-end diagnostic deliberately feeds the top C-method neighbor even when
Test 1 abstains, to expose propagation of wrong/same-body pairs. It does not claim
that those two bodies have been independently certified. There are 11 available
synthetic automatic pairs and 12 membership-only oracle pairs. Oracle selection does
not constrain index difference; most nearest visible-body pairs are outside the
immediate families. This is a result, not a reason to replace the oracle sample.

| Synthetic mode | Pairs | Retained hypotheses | Correct AB-family hypotheses | Visible-C comparisons for correct family | Correct conditional C identities | Median C error | Photographic baseline median* |
|---|---:|---:|---:|---:|---:|---:|---:|
| Automatic top-pair pipeline | 11 | 248 | 56 | 48 | 6 | 44.51px | 23.34px |
| Membership-only oracle | 12 | 288 | 8 | 8 | 2 | 39.82px | 23.31px |

*Baseline predicts continuation of AB or a ±90° turn, before C inspection. Its score
is the **best of three regions**, while the geometric median includes individual
retained hypotheses with the correct AB family. These are diagnostic summaries with
different alternative budgets, not a calibrated competitive accuracy test. There is
no demonstrated improvement beyond photographic-only prediction. Multiple hypotheses
from one pair are correlated and must not be treated as independent successes.
Across all retained hypotheses there are also 38 incorrect conditional matches in
the automatic mode and 14 in oracle mode (including wrong AB families).

On the real photo, six provisional AB pairs produce 144 frozen alternatives and 40
conditional pixel matches. Those are neither 40 independently predicted bodies nor
verified correspondences. Both hands and the non-neighbor alternatives survive.

After conditional C matches, the first qualifying alternative per hand undergoes
joint ABC **centroid-proxy** refinement: shared translation, rotation, scale and phase,
with inclination/pitch fixed and bounded updates. No per-bead displacement is allowed.
This proxy is a diagnostic limitation, not a full positive-surface inverse fit.
D at relative ±8 is then frozen before its evidence is consulted. Seventeen synthetic
and seven real D predictions survive, with all before/after files and hash links.
Only three synthetic ABC fits have the correct C identity; only one of those chains
also matches D correctly. Seven synthetic refinements hit a parameter bound.
None is physically accepted. Lower fitted ABC error does not validate a withheld D.

[Selected examples](review/r279/README.md#synthetic-examples) include correct image
matches in rejected constructions, incorrect matches and unmatched alternatives.
No success claim is inferred from the algebraic identity 1+6=7: that holds inside
every generated template, while correspondence still needs independent evidence.

## Packing, sensitivity and identifiability

The exact annular signed-distance test finds sampled material penetration in ±6
pairs throughout the prescribed limited pitch range. Negative samples establish
actual overlap; no “zero sampled penetration” certification is being inferred.

| Pitch / source | Minimum sampled ±6 SDF, source units |
|---:|---:|
| .95 | −.22253 |
| 1.00 | −.15347 |
| 1.05 | −.08441 |
| 1.10 | −.01535 |

The [section illustration](review/r279/packing-sections.png) shows this overlap.
The source +1 and +7 pairs are separated at pitch 1.00, but that does not rescue ±6.
Both helicities have equivalent contact constraints by reflection symmetry. Therefore
**zero tested models are physically valid**. Larger pitch, changed height/aspect or
hole-axis tilt were not added to make a fit pass. The old 1.30–1.45 constructions are
not inputs. Pitch sensitivity here audits packing, not a new held-out pitch fit.

All synthetic scenes intentionally use source or +10% pitch and therefore also have
this packing defect. They remain useful renderer/body-separation and mismatch stress
tests, but **are not a physically realizable positive-control benchmark**. R279 cannot
establish performance on correct packed jewelry geometry. This limits any claim that
poor oracle results isolate only inference error.

AB provides four coordinate scalars for seven continuous quantities (translation ×2,
rotation, scale, phase, inclination and pitch), before discrete family/hand uncertainty.
The saved finite-difference Jacobians have rank four for all 680 retained hypotheses:
at least three continuous null directions in the centroid-only equations. Positive
surface interiors can constrain some directions but are incomplete silhouettes.
Scale, phase, projected orientation and pitch can compensate strongly; numerical
Jacobian singular values, null vectors and column similarities are archived.
ABC adds two coordinates; restricting which parameters can move avoids a free
translation for each bead but does not establish physical identifiability. The local
camera/section gauge and index-origin/reversal freedoms remain unresolved.

## Failures preserved, interpretation and next experiment

The first run's hole-filling operation enclosed paper inside the necklace as
foreground, producing 12,560 observations and several paper anchors. That failed
sample, all predictions, evaluation, render data and executable source remain in
`failed-hole-fill-control`. The correction removes global hole filling and learns
two circular chromatic appearance clusters rather than using a misleading fixed
red/yellow reporting threshold. Fresh seed 279014 replaces 279013 for final evaluation;
no ranking/decision threshold changed. It is transparently a corrected second run,
not an untouched first benchmark. The archive also retains an unused triangle-label
metadata error; final labels correctly list `[0, AB_delta, C_target]`. No saved
numerical prediction was silently revised after its error was seen.

The dominant operational obstacle is **distinct-body photographic ownership**: extra
reflections, truncated masks and missed bodies invalidate nearest-neighbor ranking.
Geometry does not repair that uncertainty here. Independently, the fixed construction
fails contact, and centroid-as-center initialization plus a coarse camera/phase grid
limits the oracle diagnostic. Camera ray projection itself passes the independent
render check. The present evidence cannot uniquely apportion the remaining geometric
error among shape/pitch, pose underconstraint and correspondence search.

Recommended next bounded experiment: improve image-only same-body grouping and
visible-body representative uncertainty on a new, frozen synthetic set with an
explicit physically compatible construction control; retain the source-pitch failure
as a separate stress test. First establish the intended bead height/hole-axis/row-pitch
relationship rather than importing historical fitted poses or inflating pitch to fit
the photograph. Use a third independently separated body plus an exposed rim/size cue
to constrain phase/scale, then demand a fourth withheld prediction. A third point
alone, especially another displaced reflection, need not distinguish the hypotheses.
Do not start 20–50-bead growth or pattern reconstruction.

Validation: 14 focused scientific tests; exact full-photo observation/sample replay;
byte-exact synthetic scene-00 observations and C/D prediction replay; 29 C-freeze and
24 D-freeze hash checks; native mask and source-preservation audits. The failed camera
control and failed foreground control remain separate. No historical evidence or
shared implementation was changed. Keep the current model/reasoning; no `/new` is
needed. Stop after scoped commit/push and remote verification.
