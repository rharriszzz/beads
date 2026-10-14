# R286 — dark boundaries without sacrificing diffuse red

**Recommend M: context-supported marker repair, for user review before adoption.**
It fixes the demonstrated P5 failure and leaves P2’s good495-pixel red interior
exactly unchanged. B, a stronger protected-watershed alternative, gives the same
P5/P2 result but falsely splits a shallow-shading control. A/C direct-path methods
show central photographic leakage and are not recommended. No production inventory,
Phase2 fit or Phase3 pattern has changed.

Start with the [visual review](review/r286/index.html), especially
[P5](review/r286/P5-choice.png), [P2](review/r286/P2-choice.png),
[all three two-sided observations](review/r286/two-sided-three.png), and
[independent C05 failure](review/r286/C05-all.png).
The compact strips label B; **M and B are identical on all five reviewed cases**.
Full panels show J/S/M/A/B/C, exact native fills, barriers, photographic centroids
and native brightness profiles. All52 confirmation cues, including failures, have
atlas panels. Native crops are linked separately without resampling.

## Why S failed on P5

The cause was missing photographic markers, not merely a permissive basin-merging
threshold. Two strong neighboring yellow maxima were0.47° and0.16° outside the
single-pixel learned-pigment hue gate. The surrounding radius3 neighborhoods were
89.7% and96.6% valid pigment. The maxima were not paper and survived smoothing, but
intersecting the maximum map with the material mask erased their markers. All three
yellows therefore occupied **one basin before merging**.

The direct paths from the target to those neighbors cross minima of linearY
0.00760 and0.09491, below S’s0.11571 growth floor. Nevertheless, connected routes
around those dark regions have minima0.15173 and0.15470, above the floor. Those
brighter detours join the eligible material. With no neighboring markers, watershed
competition cannot separate it. The remaining marked upper-right neighbor *is*
correctly separated: its saddle/reference ratio0.223 is below0.65.

The local background estimate and smoothing did not erase the dark valleys.
A smaller search domain truncates the large merger (1114 rather than1817pixels),
but does not solve it. This explains why changing merger thresholds or making a
smaller, prettier support would miss the demonstrated defect. See the
[pre-implementation diagnosis](R286_P5_DIAGNOSIS.md),
[native diagnostic](review/r286/P5-root-cause.png), and
[full path/marker evidence](r286/results/P5-diagnosis.json).

## What was compared

The unchanged S measurement domain separates diffuse pigment brightness from
isolated highlights. It uses sigma0.65 luminance, local diffuse60th percentile,
background plus20% diffuse contrast, learned hue/saturation material eligibility,
and bounded neutral continuation. This retains P2’s darker red. All new methods
use that same domain so their separation mechanisms can be compared. No thickness,
solidity, roundness or area objective was optimized;870pixels remains a flag.

|Method|Distinct mechanism|Observed limitation|
|---|---|---|
|J|Unchanged local contrast isophote control|Preferred P1/P3 but truncates P2; not ground truth|
|S|Unchanged diffuse field + maximum-saddle watershed|Loses P5 markers; bright detours merge unmarked neighbors|
|M, causal control|Retain a maximum supported by ≥half its radius3 pigment neighborhood, project its marker ≤3px to eligible material; retain original maximum/projection ledger; original saddle rule|Fixes marker deletion, not every ownership/merger defect|
|A|Persistent dark ridges: bilateral bright shoulders at4/7px, eight directions, valley ratio0.70, connected ridge≥5pixels; direct paths cannot bypass a detected ridge|Incomplete ridge geometry lets diagonal routes reach other beads; C03/C05 leakage|
|B|Completed markers + watershed interface distribution; ≥60% dark pairs below0.65 reference, ≥3pairs and marker distance≥6; strong separations become immutable cannot-links through later unions|Can split normal internal shading; marker count is not bead count|
|C|Direct native paths retain running minima; stop after a deep valley (<0.65 diffuse) and renewed rise (>0.18 diffuse) lasting≥2px|Ray-dependent wedges, lobes and missed separation; dim internal texture remains ambiguous|

A/B/C are three distinct mathematical alternatives. M is an additional causal
ablation, not counted as a fourth independent separation idea. Algorithms contain
no reviewed coordinates, target masks or physical identities. Exact parameters,
source hash and selection hash were frozen before confirmation; **no tuning after
confirmation**. The initial implementation and all failures survive.

## Reviewed photographs: solve P5 without breaking P2

|Case|User decision|J|S|M|A|B|C|
|---|---|---:|---:|---:|---:|---:|---:|
|P1 lower yellow|J better; S acceptable|439|540|540|540|540|604|
|P2 red centerline|J poor; S good|200|495|495|495|495|495|
|P3 yellow brightness|J better; S slightly worse|405|446|446|451|446|519|
|P4 edge yellow pair|J bad; S acceptable; secondary priority|439|320|320|325|320|363|
|P5 multiple yellows|J acceptable; S seriously merges|511|1817|664|665|664|777|

Areas are native photographic pixels, not physical silhouettes. M/B remove1153
P5 pixels belonging to the connected neighboring regions and shift the measured
centroid19.88px back toward the target. This large correction is not automatically
instability. M’s repair alone produces the gain; B’s stronger merger protection
adds no benefit on these five cases. A provides an independent near-identical
P5 separation, but fails elsewhere.

All four candidates preserve P2’s495pixels exactly, including its darker material.
The supplementary right yellow remains614pixels in S/M/A/B/C (J499), support-crossing
and near. The lower yellow, left red and right yellow remain three separate
observations. No invented fixed station count is imposed.

P1/P3 remain limitations: M/B inherit acceptable/slightly worse S rather than the
user-preferred J. C’s larger P3 support adds a lobe/notch, not established valid
material. This round solves the specific P5 separation defect, not every prior
brightness-boundary preference.

## Independent confirmation and unexpected failures

The selection was frozen before generating new results: ten spatially separate
regions, eight central and two clear-edge, chosen by reproducible SHA256 ranking
within photograph-only strata. Native11×11 medianY>0.025 and existing photographic
high status identify anchor candidates; that historical status is not ground truth.
Regions are >145px from earlier reviewed/confirmation centers and each other.
Strata include red/yellow crossing, strong-highlight diffuse red, same-color dark
seam, opposite-side nearby pairs, additional central and clear-edge cases.

All existing colored cues within40px and complementary mean3/7px maxima were
frozen together: **52 observations,44 in central crops and8 in edge crops**.
Fresh maxima must be≥5px from old cues and within30px of the image-derived curve.
Eight fresh cues survive as unresolved evidence. Three are area-flagged; all five
unflagged fresh supports overlap an old proposal with IoU≥0.5. Thus this sample
does not establish any newly recovered distinct physical bead from fresh cues.
See [selection](r286/results/selection.json) and
[full evaluation](r286/results/evaluation.json).

**All ten M/B anchor masks equal S exactly.** Thus the new sample demonstrates
preservation of good central diffuse interiors, but does not independently repeat
P5’s missing-marker improvement. All ten have domain32/48 IoU1; mean illumination
IoU0.9934. Illumination perturbations scaleY0.8/1.2 and impose a0.8→1.2 ramp while
holding pigment/background labels fixed. These are conditional stability tests,
not physical relighting or proof of reliable ownership.

|Candidate, all52 cues|Flagged|Area>870|Domain-sensitive|Illumination-sensitive|Window contact|
|---|---:|---:|---:|---:|---:|
|M|9|6|9|1|3|
|A|14|11|12|2|7|
|B|8|5|6|2|1|
|C|8|3|6|1|3|

Flags overlap. Unflagged means reviewable-unrated, never high confidence or a
calibrated acceptance decision. Original J/S did not receive this same full
perturbation protocol, so their apparent flag rates must not be compared directly.
All new nonempty supports are4-connected. There is no hidden selection of a nearby
component if the actual cue is excluded.

Important failures, with every cue shown in the atlas:

- **C03/C05 central anchors:** A extends into neighboring colored material. C05 A
  grows1134pixels and is area-flagged; C also leaves protrusions. A higher number
  of apparent centerline crossings from such supports is not recovery.
- **C02 weak interstice:** M/S1475pixels merge neighboring material. B131pixels
  isolates a tinted highlight, but is illumination-sensitive; its red assignment
  and physical ownership remain uncertain. No new red bead is certified.
- **C03 weak outer interstice:** M/S454pixels extend toward the yellow/paper edge;
  B92pixels confines a small feature. This is a lower-priority uncertain edge cue,
  not evidence that B’s extra rule improves clear central beads.
- **C04 fresh weak cue:** M/B885pixels still span a dark-profile pair and are flagged.
  Repairing missing markers does not guarantee every separating seam has markers.
- **C07:** four near proposals form two high-overlap groups. They must not be reported
  as four distinct beads. Nearby observations and their provenance remain present.
- **C10 edge anchor:** A becomes domain/illumination-sensitive. No retuning to rescue
  it; difficult edges remain lower priority than central material.

The native mean3 direct-profile diagnostic finds49 same-color cue pairs with a
valley below0.65 of the weaker endpoint. A support includes both radius2 endpoint
cores in1 pair for J/S/M/B/C and4 for A. This is a merger-warning proxy, not49
verified distinct-bead seams. Multiple cues can belong to one bead. M/B retain6
near-duplicate pairs (IoU≥0.5), versus J3, A5 and C5. False partition versus duplicate
physical ownership cannot be certified automatically from these photographs.

Boundary gradient is also a proxy: on ten anchors J averages0.0503 linearY/pixel,
M/B0.0343. J’s higher gradient can come from a highlight/core edge while excluding
valid diffuse red. We did not optimize this number. M/B retain100% of S anchor
material; J retains62.4% on average. That comparison is supporting evidence plus
photographic inspection, not an assumption that all S pixels are correct.

## Centerline evidence and remaining coverage gaps

Across the eight central crops, M/B have29 unflagged support-near proposals,
forming25 overlap groups under IoU≥0.5: per crop3,3,3,5,3,3,2,3 groups. These are
photographic groups, not certified physical beads, and crops span multiple stations.
The signed-support/arc-interval diagnostic finds three opposite-side flanking pairs
in C03/C04/C05. It does not enforce two or three at every station.

On the ten anchors, S/M/B provide five measured support-crossings versus J’s three;
all have eight near anchors. A/C add an apparent crossing partly through leakage,
so count increases alone are not improvement. The three original two-sided
observations remain individually represented. Uncertain/fresh observations are
retained, including all exclusions and stability reasons.

No claim of every crossing bead recovered is justified yet. Compact interiors can
miss a body’s crossing; black reflections cannot establish body extent. The sample
is deliberately central-heavy but is not a whole-photo census. Better marker
completeness is a necessary local improvement; reliable distinctness and complete
coverage remain unresolved.

## Mechanism controls and physical renders

Mathematical brightness fields independently test narrow bright continuation,
shallow shading and a deep valley. M retains the first two and separates the last.
**B incorrectly splits the shallow-shading control.** Its interface distribution
includes dim lateral interface pixels and can preserve a separation despite a
valid bright connection. This directly tests the concern that extra dark-boundary
sensitivity can reject genuine material. No parameter was changed to hide it.
Identical deep-seam and deep-internal-texture fields produce identical results;
no photograph-only method can infer different physical ownership from identical
pixels. A/C also truncate parts of the connected control through direct-path
visibility restrictions. See [controls](review/r286/mechanisms.png).

Four fresh seed286501 POV scenes use certified noninterpenetrating geometry,
varied illumination/specularity/pose, and41 automatically detected colored cues.
Identity truth is rendered/read only after saving inference. With the same870pixel
ceiling and ≥95% synthetic purity: J19/38pure, S/M16/22, A17/31, B18/27, C19/27.
Distinct eligible bodies recovered out of74: J17, S/M13, A15, B14, C17; duplicates
2/3/3/2/4/2 respectively. These weak results do not establish general ownership
reliability and do not override the actual-photo findings. Full renders, inputs,
certificates, inference, truth evaluation and failures remain saved.

## P6: black reflections remain unchanged

Replayed48 black features × R1/R2/R4: **all144 native masks, subpixel contours and
peaks match R285 exactly**. Upper-good and lower-secondary supports overlap0pixels
in every method. Keep R2 as the existing experimental default, with R1/R4 available;
the user considers them approximately equally acceptable. No dark-body collar,
physical outline or automatic assignment of the secondary reflection to a bead.
The old smoothness/brightness metrics and perturbations are carried forward in
[reflection stability](r286/results/reflection-stability.json).

## Recommendation, validation and stopping point

Prefer **M’s context-supported marker repair** as the smallest scientifically
supported next change. Preserve maxima based on their local material evidence,
without adding excluded peak pixels to the native mask or equating markers to
physical beads. Keep B as an unresolved alternative, not a global default after
its shallow-shading failure. Do not adopt A/C. Retain J for P1/P3 comparison and R2
for reflection-only measurements. Difficult edge discrepancies do not need to be
solved before consistently good central measurements.

91 scientific tests pass (17new +74historical). Exact full development and
confirmation reruns,31 exact original crops,10293 preserved historical blobs and
rendered desktop/narrow review are recorded in `r286/results`. See the
[reproduction instructions](R286_REPRODUCE.md), [checklist](R286_CHECKLIST.md), and
[six checkpoints](r286/checkpoints). Source and environment hashes are saved.

**Stop for user assessment.** If the user selects M, the next bounded task would
be to evaluate whether contextual markers plus independently supported seams can
reduce remaining central mergers without B’s internal-shading false splits.
That is a proposal only: no automatic R287, production replacement, global fitting
or pattern search. Keep current model/reasoning; no `/new` needed.
