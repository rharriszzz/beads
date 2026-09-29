# Photo-2 reconstruction plan

Start: origin/master 020303ec16c81cb62802b6ae718adda9bbc2fdfa, the default branch.
Working branch: photo-2-reconstruction-v2. Python 3.12 and POV-Ray.

**Current model recommendation — R134:** gpt-6.1-sol / High for the next bounded
task. The [official model catalog](https://developers.openai.com/api/docs/models)
describes near-Astra performance and lists input/output prices of $2/$10 per
million tokens versus Astra's $10/$50, checked 2026-09-29. This supersedes older
Astra recommendations below. Project-specific quality remains to be evaluated
using the existing synthetic, holdout and illustrated checks. User controls
model selection; stay in this session, no /new required.

## Current task — R138–R141: numbered locations and direction series

The requested [raw-photo labeler](photo2/LABELER.md) now lets the maker place each
bead by hand, assign a unique number, then Start a d1/d2/d3 series, click existing
beads in order and End it. Arrows and the sidebar show click order. Renumbering
preserves stable-ID series references; saving/undo cover locations and series.

[Q138.1 and Q139.1](photo2/LABELER_QUESTIONS.md) are answered. R140–R141 clarify
d3 as down to up clockwise, equivalently up to down counterclockwise; d2 remains
up to down clockwise. No d2/d3 mapping to 6/7 or numerical signs is supplied.

**Stopping point:** the program and automated verification are complete for this
bounded step. Real graphical-browser interaction is unverified in this environment.
**Next task:** the maker runs the program and supplies numbered patch/series
annotations; review those before resuming numerical chart comparison.

This collects manual evidence for local geometry/neighbors (stage 1). No old
assistant markers are preloaded; unique numbers are not accepted as string indices.
The coupled BC/CG alternatives and unknown signs remain preserved for later analysis.

## Where this sits in the overall solution

| Stage | Purpose | Status |
| --- | --- | --- |
| 1. Local geometry and neighbors | Establish usable bead surfaces and +/-1/6/7 relations on a small patch | **Current.** Numbered maker locations/series program ready; awaiting annotations, coupled 6/7 families/signs unresolved |
| 2. Whole-necklace coverage and indexing | Follow supported central bodies around the loop; preserve gaps; resolve string indices and closure/N | Not started from an accepted local chart |
| 3. Shortest repeating pattern | Combine verified indices and uncertain colors; test repeat divisors with conflict witnesses | Waiting for stage 2 |
| 4. Rendered appearance | Fit POV-Ray materials, lights and camera; compare against the photo | Local rendering calibrated, final appearance recovery pending |

Background/centerline refinement and the requested FFT comparisons support these
stages when needed; they are not completed merely because local fitting has begun.
The final method must estimate location and appearance from each input. Today's
hand-selected patch is diagnostic evidence, not an automatic reconstruction.

## Prior bounded step — R135–R136: correct the local neighbor chart

**Latest bounded step completed:** tested selected boundary brackets with interior
support. Narrow bands still enlarged C; stronger H2 boundary penalties improved C
but lost other clear interiors and reduced G overlap to 48.2%. No replacement fit
was adopted. Eight independent render checks pass; local optimization remains limited.

**New maker evidence — R136:** B/C family 6 implies C/G family 7; B/C family 7
implies C/G family 6. Both signs are unresolved. Both old charts used B/C family 1,
so neither represents these alternatives; retain their fits as historical controls,
superseding them as active photo maps. [Verbatim answer and illustration](photo2/SURFACE_CONSTRAINT_QUESTIONS.md).

**Next bounded task:** compare the two coupled B/C/G families and unresolved signs,
rebuilding other proposed patch relations from supported evidence. Do not inherit
old E/F/H/J offsets as maker facts. Keep P unknown and G's pixels withheld from
continuous fitting; future graph construction will use the maker's C/G relation.
No whole-necklace walk or full-string index recovery yet.

[Completed experiment and limitations](photo2/BOUNDARY_ARC_FIT.md).
The current stopping point is this comparison plus saved maker review.
[Q135.1](photo2/BOUNDARY_ARC_QUESTIONS.md) about C's proposed segments remains
pending; Q132.1 is answered. R137's [wider context](photo2/review/r135/wider-context.png)
is in both review files.


## Starting evidence and limits

The [seven-body fit](photo2/LOCAL_SURFACE_FIT.md) is complete to illustrated review.
B/C/E/F/H/J were fitted; G was withheld. H1/H2 are historical controls superseded
as active photo mappings by R136; they do not represent its supplied alternatives.
Orthographic held-out overlap is 76.1%/80.5%; a nominal metadata-based perspective
fit gives 75.4%/82.2%. These compare against assistant polygons, not verified truth.
C and F retain meaningful outline errors, so no full-ring propagation is justified.
The independent POV surface checks and assisted known-synthetic inverse test pass.

R127 supplies no camera elevation: reflections couple camera and lighting.
R128 says iPhone, likely fairly close. File metadata identifies an iPhone 11 Pro
lens, focal 4.25mm, 51mm equivalent and 1.96875 digital zoom; no subject distance.
Perspective sensitivity is evaluated at half/nominal/double an approximate focal
calibration; image-center principal point and unknown crop remain assumptions.
The 55-degree local camera/phase convention is not measured global elevation.

**R130–R131 review:** [Q126.1](photo2/LOCAL_SURFACE_FIT_QUESTIONS.md) is answered.
R130 describes shadow from four adjacent beads; R131 considers P probably outside
a bead and near an edge. This remains tentative, with no exact boundary or edge
type supplied. The picture contains four red, two yellow and at least two black
beads: contextual maker evidence, not a color-to-ID map or a changed fitting
inventory. Numerical R126 results remain frozen.

R132 completed the comparison described above. A further local fit must keep
P out of positive and negative ownership constraints; the diagnostic circle is
not a maker-supplied boundary. All twelve original IDs, D/B separation and
excluded A/D/I/K/L remain preserved. See R136 above for the current family alternatives.

The current stop is the boundary-bracket comparison and saved R136/R137 review;
local correspondence remains unresolved. FFT comparisons remain pending, adoption
optional. Recommend gpt-6.1-sol / High (R134). Stay in this session; R126 explicitly
declines /new and reports
84% context remaining (user report, not an independently measured status).
Historical scheduling below is superseded where it requests the already completed
first seven-body fit or defers black beads.

The next aspect is **local bead geometry and correspondence**, with colors as evidence.
Do not restart global boundary optimization or attempt the full pattern now.
The comparison with METHODS found stale boundary-first language, an implicit
assumption that usable local geometry already existed, and later phases listed
without clear input/output checkpoints. The schedule below replaces those gaps;
historical rationale follows for provenance, not as competing next-step orders.

1. **Establish reliable local geometry and neighbors (current stage; R114 pilot reviewed).** Select one diagnostic photo patch with
   several clear bodies, same-color adjacency and a dark/highlight case where
   available. Show raw context, candidate bodies/interior samples and local
   tangent/spacing evidence using B1/B4/B5 before attempting I1 neighbor labels
   and C1 color summaries. Use I2/C2 only for a specific ambiguity. Record manual
   assistance; a patch selected for review is not automatic necklace localization.
   Compare with a small known synthetic counterpart, with truth used only for
   evaluation. Inventory unresolved visible bodies as well as supported ones.
   Deliver raw/candidate/uncertainty panels, observation and edge tables, relative
   index alternatives, palette evidence, checks and one focused illustrated
   question in the tracked question file. **Stop for local review**, even if
   insufficient evidence prevents a confident graph. No full-ring count yet.
2. **Expand geometric coordinates after review; derive indices later.** Extend useful local evidence
   around the necklace; bridge only supported ambiguous boundary stretches,
   connect local coordinate charts, test helicity conventions, then derive string
   indices and check closure to establish exact N. Review gaps and central-body coverage before calling the inventory
   complete. Run the two supporting FFT comparisons below in separate bounded
   steps during this phase, or earlier if the first pilot needs one; choosing
   not to adopt FFTs must not erase the requested exploration.
3. **Shortest-repeat checkpoint.** With resolved global indices, verified exact
   N and accepted color evidence, adapt historical P1 and check with P2. Apply
   photo-specific L<400, L dividing N and L not divisible by 13; include shorter
   candidates below the rough 200 estimate. Deliver rejected-length witnesses,
   slot support/unknowns, alternatives and withheld-section predictions. Stop
   to review unresolved pattern slots rather than inventing their colors.
4. **POV-Ray appearance checkpoint.** Once geometry and palette assignments
   support it, compare A1/A2 paper-shadow/highlight initialization, A3 pooled
   pigments and A4 bounded render refinement on one section plus a held-out
   section. Stop at raw/render/residual review before full-image tuning. Unknown
   pattern slots outside the tested observations need not block a local material
   experiment, but must remain explicit. Final scene needs both completed or
   explicitly uncertain sequence inputs and tested appearance parameters.

Supporting explorations are bounded tasks, not mandatory algorithm components:

- **Background FFT:** compare the explorer's raw Gaussian low-pass power fraction
  with current detrended/spatial cues on lit paper, shadowed paper and beads;
  report exact windows, masks and power normalization. Use a local anchor/bridge
  comparison if ambiguous boundaries prevent useful tangent/width evidence.
- **Directional FFT:** compare Gaussian band-pass peak pairs with spatial neighbor
  evidence on the same short section, testing 1/6/7 labels and helicity conventions
  against synthetic truth. Show window/band masks, pair reconstructions/direction
  overlays and sensitivity; retain a non-FFT solution if it works better.

These checkpoints do not authorize running all phases in one turn. A standalone
continue executes the unfinished bounded step and stops. Recommend gpt-6.1-sol /
High; stay in the current session as requested, no /new required.

## Evidence and rationale retained from preceding requests

R106 documentation detour completed: [initial question and construction facts](INITIAL_QUESTION.md)
and [reusable methods collection](METHODS.md). The catalog proposes five background
methods under varying illumination, with failures and validation plans. No new
classifier or contour was implemented. All supplied images place the bracelet
centrally with substantial margins; use that generic prior for background seeds,
not fixed bead coordinates or a prescribed border width. Enclosed paper/gaps need
support beyond exterior connectivity. The anchor/bridge experiment was then the
next task; it remains unrun and is now supporting work under the active schedule.

R107–R108 extend the [methods discussion](METHODS.md#shadowed-paper-alternatives-and-evaluation-for-splines)
with the maker's strip-to-HSV-region proposal and five shadow treatments.
Recommend image-trained lit/shadow appearance, spatial texture with an FFT
comparison, and supported boundary anchors with smooth completion. This is a
reasoned choice, not a measured full-image winner. The intermediate goal is a
useful spline without broad cast-shadow bias; pixel-perfect masks can wait for
later geometry refinement. Judge signed displacement, stability and supported
coverage, preserving unresolved stretches.

R109 adds [six bead-analysis methods given a centerline](METHODS.md#bead-analysis-given-approximate-boundaries-and-a-centerline):
centerline HSV paths, Gaussian-window FFT at necklace-width scale, spatial
repetition, seam tracing, color/highlight regions, and local 3D/neighbor fitting.
R109 recommended the maker's HSV + FFT pair first, with spatial repetition as an
interpretation check; then region/color and geometry refinement. This is a
conditional methods discussion, not a recovered centerline or a new detector.
The bounded boundary task remains pending; once a usable curve is available,
compare these cues on a few sections and stop for illustrated review before
whole-necklace indexing or pattern recovery.

R110 clarifies prior practical FFT success and [the source baseline](photo2/FFT_EXPLORER_NOTES.md):
Gaussian-window low-pass power for background (saved scanner uses a fraction),
band-pass plus three opposite peak pairs for directions1/6/7. Reproduce the raw
explorer statistic before replacing it with detrending/spatial texture; method
priority becomes appearance + FFT + smooth completion, spatial cue as comparator.
This was a method-priority update, not a benchmark; the active R111/R113 schedule supersedes
its implication that FFT work must come first.

**R111 supersedes FFT-first scheduling:** explore FFTs for both background/shadows
and bead directions/spacings/helicity, but adoption is optional. The next inference
objective is bead_index and color for every clearly visible body. [Chosen methods](METHODS.md#assign-bead_index-and-color-to-clearly-visible-beads):
signed ±1/±6/±7 neighbor graph plus robust interior color/palette assignment,
with local 3D template and shading models as targeted support. Ordered strip/row
tracking and joint discrete constraints are alternatives for specific failures.
No new assignments or measured performance in this method-selection step.

R112 extends the documentation roadmap: [two shortest-repeat methods](METHODS.md#shortest-color-pattern-from-indexed-observations)
and [four POV-Ray appearance methods](METHODS.md#fit-paper-bead-materials-and-lighting-in-pov-ray).
Prefer residue-class consistency, reusing the historical partial-word solver's
core with explicit configurable inputs. With verified exact N, test candidate
divisors; exclude multiples of 13 for this necklace, not generic inputs or N.
Preserve unsupported slots and contradiction witnesses. The <400 bound is saved;
the rough 200 lower estimate must not conceal shorter compatible candidates.
For later appearance, initialize from paper/shadows and bead highlights, pool
pigments by color, then alternate bounded Python-driven POV-Ray fits. These are
method proposals, not a recovered sequence, count or appearance fit. The local
index/color pilot remains the next numerical step.

One aspect at a time; offer 3–6 implementation methods at each phase and use
short illustrated feedback rounds. A phase boundary is a reviewable result,
not automatic authorization to select all later methods.

R103 generality constraint: final inference should use little image-specific
color or bead-location knowledge. Current fixed routes, paper reference centers
and historical HSV boxes are diagnostic fixtures only. The eventual pipeline
must estimate background statistics and necklace location from the supplied
image; color cues should use local differences or image-derived models, not
hard-coded red beads/magenta paper. Validate on changed palettes/backgrounds and
translated/rotated placements, keeping manually reviewed cases separate from
the algorithm's inputs. These generalization tests have not yet run.

| Aspect | Intended result | Status |
| --- | --- | --- |
| Paper versus necklace | Paper includes cast shadow and visible gaps; uncertain border retained | R104 hue trend survives ±8 px; hue maxima and reference-scaled texture crossings remain unreliable as edge rules |
| Lighting and paper appearance | Independently parameterized paper pigment; lighting constrained by shadows and specular reflections | R112 four fitting methods and official POV-Ray references saved; fitting deferred |
| Planar centerline and camera | Spline matching physical arrangement, with global plane/camera view | Deferred; old spline is reference, not ground truth |
| Bead locations and exposed shapes | Occlusion-aware 3D candidates with missing/hidden observations | R115: ten proposed bodies, D confirmed distinct from B, L unresolved; D's edge/shape remain uncertain; no automatic detector or accepted outlines |
| Colors and POV-Ray materials | Pigment/finish/normal/interior separated from lighting effects | R114 C1 appearance baseline splits red-looking surfaces; pigment/material fitting deferred |
| Visible-bead indices and colors | Full-string bead_index plus observed palette ID, preserving missing/unknown states | R116 prioritizes clear non-black interior bodies; R114 alternatives/summaries retained, global indices unresolved |
| Helicity and spacings | Band-pass FFT peaks for directions 1/6/7; direction-1 angle relative to local centerline | R098/R109 maker method saved, width-scale window specified qualitatively; synthetic sign/convention validation pending |
| Repeating pattern | Shortest compatible divisor of exact N, <400 and not divisible by 13; preserve ambiguity | R112 two methods documented; include candidates below rough 200 estimate; no photo-2 sequence established |

The phases can require revisiting shared parameters; lighting and material are
coupled. Background color is a configurable scene property, never a fixed rule
that determines foreground membership. Preserve legacy beads.pov while methods
are reviewed; add a configurable photo-2 mode once supported scene inputs exist.

For the later directional FFT phase, use [the R098 method and display plan](photo2/PRIOR_WORK.md#r098--makers-directional-fft-method):
retain a bead-spacing frequency band, label peak pairs, and show their relationship
to a tangent-aligned image patch. Compare the direction-1 relative angle for known
opposite helicities before assigning the photograph's hand. This preserves the
maker's proposed angular rule without treating the background-energy probe as
an implemented direction estimator.

R099 completed the bounded transition comparison: 48/24/12/6-pixel windows,
DC-only/finite exclusions, raw/detrended power fractions, spatial texture and
paper references. [Findings and limitations](photo2/BACKGROUND_TRANSITIONS.md).
Small windows narrow the texture response but have not established an edge rule.

R100–R102 adds [hue measurements and confirmed HSV-map provenance](photo2/HUE_TRANSITIONS.md).
Overlap does not eliminate useful hue transitions; white-balanced presets must
not be applied to the original JPEG without a new calibration.

R104 completes the [parallel-route/reference sensitivity comparison](photo2/PARALLEL_PATHS.md).
Largest hue changes can mark internal bead colors/highlights; changing paper
reference moves texture crossings by up to 32 pixels. No contour points selected.

R105 supplies the next strategy: move farther along the necklace in either
direction until boundary evidence is reliable; bridge ambiguous stretches with
a smooth large-scale envelope, keeping bead-scale scallops separate.

The active schedule above is the authoritative next-task description. No confirmed
centerline or automatic bead detections yet exist: review the R114 local proposals
before propagating indices. A perfect global mask is not a prerequisite.

Available supporting boundary task: expand one ambiguous neighborhood along the necklace, show
candidate reliable boundary anchors on either side and compare a short smooth
bridge with the raw image. Compare local cubic interpolation, a robust smoothing
spline, and coupled inner/outer envelopes as implementation options. Start with
the simplest local bridge if evidence supports its endpoints. Show anchor evidence
separately from inferred spans and sensitivity to anchor choice; leave unsupported
spans unresolved. Use supported paper/shadow samples and local texture to assess
anchors; do not expand this into a perfect-mask prerequisite. Stop for review
before whole-necklace contour adoption,
centerline/scene fitting or bead assignments. Diagnostic crops remain validation
fixtures, not runtime priors. The earlier proposed whole-image search is deferred
to follow the maker's more specific guidance.
