# Photo 2: checking the width correction against visible edges — R066

The twelve-location review supports the main shadow correction, but does not
establish an accurate boundary everywhere. The width-constrained candidate is
more compatible with assistant-estimated visible edge ranges than the original
curve. Keep it provisional: some small disagreements remain, and the ranges are
subjective image observations rather than maker labels or physical ground truth.

[Open the committed review](review/r066/review.html),
[location map](review/r066/locations.png), or
[questions with supporting images](QUESTIONS_FOR_MAKER.md).

## What was measured

Selected twelve positions across the top, bottom, sides, bends and return loop
before reading their predicted offsets. Selection intentionally covers difficult
areas; it is not a random sample. At each location, a strip perpendicular to the
saved centerline shows offsets −90 to +90 pixels, with ±28 pixels along the
rope for context. Images display at four times the original size using bilinear
sampling. Left always means outer side, right inner side, regardless of the
strip's orientation in the photograph. Side ticks mark the exact transect.

The assistant first inspected the three **raw** sheets without edge overlays,
recorded plausible outer/inner transition intervals at the central transect in
[transect-annotations-r066.json](transect-annotations-r066.json), and only then
read the original/corrected offsets. Earlier whole-image corrections were already
known: this is not observer-blind or independent human validation. Hashes bind
the annotation file to the photograph and raw sheets. Intervals were not adjusted
after inspecting the comparisons. They describe visible bead scallops at each
cross section, not an independently fitted smooth rope envelope.

A prediction inside a visual interval gets zero distance; otherwise the score
is its distance to the nearest interval endpoint. This is **distance outside a
plausible range**, not true boundary error. The midpoint interval comes from the
midpoints of all possible outer/inner endpoint combinations; it is a silhouette
midpoint, not a calibrated physical rope axis.

| Check on the selected transects | Original | Width-constrained |
| --- | ---: | ---: |
| Edges inside the visual ranges | 12 / 24 | 14 / 24 |
| Edges inside or within 2 pixels of the ranges | 18 / 24 | 23 / 24 |
| Mean distance outside the edge ranges | 1.71 px | 0.49 px |
| Largest distance outside an edge range | 11.27 px | 2.40 px |
| Centers inside the visual midpoint ranges | 8 / 12 | 11 / 12 |

The two-pixel comparison exposes sensitivity to small visual/rounding differences;
it is not an adopted accuracy requirement. Many intervals are wide, especially
for dark beads and blurred/shadowed transitions. These counts cannot establish
performance elsewhere on the necklace.

## Where it helps and where it still disagrees

All coordinates and distances use the original 2540×3182 photograph.

| Transect | Location | Original shadow-side distance outside range | Corrected distance outside range | Interpretation |
| --- | --- | ---: | ---: | --- |
| D | Left bend, (247, 1056) | 6.94 px | 0 | Correction agrees with the broad visual range. |
| E | Left bend, (243, 1356) | 11.27 px | 2.40 px | Improvement, but the inner edge may still be too far into shadow. |
| H | Lower loop, (995, 2717) | 8.15 px | 0 | Correction agrees with the visual range. |
| C | Upper-left slope, (565, 590) | 2.37 px outward | 1.79 px inward | Candidate crosses the range and may cut into a bead. |
| G | Lower loop, (933, 2479) | 3.50 px | 1.58 px | Small residual outward discrepancy. |
| I | Bottom-left, (1373, 3010) | 3.66 px | 0.86 px | Small residual outward discrepancy. |

At C the original center is inside the visual midpoint range, while the corrected
center is 1.32 pixels beyond it. This is a local caution against automatic
adoption, not proof of a true error at that precision. On the right (K/L), both
original and corrected edges lie within the broad visual ranges: this check
cannot choose between them.

There are fourteen edges labeled clear by the earlier exterior-brightness rule.
Six lie outside these visual intervals, all by less than 1.64 pixels. Two differ
by less than 0.1 pixel and should not be treated as meaningful failures. The
larger discrepancies at C/D/F/H are still small relative to blur and subjective
annotation. They illustrate why brightness outside an edge cannot itself certify
the boundary position. In particular, F passes both-clear selection even though
its saved outer curve may miss a small visible scallop. A future fit should allow
uncertainty on the nominally clear side as well.

## Width and perspective

The fitted 95.8-pixel width lies inside all twelve visually derived width ranges.
For example, top A/B span 86–103 and 90–104 pixels, middle F spans 89–102, and
bottom J spans 90–112. These broad overlapping ranges do not resolve a camera
perspective gradient. No new slope or revised width is fitted to these twelve
observations; no correction parameter has been tuned to them.

Use width as a smooth prior, with direct bead-to-paper transition evidence on
both sides. The current practice of treating a brightness-qualified edge as a
perfect fixed anchor is a useful initial approximation, not an accuracy claim.
Retain original geometry and candidate curves separately.

## Reproduce and checks

```sh
.venv/bin/python photo2/transect_review.py \
  --output photo2/review/r066 \
  --annotations photo2/transect-annotations-r066.json
.venv/bin/python -m unittest discover -s photo2 -p test_transect_review.py -v
.venv/bin/python -m unittest discover -s photo2 -p test_width_correction.py -v
```

The committed bundle has three raw sheets, three comparison sheets, a location
map, HTML review and JSON report. Source/photo/annotation/artifact hashes and
exact sampled coordinates are retained. A second output-directory run reproduces
all eight image/HTML artifacts byte for byte; reports match except command paths.
Seven source hashes verify. Report SHA256:
`6b2b9ea31bc095e69e20b884eb0c5a17e51e243c7938b6039b30e035b7046ba2`.

Four new controls pass for interval scoring/invalid inputs, width/midpoint
interval propagation, normal/tangent coordinate sampling, rotation and out-of-frame
sampling. The existing nine width controls also pass; compilation passes. Sample
axes are orthonormal, and reproduced candidate offsets match R065 measurements
to 1e-10 pixel. Raw/annotated sheets and location map were visually inspected.
No source-pattern lookup, bead detection, new render or full legacy regression.
Original spline data, width-correction algorithm and reconstruction defaults
are unchanged. Bulk duplicate outputs remain ignored.

## Next bounded task

Test direct image evidence for bead-to-paper transitions on both edges, keeping
width as a soft prior rather than a fixed target. Evaluate against these frozen
intervals without fitting to them; include the C/E residuals and clear-edge
scallops. Stop after a comparison of original, width-only and image-guided
candidates, before globally adopting new geometry or proceeding to bead indices.
Maker answers can refine the review if supplied, but are not an approval gate.
Use gpt-6-astra / High; stay in this conversation, no `/new` needed. The pending
visible inventory of beads1.jpg–beads7.jpg remains unfinished.
