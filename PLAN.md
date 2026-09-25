# Photo-2 reconstruction plan

For a plain-language account of the current capability, available splines,
background separation, bead detector and staged plan, read
[METHODS_AND_PLAN.md](METHODS_AND_PLAN.md) (R060, 2026-09-24).
R061 adds a reproducible saved-centerline overlay of photo 2 for inspection;
it does not change the generated-images-first analysis priority.

The goal is to extend `beads.pov` to reproduce `beads-photo-2.jpg` using Python
and POV-Ray, fit bead colors and POV-Ray materials, and identify helicity
and a repeating sequence of roughly 200–400 beads. Appearance fitting and
sequence identification are separate claims. Instructions are in `REQUEST_LOG.md`.

## Current step — R087 explained S/V paths and travel-order visuals

[Illustrated assessment](photo2/BEADS6_SV_PATHS.md) and
[walkthrough](photo2/review/r087/review.html): ten selected paths plus one rejected
placement in beads6, five translations and three RGB smoothing levels. Candidate
same-color seams can produce V dips with little S change; highlights inside one
apparent face can produce large S changes. K starts in the stripe being tested
and is rejected. Revised B is a different connection, not evidence of improved
classification accuracy. No bead identities or boundaries are established.

Maker found R082's lines mysterious and asks to see what is learned along paths.
AGENTS.md and [SHAPE_REASONING](photo2/SHAPE_REASONING.md) now require raw context,
explained endpoints, a separate sampling route, and useful travel-order color
strips with image-linked stops and plain-language lessons. Four sets of these
pictures include A, revised B, red highlight H and failed K. Old R082 cuts were
area-partition guesses, not fitted boundaries; preserve that historical evidence.

Five analytic controls pass; source/artifact hashes, 15 byte-identical repeat
artifacts, 9,240 samples and 165 metric records verify. All seven active counts
remain 313/318/304/342/328/310/327 and none is verified complete. Keep beads6
144/189, beads3 122/405, beads5 188, R081 queue, colors/borders/glint repairs,
missing observations and null indices. Ignore slivers; no source-pattern lookup.
Planar section views plus global camera view remain the geometric constraints.

[Two illustrated endpoint questions](photo2/BEADS6_SV_QUESTIONS.md) are pending;
R069 answers remain applied and older photo questions remain pending.
Next bounded task: incorporate endpoint feedback, then assess independently
perturbed interior endpoints in the same two neighborhoods. Preserve rejected
routes and publish a small illustrated supported/ambiguous/rejected path review.
If no answers arrive, retain identity hypotheses; questions are not approval
gates. Stop before mask/count/index changes or source-pattern lookup. Beads5 area
cuts remain deferred. Recommend **gpt-6-astra / High, fresh `/new`** after feedback;
user controls model/session changes and the next experiment.

## Underlying direction — R059: generated JPEGs, visible beads first

The user supersedes the second-anchor experiment: first identify every visible
bead, then choose how to infer the rest. Test beads1.jpg–beads7.jpg before any
photographs, without consulting the patterns in beads.pov. Existing pattern
knowledge is sufficient; no further construction-pattern questions are needed.

The blind attempt in **photo2/BLIND_GENERATED.md** produces image-only candidate
maps for all seven JPEGs, but **zero verified complete inventories and zero
recovered full patterns**. All four indexing variants per image have conflicts.
Do not treat the 352/392/435/410/403/354/417 candidates as correct bead counts.

R068–R082 provide provisional active maps for all seven JPEGs. Resolve or
characterize the remaining body/mask warnings as specified above; preserve missing observations and color/border
uncertainty. R069 supersedes earlier fragment-accounting plans: ignore slivers.

## Previous direction — R057 (superseded by R059)

The maker's new request supersedes the pending centroid/body-center diagnostic.
Work on two explicit tasks: detect the visible bead regions/colors from beauty
images, then assign bead indices using visible boundaries, local ±1/±6/±7
neighbors and forward-model predictions with smooth local corrections.
The maker can identify neighbors without centers and separate same-colored
beads; color selection is a useful computational aid, especially red/yellow.

The staged comparison and concrete correction-field experiment are specified in
**photo2/DETECTION_PROGRAM.md**. The 303-point photo centerline and two-click HSV
picker have been found and their provenance checked. First executable stage:
four fixed color/boundary methods on eight existing legacy beauty views, six
matched palette-control views and two mild blur/noise variants. Truth masks are
used only by the evaluator. Stop this step after the comparison, checks and
publication; no photo recovery or exact-index claim. Next is a bounded local
model-guided visible-boundary/index experiment, with seed/phase/width/centerline
perturbations and comparison of fixed versus smoothly corrected predictions.

R047 implemented the first **geometry-calibrated local** contour/index experiment;
see photo2/LOCAL_PATCH.md. Smooth corrections give 34/38 correct region/color/index
matches (one false region) on one warped R/Y/black patch and 38/38 on paired gray.
The known legacy camera/rope dimensions are supplied calibration. The click-margin
gate rejects all unwarped cases and most other trials, and all-black fitting fails.
An opposite-hand candidate has a near-tied contour score but mostly wrong indices.
These results do not establish automatic photo geometry, helicity or indexing.

R052 implements observed-region anchors and tests 17 click variants for both
three/four-bead groups in 16 conditions across two frozen patches. See
photo2/REGION_ANCHORS.md. Original R/Y/black identity/translation now accept all
17 variants with correct indices (34/37 and 32/34 matches); warped conditions
retain wrong-hand alternatives. Four-anchor acceptance rises 59→100/272, but
36 accepted trials include wrong indices. Second-patch gray gives 35/35 correct
output indices despite one wrong anchor selection; R/Y/black there and all-black
still fail. Higher acceptance does not establish reliable seed/helicity recovery.

R055 tests conservative bright-cavity repair; see photo2/HIGHLIGHT_REGIONS.md.
It assigns 4,672 pixels to their correct enclosing beads without adding background
or changing existing labels. Four-anchor acceptance rises 100→115/272; accepted
wrong-index trials stay at 36. Region detection/merge/split counts do not improve;
first nominal gray clicks still touch cavities shared by two regions, and the
second-gray seed slip remains. Smooth surfaces and usually one lighting-dependent
highlight are maker guidance, not an exactly-one-highlight constraint.

R057 compares fixed distance and RGB-gradient paths in shared bright cavities;
see photo2/SHARED_HIGHLIGHTS.md. Both raise four-anchor acceptance 115→140/272,
but add respectively 137/151 wrong-owner pixels and 216/301 unresolved-owner
pixels. Wrong-index trials remain 36; excluded-phase acceptance worsens 10→12/32.
Supported region/color/missing-index summaries and split/merge counts do not
improve. Keep R055 conservative abstention as the baseline, not either extension.
Unknown photo flash use remains unspecified; no lighting/model parameter changed.

Next bounded task: test a second spatially separated observed-region group
within each frozen crop against surviving wrong-helicity/phase candidates. Select from beauty and
observed regions before evaluator truth, keep fixed fits and R055 conservative
repair, and measure both lost correct and rejected wrong alternatives. Retain
jitter and background/duplicate/excluded-phase controls. Stop after local
hypothesis/seed/index evidence and checks, before ring growth or photo fitting.
Recommend gpt-6-astra / High with a fresh `/new` for this distinct step.

R049–R051 constraints: assistant marks anchors; equal bead size/shape, small
gloss differences; hole axes lengthwise, holes invisible; white thread invisible.

The historical plan below retains prior evidence; R059 defines the current next task.

## Whole plan

1. **Establish a reproducible forward model and evidence baseline.** Pull the
   workspace repositories, create a branch, read prior work, use Python 3.12,
   bring in the saved closed spline with provenance, render adjustable paper,
   lighting and beads, save photo comparisons and diagnostics, preserve the
   legacy renderer and create request/experiment/handoff records.
2. **Fit the bead geometry to visible evidence.** Label centers and colors in
   several separated photo patches, including both bends and straight sections.
   Assume bead proportions and hole orientation from legacy `beads.pov` (R016).
   Fit image scale, rope width, pitch, circumference count and phase under the
   crochet connectivity and small closure-twist constraints. Compare both hands.
   Decide whether the orthographic approximation is sufficient. Measure residuals
   and hold out patches; do not use arbitrary nearest-neighbor chain ordering.
3. **Fit paper, lighting and POV-Ray materials.** Use background-only patches
   and bead interiors/highlights/shadows. Separate illumination from pigment
   estimates where possible. Fit pigment color/filter/transmit, finish diffuse,
   specular/phong, roughness and reflection, normal texture, and interior IOR
   where relevant. Compare opaque/translucent and glossy/frosted settings by
   their rendered agreement with the photo. R008 defines material in this sense.
4. **Recover and validate the repeat.** Preserve hidden/uncertain positions in
   the helical index sequence. Search 200–400 jointly with remaining layout
   ambiguity; require total bead count N = kL for integer repeat count k and
   pattern length L (R021). Keep 2,698 as the adequate working bead-count
   estimate (R022); the maker's usual ranges do not require revising it.
   Do not treat that estimate as an exact divisibility constraint on L.
   Review established methods
   for periodic sequence recovery with missing observations before designing a
   custom algorithm. Use categorical evidence, held-out repeats, support/confidence
   maps, perturbation checks and synthetic known-pattern image round trips.
   Test documented photo-4/case-4 correspondence when needed. Accept a pattern
   only if the evidence distinguishes it from alternatives; report unresolved
   positions and symmetries instead of inventing beads.
5. **Render the recovered model and deliver.** Feed the inferred repeating
   sequence into the forward model, compare full image and held-out crops,
   retain sources/parameters/checks, and produce a higher-resolution final
   render after geometry and inference are validated.

Stages can inform each other, but each result must retain its evidence and
limitations. A visually plausible image alone cannot pass Step 4.

## Completed baseline: Step 1, plus exploratory Step 4 diagnostics

This step produces a runnable initial scene and a reliable place to continue.
It includes repository synchronization, all-branch Markdown review, Python 3.12
setup, sourced spline, shared bead geometry, procedural paper, area light/fill,
three material proxies, photo-sampled color preview, both-sign 200–400 candidate
ranking, focused tests, legacy render regression, written plan/request/handoff,
and the user's authorized add/commit/push.

Completion criteria:

- The photo-2 entry point renders headlessly with recorded settings and inputs.
- The closed spline/arc-length geometry passes finite/continuity checks; visual
  inspection and a mirror comparison catch gross coordinate mistakes.
- Synthetic missing-data tests recover a known repeat without losing indices
  or depending on palette numbering; no real-pattern success is implied.
- A legacy scene renders identically to the pre-change scene.
- All current instructions, actual results, limitations and one next task are
  recorded; scoped source/docs are committed and pushed, with user files excluded.

Stop this step after those checks and publication. Do not claim the exact bead
count, helicity, fitted POV-Ray material parameters or repeating pattern is
established. The exploratory period ranking establishes a baseline and tests
the data path only.
No animation, physical necklace measurement or Mac validation is in this step.

## R014 step: fixed-observation geometry comparison — complete at ambiguity

Created a provisional 103-center/color dataset across three straight and three
bend patches. Compared both hands on identical annotations, with shared geometry
trained on three patches and 27 withheld centers after partial calibration of
three separate patches. Full results and equations: `photo2/GEOMETRY.md`.
Withheld errors are 6.27/6.41 px and inconsistent across patches; neither hand
is accepted. Pitch/count/linear-twist have an exact degeneracy. Hole-axis tilt,
body dimensions and camera adequacy are unmeasured by these centers. Numerical
fits condition on zero local twist and front-half visibility. No change to
scene defaults or repeat claims. Step 2 as a whole remains open.

## R015 step: synthetic occlusion benchmark — complete at limited discrimination

Added a both-hand POV-Ray benchmark with exact instance/isolated masks and known
body geometry. Center-only scoring favors dense stress geometry under noise and
cannot distinguish depth reflection, size or tilt here. Exact internal boundaries
distinguish those discrete alternatives; silhouette alone does not resolve depth
reflection. The pitch/count/twist gauge remains pixel-identical. Missing-label
trials retain unknown indices; mask centroids and true centers are separate.
Details, checks and limitations: `photo2/SYNTHETIC.md`. No photo settings changed.
This is fixed-registration candidate discrimination with perfect masks, not
continuous geometry recovery; Step 2 remains open.

## R016: construction constraints and source authority

User guidance: beads are pre-strung, then a slipknot is added, then crocheted one
bead per chain stitch. The first three rows require dexterity. Additional twist
is small, no more than joining the ends requires. Ask the user about construction
uncertainties; no numerical twist bound or precise stitch-to-row map was supplied.
Use legacy `beads.pov` for assumed bead size/proportions and hole direction.
The user explicitly authorizes invented repeating patterns for synthetic tests.

Inspected source: local y is the hole axis; rotation by `chain_angle` about z
makes it tangent to the central circle, independent of `row_angle`. Hole/body
radius ratio is 0.14. Most cases use height/diameter 0.7, roundedness 0.8 and
relative size 1.0, with case-specific exceptions. All eight cases use nominal
6.5 beads/row. `nrows=round(nbeads/6.5)` and `exact_beads_per_row=nbeads/nrows`
close the helix with a small distributed adjustment. Image scale still needs
fitting; these are source assumptions, not newly recovered photo measurements.

R015 instead used hole ratio 0.3, height ratio 0.65 and tilt 20 degrees; current
photo settings use provisional height ratio 0.78. No code/settings change in
R016. Preserve that benchmark's evidence, but its unrestricted twist redundancy
does not prove ambiguity under the user's construction constraints. Repeated
colors in different visible sections can supply evidence for hidden repeat slots.

## R017–R023 legacy practice and visibility within Step 2

R017 supersedes the proposed recovery benchmark with direct practice using
`beads.pov`: invent a small repeating color sequence, render it through the
legacy scene, inspect the full necklace and enlarged bead overlaps at two phases,
and record what the source and images actually show. Keep the original camera,
lighting, materials, bead shape/orientation and closure rule. A small optional
pattern override may be added; verify the default legacy render is unchanged.
Retain deterministic pattern inputs, render commands, parameters and hashes;
generated scenes/images/reports stay ignored. Stop after the practice renders,
observations and checks, then commit/push. No segmentation, inverse benchmark,
photo refit or repeat-recovery claim in this step. Reconsider the next experiment
after inspecting these renders rather than automatically resuming R015's approach.

Further source reading: color is indexed by `bead_index mod pattern_length`,
whereas angular placement uses `exact_beads_per_row`; a color repeat need not
equal a geometric row. `clock` chooses one of eight cases and also sets two
rotations through `rclock`; practice views must stay in the same case. The legacy
scene represents bead bodies and their placement, not actual thread/stitches.

R017 completed: original-scene custom sequence rendered at two phases; default
render remains pixel-identical. Forty colors repeated 20 times give 800 beads,
123 turns and a 54-degree cross-section advance between repeat occurrences.
Full images and overlap crops inspected; details/commands in `photo2/PRACTICE.md`.
Thirteen tests, compilation, report hash verification and whitespace checks pass.

Next: trace selected known bead indices/repeat slots through these same legacy
renders and measure visibility across occurrences. Stop at an illustrated
visibility/sequence check before automated recovery or real-photo refit. Do not
automatically return to the unrestricted R015 model.

R018 counterexample supplied by the user: a repeat length divisible by 13 can
keep different colors on hidden and visible sides. At exactly 6.5 beads/turn,
13 beads span two turns, so repeat slots return to the same cross-section phase.
Include a multiple-of-13 practice pattern alongside the 40-bead example when
checking visibility. Actual coverage still depends on closure and camera view
around the ring; never infer completeness from repetition alone. Positions with
no visible evidence stay unknown. R020 moves focused advice questions to the
beginning of each round, superseding R018's original end-of-round timing.

R019 maker guidance: the user designed and made the necklace in photo 2 and has
never designed a multiple-of-13 pattern, although they may in future. Treat that
case as a synthetic counterexample, not an expected explanation of photo 2.
Every crochet stitch is the same; the maker need not count or manage rounds.
The half-step advance is built into attachment to the preceding row, not a
deliberate alternating stitch/round instruction. Geometric turns in the model
must not be confused with maker-controlled rounds. Exact photo repeat length
and a numerical attachment rule have not been supplied. Record these answers
as user knowledge; do not ask the same questions again. Next task unchanged.

R020 workflow correction: ask contextualized questions at the beginning of each
round and preserve answers/pending questions across sessions. The user finds
answering after /new difficult because the old context is no longer available
to them. This request records workflow/status and opens the questions; it does
not launch the visibility experiment. The next bounded task remains unchanged.

R021 answers: photo 2 settled into its photographed position on its own; the
user did not rotate sections to display selected colors. This does not measure
local twist or require a zero-twist model. The maker always uses an integer
number of pattern repeats, enough for 700–800 beads for a bracelet or
3,000–5,000 for a necklace. Apply N = kL in subsequent count/repeat fitting.
R022 clarifies that the provisional 2,698-bead photo estimate is good enough;
retain it without a count-revision task based on the usual necklace range.
Exact photo-2 count/repeat length remain unspecified. Do not
invent join edits or ask again whether whole repeats are used.

The user is confident the photo contains enough information and expects an
existing clever algorithm to suffice. Treat this as direction to seek established
methods, not a validated recovery result. Retain the next bounded visibility
check; before the later recovery implementation, research relevant primary
sources and justify the chosen method against this observation model. No new
algorithm, literature search or rendering was performed in this answer-saving turn.

R022: retain 2,698 beads as the working estimate. This accepts its adequacy for
current work, not an exact measured count; whole-repeat construction remains
valid without restricting candidate periods to divisors of 2,698. Next task unchanged.

## R023 completed; next bounded step

Measured known bead and repeat-slot visibility in the actual legacy camera/body
model using the 40-color/800-bead practice case and a 13-color/780-bead case.
Separate instrumentation passes match the original palette silhouettes/colors
exactly. All 40 slots have at least ten occurrences with >=100 visible pixels in
each tested phase. The 13-repeat case has zero phase drift but changing local
view direction around the ring; in phase half, slot 0 is exposed only in small
slivers (maximum 69 pixels, 1.6854% of that body's isolated projection). It fails
the 100-pixel coverage threshold; quarter-ring sections also have missing slots.
No slot is completely hidden over the full ring at the 1-pixel threshold in these
particular oblique views. Do not generalize to other views or photo identifiability.
Details and illustrated checks: `photo2/VISIBILITY.md`. Seventeen tests pass;
source/artifact checks and repeated-render numerical/pixel comparisons pass.
Original scene and photo settings unchanged; the 2,698 working estimate remains.

Next: review established image-registration and periodic-sequence methods from
primary sources, choose an approach that supports unknown bead indices, missing
slots, uncertain colors and whole-repeat closure, and specify a small validation
using the known legacy renders. Stop with a justified method choice and concrete
test plan, before implementing recovery or refitting the photo. This follows the
user's R021 direction to use existing algorithms and supersedes the earlier
next-visibility task, now complete. Open the next round with contextualized advice
questions; do not repeat R019–R022's saved construction answers.

R024 opens the new session with two questions about the intended photo-2 palette
and whether to allow occasional stringing errors. R025 answers are saved in the
handoff. Method-selection scope/stopping point unchanged; no review or experiment
started by the status/questions request. Stay in the current conversation.

R025 constraints for method selection: exactly three physical colors, red, yellow
and black. The maker checks every pattern sequence against the previous one;
assume no construction mistakes. Retain observation/registration uncertainty.
Insufficiently visible beads must be recorded as "color unknown" and contribute
no color evidence; retain sequence positions and unknown indices. Unknown is
not a fourth palette color, and later repeat-based inference must not overwrite
the observed unknown. No photo readability cutoff has been calibrated; do not
adopt R023's synthetic pixel thresholds as a supplied rule. Both opening questions
are answered; next remains method choice/test plan, before implementation/refit.

## R026 review draft and R027 indexing guidance

The primary-source review is drafted in `photo2/METHODS.md`. Select strong-period
partial-word testing for exact indexed observations, preserving unknown colors and
all compatible candidates. The proposed CPD registration component is now only a
fallback: during the review the maker offered a method to assign bead_index to
every visible bead. The requested walkthrough is pending in the handoff. Prioritize
that guidance, then finish the method/test-plan choice before any implementation.
The sequence-only synthetic test plan remains useful independently of index source.
No new recovery/registration experiment or photo refit occurred. R026 is unfinished
pending the indexing explanation; stay in this conversation with Astra/High.

## R028 final method choice and next bounded step

The maker supplies the missing rule: identify immediate neighbors along three
index directions ±1, ±6 and ±7. Select signed graph traversal/difference constraints
for bead indexing, then strong-period partial-word testing for color repeats.
R026's method review is complete with this steering incorporated in METHODS.md;
CPD is not the chosen indexing route, and no questions remain pending. No method
has yet been validated on photo 2.

Next: implement an illustrated neighbor/index audit on the four existing legacy
views, using known topology with anonymous vertex IDs to isolate propagation,
cycle consistency, missing edges/components and seam/winding handling. Inspect
projected neighbor directions at bends and the weak-slot region. Follow METHODS.md
§A; stop after the illustrated audit and checks before automatic edge detection,
photo indexing, color recovery or refit. Keep known index separate from unknown
color. Stay here with gpt-6-astra / High; no /new needed after this useful discussion.

## R030/R031: both helicities and supplied-edge audit — complete

R029's opening questions were answered by R030: ±1 is around the small radius,
±6/±7 are diagonal and depend on helicity. Unseen beads lie at visible-patch edges
according to the maker. User adds both-hand support in legacy beads.pov to the
scheduled graph audit. The new LegacyHelicity switch preserves the default;
Photo2's existing handedness control is separate.

NEIGHBORS.md records the both-hand audit. All 24 full-ring threshold graphs are
connected and all 240 graph trials recover exact relative indices with supplied
topology. Quarter patches retain offsets at the explicit index seam. Contradiction,
duplicate-index, missing-edge, winding and wrong-bridge controls delimit the claim:
consistent graph labels alone do not establish a correct image edge or helicity.
Eight original cases retain identical default pixels; four original fixtures
retain identical full-resolution beauty/ID/layout results. Both hands' masks,
colors, analytic placement and calibrated annotation projection are checked.
Twenty-five tests pass. No photo setting, fitted material or repeat is accepted.

Next bounded task: METHODS.md §B, sequence-only strong-period validation on known
synthetic indices with unknown colors, preserving all compatible periods and
unsupported slots. Stop after that report/tests before automatic image-edge
integration or photo refit. Keep 2,698 provisional; exact divisibility uses only
known synthetic counts. Retain gpt-6-astra / High and recommend fresh /new for
this distinct task. Begin its round with focused questions using saved answers.

## R032/R033: helicity name and pattern conventions

Rename the scene option to `Helicity` and update its callers, tests and current
examples. Preserve the +1 default and both-hand behavior. Historical generated
reports remain unchanged; their source hashes refer to their original revisions.

R033 answers: pattern length is the shortest repeating color block, with redundant
copies removed. Starting bead, stringing direction and helicity may be chosen
freely. Apply a consistent presentation convention while preserving unsupported
colors and genuinely different candidate completions/index mappings. A shortest
compatible period under erasure is not proof of the complete pattern's period.

Stop this step after the rename, checks and publication. Next remains METHODS.md
§B's sequence-only synthetic validation, stopping after its report/tests before
image-edge integration or photo refit. Use gpt-6-astra / High and stay in this
conversation; R032's opening questions are answered and no questions are pending.

## R035: maker's simpler sequence and photo period guidance

R034's questions are answered: photo 2 is the maker's longest pattern, with
shortest repeat <400. Under-five repeats are considered boring; five is acceptable.
Its black/yellow/red spirals were deliberately made continuous on custom graph
paper; the precise continuity rule remains unspecified. Length 42 is a useful
design length because it aligns with both 6/7 diagonals, not an asserted photo
period. Preserve the provisional count without a divisor restriction.

Introduce the maker's simpler `123333, 112333, 111233, 111123, 111112` example
in the next sequence-only test, interpreted as one 30-bead repeat with
1=red, 2=yellow, 3=black. Its shortest complete block is 30 by direct enumeration.
Keep the existing 40/13 visibility cases; the new example has no rendered
visibility evidence. Record-only follow-up; no experiment started. Stop the next
implementation after its synthetic report/tests, before image integration/refit.
Stay in this conversation with gpt-6-astra / High; no opening questions pending.

## R036: known-index sequence validation — complete

Implemented the maker's 30-bead symbolic control and the original 40/13 visibility
cases. All 72 cases and 288 quarter holdouts pass the expected checks; all 32
repository tests pass. The true period survives all 63 uncorrupted inputs with
correct supported colors. Its holdout totals are 24,383 correct, zero wrong and
52 abstained. The weak 13-slot view leaves slot 0 unknown with three distinct
completions. Wrong-color controls reject truth but can retain longer alternatives.
Preserve that ambiguity; no photo recovery or automatic image reading is claimed.
SEQUENCES.md contains the complete scope, commands, evidence and limitations.

Next bounded task: infer synthetic construction neighbors from supplied visible-
mask centroids with anonymous IDs, keeping source bead indices/colors hidden from
edge construction. Evaluate ±1/±6/±7 edge labels and relative indices against truth
at bends/occluded edges/crossings, preserving unresolved alternatives. Supplied
mask detections remain oracle segmentation. Stop after an illustrated report and
checks, before beauty segmentation or photo fitting. Recommend gpt-6-astra / High
and a fresh /new for this distinct perception step. No new questions at round end.

## R038: shape guidance for neighbor inference

R037 opening questions are answered. The maker reports almost no tilting/sliding;
top beads look rectangular, with direction 1 close along the shorter dimension
and directions 6/7 forming staggered brick-like layers. Preserve the exact wording
in REQUEST_LOG/handoff rather than treating it as a calibrated image-axis rule.
Re-read beads.pov and bead-shape.inc: rounded hollow cylinders, case-1 axial
height/diameter 0.7, local y hole axis, body rotation by chain_angle only.
Extend the next test to compare centroid-only inference with visible-mask shape/
orientation cues; withhold truth axes, indices and colors from construction.
The report/check stopping point and oracle-segmentation limitation remain unchanged.
No experiment started by this advice record. Stay in this conversation with
gpt-6-astra / High; no further /new needed and no questions pending.

## R039: centroid-versus-shape neighbor baseline — complete

Implemented the bounded synthetic perception comparison; see photo2/INFERENCE.md.
At T12, pair precision improves from 90.85% to 95.45% with mask orientation, while
recall falls from 61.30% to 55.61%. Even the best truth-evaluated sign/convention
choice gives shape signed precision only 82.24%. All 192 convention graphs retain
contradictions; no photo indexing claimed. The ideal brick lattice works exactly,
but missing detections cause four false bridges and the superposed-ring crossing
control still gives 96 shape cross-sheet links. Retain these exposed failures.

All 39 tests, compilation, provenance/whitespace checks pass; two runs reproduce
all 208 artifacts byte for byte. No scene/material or photo changes. Publish the
scoped source/report/docs and R037/R038 advice/status records. Generated artifacts
and environments remain ignored.

Next bounded task: joint local triangle/lattice constraints for selecting and
signing ±1/±6/±7 edges using 1+6=7, mask orientation and explicit abstention. Keep
this fixed baseline and missing/crossing controls; evaluate against withheld truth.
Stop after synthetic edge/component-index evidence and checks, before photo
segmentation, sequence integration or fitting. Recommend gpt-6-astra / High with
a fresh /new for that distinct algorithm task. No questions at round end.

## R041/R042: illustrate a concrete failure — complete

NEIGHBOR_FAILURE.md and show_neighbor_failure.py locate one saved synthetic
false edge in the whole render, with a labeled detail. The predicted +7 edge
611 → 613 has true difference +2; visible bead 612 gives the intervening +1 path.
This is an algorithm failure, not established human/photo ambiguity. Source and
artifact hashes, embedded original bytes and two-run reproducibility checked.
No inference or photo-fitting work was started by this illustration request.

The maker says ambiguity occurs only near edges and advises tracing 1, 6 and 7.
The rough rectangular color paths probably use ±6/±7, correcting the initial
±1 recollection; exact pattern steps remain unspecified. Carry these into the
next bounded joint-tracing/constraint test without making color-based truth
assumptions. Stop after synthetic edge/component-index checks. Stay here with
gpt-6-astra / High for this example's review; no /new needed now.

## R043: joint triangle and three-family tracing — complete at excessive abstention

See photo2/JOINT_INFERENCE.md for the fixed rule, scores, controls and reproduction.
Local 1+6=7 triangles and smooth same-family continuations reject the known false
bridges but lose too many true edges: T12 shape precision 96.86%, recall 16.73%
versus baseline 95.45%/55.61%. Best evaluator-only signed precision is 94.40%.
Even best-convention evaluation leaves 66/846 nonseed relative indices wrong in
consistent components. This does not validate photo indexing or human ambiguity.
The ideal lattice stays exact; missing detections and superposed crossings lose
their false bridges at the cost of further missing edges. R041's false shortcut
and its true replacement path are both absent.

All 47 tests, compilation/whitespace and hash checks pass. Two final audits
reproduce all 114 artifacts; all 48 paired shuffles preserve signed edges.
Source/artifact provenance and failed NumPy-scalar serialization (corrected) are
recorded. No scene/material, photo, segmentation or sequence changes. Publish ten
scoped source/docs files; generated outputs/environments stay ignored.

Next bounded task: compare visible-mask centroids with projected true body
centers on the same synthetic vertices and audit true 1/6/7 turn/spacing/support
violations. Use saved layout CSVs and neighbor_audit.projected_centers; distinguish
instrumented truth diagnostics from recoverable image evidence. Mark losses in
whole-image context and stop after the causal comparison/report, before another
inference algorithm or photo fit. gpt-6-astra / High; fresh /new recommended.
