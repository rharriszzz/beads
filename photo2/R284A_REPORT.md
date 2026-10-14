# R284A — compare native Phase 1 supports before adoption

**Recommendation: choose A as the conservative colored-support direction and C's
separate black-reflection/body treatment as the second component to investigate.**
Do not adopt C's colored straight-path rule or certify B's partitions as separate
beads. No combined A+C method has been tested or adopted in this round.

Start with the [comparison viewer](review/r284a/index.html). Its three focused
panels address the user's exact concerns:

- [Two-sided: bottom spike, left red, right yellow](review/r284a/two-sided-focus.png).
- [Upper black, lower secondary, neighboring red](review/r284a/duplicate-focus.png).
- [Bad magenta outline](review/r284a/abstention-focus.png).

The viewer also includes eight complete-context comparisons, native 128×128 crops,
4× enlargements, eight reflection/collar diagrams, expandable measurement tables,
and [630 per-method records in CSV](review/r284a/measurements.csv). Exact native
masks, cue dispositions and parameters accompany the images. All 1,092 R283
records and all Phase 2/3 inputs, code and results remain unchanged.

**This is a method-comparison result, not complete centerline recovery.** A improves
the named colored outlines, C improves the named black interpretation, and B exposes
more plausible neighbors. None establishes that every bead crossing the centerline
has been found. A has no net increase in high support-near candidates across these
eight crops; its high interior-crossing count falls. That limitation is central to
the recommendation, not a footnote to a larger candidate count.

## What actually failed in R283

1. **The lines follow erroneous masks.** `r283/review.py:overlay` paints native mask
   edge pixels. There is no spline overshoot causing the cyan spike. The error
   originates in `r282/phase1.py:attempts`: connected color growth, a radius bound,
   disk-2 opening and one-pixel erosion can retain a thick enough side branch.
   Shape gates can accept that region even when part belongs to another bead.
2. **Abstention did not repair geometry.** R283's symmetric graph marked shared
   supports unresolved while retaining their original masks. The magenta example
   contains two overlapping measurements of a yellow feature; one reaches toward
   an upper-left patch. Coloring a wandering mask magenta does not make its outline
   a useful ownership proposal.
3. **Reflection connectivity is not body identity.** A small bright feature and
   a larger bright feature can share dark material whether they are one bead or
   adjacent black beads. R283 retained the alternatives without deciding which
   was primary. The new design explicitly separates reflection, collar and
   secondary-feature hypotheses; no full black-body silhouette is inferred.
4. **The review selected too little context.** The red left and yellow right in
   `two-sided.png` already have high R283 records but were omitted from its selected
   pair. They must be represented in the review and coverage accounting; their
   appearance here is not evidence of newly discovering two previously missed beads.
   Likewise, the red right of the upper black is now a required comparison feature.
5. **More seeds can reduce reliability.** Native maxima and pigment-thickness cues
   find additional features, but may also find several features on one body or
   shadowed paper. A neat exclusive partition can turn those features into false
   separate bead proposals. This occurred in both real and synthetic comparisons.

The user's qualitative statements are recorded as evaluation evidence in the
request log and focused panels. `assess.py` contains evaluation-only locations for
these seven reviewed features. Neither `methods.py` nor `run.py` imports them.
No reviewed identity, pixel ownership, Phase 2 index or Phase 3 pattern enters
segmentation.

## Three genuinely different native-mask methods

All methods receive the same photograph-derived cue bank. It combines mean-3 and
mean-5 maxima, learned-pigment thickness maxima and preserved photographic seeds.
Nearby cues consolidate within four pixels; same-color cues within 16 pixels
consolidate only when a same-material straight route has no sufficiently dark
saddle. Every raw cue and its disposition remains in a ledger. This consolidation
is a feature hypothesis, not proof of one body. The palette and paper hue are
estimated from the image using the existing Phase 1 feature extractor.

High colored supports additionally require a sufficiently strong cue (native local
peak ≥0.12 linear Y, mean-5 ≥0.045), area 30–870, one connected component, solidity
≥0.80 and neck retention ≥0.70. Smaller/weak/conflicting alternatives survive.
These are engineering gates, not calibrated correctness probabilities. Native
supports below 12 or above 870 pixels are rejected; oversized failures are retained
as diagnostics, never accepted or silently clipped into compliance.

| Method | Actual ownership/support change | Main limitation |
|---|---|---|
| **A: thickness-core pruning** | Start with the existing C measured interior. Open by an adaptive disk of radius 2–4 from its interior thickness, select the cue-connected thick component, reconstruct at most one native pixel within the original mask. No convex fill. Symmetric overlap abstention remains. | Cannot settle same-body multiple cues; new cue positions can change the starting mask. Compactness is not identity. |
| **B: geodesic competition** | Native eight-neighbor path cost uses image gradient and brightness inside learned material. All nearby cues compete; retain an owner only with cost margin ≥1.4, then remove small protrusions and disconnected pieces. Black proposals also participate. | Exclusive pixels do not imply exclusive bodies. A missed true cue can still permit leakage; extra cues can split one bead. |
| **C: irreversible paths + black feature/body separation** | Colored pixels require native straight paths with no material-barrier crossing and no renewed brightness rise after a trough. Black support is a compact neutral reflection plus a one-pixel measured dark collar, with a separate two-pixel enclosure test. Weaker nearby neutral features can become secondary hypotheses. | Colored shading creates severe notches/crescents. A shared dark route cannot uniquely establish black-body ownership. |

C's secondary test compares nearby black cues within 18 pixels, weaker/stronger
peak ratio <0.70, ≥80% neutral route, ≤10% paper-classified route and a dark route
median. The small paper allowance handles a tinted reflection pixel; it is not a
license to cross paper gaps. The weaker feature remains saved and is excluded
from the high-bead count. Strong and weak features are not merged into an invented
body mask. Three of four final real secondary links have no supplied identity truth.

All outlines are exact native mask edges. Display enlargement uses nearest-neighbor
pixels. White dots are measured-support centroids, orange crosses initial cues,
and the white line is the unchanged image-derived centerline. None is a physical
bead center or full-body outline.

## Real-photo findings, including unsuccessful alternatives

| Reviewed feature | R283 | A | B | C |
|---|---|---|---|---|
| Bottom cyan yellow | High, 509 px with side spur | High, 516 px; reduced spur | High, 562 px; competitive separation | High, 584 px; old spur removed but a notch appears |
| Red left, line crossing | High but omitted from old pair picture | High, 537 px, crossing | High, 501 px, crossing | High, 670 px, crossing |
| Yellow right | High but omitted from old pair picture | High, 490 px, crossing | High, 626 px, crossing | Unresolved, partial 362 px |
| Upper good black reflection | Unresolved, 78 px | High, 67 px | High, unchanged 78 px | High, compact 40 px reflection/collar |
| Lower secondary reflection | Unresolved, 40 px | Unresolved, 32 px | Unresolved, 40 px | Explicit secondary hypothesis, 8 px, linked to upper cue |
| Red right of upper black | High, 440 px | Unresolved, 435 px, overlapping cue | High, 338 px | High, 447 px |
| Bad magenta yellow feature | Overlapping unresolved 429 px measurement | High, compact 355 px | High, bounded 399 px | Unresolved, irregular partial 236 px |

These areas are exact measurements, not true bead areas. The bad-magenta row uses
the nearest original seed; both original competing supports remain in the full
panel. A removes 103 pixels from that original mask and adds 29 after shared cue
remeasurement. For the bottom cyan feature A removes 15 old pixels and adds 22.
Although its pruning operation is strictly a subset at a fixed seed, changing the
shared cue from the old seed can add pixels relative to the historical mask.

The reviewed lower reflection was **already not high in R283**. C improves the
interpretation and the reflection/body decomposition; it does not demonstrate
removal of a previously high false bead in this case. A/B also avoid counting it
as high, but do not explain its relationship to the upper reflection.

Five additional crops are selected before comparative inference by reproducible
criteria saved in [cases.json](r284/results/cases.json): highest-quality high red
and yellow crossing interiors; a high black near interior; a saved opposite-side
pair; and three nearby high candidates with maximal side diversity. Crops are
separated from earlier selections by >180 pixels. This intentionally includes
established cues and difficult neighbors; it is not a blind random recall sample.

Visible failure diagnostics include B splitting the left yellow in `auto-red`
into high supports 1/4/10, the right yellow in `auto-yellow` into 2/12, and the left
yellow/highlight area in `auto-black`. Thus **at least three reviewed cases show
apparent same-body partition failures**; this is qualitative inspection, not a
pixel-labeled real precision measurement. C still separates some yellow features
incorrectly and severely trims the main crossing yellow in `auto-three`. A retains
unresolved same-color overlaps, including the red neighbor in the duplicate crop.
All three still have doubtful peripheral/background candidates.

A's two named colored repairs are the most useful real-photo improvements. C's
black decomposition is useful independently. B's broader proposals are worth
retaining for a future ownership test, but its extra supports cannot be called
additional recovered beads.

## Centerline accounting and quantitative comparison

Every native support pixel is projected onto the saved curve. Records contain
signed-distance extent, minimum distance, median signed side, longitudinal station
and local arc extent. Crossing requires both signed sides and a support point
within one native pixel of the curve. Nearness uses half the **frozen R283 local
support scale**, so shrinking a candidate cannot shrink its own acceptance band;
a fixed 12-pixel sensitivity is also saved. Centroid proximity never certifies near
membership. Reflections and rejected/uncertain supports retain their own geometry.

A full body can cross the line even when its compact measured interior does not.
Consequently, neither interior-crossing counts nor high-near counts measure the
number of true crossing beads recovered. There is no complete real bead truth set.
The seven qualitative reviewed features above provide limited, explicit evidence.

| Eight disjoint 128×128 crops | R283 baseline | A | B | C |
|---|---:|---:|---:|---:|
| High candidate observations |69|85|145|85|
| High support-near observations |45|45|71|42|
| High interior-crossing observations |23|19|32|20|
| High near red / yellow / black |13 / 22 / 10|12 / 18 / 15|21 / 35 / 15|13 / 17 / 12|
| Candidate opposite-side pairs at nearby station |5|9|13|2|
| Distinct windows with ≥3 high near candidates |1|3|14|1|
| Overlapping candidate-mask pairs, including unresolved |—|70|0|53|
| Explicit secondary hypotheses |—|0|0|4|
| Disconnected high masks |0|0|0|0|

Pair/window counts are descriptive candidate relationships. Windows overlap and
are not independent bead counts. A whole crop contains several longitudinal
stations; 71 candidates across eight crops does not mean eight stations each need
nine beads. No exact number is imposed at any station. Every candidate is counted
once in the observation totals; pairs and windows are separate diagnostics.

The disk-2 opening loss for the named bottom-yellow support is 1.57% in R283,
0.58% in A, 1.78% in B and 0% in C. This thin-part penalty is not a calibrated
leak detector: C's deep notches can score zero. Across all high masks, median
solidity is 0.952 / 0.946 / 0.926 / 0.909 for R283/A/B/C. The native boundary-pixel
compactness diagnostic is 1.212 / 1.238 / 1.134 / 1.127; because it counts boundary
pixels rather than a calibrated geometric perimeter it can exceed one. None of
these scalars overrides the photographic failures.

Exact distinct real-bead recovery, leaking-support counts and false-secondary
counts remain **unmeasured**, rather than being equated to overlap counts. The
strongest explicit real secondary check is one user-confirmed feature, which C
handles as requested; its three other links remain unverified. All high masks are
connected, but connectedness is plainly insufficient to establish ownership.

An [original-cue-only control](r284/results/original-cue-control.json.gz) reruns the
same support methods at exact R283 seeds, without expanded discovery/consolidation.
It yields 53 / 64 / 48 high-near observations for A/B/C, compared with 45 / 71 / 42
using the shared new cue bank. Thus expanded cues do **not** uniformly improve
recovery. Extra conflicts and moved cues reduce A/C acceptance; B accepts more
partitions. No control is promoted merely for its count.

## Supporting synthetic controls, subordinate to the real photographs

Sixteen saved, physically certified POV-Ray scenes from R283 are reused with
unchanged appearance and truth. They are now retrospective development controls,
not a new held-out confirmation. Inference sees appearance pixels and serializes
results before the evaluator opens identities. No real reviewed coordinates,
physical indices or pattern assumptions enter detection. There are 389 eligible
visible bodies; ≥95% single-body mask purity defines a correct synthetic support.

| Retrospective controls | A | B | C |
|---|---:|---:|---:|
| High supports |138|225|167|
| Distinct pure bodies / high supports |124 / 138|173 / 225|157 / 167|
| Distinct-body precision |89.9%|76.9%|94.0%|
| Eligible-body recall |31.9%|44.5%|40.4%|
| Extra detections of an already detected body |3|30|3|
| Mixed/foreign-body supports |11|22|7|
| Red / yellow / black eligible bodies recovered |36 / 30 / 58|47 / 66 / 60|50 / 52 / 55|

These numbers support the real-photo diagnosis that B's exclusive pixels can
multiply body identities. C's better synthetic precision does not excuse its
visibly poor yellow real-photo masks. A/C both retain synthetic duplicates and
mixed supports. None is sufficiently validated for global automatic adoption.

## Preservation, verification and stopping point

The [first pass](r284/first-pass/) retains source, every mask/cue result and three
main panels. It exposed high-class shadowed-paper proposals, aggressive splitting
and failed colored radial supports. The final pass added stronger cue evidence,
same-material consolidation and irreversible native brightness stopping. A route
helper was also corrected to preserve endpoint order; native pixel deduplication
must not sort a sampling route spatially. This has a direct regression test.

[Reproduction instructions](r284/README.md), [requirements](R284A_CHECKLIST.md),
[exact replay/preservation audit](r284/results/audit.json), and
[rendered browser audit](r284/results/browser-check.json) accompany the package.
45 tests pass (12 new and 33 preserved). The independent replay matches 19 files;
9,793 pre-round photo2/source-photo Git blobs and eight native crops are unchanged.
Chromium loads 27 images (19 comparison/evidence panels plus eight native crops),
25 tables and all linked local artifacts without page errors. Tests cover anti-spike subset behavior, disconnected-neighbor isolation, first-barrier
and dark-trough stopping, order-independent competition, native support/centroid
round trips, one-owner masks, complete cue disposition and uncensored uncertainty.
The preserved R282/R283 suites check that the surrounding architecture still works.
No later-phase optimization, model identity, total count, helicity or pattern work
was performed.

**After the user chooses:** freeze the selected support design and compare it on
additional automatically chosen crossing/two-sided crops, explicitly testing
same-body multiple cues and missed crossing bodies. If A plus C's black branch is
chosen, implement that combination as a new bounded experiment first; it has not
been tested as a combined method here. Keep old measurements and unknowns intact.
Only consider a full Phase 1 replacement after ownership/coverage evidence improves.

Stop after scoped commit/push and remote verification. Await method review and
choice. Keep the current model/reasoning setting; no `/new` is needed.
