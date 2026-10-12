# R264 — fixed hue comparison and coordinate review

**Recommend 8° provisionally, with 10° and 12° retained as alternatives.** This is a
photographic tradeoff, not selection against an expected bead count. The unchanged
R263 detector's historical default remains 10°; the saved recommended run opens at
[localhost:8767/?hue=8](http://localhost:8767/?hue=8). Open **Compare six hue settings**
in the simple viewer, or [the comparison page](http://localhost:8767/hue-comparison).
Restart an existing server after updating. [Evidence index](review/r264/README.md).

8° keeps the upper red body P013502 at (1342,276), which 10°–20° reject on the hard
pre-retreat ceiling. It supplies compact on-body coordinates in the reviewed red,
yellow and reflected-dark examples, without the severe thinning at 5°. It also
avoids the measured encroachment of wider settings into a small visually judged
paper window. This does **not** mean 8° resolves background rejection or identities.
12° is a useful alternative for P090697's yellow interior; 10° remains a reasonable
middle alternative where 8° leaves a thin rim. No per-bead adaptive hue rule was
introduced, and all six full results remain available.

## Controlled experiment

Only `hue_stop_deg` changes: 5, 8, 10, 12, 15, 20. Fixed: prominence 35 DN,
minimum peak 0, rise allowance 0 (equality allowed), maximum 870 distinct accepted
native pixels **before retreat**, retreat fraction .30 and minimum retreat 2 DN,
patch drop 10 DN, dark 81 DN, reflection drop 36 DN, saturation reliability .35,
saturation drop .40, minimum-support flag 3, border fraction .035. Complete
parameters/source hashes are in each run's summary. The detector source is unchanged.

No blur, interpolated sampling, watershed, replacement ownership partition, new
seed selection, bead merging, geometry, indexing or pattern inference. The 871st
eligible pixel rejects a proposal and preserves pending stop edges. The reported
minimum support is a flag, not a new hard minimum rejection. Independent maxima
still grow and can overlap. Hue is circular displacement from the first reliable
chromatic pixel on a predecessor path; it is not a material classification.

Four complementary reviews were selected: full-photo coordinate/overlap sensitivity,
matched photographic crops, explicit local visual identity/coverage judgments, and
an isolated leaf-retreat sensitivity control. Six main crops cover the requested
failures and bright/shadowed red/yellow material. Three additional stress crops
show the largest coordinate movement, paper risk and another yellow-coordinate
movement. Diagnostic landmarks enter evaluation only, never detection.

## Measurements across the photograph

| Hue | Retained supports | Size-limit rejections | Supports with any overlap | Supports in IoU > .5 groups | Excess supports in those groups |
|---:|---:|---:|---:|---:|---:|
| 5° | 1,551 | 0 | 544 | 196 | 102 |
| 8° | 1,556 | 1 | 644 | 298 | 162 |
| 10° | 1,552 | 5 | 695 | 344 | 187 |
| 12° | 1,540 | 18 | 729 | 364 | 200 |
| 15° | 1,524 | 36 | 756 | 407 | 224 |
| 20° | 1,496 | 64 | 772 | 429 | 236 |

These are **measured support relationships, not measured bead identities**. Build
an edge for intersection/union > .5; the last column sums component size minus
one. A connected component need not be a single bead. Small disjoint supports can
also duplicate a bead, so low overlap is not evidence of low duplicate incidence.
Exact pair intersections and group membership are saved, with no merger applied.

Among common IDs, supported-coordinate movement relative to 10° has median/p90
1.00/4.24 px at 5°, 0/2.24 at 8°, 0/2.00 at 12°, 1.00/3.61 at 15°, and 1.00/4.47
at 20°. Respectively 99, 24, 19, 64 and 125 coordinates move more than 5 pixels.
These measure sensitivity, not coordinate error. At 8°, all 1,552 baseline IDs
survive and four additional IDs survive. Retaining more IDs was not the objective.

The largest movement relative to 10° is P074702: (924,1560) → (942,1561) at 12°,
18.03 px. Both points appear on the same yellow body; a large displacement alone
is not background contamination. [Identical crops](review/r264/largest-shift.png).
P097805 similarly shifts from a thin left rim toward the yellow interior at 12°.
[Yellow alternative](review/r264/yellow-shift.png). These cases prevent choosing
only by minimum movement or area.

In the [paper-risk crop](review/r264/paper-risk.png), the review window
x=1992..1997, y=2628..2634 is visually paper-dominated exterior next to a red bead.
It contains 0, 0, 1, 3, 8, 8 retained P126974 pixels across the six settings.
Membership is exact; identifying this window as paper is an assistant judgment,
not a verified boundary segmentation. Wider settings visibly extend farther along
this bead/paper transition. All settings still contain suspicious edge proposals;
this is not a whole-photo contamination rate. No known palette box was used.

## Local duplicate and missing-location review

[Annotated review landmarks](review/r264/visual-review.png) ·
[every identity judgment and seed diagnostic](review/r264/visual-review.json).

Across the **six main purposively selected crops**, 12 likely same-body pairs
persist at **every setting**: 24 participating regions, or **12 apparent extra
regions** if those pairwise identity judgments are correct. The inventory includes
partly cropped but substantial red patches, the requested red pair, two yellow
pairs around R01284, and a repeated reflection near R01307. It is an explicit
reviewed subset, not a complete census of every region in those crops or the photo.
The three stress crops are not added to this visual tally.

| Hue | Stronger plausible missed locations | Additional tentative location |
|---|---:|---:|
| 5°, 8° | 4 | 1 |
| 10°, 12°, 15°, 20° | 5 | 1 |

M1 (2255,1919): lower yellow in R00956. M2 (1005,2678): shadowed yellow right of
R01284. M3 (1929,2712): pale upper colored body in R01307; color uncertain.
M4 (1920,2761): lower yellow in R01307. M5 (1601,1445): tentative separate
shadowed red-looking body in the inner transition. M6 (1342,276): upper red
P013502 lost only at 10° and above. Coordinates here are approximate **review
landmarks**, not accepted detector outputs or inferred physical centers.

The four nearest raw maxima to each of M1–M5 fail prominence 35; this supports a
seed-selection bottleneck, not a hue-only explanation. It does not prove every
possible source peak for each body is absent. M6's retained/rejected status and
size-limit reason are exact. No prominence change was tested in this step.

P091744 on the middle R00956 yellow is counted as **detected but weak**: its point
is on the left rim, not in the middle of the body. [Q264.1](HUE_REVIEW_QUESTIONS_R264.md)
asks whether this is usable; no maker answer has been received. Counting that rim
as unusable would add one miss at every setting without changing the relative hue
ranking. Dark regions without a clear reflection remain deferred, not declared
misses. There is **no defensible whole-photo missing-bead count or recall estimate**
from these selected crops, and these local counts are not extrapolated.

## Named failures and bright/shadowed color evidence

- **R00956:** P091744 remains a left-rim support, from (2261,1903) at 5° to
  (2260,1898) at 20°. None of the six settings recovers M1 below it. P090697 above
  it changes from (2279,1879), 41 pixels at 10°, to (2288,1880), 126 pixels at 12°;
  visually that moves into the yellow body. 12° is a credible local alternative,
  not a repair of R00956's missing location. [All six](review/r264/R00956.png).
- **R01284:** P128275/P128915 remain two plausible supports of the same yellow
  body at all settings, even when their masks barely overlap at 5°. At 8° their
  points are (979,2664)/(983,2671); at 20°, (981,2663)/(984,2670). The lower yellow
  also has two supports. Shadowed yellow M2 remains missed. [All six](review/r264/R01284.png).
- **P032240/P032353:** points are (484,669)/(481,669) at 5°, (485,669)/(483,670)
  at 8°, and both (485,669) from 10° onward. The central red body still has two
  proposals. Tightening hue does not remove the duplicate. [All six](review/r264/pair.png).
- **R01307:** compact yellow support stays plausible, but M3/M4 remain unrepresented
  and a neighboring dark reflection is duplicated. [All six](review/r264/R01307.png).

[Top illuminated transition](review/r264/top-transition.png) and
[inner mixed-light transition](review/r264/inner-transition.png) show identical
source crops in every panel. Highlights are not interpreted as boundaries.

[Native HSV paths](review/r264/hsv-routes.png) begin with raw context and annotated
interior endpoints. Two short routes stay within visually identified red/yellow
bodies, from brighter to darker surface; a third crosses from a shadowed red-looking
patch toward yellow and explicitly includes intervening boundary/gap pixels.
Integer Bresenham steps visit adjacent native pixels; no interpolation or averaging.
These are diagnostic routes, **not growth predecessor paths**. Exact samples are
in [CSV](review/r264/hsv-routes.csv).

The red interior changes H 352.88° → 354.43°, S .498 → .838, V .929 → .655.
The yellow interior changes H 44.48° → 25.23°, S .591 → .912, V .949 → .757:
a **19.25° within-bead hue change**. Circular red/yellow separation between the
brighter endpoints is 51.59°, versus 30.80° between the darker endpoints. This
small selected example supports the maker's observation that their appearances
can converge under shading; it is not a calibrated illumination experiment or a
universal color rule. Even 15° can stop within a yellow body. A hue stop is evidence
for limiting a support, **not proof of a physical bead boundary**. It is acceptable
for a compact support to omit those pixels if the coordinate still identifies the
body reliably. HSV at coordinates and circular support percentiles are also shown
in the viewer; these percentiles are not growth-anchor measurements.

## Predecessor-tree leaf retreat affects coordinates

For a non-peak accepted leaf with no terminal dark-frontier evidence, the current
propagated floor equals its own value v. Its threshold is
`v + max(2, .30*(peak-v))`, so `v > threshold` is impossible. The leaf is removed
regardless of whether it is still a bright interior pixel. Tree topology depends
on first-queued predecessor/tie order; this is not a physical darkness test.
Its consequences include ragged supports and removed bright interior samples.

The diagnostic control restores only such removed terminal leaves whose **original
parent survives** and whose value exceeds that parent's original retreat threshold.
Leaves with explicit dark-frontier stops stay removed; removed internal branches
stay removed. It changes no accepted growth pixels, predecessors, stops, maxima,
limits or ownership. This conservative control is **not a validated retreat repair**,
and does not expose every consequence of the defect. Production results remain
unchanged. A broader fix needs its own bounded comparison.

| Hue | Supports with restored leaves | Changed supported coordinates | Largest coordinate movement |
|---:|---:|---:|---:|
| 5° | 1,505 | 682 | 7.07 px |
| 8° | 1,515 | 684 | 7.00 px |
| 10° | 1,505 | 634 | 5.66 px |
| 12° | 1,492 | 619 | 5.66 px |
| 15° | 1,478 | 596 | 6.08 px |
| 20° | 1,451 | 618 | 6.08 px |

At 8°, P019077 moves (817,395) → (817,388) even though its area centroid moves only
0.61 px: the chosen coordinate is the nearest **retained native pixel** to the
centroid, so restoring candidates can change that discrete choice considerably.
P032353 moves (483,670) → (484,669); P032240, P091744, P128275 and P128915 do not
move under this control, though their masks/centroids change. The control therefore
does not repair R00956's rim coordinate or resolve the named duplicate identities.
[Original versus control](review/r264/leaf-coordinate-control.png) ·
[all measured changes, including total retreat versus pre-retreat](review/r264/leaf-control.json).
These are sensitivity movements, never measured physical-center errors.

## Validation, delivery and stopping point

43 preserved detector tests plus two targeted leaf-control tests pass. Six complete
native audits check 2,565,649 accepted pixels and 3,079,032 stopped edges, including
raw HSV, eight-neighbor predecessors, irreversible stops, cap rejection, retreat,
centroids, supported coordinates, overlap memberships and all maxima. The fresh
10° generation matches the delivered R263 generation `90b4284f50a29ced`. The 8°
run also has an isolated source/photo replay check. Browser verification covers
60 comparison/run-specific checks plus 41 existing viewer checks. All six maxima
catalogs, rejected candidates, exact regions and 1,595 traces per run are archived.
[Reproduction commands and hashes](review/r264/README.md).

Stop at this scoped commit/push. Next proposed bounded task: compare explicit
retreat repairs for coordinate stability, with the named failures as held-out
review cases; separately plan seed/duplicate association work afterward. Do not
quietly couple either change to hue or introduce an ownership partition. Continue
with GPT-6 Astra / High for the next visual-inference review (recommendation only;
no new model status is inferred). No `/new` needed to review these artifacts; use
`/new` before another substantial algorithm experiment. No geometry, indexing or
pattern work was resumed.
