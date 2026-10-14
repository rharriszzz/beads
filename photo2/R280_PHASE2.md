# R280 — geometry-assisted Phase 2: easy surfaces improve, identity gate fails

**With exact geometry, the frozen detector strongly supports 20/26 easy held-out
beads, with zero wrong strong assignments. Three were absent from the frozen
Phase 1 inventory. It is not yet a reliable bead-presence verifier:** deleting an
easy bead while retaining its prediction produces **2/8 false confirmations**.
A 0.1-diameter position error also reduces easy-case precision to 80%. Do not grow
a reconstruction from these outputs.

[Interactive review](r280/index.html) · [Reproduction/API](r280/README.md) ·
[Raw/annotated examples](r280/results/examples/index.json) ·
[Accuracy and sensitivity](r280/results/accuracy-sensitivity.png) ·
[False confirmations](r280/results/false-confirmations.png)

## Scope, independence, and preserved evidence

R280 implements three genuinely different controls in an isolated directory:

| Method | Evidence used | Main limitation |
|---|---|---|
| A: local appearance | Independent brightness seeds and image-only watershed supports, queried in the prediction aperture | Multiple reflections, merged same-color basins, and nearest-body mistakes |
| B: visible-surface matching | Annular model surface, observed chromatic/dark-body pixels, image gradients at predicted boundaries, background contradictions; bounded registration | Model clipping can hide impure ownership; edges can belong to another body |
| C: B plus joint ownership | Symmetric competition between hypotheses sharing measured pixels; preserves all rivals | Abstains rather than identifies the winner; cannot catch every disjoint partition of one real body |
| P: frozen Phase 1 | Unchanged R275 chain plus R278 recovery; nearest accepted observation in the same aperture | Query correspondence can be wrong even when the observation itself is valid |

C is the principal experimental implementation. It is neither a relaxed Phase 1
selector nor an accepted production detector. No existing observations are edited.
All **900 locations/897 masks**, archived/suppressed evidence, uncertainties,
original photograph, original `beads.pov`, and **5,990 prior tracked input files**
remain byte-identical. No new discovery is relabeled Phase 1.

Permitted inputs are original pixels, source construction principles, pure annular
surface functions, and frozen image-only interiors. No earlier hand-specified
neighbors, maker adjacency answers, charts, historical fitted poses, global
centerline fit, or repeating colors enter initialization or inference. A5 uses
local PCA of photographic observations, never the historical centerline. The
Phase 1 benchmark wrapper replaces the photograph-specific band with an
unrestricted image domain; all detection/measurement thresholds remain unchanged.
It executes the full R275 synthetic chain plus R278 additions, not merely R278's
previous empty-inventory recovery test.

An import audit caught an **unused** historical spline-seed/model-index read through
R278's contact module importing a general surface utility. The identical support
function, certificate, and vector normalization are now isolated locally. The
post-freeze change is an import repair, not algorithm tuning: all 18 scene contact
certificates and all 25 A5 files replay exactly. The original freeze and explicit
[repair record](r280/results/dependency-repair.json) survive. Fresh geometry imports
now read no historical project data.

## Physically valid benchmark and easy-first curriculum

The radius is `.96*4*sin(pi/6.5) = 1.784536980648071`. Every appearance and identity
render uses the actual rounded, hollow `bead` macro extracted from `beads.pov`:
roundedness .8, axial half-height .7 radius, hole radius .14 radius. No sphere or
ellipse substitutes for the bead. Python traces the independently implemented
implicit annulus; bounding spheres only accelerate intersection tests.

There are eight development scenes (seed 280101), eight held-out scenes (280202),
and two separate invalid-packing stress scenes (280303). Each contains a fixed
29-site straight construction context, not a reconstructed/grown segment. Both
helicities, four camera inclinations, random phase/roll, two image scales, four
backgrounds, four light/gloss conditions, same-color runs, red/yellow/black,
strong/weak/absent specular terms, occlusion and small remnants are included.
Lighting/background/camera factors are paired in this small design; this is not
an independent factorial attribution of their effects. Orthographic cameras,
opaque materials, one light and unblurred POV pixels remain a substantial domain
limitation. Perspective, sensor blur, translucent materials and photographic
white balance are not validated here.

The primary scenes use pitch **1.12 or 1.20 times source**, explicitly testing
geometry, not inferred necklace dimensions. Every possible bounding-sphere pair
has an analytic separating-plane witness for the filled convex outer envelope;
minimum margins are **.0199868 and .1487114 source units**. All other pairs are
excluded by bounding spheres. These are sufficient floating-point witnesses,
not interval-arithmetic proofs. Source pitch 1.00 fails and remains stress-only.
Python and independent POV identity rasters agree on every resolved audit ray;
grazing unknowns are recorded, never forced to a body. Each scene saves witnesses,
parameters, exact POV sources, renderer logs, photograph and identity truth.

The detector never receives the POV identity raster, true colors or observed
segmentation. Predicted first-hit surfaces come from Python forward geometry.
A1 deliberately supplies true geometric parameters, as requested, which naturally
makes its model support unusually accurate. This is API/data-flow separation,
not an operating-system security sandbox. Truth is used only by benchmark
providers and evaluators. Immediate-neighbor tests use **+1/-1 construction
neighbors**, not nearest visible-centroid oracle pairs. A5 explicitly retains
signed ±1/±6/±7 alternatives.

Following the user's steering, the initial gate is easy A1. The frozen easy tier
requires >=150 visible pixels, >=65% isolated area exposed, position within the
middle 65% of projected strip width, upper-quartile max-channel >=.25 and luminance
>=.05, and visible-centroid separation >=.55 projected diameter. Moderate is
sufficiently visible but not easy; hard includes dark bodies and small/hidden
surfaces. Sufficient visibility means >=30 pixels and >=10% isolated area.
These truth-based tiers select **evaluation strata only**, never detector inputs.
They are proxies, not a universal ordering of photographic difficulty.

The first easy definition required a gap between every projected silhouette and
therefore selected zero beads. That failed design and summary are preserved.
The development amendment replaces that gap with centroid separation and avoids
penalizing illuminated red pigment by luminance alone. It occurred before the
uncertainty tests and held-out rendering. An additional, explicitly post-hoc
sensitivity excluding synthetic segment ends gives **9/11 central easy beads**
strongly correct, zero incorrect strongs; it did not select thresholds.

## Detector contract and freeze

`infer(rgb, predictions, method, thresholds, phase1=())` accepts approximate model
centers, diameters, rasterized annular visible/silhouette surfaces, translation/
scale/angle uncertainty and nearby hypotheses. Occlusion is supplied by the
forward first-hit surfaces. It returns measured support, supported-interior
centroid, raw pixel color or unknown, separate model registration, uncertainty
radius, rivals, Phase 1 overlaps, cue scores, and one of strong/partial/ambiguous/
contradicted/insufficient. `physical_center` is always null.

Background chromaticity is learned from image borders; illumination changes alone
do not create positive material. Dark neutral evidence depends on contrast to
that background model. Shape scoring combines foreground fraction (.45), image
edge fraction (.55), and paper contradiction penalty (.35). Strong support requires
score >=.65, foreground >=.55, boundary support >=.40, and >=40 measured pixels.
Eight pixels suffice only for weaker evidence. Registration searches translation
inside a declared disk, or scale/roll alternatives, not all free parameters at
once. Color is read from pixels; six strongly supported yellow bodies remain
unknown in the held-out set, rather than receiving a guessed pattern color.

Development exposed high-scoring tiny fragments. The original .80/8px control,
source, complete predictions and errors survive under `development-v1`. Final
selection uses the development easy A1 plus contextual false predictions at a
98% empirical precision target, with .10 score margin above the lowest tested
qualifying threshold (.55). The 40px strong gate deliberately prioritizes substantial
surfaces. Final development easy A1 is **33/36**, all 33 strong assignments correct.
A1 clears the planned >=90% precision / >=60% recall development gate, allowing
A2–A4 diagnostics. [Freeze](r280/results/freeze.json) precedes held-out rendering
and A5; no detector threshold or measurement rule changed afterward. The later
removed-bead control is explicitly post-freeze and was not used to retune.

This implementation's support is **photographic positive pixels conditioned on a
model surface**, not an independently recovered full-body segmentation. Likewise,
the fixed max(2px, .25 diameter, input uncertainty) radius is an engineering estimate,
not a calibrated statistical interval. These distinctions are crucial to its failures.

## Held-out results, with difficulty kept separate

Eight scenes contain 232 modeled sites; 169 meet sufficient visibility. Scene is
the statistical unit. Counts are descriptive, not 232 independent experiments.

| A1 tier, method C | Eligible | Correct / strong | Recall | Wrong strong owner | Other statuses |
|---|---:|---:|---:|---:|---|
| Easy | 26 | 20/20 | 76.9% | 0 | 6 partial |
| Moderate | 59 | 57/57 | 96.6% | 0 | 1 partial, 1 insufficient |
| Hard | 84 of 147 sites | 38/38 | 45.2% | 0 | 46 partial, 63 insufficient |
| All sufficiently visible | 169 | 115/115 | 68.0% | 0 | 53 partial, 64 insufficient across all 232 sites |

Moderate happens to score better than easy because these strata mix illumination,
color and projected exposure. This does not establish that harder beads are easier.
Scene-bootstrap easy recall interval is **52.9–93.1%**; individual scene results are
saved. A bootstrap precision interval of [1,1] merely resamples a zero-error sample:
it does **not** prove perfect population precision. Eight scenes are limited evidence.

| Easy A1 comparison | Correct / strong | Strong precision | Recall |
|---|---:|---:|---:|
| Frozen Phase 1 + same-aperture nearest query | 17/21 | 81.0% | 65.4% |
| Local appearance A | 5/15 | 33.3% | 19.2% |
| Surface B | 20/20 | 100% observed | 76.9% |
| Joint ownership C | 20/20 | 100% observed | 76.9% |

The separate **whole-image frozen Phase 1 inventory already finds 21/26 easy bodies**;
its nearest-query correspondence loses four. C finds **three genuinely additional
easy bodies**, misses four that Phase 1 found, and gives a truth-evaluated union
of **24/26**. Thus C improves conditional correspondence precision and adds some
recovery; it does not dominate Phase 1's easy-body recall. No Phase 1 observation
is deleted. Phase 1 has 93 accepted observations overall, seven impure/false supports
and seven extra same-body observations; exact ownership ledgers survive.

At the frozen high-precision easy A1 point, recall is 76.9%, versus 65.4% for the
same-query frozen baseline, an 11.5-point difference. The three independent new
bodies are the more relevant recovery measure. Fixed-grid precision–recall curves
for all controls are saved; the held-out curves do not select a new threshold.

For C's correct strong easy detections, median location error is **.0111 diameter**,
mean supported-interior IoU **.770**, and mean pixel purity **1.000**. All lie inside
the deliberately broad .25-diameter radius. This locates the visible interior, not
the physical center. All-strong errors, contamination and coverage also survive in
supplemental data, so conditioning on correct detections cannot conceal failures.

Across sufficient A1 bodies: red **35/58**, yellow **46/56**, black **34/55**. These are
separate color results, not an instruction to prioritize hard black cases. Reported
colors among 115 correct strongs: 35 red, 40 yellow, 34 black, six unknown; zero wrong
named colors. No known or inferred repeating pattern enters these decisions.

## Increasing uncertainty exposes the remaining failures

| Easy tier, method C | Correct / strong | Recall | Observed precision |
|---|---:|---:|---:|
| A1 exact | 20/20 | 76.9% | 100% |
| A2 .10-diameter input shift | 16/20 | 61.5% | 80.0% |
| A2 .25-diameter shift | 11/14 | 42.3% | 78.6% |
| A2 .50-diameter shift | 9/10 | 34.6% | 90.0% |
| A3 scale .75, inverse scale alternative available | 24/24 | 92.3% | 100% |
| A3 scale 1.25, inverse scale alternative available | 20/20 | 76.9% | 100% |
| A3 roll −20° / +20°, inverse alternative available | 19/20 each | 73.1% | 95.0% |
| A3 camera inclination +15°, no camera refit | 6/21 | 23.1% | 28.6% |

The A3 scale/roll search explicitly includes the inverse perturbation; success does
not imply recovery from arbitrary unknown shape changes. Camera error is a genuine
unmodeled surface change. At .10 diameter, the four failed strongs are impure
supports, not majority-wrong-body assignments. Larger searches also increase
ambiguity: 34.6% at .25 diameter, 57.7% at .50. All methods use the same input scenes,
hypotheses and approximate search aperture. No simultaneous unconstrained fitting.

## False confirmations and absence: the blocking result

In A4, each contextual trial includes valid hypotheses and false alternatives:
paper shift, immediate-neighbor shift, midpoint insertion, duplicate identity,
wrong phase, wrong scale and wrong roll. **C has zero strong false confirmations
among the 182 easy-target alternatives**, but usually abstains on **both** the
correct and false owners. All easy duplicate/midpoint/phase/wrong-scale/wrong-roll
trials are ambiguous. This is a useful guard, not successful owner discrimination.
On those same 182 false alternatives, P confirms 121, A confirms 87, and B
confirms 112. The full tables/graph show their contributions. Counts also include separate moderate/hard strata.

Without the unchanged competing bank, an adversarial neighbor-identity permutation
produces **18/26 false strong confirmations** on easy targets. The surface/image
match can be excellent while its physical identity is wrong. An arbitrary identity
relabeling of identical geometry is not identifiable from those pixels alone;
anchored construction context must supply that information, and uncertain mappings
must remain alternatives.

The more direct post-freeze absence control removes one easy bead from each of
eight held-out scenes, rerenders the photograph and its independent truth, and
retains the original predictions. **A falsely confirms 5/8; B and C each 2/8.**
C returns three contradicted, two partial, one insufficient, and two strong false
confirmations. In the latter cases, newly exposed background bodies and seams
supply plausible pixels inside the absent bead's predicted surface. Those pixels
were occluded in the *predicted* scene, so the usual visible-support overlap guard
cannot protect them. This demonstrates why predicted occlusion cannot be treated
as observed ownership. The original and removed-body renders, all predictions,
and false confirmations remain reviewable. No operating point was retuned afterward.

## Actual photograph A5

Six automatically selected, geographically distributed large colored Phase 1
interiors initialize fresh local hypotheses. PCA supplies local orientation;
annular visible-surface centroids initialize uncertain translation. Each candidate
is scored only by seven frozen photographic interiors with one-to-one candidate
ownership, not brightness-maximum-as-physical-center fitting. Both hands, three
inclinations, 12 phases, two scales and a documented valid test pitch are explored;
all alternatives survive. One candidate per hand is retained, yielding 12 conditional
models. This underconstrained finite grid does not establish camera, pitch or hand.
All 29 context predictions survive; attention is on the six ±1/±6/±7 target sites.
There is no growth step or whole-necklace fit.

Raw crops, Phase 1 points, orange model surfaces, green measured pixels, location
uncertainty and alternative owners have separate viewer layers. Default synthetic
examples are easy; difficult evidence remains accessible separately. The static
panels show raw pixels beside annotations; no render substitutes for the photo.

Visual review of the selected positive-hand examples:

| Region | Photographic conclusion, independent of algorithm label |
|---|---|
| 00 | Supported red fragment on a substantial body; physical identity unresolved |
| 01 | Ambiguous: model support approaches the yellow/red interface |
| 02 | Ambiguous: predicted interior includes adjoining colored material |
| 03 | Ambiguous: body/black-seam ownership is not secured by the predicted outline |
| 04 | Supported yellow interior; physical identity unresolved |
| 05 | Ambiguous: mixed neighboring material and reflection context |

Some of these are algorithmically labeled **strong**. They remain failed/ambiguous
review examples, not silently corrected detections. The other hand and all negative/
partial/contradicted outputs survive. These are qualitative crop judgments, not
manual training labels or verified real-photo accuracy percentages. No geometric
index becomes an observed bead identity. The coarse geometry and photographic
appearance mismatch both remain plausible causes; this experiment does not uniquely
separate them on the real image.

## Decision and next bounded task

A1 demonstrates useful **conditional surface detection on easy synthetic beads**,
including three missed by Phase 1. It does not establish reliable presence of the
particular predicted physical bead. A2, camera-error A3, and especially removed-body
A4 block automatic growth. The successful packing audit removes one R279 confound;
it does not resolve the actual necklace's physical dimensions.

Next, keep easy central bodies and test a **target-present versus target-absent
local surface interpretation**, including surfaces newly exposed behind the target,
with anchored ownership alternatives. Measure a narrow 0–.1-diameter position range
and camera uncertainty separately, on new development and held-out scenes. Require
low false confirmation on removed-body cases before one-neighbor growth. Do not
increase parameter freedom, recover difficult fragments, or grow a connected chain
yet. A later incremental experiment should add exactly one ±1/±6/±7 neighbor from
at least three independently supported anchors, retaining both hands and absent/
non-neighbor alternatives; it is a recommendation, not executed work.

Validation: 11 focused scientific tests, complete native support/centroid audit,
independent POV/Python ray agreement, analytic contact witnesses, exact detector
replay, exact A5 replay, all prior-file hashes and a rendered 32-case browser review.
The browser test required sandbox escalation because Chromium launch was blocked;
it completed successfully afterward. Source code and reproduction details are linked
above. Stop after scoped commit/push and remote verification. Keep the current model
and reasoning setting; no `/new` is needed.
