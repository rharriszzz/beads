# R235 — four-section Stage 1 photographic pilot

**The pilot is complete; the automatic coverage criterion is not met.** Against
the provisional visual inventory, the frozen colored and black-reflection passes
cover **76 of 109 eligible beads**. The reviewed inventory supplies **33 assisted
additions**. Thirteen reference cases and seven detector proposals remain
unresolved. Six dark-body hypotheses without obvious reflections are deferred,
not detector misses. These are local photographic results, not whole-necklace
completion or independently established ground truth.

No reconstruction detector, geometry, physical-center estimator or indexing
algorithm was changed. The new script assembles frozen detector outputs, draws
review images and scores explicit visual associations. Global indexing and
repeating-pattern recovery have not begun.

## Eligibility and measurement conventions

The R235 user clarification governs this experiment:

- A distinct red/yellow bead qualifies when approximately 10% or more of its
  unobstructed projected area is visible and its visible pixels convincingly
  identify a separate bead and color. Small patches are included; an exact
  center or segmentation mask is unnecessary.
- A black bead qualifies through an obvious reflection with surrounding dark
  body evidence. No recognizable reflection means deferred, not missed.
- A colored interior point, useful representative location, visible-surface
  centroid, reflection and physical center are different quantities. The
  visible centroid and physical center are not inferred
  here. All `bead_index` values are null. No model-predicted beads are added.

Coordinates are native photograph pixels, x rightwards and y downwards, in the
2540×3182 source. EXIF orientation is 1. Each section has a 30px context halo;
its border does not physically occlude a bead. Eligibility uses the actual
visible surface including the halo. Section membership uses the frozen reference
representative inside the half-open box. Automatic representative locations can
therefore fall just outside the box when they belong to that same body.

Visible fractions are **rough heuristic ranges**, not measured masks or statistical
confidence intervals. Nearby broad faces set a local full-footprint width/height:
D3 28×34px, D4 32×30px, H1 32×29px, H4 29×33px. The protocol names the examples.
Visible width/height were estimated visually. Area ranges use 0.50–0.85 times
their product, divided by 0.65–1.05 times the neighboring full-footprint product,
clipped at 100%. These shape factors are uncalibrated assumptions allowing for
nonrectangular faces, holes, orientation and partial exposure. No fitted geometry
or camera justifies a more precise fraction. H1-B13 and H4-B06 remain uncertain
near the guideline. Fraction uncertainty does not silently delete a clear bead.

Representative marking tolerances of roughly 3px for clear observations and 6px
for uncertain ones describe where a mark can be placed on visible support;
they are not physical-center errors. A reflection can be much farther from a
physical center. Separate reference/interior/reflection fields and unestimated
centroid/center fields are retained in the [CSV](review/r235/observations.csv)
and [full report](review/r235/report.json).
Null reflection fields mean not separately measured, not proof of no reflection;
colored-bead glints were generally not measured separately.

## Sections and review artifacts

D3/D4 are development sections; H1/H4 are reserved from tuning. These are four
unchanged boxes from the earlier eight-box proposal. R234 did not specify a
four-box subset; this subset was declared before R235 detector-overlay evaluation.
Raw images had previously been inspected. “Reserved” means **no parameter tuning**,
not an unseen photograph or independent annotator. No tuning was performed on
either split, and no section was replaced.

| Section | Native box [x0,y0,x1,y1) | Enlarged original | Numbered reference | Automatic overlay | Reviewed detection overlay | Observation table |
| --- | --- | --- | --- | --- | --- | --- |
| D3, upper arc | [1210,225,1370,365) | [Raw](review/r235/D3-raw.png) | [Numbered](review/r235/D3-numbered.png) | [Automatic](review/r235/D3-automatic.png) | [Reviewed](review/r235/D3-reviewed.png) | [D3 table](review/r235/D3-observations.md) |
| D4, right bend | [1660,1540,1860,1740) | [Raw](review/r235/D4-raw.png) | [Numbered](review/r235/D4-numbered.png) | [Automatic](review/r235/D4-automatic.png) | [Reviewed](review/r235/D4-reviewed.png) | [D4 table](review/r235/D4-observations.md) |
| H1, left side, reserved | [135,1040,335,1240) | [Raw](review/r235/H1-raw.png) | [Numbered](review/r235/H1-numbered.png) | [Automatic](review/r235/H1-automatic.png) | [Reviewed](review/r235/H1-reviewed.png) | [H1 table](review/r235/H1-observations.md) |
| H4, lower arc, reserved | [1390,2910,1590,3110) | [Raw](review/r235/H4-raw.png) | [Numbered](review/r235/H4-numbered.png) | [Automatic](review/r235/H4-automatic.png) | [Reviewed](review/r235/H4-reviewed.png) | [H4 table](review/r235/H4-observations.md) |

All enlargements use original RGB pixels with nearest-neighbor scaling, without
sharpening, recoloring or generated detail. B numbers are stable observation IDs,
not string indices. P numbers identify automatic proposals; Q numbers identify
the five credited halo proposals. Reviewed circles have automatic support,
triangles are assisted additions, and squares are unresolved/deferred. Red and
yellow indicate those colors; cyan marks black for legibility. Unresolved extra
proposals D4-P03 and H1-P08 also appear in the reviewed overlay. The raw images
allow inspection without labels covering evidence.

## Frozen baseline, reference provenance and disclosed corrections

The automatic baseline uses all 599 R231 M4 colored proposals plus the 256 R192
dark-reflection records with successful native reflection/dark-surround evidence
(236 region proposals and 20 reflection-only proposals). Earlier excluded-edge
records are not silently reinstated. Color names label the photo's two learned
hue modes; no reference positions enter candidate assembly. These are cached
full-photo detector results with verified source hashes, not newly rerun detector
extraction. The pilot newly evaluates them under the revised eligibility rule.

The agent first annotated 127 raw-photo references and froze their input file
before inspecting candidate overlays. The labels are **provisional visual
interpretations by the same agent doing evaluation**, not maker confirmations
or independent ground truth. Ownership is assessed from the visible body and
its surroundings, not a nearest-center matching threshold. All 78 in-box
automatic candidates have an explicit decision and reason.

Two corrections were required after overlay inspection and are preserved in
[evaluation-amendments.json](review/r235/evaluation-amendments.json):

1. Five proposals on already annotated border-crossing bodies lie just outside
   the boxes. Credit D3-B20/B26, D4-B01/B04 and H4-B17 by visible same-body
   association. The complete [halo audit](review/r235/halo-audit.json) preserves
   the other nearby proposals as context. No detector point or box was moved.
2. Initial annotation missed one obvious reflection-supported black bead,
   H4-B34. It was added after reinspection, remains an automatic miss and is
   marked as a post-overlay assisted reference correction. This omission also
   demonstrates why the manual inventory cannot be claimed infallible.

The frozen inputs are untouched. The [original scoring](review/r235/frozen-score.json)
was 71/108 eligible bodies with 37 apparent misses. Boundary ownership credits
five detections; adding H4-B34 adds one eligible miss, yielding 76/109 and 33
misses. Both scores fail the completeness gate. The primary result below uses
bead ownership rather than the accidental placement of a point relative to a
crop boundary. The corrected annotated/automatic images include these amendments.

## Results

Counts are conditional on the reference interpretation. “Duplicate,” “false”
and “wrong color” below mean **confirmed** errors; zero does not establish their
absence among unresolved candidates.

| Section | Eligible | Correctly covered | Missed / assisted additions | Confirmed duplicates | Confirmed false positives | Confirmed wrong colors | Unresolved proposals | Uncertain references | Deferred black |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| D3 | 22 | 19 | 3 | 0 | 0 | 0 | 0 | 3 | 2 |
| D4 | 32 | 16 | 16 | 0 | 0 | 0 | 1 | 1 | 0 |
| H1, reserved | 27 | 20 | 7 | 0 | 0 | 0 | 3 | 4 | 3 |
| H4, reserved | 28 | 21 | 7 | 0 | 0 | 0 | 3 | 5 | 1 |
| Total | **109** | **76** | **33** | **0** | **0** | **0** | **7** | **13** | **6** |

Unresolved-proposal and uncertain-reference columns overlap and must not be
added to obtain a bead count. H4-B22 may contain one or two beads. The six deferred
entries are body hypotheses, not an established count of hidden black beads.

| Color / split | Eligible | Correctly covered | Missed |
| --- | ---: | ---: | ---: |
| Red | 29 | 24 | 5 |
| Yellow | 46 | 35 | 11 |
| Reflection-supported black | 34 | 17 | 17 |
| Development combined | 54 | 35 (64.8%) | 19 |
| Reserved combined | 55 | 41 (74.5%) | 14 |

The reviewed map accounts for each of the 109 eligible references once, with 76
automatic origins and 33 assisted additions. Ownership review itself was also
assisted. This is not a 100% accurate automatic detector, nor independent
validation of assisted completeness. All 13 uncertain references, six deferred
entries and seven unresolved proposals remain available for review. No proposal
was classified out of scope merely because it was difficult.

The omissions are not confined to tiny patches. D4-B02/B03/B05 are broad yellow
faces; D4-B24 is a broad red face; D4-B26 and H4-B34 have conspicuous reflections.
Small eligible side faces are also frequently missed. At least one specific
historical exclusion is visible: R192 record 585 at approximately (1697.1,1587.5)
falls on D4-B08's reflection but was excluded near the approximate search-band
edge. The R192 implementation applies that gate before native evidence extraction.
This supports auditing that gate; it does not establish that removing it repairs
all misses or avoids false positives. The pilot does not attribute every failure
to the same mechanism.

## Unresolved interpretations

The per-observation tables contain all cases. The main issues are:

- Color/identity: D3-B03, D4-B06, H1-B20/B25 and H4-B02 have shaded or pale pixels
  that do not establish a reliable color. D3-B27 might continue an adjacent body.
- Approximate 10% eligibility: H1-B13 and H4-B06 need a firmer visible-area/identity
  interpretation. They are retained, not called misses or successes.
- Reflection recognition: D3-B02, H1-B16 and H4-B24/B26 have weak features whose
  eligibility is uncertain. Definite no-reflection hypotheses are D3-B01/B05,
  H1-B05/B15/B34 and H4-B01, excluded from the miss denominator.
- H4-B22 has two nearby features whose one-body versus two-body interpretation
  remains open; H4-P20 supports a reflection, not a proven bead count.
- D4-P03 could be a separate shaded red body or another feature. H1-P08 could
  duplicate B11 or belong to a distinct shaded rear bead. Both survive as
  unresolved proposals. H1-P14's red label and H4-P01's red label are not accepted
  as verified colors. H1-P02 lacks an obvious reflection in the raw reference;
  H4-P03 belongs to the threshold-uncertain red patch.

These ambiguities do not change the conclusion that the baseline misses clear
bodies. No additional user image-processing question was needed to establish
that conclusion. The supplied numbered images make the remaining interpretations
reviewable without pretending that the reference is settled.

## Recommendation and stopping point

Retain the two-pass proposal approach and the assisted observation inventory.
The baseline is useful but inadequate as a complete map. This is evidence against
requiring its trusted seed at every bead, not evidence that image observations
are a dead end. Broad faces and recognizable reflections support additional
observations without perfect segmentation or a physical-center estimate.

**Stop for review before global indexing.** The immediate review should check the
numbered inventory, especially the ambiguous body counts/colors and the disclosed
reference correction. After review, use a vetted subset to design the bounded
local correspondence test already described in the strategy review: planar spline,
both helicities, competing counts/phases and explicit point-to-surface uncertainty.
An incomplete automatic detector need not prevent that test; the existence of
109 provisional observations does not prove they are sufficient to resolve it.
Continue whole-photo coverage work separately with uncertainty and assistance
visible. If further detector improvement is chosen, first audit old exclusion
gates and the measured D3/D4 omissions; do not require universal perfect segmentation.
H1/H4 must not be advertised as fresh holdouts after their failures inform tuning.

Later geometric predictions may direct searches for black beads without obvious
reflections, but only fresh photographic confirmation can promote predictions to
observations. Count, phase, local spacing/stretch, both helicities, loop closure
and consistent relative indices remain untested by this pilot. Repeating-color
recovery remains a separate later stage.

## Reproduction and validation

[Protocol](review/r235/protocol.json), [reference input](review/r235/reference-input.json),
[reference freeze](review/r235/reference-freeze.json), [adjudications](review/r235/adjudication.json)
and [summary/hashes](review/r235/summary.json) preserve inputs and decisions.
The photograph SHA-256 is
`eb7c9edb62f5580ef56632872da48da92556d62b758295137068cc2404dc8fbb`.
The executable is [stage1_pilot.py](stage1_pilot.py).

```bash
.venv/bin/python -m unittest photo2.test_stage1_pilot
.venv/bin/python photo2/stage1_pilot.py evaluate --output photo2/output/r235/reproduction
```

Five accounting tests pass: deferred/unknown handling, duplicates/wrong colors/
false positives, mandatory explicit adjudication, preservation of frozen inputs
under boundary amendments, and coordinate/threshold uncertainty. Reproduction
matches the 26 emitted files byte for byte. Images were visually inspected.
Tests check accounting and reproducibility, not whether an agent's visual label
is scientifically correct. Source detector payloads, original photograph and
the user's untracked screenshot remain unchanged.
