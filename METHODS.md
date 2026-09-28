# Methods collection — bead-rope reconstruction

This is the reusable method index. The task and maker's construction facts live
in [INITIAL_QUESTION.md](INITIAL_QUESTION.md); current execution priorities live
in [PLAN.md](PLAN.md). Start each future entry with its inputs, output, assumptions,
procedure, known failures, validation and a reproduction link. Distinguish a
proposal from an implemented procedure and a validated capability.

## Current aspect: background pixels under varying illumination

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
| 2. Gaussian-window spectral texture | Power and directional structure after removing slow variation | Learn paper spectra and noise distributions | Hard shadows create power; dark smooth beads may not | Local FFT probes implemented, no global mask |
| 3. Spatial texture and local ordering | Small-scale structure across several spatial scales | Learn distribution of paper residuals and local order changes | Paper grain, sharp shadows, clipping and low signal | Gaussian residual implemented; ordering extension proposed |
| 4. Seeded region propagation | Agreement of neighboring regions with paper/bead evidence | Start with known exterior-paper seeds | Can leak across weak edges; enclosed paper needs separate support | Proposed; not just a border flood fill |
| 5. Boundary anchors and smooth envelope completion | Reliable silhouette sections plus larger-scale geometry | Establish exterior side and reject contour excursions into clear margins | Smooth wrong outlines are possible; small gaps need separate treatment | Maker-directed next comparison; bridge not yet fitted |

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
`r`, not simply a Gaussian blur of the image. Fit/subtract a weighted constant
or plane, apply the window, then compute the 2D FFT. Compare retained band power
with paper controls; also retain the spectrum's directional organization and
band-power ratios. Keep absolute power and normalized spectral shape separate.
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
| C. Follow texture across a lighting change | Compare fine paper structure after local trend removal/limited contrast normalization; use spatial filters or Gaussian-window FFT | Paper grain, hard shadows, mixed windows and dark bead interiors confuse the cue | Use spatial texture first for simplicity, retain FFT as a paired comparator |
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

Choose **method 1 + method 3 + method 5** as the first practical combination:

1. **Learn paper colors from the image.** Start with margin strips; add only
   supported shadow-paper samples. Compare an HSV box with a circular-hue density
   region. Use a restricted shading extension to propose additional candidates,
   not to turn every low-V pixel into background. This makes use of the maker's
   successful sampling idea without hard-coding the paper's pigment.
2. **Check candidates with local structure and context.** Use a small spatial
   filter stack as the initial texture check because its responses are easy to
   relate to the image. Run the existing FFT cue on the same patches as a
   comparison, keeping it if its spectral information improves discrimination.
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
is trustworthy. FFT remains part of the comparison, not a required final mask.
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
already satisfied. The next numerical step remains one wider-context anchor/bridge
comparison with shadow-aware supporting measurements, then illustrated review.

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
