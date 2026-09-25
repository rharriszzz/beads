# Reconstruction experiments

Append results; preserve failed attempts and limitations.

## 2026-09-23 — Initial forward model and diagnostic baseline

Started at `402663e` on new branch `photo-2-reconstruction`. All eight sibling
repository pulls reported already up to date. Existing `beads-render.png` and
`image-to-pattern/pattern_from_photo/` were present before work and preserved.

The saved FFT-explorer centerline visually follows the full nonconvex necklace
shape. A periodic cubic fit has arc length 9,235.5869 source pixels. The first
POV render exposed a horizontal reflection caused by `look_at` rotating the
camera basis. Explicit `direction -z`, `right x` and `up y` correct it. A
color-mask overlap check now records ordinary and reflected comparisons.

The first prototype ran on system Python 3.10.12. After the user's Python 3.12
instruction, created beads' own environment, installed NumPy/SciPy/Pillow, and
reran the baseline with CPython 3.12.14. No other environment was changed.

Five focused numerical tests pass: closed-path spacing/frame continuity;
handedness reflection and height; photo-specific paper/shadow rejection;
synthetic 271-bead repeat recovery with 55% hidden and 6% randomized labels;
preservation of unknown residues. A test initially exposed palette-ID-dependent
tie breaking in held-out scoring; fractional tie credit fixes it and makes
the candidate ordering invariant to color renumbering. These tests validate
parts of the machinery, not synthetic-image round trips or the real pattern.

Legacy regression: rendered original HEAD and modified `beads.pov`, both at
320x240 and clock 0.32 with two threads. PNG pixel arrays match exactly, maximum
channel difference zero. Evidence: `output/legacy-check.json` and render logs.

Baseline photo preview: 800x1002, 2,698 model beads, 415 turns, effective pitch
22.2544 pixels, all positions finite. Rough color-mask IoU is 0.4731 versus
0.1044 for a horizontally reflected render. This checks broad registration;
it is not a bead segmentation accuracy score. Visually the lattice remains
too regular and square, with mismatched highlights, local bead orientation,
color boundaries and shadow softness. Paper color/texture are initial proxies.

For negative sign: 1,047 retained color observations; top-ranked period 202,
held-out accuracy 0.4497, majority baseline 0.4315. For positive sign: 1,018
retained observations; top-ranked period 311, accuracy 0.4555, baseline 0.4064,
held-out coverage 0.9614. The hypotheses have different sampled positions;
their accuracies are not a controlled handedness comparison. **Both helicity
and repeat remain unresolved.** A visually fitting observation render is not
evidence for the inferred period. No scientific acceptance gate is passed.

Next: label bead centers/colors in several separated sections of the unwrapped
rope, then fit pitch, circumference count, phase, local twist and hole-axis tilt
against those observations before ranking repeat lengths again.

## 2026-09-23 — R014 fixed-label geometry comparison

On daisy, clean `photo-2-reconstruction` at `f6fb3b3`, fetch verified 0/0 with
upstream after retrying outside the read-only .git sandbox. Python 3.12.14.
The supplied session/status and continuation request are retained under R014.

Created 103 provisional visual center/color annotations across six 160-pixel
unwrapped patches (three bends, three straights), before fitting model overlays.
Colors and unknown original chain indices are retained. Dark bead/glint boundaries
are uncertain; four pixels is only a typical visual annotation-error estimate.
The dataset is not complete or human verified. See `GEOMETRY.md` for equations,
parameters, result tables and reproduction commands.

Fit both hands to the exact same 51 training centers. Three separate validation
patches use 25 left-half centers only for local alignment; 27 right-half centers
are withheld. This is partial patch holdout, not fully unseen-patch prediction.
Unwrapped withheld RMSE: negative 6.2728 px, positive 6.4124 px. Original-photo
withheld RMSE: 6.2698 versus 6.4141 px. Training prefers positive (3.9479 versus
5.9696 px), and withheld patch preferences disagree. All four seed searches
converge numerically, but the positive seeds find distinct radius/count solutions.
No hand or fitted dimension is accepted; high density is favored by the incomplete
point-set objective, which does not penalize unmatched model beads.

Resolved an identifiability question algebraically and numerically: pitch,
circumference count and unconstrained linear twist have an exact gauge freedom.
The conditional numerical fits therefore fix twist to zero. Center-only data
also cannot constrain hole-axis tilt, body dimensions or perspective; no hole
rims were confidently labeled. Removing assumed front-half visibility yields
an exact projected-hand ambiguity. Keep all these limitations explicit.

Two full deterministic runs reproduced the same numerical results; the second
updated source/data provenance and identifiability fields after documentation of
annotation uncertainty. Enlarged source, label and positive-fit panels were
inspected for bend_b and straight_b. The original full centerline/unwrap and all
six source patches were inspected before labeling. No annotation was adjusted
using fit residuals. Nine focused tests passed, including four new numerical
checks; the known-lattice test does not validate synthetic-image recovery.
No POV-Ray source changed; legacy render rerun, material fitting, camera model
comparison, whole-necklace fit, synthetic-image round trip and repeat search were
not performed. Generated images/reports and .venv remain ignored.

Next bounded task: occlusion-aware synthetic patch benchmark in POV-Ray, with
Python center/outline scoring, testing both hands, bead density and missing labels.
Stop at measured recovery or ambiguity on known geometry before real-photo refit.

R014 final-run SHA-256 provenance:

- `photo2/geometry-labels.json`: `c8f2f5c34dd72a661e7cd30b03633585d5a837a31254f0cc38eb0d4df561626a`
- `photo2/fit_geometry.py`: `b64fcdceb43512cbca21e06cdebeb4ff1457ea30dd2a947ee26ed473b762870a`
- `photo2/reconstruct.py`: `35322da2ed21c39f5b1c1cd68401377b811a53e2786fa1b11288e61079d901f9`
- `photo2/centerline.json`: `49c59cc6049815e9cac9fd94e097e0aaf1d9f647d287d7920793aca2acfd9f36`
- `beads-photo-2.jpg`: `eb7c9edb62f5580ef56632872da48da92556d62b758295137068cc2404dc8fbb`
- Generated `output/geometry-fit/report.json`: `1c6c18da6944541e566689d8efe0c98c3e5ea0f911ad7bf92c171fee3e9ab705`

## 2026-09-23 — R015 synthetic occlusion benchmark

Started on daisy at clean `01dd173`, tracking `photo-2-reconstruction`; fetch
confirmed 0/0 after escalation for read-only .git. User's old usage/current
session status are separately attributed in R015. Python 3.12.14, NumPy 2.5.3,
SciPy 1.18.1, Pillow 12.3.0, POV-Ray 3.7.0.10.unofficial.

Added `synthetic_benchmark.py`, `synthetic-patch.pov` and four focused tests.
Each complete run renders 84 images: 24 candidate ID masks, two beauty images
and 58 isolated reference beads. Ground truth has 29 visible centers per hand;
12 per hand are behind the cylinder's front half. Reference bodies are certified
non-intersecting by enclosing spheres. Partial occlusion affects 15/19 beads;
centroid-to-center RMS shifts are 1.5336/1.4347 units (negative/positive hand).
Exact parameters, equations, metrics and limitations are in `SYNTHETIC.md`.

Both-hand density stress candidates win all 24 full-label trials at sigma=2
coordinate noise. Center scores also cannot distinguish body size, tilt or depth
reflection. Internal boundaries distinguish these particular alternatives under
perfect segmentation, including tested 75%-missing instance subsets; silhouette
alone leaves reflection exactly ambiguous. Pitch/count/twist-equivalent geometry
has pixel-identical ID masks. No geometry accepted for the real photo.

First run: `output/synthetic-benchmark/`. After adding recorded trial IDs/protocol,
source-test hash and runtime image-invariant/visibility assertions, second full
run: `output/synthetic-benchmark-verified/`. All candidate scores and every prior
trial score reproduce exactly. All 86 common decoded image arrays match, as do
24 include files byte for byte. An initial raw-hash assertion failed: POV-Ray's
84 PNGs contain changing render timestamps in tIME/tEXt chunks. Pixel comparison
and metadata inspection resolved this; actual per-run file hashes are retained.
All final report source/artifact hashes match their files. Final report SHA-256:
`398b9424a9b8acb4efb33b8eb4c22745ed2b9b4caaadf545471a685d88043a66`.

Inspected negative-hand beauty and both-hand ID/boundary comparison panels.
Thirteen tests pass, including a real POV-Ray front/rear occlusion integration
test; py_compile passes. Final diff/whitespace checks precede publication. No
legacy scene changes, so no repeat legacy pixel test. No photo refit, material
optimization, curved/perspective test, segmentation from beauty images or repeat
inference. Outlines stay exact when centers are noisy; no robustness claim follows.
No sub-agent work, model change, remote messaging or computer transfer.

Next: shaded synthetic boundary extraction with controlled blur/noise and local
alignment fitting; validate errors/ambiguities against hidden mask truth before
photo refit. Step 2 remains open. Generated outputs and .venv stay ignored.

## 2026-09-23 — R016 construction clarification, no experiment

User supplies pre-stringing/slipknot/one-bead-per-chain-stitch construction, small
end-matching twist, permission to assume bead shape/orientation from `beads.pov`,
and permission to invent test patterns. Inspected legacy source and shared macro:
hole axis tangent to center circle, hole ratio 0.14, nominal count 6.5 with rounded
turn count for closure, case-specific bead proportions. R015's tilt/hole ratio
and current photo height differ; no source/settings changed in this step.
Updated plan/handoff and contextualized historical ambiguity claims. Next is a
known-pattern rendered recovery test with source geometry, actual visibility and
fixed known layout, before photo refitting. Ask user when construction matters.
Documentation review/whitespace checks only; runtime tests/renders unnecessary.

## 2026-09-23 — R017 direct legacy practice

User requested original beads.pov practice, then explicitly requested a plan
commit before continuing. Committed revised plan/log/handoff as 0fbd48f.
Added optional legacy color/group override, authored 40-color pattern and a
runner that includes the actual legacy scene. Two 2400x1800 case-1 views contain
800 beads and 123 turns; each repeat advances 54 degrees around the rope.
Both full images and corrected right-side crops inspected; no inferred indices
or photo recovery claims. See PRACTICE.md for source lessons, hashes and commands.
Default 640x480 before/after pixels match. All 13 tests, compilation and final
report hash verification pass. Initial crop was mostly blank center; corrected
and rerendered. Existing missing gamma/version placement warnings remain.
Next: trace known indices and measure visibility across these same repeats,
stopping at an illustrated check before automatic recovery/photo refitting.

## 2026-09-23 — R018 user advice and questions workflow

User notes that multiples-of-13 patterns may conceal a different hidden-side
pattern. At exact 6.5 beads/turn, 13 spans two turns; add such a case to the next
visibility check instead of relying solely on favorable 40-bead phase advance.
Closure/camera coverage still need measurement. User requests advice questions
at every round end; recorded in AGENTS and handoff. Documentation only; no new
render or test experiment. Retain Astra/High and this conversation for next work.

## 2026-09-23 — R019 maker's answers saved for next round

User designed and made photo 2's necklace; has not designed a multiple-of-13
pattern, though may in future. Every stitch is identical, with no need to manage
rounds; half-step advance comes from attachment to the previous row. Recorded as
maker knowledge in plan/handoff/log. The multiple-of-13 case remains a synthetic
visibility check, not the expected photo-2 pattern. No new experiment or code
change; documentation review/whitespace checks only. Next bounded task unchanged.

## 2026-09-23 — R020 questions at the beginning of each round

User replaces R018's end-of-round questions with beginning-of-round questions,
because answering after /new requires remembering lost conversation context.
Updated standing instructions, plan and handoff; preserve answers and pending
questions across sessions. Asked about positioning photo 2 and bead changes at
the join; answers pending. Recorded supplied old-session timing/usage separately
from new-session status in REQUEST_LOG. No experiment/code change; next task is
still the illustrated legacy visibility check. Documentation checks only.

## 2026-09-23 — R021 natural placement and integer pattern repeats

Photo 2 settled naturally; no deliberate rotation to display colors was needed.
User always uses whole pattern repeats, totaling usually 700–800 bracelet beads
or 3,000–5,000 necklace beads. Record N = kL for later inference and revisit the
provisional 2,698-bead photo count. No exact photo-2 count is supplied, and natural
placement does not imply zero local twist. User expects enough information and
an established algorithm; plan a primary-source method review before custom
recovery development. Saved opening answers; no repeated questions, new experiment,
literature search or settings change. Next illustrated visibility task unchanged.

## 2026-09-23 — R022 retain the working bead estimate

User clarifies that the provisional estimate is good enough. Keep 2,698 beads
for current work; remove R021's proposed revision based on usual necklace counts.
The estimate is not an exact measurement or a divisibility filter on repeat
length. Whole-repeat construction and next visibility task remain unchanged.
Documentation correction only; no scene/settings changes or runtime checks.

## 2026-09-23 — R023 illustrated legacy bead/repeat visibility

Started on daisy at clean 271fdca, fetch/upstream 0/0. Continued after the saved
opening answers; no repeated questions. Added a generated instrumentation copy
of the unchanged beads.pov, POV-Ray ID materials, authored 13-color counterexample,
Python visibility/figure runner and four focused tests. Case-1 shapes and camera
come from the original scene, not R015's unrestricted geometry.

Forty colors/20 groups: 800 beads, 123 turns, 54-degree repeat advance. Each phase
shows all slots with >=100 pixels in at least ten occurrences. Thirteen colors/
60 groups: 780 beads, 120 turns, zero repeat advance. Every slot has some pixels
in the full oblique view, but phase-half slot 0 has only four >=12-pixel occurrences
and none >=100. Its strongest occurrence (#533) exposes 69/4094 isolated pixels
(1.6854%). Quarter-ring sections miss several slots. This tests local/weak support;
it does not establish a wholly hidden full-ring slot in these particular views.

Final run: output/legacy-visibility-verified, 26 renders, 74 hashed artifacts;
report SHA-256 12ac2b92948e920b89e7da5a49ae1ecfdfcfb44c102d4c07e53606344489c7c0.
All source/artifact hashes match. Four full ID/palette silhouettes and color maps
agree exactly; sixteen isolated masks satisfy containment, including complete
occlusion. Clear image borders checked. First/final runs match all prior numeric
visibility results, four layout CSVs and 22 common render pixel arrays. Figure
labels initially overlapped in the weak-slot trace; final margin labels fix it.
Four full trace views, coverage chart and weak-slot close-up inspected. Seventeen
tests, compilation and whitespace checks pass. R017 practice hashes verified;
no legacy source/settings changed, so no repeated before/after beauty regression.
No noise/resolution sweep, segmentation, algorithm literature search, inverse
recovery or photo refit. Generated files/environments remain ignored.

See VISIBILITY.md. Next: primary-source review and choice of an established
registration/periodic-sequence approach with a concrete synthetic validation plan;
stop before implementation/photo refit. Retain Astra/High; fresh /new recommended
for that distinct task, with opening questions based on saved construction answers.

## 2026-09-23 — R024 new-session status and opening questions

Read saved construction answers and R023 visibility evidence. Asked about intended
photo-2 colors/similar shades and occasional stringing errors; answers pending in
the handoff. Recorded prior-session timing/usage separately from current supplied
status. No literature review, experiment, code or scene changes. Next task remains
the primary-source method choice and concrete synthetic test plan. Stay here with
the retained Astra/High recommendation; no further /new needed for this round.

## 2026-09-23 — R025 palette, checked repeats and unknown colors

Saved the maker's answers: photo 2 uses red, yellow and black; each pattern
sequence is carefully checked against the preceding one, so assume no construction
mistakes. Beads with too little visibility to decide color are "color unknown",
excluded from color evidence while preserving sequence positions/index uncertainty.
No numerical readability threshold supplied. Observation errors remain possible;
later inferred colors must stay distinct from observed unknowns. Opening questions
are answered. Documentation only; no method review, implementation or photo refit.
Next method-selection task and stopping point unchanged; stay here with Astra/High.

## 2026-09-23 — R026 review draft; R027 direct indexing advice pending

Reviewed primary papers on CPD, strong periods of partial words, DTW and event-log
MDL, plus official rectangular-assignment documentation. Drafted METHODS.md with
a sequence-only synthetic validation and a conditional registration test. Verified
all seven R023 source and 74 artifact hashes; no new experiment or runtime tests.
During the review, the maker offered a direct method for assigning every visible
bead an index. Asked for their walkthrough and deferred the registration choice;
CPD remains only a fallback. Known indices and unknown colors are independent.
The full method-selection step remains unfinished until this advice is incorporated.

## 2026-09-23 — R028 neighbor rule resolves method choice

Maker specifies neighbors along ±1, ±6, ±7 index directions. Replaced the proposed
registration route with graph index propagation and cycle checks, followed by
partial-word strong periods for colors. METHODS.md contains primary sources and
a concrete synthetic graph audit as the next task; unknown colors keep their bead
positions. Automatic identification/signing of image edges is unvalidated. Full-ring
winding, disconnected offsets and wrong bridge edges are explicit test cases.
The literature/design step is complete; no recovery implementation or experiment.
Documentation review/whitespace and local-link checks; runtime tests skipped.

## 2026-09-23 — R029 opening answers; R030/R031 helicity and neighbor audit

Saved current/prior session status separately and asked about identifying neighbor
directions and hidden beads. Maker answered: ±1 follows the small radius, ±6/±7
are diagonals affected by helicity; hidden beads lie at visible-patch edges.
Added the requested legacy helicity switch and implemented the scheduled supplied-
edge audit. Both hands of four fixtures pass 240 graph trials with exact relative
indices and retained component origins; all 24 full-ring threshold graphs connect.
Wrong-bridge and reversal controls show why consistency cannot establish image
edges or hand. See NEIGHBORS.md for evidence, images and commands.

Eight default cases retain pixel equality; four +1 fixtures retain full-resolution
ID/beauty/layout equality. Both hands match ID/palette pixels and analytic source
placement. Twenty-five tests pass. Initial checks corrected Python's interpretation
of the legacy sine expression and camera projection (horizontal orientation and
default 1.33 right-vector length); isolated markers now agree within 0.15 pixel.
All ten final panels inspected. Legacy geometry remains unchanged except for the
optional opposite winding. No automatic edge extraction, photo indexing, period
recovery or photo refit.

Next: METHODS.md §B known-index partial-word sequence validation, stopping before
automatic image-edge integration/photo refit. Retain Astra/High; fresh /new advised.
No unanswered construction questions remain for this round.

## 2026-09-23 — R032/R033 Helicity rename and pattern conventions

Renamed the scene option from LegacyHelicity to Helicity, including the audit
runner, tests and current documentation examples. Source/test byte comparisons
against entry commit 08ba3bb confirm only that substitution in the three affected
code files. All 25 existing tests pass, including both-hand real renders and
invalid-value rejection; whitespace checks pass. No new tests or full 49-render
audit were needed. Historical outputs and hashes remain unchanged and refer to
their original sources; rerun the audit in a fresh directory for current hashes.

Maker defines pattern length as the shortest repeating block, considers redundant
copies a mistake, and accepts arbitrary first bead, stringing direction and
helicity. Updated METHODS/PLAN/handoff to carry those conventions forward while
retaining unknown colors and different possible completions. R032's questions are
answered; no new questions at round end. No new usage supplied under R033.

Next: METHODS.md §B sequence-only synthetic validation; stop after report/tests
before image-edge integration or photo refit. Use gpt-6-astra / High and stay in
this conversation. This step publishes the rename and the R032/R033 records.

## 2026-09-23 — R034–R036 advice and known-index sequence validation

Saved separately attributed session status and the maker's answers: photo-2
repeat <400, custom graph-paper design of continuous three-color spirals, and a
simpler 30-bead staircase example. Keep the 2,698 total provisional. Implemented
strong-period testing with original indexed unknowns, conflict witnesses, support
provenance, exact-synthetic-count closure flags and rotation/reversal conventions.

All 72 synthetic cases and 288 holdouts satisfy the expected checks; all 32 tests
pass. Known periods survive all 63 uncorrupted cases; supported true-slot colors
match truth. At the known period holdouts give 24,383 correct, zero wrong and
52 abstained predictions. Weak 13-slot phase-half/T100 leaves slot 0 unknown and
three distinct completions. Longer compatible candidates can survive wrong-color
injection. No evidence is silently filled, and no unique photo recovery is claimed.

Final/reproduced runs have 77 byte-identical artifacts; six current source hashes,
seven historical source hashes and 74 historical artifacts verified. Compilation,
whitespace and visual inspection of both chart panels pass. No failed runtime
checks. One documentation patch had an unmatched context and made no changes;
corrected its context and reapplied it. Adjusted provenance handling to allow
regenerated historical report hashes while checking source/artifact manifests.
Historical fallback render commands were inspected but not rerun. Generated
outputs and .venv remain ignored.

See SEQUENCES.md. Next: synthetic neighbor inference from anonymous visible-mask
centroids, tested against hidden indices; stop after illustrated edge/index
accuracy and checks, before segmentation/photo refit. Use gpt-6-astra / High;
recommend fresh /new for that separate task. No questions pending for this round.

## 2026-09-23 — R037–R039 advice and image-neighbor baseline

Saved separately attributed supplied session status and maker advice: almost no
tilting/sliding, rectangular top-bead faces, close direction-1 spacing and
half-offset brick-like diagonals. Re-read the actual shared bead geometry.

Implemented anonymous centroid proposals and a visible-mask orientation variant;
both preserve label conventions, ties, missing indices and failed reciprocal
proposals. No source indices, colors, true axes, helicity, camera or N enters
inference. The oracle masks do not validate photo segmentation. INFERENCE.md
records parameters, exact scope, results, controls and reproduction commands.

At T12 across eight views once each, shape improves pair precision 90.85%→95.45%
and reduces recall 61.30%→55.61%. Best evaluator-selected signed precision is still
only 82.24%; all 192 convention graphs contain contradictions. Consistent small
components also contain wrong indices. Ideal brick-ring inference is exact;
missing detections create four false bridges, and superposed rings create 96
shape cross-sheet false links. The crossing is a 2-D stress, not a new render.

All 39 tests pass, including seven new checks. Compilation, whitespace, seven
current/eleven input source hashes and 148 input artifact hashes pass. All 48
paired shuffles agree. Two full runs reproduce all 208 artifacts byte for byte.
Ten crop panels inspected in contact sheets, original-hand bend also full size,
and summary/crossing figures full size. One development patch failed on context
without edits; corrected/reapplied. No failed runtime tests/assertions. Exact
diagonal ties found in review now abstain symmetrically; no threshold search.
Staged whitespace later caught an extra fixture EOF blank line. Removed it and
regenerated both audits for final source hashes; all 208 artifacts remain identical
to the inspected run. Final evidence is inference-audit-verified, documented in
INFERENCE.md. No logic change or repeat runtime suite needed for whitespace.

Initial fetch failed on sandbox read-only .git/FETCH_HEAD; escalation succeeded,
ahead/behind 0/0. No scene, material, photo, segmentation or sequence changes.
No new visibility render/full legacy regression needed; existing small renderer
checks ran with the suite. Generated final/reproduced/development outputs and
.venv remain ignored. Publish eleven scoped files including R037/R038 records.

Next: joint local triangle/lattice edge and label inference with 1+6=7 and mask
orientation, preserving alternatives and abstentions. Retain this baseline and
failure controls; stop after synthetic edge/component-index report/checks before
photo segmentation, sequence integration or fitting. gpt-6-astra / High, fresh
/new recommended. No pending or end-of-round questions.

## 2026-09-23 — R040–R042 questions, advice and one illustrated failure

Saved separately attributed session status and answered advice questions.
The maker sees neighbor ambiguity only at edges and recommends tracing all
three directions. The spiral forms a rough rectangle, probably using ±6/±7;
this later correction supersedes the initial ±1/±7 recollection.

Created show_neighbor_failure.py and NEIGHBOR_FAILURE.md: whole synthetic render
with a rectangle and detail of the false 611 → 613 edge (predicted +7, actual +2).
Visible intermediate 612 is marked; no human/photo ambiguity is claimed.
SVG embeds original image bytes unchanged; system librsvg/Cairo creates its PNG.
Saved input manifests, exact false edge, intermediate visibility, source/artifact
hashes and embedded image equality pass. Both diagram artifacts reproduce byte
for byte; compilation and whitespace pass; figure visually inspected. Exploratory
import initially lacked photo2 on sys.path, corrected without source changes.
No inference suite, new scene render, segmentation or photo fit needed/run.

Fetch succeeded on daisy, branch photo-2-reconstruction, ahead/behind 0/0.
Publish six scoped source/docs files including R040 local records; generated
diagrams/reports and .venv remain ignored. Next: review this case then trace all
three families jointly with lattice checks, stopping at synthetic edge/index
evidence. Stay in this conversation, gpt-6-astra / High; no /new needed now.

## 2026-09-23 — R043 joint triangle/trace inference

Continued the answered round on daisy, clean photo-2-reconstruction at e17dd60.
Sandboxed fetch failed on read-only FETCH_HEAD; escalation succeeded, 0/0
ahead/behind. No pull, transfer, delegation or new supplied status.

Implemented joint_neighbors.py, joint_audit.py and eight tests, with fixed local
triangle and three-family continuation support, retained competing candidates,
reciprocal selection, repeated support pruning and maximal surviving traces.
Source truth enters evaluation only. See JOINT_INFERENCE.md for all parameters
and the oracle-mask/global-ellipse/projection limitations.

T12 shape gives 1,850/1,910 correct pairs (96.86%) and 16.73% recall, compared
with baseline 95.45%/55.61%. Best evaluator-only signed precision is 94.40%.
Forty of 192 convention graphs remain inconsistent. Even optimistic convention
selection leaves 66/846 nonseed indices wrong in consistent components. The
ideal lattice remains exact; missing control keeps 480/504 true pairs, crossing
shape keeps 594/1,040, both without false pairs. The example's false shortcut
and its true replacement path are both rejected. No human ambiguity asserted.

All 47 tests pass; compilation and whitespace pass. Verified ten current source
hashes, seven baseline sources/208 artifacts, eleven current/historical render
sources/148 artifacts and matched input-report hashes. All 48 paired shuffles
agree; two final audits reproduce 114 artifacts byte for byte, reports agree
except command. Ten crops inspected in contact sheets and selected detailed/
whole/summary/crossing figures full size. One added crossing metric initially
failed JSON serialization as NumPy int64; converted to int, both full audits
rerun successfully. No failed unit test or threshold optimization.

Final output: joint-audit-verified-2, report hash recorded in JOINT_INFERENCE.md.
Generated final/reproduced/development/failed outputs stay ignored. No new
visibility render/full legacy regression, scene/material change, segmentation,
sequence integration or photo fit; existing renderer tests ran in the suite.
Publish ten scoped source/docs files and verify remote/status.

Next: causal synthetic comparison of mask centroids and projected true centers,
auditing true-neighbor turn/spacing/support violations and marking losses in
whole-image context. Stop at diagnosis before algorithm changes or photo fitting.
Use gpt-6-astra / High with fresh /new. No end-of-round questions.

## 2026-09-23 — R045 visible-boundary detection program

The maker answered R044: neighbors are recognized from visible edges, without
centers; same-color neighbors remain distinguishable. The new request replaces
the pending centroid diagnostic with two tasks: visible bead position/color,
then exact relative indices, using progressively harder tests and multiple
methods including local forward-model prediction with smooth corrections.
No pending questions. Read DETECTION_PROGRAM.md for the complete ladder.

Found the 303-point photo centerline and verified its source/photo hashes and
rounding-only difference from fft-image-explorer's saved spline. Found the HSV
two-click sampler in hsv_tools; it unions tolerance boxes with circular hue,
not a convex hull. Sibling checkouts remained untouched.

New detect_beads.py accepts only beauty pixels, method and known palette.
Compared color components, color-distance watershed, gray-boundary watershed
and color-seeded boundary watershed on 16 views /64 trials. Eight are saved
legacy RGB views; six are matched pigment-only R/Y/black, gray and black
rerenders; two are fixed mild blur/noise variants. Separate evaluation retains
IoU matches, all missed/hidden indices, splits/merges and per-color scores.
Every detection's bead_index remains null. No inference truth input.

At >=100 visible pixels /IoU >0.5, gray-boundary finds 883/1,008 all-gray beads
(87.60% recall, 70.92% precision), versus zero whole-bead matches from color
components. The same method finds 616/1,008 in R/Y/black, but 721 predictions
remain unmatched. All-black fails: 29/1,008 matches. Its phase-0 foreground
union nevertheless has 95.22% IoU, illustrating coverage versus separation.
Pure legacy Black is an extreme control, not fitted photo appearance.

Both unmodified RGB control renders reproduce saved beauty pixels. All 54
tests pass; seven focused tests pass again after adding foreground-union
assertions. Compilation, dependency/whitespace checks pass; verified 11 new
source hashes, 163 artifacts, 24 fixture artifacts, and the runner verifies
11 current/historical baseline sources/148 artifacts. Final report path/hash
in DETECTION_PROGRAM.md. Both final runs reproduce all 163 artifacts byte for
byte; reports agree except the command output path. Selected details, six-panel
contact sheet and whole R/Y/black/black context figures visually reviewed.
Initial sandbox pip DNS failure corrected by approved download into local .venv;
no failed runtime test/audit. Only reporting additions after first scores,
no detector/threshold tuning. No photo segmentation or index-recovery claim.

Preflight daisy, photo-2-reconstruction at 74d4f573; R044's two local record
edits included. Fetch succeeded, 0/0 ahead/behind, no stashes/pull/transfer or
delegation. Publish scoped source/docs and verify delivery; generated outputs
and .venv remain ignored. Next: local model-guided visible-boundary/index patch
test, fixed versus smooth correction, including wrong-phase and black-run
controls; stop before whole-ring propagation/photo work. Recommend
gpt-6-astra / High, fresh /new. No new questions at round end.

## 2026-09-23 — R047 calibrated local contour/index comparison

Saved the maker's black-bead cues (specular reflections, otherwise periodic
saturation/value variation), three/four-bead anchor advice and explicit need
to retain both helicities. No pending questions. See LOCAL_PATCH.md.

Implemented eight independently rendered hand/phase templates, fixed/translation/
smooth alignment, image contour support and conditional seed-relative indices.
Four supplied image clicks and known legacy camera/rope/scale are explicit
assistance; observed ID truth enters only after predictions. Four paired source
views × three warps plus two evidence ablations give 14 local trials.

Two smooth target conditions yield accepted hypotheses: R/Y/black 34/38 correct
region/color/indices plus one false region; gray 38/38 with none false. Actual
no-model segmentation matches 26/38 and 31/38. The anchor margin rejects all
unwarped cases despite correct three-family topology; small warps change that
gate. Opposite-hand contour near-ties can have mostly incorrect indices. All-
black smooth candidates fail. No robust automatic indexer or photo claim.

All 61 tests pass; compilation/dependency/whitespace checks pass. Source/input/
artifact hashes verified. Initial comparison incorrectly warped prior masks
for the no-model baseline, corrected before final runs. Fits, thresholds and
clicks remain unchanged after scoring. Three optimizations hit the fixed budget;
recorded and none retained. Final reproduction/publication recorded in request
log. Generated outputs/environments ignored; no tracked POV source change.

Next: observed-region anchors with prescribed click jitter and a new frozen
patch, both helicities retained. Stop at local seed/region/index evidence before
whole-ring growth/photo fitting. Recommend gpt-6-astra / High, fresh /new.

## 2026-09-23 — R052 observed-region anchors: useful gains, unresolved failures

Saved R048–R051 status/advice: assistant marks its seeds; equal size/shape, small
gloss differences; lengthwise hole axes, invisible holes and invisible white
thread. Implemented region_anchors.py, region_anchor_audit.py and eight tests;
see REGION_ANCHORS.md for frozen protocol, scores and reproduction.

Sixteen conditions/two patches, three/four anchors, 17 nominal/jitter variants
and three controls each. Reused 96 verified smooth fits and computed 32 on the
new patch. Original R/Y/black identity/translation recover 34/37 and 32/34 correct
region/color/indices for all 17 four-anchor variants, versus old 6/17 and 8/17
acceptance. Four-anchor total acceptance rises 59→100/272, with wrong-index
alternatives in 36 accepted trials versus 19 previously. Keep both helicities.
Nominal warped R/Y/black alternatives identify all four anchor bodies correctly
yet assign different signed 1/6/7 increments and mostly wrong patch indices.

Second gray patch: 35/35 correct output indices, but second anchor selects
source 761 instead of 767. Second R/Y/black region matching and all-black fail.
Gray highlights can remain unassigned by foreground segmentation. Background
and duplicate controls reject throughout; true-phase exclusion often fails to
reject. No automatic seed/helicity/geometry or photo-recovery claim.

All 69 tests, compilation/dependency/whitespace pass. Two final runs reproduce
all 80 artifacts byte for byte; ten sources/five bound reports and prior inputs
verify. Reporting-only anchor diagnostics/panel corrections leave original scores
unchanged. No threshold/click tuning or failed runtime test/audit. Small renderer
tests ran; no new candidate renders or full legacy regression. Generated output
and environments remain ignored. Publication and final status recorded in log.

Next: fixed highlight-tolerant observed-region extraction comparison on these
two patches, retaining black/shadow/missing-region/jitter controls and both hands.
Stop after local region/anchor/index evidence before ring growth/photo fitting.
Recommend gpt-6-astra / High with fresh /new; no end-of-round questions.

## 2026-09-23 — R055 conservative highlight repair

R053 status is saved with prior-session usage distinguished. R054 maker answers:
smoothly rounded surfaces; usually one bright reflection, depending on lighting.
No exactly-one-highlight constraint. R055 authorizes the bounded comparison.
See HIGHLIGHT_REGIONS.md, highlight_regions.py and highlight_region_audit.py.

One fixed image-only rule fills enclosed bright, low-saturation cavities touching
exactly one existing region. All old labels stay fixed; shared/open/dark gaps
remain unassigned. Reuse 128 R052 fits and both hands across the same 16 conditions;
no new fits/renders. Seventy cavities add 4,672 correctly owned pixels, no
background or wrong-owner pixels. Region matches, false regions, missing indices,
color summaries and split/merge counts stay unchanged in every condition.

Three-anchor acceptance improves 123→134/272, four-anchor 100→115/272, with no
acceptance losses and no increase in wrong-index trials (36 in each group size).
Original gray gains 14 four-click acceptances, all correct seeds; second gray
gains one with the known 761-for-767 seed slip despite correct output indices.
Original gray nominal first clicks still lie in cavities shared by two regions.
Existing wrong hands, second R/Y/black failure and black failure remain.

Background/duplicate controls reject throughout; phase exclusion retains 10/32
alternatives with either method. Thirteen applicable region-deletion controls
restore no removed pixels; three already-empty gray seed cases are inapplicable.
Nine focused controls/tests plus full suite: all 78 pass. Compilation, dependency
and whitespace checks pass. Two final runs reproduce 80 artifacts byte for byte,
reports equal except output path; 13 sources and all bound inputs verify.
After initial scoring, ownership reporting and deletion-control serialization
order changed; all original numerical/gate/control results remain identical.
No rule/click/fit tuning. Small renderer tests ran; full legacy regression skipped
for unchanged POV sources. Generated outputs and environments remain ignored.

Next: compare fixed distance/gradient assignment of shared bright cavities with
current abstention, preserving existing region labels, both hands and controls.
Stop after added-pixel ownership/region/anchor/index evidence and checks before
ring growth/photo fitting. Recommend gpt-6-astra / High with fresh /new.


## 2026-09-23 — R057 shared highlights: more acceptance, incorrect ownership

R056 current/prior-session status saved separately. R057 authorizes continuation
without more answers: iPhone capture, flash unknown; color reflections unspecified.
No lighting parameter or scene change inferred. See SHARED_HIGHLIGHTS.md for
protocol, results, controls and reproduction.

R057 compares fixed distance and RGB-gradient paths in shared bright cavities;
see SHARED_HIGHLIGHTS.md. Both raise four-anchor acceptance 115→140/272,
but add respectively 137/151 wrong-owner pixels and 216/301 unresolved-owner
pixels. Wrong-index trials remain 36; excluded-phase acceptance worsens 10→12/32.
Supported region/color/missing-index summaries and split/merge counts do not
improve. Keep R055 conservative abstention as the baseline, not either extension.
Unknown photo flash use remains unspecified; no lighting/model parameter changed.

Distance adds 1,465 shared pixels: 1,112 correct, 137 wrong, 216 unresolved;
gradient adds 1,679: 1,227 correct, 151 wrong, 301 unresolved. No added background.
R055's 4,672 correct single-owner pixels and all existing labels stay fixed.
Forty-five shared cavities, 222/8 ties. Three-anchor acceptance 134→155/272;
four 115→140/272; no losses, 36 wrong-index trials per group size unchanged.
Twenty original-gray four-anchor gains have correct seeds; two of five second-
gray gains have correct seeds, three retain the known seed slip. Four gray
conditions accept all 17 variants; second R/Y/black and black still fail.

Background/duplicate controls reject throughout. Excluded phase retains 12/32
instead of 10/32. All 13 applicable deletion controls leave seeds unassigned
and restore no deleted pixels; three original-gray ablations are inapplicable.
Reused 128 fits, both hands, 16 conditions, 544 positive and 96 control trials;
no fitting/rendering. All old/conservative masks, gates, scores and ownership
reproduce; all 86 tests pass. Compilation/dependency/whitespace checks pass;
pip cache warning only. Two final runs reproduce 80 artifacts byte for byte;
16 sources and previous/bound manifests verify. Initial/final numerical results
and prediction/evaluation/mask bytes identical after reporting-only additions.
Visual review: 16 initial contact-sheet panels and four final full-size panels.
No failed runtime test/audit, scene/material/photo change or automatic recovery
claim. Small renderer tests ran; full legacy regression skipped for unchanged
POV sources. Generated outputs/.venv remain ignored.

Next: Test a second spatially separated observed-region group within each frozen
crop against surviving wrong-helicity/phase candidates. Select from beauty and
observed regions before evaluator truth, keep fixed fits and R055 conservative
repair, and measure both lost correct and rejected wrong alternatives. Retain
jitter and background/duplicate/excluded-phase controls. Stop after local
hypothesis/seed/index evidence and checks, before ring growth or photo fitting.
Recommend gpt-6-astra / High with a fresh `/new` for this distinct step.

## 2026-09-23 — R059 blind generated-image test; visible inventory remains first

User explicitly redirects work to beads1.jpg–beads7.jpg before photographs and
requires visible-bead identification before choosing how to infer remaining beads.
No more pattern knowledge is needed. Supersedes the second-anchor experiment.

The JPEG-only pipeline produces candidate maps for all seven images, an interactive
observation gallery, sensitivity counts and both-convention index attempts. It
reads no POV-Ray pattern definitions, saved patterns, source layouts or ID truth.
Candidate counts are 352/392/435/410/403/354/417; these are not verified bead counts.
All four indexing variants per image have contradictory/duplicate indices; **zero
full patterns recovered**. Small consistent groups in beads3 retain only local,
conditional period families. No photographic or complete visible-inventory claim.
See **BLIND_GENERATED.md** for methods, table, commands, hashes and failures.

The gradient-only watershed failed around highlights; the final compact
value/gradient method improves the map but still cuts through side beads and
omits/slivers or fragments dark/bright evidence. Explored local/global glint
geometry did not establish valid indices. All seven originals and final-method
boundary maps inspected. Five new controls and fourteen relevant existing tests
pass; a seam-sensitive test fixture was corrected before the final pass.
Compilation, source/input/artifact hashes and byte reproducibility of 29+7
artifacts pass. No old renderer regression for unchanged sources; no new render.

Correct/review beads1.jpg's visible inventory next, retaining full-image context
and unknown slivers. Stop after its instance/color map and checks, then extend to
the remaining six images before further indexing or photographs. User's complete
seven-pattern objective is still unfinished. gpt-6-astra / High, stay here.

## 2026-09-24 — R060 plan/methods explanation and geometry inventory

Wrote ../METHODS_AND_PLAN.md at the user's request. Generated JPEGs currently
have approximate masks and incomplete bead candidates, but no saved three-spline
set in the active pipeline. Photo 2 has outer/inner/centerline curves (907/847/303
samples) in the existing sibling spline file; only the centerline is copied here.
Verified source/photo hashes, closure/finite coordinates, rounding correspondence,
and R059 source/input/artifact hashes. Read actual threshold, watershed and spline
methods; preserved historical predicate uncertainty and unmeasured boundary accuracy.

No new experiment or algorithm: documentation links/whitespace checked, runtime
and renderer tests skipped. Generated-image visible-bead correction remains first;
next bounded step is beads1.jpg's reviewed instance/color map before repeat inference.

## 2026-09-24 — R061 requested centerline visualization

Created a reproducible photo-2 overlay with the saved 303-point centerline in cyan,
without refitting. Full-resolution and preview PNGs plus source/artifact hashes
are under output/centerline-view-r061/. Run show_centerline.py to reproduce.
Visually inspected original/preview; input dimensions/hash and coordinate checks,
compilation, byte reproducibility and unchanged pixels outside the stroke pass.
No detection, rendering or pattern work. Generated-image priority remains unchanged.

## 2026-09-24 — R062–R065 width correction and illustrated review

Completed width/shadow diagnostic and provisional corrected curves. The source
boundary JSON is now tracked byte-identically with its original provenance hash.
600 normal cross sections yield96 both-clear references,500 one-clear and4 neither.
Robust width95.8px; positive perspective slope not established. Left region excess
width16.7px, empirical uncertainty9.6–22.9px, center shift8.8px; lower loop15.5px/8.2px.
Fourteen regions flagged;207/600 strong positions,296 blended shifts, max14.7px.
Shadow extent is distinct (left124px, lower110px), with missing frame references
explicitly unavailable. Threshold sensitivity gives left shifts8.6–9.1px. Reference
holdout errors3.1–8.0px; one holdout unavailable after losing vertical coverage.
No true-edge accuracy or camera tilt established. Original geometry/defaults stay.

Added width_correction.py, nine focused tests, WIDTH_CORRECTION.md, three saved
questions and curated review bundle (four PNGs, SVG, HTML, hash manifest). Updated
overall methods, plan, README, handoff, progress and standing AGENTS workflow.
Future questions and useful supporting images must be committed files (R065).
No replies to the opening advice questions; consolidated them into the file.

Nine tests and compilation pass. Two final runs reproduce10 analysis artifacts
and6 curated review artifacts byte for byte; reports equal except commands, all5
source hashes and manifest/report binding verify. Report SHA256:
089e42c36d6d45c1104f3d4b0e7359df8bd3819ecf6cf8ce38727717692090c6.
Finite/closed curves, center-between-edges, unchanged clear anchors and abstention
checks pass. No strict interior crossings found in candidate curves or paired
boundaries. Original and all comparison/overview/preview PNGs visually inspected;
SVG checked as XML. Initial run failed on insufficient holdout coverage and NaN
references, now unavailable results. Initial exact-zero assertion failed at1.8e-15;
bounded gain and numerical tolerance fixed it. No patterns read, render or legacy
regression needed. Prepublication ls-remote hit sandbox DNS failure; escalation
confirmed remote still4cadaf6. Bulk outputs/environment stay ignored; curated
question illustrations are intentionally committed under the user's exception.
Next: reviewed edge/width references and geometry check before adoption, then
return to generated inventories. gpt-6-astra/High, stay here; no `/new` needed.

## 2026-09-24 — R066 direct transect check

Twelve assistant-reviewed image transects support the main width correction,
with residual over/undercorrection at C/E. See TRANSECT_REVIEW.md and committed
review/r066/. Within2px of visual ranges:18/24 original,23/24 corrected; this is
subjective compatibility, not true accuracy. Annotations frozen before reading
projected offsets. No new width fit, curve/default change or perspective claim.
Four new plus nine existing tests, compilation, artifact/source hashes and
repeatability pass. Questions gain lettered supporting images, no maker answers
yet. Next: direct image-edge evidence on both sides with width as a soft prior,
compare against frozen intervals and stop before geometry adoption.

## 2026-09-24 — R067 image-edge cue rejected

Completed the fixed-setting direct color/brightness-edge comparison; see
IMAGE_EDGES.md and committed review/r067/. Default image-guided candidate has
18/24 edges within2px of frozen visual intervals versus23/24 width-only; mean
outside1.26 versus.49px. Reject it, retaining provisional width-only geometry.
Sensitivity variants also regress; no-image metrics mixed, not adopted.
Initial linear interpolation hit iteration limits; C1 interpolation converges.
Five new+nine width+four transect tests pass (18); compilation, hashes, geometry
sanity and repeatability checks pass. Questions gain F/G/H supporting images.
Next: resume beads1.jpg visible inventory before further pattern inference.

## 2026-09-24 — R068 beads1 reviewed observation map

Added323 supported bodies and37 unresolved fragment records, preserving colors
and unknown indices. Removed21 unsupported/duplicate markers; added29 visible
fragments including11 coverage-audit slivers. Color-constrained provisional
regions retain41 unassigned pixels; coverage is not completeness. See
BEADS1_INVENTORY.md and committed review/r068. Two illustrated questions saved
in BEADS1_QUESTIONS.md; no maker replies yet. Ten tests, compilation, hashes,
repeatability, seed/ID/color/connectivity checks pass. Next extend review to
beads2.jpg, adapt palette support, stop at map/checks before any indexing.

## 2026-09-24 — R069 ignore slivers and compare local area

Applied maker reply: all 37 known fragments ignored; 211 remains excluded.
Local area below half eight nearby bodies' median excludes ten further regions,
all near an edge, leaving 313 active body observations. 38 normal-sized edge
observations remain. Historical masks/IDs preserved; no reassignment of excluded
pixels. Beads1 questions answered; lighting suspicion saved as a hypothesis.
See INVENTORY_SELECTION.md and review/r069 for method and illustrated results.
Twelve tests, compilation, source hashes, repeatability and label checks pass.
Next beads2 JPEG-only review with its own palette and the R069 selection policy.

## 2026-09-24 — R070 beads2 image-only active inventory

Reviewed beads2 with pale-lavender support and R069 policy: 318 active bodies
(111 orange, 124 lavender, 45 violet, 38 yellow). Removed 56 markers, added two
bodies, ignored seven known fragments and 13 small candidates. Corrected violet
324 but its area remains below cutoff; bottom 382 retained, duplicate 383 removed.
No new questions or pattern claim. BEADS2_INVENTORY.md and review/r070 contain
method, maps and correction examples. Eleven tests, compilation, source hashes,
repeatability and region/ID checks pass. Next beads3, distinguish neutral beads
from shadow, stop after active map/checks without indexing or POV pattern lookup.

## 2026-09-24 — R071/R072 beads3 neutral bodies and black-region illustrations

304 selected observations (120 white, 117 black, 67 red), with slivers ignored.
New neutral-color support, marker corrections and connected masks; 122/405 retain
large-area warnings. Requested raw/marked/outlined close-ups plus whole-image
locations committed with the review. BEADS3_INVENTORY.md records method, rejected
approaches and limits. Twelve tests, compilation, hashes, repeatability and label
checks pass. Handoff now starts with a progress table; AGENTS clarifies palette/
mask review before area filtering and image-specific IDs. No new questions.
Next beads4 active map/checks, retain beads3 warnings; recommend fresh `/new`.

## 2026-09-24 — R073/R074 local geometry first for black regions

Implemented maker's two diagnostics on 122/405; geometry is primary, HSV supports.
Median neighbor-step predictions and mask-derived ellipse proxies expose 3.16/
6.32px held-out marker errors; outlines extend into background. Interactive
long/short-axis shifts, static contours and HSV plots saved in review/r073.
405 has a faint second glint;122 is mostly quantized black. Neither split is
accepted, all inventories unchanged. BLACK_REGION_METHODS.md records methods,
threshold sensitivity and saved advice; no new questions required. Five controls,
compilation, eight source hashes and seven repeated artifact hashes pass.
Matplotlib initially absent, installed locally/pinned; crude partial-contour fit
rejected. Next calibrate clearer neighbor centers/outlines and validate withheld
predictions before missing-bead/index claims. Beads4 deferred; fresh /new advised.

## 2026-09-24 — R075 calibrate local mask geometry near beads3 warnings

Transferred same-color marker-to-mask offsets and covariance ellipse proxies
from nearby R071 bodies; warning rows and warning-bearing controls excluded.
Leave-one-out mask-centroid median/p90 errors are 2.38/4.52 px at 122 and
3.14/5.54 px at 405. Target warning-mask contour errors remain larger: 5.94/4.00
px symmetric mean with p90 12.22/8.15. This calibrates provisional mask transfer
only; both warnings and the 304-observation inventory remain unchanged. Added the
script and two curated figures. Compilation, repeat artifact hashes and
whitespace check pass; no tests run. Next beads4 JPEG-only body/color review,
R069 applied, retain 122/405 warnings; recommend fresh `/new`.
