# Photo-2 reconstruction plan

Start: origin/master 020303ec16c81cb62802b6ae718adda9bbc2fdfa, the default branch.
Working branch: photo-2-reconstruction-v2. Python 3.12 and POV-Ray.

## Active schedule after the R115 body review

**R114 pilot and R115 B/D review recorded; stop after feedback.**
[Evidence and limitations](photo2/LOCAL_PILOT.md) and
[maker's B/D answer](photo2/LOCAL_PILOT_QUESTIONS.md) are available. D is separate
from B; its proximity to the edge makes its other properties harder to establish.
Twelve selected observations now comprise ten proposed bodies, D with confirmed
separation from B, and unresolved region L. No accepted global indices or pigment
labels; D's boundary and sample purity remain uncertain. Two conditional C/E/G
graphs remain consistent; the synthetic counterpart demonstrates that consistency
can hide a 13-index error. C1 photo appearance groups remain shading-sensitive.
Next bounded task is to present 3–6 local geometry comparison methods, then select
and run a small comparison to distinguish 6/7 families. Retain D's uncertain
attributes; its confirmed separation does not verify a neighbor edge or index.
Do not expand around the ring or run later phases automatically.
Stay here for discussion; gpt-6-astra / High, optional
fresh /new for the next numerical experiment. The schedule below retains the
R113 phase definitions; step 1 has now reached its specified review checkpoint.

The next aspect remains **local bead observations, relative indices and colors**.
Do not restart global boundary optimization or attempt the full pattern now.
The comparison with METHODS found stale boundary-first language, an implicit
assumption that usable local geometry already existed, and later phases listed
without clear input/output checkpoints. The schedule below replaces those gaps;
historical rationale follows for provenance, not as competing next-step orders.

1. **One local evidence pilot (R114 completed to review).** Select one diagnostic photo patch with
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
2. **Expand geometry and indices after review.** Extend useful local evidence
   around the necklace; bridge only supported ambiguous boundary stretches,
   connect index components, test helicity conventions and check closure to
   establish exact N. Review gaps and coverage before calling the inventory
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
continue executes the unfinished bounded step and stops. Recommend gpt-6-astra /
High, stay for methods discussion and use a fresh /new for the numerical pilot.

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
| Visible-bead indices and colors | Full-string bead_index plus observed palette ID, preserving missing/unknown states | R114 local pilot at review; conditional C/E/G index alternatives and twelve appearance summaries; global indices unresolved |
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
