# R284B — photographic interiors, boundaries and specular reflections

R284B is an isolated Phase1 comparison. **No alternative is adopted into the
production inventory.** R283/R284A implementations, records and review evidence
remain unchanged. Phase2 and Phase3 were not optimized or used to certify pixels.

Start with the [visual review](review/r284b/index.html). The three principal
panels are [colored tails](review/r284b/two-sided-focus.png),
[upper reflection](review/r284b/duplicate-focus.png), and
[wandering outline](review/r284b/abstention-focus.png). The important counterexample
is the [automatically selected weak reflection](review/r284b/auto-weak-anchor-1.png).
The complete, unabbreviated request is in [the specification](R284B_SPECIFICATION.md).

## Permanent scientific distinction

[PHASE1_MEASUREMENTS.md](PHASE1_MEASUREMENTS.md) is the permanent contract:
red/yellow supports are compact photographic interiors, not required full
silhouettes. **Black supports measure specular reflections only.** They never
include an inferred dark collar or body. Native masks, intensity fields, input
cues, peaks, mask centroids and subpixel contours remain separate. A highlight
centroid is not a physical bead center. Multiple reflections remain independent
observations with unresolved physical ownership.

Phase2 interprets geometry, correspondence and common lighting; Phase3 interprets
pattern from the uncertain physical inventory. Neither may manufacture or alter
independent Phase1 measurements. Every experimental record retains the R282 shared
schema, high importance, separate photographic/color/identity reliability,
visibility, discovery phase and provenance. Experimental reliability is explicitly
**unrated**, not a probability; numeric zero is the schema placeholder for an
unassigned score. Physical identity confidence remains zero and indices/centers
remain null. Historical R283/A collars appear only as labeled comparison baselines.

## Diagnosis and experiment design

The [452-word explanation](R284B_ALGORITHM_EXPLANATION.md) was saved before
replacement algorithms. [Checkpoint1](r284b/checkpoints/01-diagnosis.md) and seven
native diagnostic panels record thickness, restored rims, intensity and gradients:
[yellow1 profile](r284b/results/two-sided-bottom-cyan-spike-diagnosis.png),
[red2 profile](r284b/results/two-sided-left-red-crossing-diagnosis.png), and
[upper reflection](r284b/results/duplicate-upper-good-black-diagnosis.png).

The two reviewed tails are native support errors. Pre-A thickness radii are about
10px, but A caps opening at4px. Broad lobes survive. Restoring one pixel adds only
15/10 pixels to yellow1/red2, shifting the opened-core centroid0.158/0.122px: it is
not the main cause. Brightness valleys and renewed neighboring material are not
examined by the opening operation. For the upper black feature, A's67px mask has
10th-percentile linear Y≈0.002, including very dark material outside the reflection.

All alternatives share fixed image-only cues. They use ICC-managed linear
luminance and learned photographic pigment/background evidence. Native masks are
4-connected; measurements use unresampled pixels. Gaussian fields and subpixel
curves are separate derived quantities. No reviewed coordinates occur in the
inference module; the old review locations select evaluation figures only.

| Method | Mathematical idea | Main limitation exposed |
|---|---|---|
| A | Preserved R284A thickness-core opening plus bounded rim restoration | Broad tails and old clipping survive |
| T | Opening radius round(0.70 × maximum thickness), no restoration | Can remove genuine narrow material; ignores brightness |
| E | Connected flood carrying the best surviving path minimum; renewed rise >7% peak stops a path | Another connected route can bypass a valley |
| W | Watershed of negative smoothed Y with prominence markers | Missing markers cause leakage; multiple markers can partition one body |
| L | Geodesic active contour, image-gradient stopping plus curvature regularization | Notches, expansion and material-domain clipping |
| I | Local-background plus18% contrast isophote inside18px photographic domain | Red shading gets truncated; radius can clip bright material |
| J | I with24px domain: an explicit radius ablation, **not another independent method** | Repairs clipping locally but permits larger leakage elsewhere |

W solves a local competition for each cue; separate local solves can still overlap.
It is not a globally exclusive ownership partition.

E/W/L/I are four distinct brightness approaches. T/E/I/J also give several native
alternatives for the tails. The first pass restricted E/W/L/I to A dilated2px;
it inherited A's clipped edge. All ten failed-pass outputs and exact source are
preserved in [pass01](r284b/results/pass01). The subsequent domain experiment
retains that failure as evidence rather than overwriting its scientific record.

## Picture1 — preferred tail correction

The user prefers A as the starting point and requires all three observations.
T removes the lower-left protrusions without expanding into other material.
These are changes to native masks, not cosmetically smoothed lines.

| Reviewed observation | A pixels | T pixels | Removed | Retained | Centroid shift |
|---|---:|---:|---:|---:|---:|
| 1 lower yellow |516|471|45|91.3%|0.74px|
| 2 left red crossing the line |537|491|46|91.4%|0.52px|
| 3 right yellow |490|471|19|96.1%|0.12px|

All three remain near; the red and right-yellow **measured interiors** cross.
The lower-yellow interior lies on the positive side. These statements use native
support signed extent and nearest-line distance, not closest-centroid selection.
The complete physical silhouettes have not been measured.

E/W/L expand the unwanted regions. I/J remove the yellow tail, but retain only
200/537 red pixels and shift its centroid3.64px. The red neighbor in picture2
similarly shrinks435→228px. T is the preferred **local tail correction**, with
its broader truncation risk visible in the automatic validation. No exact fixed
number of beads is imposed at any station.

## Picture2 — reflection contours and secondary features

The user's R283/A preference replaces R284A's former recommendation of C for
black beads. Every new alternative measures reflection intensity only:

- **R1:** sigma0.65 linear-Y field,16% local peak contrast subpixel isophote;
  separate native16% peak-contrast mask. No dark dilation.
- **R2:** adaptive local Otsu intensity threshold, bounded below by R1's level;
  separate native threshold support. This often measures a smaller bright core.
- **R3:** gradient snake initialized from R1,64 arc-length samples,
  alpha0.025/beta0.25,180 iterations. A2.5px maximum-departure guard retains the
  starting contour on failure; native support also requires8% positive contrast.
- **R4:** competing reflection-intensity basins, followed by R1's intensity
  contour/native threshold inside the selected basin. Prominence is
  max(0.003,10% smoothed peak). Basins represent features, never bead identities.

| Upper reflection | R283 | A | R1 | R2 | R3 | R4 |
|---|---:|---:|---:|---:|---:|---:|
| Native area(px) |78|67|41|32|17|41|
| Centroid shift from A(px) |0.35|0|0.53|0.74|1.08|0.53|
| Mean native-boundary gradient |0.0403|0.0468|0.0823|0.0891|0.0687|0.0823|

R1 gives the most faithful isolated-reflection footprint among the original three:
it keeps the elongation and nearly the same location while removing dark rim
pixels. R2 is smoother but contracts toward the core. R3 contracts too far here.
A strong automatic reflection confirms that R1/R4 can preserve location while
removing a large historical dark collar (176→78 native pixels for R1).

The [lower secondary](review/r284b/secondary-focus.png) remains a photographic
feature: A32px, R1/R425px, R215px, R34px. R1/R4 shift its centroid1.95px toward the
actual elongated intensity feature. This is not a second certified physical bead,
and no nearby feature establishes same-bead ownership. The [red neighbor](review/r284b/red-neighbor-focus.png)
is shown separately, as requested. Review-based secondary status is evaluation
evidence; inference does not hardcode that location or ownership.

**Important failure and redesign:** in auto-weak, R1 connects the weak reflection
to a brighter upper highlight,129px with5.43px centroid shift. R3 inherits the
merger. R4 isolates22px with2.53px shift; R2 retains25px with0.93px shift. This
prevents a blanket recommendation of R1 alone. A two-Gaussian mathematical bridge
reproduces the merger and demonstrates R4's separation without physical identities.
The [saved mathematical bridge](r284b/results/synthetic-bridge.json) also shows
R2 can instead jump to a nearby component when its threshold excludes the weak
peak; that failure is preserved in the mathematical evidence.

R4 is the preferred **next reflection direction**, with R1 retained as the
isolated-feature reference. R4 has its own limitations: basin clipping, possible
fragmentation, one empty output, and greater perturbation sensitivity. Across46
black cues, mean directed contour movement under sigma0.50/0.80 and contrast±0.02
is R1≈0.066px, R2≈0.078px, R3≈0.315px, R4≈0.275px. These are algorithmic sensitivity
measurements, not calibrated error bars. R3's displacement guard rejects18/46
fits. Neither smoothness nor a larger gradient automatically raises reliability.

## Picture3 — brightness structure, clipping and neighbors

The user's assessment of B's smoothness does not approve its ownership or
splitting. E/W/L/I test different brightness mechanisms, with J isolating a domain
assumption. A's355px support has a leftward branch and a low edge inconsistent
with the continuing vertical brightness profile. T319px rounds the branch but
cannot recover the missing lower material. E414px is still limited; W545px grows
a new upper-left branch into the neighbor; L416px retains an artificial notch.

I350px removes the left branch but hits its18px search radius. J405px removes52
old pixels and adds102 photographically supported pixels below/around A, shifting
the centroid2.65px. Its mean boundary gradient0.0347 exceeds A0.0302 and its
boundary follows the observed intensity transition more convincingly. This is
**the strongest local result for picture3**, not a universal colored-bead rule:
J still truncates red interiors and creates oversized leaks on weak cues elsewhere.

## Additional real-photo validation and quantitative limits

Seven automatic cases supplement the three reviewed regions. Criteria and IDs
are frozen in [cases.json](r284b/results/cases.json): existing high red/yellow
crossing support, strong black near support, opposite-side pair, three-feature
station, weakest stored near black peak, and closest same-color cues at14..30px,
with180px separation from earlier case centers. No manual label is an algorithm
input. Eleven selected-anchor panels show native supports, contours and profiles;
all249 cues are also visible in the ten full overviews.

Selection is conditional on existing image-only observations, including bad cues;
this is not blind whole-photo recall validation. An initial selector read a
nonexistent peak field and tied by ID; its two affected case outputs survive in
[selection-control](r284b/results/selection-control). It was corrected to the
stored native `illumination.peak` before the final weak-case evaluation. A
same-color selected cue proves unreliable near a reflection/material interface;
it is retained as a failure, not replaced with an easier example.

The249 unique input cues comprise130 red,73 yellow and46 black. All have high
importance but **none is newly certified or assigned a calibrated reliability**.
The following counts are diagnostic supports within the870px ceiling, including
unresolved cues. Overlaps mean shared pixels between proposals, not independently
verified leakage. Marker multiplicity means possible false partition, not proven
extra beads. Native mask connectedness is checked; physical ownership remains open.

| Color / method | Nonempty ≤870 | Near | Measured crossing | Same-color overlap pairs | Mean centroid shift |
|---|---:|---:|---:|---:|---:|
| red A | 130 | 31 | 14 | 59 | 0.00px |
| red T | 130 | 30 | 12 | 51 | 0.61px |
| red E | 115 | 31 | 14 | 70 | 2.05px |
| red W | 106 | 29 | 15 | 71 | 2.51px |
| red L | 118 | 32 | 17 | 85 | 1.72px |
| red I | 129 | 29 | 10 | 65 | 3.60px |
| red J | 106 | 28 | 9 | 79 | 4.64px |
| yellow A | 73 | 39 | 22 | 29 | 0.00px |
| yellow T | 73 | 39 | 20 | 21 | 0.67px |
| yellow E | 68 | 36 | 22 | 37 | 1.29px |
| yellow W | 68 | 37 | 22 | 47 | 1.84px |
| yellow L | 73 | 42 | 25 | 38 | 1.52px |
| yellow I | 73 | 41 | 22 | 23 | 1.74px |
| yellow J | 73 | 41 | 22 | 27 | 2.76px |
| black R283 | 42 | 23 | 10 | 1 | 0.16px |
| black A | 46 | 25 | 11 | 1 | 0.00px |
| black R1 | 46 | 22 | 9 | 1 | 1.05px |
| black R2 | 45 | 21 | 8 | 0 | 0.86px |
| black R3 | 42 | 22 | 7 | 1 | 1.14px |
| black R4 | 45 | 22 | 8 | 0 | 1.17px |

T reduces same-color overlap pairs red59→51 and yellow29→21, but can shrink away
crossing evidence: colored crossings36→32. E/W/L frequently expand overlaps;
W has42 marker-multiplicity flags. J produces23 red proposals over870px, all
rejected as oversized diagnostics. R1 retains46/46 nonempty black features, R4
45/46, but no physical-bead precision/recall follows from this. R4 removes the
one remaining black pair overlap in this case set. One inherited black cue has
a material-ineligible peak; its explicit flag prevents any reliability claim.

The clear automatic red example shows I/J producing an artificial crescent;
the automatic yellow shows E/W leaking into an adjacent yellow. The strong black
example supports R1/R4; the weak example exposes their difference. Full overviews
also expose paper-facing inherited proposals. False-positive color/seed evidence
is unresolved rather than hidden by a smooth contour.

## Centerline recovery: what improved and what remains unknown

Native geometry, signed side, longitudinal station and frozen local support scale
are retained. Near means minimum support distance≤half the nearest R283 scale.
Every observation is counted once per method; an observation may flank another
without its centroid being closest to the line. No two/three quota is enforced.

A+A gives95 near candidate features (47 measured crossings); T+R4 gives91
(40 measured crossings), with15 disjoint opposite-side candidate pairs versus17.
These counts include uncertain cues. They are **not evidence that fewer physical
beads exist**: compact colored interiors and reflection-only masks can lose line
intersection while their full bodies still cross. Black-body crossing is null.
The reviewed three observations remain represented, but this experiment does not
establish recovery of every crossing bead. Missing-seed discovery and calibrated
real distinct-body ownership remain unresolved. One nearby feature never proves
complete local coverage.

## Recommendation and stopping point

1. Prefer **T** for the reviewed colored-tail repair: native changes are small,
   all three observations remain, and the protrusions disappear. Do not adopt
   its stronger erosion globally without the user's choice and further validation.
2. Prefer **R4** as the reflection-separation direction, keeping **R1** as the
   isolated-reflection reference. R4 fixes the weak/strong merger but needs
   explicit basin-clipping/peak-eligibility/instability abstention.
3. Keep **J** as the best picture3 demonstration and a useful redesign clue:
   photo-supported transitions must replace inherited radial cutoffs. Its red
   truncation and leakage disqualify it as a general production replacement.

After user selection, the proposed bounded next step is to combine only the
chosen measurement rules with explicit ownership/clipping/merge uncertainty,
then test crossing-support losses and missing cues on a new automatic case set.
Do not proceed now to a whole-inventory replacement, physical fitting or patterns.

## Reproduction and verification

Run from repository root with the existing Python3.12 environment:

```sh
.venv/bin/python -m photo2.r284b.diagnose
.venv/bin/python -m photo2.r284b.synthetic
.venv/bin/python -m photo2.r284b.run
.venv/bin/python -m photo2.r284b.review
.venv/bin/python -m photo2.r284b.validate_photo
.venv/bin/python -m photo2.r284b.package
.venv/bin/python -m unittest photo2.r284b.tests photo2.r284.tests photo2.r283.tests photo2.r282.tests
.venv/bin/python -m photo2.r284b.audit
/home/rharris/.local/bin/beads-chromium-review photo2.r2840.browser_check
```

The numeric `r2840` module is only an adapter for the existing authorized browser
launcher; scientific code/results are under `r284b`. No broad browser permission
or launcher modification is needed. Freeze records include photo/ICC/input/source
hashes and parameters. Exact native runs, intensities, subpixel contours, peaks,
perturbations, centroids, side/station evidence and pair conflicts are saved in
per-case compressed JSON. `--output` supports independent reruns.

The mathematical tests cover branch removal without invented material, brightness
saddles, connectedness, multiple-feature splitting warnings, native reflection
contrast, translation, weak-feature retention, subpixel/native separation and the
weak/bright merger control. Saved-record tests enforce the permanent phase
contract. Final checks:59 scientific tests,15 exact replay files,9916 unchanged historical
Git blobs,10 pixel-exact native crops, and36 browser images/16 tables/10 cases.
[Audit](r284b/results/audit.json), [browser record](r284b/results/browser-check.json),
and [checkpoint6](r284b/checkpoints/06-recommendation.md) preserve the evidence. All failed alternatives remain reviewable.

**Stop for the user's method selection after scoped commit/push and remote
verification. Keep the current model/reasoning setting; no `/new` is needed.**
