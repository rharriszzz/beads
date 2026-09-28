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

## Comparison and recommendation

Use the same inputs and evaluate each method before combining them. Track paper
recall in lit, shadowed, enclosed and narrow-gap regions; bead pixels incorrectly
called paper, especially black beads; boundary displacement; and the unresolved
fraction. Vary lighting, exposure, background/bead palette, placement, blur and
JPEG quality. Keep mask/ID render passes strictly on the evaluation side; beauty
images are the analysis inputs. Extreme clipping tests should allow abstention.
Vary the perimeter sampling width and hold out whole regions so overlapping windows
do not masquerade as independent validation. Review raw context beside labels and
support maps. No such full comparison has run in this documentation step.

**Recommended division of work:** margin samples initialize background statistics;
texture proposes clear paper/bead neighborhoods; the anchor/bridge method addresses
locally ambiguous boundaries. This is a proposed combination, not an implemented
solver. Keep the next numerical step bounded to the already requested wider-context
anchor/bridge comparison. The new margins make later automatic initialization more
practical without changing the immediate need to review local evidence.

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
