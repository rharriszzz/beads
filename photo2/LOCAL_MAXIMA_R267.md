# R267 — local maxima before region growth

**Better foreground candidates were excluded before R266's ranking. Neighborhood
averages help expose them, but the tested selector does not yet reliably preserve
adjacent beads. No production detector or previous result was changed.** Changing
only the seed also fails to remove R01284's irregular support. This audit stops at
that evidence; it does not optimize outlines or reopen background separation.

Start with the photographs and their numbered tables:

| Crop | Original / old seeds / average candidates | Every maximum, numbered by pixel | Table |
|---|---|---|---|
| R00956 | [Comparison](review/r267/R00956-comparison.png) | [7×7 ranking](review/r267/R00956-all-square7.png) | [All 160 pixels](review/r267/R00956-TABLE.md) |
| R01284 | [Comparison](review/r267/R01284-comparison.png) | [7×7 ranking](review/r267/R01284-all-square7.png) | [All 138 pixels](review/r267/R01284-TABLE.md) |

The comparison overview deliberately includes the **ungated** average control.
Following the user's steering, the relevant candidate views hold the established
R266 background treatment fixed: [R00956](review/r267/R00956-fixed-background-square7.png)
and [R01284](review/r267/R01284-fixed-background-square7.png).
Background is an independent established input, not something an average must
solve. FFT/standard deviation could supply that evidence, as the user notes;
no new background method or threshold search was performed here.

## What was measured

Use the EXIF-oriented original JPEG, 2540×3182 native pixels; origin top left,
x right, y down. V is **max(R,G,B)** in 0–255 DN, without blur, resampling,
white-balance changes or linear-light conversion. H is circular degrees; S is
0–1. The existing 81×81 review boxes select evidence only, not detector inputs.

An eight-connected *regional maximum* is an equal-V plateau with no brighter
neighbor on its boundary. Compute this over the **whole photograph**, before
cropping, and compare it with the saved R266 inventory. The masks match exactly.
Preserve **every plateau pixel**, not just R266's nearest-to-plateau-centroid seed:

- R00956: **127 plateaus / 160 maximum pixels**.
- R01284: **114 intersecting plateaus / 138 maximum pixels**. One plateau's old
  representative lies outside the crop; filtering only by representative would
  incorrectly report 113 / 137 and omit its in-crop pixel.

Each numbered pixel has six independent measurements/rankings: square 5×5, 7×7,
9×9 (25/49/81 samples); Euclidean disks of radius 2/3/4 (13/29/49 samples), including
the central pixel. Neighborhoods use the full photograph beyond crop boundaries.
All samples receive equal weight, including any background samples. Tied means
share a competition rank; pixel number is stable raster order, never bead identity.
The six annotated maps use rank-percentile colors and collision-checked labels.
Native and enlarged unmarked originals are saved separately.

Prominence is now an **exact integer topographic drop** to the highest superlevel
connection containing a strictly higher pixel. Connected superlevel tests expand
beyond the crop until no unexamined outside path could change the answer. This
computes a saddle statistic, not watershed regions or bead ownership. Equal global
maxima use full-image dynamic range, matching h-maxima. Saved R266 prominence
values were only tested lower bounds (0, recovery threshold or 35), and are
preserved separately. All 1,446 crop-plateau × run prominence-gate checks agree.

[Complete evidence index](review/r267/README.md) includes every raw peak V, H/S,
exact prominence, six means/ranks, original plateau, old representative, current
status and rejection/suppression reason. Both straight and annular variants at
12/6/3-DN recovery are preserved in the status ledger. No foreground candidate
is removed from the all-maxima rankings.

## Why R266 made these choices

The exact order is:

1. Require raw h-prominence ≥12 DN (or 6/3 in sensitivity variants). Lower-prominence
   maxima **never reach the neighborhood score**, however good their average.
2. Apply existing seed/background checks; grow a support; apply paper, size and
   recovery-support deferrals. In particular, a recovered support below 12 pixels
   is deferred before final competition.
3. Among remaining candidates, sort by this mixed score:

   `0.04 peakV + 0.08 min(prominence_lower_bound,60) + 0.20 median7 + 0.25 p25_7 + 0.04 min(area,150) + 60 area/perimeter²`.

   This uses a **median and lower quartile, not neighborhood mean**. It also uses
   grown-region area/compactness; it is not a pre-growth selector. The prominence
   term changes with the tested threshold, rather than using exact prominence.
4. Greedily suppress a lower-score eligible candidate within 18 pixels only when
   a direct five-pixel ribbon passes the existing brightness/gradual-color tests.
   No transitive grouping is required. An earlier selected compatible winner can
   prevent a later candidate from competing. There is no edge-distance criterion.

[Why each selected maximum survived](review/r267/SELECTION_EXPLANATIONS.md) covers
**213 selected records across all six variants**, including exact score terms,
losing IDs/scores, seed and displayed coordinate. The displayed white coordinate
is the supported pixel nearest the area centroid; it is often **not the seed**.
For example, P090697 grows from (2279,1879), but displays (2278,1879).

There is also a saved-metadata defect: some final retained maxima still carry an
old `inferior-quality-maximum` reason from the earlier association pass. R266
reset the region's bright-patch reason but did not reset the separate maxima
record's reason when re-synchronizing retained entries. The audit flags these
stale strings and uses final membership/status and suppressor records to explain
actual decisions. It preserves the original strings and detector unchanged.

## Photographic candidates and neighborhood sensitivity

These are positional photographic descriptions, **not manually assigned bead
identities or a segmentation used by the experiment**. Numbers refer to the full
maps. The quantitative comparison uses direct R266-compatible candidates within
18 pixels, retaining every alternative; the shadowed-neighbor counterexample below
shows why this neighborhood must not be called a verified bead group.

| Apparent location | R266 selected12 seed | Higher-average candidate / result | Why overlooked |
|---|---|---|---|
| R00956 upper yellow | #32 P090697; mean7 230.37 | #34 P090766 (2289,1880); 239.88; 10.05px move toward interior | Exact prominence **1**, excluded before scoring |
| R00956 middle yellow | P091868 (2275,1903); 235.35 | #71 P091694 (2262,1899); 239.63 | Prominence **2**, excluded; this mean favors the left bright patch, not necessarily the body center |
| R00956 lower yellow | P093030 (2262,1926); 232.27 | #112 P092706 (2252,1919); 242.90 | Prominence **10**, below 12; all six averages favor this paper-facing patch within the tested neighborhood, so averaging does **not** guarantee an interior coordinate |
| R01284 central yellow | #77 P128915; 229.76 | #73 P128672 (981,2671); **240.12** | Prominence **2**, rejected even at the saved 3-DN setting |
| R01284 lower yellow | #122 P130055; **235.76** | Same #122 wins mean7/disk4; #110 wins mean9 | Current choice is already competitive; do not replace it just because another raw peak is higher |
| R01284 shadowed yellow at right | #83 P129034; 156.80 | #89 P129155 has 153.88; exact per-body winner remains uncertain | Direct-compatible search instead jumps to #67 on the brighter adjacent yellow; invalid evidence for improvement |
| R01284 upper red patch | #12 P127000; 167.69 | #13 P127001; 180.65, favored by all six averages | Prominence **3**, rejected at 12/6 |
| R01284 upper-left reflection | P127764 (951,2652); 172.63 | #39 P127837 (951,2654); 183.88 | Prominence 14 passes, but **weak-recovery-support** defers its 10-pixel support |

The small scales do not uniformly improve the yellow choices. For the upper
R00956 yellow, square5/disk2 favor #33, another pixel of the **existing edge
plateau**, disk3 favors #24 P090532, and square7/9/disk4 favor #34. For R01284's
central yellow, five methods choose #73 but disk2 retains #77. For its lower
yellow, square5/disk2/disk3 prefer the lower-rim #128 P130260; square9 favors
#110 P129826, while square7/disk4 retain #122. All six independent numerical
rankings and coordinate controls are saved; no scale was selected by bead count.

The other obvious reflection patches are retained in the comparison: R00956
upper-left #22, left-middle plateau's #63, upper-right #65 and bottom #144 remain
local mean7 representatives; the lower-right reflection shifts to #110 by 3.16px.
R01284's left-edge #90 and bottom #133 stay. R00956's clipped bottom-right red
plateau shifts to #153 by 3px. Cropped yellow/red areas at the top/bottom and the
faint dark-region maxima remain in the all-maxima maps and halo competition;
there is insufficient in-crop body evidence to assert a unique bead or a center
for each. The clipped upper-left R01284 red maximum #2 has an outside-crop winner.
No current seed, including the dark-region extras, is treated as a confirmed bead.

**The 6-DN R266 version is different and was also audited.** Its upper yellow
#24 P090532 survives with score 122.397 versus 121.611 for the suppressed edge
P090697. It still cannot consider #34 (prominence 1). On the middle yellow,
P091867 wins with score 123.915 over P091591 (122.015) and P091592 (122.893), despite
the latter interior alternatives' higher mean7. The mixed median/quartile/support
score explains this, not a direct comparison of arithmetic means. P091694 is
still excluded at prominence 2. The lower yellow's paper-facing P092706 is already
selected at 6 DN. Thus the user's edge concern is not resolved merely by changing
12 to 6. [Selected6 R00956](review/r267/R00956-straight-0-selected6-seeds.png).

## Foreground selection and the adjacent-neighbor test

Run each arithmetic mean as the sole competition score, selecting the best native
pixel of each raw plateau. Keep the existing 18-pixel direct bridge test fixed;
use a 36-pixel context halo and retain all selected/suppressed evidence. This is
an offline diagnostic, not an adopted detector. Neither expected count nor manual
bead membership enters it. The all-maxima and fixed-background variants remain
separate, so background evidence is not silently replaced by brightness.

The fixed-background control reuses the existing learned margin HSV/texture model,
obvious-paper seed test, nearby smooth-paper uncertainty and already recorded
paper deferrals. It introduces no new thresholds. Region-fraction evidence is
reused only where recorded; no nonexistent pre-growth support is invented. It
retains 117/160 maximum pixels in R00956 and 138/138 in R01284 for competition.
At mean7, 38/63 candidates survive: these include weak/dark local maxima and are
**not bead counts**. Removing prominence/growth eligibility naturally exposes
those alternatives; the test does not certify all of them as beads.

The clearer yellow candidates above remain useful with background held fixed.
The obstacle to adopting this selector is **local identity/association**, not a
requirement that averaging solve background:

[Photographic neighbor-failure witness](review/r267/R01284-neighbor-failure.png)
shows P129034 (994,2678) being attracted to P128549 (983,2668), visibly on the
brighter adjacent area. Mean7 rises 156.80→234.49 and distance is 14.87px. The
existing rule accepts bridge minimum 158 DN, ribbon tenth percentile 162.5 DN,
hue p90 17.90°, hue-step p95 4.03° and saturation range .217. These values satisfy
its thresholds despite crossing the apparent boundary. All six direct-average
controls make this same unsafe relocation. The independent greedy mean7 run
happens to retain P129034 because a different brighter candidate wins first;
that ordering accident does not establish safe neighbor separation. No beads or
masks were actually merged in this audit.

## Added steering — hue alone and discard small ambiguous regions

The user also states that hue alone can distinguish background in this photograph
and instructs us to discard small ambiguous regions. **The revised candidate
views exclude supports below 12 distinct native pixels**, using the existing
R266 recovery cutoff as the operational minimum. This is a size decision for
ambiguous supports, not a claim about physical bead size. All rejected maxima
remain in the complete rankings and exclusion ledger.

[Fixed background + size filter: R00956](review/r267/R00956-fixed-background-size12-square7.png) ·
[R01284](review/r267/R01284-fixed-background-size12-square7.png).
These are the recommended final candidate-review views. At mean7, the filter
excludes 10/16 small candidate supports before association in the two crops;
29/51 candidates survive subsequent competition. These are not verified beads.
The key P090766/P091694/P092706/P128672 candidates survive with supports of
14/20/51/49 native pixels. The brighter R01284 reflection P127837 has only
10 pixels and is now discarded from these candidate views, as requested.

[Hue alone + same size filter: R00956](review/r267/R00956-hue-only-size12-square7.png) ·
[R01284](review/r267/R01284-hue-only-size12-square7.png).
This separate control uses only circular hue distance from the **already learned**
paper center 312.21°, with the existing 30° uncertainty half-band. It does not
introduce an FFT, standard-deviation classifier, learned palette box or new hue
search. It yields 23/34 mean7 candidates after the same size cutoff and association.

That literal broad-band control also removes visible left-side reflection maxima
in R01284: P127837 has H339.2°, and P129209 has H332.4° (the latter has a 25-pixel
support). This is a limitation of transferring this particular uncertainty band
into a hard hue-only gate; it does **not** establish that a carefully chosen
photo-specific hue treatment cannot separate background. Keep the established
background version alongside it and do not silently adopt the literal band.
Background separation remains outside the next requested seed-selection aspect.

The exclusion ledger records hue, circular paper-hue distance, support size and
reason for every tested candidate. The additional support-size check reuses
preserved masks where available and otherwise replays the same frozen growth
(509 seed replays including the context halos and six-scale plateau alternatives).
No growth threshold, outline rule or production selection method was changed.

## Do the starting points explain the irregular support?

Only **after saving the initial rankings**, replay unchanged strict straight
R266 growth from the old seeds and the six direct-compatible alternatives. Same
photograph, background map, valleys, hue10°, first-dark/retreat rules and 870 cap.
No parameter search, smoothing, annular optimization or new region rule.
Twenty-five available original masks reproduce exactly; 43 distinct seeds yield
132 old/new metric comparisons. Preserve native masks and stop-reason counts.

[Freeze-growth R00956](review/r267/R00956-frozen-growth.png) ·
[Freeze-growth R01284](review/r267/R01284-frozen-growth.png).

| Seed change, mean7 | Support pixels before→after | Boundary-pixel/area before→after |
|---|---:|---:|
| R00956 upper yellow P090697→P090766 | 63→14 | .524→.786 |
| R00956 middle yellow P091868→P091694 | 54→20 | .611→.700 |
| R00956 lower yellow P093030→P092706 | 142→51 | .465→.627 |
| R01284 central yellow P128915→P128672 | 98→49 | .520→.694 |
| R01284 lower yellow P130055 unchanged | 21→21 | .714→.714 |

These are support-shape statistics, not physical-boundary accuracy. A smaller
support can look simpler without being a better bead outline. At the improved
R01284 central seed, the replay still records 78 brightness-rise, 22 local-valley,
44 blocked-prefix, 16 corner and 4 hue stops. Raw native variations and the
unchanged strict stopping rules remain influential. Better starting coordinates
are worth retaining, but **poor starting points are not the sole explanation**
for irregularity. The direct-neighbor relocation can even look numerically more
compact while being photographically wrong; shape score is not identity evidence.

## Verification, reproduction and stopping point

Four numerical tests cover exact neighborhood sums, disk sample counts, tied
ranks/overflow, prominence versus h-maxima and adaptive boundary certification.
Photographic checks independently verify the raw-maxima mask, 1,446 prominence
gates, 213 original score sums, 25 exact original mask replays and nonoverlapping
labels. Frozen inputs and every curated output are hashed. No old detector,
review artifact or viewer was edited. No simulated bead positions, watershed,
old spline, manually assigned bead identities, geometry or indexing was used.

```sh
MPLCONFIGDIR=/tmp/beads-r267-mpl .venv/bin/python -m photo2.bead_detection.audit_r267
MPLCONFIGDIR=/tmp/beads-r267-mpl .venv/bin/python -m photo2.bead_detection.compare_r267
MPLCONFIGDIR=/tmp/beads-r267-mpl .venv/bin/python -m photo2.bead_detection.document_r267
MPLCONFIGDIR=/tmp/beads-r267-mpl .venv/bin/python -m photo2.bead_detection.background_control_r267
MPLCONFIGDIR=/tmp/beads-r267-mpl .venv/bin/python -m photo2.bead_detection.hue_size_control_r267
MPLCONFIGDIR=/tmp/beads-r267-mpl .venv/bin/python -m unittest photo2.bead_detection.test_audit_r267 > photo2/review/r267/tests.log 2>&1
MPLCONFIGDIR=/tmp/beads-r267-mpl .venv/bin/python -m photo2.bead_detection.validate_r267
```

**Stop after delivery.** The concrete next task, only when requested, is a
pre-growth selector that retains these low-prominence interior alternatives and
tests direct adjacent-bead separation with the established background fixed.
Do not resume outline optimization. Keep the user's current model/reasoning;
no `/new` is needed to review the saved photographic evidence.
