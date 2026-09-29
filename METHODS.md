# Methods collection — bead-rope reconstruction

This is the reusable method index. The task and maker's construction facts live
in [INITIAL_QUESTION.md](INITIAL_QUESTION.md); current execution priorities live
in [PLAN.md](PLAN.md). Start each future entry with its inputs, output, assumptions,
procedure, known failures, validation and a reproduction link. Distinguish a
proposal from an implemented procedure and a validated capability.

Start with [background methods](#background-pixels-under-varying-illumination),
[shadow handling for splines](#shadowed-paper-alternatives-and-evaluation-for-splines),
[bead methods given a centerline](#bead-analysis-given-approximate-boundaries-and-a-centerline),
[index and color assignment](#assign-bead_index-and-color-to-clearly-visible-beads),
[shortest repeat](#shortest-color-pattern-from-indexed-observations), or
[POV-Ray appearance](#fit-paper-bead-materials-and-lighting-in-pov-ray).

**R111 clarification:** explore FFTs for background/shadows and for directions/
spacings/helicity, alongside non-FFT alternatives. Adoption is optional in either
use; an FFT result is not a prerequisite for the index/color pilot below.

**Execution order (R113):** this is a method catalog, not a requirement to run
every section in document order. The next bounded task is the
[local observation/index/color pilot](#outputs-evaluation-and-the-bounded-first-pilot).
[PLAN.md](PLAN.md) defines its evidence requirements, stopping point and later
checkpoints. Background bridges and the two FFT explorations supply evidence
where useful; neither a perfect mask nor adopting FFTs is a prerequisite.

## Background pixels under varying illumination

**Background means every visible part of the paper**, including cast shadows,
the enclosed center and gaps between beads. It does not mean “magenta,” “bright,”
or merely “connected to the image border.” The maker now supplies a useful
framing assumption: all rendered and actual images have the bracelet in the
middle with substantial margins. Margin width is unspecified. A narrow perimeter
sample can initialize a background model without fixed bead coordinates; check
several inset widths rather than assuming a particular percentage is clear.
Margin samples need not cover the illumination or texture of every interior patch.

**R108 purpose:** the immediate output is a useful smooth necklace spline,
without systematic displacement into cast shadow. A perfect pixel mask is not a
prerequisite: reliable boundary stretches can constrain a coarse curve while
ambiguous stretches and tiny gaps wait for later bead/geometry refinement.
Measure success at the spline as well as at the pixels. The shadow-specific
comparison and recommendation below explain how.

The goal is illumination robustness, not a promise of unique classification
under literally every possible light. Where paper and beads produce identical
observations, or clipping/blackness removes the evidence, one photograph cannot
supply a certain label. Use **paper / bead / unresolved** with supporting scores;
do not present an uncalibrated score as a probability. A geometrically inferred
paper label should be marked differently from one supported by local appearance.
For blurred boundary pixels, retain uncertainty rather than pretending that each
mixed pixel depicts a single surface.

### Five different methods

These differ in the evidence that makes the decision. They can later be combined,
but compare their standalone failures first. None is yet a validated whole-image
background classifier on this branch.

| Method | Main evidence | How it uses the margins | Illumination limitation | Status |
| --- | --- | --- | --- | --- |
| 1. Fit paper appearance while allowing shading | Paper reflectance/texture consistent with a local lighting field | Learn appearance from several perimeter regions | Abrupt/colored illumination and bead colors can fit the same model | Proposed; old fixed-HSV masks are a separate baseline |
| 2. Gaussian-window spectral texture | Maker's raw-window low-pass power fraction; detrended texture as a separate comparison | Learn paper spectra and noise distributions | Hard shadows change spectra; weak dark signals remain ambiguous | Existing explorer baseline found in R110; beads probes use different statistics |
| 3. Spatial texture and local ordering | Small-scale structure across several spatial scales | Learn distribution of paper residuals and local order changes | Paper grain, sharp shadows, clipping and low signal | Gaussian residual implemented; ordering extension proposed |
| 4. Seeded region propagation | Agreement of neighboring regions with paper/bead evidence | Start with known exterior-paper seeds | Can leak across weak edges; enclosed paper needs separate support | Proposed; not just a border flood fill |
| 5. Boundary anchors and smooth envelope completion | Reliable silhouette sections plus larger-scale geometry | Establish exterior side and reject contour excursions into clear margins | Smooth wrong outlines are possible; small gaps need separate treatment | Pending supporting comparison when geometry needs it; bridge not yet fitted |

### 1. Fit paper appearance while allowing shading

**Inputs:** image and generic perimeter samples, with optional automatically
selected interior patches. **Output:** paper-model compatibility and residual
maps, with explicit unresolved regions.

Start with separated perimeter patches so one noisy or shadowed patch cannot set
a universal maximum. Estimate a robust paper texture/noise distribution and color
model from this image. One simple model in approximately linear RGB is
`I_c(x) ≈ a_c(x) * P_c + noise`, where `P` is the estimated paper reflectance
color and `a` describes illumination. For neutral lighting start with one scalar
`a(x)` shared across channels; allow a slowly varying channel-dependent field
only when the data support it. Permit lower illumination in cast-shadow regions
instead of labeling every brightness drop foreground. Fit robustly so central
beads do not redefine the paper model; keep a held-out margin subset for checking.

Compare each patch to the predicted paper color **and texture**, using relative
chromatic change as optional evidence. No stored magenta/red bounds are inputs.
The scalar model explains brightness changes only under its assumptions; JPEG
processing, colored interreflection and mixtures of lights can violate them.
An unconstrained per-pixel RGB field would explain everything and classify
nothing, so illumination flexibility must be limited and reported.

**Test:** hold the paper/bead geometry fixed and vary exposure, light color,
shadow softness and background pigment independently. Report dark-bead false
background and shadowed-paper false foreground separately. Compare with color
features disabled. A hard shadow may require another method to establish which
surface continues across it.

#### The maker's line-to-HSV-region proposal (R107)

Draw a line across a clear image margin and sample a narrow strip around it.
Store the sample coordinates and HSV values, then build an enclosing acceptance
region in color space. Membership tests elsewhere in the image give a
**paper-color compatibility map**. This is an image-trained version of method 1;
using accepted samples as spatial seeds also connects it to method 4. A line near
an object boundary must first be checked to remain on paper; proximity alone is
not a background label.

| HSV region | Advantage | Risk / assessment |
| --- | --- | --- |
| Separate H/S/V ranges | Transparent, cheap baseline resembling the earlier manual tools | Admits unseen combinations inside the box; extending V downward can swallow dark beads |
| Convex hull around samples | Captures correlations that a box misses | Fills empty space between distinct lighting clusters; an extreme sample can enlarge it; a thin sampled cloud needs tolerance |
| Union of local clusters or a smooth density region | Can preserve separate lit/shadow modes and curved correlations | Needs enough samples and a tolerance/bandwidth; rare valid shadows can be rejected as low-density |

I would compare a simple box with a **smoothed density region**, using circular
hue and an explicit tolerance for sampling/noise. Do not make every observation,
including JPEG outliers or an accidental bead pixel, expand the accepted region
without inspection. Retain rejected samples and their locations for review.
Hue must wrap at 0/360 degrees, and its contribution should decrease for weak
chroma/near-black samples. Document H/S/V units. A smoothed circular-H histogram
is one possible implementation; it has not been implemented here.

Learn from several separated strips and retain lit/shadow sample provenance.
Check on held-out strips, not adjacent pixels from the same strip. A richer HSV
region still cannot distinguish the maker's overlapping red-bead and shadowed-
paper colors. Neither membership nor nonmembership is a final label: a point
outside the region may simply be paper under an unobserved illumination.

### 2. Gaussian-window spectral texture

**Inputs:** grayscale/local channel images, window scales and frequencies;
perimeter spectral controls. **Output:** maps of texture excess, spectral shape
and uncertainty across scales, not a thresholded contour by default.

Start with the maker's `r = 0.05 * sqrt(width * height)`; explicitly state whether
`r` is sigma. The existing convention is a spatial Gaussian window with sigma
`r`, not simply a Gaussian blur of the image. **R110 clarifies the maker's useful
background method: Gaussian-window FFT, low-pass filtering and a power score.**
The inspected explorer scanner computes the fraction inside the central disk,
named `hp_removed` because it is the power removed by a complementary high-pass
mask. It uses raw windowed luminance, without subtracting a fitted plane.

When testing FFT, include that source baseline so changes are compared fairly.
Its adoption is optional under R111. For the same spectrum and hard
cutoff, low-pass retained fraction equals one minus high-pass retained fraction;
this connects the latest description to the earlier central-removal description.
Absolute power and fractions are different, and the maker's exact historical
interactive settings are not all known. [Source review, formulas and one saved
configuration](photo2/FFT_EXPLORER_NOTES.md) make these distinctions explicit.

Compare weighted-mean/plane removal and retained texture bands as **separate
variants**, not silent replacements. Also retain directional organization.
Keep absolute power and normalized spectral shape separate.
Use a noise floor and minimum signal requirement before normalizing weak spectra.
Estimate paper reference distributions from multiple separated margin regions;
check interior shadow controls before extending that reference across the image.

Shrink windows near transitions, comparing several sizes. Large windows identify
neighborhood texture; their tails can include beads even with the center on paper.
Small windows can miss dark smooth bead interiors. A strong response may be paper
grain or a hard shadow, so directional/persistence evidence and uncertainty matter.
Do not identify a boundary by connecting independently thresholded window centers.

**Existing evidence:** [initial FFT probe](photo2/BACKGROUND_METHODS.md),
[transition comparison](photo2/BACKGROUND_TRANSITIONS.md), and
[parallel/reference sensitivity](photo2/PARALLEL_PATHS.md). Removing only DC
left 65.7–99.5% of a constant patch's windowed raw power in the R099 controls:
the Gaussian window broadens the central feature. Weighted-plane subtraction
removes this control response. Detrended power fractions alone still confuse weak
paper texture with bead texture. Reference replacement moved crossings by up to
32 original pixels in R104. These results support keeping the controls, not a
claim that FFT reliably classifies every point. Directional 1/6/7 analysis is a
separate future use; radial power sums cannot recover helicity.

**Test:** constant/gradient patches, independent brightness scaling, paper grain,
soft/hard shadow edges and dark beads, followed by held-out POV-Ray masks. Show
frequency exclusions, raw patch and scale disagreement in the review images.

### 3. Spatial texture and local ordering

**Inputs:** image and spatial neighborhoods at several scales. **Output:** local
structure features and paper compatibility, with weak-signal pixels unresolved.

Compute Gaussian residuals `I - G_sigma(I)` or differences between two blur
scales. Summarize their energy and oriented gradients in local windows. Add a
separate descriptor of neighboring pixel order: whether a neighbor is brighter
or darker than a local reference, ignoring comparisons smaller than a measured
noise tolerance. Under a strictly increasing intensity transformation applied
uniformly to the neighborhood, order is preserved. Spatially changing shadow,
noise and clipping do not satisfy that condition.

Compare scale profiles and ordering statistics to margin paper. Contrast
normalization can reduce exposure dependence, but cap its gain near black so
noise is not amplified into “bead texture.” A spatial filter stack is the simpler
baseline against which to judge the extra FFT cost. Repeated curved bead-scale
edges may help distinguish beads from a single broad shadow edge; that is a
hypothesis to test, not a guaranteed visual signature.

**Existing evidence:** R099/R104 implement a sigma-4 blur residual with different
measurement-window sizes. The ordering descriptor, automatic scale selection and
whole-image margin calibration have not been implemented. Small-window spatial
texture missed the provisional dark T3 start under some thresholds.

**Test:** paired exposure variants, same-color/black beads, grainy paper and a
paper-only sharp shadow. Compare spatial-only and FFT-only outputs on identical
windows and labels; their correlated errors should not count as independent
confirmation.

### 4. Seeded region propagation

**Inputs:** paper seeds at the perimeter, conservative bead seeds supported by
structure, and local features from methods 1–3. **Output:** region labels and
ambiguity near weak or conflicting connections.

Partition into small regions or use a pixel graph. Connect neighboring regions
with weights that reflect similarity in texture and locally normalized appearance.
Propagate paper/bead support, for example by a random-walk label solver or a graph
energy with seed constraints. Keep isolated decisions unresolved when foreground
seeds are absent or opposing evidence is weak. A graph with only paper seeds
cannot be allowed to declare the whole image paper.

Crucially, the center inside a closed necklace is paper too: establish additional
interior paper seeds from independently supported appearance/texture, then review
them. An exterior flood fill cannot reach it through the necklace. Likewise,
visible gaps may be separate components; do not fill every hole in a bead mask.
Use soft similarity across illumination transitions rather than treating every
large gradient as a surface boundary. Boundary shadows and identical-color beads
can still break or overconnect the graph.

**Test:** a closed necklace with enclosed paper, narrow gaps, a dark bead next to
shadow, touching rope sections and a sharp shadow crossing otherwise plain paper.
Perturb seed locations/feature weights and show where labels change. Hand labels
are optional validation/intervention; final automatic seeds must not contain the
old fixed T1/T2/T3 coordinates or maker-specific HSV boxes.

### 5. Boundary anchors and smooth envelope completion

**Inputs:** locally supported bead-to-paper boundaries and their context;
image-derived local direction and scale. **Output:** two coarse envelopes and
explicitly inferred stretches, plus unresolved bead-scale boundary/gap pixels.

Follow the maker's R105 advice: if the boundary is ambiguous, search farther
along the necklace in either direction. Find neighborhoods with reliable surface
transitions, using raw context and more than a threshold crossing. Fit the
larger-scale outline between those neighborhoods. Compare a local cubic bridge,
a robust smoothing spline, or coupled inner/outer curves with a slowly varying
width. Vary anchors and smoothing to reveal where the prediction is unsupported.
Use the full context to avoid joining nearby but different rope sections.

Classify clear space outside the outer envelope and inside the inner envelope as
candidate paper, keeping an uncertainty band around the curves. Do not call the
entire intervening ribbon solid beads: it contains visible gaps, and the true
silhouette has bead-scale scallops. Refine these with supported surface evidence
or leave them unknown. Do not force every image into a perfect circle, constant
width or a simple annulus if its visible arrangement contradicts that topology.
Planar centerline geometry is a permitted physical prior, not a known spline.

**Existing evidence:** this is the pending anchor/bridge experiment. The older
edge correction made false indents/bumps and was rejected. The current branch has
not recovered anchors or fitted a bridge. [Three bridge options and current
illustrations](photo2/PARALLEL_PATHS.md) preserve that distinction.

**Test:** hide a well-observed stretch from the fitter and check its predicted
location; vary gap length and anchor placement. Include bends, bead scallops and
cast shadows. Score held-out pixel labels and boundary displacement, and report
how much is inferred. Smoothness by itself is never the ground truth.

## Shadowed paper: alternatives and evaluation for splines

The following are shadow-handling variants of the five methods above, not five
additional unrelated segmentation projects. Evaluation here is **reasoned from
the model and existing local experiments**, not a new accuracy benchmark.

| Shadow treatment | How it recovers paper in shadow | Main weakness | Choice for this task |
| --- | --- | --- | --- |
| A. Expand the HSV region using actual shadowed-paper samples | Add independently supported shadow strips/patches as separate modes; retain their locations | Requires trustworthy sample membership; the saved red/shadow overlap survives | Use alongside margin samples; strongest direct color evidence available |
| B. Predict a shading family from lit paper | Permit darker versions of learned paper; in a restricted linear-RGB model compare `a * paper`, with positive scale `a` | Real shadows can change hue/saturation through mixed lights and reflections; near-black beads fit too | Candidate generator or fallback, never a blanket “lower V means paper” rule |
| C. Follow texture across a lighting change | Compare local spectral shape or spatial structure through the darker region | Paper grain, hard shadows, mixed windows and weak dark signals confuse the cue | R111: compare the maker's Gaussian FFT baseline with spatial texture; neither is mandatory |
| D. Grow supported paper regions into shadow | Propagate through gradual appearance changes with texture support; allow a brightness edge without automatically treating it as a surface edge | Weak bead edges permit leakage; no exterior route reaches a fully enclosed paper island | Use only conservatively if local candidates need connection; not the first whole-image solver |
| E. Complete the necklace boundary from clearer neighbors | Infer the coarse bead envelope between supported sections; paper beyond it remains background even if dark | Smooth but biased anchors produce a smooth wrong curve; long gaps and bends need sensitivity checks | Primary way to stop ambiguous shadow bands pulling the spline outward |

**A — actual shadow samples:** first inspect a wider area than the disputed edge.
Select a paper strip that passes from lit to shadowed paper while staying clear
of bead surfaces, when such a path can be supported. It need not be perpendicular
to the necklace. Record raw context, endpoints and sampled colors separately.
Prefer several short supported pieces to a long line that crosses an uncertain
bead edge. The existing S1/S2 centers are provisional examples, not certified
shadow labels. Once a shadow mode has independent support, it can identify other
compatible patches; it must not label every pixel of the same color as paper.

**B — a shading family:** scalar darkening preserves RGB channel ratios in the
idealized model, and preserves H/S when applied directly to positive RGB values
before HSV conversion. This is an assumption to test, not a law of photographed
shadows: loss of one light source can change the remaining light's color. Simple
V extension is therefore a useful baseline but a poor final classifier. Fit the
family to actual lit/shadow pairs when available; leave near-black matches weak.
Do not fit a separate unconstrained illumination color at every pixel.

**C/D — continuity of paper:** evidence that the same fine paper structure
continues through a darker patch can support a shadow interpretation even when
brightness changes strongly. Raw intensity continuity alone cannot do this.
In very dark regions structure may disappear, so growth should stop or retain
uncertainty rather than relying on the current label to confirm its next step.
Keep original seeds separate from predictions; avoid repeatedly retraining on
the algorithm's own unverified labels. Add independently supported interior-paper
seeds for the enclosed center. A graph method has no magical way around HSV overlap.

**E — geometry:** a shadow may extend asymmetrically along a long section. Merely
smoothing the boundary of a shadow-contaminated mask will preserve that broad
bias. Find clearer sections farther along the necklace, keep both sides where
supported, and fit across the weak section with reduced or zero weight on its
ambiguous edge candidates. Mark the bridge as inferred. Preserve bead-scale
scallops for later refinement instead of making the initial spline trace them.

The [existing raw/route illustrations](photo2/review/r104/review-crops.png) show
the ambiguity being discussed; the paths are **not** pure-paper training strips
or verified boundary anchors. [R104](photo2/PARALLEL_PATHS.md) found up to 32 px
of crossing movement from reference replacement, while the strongest hue change
could lie inside the necklace. That argues against using either color or a single
texture threshold as the complete outline. It does not measure the accuracy of
the proposed combined method.

### Which combination I would choose, and why

R110 supplies practical FFT experience; R111 makes adoption optional.
Choose **method 1 + a tested texture cue (2 or 3) + method 5**. Compare FFT and
spatial evidence without making either a prerequisite for useful local geometry:

1. **Learn paper colors from the image.** Start with margin strips; add only
   supported shadow-paper samples. Compare an HSV box with a circular-hue density
   region. Use a restricted shading extension to propose additional candidates,
   not to turn every low-V pixel into background. This makes use of the maker's
   successful sampling idea without hard-coding the paper's pigment.
2. **Check candidates with local structure and context.** Reproduce the explorer's
   raw Gaussian-window low-pass fraction, which the maker found useful even for
   shadows. Compare the beads detrended FFT statistics and a spatial filter stack
   on identical patches; preserve parameters and denominators so the comparison
   actually tests the methods described.
   These correlated cues are not independent votes; disagreement means weak
   evidence. Neither low texture nor a matching HSV value alone proves paper.
3. **Fit the broad curve from supported boundary sections.** Use several anchors
   with evidence weights and a smoothness penalty; reduce the effect of isolated
   bad points. Start with the small local bridge already proposed, then use a
   robust smoothing spline if the wider set of anchors warrants it. Treat inner
   and outer boundaries separately before deriving a coarse centerline; local
   width should change slowly, not be forced constant.

I would postpone a full graph propagation system and a detailed light/reflectance
fit until this combination fails in a way they could address. They add unknowns
and failure modes without yet resolving the key issue: which boundary evidence
is trustworthy. Explore the source FFT baseline alongside spatial texture and
choose by demonstrated usefulness. R111 does not require FFT adoption or require
that this comparison block local index/color work.
No method choice here has been benchmarked as superior on the full photograph.

### What counts as good enough for this stage

The desired intermediate result is a coarse spline plus supported/inferred/unknown
sections. Small mask holes and unresolved individual scallops can wait. A long
shadow strip incorrectly included as necklace cannot: it shifts the curve and
can make all later bead predictions wrong in the same direction.

For a straight image cross-section with true boundaries `left` and `right`, a
midpoint estimate is `(left + right)/2`. If shadow shifts only the right estimate
outward by `d`, the estimated midpoint shifts by `d/2`. This is an illustrative
algebraic example, not a measured photo error or an exact 3D projection rule.
Perspective and bead occlusion can also bias silhouette midpoints; this centerline
is initialization for later camera/geometry refinement, not a final physical fit.

Assess the actual purpose with:

- **Systematic boundary and centerline displacement:** hold out supported edge
  sections or use synthetic evaluator masks; check whether the curve follows
  bead extent rather than the farther shadow edge. Report signed errors locally.
- **Stability:** vary strip placement, HSV tolerance, texture scale, anchor choice
  and smoothing; overlay the resulting curves. A stable wrong curve can still
  fail the held-out check, so stability alone is insufficient.
- **Useful coverage:** show which parts have evidence, how long inferred gaps
  are, and where uncertainty is large relative to local rope width/bead spacing.
  Do not obtain stability by discarding nearly the whole necklace.
- **Downstream adequacy:** confirm the coarse curve supports sensible local
  cross-sections and a search band for later bead geometry; set numerical
  tolerances with that later search scale, rather than requiring a perfect mask.

Proceed once the curve is useful and the remaining ambiguity is localized and
explicit; later stages may refine it. Do not claim this stopping condition is
already satisfied. If the local bead pilot lacks useful geometry because a boundary
is ambiguous, use one wider-context anchor/bridge comparison with shadow-aware
measurements, then illustrated review. This is supporting work, not the unconditional
next numerical step; the active schedule is in [PLAN.md](PLAN.md).

## Shared pixel-level validation

Use the same inputs and evaluate each method before combining them. Track paper
recall in lit, shadowed, enclosed and narrow-gap regions; bead pixels incorrectly
called paper, especially black beads; boundary displacement; and the unresolved
fraction. Vary lighting, exposure, background/bead palette, placement, blur and
JPEG quality. Keep mask/ID render passes strictly on the evaluation side; beauty
images are the analysis inputs. Extreme clipping tests should allow abstention.
Vary the perimeter sampling width and hold out whole regions so overlapping windows
do not masquerade as independent validation. Review raw context beside labels and
support maps. No such full comparison has run in this documentation step.

## Bead analysis given approximate boundaries and a centerline

R109 asks us to take the nearly trusted inner/outer boundaries and their derived
centerline as given, then consider colors, bead identification, pixel sizes,
directions 1/6/7 and helicity. This section is that **conditional method plan**;
it does not assert that the current branch has already recovered these curves.
A usable approximate centerline is enough to begin local analysis; it need not
wait for a perfect background mask.

Parameterize the centerline by image arc length `s`, with local tangent `T(s)`,
normal `N(s)` and apparent necklace width `W(s)`. Pair boundary positions across
local cross-sections rather than pairing unrelated spline parameters. Record the
orientation convention and source-image coordinates. Use short tangent-aligned
patches or a narrow strip `C(s) + u N(s)` to compare sections. Preserve pixel scale:
normalizing transverse coordinates by width is useful for displays but must not
silently turn pixel distances into normalized distances. In tight bends, large
patches mix orientations and strip coordinates can overlap; shorten the patch
or inspect it in the original image.

### Six complementary methods

| Method | Main procedure | Most useful outputs | Main limitation |
| --- | --- | --- | --- |
| B1. Centerline paths through HSV — maker's proposal | Sample by arc length; inspect circular hue, saturation, value, chroma and their local changes; compare nearby parallel paths | Candidate seams, highlights, color interiors and along-path spacing | A single path misses beads and can cross internal shading; black beads and specular peaks defeat simple rules |
| B2. Local Gaussian-window 2D FFT — maker's proposal | Center windows on the curve, use width comparable to W, band-pass, inspect directional peak families and their spatial interpretation | Local scale/direction hypotheses; direction-1 angle relative to tangent for helicity | Spectral peaks mix geometry, color pattern, highlights, harmonics and window effects; labels need calibration |
| B3. Spatial repetition / patch matching | Find displacements that align local image structure; inspect a 2D autocorrelation or shifted-patch similarity map | Neighbor displacement/spacing candidates and a real-space check on FFT interpretation | Repeated colors can dominate; shape changes/occlusion weaken repeats; not an independent vote when derived from the same spectrum |
| B4. Seam and outline tracing | Detect local dark valleys and gradients; connect supported curves and split seeded regions | Visible bead portions and boundaries, including adjacent same-color beads | Highlights and shading make false edges; one bead may split and several may merge |
| B5. Color regions with separate highlight handling | Learn image-specific appearance clusters from supported interiors, grow locally and combine with seams | Palette candidates, color evidence per visible region and highlight flags | Same-color neighbors merge; shadows make one pigment appear as several clusters; white glints are not extra beads/colors |
| B6. Local 3D geometry and neighbor constraints | Fit small occlusion-aware bead arrangements under both helicities to observed contours/appearance | Joint scale, phase, exposed-shape, neighbor-label and helicity hypotheses | Needs reasonable initialization; a plausible model can impose unsupported beads or choose the wrong hand |

### B1 — Read the path through HSV space

Sample original RGB along the centerline at uniform arc-length steps, preserving
the interpolation rule and coordinates, then convert to HSV. Display the raw
route, pixel-color strip, H/S/V/chroma against distance, and a color-space path
whose points retain their image positions. Hue is circular; unwrap locally for
plots or use circular differences, and downweight hue in low-chroma/near-black
samples. Mild smoothing should be applied consistently, with the raw trace retained.
Choose sampling and smoothing relative to the estimated bead scale, not a fixed
photo coordinate or palette.

The maker's cues are a useful first hypothesis: **local V troughs may be seams;
very bright excursions may be specular reflections**. Compare each trough with
its nearby shoulders, and look for changes in H/S or agreement on nearby offset
paths. A sustained, relatively stable color portion between candidate seams can
supply an interior sample. Track repeated trough spacing as an apparent scale
cue. Brightness alone cannot assign surface identity: a black body is dark over
an interval, one bead may contain shading valleys, and a yellow/white diffuse
surface can be bright without being a highlight. Specular reflection may also
change hue/saturation; it is not always a neutral white spike.

Use several paths at small positive/negative offsets from the centerline, scaled
to local width. This tests whether a feature extends as a plausible seam or is
an isolated glint. Multiple paths can still share the same lighting ambiguity.
The distance between two seams on one path is a **visible chord**, not necessarily
the bead's full diameter. Traversal along the necklace centerline is not the
crochet string order; do not turn successive path events into consecutive bead
indices or require the centerline to intersect every bead.

[Historical S/V paths and maker review](https://github.com/rharriszzz/beads/blob/2c4c116bf7f7b9e8c773358a97740dcd77879a8a/photo2/BEADS6_SV_PATHS.md)
support using these cues while preserving failed endpoints and internal-highlight
examples. Current T1/T2/T3 are cross-boundary diagnostics, not centerline traces;
no centerline-HSV detector has been run in this step.

### B2 — Gaussian FFT along the centerline

Take local patches centered on `C(s)`, display them relative to the tangent, and
apply a **spatial Gaussian window whose width is comparable to the local necklace
width**. Specify the width convention: for example, an initial Gaussian FWHM of
`W` means sigma `W / 2.355`; compare neighboring widths rather than claiming this
is the maker's unspecified convention. This is a proposed starting definition,
not an adopted parameter. Use enough longitudinal support to see several repeats,
but keep the tangent variation small. An anisotropic window is an option if the
cross-rope extent needs limiting while longitudinal support remains useful.

Remove slow variation, suppress the central low-frequency region and very high
frequencies, then look for **three opposite, noncentral peak pairs** in a bead-scale
band. R110 explicitly identifies these as the maker's 1/6/7 families. Initially explore a
range of bands because bead spacing is itself an output; use B1/B3 only as loose
scale proposals. Run intensity first; compare color-sensitive channels if needed.
Do not Fourier-transform wrapped H as an ordinary scalar. Retain raw-versus-
detrended views, the exact band mask and window support. A hard silhouette mask
creates its own spectral edges; avoid treating them as bead lattice evidence.

The maker reports that these spectra reveal families 1/6/7 and that **direction
1's angle relative to the centerline directly determines helicity**. Use this as
the primary directional hypothesis. Show peak pairs beside corresponding image
structures, optionally reconstructing selected bands to see what produced them.
The explorer already groups opposite peaks and offers pair reconstruction; its
generic peak list includes the origin and does not automatically identify three
physical families. [R110 source review](photo2/FFT_EXPLORER_NOTES.md) records what
to reuse. Preserve weak/extra/harmonic candidates instead of forcing any three
pairs into the labels merely because conjugate symmetry is present.
Frequency vectors describe phase variation; their angle is not automatically the
real-space bead-neighbor angle. Convert/calibrate that relationship before labeling
a peak “1,” “6” or “7.” These labels are index offsets, not frequency-radius ratios
of 1:6:7. The reciprocal of a peak frequency measures a periodic wavelength along
its frequency direction, not automatically bead diameter or a neighbor distance.

For the spatial direction-1 line angle `theta1` and tangent `thetaT`, inspect the
signed relative angle wrapped modulo 180 degrees. Define image y orientation,
viewing side, tangent convention and hand labels, then calibrate the mapping on
known opposite-helicity POV-Ray examples at several loop positions. Tangent reversal
should not change a line angle modulo 180 degrees; reflections/coordinate changes
must be accounted for. Keep alternate assignments when peaks are weak, the angle
is near an ambiguous configuration, or families cannot be separated. A consistent
hand across well-supported sections is stronger evidence than a single peak.

The current FFT code measures background texture power; it does **not** implement
this directional estimator. [R098's saved display/convention plan](photo2/PRIOR_WORK.md#r098--makers-directional-fft-method)
remains applicable. Width-scale spectral analysis does not by itself locate every
bead: Fourier power loses phase, and candidate spacing still needs localization.

### B3 — Look for repetition in image-space displacements

Compare a short patch with translated copies, measuring similarity of detrended
intensity, gradients or local appearance over their valid overlap. Normalize for
overlap and contrast, discount shifts with too little support, and inspect peaks
away from zero displacement. Plot arrows for the candidate shifts directly on
the photograph. Repeat over several local windows; gradients may reduce dependence
on a particular color sequence but are still affected by reflections and seams.

A local 2D autocorrelation is one implementation. It can display spacing in pixels
more intuitively than a frequency plot. For the same signal, autocorrelation and
Fourier power are mathematically linked: agreement is an interpretation check,
not independent confirmation. Try direct feature/patch comparisons when the raw
appearance varies strongly. Subdivide windows where curvature or projection makes
a single translation inappropriate; the visible rope is not a globally flat lattice.

Use multiple plausible displacement families as candidates for ±1/±6/±7, requiring
compatible local neighbor triangles and image evidence to label them. A repeated
color motif may favor several-bead displacements; the strongest nonzero peak need
not be the nearest bead. This method offers spacings/directions, not absolute bead
origins or hidden-bead identities. Compare its inferred directions with B2 before
using either to assign helicity.

### B4 — Trace seams and visible outlines

Find dark valley curves and intensity/S/V gradients at several scales within the
necklace strip. Use B1 interior candidates or supported region interiors as seeds;
trace candidate seams or use seeded watershed/region splitting. Retain competing
splits when evidence is weak. Require a proposed seam to fit neighboring visible
surfaces, not merely pass through a brightness minimum.

This can distinguish adjacent same-color beads that color clustering would merge.
It can also incorrectly partition a single glossy bead or miss an occluded seam.
Regularize at the bead scale, using local orientation/spacing hypotheses without
forcing every visible portion into an ellipse or rectangle. Projected caps,
crescents and notches are possible after occlusion. Exposed area or centroid is
not the full bead's size or physical center. For dark beads, use clearer neighboring
outlines and highlight context, while leaving truly unsupported extents unresolved.

### B5 — Infer appearance groups, then separate bodies

Sample candidate interiors from several supported sections, retaining both
ordinary shading and flagged highlights. Estimate the palette from those samples
with circular hue and brightness/chroma information; do not require red/yellow/
black in the general implementation. The maker's known palette is useful for
review, not an input that forces a desired result. Use robust color summaries and
local shading variation; postpone exact POV-Ray material parameters to lighting/
material fitting. A color cluster is not a material measurement.

Grow compatible regions locally, then split them using B4 seams and B2/B3 scale
information. Keep a bead's ordinary surface and possible highlight pixels related
without treating each bright component as a new bead or a new pigment. Associate
highlights only when enclosing/neighboring evidence supports it; leave shared or
clipped bright areas unresolved. Black-bead glints can supply useful landmarks,
but neither their count nor positions are guaranteed bead counts or centers.

Simple clustering alone merges same-color neighbors and can turn shadows into
spurious extra colors. A low-S/high-V point alone is not sufficient to distinguish
a highlight from a pale bead. Preserve per-region color alternatives and unknown
readings rather than forcing every portion into a palette class.

### B6 — Fit a small geometry/occlusion model with neighbor constraints

Use the centerline, local width and B1–B5 hypotheses to initialize a short patch
of the known bead geometry. Compare both helicities, minor-circle phases, image
scale and local position, using the planar necklace/global camera relationship.
Neighbor index offsets are ±1/±6/±7; cycle consistency and supported neighbor
triangles can reject assignments. They do not turn every nearest image point into
a correct crochet neighbor. Keep overlapping rope sections separate.

Render or project the **exposed** portions after neighbor occlusion, compare
predicted outlines and observed seams, and test withheld parts of the patch.
Use numerical geometry in Python and appearance in POV-Ray. Once calibrated,
clear neighbors may constrain a black bead even when its own HSV trace is weak.
Do not require every predicted site to have a detected visible body, and do not
confuse a model prediction with an observation. Retain wrong-hand alternatives
when the image scores do not distinguish them.

This is the most informative eventual joint method, but also the most demanding
and easiest to overconstrain. [Historical calibrated local fitting](https://github.com/rharriszzz/beads/blob/2c4c116bf7f7b9e8c773358a97740dcd77879a8a/photo2/LOCAL_PATCH.md)
had successful examples as well as black-region and competing-helicity failures;
it did not establish automatic photo recovery. Use it after establishing local
appearance/scale evidence, rather than guessing all parameters simultaneously.

### What “bead size” and “identified bead” mean here

Keep separate measurements for visible footprint extent, path chord length,
neighbor displacement in each family, and inferred projected full-body size.
All may be in pixels, but they are different quantities. Foreshortening and
occlusion change them around the loop. Necklace width divided by 6.5 is not a
bead-diameter measurement: the 6.5 counts progression around a 3D cross-section,
not beads laid across the image width. Recover full-body scale through calibrated
geometry or well-exposed shapes, with the assumptions stated.

For each candidate visible body retain a region/observation ID, supported pixels,
color evidence, highlight/seam flags, candidate neighbor links and uncertainty.
A body can be identifiable while its color or index remains unknown. A bright
spot, color patch, visible centroid and physical bead center are different objects.
Ignore slivers as active observations without merging their pixels into neighbors.
Material fitting and full repeating-pattern inference remain later tasks.

### Recommended first comparison once a centerline is available

This is a focused directional-method comparison when that evidence is needed,
not a mandatory sequence of B1 through B6 before starting the index/color pilot.
Explore **B1 + B2** on the same few short sections: the maker's HSV paths give
localized evidence, while Gaussian FFT proposes organization/scale and a helicity
cue. R111 makes B2 optional in the final solution; spatial directions or B4/B6
geometry can instead support indexing. Use **B3 as an interpretation cross-check**,
not an independent spectral vote.
Choose sections with different local tangents and include a difficult dark portion.
Display raw context, centerline/offset paths, color strips and HSV trajectories,
window/band masks, peak pairs and corresponding spatial direction arrows together.
Perturb the centerline slightly and vary window width/band limits to expose fragility.

Then use B4/B5 to turn supported cues into candidate visible bead regions/colors;
bring in B6 only where geometry is needed to resolve weak black/occluded portions
or competing directions. A complete detector is not needed to compare the first
cues. This ordering is a reasoned proposal, not a measured ranking of the six methods.

Validate on known-pattern POV-Ray beauty images with both helicities, several
in-plane section directions, changed palettes (including same-color/dark cases),
light/highlight changes, scale and modest blur. The evaluator may use true masks,
indices and centers, but the image-analysis input must not include those labels.
Check local direction/spacing errors and handedness, region splits/merges and
misses, interior color stability and sensitivity to centerline error separately.
Treat source geometry supplied to B6 as explicit calibration, not image-inferred
knowledge. Show unresolved cases. Stop after the illustrated local comparison,
before whole-necklace bead indexing or pattern recovery.

## Assign bead_index and color to clearly visible beads

**R150–R151 outward-point direction geometry:** [intrinsic angle calculation](photo2/DIRECTION_ANGLES.md)
uses the outer-wall midpoint in the minor-radial direction, radius chain_minor
plus bead_radius. Distinguish shortest unrolled minor arcs, 3D point chords and
camera projection. Nominal local chord inclinations are 85.54°/47.72°/43.31° for
directions 1/6/7; signed sides reverse with helicity. Explicit source row rounding
and full-torus phase dependence prevent treating these as exact photo angles.
Placement/outward-point checks validate the calculation; exposure and projected
direction comparison remain separate, not automatic consequences of visibility.

**R149 maker-point ownership comparison:** [positive-only surface fitting](photo2/MAKER_POINT_FIT.md)
uses six confirmed locations around C, holds out G's location, and tests both
6/7 families/helicities with all latent neighbors in first-hit occlusion. Loose
outward proposals are initialization only. Both photo families have poses passing
all seven points; the independently rendered known-synthetic case also permits
the wrong family. This guards against claiming index recovery from point success.
Nine Python/POV checks validate the local surface kernel; two tests guard mapping
symmetry and holdout exclusion. No uniqueness, automatic detector or accepted
whole-necklace fit. Next use supported visible boundaries after
[illustrated maker review](photo2/MAKER_POINT_QUESTIONS.md).

**R144–R147 maker graph extraction:** [exact cycle propagation](photo2/LABEL_SERIES.md)
turns completed series into a connected discussion lattice, preserving UUIDs,
maker numbers and unknown full indices. Twenty-eight corrected triangle/cycle
checks support d2=d1+d3 on 27 bodies/54 links. A bounded exhaustive omission audit
localized two skipped clicks; maker corrections are preserved alongside originals.
B=22,C=20,G=23 confirmed; six complete neighbor stars provide a seven-body fitting
seed around C. Two 6/7 choices plus global reversal remain. Treat graph-implied
unrecorded edges as proposals and hand-picked anchors as visible-surface locations,
not physical centers or automatic runtime coordinates. Synthetic known-chart,
skipped-step and contradiction tests guard inverse claims.

**R138–R141 interactive maker labeling:** [local raw-photo editor](photo2/LABELER.md)
collects hand-picked anchors, unique numbers and ordered d1/d2/d3 click series in
original oriented source coordinates. Stable IDs preserve paths on renumbering;
revision-checked saving and undo cover both locations and series. d2 is up to down
clockwise; d3 is down to up clockwise, equivalently up to down counterclockwise.
No d2/d3 mapping to 6/7, signs or verified step counts is inferred. R148 adds
WSL Windows-browser launch with a quiet manual URL fallback and automatic selection
of a free port when the default is busy; explicit ports are honored. The diagnostic
viewing crop is explicit, with no assistant coordinates/colors imported. Manual
numbers require reconciliation with observation IDs before bead_index/coverage
claims. This evidence collection task supersedes another numerical chart comparison.

**R135–R136 current evidence:** [boundary-bracket comparison](photo2/BOUNDARY_ARC_FIT.md)
adds negative ownership only beside selected local segments, validating pair sides
against supplied regions to avoid crossing thin/concave bodies. Eight checks pass,
but sparse brackets do not identify a chart; stronger C constraints can lose other
interiors. Maker supplies coupled BC=6/CG=7 or BC=7/CG=6 with unknown signs.
[Preserved alternatives](photo2/neighbor-review-r136.json) supersede the old BC=1
maps as active photo hypotheses. Next compare those coupled families and signs,
keeping other observation assignments provisional and G's image pixels withheld.

**R132 constraint comparison:** [omit unknown regions explicitly](photo2/SURFACE_CONSTRAINTS.md).
Use missing ownership in both the penalty and distance transforms; do not turn
an uncertain junction into an artificial boundary. Positive interior support is
useful but cannot replace shape constraints: this test increases coverage by
enlarging predictions and worsens held-out overlap. The known wrong chart also
fits almost all cores. Keep the unknown handling, do not adopt interiors-only
fitting or infer correspondence from its score. Selected clear boundary arcs
with interior support were tested in R135; their results are linked above.

**R126–R128 executed local fit:** [seven-body surface experiment](photo2/LOCAL_SURFACE_FIT.md)
compared uncertain point fitting, exposed-region fitting and full shaded-image
fitting, selecting exposed regions. Original rounded annular surfaces and latent
occluders were fitted to six assistant-proposed regions, withholding G. Both
6/7 charts survive; H2 is only slightly better on approximate photo observations.
Independent POV checks validate the numerical surface renderer, and the known
synthetic example favors its correct chart. This does not validate photo labels.
Camera elevation/phase has an unobservable local freedom; keep it distinct from
a measured view. R128's close-iPhone information prompted metadata-based pinhole
sensitivity tests. R130 describes shadow from four adjacent beads; R131 considers
P probably non-bead and near an edge. Keep that classification tentative and omit
P from bead-fitting constraints; seek clearer surface evidence for the C/F mismatch. Picture counts
(four red, two yellow, at least two black) are contextual maker review, not a
color-to-ID assignment, an automatic runtime prior or an exact full inventory.
[Answer and annotation](photo2/LOCAL_SURFACE_FIT_QUESTIONS.md).

**Current R117–R125 route: fit a patch, then walk neighbors.** Establish a patch
of 5–12 substantial central bodies, including locatable black beads. Maker says
black is roughly twice as difficult, not impossible; this is not a fixed numeric
classifier weight. Ignore edge/behind-edge beads in the active fit/walk. Keep
their exclusions and missing slots explicit. R122–R125 propose signed direction
counts for discussion, without requiring the fitter to use them internally.

| Implementation route | Current choice |
| --- | --- |
| Maker method 1: Python placement and camera projection | Forward primitives calibrated; R126 local surface fit leaves two tentative correspondence charts and visible shape errors |
| Maker method 2: direct six-direction neighbor walk | Alternative: connect central bodies using local lattice coordinates, carry uncertain/missing steps, and continue around the necklace |
| Fit a patch, then initialize the walk | Selected overall route: calibrate placement first, fit the patch, then use neighbor consistency to check expansion |

[Placement/surface pilot](photo2/PLACEMENT_PILOT.md) implements the circular
prototype with two independent angles (major position, minor phase); the direct
API needs no bead_index or N. For a noncircular planar centerline, use arc length
and minor phase in the local frame. These are placement variables, distinct from
the maker's discussion labels `(n1,n6,n7)`: signed step counts in the three
construction directions. Derive `bead_index = origin+n1+6*n6+7*n7`. The triples
`(0,0,1)` and `(1,1,0)` can name the same bead via different paths. The
[local consistency helper](photo2/neighbor_coordinates.py) checks supplied edges,
alternate paths, conflicts and index collisions; it does not identify neighbors.
Use stable observation IDs, tentative edge labels and separate components. Say
“the +6 neighbor of B” in reviews; neither unique triples nor immediate global
indices are required. Keep missing slots; handle a full winding cycle only with
a documented cut or verified N. No photo direction label is newly established.

R118–R119's candidate anchor is the bead's outward surface point in the minor
circle, not its center or a highlight. The reference implementation chooses the
midpoint of the legacy bead's outer-wall band. Test whether it is exposed before
using it as a correspondence; compare nearest-camera surface evidence as support.
R120–R121 restrict use to substantial central bodies, excluding edge remnants.
Known-pose synthetic checks support trying this subset, not a universal visibility
theorem or an automatic photo selector. No two-point threshold was supplied.

The R114 pilot and R116 method discussion below are historical evidence/options;
their black-bead deferral and index-first ordering are superseded by this route.

**R114 pilot evidence:** [assisted local observations and synthetic check](photo2/LOCAL_PILOT.md)
implement the first I1/C1 diagnostic. Both candidate triangles are algebraically
consistent, while a wrong synthetic alternative retains a 13-index error after
global alignment. Photo RGB appearance clusters do not yet resolve pigments.
The method catalog below remains a proposal for broader inference, not a claim
of automatic detection or accepted photo indices.

**Historical R116 priority:** bootstrap from the clearest non-black bodies away from the
necklace edge. The maker suggests these may already supply enough evidence.
This is a proposed sufficient subset, not a claim that the current indices are
resolved. Black and edge observations remain in coverage accounting, but their
decoding is not a gate before testing the clearer bodies. R115 confirms D is
separate from B without making D a reliable geometry or pigment anchor.

| Clear-body approach | Role in the next local test |
| --- | --- |
| I1 neighbor graph on clear anchors | First choice: use supported immediate-neighbor edges; keep multiple labels when needed |
| B3 repeated-displacement matching | Compare several clear-body pairs to find repeated arrangements; allow skipped bodies and projection effects |
| I3 row tracking with gaps | Alternative if a slightly longer section supplies traceable chains; do not compress missing positions |
| I2 local 3D fitting to clear exposed surfaces | Targeted fallback if graph/displacement evidence cannot distinguish phase or 6/7 families; difficult bodies need not be fitted first |

R116 selected I1 plus B3 support. In the existing R114 review, B/C/G were assistant
shortlist candidates with broad colored faces; not newly maker-labeled beads,
verified physical centers or an automatic selection. Inspect a slightly wider
local section for additional clear bodies if needed, before returning to D or
black-body ambiguity. Hold out a clear observation or relation, preserve alternate
assignments, and check the sparse procedure on a known synthetic counterpart.
Two successive *selected* bodies need not be construction neighbors: any longer
index difference must have its own support, not a forced ±1/±6/±7 label.

Judge body separation, exposed interior support and distance from the uncertain
necklace boundary together. A bright specular spot does not make a black bead
a clear colored anchor. Fixed red/yellow rules and the saved B/C/G coordinates
remain diagnostic assistance, not final runtime priors. Revisit difficult bodies
after a supported structure exists, retaining inferred versus observed labels.
Enough evidence for a local structure does not itself prove exact N or a unique
full color repeat; those checkpoints retain their separate evidence requirements.

R111 selects the next inference objective: every clearly visible bead should have
a `bead_index` and a color. FFTs are **candidates to explore in two upstream uses**
(background/shadow separation and bead directions/spacings/helicity), not a required
component of the final solution. Compare against non-FFT alternatives and keep the
useful evidence. An FFT estimates structure; it does not directly assign an index
or a pigment to each visible body.

### Match the meaning in beads.pov

The [actual placement loop](beads.pov) starts `bead_index = 0`, increments by one
through all `nbeads`, and uses that same index for both major-circle and minor-circle
placement. Its palette lookup is `color_pattern[mod(bead_index, pattern_length)]`.
Thus **bead_index is a position in the full string**, not an image-region number,
a count of visible beads, a distance along the centerline, or a repeat-slot number.
Color assignment now does not require discovering `pattern_length` first.

Give each visible observation a stable `observation_id`. A seed can establish
index0 in a chosen convention; the maker permits arbitrary origin and stringing
orientation. Keep physical-helicity hypotheses separate from that reporting freedom.
Unknown/hidden positions must not be deleted to make visible indices consecutive.
Disconnected components have local indices with unknown relative offsets until
there is evidence connecting them. Do not call those global bead_index assignments.

The target is complete coverage of **clearly visible bodies**, including clearly
visible black beads. Record unresolved cases in the inventory instead of quietly
omitting them. A visible bead with unreadable color still needs an observation
record and may have a known index. Conversely, a clear color does not establish
its index. Ignore tiny slivers under the existing maker rule, without absorbing
their pixels into neighbors. No complete current photo inventory is claimed.

### Four ways to assign the indices

| Method | How indices are obtained | Advantage | Failure / choice |
| --- | --- | --- | --- |
| I1. Signed neighbor graph | Identify immediate neighbors in the ±1/±6/±7 families; propagate index differences and check loops | Directly uses the maker's construction; tolerates unknown colors | A wrong edge can corrupt a patch; nearest image distance alone is inadequate. **First choice.** |
| I2. Local 3D template matching | Fit both-helicity/phase/scale arrangements, then match visible observations one-to-one to predicted exposed beads | Occlusion and shape can constrain difficult black beads and connect regions | Requires calibration and may have equally plausible wrong-hand fits. **Local support for I1.** |
| I3. Ordered strip/row tracking | In centerline coordinates, track several diagonal bead/seam chains jointly; use constrained dynamic programming to match them to a candidate 6.5-turn layout | Uses continuity across a long section and can retain skipped observations | A single missed row/phase slip can shift many indices; sorting by arc length is insufficient. Alternative for clearly traceable sections. |
| I4. Joint discrete constraint solving | Retain several candidate neighbors/index labels; optimize consistent integer assignments with uniqueness, geometry and cycle constraints | Can resolve choices that greedy propagation cannot | More expensive and still vulnerable to consistently wrong image evidence. Escalate only where I1/I2 leave concrete competing assignments. |

All four share the appearance procedure below, so their index quality can be
compared without changing the palette model at the same time. Repeat-pattern
agreement is reserved for a later cross-check, not used to manufacture index/color
agreement in this first assignment stage.

### Selected indexing procedure: I1 with local I2 support

1. **Build a reviewable observation inventory.** Combine the earlier B1/B4/B5
   path, seam and appearance cues into candidate visible regions. Review a short
   patch's missed, merged and split bodies. Use supported interiors/outlines;
   visible centroids are convenient anchors but are not assumed physical centers.
   Do not wait for every boundary pixel to be perfect.
2. **Propose actual construction neighbors.** For each body, use local orientation,
   spacing, exposed shapes and boundary contacts to propose edges labeled
   `d in {-7,-6,-1,+1,+6,+7}`. FFT directions may help, or spatial matching and
   outline orientation may supply them. Keep uncertain signs, 6/7 swaps and both
   hands as alternatives. Do not connect different rope sections merely because
   they touch in the photograph, or skip a missing immediate neighbor while
   pretending the next visible body is adjacent.
3. **Propagate supported constraints.** Each accepted edge u→v asserts
   `index(v) = index(u) + d`. Start from a small well-supported seed group and
   check all alternate paths, not only a traversal tree. Require reciprocal labels
   and unique indices for distinct observations. A local triangle must satisfy
   `1 + 6 = 7`. If constraints conflict, flag the implicated region/edges rather
   than renumbering to hide the contradiction. A consistent graph can still be
   wrong, so also check held-out image evidence.
4. **Use geometry where it adds information.** Fit a small exposed-bead model
   around difficult regions, comparing both hands/phases and supported contours.
   One predicted physical bead can own several disconnected visible fragments;
   body-level assignment must handle that without counting each fragment as a bead.
   Permit unmatched observations/predictions and record why. Withhold part of the
   patch for checking; do not let predicted indices become their own evidence.
5. **Extend and reconcile patches.** Shared supported bodies establish component
   offsets; overlapping patches must agree on index differences and colors.
   Preserve disconnected offsets instead of estimating missing counts from a
   rough centerline length alone. For the full closed loop, use a documented cut
   or indices modulo an established total N: a winding cycle can add ±N, whereas
   a small local cycle sums to zero. The old approximate N is not exact closure truth.

A small hypothetical constraint example (not a photo annotation or visibility map):

```mermaid
flowchart LR
    A["Observation A: index 0"] -->|"+1"| B["Observation B: index 1"]
    B -->|"+6"| C["Observation C: index 7"]
    A -->|"+7: independent route"| C
```

If the two routes assign different indices to C, inspect the edges. The omitted
indices in this schematic are not assertions that those beads are hidden.

[Historical graph method](https://github.com/rharriszzz/beads/blob/2c4c116bf7f7b9e8c773358a97740dcd77879a8a/photo2/METHODS.md)
already explains the construction constraints. Its numerical graph checks did not
solve automatic image-neighbor identification. [Local contour fitting](https://github.com/rharriszzz/beads/blob/2c4c116bf7f7b9e8c773358a97740dcd77879a8a/photo2/LOCAL_PATCH.md)
provides useful conditional evidence and wrong-hand/black-region failures. Reuse
those lessons rather than presenting either as a finished photo-indexing solver.

### Choose colors from bead surfaces, not from a single pixel

Compare three appearance estimators on the **same supported regions**:

| Color method | Procedure | Choice |
| --- | --- | --- |
| C1. Robust interior summary plus learned palette | Use interior pixel distributions, suppress supported highlight/mixed-edge outliers, classify against appearance groups learned from this image | **First baseline:** transparent and easy to illustrate; needs shadow-aware support |
| C2. Joint palette and local shading model | Let one latent pigment produce a family of observed colors under local shading; share lighting context across nearby beads | Refine when C1 splits one pigment into several shadow clusters; constrain flexibility so every color cannot explain everything |
| C3. Small reviewed prototype set | Select a few clearly supported bead interiors for each observed appearance group, including shaded examples; classify others with distances/distributions | Useful diagnostic or assisted fallback; selected examples and human assistance must be explicit, not baked into final code |

I would start with **C1**, adding a restricted **C2** where shadow/gloss causes
systematic mistakes. Preserve hue wrap and use chroma/value as well as hue: hue
alone cannot identify black or distinguish pale/neutral beads. Use robust RGB or
circular-HSV statistics, never an ordinary arithmetic mean across the hue wrap.
Do not discard every dark pixel as a seam; black-bead interiors are dark. Likewise,
a bright pixel is only a possible reflection, not automatically a different pigment
or a pixel to delete from a pale bead. Retain the raw distribution and rejected
pixels so color choices can be reviewed.

Learn candidate palette groups across several image sections, then merge or split
them only with supporting appearance/lighting evidence. Do not fix red/yellow/black
or a color count in the general solver; the maker's known photo-2 palette can be
used for review. Associate a stable palette ID and representative appearance with
each assigned color. A per-bead palette ID is not the recovered repeating
`color_pattern`, and neither establishes POV-Ray finish/normal/interior properties.

If evidence is insufficient, keep ranked color candidates or unknown, even when
an index is clear. Never choose a color just to make a future repeat fit. Preserve
observed readings separately from any colors later inferred for hidden positions.
These unresolved cases count against completion of the assignment target.

### Outputs, evaluation and the bounded first pilot

For every observation, retain: image/region reference, visibility assessment,
component and local index, global bead_index or explicit alternatives, neighbor
constraints, palette ID/candidates, supported interior pixels and uncertainty
reasons. Indices and colors have separate statuses. Uncalibrated scores are not
probabilities. A clearly visible bead is not silently excluded for being difficult.

Choose **I1 + C1**, with **I2/C2 as targeted support**. This avoids making a full
inverse-rendering fit or an FFT result a prerequisite to useful local assignments.
I3 is worth comparing where rows can be followed cleanly; I4 is justified when
specific remaining ambiguities require joint choices. This is a selected plan,
not a claim of measured superiority or a new assigned bead in the photograph.

First pilot: one short patch with supported visible bodies, including neighboring
same-color beads, a dark bead and a highlight where available. Show the raw patch,
observation inventory, proposed signed edges, index alternatives and interior color
samples separately. No confirmed centerline or detections currently exist: first
use B1/B4/B5 (local appearance paths, seams and region evidence) to propose bodies
and local tangent/spacing, then apply I1+C1 only where this supports them. Mark
any hand-selected patch, path, anchor or region as diagnostic assistance, never
as a learned or automatic result. Use I2 locally for unresolved shape/direction
hypotheses; if labels remain ambiguous, present alternatives instead of forcing
indices to complete the pilot. Do not demand a full centerline first.
Compare the non-FFT direction baseline with FFT proposals
when available, so exploration does not turn into mandatory adoption. Evaluate
on a known synthetic counterpart with truth available only to the evaluator;
any supplied camera/geometry/region masks must be declared as assistance.

Report visible-body coverage, false/split/merged observations, correct signed
neighbor labels, index errors after one allowed component origin/orientation
alignment, color errors/unknowns, contradictions and unresolved component offsets.
Do not align each bead independently or delete contradictory observations to make
scores improve. Test held-out bodies and modest input/anchor perturbations; a
wrong consistent graph or an overly permissive color model must be able to fail.
Stop at the illustrated local index/color review, before full-necklace numbering,
closing the unknown global count, or repeat-pattern inference.
Save a short illustrated question about the most consequential body separation
or neighbor alternative in the tracked question file, with its curated crop and
current assumptions. The review may conclude that better local evidence is needed;
it is not a requirement to produce confident labels from insufficient evidence.

## Shortest color pattern from indexed observations

R112 asks for one or two methods and guarantees that photo 2's repeat length is
not divisible by 13. This is conditional planning: this branch still has no
resolved photo inventory, exact N or recovered sequence. Complete full-string
indexing of every bead, including hidden positions, establishes N; indexing just
the visible bodies does not by itself establish the missing closure interval.
With a complete zero-based assignment N = max(index) + 1. Do not substitute the
largest visible index or the historical approximate count.

**Why 13 matters:** at exactly 6.5 beads per turn, a repeat of 13m beads advances
2m full turns, returning each pattern slot to the same cross-section phase, so
repeated copies can all conceal the same unknown color on the hidden side.
This is the maker's earlier R018 counterexample, preserved in the
[historical plan](https://github.com/rharriszzz/beads/blob/2c4c116bf7f7b9e8c773358a97740dcd77879a8a/PLAN.md)
and tested in the [R023 visibility study](https://github.com/rharriszzz/beads/blob/2c4c116bf7f7b9e8c773358a97740dcd77879a8a/photo2/VISIBILITY.md).
That study showed weak slot coverage, not a wholly invisible slot in every view:
camera direction around the loop still changes. Allow for actual closure/twist
and viewing geometry; a nonmultiple of 13 improves phase diversity in the ideal
model but is not proof of complete observable coverage. Report slot support.

This is an existing problem: **periodicity of a partial word**, where unreadable
positions are holes. Strong periodicity requires agreement between every pair
of known positions congruent modulo L, not just adjacent occurrences separated
by L. See [Blanchet-Sadri, Periodicity on Partial Words (2004)](https://libres.uncg.edu/ir/uncg/f/F_Blanchet-Sadri_Periodicity_2004.pdf).
Our older branch already implements this in
[partial_word.py](https://github.com/rharriszzz/beads/blob/2c4c116bf7f7b9e8c773358a97740dcd77879a8a/photo2/partial_word.py),
with [known-index synthetic evaluation](https://github.com/rharriszzz/beads/blob/2c4c116bf7f7b9e8c773358a97740dcd77879a8a/photo2/SEQUENCES.md).
Those results validate a sequence stage supplied with indices/colors, not photo
recognition. Inspect/reuse the solver in a later bounded implementation; it has
not been imported or rerun here. The historical implementation accepts only
three integer color labels and scans 1..floor(N/2), separately flagging closure.
Reuse its residue logic, but make the alphabet, candidate domain and photo-specific
13 exclusion explicit; do not silently inherit its benchmark assumptions.

### P1 — Exhaustive residue-class consistency (recommended)

Inputs: verified exact N, indexed visible colors and their evidence, and the
maker's whole-repeat construction. Enumerate L in increasing order with
`N % L == 0` and, for photo 2 only, `L % 13 != 0`. Use the confirmed `<400`
bound, but include lengths below 200 when checking minimality: the earlier
rough 200–400 estimate is not proof of a lower bound. Keep an unrestricted
diagnostic scan available if supplied facts and observations conflict.

For each L, group observations by `r = bead_index % L`. A candidate passes if
every group has a single consistent color. Retain every supporting original
index and a conflicting pair for each rejection. The first passing candidate
is the smallest compatible length under the stated constraints. Keep the other
passing candidates for ambiguity review. Work is O(M D) for M observations and
D candidate divisors; this is small enough to prefer clarity to elaborate search.

If colors are candidate sets rather than certain labels, intersect all sets in
each residue class. Empty intersection rejects L; several remaining colors stay
ambiguous. No observation means an unsupported slot, not permission to claim a
color. A fully unknown observation supplies no color constraint. Preserve these
states separately from measured labels. Never majority-vote away a contradiction
to report an exact match; revisit its actual image evidence or index assignment.

Toy illustration only: for N=18, observations `0:A, 1:B, 2:C, 3:A, 4:B, 5:C,
9:A, 16:B, 17:C` support shortest block `ABC` of length 3. L=1 conflicts at
indices 0/1; L=2 conflicts at 0/2. All three slots are supported. Conversely,
observations only at `0:A, 3:A, 6:A` allow L=1 even if unseen beads would reveal
a longer true design. A smallest compatible completion is not automatically
proof of the maker's complete original pattern.

### P2 — Eliminate divisors using different-color distances

For each pair of confidently differently colored beads at indices i,j, compute
`d = abs(i-j)`. Every candidate L dividing d is impossible: those beads would
occupy the same pattern slot. Remove such divisors from the initial candidate
set, retaining witness pairs; choose the smallest survivor and construct its
slots with P1. Same-color pairs do not prove any period. Contradictory labels at
the same index invalidate the input rather than becoming a normal distance test.

This is an independent formulation of the same exact constraints for certain
labels. A simple version costs O(M² D), though distances can be deduplicated and
their divisors cached. It is useful as a checking oracle and for explaining why
a shorter repeat fails, not my first production choice. Pairwise intersections
alone are insufficient for uncertain color sets: `{A,B}`, `{B,C}`, `{A,C}` have
no common color despite pairwise overlap. Use P1's full intersection in that case.

### Evidence required before calling a pattern recovered

Report exact-N provenance, candidate domain/exclusions, shortest compatible L,
slot colors/alternatives, support indices and unobserved slots. Every accepted
clear observation must match; missing indices must not be compacted. No admissible
L means a conflict to investigate, not an invented pattern or silent relaxation
of the maker's promise. N may itself be a multiple of 13 even when L is not.
Keep alternatives when N or disconnected index offsets remain unresolved.

To distinguish agreement from prediction, freeze a candidate using training
sections and predict separately withheld sections, recording abstentions. After
validation, refit using all accepted observations and check every one. Reject
all shorter admissible lengths with witnesses. A complete minimal block can be
presented up to cyclic rotation/reversal without changing actual color identities;
retain the transformation to original indices and the independent physical
helicity convention. Unknown slots and longer compatible alternatives limit
claims about the true authored sequence even when minimum-length fitting succeeds.

Future Python validation should compare P1/P2 on known synthetic words with holes,
whole missing slots, wrong colors/indices, cyclic shifts/reversals, and exact-N
errors. Include period 13 both with the photo-specific exclusion disabled and
enabled; include total N divisible by 13 but allowed L. Truth is evaluator-only.
No additional FFT is needed for this sequence stage. The two requested spatial
FFT explorations remain optional supporting work in their original roles.

## Fit paper, bead materials and lighting in POV-Ray

These are four proposed, complementary fitting methods for the later appearance
phase, not fitted parameters or changes to beads.pov. Use recovered geometry,
indices and palette membership when available. Pattern colors are discrete labels;
rendered RGB additionally depends on pigment, finish, illumination and camera
processing. Fit shared material per color first, allowing small per-bead changes
only if repeated evidence supports them.

| Method | Evidence and fitting procedure | Main limitation |
| --- | --- | --- |
| A1. Paper and cast-shadow fit | Fit an independently colored plane from reliable lit paper; use cast-shadow direction, displacement and softness to propose light position/extent and fill. Jointly check lit and shadowed paper in several sections. | Shadow displacement depends on bead height/camera as well as light; paper brightness alone cannot separate pigment from light intensity. |
| A2. Highlight and surface-normal fit | On many modeled bead surfaces, use highlight locations to constrain source directions; fit highlight shape/width alongside cast-shadow softness to separate source extent from finish roughness. Compare one broad source, broad source plus fill, and two sources if supported. | Normals depend on correct geometry; clipping, multiple sources and occlusion make a single glint insufficient. |
| A3. Repeated-color material fit | Pool diffuse interior samples for each palette label across positions and illumination; estimate one pigment per class under the shared lights, then finish strength/roughness from highlights. Compare material swatch renders on the actual bead geometry. | Dark pigment versus shade and light color versus pigment remain coupled; do not fit a different pigment to every shadowed occurrence. |
| A4. Alternating render-and-compare fit | Python proposes bounded parameter changes, invokes POV-Ray, and compares paper, shadows, diffuse bead interiors and highlights separately. Alternate light, pigment and finish groups, starting with a coarse parameter grid and then local derivative-free refinement. | Flexible models can hide wrong geometry or camera processing; use held-out sections, parameter bounds and several initializations. |

I would initialize with **A1+A2**, estimate pigments with **A3**, then refine with
**A4**. Keeping these evidence types separate helps explain failures: broad shadow
errors suggest lighting/geometry; repeated diffuse-color errors suggest pigment
or color processing; highlight-width errors suggest source size or finish.
These are proposed diagnostic interpretations, not unique inverse solutions.

The paper should be a shadow-receiving plane (or a finite sheet if its edges
matter), with pigment estimated from this input and independently configurable.
Do not bake the photograph's shadows into its texture and then shadow it again.
Start smooth and matte; add measured fine texture/normal variation only if it
improves held-out comparisons. Magenta is a scene parameter, never the definition
of a background pixel. Margins, enclosed paper and cast-shadow paper all constrain
the fit, with uncertain bead-edge pixels excluded from calibration measurements.

Implementation reference: POV-Ray's `finish` offers diffuse, specular/roughness
and reflection controls. A finite `area_light` gives soft shadows; in 3.7,
`area_illumination` is needed to include its extent in diffuse/specular lighting.
Do not enlarge a default area light and assume its highlight response also changes.
See the official [3.7 lighting and finish reference](https://www.povray.org/documentation/3.7.0/r3_4.html).
Our proposal is to compare those direct-light highlights with a visible emissive
panel plus reflection only if highlight shape calls for it, checking against
double-counting the same source. Start with opaque smooth beads; introduce
`normal` or transmissive `interior` parameters only with image evidence, not a
guess about physical composition. Small finish differences by color are allowed.

Paper color may contribute indirect illumination onto beads. Compare a simple
fill model with radiosity if residuals support it. Radiosity models diffuse
interreflection; it changes how ambient/emission settings should be interpreted.
See the official [radiosity tutorial](https://wiki.povray.org/content/Documentation%3ATutorial_Section_3.7).
For a new scene use the documented [linear-light assumed_gamma convention](https://www.povray.org/documentation/view/3.7.0/260/).
Record image encoding, white balance and display transform; an iPhone JPEG need
not be an exact linear radiance measurement after decoding. Avoid treating raw
JPEG RGB as pigment. Fix an exposure/light scale convention and constrain color
balance: absolute reflectance and illumination cannot both be uniquely measured
from this one uncalibrated image. Report an effective matching scene and remaining
parameter alternatives rather than claiming the original physical lighting.

Future comparison: show the raw crop beside renders and residuals for a short
section with paper, cast shadow, multiple colors and highlights. Balance losses
by region so abundant paper pixels cannot swamp bead evidence; use robust diffuse
errors and treat clipped highlights separately. Hold out another section, compare
source models, and recover known synthetic examples before claiming generality.
Save scene parameters, input hashes, renderer version/options and Python commands.
Stop for an illustrated local review before fitting the full image. This catalog
does not authorize jumping over the pending local indexing/color pilot.

## Procedures for later aspects

This index starts the broader collection without turning every idea into a new
implementation task. Read the linked evidence before reuse; historical branch
results are not automatically present or validated on this branch.

| Aspect | Reusable procedure / next idea | Evidence and limitation |
| --- | --- | --- |
| Local measurements | Show raw context, interior endpoints, path, color strip and traces separately; retain rejected endpoints | [Hue paths](photo2/HUE_TRANSITIONS.md), [parallel paths](photo2/PARALLEL_PATHS.md); hue changes are supporting cues, not boundaries by themselves |
| Lighting and material | Fit paper illumination and bead highlights/shadows jointly with POV-Ray pigment/finish/normal/interior; compare alternative lights | Proposed future fitting; iPhone does not determine flash/light geometry; no physical-composition inference |
| Exposed bead shapes | Use 3D geometry, planar section direction/global camera and neighbor occlusion; distinguish visible centroid from physical center | [Shape quick model](photo2/PRIOR_WORK.md); historical R084/R085 atlas is synthetic evidence, not a universal oval detector |
| Helicity and spacings | Band-pass local FFT; compare direction-1 angle with local tangent; calibrate coordinate signs on both synthetic helicities | [Maker's method and display plan](photo2/PRIOR_WORK.md#r098--makers-directional-fft-method); not yet an implemented direction estimator |
| Index assignment | Label neighboring beads with ±1/±6/±7 differences; propagate integer indices and detect inconsistent cycles, keeping alternatives | [Historical method/graph discussion](https://github.com/rharriszzz/beads/blob/2c4c116bf7f7b9e8c773358a97740dcd77879a8a/photo2/METHODS.md); finding the correct image neighbors is still unresolved |
| Repeat recovery | For each candidate L, compare known colors at indices congruent modulo L; preserve empty slots and contradictions; validate withheld repeats | [Historical sequence tests](https://github.com/rharriszzz/beads/blob/2c4c116bf7f7b9e8c773358a97740dcd77879a8a/photo2/SEQUENCES.md); works conditionally on usable indices, not an image-only recovery claim |

Reproduce the current local background evidence with Python 3.12:

```bash
.venv/bin/python photo2/background_probe.py --output photo2/output/r092
.venv/bin/python photo2/background_transitions.py --output photo2/output/r099
.venv/bin/python photo2/parallel_paths.py --output photo2/output/r104
```

The linked reports preserve inputs, parameters and hashes. Outputs belong in
ignored directories; curated question illustrations remain tracked. This methods
catalog replaces neither those experiment records nor their documented failures.
