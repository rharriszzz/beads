# R258 — bead-driven geometric refitting

Implemented and run: exact rounded-annulus surface fitting in four separated photo
sections, A/B/C/D comparisons, equal-budget count/hand alternatives, synthetic inverse
tests, and additive debugger models. **Bead2's maker-confirmed lower-left pixels can
be explained by moving the physical curve. A complete visible-body reconstruction
and a validated global solution have not been established.**

[Clean raw/old/C2 bead2 comparison](review/r258/bead-2-compact-comparison.png) ·
[A/B/C/D comparison](review/r258/bead2-comparison.png) ·
[Raw crop](review/r258/bead2-raw.png) ·
[Confirmed positive support](review/r258/bead2-confirmed-support.png) ·
[Section locator](review/r258/sections.png) ·
[Whole-photo curve comparison](review/r258/whole-photo-before-after.png) ·
[All numerical tables and parameters](review/r258/README.md).

## Evidence first, including the maker's correction

The photograph is the original `beads-photo-2.jpg`; all coordinates are original
pixel centers, x right/y down. Start with the raw crop, then the clean footprint,
then the positive-pixel image. No sampled interior or reflection is called a bead
center. Camera rays decide ownership, including holes and mutual occlusion. Primary fitting uses an orthographic camera with free joint scale; finite-focal4799/9598/19197px sensitivity cases are separately recorded, not treated as calibrated iPhone intrinsics or fitted perspective solutions.

R258 identifies **old-model review bead2 as yellow**, with roughly one-third of
its visible yellow area outside the old footprint, lower-left. This supersedes
R257's dark/red interpretation; it is not a pixel mask or exact area measurement.
The fresh R256 detector misses much of this shadowed yellow surface and calls
its sparse fragments red. The first provisional union contained 49 detector pixels.
The maker rejected it as mixed with a neighbor/background, then answered **“B only;
exclude A”** on the two-group illustration. Both questions, illustrations and answers
are retained in [questions.json](review/r258/questions.json).

Only **seven B pixels**, `(1344..1350,340)`, from fresh proposal
`I256-eb7c9edb-R-1345-0340` now constrain old review bead2. Their observed color is
yellow according to the maker. The upper hooked group A is excluded from that
correspondence. It is not reassigned to another bead. These are confirmed positive
pixels, **not the full visible area**, and do not establish a physical center.
Unreviewed-union exploratory fits were withdrawn and superseded by the delivered
rerun. The original detector, old observations, models and review records remain
unchanged; the correction is a separate R258 evidence record.

Other evidence comes from R256 photo-only interiors and R257's photo-only reliable
reflection-on-dark patches. Saved R257 owners, old R200/R252 labels, maker graph
edges and color-order hypotheses are never used by the new objective or matching.
No lighting inversion was performed. Dark gaps and shadows supply no positive masks.

## Implemented model and objective

Four methods were compared before implementation, as requested:

| Variant | Free geometry | Purpose |
| --- | --- | --- |
| A | None; exact existing N2696 h+1 model | Frozen diagnostic control |
| B | Local phase and phase gradient; exact old curve fixed | Diagnostic phase explanation |
| C | Six local curve coefficients; phase and camera fixed | Bead-driven curve explanation |
| D | C plus phase/gradient, camera elevation/roll/translation/scale, longitudinal shift | Joint ambiguity test |

`BeadCurve` stores **192 absolute periodic cubic-spline knots** in world coordinates.
The fitted specialization is planar (`z=0`), justified by the maker's table-plane
construction fact. Beads remain 3D. Arbitrary nonplanar knots are rejected by this
specialization; a general transported-frame nonplanar fitter is not claimed.
Only six local curve coefficients are active per C experiment: projected x/y
translation, slope and curvature of a compact smooth displacement field. Its
half-support is 0.025 of material-string length. They move spline knots, not beads
independently. The compact support joins smoothly into the rest of the closed curve.
D has 14 active parameters, including a free positive camera scale. A post-hoc C2/C4 control restricts C to 2/4 parameters.

At material fraction `t=i/N`, the world centerline and tangent define the annulus
axis. The bead center is `curve(t) + 4*minor_radial(t)`. The phase is an integer
number of signed minor-circle turns plus periodic corrections. For N2696, the
source rule gives 415 turns and 6.49639 beads per turn. `beads.pov` dimensions are
retained literally: radius2.1109157489, hole0.14R, rounded radial profile major0.57R,
minor0.43R, rounding0.8, axial half-height0.7R. POV-Ray's literal radians-valued
`sin(180/6.5)` is preserved. The source annulus is never replaced by a sphere;
spheres only bound ray-intersection candidates.

The old curve/camera and approximate phase initialize the principal comparison;
initial old longitudinal/twist fields enter only its initial geometry. They are
not observations, objective terms or acceptance criteria. This is a **warm-started
bead-evidence fit**, not an independently initialized global reconstruction. A/B
explicitly use frozen historical geometry for the requested diagnostics. C/D operate
on their own serialized absolute knots and parameters; no legacy data are read by
their geometry objective. Count/hand screens reset phase corrections and use eight
uniform phase starts, with equal fitting flexibility and budget.

The objective is:

```
weighted robust positive-patch distance to assigned FIRST-HIT footprint
+ color-owner conflict cost
+ 0.8 * physical regularization
```

Footprints are traced on a3px grid during search. Distance transforms of **visible
owned surfaces** give a footprint-distance residual, not a center residual.
Per-pixel squared distances clip at12px and the per-observation robust loss caps
at36px². Candidate distinct interiors have weight1, uncertain splits0.3,
reflection-on-dark patches0.6, and the maker-confirmed B patch2. These are declared
engineering weights, not calibrated likelihoods. The scalar objective and final
ownership fraction differ; both are reported, including regressions.

Unknown observation identities are rematched using surface costs and an unmatched
option. Distinct proposals compete for unique slots; uncertain splits may share
an owner. Opposite observed classes sharing an owner incur a conflict cost. The
confirmed bead2 correspondence is reserved explicitly and cannot fall through an
unmatched-cost tie into a distant index. Its review namespace is unchanged. Proposal
“interior” status remains fallible; counts are **conditionally distinct candidates**,
not certified total bodies. No final bead count or complete correspondence is inferred.

Physical regularization penalizes material-speed deviation beyond8% from the source
row spacing, curvature above0.12 inverse source units, local winding-step deviation
beyond3%, and adjacent-center distance below3.25 source units. Cubic smoothness,
periodicity and integer winding enforce continuous closure. These tolerances are
modeling assumptions, not measured material constants. The packing term is a
center-separation surrogate, **not a full noninterpenetration proof**. There are no
curve/edge distances or old bead positions in the loss. **No displacement, tangent,
curvature, registration or spacing bound is anchored to the initial curve.** Only
B's explicitly limited diagnostic phase freedom and the camera-above-paper domain
have hard bounds. Search has a finite evaluation budget, not a resemblance prior.

The coordinate pattern search has a400-evaluation cap per primary fit; individual
runs can stop earlier when their steps shrink. Both hands/counts receive the same
8 phase starts and220-evaluation local joint-fit cap. This is a reproducible local
search, not a proof of finding the global minimum. No evidence justifies increasing
flexibility until all pixels fit.

## Validation and interpretation

Whole detector connected-component groups are held out by a deterministic hash,
including every member of an ambiguous split group. This is conservative for touching
same-color bodies; erroneous fragmentation can still split a true body across
components. A full body-level independence claim requires reviewed body masks.
Geographic tests use the other three distant sections without refitting; a fifth
region is held out from every primary/alternative fit. A compact local correction
leaving that region unchanged is not evidence of global improvement.

Native rays evaluate every retained positive pixel. Per-observation ledgers include
intended/conditional owner, wrong-owner fraction, missing support, mean/RMS/median/
90th-percentile/worst footprint residual, native positive ownership, approximate
predicted area, and index stability. Distances to a3px footprint have a sampling
floor and do not measure physical-center error. Unmatched residuals use a declared
30px reporting sentinel. Native selected-neighbor footprints and1px centroids are
also saved, and the debugger supports R257's adaptive boundary integration.

Full visible boundaries are not verified, so **boundary IoU is null**, not fabricated.
The reported unsupported predicted area is an upper bound from sparse positive
support, not a false-positive segmentation score. The debugger colors such surface
samples orange for inspection; shadowed real bead surface may have no detector support.

The [numerical summary](review/r258/README.md) gives all major comparisons. C and D
explain all seven confirmed B pixels, whereas A and B explain none. Removing curve
translation from either fitted model loses those pixels. C needs no phase/camera
change. D trades camera and curve changes against each other: it is not a unique
physical explanation. Radius and axial-dimension perturbations, each geometric
parameter, hypothetical ±1/6/7 index substitutions and neighbor-occlusion removal
are quantified in separate ledgers. Removing occluders is only a diagnostic, never
an admissible fit. The identity alternatives do not silently renumber maker reviews.

The origin C fit improves training ownership but **regresses on held-out nearby
observations**. Therefore it is not an accepted neighborhood solution. The post-hoc
C2 control shifts the curve roughly2.63px left and4.50px down, covers all confirmed
B pixels, and has less held-out regression. C2 was tried after seeing the primary
regression; its holdout is explicitly exploratory, not untouched confirmation.
Several distant sections improve, but that does not rescue the origin failure.

At bead2, C2's5.21px material-point displacement decomposes into4.05px normal to
the old projected curve and−3.28px along it; tangent rotation is only−0.0066°.
The tangential component can trade against material registration/spacing, so the
entire5.21px must not be called normal centerline deformation. C changes the local
tangent by7.45°, D is separately quantified in origin-curve-components.json; their flexibility does not establish those rotations.
The distributed curve differs from the old registered physical model by2.03px RMS,
11.29px maximum. Nearest-distance comparison with the original **unregistered
image spline** is separately reported (distributed RMS3.09px, maximum9.56px);
these are reference comparisons, never fitting targets or acceptance tests.

Frozen fresh-A correspondence checks reveal nearby regressions even for C2:
proposal `(1349,273)`, conditionally old k0, drops88.2%→63.3% ownership, while
`(1339,285)` on the same conditional k0 rises68.6%→98.1%. A k6-associated fragment
improves85.8%→98.1%, another drops42.1%→6.6%. These may include detector splits or
wrong correspondences; they prevent calling the neighborhood solved. There is no
reliable assigned observation for k1 in this local subset. All0–7 and±1/6/7
footprints/centroids remain inspectable, including unsupported and hidden beads.


The distributed C model simply combines four fitted, disjoint spline supports into
one periodic curve. It is available for whole-photo inspection. Most of its curve
remains initialization/interpolation; it is **not an adopted global reconstruction**.
A further eleven-parameter whole-curve fit frees constant translation and first/second harmonic displacements everywhere, plus camera scale, with no anchors or old-curve bounds. Its training search finds no lower objective (3.34323 before and after); this null result does not validate the inherited spans. The fifth spatial holdout has unchanged agreement. Both helicities and N2674,2681,
2696,2700 remain viable. The h+1 screen scores better in these tests, but uncertain
correspondences, local phase ambiguity, nonexhaustive N search and lack of measured
closure prevent a selection. N2670–2700 values not explicitly tested are not excluded.

Synthetic inverse tests use a known analytic circular source string and exact
visible surfaces. A deliberately incorrect smooth curve is recovered with the
same fitter; rigid translation leaves physical cost invariant, and forbidding
historical reads during the objective succeeds. Opposite-hand phase recovery,
missing/ambiguous observations, holdout isolation, exact annulus/profile normals,
holes/occlusion, dimension-tracer equivalence, closure, review preservation and
native region exports are tested. All29 Python tests,4 JavaScript contracts and74
real-Chromium checks pass. The deliberately wrong initial curve's RMS error falls
from8.315px to0.310px. These inverse tests use the same ray kernel as fitting;
independent analytic shape/normal contracts provide an additional check, not a
separate photographic reconstruction benchmark. See validation.json and the
reproducible commands.

## Inspect now and next question

Restart `.venv/bin/python -m photo2.bead_debugger.server` and open
http://localhost:8767. **Bead 2: old / fitted C2** switches the simpler displacement-only
comparison without changing viewport. Select `R258_origin_C` for the primary curve
experiment; C4, every A/B/C/D region, eight origin hand/count alternatives and
`R258_distributed_C` and the unanchored `R258_global_low_modes` trial are also available. Native selected footprints, centroids,
neighbor navigation, explicit new/historical index namespaces, original reference
curves, ownership failures and unsupported-area overlays work with every new model.
Hover reports the native owner inside the calculated neighborhood. Lighting remains
an approximate shared diagnostic; it does not enter fitting.

In Review, **Draw bead region** adds vertices directly in original-photo coordinates;
choose positive interior versus visible boundary versus uncertainty and observed
color, then Save review. Undo/clear, drafts, backup/import, reload and debug ZIP keep
that region with its exact model/version/index namespace. Drawing does not silently
refit or reinterpret any old review. User production review files are untouched.

The next useful task is to mark bead2's full visible yellow extent and a few reliable
positive regions on beads0/1 and its diagonal neighbors. That can distinguish a
simple local curve displacement from a wrong conditional neighbor assignment or
occlusion model. Stop at this delivery; no global indexing or pattern recovery.
Recommendation: GPT-6 Astra / High for that ambiguity; this is a recommendation,
not a newly inferred active-model status. [Official OpenAI model guidance](https://developers.openai.com/api/docs/models/gpt-6-astra).
No `/new` needed for review; use `/new` before another substantial inference round.
