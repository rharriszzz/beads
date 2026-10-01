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

## Current R186: saved graph restoration, zoom and pan

Found41 saved centers and their existing hand−1 score scan. Latestcenterrev2
and scorecenterrev1 have identical points; restore both without writes/rescan.
[Graph controls / actual saved plot](photo2/SCORE_GRAPH.md) add pointer-anchored
wheel zoom, Shift-score/Ctrl-count zoom, drag pan, larger dialog, full/visible-Y
fit, Best±30 and explicit view range. Hover exact sampled scores, PNG current
zoom, JSON all samples. Graph domain persists in browser for this saved scan.
Restore marker model reference2646/−1/guides if no saved choice; preserve CLI
precedence. Different-point old score flagged stale, not silently reused.

Readonly live restore and all three saved JSON byte hashes checked.14 Python/
10 JS checks pass; frozen actual centers/score and full/local score plot saved
with source hashes. No new geometry fit, score scan or browser/server/launcher
interaction test. Existing scan minimum3592 nearupperboundary is conditional,
with nearest-density/phase/centerline/visible-center proxy bias; not inferred N.

**Stopping point:** restored points/scores and zoomable graph. **Next task:**
inspect low-score counts/matches before choosing scan extension or geometry
refinement. gpt-6.1-sol / High, same session, no/new.

## Prior R184–R185: visible-part centers and sum-of-squares count profile

Maker confirms107% closer but still too small, centerline good but imperfect;
retain [qualitative feedback](photo2/width-feedback-r184.json), no invented
extra percentage or corrected spline. User requests10–20 hand-picked centers
all around and a graph of squared predicted/marked distances versus count.
[Center tools and metric](photo2/CENTER_MARKS.md) extend the viewer with stable
numbered source-pixel marks, independent save/edit/delete/undo/export, and
background SSE scans with progress/cancel. Default every integer2000–3600;
graph click selects a tested count and shows provisional distinct matches.

Nearest distinct outward predictions minimize SSE; phase/origin/camera/spline
fixed per hand. Snapshot all marks/settings/scores and best matches. These
visible-part centers are proxy targets, and correspondence may change with N.
No robust trimming or silent reuse/drop of marks; no automatic old-label import.
Width guides don't change score. Preserve aliases, centerline/width/visibility
bias and unknown closure. Minimum isn't recovered N or helicity.

13 Python/seven JS checks pass, including unchanged frozen variants, stable
center persistence/conflicts, optimal squared matching, both-hand synthetic
known-N recovery and background completion without server interaction. Curated
[synthetic graph](photo2/review/r184/synthetic-score-check.png) and full
[hash/parameter/score record](photo2/review/r184/validation.json) saved. No actual
maker center data or browser/server/launcher test yet. Restart viewer/refresh.

**Stopping point:** manual center capture and reproducible provisional graph.
**Next bounded task:** read maker's saved centers/score; inspect all-around
correspondences/residuals and choose the next geometry refinement. gpt-6.1-sol /
High, same session, no/new. Don't continue into a new fit without actual marks.

## Prior R183: centerline ± maximum radius and +7% width guide

User requests marked model edges and suggests photo diameter may be about7%
larger. [Width review / Q183.1](photo2/WIDTH_GUIDES.md) supplies raw alongside
white centerline, amber current-width and green107% guides; whole-photo view
also saved. Viewer adds80–130% guide control, toggles and saved/exported settings.
Only reference curves change: count, physical beads/circles and exposure remain
the same. Current guide radius is(4+R)*image scale, perpendicular to projected
centerline tangent. Smooth references are not detected/verified photo edges.

Seven Python and five viewport tests pass; old circle variants preserved,
guide closure/support, symmetric width scaling and old save compatibility
checked. No browser/server/launcher test. User restarts the server and reloads.
Q183.1 asks which width better brackets bead bodies, excluding cast shadow;
pending, not an approval gate.7% is a maker proposal, not a measured diameter.

**Stopping point:** interactive width guides and curated raw comparison.
**Next bounded task:** use width review/saved settings to separate width versus
centerline bias before count-drift refinement. gpt-6.1-sol / High, same session,
no /new needed; retain both helicities and unverified count/closure.

## Prior R180–R182: maker drift feedback and interactive count viewer

Maker reports center-to-boundary drift after130–156 bead steps at2698 and
65–91 at the increased count, similarly for both hands. “Minus3833” is
provisionally interpreted as supplied2833, exact wording preserved in
[drift review](photo2/drift-review-r180.json). Signed/component drift and
best count remain unknown; do not derive a numeric N from an assumed boundary.

User asks for an active Python count slider with zoom/pan. Three interfaces
considered: desktop, browser (selected), notebook. [Viewer/launch instructions](photo2/TANGENT_VIEWER.md)
implement full-source canvas with pointer-centered zoom, drag pan, count slider
2000–3600/editable endpoints, both saved helicity registrations, no viewport
reset on model changes, latest-response handling and save/reload/PNG/JSON.
Recompute full-model outward-point exposure for every count; no new fit.
Maker saves are separate from annotations. Four Python and four viewport
checks pass; original4 frozen variants reproduce. Browser/server/launcher
interaction not tested. Existing geometry/production detector unchanged.

**Stopping point:** working viewer program and preserved maker evidence.
**Next bounded task:** read maker-selected count and assess remaining drift
on an adjacent unfitted patch; retain both hands and unknown N/closure.
No required signed-drift answer before viewer use. gpt-6.1-sol / High;
same session, no /new needed.

## Prior R179: both helicities at original and +5% counts

User is still reviewing spacing and requests the same images for both
helicities at both counts. [Four-way review](photo2/HELICITY_COUNT_COMPARISON.md)
contains full-source overlays, matching raw/local crops, wider spacing
comparisons and parameter files for +1/−1 ×2698/2833. Each helicity reuses its
saved original fit to8/11/20; camera/spline/physical dimensions are common,
phase/origin stay fixed within each count pair. No new fit or inference.
Earlier −1 overlays are reproduced byte-for-byte; pending Q177.1 unchanged.

**Stopping point:** four matched image sets and independent forward-visibility
checks. **Next bounded task:** incorporate the maker review, then refine an
unfitted adjacent colored patch while preserving both hypotheses. No added
question while the user is working. gpt-6.1-sol / High, same session; no /new.

## Prior R175–R178: forward tangent circles and +5% count overlay

The user diverts from triangle refinement to a planar-spline forward model:
calculate minor-outward points and tangent planes, show cyan circles only where
the point is visible, register a few colored beads, and allow small adjustments.
Reuse the historical303-point spline diagnostically. Initial2698 is provisional;
R177 increases it to2833 due to observed spacing drift, without changing phase,
spline station, camera, hand or physical bead sizes. R178 requires the whole
source image; [current full overlay](photo2/review/r177/bracelet-overlay.png)
preserves2540×3182 pixels. [Experiment / Q177.1](photo2/TANGENT_CIRCLES.md).

Python uses literal beads.pov rounded-annular geometry and all-neighbor
occlusion; hidden-point beads never receive circles. Three colored positive
cores8/11/20 fit phase/station, neither black nor held group22–25. Both charts
fit, so helicity/N/camera elevation remain unresolved. All96 candidates saved.
Four geometric tests and independent POV first-owner checks pass; unfinished
rays remain excluded. Before/after images, portable parameters, provenance and
reproduction commands tracked; generated geometry/scenes stay ignored.

**Stopping point:** working adjustable prototype, initial colored registration,
requested count change and whole-image view. Q177.1 spacing review pending.
**Next bounded task:** use that review and an adjacent unfitted colored patch
to refine phase/station/count/spline, preserving chart alternatives and explicit
uncertainty. This supersedes the immediate R174 position-refinement task, whose
maker relation remains preserved. Recommend gpt-6.1-sol / High; same session,
no /new needed. User controls switching.

## Prior clarification — R174: visible14 lies approximately midway

Maker supplies `c14_visible ≈ (c11_visible+c16_visible)/2`, where each c is the
center of the visible part of that bead. [Saved relation](photo2/visible-center-relation-r174.json)
preserves the exact statement, three stable identities and source provenance.
This is a diagnostic geometric constraint on the correct11→14→16 d3 chain;
numeric tolerance and pixel center locations were not supplied.14 is black;
its reflection remains an ownership anchor with uncertain representative position.

**Stopping point:** record the midpoint relation; preserve all numerical outputs
and observations. **Next bounded task:** diagnose14's representative position
using this approximate relation with uncertain11/16 visible-center estimates,
then test neighbor/triangle alternatives. Keep this maker constraint separate
from image-derived automatic runtime inference and from the outward-anchor target.
Recommend gpt-6.1-sol / High, same conversation; no /new needed.

## Prior R173: bead14 ownership versus position

The maker confirms11→14→16 is correct and says the selected point on14 is not
close to the center of its visible part, because black beads are hard to see.
[Saved clarification](photo2/anchor-position-note-r173.json) retains the exact
statement and reflection-point provenance. The measured48.32° bend is between
selected anchors, not bead centers; its geometric cause is not fully quantified.
Keep confirmed body identity separate from uncertain representative position.
No replacement point/numeric error bound was supplied; do not move observations
or equate visible-area centers with physical centers/outward minor-circle anchors.

**Stopping point:** preserve this maker correction and qualify the diagnosis;
no numerical/code changes. **Next bounded task:** test triangle/neighbor proposals
with reflection-point positional uncertainty, retaining competing relations.
Recommend gpt-6.1-sol / High, same session; no /new needed.

## Prior R171: diagnose missing11→14 d3 adjacency

[Raw review and Q171.1](photo2/NEIGHBOR_ANGLES.md) isolate an angle-gate failure:
both11 and14 have confirmed interior ownership, but their119.12° connection
is rejected by the local d1/d2/d3 estimates81°/32.5°/161°. The program instead
proposes11→17 d3. This is not a detection failure or a gap filter rejection.

Compare four approaches; test shorter-pair histograms first. Seven controlled
variants share identical958 points. Inverse-squared weights restore11→14,
increase maker forward matches49→54/129, but lose supplied14→proposed16 d3.
Independent true render neighbors280→270,271→268,279→276 also decline.
Other target-recovering variants have the same tradeoff; adopt no runtime change.
Source detector, maker live save and prior proposal files remain unchanged.

The two consecutive supplied d3 connections measure119.12° and167.44° using
the proposed interior/reflection points, exceeding a shared22° angle gate.
Those are not physical center/outward-anchor measurements. R172 answers Q171.1:
“Yes, S is inside bead 16.” All three body identities in11→14→16 are established;
the discrepancy is not an ownership error at S. Numerical results stay frozen.
Curated raw/current/experimental and angular-support figures plus frozen metrics
are tracked. The probe reproduces exact R169 baseline graph/evaluator counts and
all three render baselines before any conclusion. No full indices,N or helicity.

**Stopping point:** one local neighbor diagnosis and rejected simple fix.
**Next bounded task:** test small triangle constraints with competing neighbors
and supported body identities, retaining noncollinear interior-point uncertainty.
Recommend gpt-6.1-sol / High; stay here, no /new. User controls model/session.

## Prior R169: recover suppressed black reflections

Standalone continue resumes central-body coverage. [Correction and Q169.1](photo2/REFLECTION_SUPPRESSION.md)
move bead-scale reflection suppression after appearance-context checks. A colored
highlight flank was erasing a strong reflection in maker-confirmed black core14.
Choose this mechanism after comparing weaker reflections, colored-region seams,
missing-neighbor searches and projected templates. Do not lower the learned
reflection threshold or change color priors/geometry to fix this error.

Preserve all908 baseline locations and add50 dark-surround reflection proposals:
958 points,1462 tentative links. Freeze revision422 (76points/41series/129links)
separately; original live labels and old snapshots stay untouched. Paired photo
comparison58→63 nearby associations,44→49 forward-agree links. R on14 is inside
the previously confirmed core; R170 confirmsP is inside maker10. The supplied
10→14→17 d2 chain is reproduced with established body identities.
No new confirmed identity follows from a proximity association alone.

Known-source fixtures locate130→132/168,130→133/168,132→133/169 eligible bodies;
0 points on paper, duplicate counts remain4/4/3. Neighbor precision declines
97.2→95.9%,97.8→97.1%,96.8→95.9%; preserve this tradeoff and tentative edges.
Graph45→37components,largest192→204,17isolates,62ambiguities,190possible gaps.
Blind/evaluator runs identical; all R168 confirmed stable IDs/positions retained.
Eleven tests pass, including an independent maker-confirmed black-core regression;
no sockets/browser/launcher test. No pose fitting, index/N/repeat or hand inference.

**Stopping point:** one suppression correction with paired checks and illustrated
ownership review. **Next bounded task:** diagnose missing/wrong local neighbor
links from established body identities, especially supplied11→14 d3 (still absent),
before treating any whole-ring path as consecutive steps. No physical necklace
or hidden-body prerequisites. Recommend gpt-6.1-sol / High; stay here, no /new.

## Prior R167: first automatic pass delivered; coverage review

User asks to automate all sufficiently visible bodies and directional neighbors
around the photograph, using only the photo. The [first implementation and checks](photo2/AUTO_LABELS.md)
produce908 proposals (642 chromatic/266 reflection-dark) and1330 tentative links.
The live maker file is untouched. Learn background/palette/scale/locations from
the image; no saved coordinates, fixed HSV boxes or magenta rule. Four methods
considered; select learned image strip plus interior/reflection evidence.

Fixed revision340 evaluation:50/66 nearby point associations,34/54 associated
maker links agree (96 supplied links total). Proximity does not prove identity.
Independent source-macro fixtures:130/168,130/168,132/169 eligible bodies located;
0 points on paper,3–4 duplicates,96.8–97.8% true unsigned neighbors. Two hands
and changed palette/background/displacement tested; completeness is unresolved.
Blind/evaluator runs identical; actual labeler load/save provenance and three
regressions pass. Automatic proposals remain marked after editing/saving.

Whole-photo graph45 components,20 isolated observations,66 ambiguous choices,
207 possible skipped-step links. Missing/excluded evidence remains explicit;
297 rejected edge features are not297 excluded beads. No accepted helicity,
full-string indices,N,closure or repeat. Earlier geometry fits remain unchanged.

**Stopping point:** automatic program, separate labeler export, independent checks
and curated raw/point/link review. [Q167.1](photo2/AUTO_LABEL_REVIEW.md) is answered:
maker confirms448/449/450are three distinct beads (R168), not all proposed edges.
**Next bounded task:** improve missed/merged/split central bodies and their
neighbors. Do not use unverified whole-ring cycles as hand witnesses.
No physical necklace or hidden-body prerequisites. Recommend gpt-6.1-sol / High;
same session, no /new needed. R161–166 checkpoint92700e4 was published and verified.

## Prior task — R161–R166: extended labels and wider photo-only workspace

[Revision 296 audit](photo2/LABEL_EXTENSION.md): 40 bodies, 30 series, 86 links,
47 closing cycles, ten six-neighbor stars; all old points/links preserved.
Both conditional index maps remain valid. Longest diagonal runs are five steps.
No larger-patch geometry test has yet been performed.

[Step minimum and visibility](photo2/DIAGONAL_MINIMUM.md) distinguish the nominal
7/6 scale from a conditional endpoint-identity guarantee; no universal bead-count
minimum. Exact consecutive 7/6-link paths decide the family if end identities
are known; that witness is absent here and may include hidden bodies.
42 mod13=3 gives nominal relative minor phase ±166.15°, approximate for q≠6.5.

[Wider labeling assets](photo2/WIDER_LABEL_VIEW.md): raw crop [900,0,1900,700],
portable matching JSON, all 40 IDs/numbers/series preserved. Prefer widening the
original-coordinate app crop; original live save untouched. No launcher change.

**R166 constraint:** inference uses only the photograph. Do not require inspecting
the original necklace, physical counts or hidden-body labels. Conditional closure
arithmetic is explanatory, not a gate. Target substantial central visible bodies.

**Stopping point:** audit, mathematical clarification and wider assets complete.
**Next task:** compare saved A/B poses with the 13 added visible surface points
after extending/checking latent coverage (old +47 limit; new +53/+51 offsets).
Preserve held-out 22/23/24/25; use new points first as validation. No fresh fit,
whole-ring walk, N/repeat/full-string indices or physical-necklace request.
Recommend gpt-6.1-sol / High; same session, no /new needed.

## Prior task — R160: confirmed-interior refit

The maker confirms all five green loops are inside their red/yellow/black beads;
Q157.1 and Q159.1 are answered. Black color is clear despite uncertain full-body
position/extent/boundaries. Orange dots were positive interior samples misowned
by a saved model, not boundary locations.

[Refit both families](photo2/INTERIOR_REFIT.md) using the unchanged loops plus
23 maker training marks; withhold 22/23/24/25 from bounds, objective and ranking.
Both A and B now have orthographic poses covering all 660 core pixels, 454 route
samples and all 27 marks, including fixed q=6.5. Keep A1's old withheld failure
and the refitted nominal-perspective B failures explicit. Known synthetic wrong
B also passes all positive evidence after fitting. No helicity accepted.

**Stopping point:** bounded refit plus independent POV and held-out isolation
checks. **Next task:** find an additional clear training body within the current
27-bead patch where the competing poses differ; show raw context and conservative
interior evidence before using a new loop. Retain H/S/V and reflection/dark-context
methods; no complete boundary or larger patch required yet. Do not start the
whole-necklace walk or infer full indices/N/closure/repeat. Recommend
gpt-6.1-sol / High; same session, no /new needed.

## Prior task — R159: frozen poses scored on provisional interiors

[Interior comparison and Q159.1](photo2/INTERIOR_POSE_COMPARISON.md) evaluates
all saved R156 poses on five unchanged R157 loops: 454 fractional line samples
and 660 enclosed pixels, positive evidence only. Baseline B1 covers everything;
saved A1/A2/A3 miss 38/171/31 enclosed pixels. Fixed q and nominal phone-camera
sensitivity also favor a saved B pose, though one all-interior perspective pose
misses an old held-out mark. Scores do not erase those failures.

B is stronger among the saved poses, not accepted helicity. Q157.1 and focused
Q159.1 remain unanswered, so loops/results are provisional. No pose refitting
or negative/background loss was performed. Known synthetic calibration also
shows that a correct-family point fit can miss true interiors; a failed frozen
pose does not rule out its family. Original model extents remain rejected.

**Stopping point:** complete frozen-pose/interior comparison with independent
POV checks. **Next task:** bounded refit of both families using the interior
samples plus existing training marks, preserving held-out 22/23/24/25 and loop
uncertainty. No outline acceptance is required first; do not infer closure,
full-string indices/colors/repeat or start whole-necklace walking. Recommend
gpt-6.1-sol / High; same session, no /new needed.

## Prior task — R157–R158: replace rejected outlines with interior loops

The maker rejects all prior full-body outlines because they cross into adjacent
beads. Use conservative closed interior loops, hue for red/yellow appearance,
S/V to avoid edges, and a black bead's reflection plus nearby dark surround.
[Five central examples and Q157.1](photo2/INTERIOR_LOOPS.md) replace the outline
selection question. Q156.1 is closed by this rejection; older unanswered outline
questions do not gate this new interior-based method.

The diagnostic loops use existing training marks only; group 22/23/24/25 stays
excluded. No prior fitted boundary, old HSV box or specular boundary marker is
used. Outside pixels remain unknown. Maker acceptance is pending; no new pose,
helicity, full index or color order is accepted.

**Stopping point:** five conservative interior loops and raw-image review.
**Next task:** compare existing poses using reviewed loops as positive surface
samples. No complete bead outline needs to be accepted first. Do not advance
whole-necklace walking, closure or repeat inference. Recommend gpt-6.1-sol / High;
same session, no /new needed.

## Prior task — R156: curved 27-body comparison complete; outlines later rejected

[Curved comparison](photo2/CURVED_PATCH_FIT.md) fits 23 ordinary maker surface
locations and withholds the neighboring 22/23/24/25 group. Both A/+1 and B/−1
have a pose owning all 27 marks under orthographic projection, including when
pitch is fixed at 6.5. The wrong family also passes all 27 in a known curved
POV example. The nominal phone-perspective sensitivity is not calibrated and
does not justify rejecting A. Neither helicity, camera nor outward anchor is
accepted. Predicted outward exposure is checked by owner AND first-hit depth,
but remains a model prediction, not an image measurement.

Raw context, proposed visible extents and outward points are compared in
[Q156.1](photo2/CURVED_PATCH_QUESTIONS.md), asking about clear central bead 11.
The older Q149.1 remains pending independently. Preserve passing alternative A
starts rather than treating the first start's withheld failure as family rejection.

**Stopping point:** this bounded comparison and illustrated review. **Next task:**
constrain a central body with the reviewed extent or a short reliable boundary
segment, then derive supported outward positions. The existing patch remains
the appropriate starting region; do not request a larger patch or begin the
whole-necklace walk/color/closure/repeat phase from these unaccepted poses.
Recommend gpt-6.1-sol / High; same session, no /new needed.

## Prior task — R152–R155: existing patch exceeds the one-step size scale

The maker asks how large a connected region must be to identify helicity.
[Assessment](photo2/PATCH_SUFFICIENCY.md) recommends starting with the existing
27-body patch and its six recorded complete neighbor stars. Roughly 20–30 clear
bodies with several overlapping stars is a practical target, not a measured
minimum. Seven accurately located outward anchors may suffice in favorable
geometry; R149's arbitrary visible points do not test that stricter claim.

R153–R154 ask for a one-bead count difference using the computed angles. Outward
angles 47.72°/43.31° imply a common centerline span of 18.6183 model units,
6.4615 nominal row spacings, with seven direction-6 steps versus six direction-7
steps. Chord, unrolled-arc and index calculations agree. R155 asks if 27 is enough:
the candidate index spans correspond to about ten rows and exceed this geometric
size scale. A larger equally clear patch may help precision; use the existing
patch first. Hidden intermediate bodies and anchor/view uncertainty remain.

**Next bounded task:** assess supported outward locations and compare competing
projected poses on the saved patch, allowing centerline curvature and holding out
a neighboring group. Judge alternatives against location uncertainty, not bead
count alone. No additional labels requested and no new fit performed in this
assessment. Stop at the requested explanation; neither helicity accepted.

## Prior task — R150–R151: outward-point direction angles calculated

The maker asks for 1/6/7 angles for both helicities, emphasizing each bead's
point farthest from the minor-circle center. [Calculation](photo2/DIRECTION_ANGLES.md)
uses reference radius 4+bead_radius=6.110915749. Nominal local 3D point-to-point
angles are +85.54°, −47.72°, +43.31° for source winding; opposite winding reverses
signs. Unrolled reference angles are +85.71°, −48.00°, +43.59°. Source row rounding
and exact torus phase dependence are preserved separately; photo angles require
camera/section pose and anchor exposure. No photo fit changed or family selected.

**Next bounded task:** project outward anchors under competing poses and check
their exposure before using observed angles. Stop at the requested intrinsic
calculation. Q149.1 remains pending; no outline acceptance is inferred.

## Prior task — R149: local point comparison complete; outlines need review

The maker declines the launcher retry and asks to move on; existing R148 checks
stand. [Seven-point comparison](photo2/MAKER_POINT_FIT.md) fits six maker locations
around C=20, withholding G=23's location. Both remaining 6/7 families admit a pose
passing all seven points. A known synthetic example also admits the wrong family
at all seven points, so this positive-only test cannot select the assignment.

Nine independent Python/POV surface checks pass; two new tests guard signed
mapping symmetry and holdout exclusion. Optimization is bounded (20/32 stages
cap), orthographic straight-tube geometry remains diagnostic, and fixed elevation
is a camera/phase gauge. No accepted surface pose or full-string indices.

**Next bounded task:** review C's proposed visible extent in
[Q149.1](photo2/MAKER_POINT_QUESTIONS.md), then constrain poses using supported
body boundaries. Preserve ambiguous shadow/occlusion. Stop at this comparison;
do not walk around the necklace from an unaccepted local fit.

## Prior task — R148: launcher fix complete

The maker explicitly requests completion of the interrupted launch fix. The
[labeler](photo2/LABELER.md) now selects a free port when default 8765 is busy,
honors explicit ports, and tries Windows browser launchers on WSL. Missing or
failed launchers yield a quiet manual URL. Thirteen Python tests pass; actual
Windows browser selection is mocked in those tests. Existing annotations and
graph artifacts are preserved. Stop after scoped launcher delivery.

The suggested manual retry is deferred by R149. No geometry work occurred in
the launcher fix; the resumed comparison is documented above.

## Prior task — R144–R147: extract the maker's local neighbor chart

[Maker-series analysis](photo2/LABEL_SERIES.md) completes this bounded step.
Corrected save revision 162 contains 27 numbered locations, 19 series and 54
links in one connected graph. All 28 independent cycles close; all 28 triangles
agree on d2=d1+d3. Six beads have complete six-neighbor sets. The maker corrected
two skipped clicks and confirms B=22, C=20, G=23. Original/corrected snapshots,
source hashes, figures and four passing synthetic/real-data tests are preserved.

Integer chart d1=(1,0), d2=(0,1), d3=(−1,1) provides discussion coordinates.
Two 6/7 assignments remain, plus global reversal; full-string origin/N/repeat
and colors are not recovered. No 3D fit or whole-necklace walk in this step.

**Next bounded task:** compare the two family/helicity interpretations using
seven-body star 16/17/19/20/21/22/23 around C=20, treating maker points as visible
surface anchors. Keep G's pixels withheld from continuous fitting; use its graph
relation. No supplied camera elevation or acceptance of old BC=1 charts.
[Answered review questions](photo2/LABEL_SERIES_QUESTIONS.md).

The [labeler](photo2/LABELER.md) remains usable; separate launch/port changes were
completed and verified in R148, after the graph analysis was published separately.

## Where this sits in the overall solution

| Stage | Purpose | Status |
| --- | --- | --- |
| 1. Local geometry and neighbors | Establish usable bead surfaces and +/-1/6/7 relations on a small patch | **Current.** 27-body maker graph consistent; seven-body fitting seed available, 6/7 choice and geometry unresolved |
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
