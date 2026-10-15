# R290 — automatic photographic edges and batch review

The automatic detector, permanent photographic collection and interactive review
are delivered. **Complete bead-boundary reliability is not established.** All
58 primary proposals are **Partial boundary / unresolved**: 41 development and
17 reserved cases. None receives a reliable complete-boundary claim or an exported
visible-region centroid. This is a conservative experimental result, with real
truncations, mergers and reflection-edge ambiguities preserved for batch review.
It does not meet the desired positive demonstration of reliable complete contours.

Launch from the repository root:

```bash
photo2/review/r290/launch.sh
```

Open **http://127.0.0.1:8290/**. Review A, B where available, neither, insufficient
photograph, or not sure. Use arrows and keys1–5, situation/split filters, next
unreviewed, wheel zoom and drag pan. Other bright points are numbered; optional
pairwise controls record same/different physical bead without constructing masks.
An edge toggle and separate raw crop leave the photograph unobstructed.

## Collection and preservation

`r290/evidence/tests.json` established T1–T8 before detector implementation.
`collection.json` froze all original positions and the development/reserved split
before any new segmentation result. It includes P1–P5; N06/N07/N11/C05/Q06/Q14;
R289 red/yellow worst and both features in each multiple example; R215 A/B/R;
R265/R267 and R284B neighborhoods; 31 additional illuminated red/yellow cases;
and four smaller unknown-context diagnostic cases. The latter do not dominate.

Additional cases were hash-ranked by independent R289 feature ID, in the interior
12–88% image rectangle, with native11-pixel-window median linear Y≥.025 and
110px feature separation from all earlier selected cases. Eight development cases
per color and eight reserved red/seven reserved yellow were available. One reserved
yellow slot was left empty instead of relaxing the rule. Two diagnostic cases
are development and two reserved. The reserved features are ≥110px from every
development feature. Larger context windows can overlap; no geographic independence
of illumination, scene or materials is implied. This is one already-studied photo.

Situation labels derived from nearby feature colors are **selection proxies**.
They do not certify touching, occlusion or common ownership. The development
contact sheet adds documented photographic observations of separated surfaces.
The full [coverage matrix](R290_COVERAGE.md) identifies missing reserved strata,
including clearly separated examples, bright-near-boundary, internal-darkness and
specific historical failure categories. No physical hole, exact boundary or true
occluder identity is independently labeled. Do not interpret coverage as correctness.
All seeds come from the accepted R289 feature bank. The dark-context diagnostic
cases therefore still have bright measured cores; subthreshold weak highlights
and uninformative/tiny cores are missing. The insufficient-measurement status has
no positive example in this collection. Same-bead ownership of distinct bright
features also lacks an independent photographic truth label.

The original `red-worst` same-physical-bead confirmation is preserved, with every
displayed coordinate and original image hashes. R215 and R284–R288 user judgments
retain their original sources and image references. None enters detector inference.
R275, J, M and W are never treated as boundary truth or runtime masks.

Two selection-description errors remain explicitly corrected in
`provenance-corrections.json`: P4/e07 concerns yellow beads, despite the old crop
name `auto-black`; the stable ID `R265-R00956` actually selects the R01284
neighborhood at (977,2665). Its stable ID is retained. The old R00956 neighborhood
is not separately covered. `R284B-lower-black` selects a red-context feature10.63px
from its historical anchor: no claim that it recovers the old black target.
Every case shows both the historical anchor and selected independent feature.

## One primary edge-first method

`detector.detect(rgb, feature, nearby)` receives ICC-managed photographic RGB,
one independently detected R289 bright patch and optional other independent
features. There are no case names, situation tags, historical masks, judgments,
physical models or identity data in its decision procedure. Nearby features are
measured as competing explanations; they are not simultaneously segmented.

1. Measure linear luminance and short normal profiles on a native four-neighbor
   pixel graph. Offsets are ±3px, with five adjacent tangent samples. This is a
   local edge stencil, not radial sampling or a shape representation.
2. T1 measures persistent dark transitions. A drop needs either brightness
   recovery across a valley or a genuinely dark far side. T2 separately retains
   ordinary drops, recovery and continuous-material cut evidence. A bright route
   around a seam never cancels its local darkness evidence.
3. T3 compares channel-difference color directions, discounted when either side
   lacks illumination or saturation. This tolerates brightness scaling and an
   additive neutral reflection better than simple RGB chroma. Saturation loss alone
   is not treated as a material change. T6 retains coherent color/brightness steps
   as possible occlusion edges, with unknown occluder identity.
4. Edge conductance is `0.0001 + (1 + continuity) * exp(-20 * evidence)`, where
   evidence is the stronger of sustained darkness and1.2×coherent color change.
   Solve the harmonic graph potential with the measured bright patch fixed at1
   and the computational frame at0. The0.5 level set supplies a **candidate**.
   This has no shape, area, convexity, roundness, solidity or perimeter objective.
5. Recompute with conductance exponents0.85/1.15 and19px more context. Each pixel
   side needs a sustained dark transition, coherent color step or sustained
   context-supported brightness step, plus boundary persistence within1px.
   Otherwise it remains dashed and unresolved. This is evidence support for a
   photographic edge; internal-versus-external ownership can still be unresolved.
6. Search starts at38px half-width and expands to76/152px on guard-band contact.
   Four cases expanded. Frame-adjacent sides are never photographic evidence.
   The152px computational cap reports unresolved rather than rejecting an object.
7. T4 saves other-feature inclusion and31-sample pair brightness profiles without
   asserting common ownership. T5 records internal dark pixels, enclosed excluded
   regions and internal coherent valleys without filling holes or assigning owners.
   T7 records supported/unresolved arc components, completeness and frame contact.
   T8 records illumination, contrast, reflection ambiguity, IoU and centroid spread.

Every A/B candidate receives all eight tests. A complete status requires every
side supported, adequate measurement, minimum perturbation IoU≥.90, no frame
contact and no unresolved competing-highlight/internal-valley/reflection evidence.
Darkness and color offer alternative local support; they are not eight yes/no
gates. Neutral reflection-region edges remain ambiguous as visible bead edges.

Exact native pixel-square sides, reasons and numerical profiles are saved for
every segment. Supported connected arcs never silently bridge unresolved gaps.
Candidate masks and their centroids are clearly hypothetical. Visible-region
centroids and bead-owned visible pixel exports are null for all partial cases;
the independently measured original bright patch remains available. There are
23 automatically arising alternative B contours from the same graph objective.

## Development failures and reserved results

Three saved checkpoints retain initial sources and complete development results:
simple RGB chroma incorrectly bounded pale red highlights; color correction alone
left monotonic illumination mistaken for darkness; and minimum-cut contour length
still contracted around small seeds. The final method retains the edge measurements
but replaces perimeter minimization with graph resistance. No family of separately
tuned segmentation methods or coordinate repairs is deployed.

The source/parameter freeze is recorded at **2026-10-15T04:04:57Z**, before reserved
inference. No detector or parameter changes followed. Later provenance and review
software corrections do not alter inference. All initial scientific failures survive.

| Primary status | Development (41) | Reserved (17) |
|---|---:|---:|
| Reliable boundary | 0 (0%) | 0 (0%) |
| Partial boundary / unresolved | 41 (100%) | 17 (100%) |
| Insufficient measurement | 0 (0%) | 0 (0%) |

Median supported-side fractions are69.5% development and82.0% reserved. These are
photographic edge-support fractions, **not boundary precision**. Some small reflection
regions have100% locally supported sides but remain unresolved as bead boundaries.
Minimum measured primary IoU across perturbations/context is.258 development and
.496 reserved. Some candidate regions change considerably; uncertainty is not
calibrated into a physical confidence interval.

Known unresolved examples include N06 and yellow-multiple-2 merging substantial
neighboring material; R215-A expanding into a larger illuminated region; several
red cases retaining only a reflection patch; and Q14 failing to establish the full
surface. The context change itself exposes instability. These cases are delivered,
not repaired against reserved outcomes. No initial method's accepted-boundary count
is interpreted as a gain or ground truth.

Human correctness of A/B, neighbor-pixel inclusion, missing target material,
duplicate ownership and centroid accuracy remain **unmeasured**. Historical
qualitative interior judgments and centroid disagreement do not establish exact
reference pixels. The batch judgments will supply evaluation evidence for a later
round; they will never become automatic coordinate exceptions.

## Durable review and validation

The server saves `photo2/r290/feedback/judgments.jsonl`, excluded from Git. Each
fsynced append records stable IDs, native coordinates, original image hash,
algorithm/parameters, exact displayed A/B masks and contour evidence, other feature
coordinates, selected answer, previous answer and revision ancestry. Immutable
candidate JSON/native-crop snapshots are saved alongside it. Undo appends a revision;
it does not delete history. Closing/restarting the same server reloads answers.
Export includes all revisions and displayed candidate measurements. No test creates
answers in the user's feedback directory.

Validation:14 real-photo regression tests; all58 native crops match original decoded
pixels; both development/reserved data files replay byte-for-byte; all58 regenerated
PNGs match;11,197 historical files unchanged. Chromium loaded all58 cases and their eight evidence panels, checked desktop1400px
and narrow520px layouts, and passed answer/revision/undo/alternative/ownership/
export/reopen checks. Receipt: `r290/results/browser-check.json`.
The technical browser check is not human scientific validation.

Production and all three phases remain unchanged. No synthetic image, generated
photograph, renderer, camera/light fitting, indexing or pattern experiment was run.
Scientific delivery and remote verification are recorded separately in
`r290/results/delivery.json`. **Stop here for the user's batch review.**
