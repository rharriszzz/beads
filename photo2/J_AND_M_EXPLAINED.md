# Methods J and M: what they measure, how they work, and why they fail

This explanation describes the frozen methods through R287. It was completed
before R288 segmentation changes. The [permanent measurement contract](PHASE1_MEASUREMENTS.md)
is authoritative; [R287's review](review/r287/index.html) provides the photographs.
The important distinction is between an image feature, a segmented photographic
interior, and a physical bead. Neither J nor M establishes the last of these.

## The measurement problem

For a colored bead, Phase 1 seeks a trustworthy set of native image pixels and a
representative photographic location. It need not recover the whole silhouette.
A packed necklace presents partially occluded, curved, reflective surfaces. A
small white highlight can be several times brighter than the surrounding red
pigment. Two adjacent yellow beads may have indistinguishable hue. Their illuminated
surfaces can connect around a dark seam. Conversely, one bead may contain a dark
hole, texture or shaded patch. Blur weakens separations, noise creates extrema,
and one surface can produce several brightness maxima.

The pixels supply color, intensity and spatial transitions. They do not supply
physical ownership. Learned pigment prototypes, thresholds, search windows,
connectivity, marker prominence and rules for joining regions are algorithmic
assumptions. Even a perfectly stable contour can assign two surfaces to one bead.
Likewise, a small contour can be accurate as an illuminated patch but inadequate
as the intended representative diffuse interior.

Black beads have a different target: Phase 1 measures their **specular reflections
only**, with separate native intensity support and uncertain physical ownership.
J/M are colored-interior methods. Neither should grow a black reflection into a
speculative body. Phase 2 later fits geometry, camera and common lighting to these
independent measurements; Phase 3 uses uncertain physical identities for pattern
inference. Neither later phase may manufacture Phase 1 observations.

## Shared inputs and coordinate conventions

The decoder applies EXIF orientation. Review crops preserve original decoded RGB;
measurement RGB is converted through the embedded ICC profile to sRGB, using
relative colorimetric rendering. See [`photo()`](r282/common.py). Coordinates are
native pixel centers, x right and y down; a pixel is not a physical length unit.

[`image_features()`](r282/phase1.py) computes HSV from encoded sRGB and luminance
from linear RGB. For an encoded channel c in [0,1],

\[
c_{lin}=\begin{cases}c/12.92&c\le0.04045\\((c+0.055)/1.055)^{2.4}&\text{otherwise},\end{cases}
\qquad Y=.2126R_{lin}+.7152G_{lin}+.0722B_{lin}.
\]

Thus Y is a relative photographic intensity, not calibrated incident illumination.
Circular hue distance is the shorter angular distance on a 360-degree circle.
Background hue is estimated from saturated border samples. A native paper mask
uses proximity within 22 degrees, saturation above .18 and Y above .035. Two
pigment prototypes come from a smoothed, subsampled hue histogram excluding likely
background. Their names are assigned by proximity to red hue. This learns peaks
from this image, but the two-color assumption and semantic naming are priors;
this is not demonstrated palette-independent recognition.

The input cue comes from the preserved automatic photographic candidate inventory,
not a fitted physical bead center. R287 reuses R283 cues and earlier image-only
review observations. Its confirmation selection uses photo exposure, support-near
geometry and reproducible hash ranking. A source status of “high” is provenance,
not a new ground-truth label. Cue discovery and support segmentation are separate
problems: a good segmenter cannot recover a bead for which no suitable cue is tried.

## J: a local contrast isophote

The executable replay is [`produce()`](r287/candidates.py); its source is
[`colored(..., variant='J')`](r284b/methods.py), with photographic domain construction
in [`old_control()`](r285/run.py). The adapter reproduces the saved controls.

1. **Material eligibility.** In a 49×49 window, estimate a native intensity peak
   within four pixels of the cue. Pigment requires saturation >.27, hue distance
   <24 degrees from its learned prototype, at least a two-degree advantage over
   the rival pigment, no paper, and Y > max(.012, .09×peak). A limited neutral
   continuation admits saturation <.35, Y > max(.06, .45×peak), within eight pixels
   of the cue and three pixels of pigment. Neutral highlights may otherwise fail hue.
2. **Noise-scale field and peak.** Gaussian-smooth Y with sigma .65 native pixels.
   Find the largest smoothed value within radius four of the cue; call its position
   p and value P. This is a local maximum search, not a global best-bead search.
3. **Background reference.** Retain the historical photographic A support. Dilate
   it by three iterations and subtract A to form a ring R. Let
   b = quantile_0.20(Y_sigma on R), or zero if the ring is empty. A was generated
   using earlier compact-support rules. Its shape therefore affects J indirectly,
   even though J does not simply reuse A's outline.
4. **Threshold and connection.** Set

\[
T_J=\max(.012,\ b+.18\max(0,P-b)),\qquad
S_J=CC_p\{x\in D_J:Y_\sigma(x)\ge T_J\}.
\]

   The pigment domain has radius 24; neutral eligibility is additionally bounded.
   Connected components use four-neighbor adjacency. Crucially, the historical
   [`component()`](r282/phase1.py) may substitute the nearest eligible component
   within six pixels if p is excluded. This is a control behavior, not guaranteed
   preservation of the original feature's ownership.
5. **Measurement.** Save the exact native mask. The displayed contour comes from
   marching squares at .5 on the padded binary mask, choosing its longest curve
   ([`contour()`](r284b/methods.py)). It is not a fitted ellipse or a full physical
   boundary. The measured location is the unweighted area centroid,
   c = (1/|S|) sum_{x in S} x, not the highlight peak or physical bead center.

The constants have engineering roles: .65 suppresses subpixel-scale noise; .18
chooses a fraction of local contrast; .012 excludes very dim material; hue margins
limit material confusion; 24 controls computation and intended locality. None is
a universal optical law. The search circle can clip still-bright material and must
not be interpreted as a photographed edge. J does not perform explicit neighboring
bead competition. Clipping, component substitution and perturbation sensitivity
are recorded externally, rather than resolved by the isophote itself.

J often stops well because a dark seam falls below T_J, disconnecting the target
from another surface. But any surviving route above the same threshold reconnects
them. A high specular P can also raise T_J above much of a valid red diffuse surface.
For example, b=.02 and P=.8 give T_J=.1604; pigment with Y=.10 is rejected despite
being clearly red. This numerical illustration explains the mechanism, not a
calibration of the reviewed bead.

## M: diffuse intensity, markers and watershed competition

M comprises [`measurements()`](r285/methods.py) followed by
[`marker_field()` and `watershed_support(..., protected=False)`](r286/methods.py).
S was its predecessor; B uses the same repaired markers with a stronger separation
rule. M does not reconstruct diffuse illumination physically. It uses a robust
local intensity statistic intended to reduce the influence of isolated highlights.

**Material and diffuse reference.** Pigment requires saturation >.24, hue distance
<28 degrees, closer to its prototype than the rival, an eight-degree advantage over
background hue, and no paper. In a radius-eight neighborhood of the input cue,
take the 60th percentile of smoothed pigment Y as D. A sparse bright peak has less
influence than on J's maximum P, although a broad highlight can still bias D.

Let b be the 10th percentile of smoothed Y in the annulus of radii 10–24. This
annulus samples the photograph, not necessarily the physical background: it may
contain shadows, other beads or dark body material. Estimate noise as the median
absolute difference between Y and its 3×3 median-filtered version. Then

\[
f=\max(.001,3\operatorname{median}|Y-\operatorname{median}_3Y|),\qquad
T_M=\max(f,b+.20\max(0,D-b)).
\]

Eligible material is pigment or bounded neutral continuation, above T_M. Neutral
continuation requires saturation <.40, Y>D, distance at most two pixels from
pigment, and no paper. The seed is refined to the brightest eligible pigment within
radius four. If none exists, M returns no support rather than borrowing a remote
component. The baseline computation window is 97×97; smaller/larger-domain checks
measure dependence on that finite boundary.

**Photographic markers.** Compute h-maxima of L=log(Y_sigma+.003), with prominence
h=.20. The log field makes prominence roughly relative in intensity, although the
.003 offset matters in dark regions. Prominence concerns the drop needed to reach
a higher peak, not simply whether a pixel exceeds its eight neighbors.

S intersected the maximum pixels with eligibility. That erased legitimate tinted
peaks. M instead examines each maximum's radius-three neighborhood. An eligible
peak becomes a marker directly. A non-paper peak whose neighborhood is at least
half pigment can project to the nearest eligible pixel within that neighborhood;
brightness breaks equal-distance ties. Unsupported peaks remain in the ledger.
Coincident projections share a marker. A marker within five pixels of the refined
cue is the target; otherwise the cue supplies a marker. These are photographic
features, never an assertion of one bead per maximum.

**Watershed.** Flood the topography -L from the markers, restricted to eligible
material. High-intensity maxima become low points of this inverted surface. Pixels
receive basin labels as the floods advance and meet. This supplies competing
regions, but the basins are not yet separate physical objects. A single bead's two
highlights can generate two basins; an unmarked neighboring bead can fall entirely
inside the target basin.

**Saddles and merging.** For each basin i, estimate reference D_i as the 60th
percentile of pigment intensity in its radius-six marker neighborhood, restricted
to that basin. For adjacent basins i,j, inspect four-neighbor pixel pairs (u,v)
across their interface. The implemented maximum-saddle statistic is

\[
s_{ij}=\max_{(u,v)\in E_{ij}}\min(Y_\sigma(u),Y_\sigma(v)),\qquad
r_{ij}=s_{ij}/\min(D_i,D_j).
\]

An interface with at least three pairs is kept separate when r_ij<.65; otherwise
its basins may merge. The maximum is deliberate: a single sufficiently bright
connection can count as continuity despite darker portions elsewhere. On the
basin adjacency graph, successive unions also create indirect connections. M's
separations are not immutable cannot-links; another sequence of unions can join
basins despite a dark direct interface. B adds that protection and evaluates the
distribution of interface brightness, but can consequently split internal shading.

For example, let weaker diffuse reference be .30. Interface pair minima
[.04,.05,.06,.07] give r=.233 and a separation. Adding one route with a pair minimum
.24 gives r=.80 and permits merging. Most of the visible seam remains dark. This
is why a bright detour can defeat a visually convincing separation. If the second
surface lacks a marker, there is no corresponding interface test at all.

The final support contains the target's merged basin group, minus dark interface
pixels between surviving separate groups, then only the seed-connected component.
Its native mask, contour and area centroid use the same measurement conventions
as J. Marker ledgers, references, interface pixels, union outcomes and flags remain
available. Neither M nor its uncalibrated reliability fields certify physical identity.

## Comparison at a glance

|Question|J|M|
|---|---|---|
|Core assumption|One local isophote isolates useful material|Diffuse eligibility plus competing intensity basins isolates useful material|
|Brightness|Peak-relative threshold|Diffuse-percentile threshold and relative saddles|
|Color|Learned pigment gates; restricted neutral continuation|Similar, somewhat broader gates plus background-hue margin|
|Specular peaks|Can dominate threshold|Reduced influence, not physically separated|
|Diffuse material|Often excluded when much dimmer than peak|Usually retained by lower diffuse-based floor|
|Neighbors|Connectivity only|Explicit markers/basins, but missing markers remain dangerous|
|Local maxima|One radius-four peak|Multiple log-prominent maxima plus supported input cue|
|Dark valleys|Below-threshold disconnection|Eligibility and maximum interface saddle|
|Shadows|Can truncate or lower reference into merger|Can create false basins or change diffuse/background estimates|
|Same-color neighbors|Color cannot distinguish them|Competition can help; color still cannot establish ownership|
|Seed changes|Move peak, ring alignment and domain|Move diffuse sampling, refinement, target and window|
|Background changes|Inherited A ring can shift threshold|Annular baseline changes eligibility and basin topology|
|Search boundaries|Explicit radius 24 plus window|Finite square window; outside features unavailable|
|Cost for n pixels|Filtering/components approximately O(n) for fixed kernels|Watershed typically O(n log n), plus marker/interface processing|
|Uncertainty|Mask plus external flags/alternatives|Mask plus feature/merge ledger and external flags/alternatives|

Quantiles also require selection/sorting; library implementation affects exact cost.
The small local windows dominate practical runtime, while repeating all perturbations
multiplies cost. Both methods share color gating, Gaussian smoothing, connected
native support and photographic centroids. Neither knows true body count, occluded
extent, or whether two acceptable features share one bead. A basin partition is
an algorithmic partition, not a physical proof.

## What the experiments establish—and what remains hypothetical

**J's highlight truncation:** [P2](review/r287/P2-choice.png) has J200 versus
M/S495 pixels. [R285](R285_REPORT.md) established the peak-versus-diffuse mechanism;
R287's direct color/intensity routes support all 295 added pigment pixels. Its first
selector nevertheless rejected the darker continuation by requiring too high an
outside/inside brightness ratio. The revised route test allowed monotonic shading.
That corrected this preference, not all colored ownership.

**J's domain and background defects:** R285 recorded 89 radius-contact cases in
its full candidate bank. A flat/circular boundary on continuing material is a
computation artifact. Enlarging the domain alone sometimes includes a neighbor.
The A-ring dependence is explicit in code; perturbations establish sensitivity,
not that every inherited ring is wrong. A weak threshold can leave two surfaces
connected. N10 shows J reaching neighboring material while the smaller M is better.

**P5's missing markers:** [the causal diagnosis](R286_P5_DIAGNOSIS.md) showed S
merging three yellows into 1817 pixels. Two maxima missed the hue gate by .47 and
.16 degrees, despite 89.7% and 96.6% pigment neighborhoods. Dark straight routes
existed, but brighter detours survived the material floor. The target occupied
one basin before merging, so changing the saddle threshold would not address the
cause. M's context repair produces 664 pixels while preserving P2 exactly. However,
[R287's perturbation image](review/r287/P5-stability.png) shows renewed mergers under
small parameter changes. Marker repair improved a demonstrated defect, not general
separation reliability.

**M's instability and extensions:** [N07](review/r287/N07-evidence.png) contains
J288/M515 pixels, with 227 directly supported additions. Background-low makes M1325;
seed-right makes M1275. [N11](review/r287/N11-evidence.png) contains J167/M694,
including a questionable upper extension; one background change makes M2018.
These observations establish discontinuous output changes. Before R288's detailed
ledger replay, the exact attribution to marker loss, target changes or basin unions
is still to be diagnosed. The upper extension's physical ownership is likewise not
established by its area or by a visually plausible contour. R288 will inspect native
profiles and identify which pixels change, rather than treating all M material as bad.

**Internal-shading false splits:** R286's mathematical controls demonstrate B
splitting shallow shading that M retains. This is specifically a B regression, not
proof that M made that same error there. M/S also cannot distinguish identical
pixels assigned hypothetical “deep internal texture” versus “two bodies” truth.
A stronger separation rule can therefore trade mergers for false partitions.

**Selector failure:** R287 vetoed unstable M and automatically preferred surviving
J in N07/N11. That is a decision-layer defect: evidence against M was substituted
for evidence that J is adequate. Both supports can have independent defects. N06
shows the other side: M merges yellow neighbors and J separates them. A correction
that merely grows all undersized J masks would reintroduce such mergers.

**Shared upstream failures:** a tinted reflection can be assigned colored-cue
metadata, as in the weak N06 neighboring cue. Multiple cues can describe one body
(C07 overlaps); smooth same-color supports can still cross bodies (C04). These are
seed/color and correspondence ambiguities as well as segmentation problems.
Plausible masks alone cannot certify distinct-bead recovery. All masks, perturbations
and decisions are saved in [R287 data](r287/results/confirmation.json.gz).

## What to try next and what cannot be inferred

Single-view intensity is the product of material, illumination, surface orientation,
visibility and imaging. Different surfaces can generate nearly identical pixels.
An identical dark region can be explained by a seam or internal shading. No threshold,
watershed or smoothness penalty can recover information absent from the photograph.
Abstention and competing photographic hypotheses are legitimate measurements.

Concrete next experiments follow the failure mechanisms:

- Replay N07/N11 perturbations with marker and union ledgers; separate stable diffuse
  pixels from unstable extensions. Test an ensemble-stable core with independent
  pigment/route evidence, rather than intersecting J and M merely for compactness.
- Compare seam-constrained competition against M's maximum-saddle unions. Retain
  uncertainty when a competitor is weak or could be another reflection on one bead;
  check shallow-shading controls to expose B-like false splits.
- Audit background-reference changes separately from marker changes. A robust
  estimator or parameter ensemble should preserve P2's diffuse material and N06/P5
  separations, rather than tune one absolute cutoff to a reviewed crop.
- Keep J inadequacy as a separate decision variable. If continuous diffuse pigment
  lies beyond J but M's ownership is unstable, construct a justified new interior
  or abstain; instability is not an instruction to return J.
- Improve cues only with independent image evidence and explicit duplicate hypotheses.
  Phase 2 may later compare physical correspondences and lighting, but those
  interpretations must link and preserve the original photographic observations.

Frozen confirmation on new central regions, with all failures retained, is required
before recommending any change. Better-looking outlines and larger coverage counts
are insufficient. The next useful result is a more trustworthy measurement with an
honest account of what remains outside it and why.
