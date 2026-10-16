# R302 — sensitivity-guided local geometry

**R302 demonstrates a better local fitting method, not uniquely recovered physical
parameters.** In580.73 seconds of timed diagnostics and fitting, the hierarchy
beats the equal-time accurate-DE control on all four training comparisons. The
primary improves dimensions and material coverage together with reflections;
comparison-reflection gains are modest and do not generalize across all starts.
[Review](review/r302/index.html) · [Reproduce](R302_REPRODUCE.md) ·
[Sensitivity figure](r302/results/sensitivity.png) · [Full comparison](r302/results/comparison.csv)

## Result on identical S1 evidence

The primary is `hierarchy-historical-plus`, chosen by the sealed training objective
before comparison evaluation. All ten reflections match, including six black
reflections (black RMS3.16px). All eight retained final models certify separation
over their153-position sections; only four pass every training contradiction flag.
No model is adopted as physical truth.

| Model | Train / comparison reflection RMS px | B15 extent MAE px | Colored omission train / held % | Dark-valley MAE px | Local positions |
|---|---:|---:|---:|---:|---:|
| R302 primary | 2.22 / 3.78 | 0.12 | 2.6 / 15.8 | 1.72 | 29 |
| R301 shared hand+ | 3.85 / 4.01 | 5.90 | 33.3 / 31.6 | 2.55 | 32 |
| R301 independent hand+ primary | 2.71 / 4.96 | 6.98 | 30.8 / 42.1 | 4.28 | 31 |
| R301 dimension-preserving hand+ alternative | 6.71 / 7.68 | 1.53 | 10.3 / 21.1 | 3.99 | 28 |
| R299 | 6.71 / 5.86 | 1.20 | 20.5 / 15.8 | 1.51 | full-chain baseline |

R302's visible B15 boundary MAE is1.15px; predicted projected extents are
22.48×31.45px. The .22px comparison-reflection gain over R301 shared hand+ is not
a significant-precision claim. The substantial result is avoiding its dimensional
and colored-material regressions while using fewer local positions. Training paper
occupation **regresses5.1→7.7%**; held paper improves11.8→5.9%. Dark-valley error
improves versus R301 but remains worse than R299's1.51px and R298's1.04px.
Outer/back-row contours still disagree visibly; sampled checks do not certify
every boundary or unseen black-body surface.

| Same start, ~67.8s each | Hierarchy loss | Accurate-DE loss |
|---|---:|---:|
| Historical hand− | 45.71 | 80.18 |
| Historical hand+ | 29.16 | 56.30 |
| R301 dimensional hand+ alternative | 55.08 | 69.83 |
| R301 shared hand+ | 71.80 | 85.58 |

These are the same new objective and native predictor, isolating the search
strategy. Charging **all37.37s diagnostic/sensitivity overhead to the hierarchy**
and truncating its saved histories accordingly still gives4/4 training wins
(45.71/29.67/55.08/75.78). No additional fit was run. Comparison-reflection RMS
wins only2/4; the two R301-derived starts lose to their controls. This is evidence
of improved bounded optimization, not universal superiority or an end-to-end
timing comparison against the entire old three-section R301 campaign. Historical
fits supply starts to both methods, so this is not a cold geometry-discovery test.

## Evidence and construction

One region only: the unchanged R301 S1 window. It supplies ten reflections
(six black, four red; seven training/three retrospective comparison), one uncertain
B15 visible contour, and194 material/paper samples. B15 supplies22.34×31.55px
projected extents with stated3px uncertainty. Its eight vertices and two extents
are dependent evidence of **one** contour. Of132 training sample locations,
39 indicate paper and39 colored material; held bands contain17 paper and19 color
samples among62 locations. Pixel count is not independent geometric information.
Four dark valleys remain comparison diagnostics, not verified bead separators.
There is no reliable independent envelope-width measurement or verified +1/+6/+7
physical neighbor identity in this window. Neighbor vectors and gap predictions
therefore remain conditional model diagnostics; reflection pair differences add
no independent observations beyond the original coordinates.

String elasticity and crochet geometry are separate. The shared effective axial
advance is free; a smooth local correction stays within±2% at every address,
including guards. This is a conservative phenomenological bound on local stitch
reconfiguration, **not a model of string strain or a measured pitch bound**.
The circular centerline uses arclength, so bending adds no artificial extension.
Net effective pitch change is not forced to zero. A thread-path/tension model is
still absent, so the experiment cannot certify inextensible crochet construction.

Constant turn rate obeys `|N*(6.5/turn−1)|≤6.5`. At conditional N=2000 this gives
6.47894–6.52119 beads/turn. Larger counts require tighter bounds. N is neither
fitted nor inferred; this is a minimum-count scenario, not a global certificate.
Each candidate has153 modeled addresses including64 guards per side. The fixed
photographic window must contain15–30 centerline addresses, preventing a denser
highlight field from winning merely by adding positions.

## Predictor and sensitivity

Thirty-six physically feasible variants cover four different initial geometries.
Coarse/native score correlation is .941, but coarse ranking recovers only5/9 of
the native best quartile. Across variants, common-owner centroid RMS has median
2.88px and a maximum individual displacement19.94px. Two-pixel sampling improves
quartile recall to8/9, yet can miss seven native lobes and move one13.26px.
Neither approximation screens candidates in R302.

The replacement traces complete selected bead bounds once on a shared native
image lattice with the same actual first-hit/shadow kernel. It reproduces every
R301 complete-bound centroid exactly at all four starts, including missingness,
and costs about .152s/candidate versus .458–.633s for repeated complete body grids.
The audit and sensitivity work took37.4s. A first per-body/per-ray field-selection
error was repaired before fitting; its source and failure log are retained.

All18 parameters receive two-sided perturbations at four starts:144 physically
certified individual perturbations, plus12 selected compensating pair moves.
Matrices retain reflection coordinates, B15 extents/visible boundary distances,
material/background fractions, transverse extent and +1/+6/+7 vectors/distances.
Predicted neighbor/gap outputs are explicitly excluded from photographic rank.
Reflections use fixed owners only within each local derivative; real fitting
retains competing assignments and unmatched penalties. Contour assignment changes
at two starts (four/two alternatives), revealing discontinuities rather than
silently claiming a smooth inverse problem.

At the declared parameter-step and measurement scales, only4–5 singular directions
exceed a standardized response of1. This is **not a statistical rank, uncertainty
interval or claim that the photograph cannot constrain more with better evidence**.
Elevation/phase sensitivity cosine is .91–.93 at three starts; pitch/elevation is
.956 at another. Axial proportion/tilt reaches .907, and local angle/curvature
−.942. Hole size, rounding, small extension and mixtures involving illumination
are weak or unstable. A reflection-only matrix has at most14 coordinate rows for
18 parameters. Dependent contour samples cannot repair that by being counted as
eight new beads.

| Quantity | Most useful evidence | What can be estimated here |
|---|---|---|
| Projected individual extent/scale | B15 silhouette, material and paper | Conditional projected size; absolute physical radius remains a unit gauge |
| Axial proportion and tilt | B15 tangent extent plus surface/reflection orientation | Coupled; neither uniquely recovered |
| Minor radius and camera elevation | Transverse material placement, reflection pattern | Their projected combination; no independent envelope width here |
| Pitch/scale/projection/phase | Reflection spacing with contour/material constraints | Local projected advance; not a physical neighbor sequence or total count |
| Centerline position/direction | Common reflection shifts and opposite material/background contradictions | Local image placement; curve and direction remain coupled |
| Turn rate and local extension | Construction constraint plus small positional changes | Primarily prior-limited; no global twist or elasticity inference |
| Hole, rounding, light | Visible surface normals and highlight motion | Weak nuisance combinations; no calibrated material recovery |

The primary has face-diameter scale31.14px, axial/face ratio .669, minor radius2.385
bead radii, effective pitch .231 bead radii/address, turn6.5, tilt−3.30°,
elevation79.51°, roll29.82° and local extension parameter .968%. Several principal
values remain at their initialization; unchanged values are **not recovered
estimates**. Even the four training-acceptable hypotheses span axial ratio
.257–.669, elevation35–79.51° and face scale28.94–33.42px. Projected local size and
placement are better estimated than physical axial proportion, camera or light.
Both hands remain viable. No count, index sequence or pattern is identified.

The primary's +1 physical center distance is2.229 bead radii; +6/+7 distances span
1.782–1.816/1.962–2.003. Their projected vectors and orientations are exported,
but unknown photographic neighbor identities prevent calling these measured
spacings. Minimum separating-plane margin is .0740 bead radii over445 close
pairs. Post-seal gap sensitivities trace background runs/owner transitions on the
four unchanged photographic routes and directional support margins; they do not
enter fitting or observational rank. Their1.78s is evaluation, not another search.

## Fitting and limits

Four identical starts feed both methods. The hierarchy opens dimensions/projection,
then helix/phase/tilt/light, then centerline/local extension, then **all parameters**
jointly. Measured column responses scale steps; correlated pairs and singular
vectors supply joint moves and limited restarts. Earlier groups are never
permanently frozen. The control is R301-style local population DE with the **same
native predictor, constraints and objective**, not a rerun of the defective coarse
screen. Historical R301 outputs remain a separate same-evidence comparison.

R301's robust squared reflection loss remains primary. Grouped squared contour
extent/boundary errors and material/background fractions penalize geometric
contradictions; observed pixels are not counted as independent residual groups.
Predeclared training flags are extent MAE>3px, visible-boundary MAE>4px,
paper occupation>10%, colored omission>23%, missing reflections, density outside
15–30, or failure of extended separating-plane certification. These are explicit
engineering checks, not calibrated acceptance of recovered physical truth.

The budget is600 seconds including diagnostics, with20 seconds reserved for call
overrun. Each of eight fits receives about67.82s. Selection is sealed before
comparison reflections, held material and dark-valley diagnostics. All proposals,
failures, alternatives and source/evidence hashes survive. The old experiments,
photo, feedback and production geometry remain unchanged. No synthetic benchmark,
whole-necklace fit, pattern or Phase3 is performed. Stop after R302.

**A second section is worth a separately authorized, bounded transfer test**, with
shared bead dimensions/camera and independent outlines, to try to falsify this
conditional geometry. Another independent18-parameter reflection fit would not
resolve the demonstrated ambiguity. No second section is started here.

Six contracts pass. Eight native selected-vector replays cover1,224 positions and
2,465 separating-plane witnesses;16,783 protected historical files are unchanged.
Chromium checks the reused18-model debugger, raw invariance, original links,
desktop/narrow/offline operation and actual launcher. Windows dispatch is mocked.
[Verification](r302/results/verification.json) · [Delivery](r302/results/delivery.json).

Scientific delivery: `91811939b427c2fe46f7b6ab1e7a50819c4313fe`, pushed to `origin/photo-2-strategy-v3`
and independently matched by `git ls-remote`. Receipt records the verified science
commit; the following metadata commit records this delivery. **STOP after R302.**
