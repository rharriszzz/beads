# R298 — thinner beads and wider rope, with unresolved local contradictions

**R298 reduces the three targeted geometric discrepancies, but does not deliver a
replacement reconstruction that avoids worse photographic contradictions.** The
bounded calibrated primary has thinner axial proportions, a larger minor radius,
a revised planar axis and a newly exposed camera rotation. Native comparison-region
transverse-width error falls **12.23→5.12px**, apparent axial-extent error
**3.99→2.34px**, and common-mode envelope residual **4.15→2.13px**. However, separator
alignment, paper-proxy occupation and several established local fits regress.
**Do not adopt it or launch a larger optimizer from it before maker review.**

[Graphical review](review/r298/index.html) ·
[Whole-loop dimensional errors](review/r298/dimensional-errors.png) ·
[Measured pixels and provenance](r298/evidence/measurements.json) ·
[Reproduction and launcher](R298_REPRODUCE.md)

From WSL2:

```sh
photo2/review/r298/launch.sh
```

The script selects the repository virtual environment, serves the review and opens
the browser. Raw photographs remain unmarked beside adjustable R297/R298 surfaces,
axis hypotheses, transverse bounds, measured contours and separator profiles.
All four feasible hand/topology families, all 51 navigation locations, arbitrary
photo locations and all exported indices are available. No repeating color pattern
is inferred. R297 and all earlier scientific artifacts remain unchanged.

## What was actually measured

The native 2540×3182 photograph, preserved Phase1 region locations and raw pixels
supply the measurements. No fitted model enters extraction. Sixteen geographically
spread large colored-region locations select raw inspection windows. Before fitting,
the analyst digitized eight visible-contour landmarks on an exposed colored bead
in each window. These are approximate **visible silhouettes**, with **±3px extent
uncertainty**, not maker-confirmed outlines, physical centers or confidence bounds.
Dark margins, blur and partial occlusion limit the inferred full-body dimensions.
The source region ID identifies the inspection crop, not ownership of every drawn
landmark; B13 deliberately measures the nearby exposed yellow rather than the
red crop anchor. No historical Phase1 mask was altered or promoted to a body mask.

Tangent/normal directions initially use the image reference as a measurement frame.
The table reports projected visible extents in that frame; the physical fit uses
camera projection rather than equating those lengths to 3D thickness/diameter.
Each link shows identical native raw/R297/R298 crops, with the uncertain contour
separate from model boundaries. All twelve development and four comparison beads
remain in the denominators, including poorly matched contours.

| Crop | Apparent tangent extent px | Apparent transverse extent px | Use |
|---|---:|---:|---|
|[B00](review/r298/comparison-B00.png)|26.3|33.9|development; old difficult 33 neighborhood|
|[B01](review/r298/comparison-B01.png)|23.3|27.3|development; old 195 neighborhood|
|[B02](review/r298/comparison-B02.png)|23.8|31.5|development|
|[B03](review/r298/comparison-B03.png)|24.2|32.8|comparison|
|[B04](review/r298/comparison-B04.png)|23.9|30.7|development|
|[B05](review/r298/comparison-B05.png)|21.4|29.4|development|
|[B06](review/r298/comparison-B06.png)|25.8|31.0|development|
|[B07](review/r298/comparison-B07.png)|21.4|28.8|comparison|
|[B08](review/r298/comparison-B08.png)|17.1|33.2|development; exposed central return|
|[B09](review/r298/comparison-B09.png)|22.7|31.1|development|
|[B10](review/r298/comparison-B10.png)|26.1|29.5|development; central return|
|[B11](review/r298/comparison-B11.png)|19.4|32.1|comparison; central return|
|[B12](review/r298/comparison-B12.png)|26.0|30.3|development|
|[B13](review/r298/comparison-B13.png)|23.3|29.8|development|
|[B14](review/r298/comparison-B14.png)|18.8|36.9|development; oblique tapered outline|
|[B15](review/r298/comparison-B15.png)|22.3|31.6|comparison|

The mean apparent extents are **22.87×31.25px**, with substantial orientation and
exposure variation. The historical **30×29px reference is not used as calibration**.
[Raw crop hashes, contour pixels and RGB](r298/evidence/measurement-audit.json)
augment the original photo hash and exact native inspection coordinates.

Across the entire loop, **193 transverse stations at 48px intervals** each retain
nine native transects over a 24px longitudinal span, every sampled RGB pixel and
three threshold alternatives. A global paper-hue/luminance test incorrectly followed
cast shadows. A global hue-only variant also failed: some shadowed paper shifted
about 24° from the border hue. Both failed datasets and source versions survive.
The final measurement compares each side with nearby paper on that side, using
10/14/18° hue and .12/.16/.20 saturation differences, retaining threshold sensitivity.
It measures material/paper transitions, not a new production segmentation.

104 profiles pass the provisional sensitivity screen; pre-fit raw inspection
excludes eight of those plus one already-ineligible profile because an edge remains
in shadow. **96 eligible profiles** remain: 70 development and 26 comparison.
The 97 excluded profiles stay visible, with reasons and sensitivity. The eligible
median transverse width is **101px**, 10th–90th percentiles **92–110px** and full
range **85–115px**. Uncertainty is at least 3px per edge; fitting uses at least 4px.
Median cross-section width differs from the outermost smooth rope guide because
of bead scallops, phase, gaps and projection. Neither width nor an edge midpoint
is asserted to be a measured physical axis.

This agrees qualitatively with R184's observation that the old 107% guide was still
narrow. That guide was about 101px for its particular model/count; it was **not** an
independent measured width and did not prescribe R298's increase.

**All geography is retrospective.** Selection on a previously studied photograph,
analyst inspection, overlapping pixels and shared color evidence prevent any claim
of untouched validation or calibrated measurement precision.

## Structural diagnosis and controlled experiments

The literal hollow rounded annulus remains unchanged apart from shared affine axial
thickness. Face diameter is `2*radius`; thickness is `1.4*radius*axial`; their ratio
is `.7*axial`. R297's `axial=1` therefore means ratio **0.700**, not a sphere or
width/height 1. Radius and minor radius control different dimensions. The continuous
transverse/face ratio is `(minor+radius)/radius`; projected discrete bounds require
actual surfaces, not just this ratio.

Longitudinal rate depends on total deprojected axis length/count plus shared strain
and the inherited local metric correction. Stored `pitch` controls the local
restoration but is not an independent full-loop pitch. The +1/+6/+7 displacements
also depend on minor phase, winding, axis curvature and the camera. Enlarging minor
radius can change diagonal contacts; it does not guarantee more separation.

Camera scale trades against physical radius, minor radius and longitudinal units.
**Radius is fixed at 1.78453698 arbitrary source units to fix that gauge**, and scale
is constrained by bead-face measurements as well as envelope width. World-unit
rescaling is tested explicitly; no millimeter size is recoverable without an
external length reference. World yaw is another gauge under deprojection of the
free planar reference. It is not the missing camera orientation parameter.

**The newly exposed image-plane camera rotation is consequential.** R297 effectively
fixed the foreshortening direction to an image axis. The new `roll` rotates right/down
about the view direction before deprojecting the paper plane. All beads share that
camera and one planar axis. This changes orientation-dependent apparent thickness.

| Control, development bead axial MAE | Result | Physical result |
|---|---|---|
|R297 baseline|4.38px; ratio .700; elevation60°|certified|
|Dimensions, camera fixed|3.63px; axial multiplier .795; scale8.665|certified|
|Dimensions + elevation, no camera rotation|2.12px; axial1.052; elevation88.72°|demonstrated collisions|
|Dimensions + elevation + camera rotation|1.40px; axial .828; elevation62.13°; rotation30.44°|certified|
|Axis only|common-mode edge error3.90→2.31px in polygon screen; width remains wrong|certified|

Paired minor-radius, scale, elevation, perspective and count interventions reduce
some errors but several cause actual interpenetration. Simply enlarging scale makes
bead-width error worse while widening the rope. Four unconstrained joint fits improve
dimensional residuals but all collide. The subsequent physical fits and camera-roll
fits retain those failures and require separate full-chain certification before
selection. The scalar collision penalty is only a search aid, never a certificate.

The axis is a periodic **16-node in-plane normal spline**, with range ±45 native
pixels and a curvature/smoothness penalty, no closeness penalty to the old curve.
It is deprojected into the paper plane, re-arclength-parameterized, and updates the
local frame, spacing and surfaces together. This has substantially more freedom
than R297's small local corrections. It cannot shift beads independently. Actual
fitted nodes span **−5.15 to +4.56px**: the photograph, rather than a small-change
bound, selects this modest adjustment. Axis error is assessed through both predicted
surface edges; an arithmetic midpoint of observed edges is never used as the axis.

The approximate paper-plane assumption is retained. Residuals still vary by
orientation and geography, but this single view and uncertain outlines do not
identify an out-of-plane correction separately from camera, axis and ownership
errors. There is no evidence here that requires unrestricted 3D axis deformation.
Rounding and hole proportions are not separately identifiable from these exposed
landmarks, so they remain literal source-shape parameters.

## Joint calibration and native dimensional checks

Sixteen bounded least-squares fits (3,602 objective calls, including finite-difference probes; 454.9s aggregate fit time) cover the controlled, unconstrained, physical and camera-rotation stages. Low-dimensional controls precede the joint fits.
A final **81-trial / 239.8-second** bounded refinement checks full-chain feasibility
and includes bead extents, transverse width, common-mode boundary residuals,
photographic separators, paper occupation, colored-material absence and color
conflicts. Large-support containment has a small secondary weight; bright-patch
containment has **no reward**. Only shared phase/origin and small shared parameter
controls are tried; counts and hand/topology families are retained, not broadly
reoptimized. 78 final trials certify; three demonstrate collisions. Every trial,
failed earlier fit and finite-difference probe survives.

Five exported models include R297 and four feasible calibrated families. The
primary is **hand−, N2438, open**, a finite objective choice, not evidence that the
necklace has an opening. The hand− closed N2337 and hand+ open/closed N2709 families
remain available. The reference's periodic lineage does not establish a physical
join. No exposed comparison result triggers another fit after selection.

| Physical or reference-scale quantity | R297 | R298 primary |
|---|---:|---:|
|Axial thickness / face diameter|0.700|0.582|
|Axial thickness, source units|2.498|2.077|
|Face diameter, source units (gauge fixed)|3.569|3.569|
|Minor radius / face diameter|1.121|1.211|
|Transverse outer diameter / face diameter|3.241|3.422|
|Reference face diameter, px|29.62|30.99|
|Reference continuous transverse diameter, px|96.02|106.06|
|Camera elevation / image rotation|60° / 0°|62.38° / 27.90°|
|Median native predicted width at eligible profiles|90px|99px|

The near-zero fitted perspective coefficient is not proof of orthography. The
finite controls expose camera/shape coupling, and the limits on body visibility,
material edges and axis geometry dominate precision. The narrow range of ratios
across four related finalists is **not** a confidence interval.

| Identical evidence, MAE in native px | R297 | R298 primary |
|---|---:|---:|
|Development apparent axial extent (12 beads)|4.38|1.44|
|Comparison apparent axial extent (4 beads)|3.99|2.34|
|Development face extent|2.02|1.73|
|Comparison face extent|2.09|1.39|
|Development native transverse width (70 profiles)|10.54|5.54|
|Comparison native transverse width (26 profiles)|12.23|5.12|
|Development native boundary position|6.36|3.51|
|Comparison native boundary position|6.88|3.29|
|Development common-mode edge residual|3.81|2.16|
|Comparison common-mode edge residual|4.15|2.13|

75/96 eligible profile width errors improve by more than1px, 15 regress by more
than1px, and six change less. The full-loop plot retains every eligible error;
excluded stretches are uncertainty, not zero error. The cheap optimizer intersects
48-vertex analytic outer-support polygons at five transects; final figures use
exact first-hit native pixels on the same nine photographic transects. Polygon
approximation is independently checked against rays. Outer support fills the
annular hole only for external-boundary calculation; actual visibility still uses
the hollow surface. Native model visibility retains unresolved rays explicitly.

## Neighbors, separators and remaining contradictions

Thirty-two geographically distributed preserved region pairs supply raw RGB profiles,
measured representative displacements and dark-interval widths. These are not
physical center displacements: representatives can move within an exposed surface.
A dark interval can be a contact seam or shading, not exposed paper or an empty gap.
The review therefore displays those measurements alongside, rather than equating
them with, each model's conditional +1/+6/+7 center vectors, projected surface gaps
and 3D separations. Projected overlap can coexist with certified 3D nonintersection.
No new +1 identity is certified from these ambiguous region pairs.

The final objective rewards a model boundary near a measured valley while preserving
unmatched banks and conditional index differences. This is a modest diagnostic;
internal shading and incorrect ownership can still pass. The comparison separator
error **regresses 3.05→5.34px**. The measurement set is adequate to expose this failure,
not to assert a complete recovered neighbor graph.

| Retrospective comparison cues | R297 | R298 primary |
|---|---:|---:|
|Existing paper-proxy samples occupied|3.45%|8.35%|
|Colored material without predicted surface|34.03%|30.08%|
|Conflicting colored evidence per modeled owner|6.81%|8.51%|
|Sampled large-support containment|62.57%|56.73%|
|Measured valley to nearest model boundary|3.05px|5.34px|

The historical paper proxy is imperfect, as the shadow extraction failures already
show; this does not justify ignoring its regression. Raw views and the separate
local-side envelope measurements expose the distinction. Widening the rope covers
more actual material but also occupies more pixels classified as paper. Thinning,
reorienting and re-arclength-parameterizing the chain disrupts earlier local phase
and correspondence. Minimal nuisance adjustment does not repair that globally.

Full native checks on **all 1,990 unchanged supports (447 larger regions)** show
mean larger-region containment **65.60→59.75%**. R297's original training/validation/
retrospective-reserved larger-region means change **67.21→59.82%**, **74.11→59.84%**,
and **61.67→58.81%**. Buffer regions improve49.36→59.59%. These are geometric support
compatibilities, not physical identity accuracy.

| Difficult original support | R297 | Primary hand− open | Hand− closed | Hand+ open | Hand+ closed |
|---|---:|---:|---:|---:|---:|
|Near old33, E5-1633-0278|49.07%|27.78%|61.11%|54.17%|56.25%|
|Near old65, C-1729-0337|65.46%|53.13%|44.78%|83.11%|98.48%|
|Near old195, C-2038-0658|99.34%|45.05%|59.34%|49.45%|50.11%|

Thus the principal “no worse contradictions elsewhere” criterion is **not met**.
The family favored by dimensional scoring is not a universal photographic winner.
The result is a useful calibration diagnosis and graphical alternative, not an
established replacement model. No post-evaluation repair conceals these failures.

## FFT, physical contact and closure

The independent diagnostic reads the original saved R249 six-site V/Y primary peaks.
It does not re-extract peaks to favor a fit. At each model's local front surface,
longitudinal/phase derivatives give direct vectors v1/v6/v7; `A=[v1 v6]`,
`B=A^-T`, and row1/6/7 normals are `b2,b1,b1-b2`. R249 uses x-right/y-up frequency
coordinates. Camera projection includes its Jacobian, and center-radius versus
outer-radius and ±20° visible-latitude alternatives remain explicit. All peak
permutations and .5/1/2 frequency aliases survive.

This is a local unrolled approximation, not an exact curved-image spectrum.
The optimistic best residual in FFT resolution units averages1.55 for R297,
1.47 for the primary, and1.37/1.36 for the hand+ open/closed models. R297 and the
primary both fail badly at T4-Y and T5-V (about3.2 units). These small gains and
assignment/alias freedom **do not select a hand or count**; the spectral diagnostic
slightly favors opposite-hand alternatives, preserving the disagreement. Saved
supported versus unsupported spectral trios remain visible in every model's JSON.

All four calibrated finalists pass full-chain nonintersection, including spatial
neighbors across an open cut and nonlocal chain approaches. Their independently
replayed minimum separating-plane margins are0.314641 (hand− closed),0.035093
(hand+ open),0.262455 (primary hand− open), and0.037524 (hand+ closed) source units.
These are conservative floating-point separation bounds, not exact distances or
formal interval proofs. Failed earlier certificates remain unresolved unless a
volume-overlap witness demonstrates collision; no unresolved candidate is selected.

Closed candidates have integer winding and position/frame/radial closure. The
primary open candidate has axis endpoint gap0.462864 units, radial mismatch0.347098,
and total phase−375.944487 turns. Those mismatches describe its conditional cut;
they do not establish a photographed opening. Every index remains exported,
including unsupported and occluded sites. No color pattern or physical ownership
is inferred to resolve closure.

## Delivery and limits

Nine targeted geometry/provenance contracts pass. Numerical verification replays
all81 final trials' dimensional results and physical states, a complete deterministic
free-camera control fit, all five exported models' positions/contact witnesses,
40,000 native rays,270 complete source supports and all saved FFT diagnostics.
Five native exports trace 5,361,979 rays;3,875 unresolved rays are retained
per model in the downloadable records, not converted to background truth.
The source photo is byte-exact in the review, raw profile RGB is replayed, and
**16,192 protected prior files** remain unchanged. Chromium checks all51 locations, four alternatives, all links, raw-panel invariance, narrow layout and offline use. The actual shell launcher is tested from another directory; Windows browser dispatch is mocked. Delivery receipts are linked below.

The technical photo-return-type and NumPy-JSON export failures, shadow-following
measurement failures, colliding controls, source versions and complete trial
histories are retained. No scientific result is repaired after final selection.
The reusable optimizer launcher is unchanged: R298 has its own review launcher.

**Stop for the maker's review. No further whole-necklace optimization or R299.**
The next decision is whether these dimensional/axis changes look physically right
in the native overlays, despite their correspondence regressions. That decision
must precede any attempt to recover the lost local alignments.

[Specification](R298_SPECIFICATION.md) · [Verification](r298/results/verification.json) ·
[Browser receipt](r298/results/browser-check.json) · [Delivery](r298/results/delivery.json)
