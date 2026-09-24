# Photo 2: width-constrained boundaries and shadow uncertainty — R062–R065

The user's proposed clear-edge/width approach improves the **candidate**
centerline at the leftmost bend. Its original apparent width is about **112.5
pixels**, versus a clear-section reference of **95.8 pixels**. The proposed
inner-edge displacement is about **16.7 pixels**, with a **9.6–22.9 pixel** range
obtained from clear-width variability. The applied centerline movement there
is about **8.8 pixels**, predominantly leftward. These are image-space estimates,
not measurements against an independently labeled true edge.

[Open the illustrated review](review/r064/review.html),
[the corrected full image](output/width-correction-r065-final/centerline-corrected.png),
or [the questions file](QUESTIONS_FOR_MAKER.md).

## How much trouble do the shadows cause?

All distances below are **original-photo pixels**, at 2540×3182 resolution.
The numbered [whole-image map](review/r064/shadow-overview.png)
shows the regions. The reference-width residual band is 89.6–102.8 pixels,
about 13.3 pixels wide. It represents observed variation in the clearer sections,
not a calibrated confidence interval or a statement that the rope has exactly
constant width.

| Map zone / location | Shadowed edge | Estimated excess apparent width | Range from reference-width variability | Applied centerline movement | Dark shadow beyond saved edge |
| --- | --- | ---: | ---: | ---: | ---: |
| 1: leftmost bend | Inner/right | 16.7 | 9.6–22.9 | 8.8 | 124 |
| 2: lower loop, left side | Inner/right | 15.5 | 8.5–21.7 | 8.2 | 110 |
| 3: upper-left sloping run | Inner | 12.2 | 5.1–18.4 | 4.1 | 98 |
| 4: right run, below middle | Outer/right | 10.3 | 3.2–16.5 | 2.2 | unavailable |
| 5: right run, above middle | Outer/right | 11.4 | 4.4–17.7 | 3.4 | 112 |
| 7: upper-right bend | Outer | 12.0 | 4.9–18.2 | 3.1 | 100 |

These are regional medians. The full JSON/HTML table contains all **14 regions**.
The boundary uncertainty and cast-shadow extent are different quantities:

- The uncertain **boundary strip** at the left bend is roughly 10–23 pixels
  between the saved shadow-side edge and the width-predicted edge. The edge's
  predicted location itself has a roughly 13-pixel empirical range.
- The much broader dark patch outside that saved edge extends about 124 pixels
  before brightness recovers under the specified image test. That does not mean
  the boundary is wrong by 124 pixels. The scan has 4-pixel spacing and a
  heuristic brightness threshold; its real accuracy is not established.
- On the right run, some distant reference samples leave the image, so shadow
  extent is unavailable even where local width evidence suggests correction.

Of **600 equally spaced centerline samples**, 96 pass the two-clear-edge rule,
500 pass on only one edge and four on neither. **207 samples (34.5% of sampled
path length)** combine a clear anchor, a dark opposite exterior and excessive
width. This is a heuristic flag rate, not the fraction of beads known to be
wrong. Blending gives a nontrivial proposed shift at 296 samples; it tapers into
adjacent eligible sections. Maximum proposed centerline movement is 14.7 pixels.
Both-clear and neither-clear center points are preserved, and every edge passing
the clear-edge rule is fixed at its sampled position.

## Perspective trend: supported in principle, not established here

We fit width as a smooth linear function of vertical image position, allowing
it to increase toward the bottom. The default robust fit lands at an effectively
constant **95.8 pixels**. Letting the slope take either sign gives a slight
negative slope, while stricter clear-edge selection gives a slight positive
slope. Thus the current measurements do **not** reliably determine camera tilt
or a positive width gradient; this does not imply the camera was overhead.

Changing the brightness-ratio cutoff .80/.85/.90 selects 121/96/60 clear pairs.
The constrained central widths are 96.2/95.8/96.1 pixels, the leftmost-area median
center shift is 8.6/9.0/9.1 pixels, and the excess-width flag fraction is
33.0/34.5/37.3%. The left correction is more stable than the perspective slope.

Clear reference samples are clustered. Four available spatial holdouts have
mean absolute width errors of 3.1–8.0 pixels. Removing the top reference block
leaves insufficient vertical coverage, so that holdout is explicitly unavailable;
three other blocks contain no qualifying holdout samples. Additional manually
reviewed width references would be useful before adopting a global model.

## Method

The exact original boundary JSON is now retained as
[boundary-splines-source.json](boundary-splines-source.json), byte-identical to
the existing sibling-repository source. Its hash matches the provenance in
centerline.json. Neither original curve data nor reconstruction defaults changed.

1. Resample the saved centerline at 600 equal arc-length intervals. Estimate
   tangent directions with a two-sample Gaussian smoothing scale. Intersect each
   normal with the original inner and outer polylines and retain their nearest
   hits. All 600 paired hits straddle the centerline.
2. Test paper-color pixels outside each edge: near distances 8/16/24 pixels,
   compared with 70/90/110 pixels, averaging robustness across five tangential
   offsets. A clear edge requires magenta-paper support and median brightness
   ratio ≥.85. A likely shadow side requires paper support and ratio <.80.
   These are explicit heuristics, not hand-verified edge labels.
3. Fit a robust affine width-versus-y model to the 96 two-clear-edge sections,
   constraining the downward slope to be nonnegative. Use the clear-sample
   10th–90th percentile residuals as an empirical variability band.
4. Keep the reliable edge fixed. Where only the opposite side is shadowed and
   the measured width exceeds the upper band, blend toward an opposite edge
   one predicted width away, and toward their midpoint. The blend grows with
   excess width and is smoothed over two samples. It is restricted to eligible
   one-clear-edge positions. No correction is invented where neither is clear.
5. Separately scan the exterior at four-pixel steps, up to 180 pixels, using
   190/210/230-pixel background references. Record where three consecutive
   samples recover ≥90% of reference brightness with paper-color support.
   Missing references remain unavailable and scans without recovery are censored.
6. Group excess-width samples for the numbered map, bridging gaps of at most
   two samples and requiring five strong samples per reported region. Grouping
   does not change the correction. Retain all 600 records and uncertain samples.

## Illustrations and reproduction

- [Left bend: photo, original, proposed](review/r064/left-comparison.png).
- [Lower loop: same comparison](review/r064/lower-loop-comparison.png).
- [Bottom reference: some edge-quality checks fail](review/r064/bottom-reference.png).
- [Measured width around the necklace](review/r064/width-profile.svg).

Cyan is the centerline. In comparison panels, green is the outer edge and proposed
edges; orange is the saved inner edge. The overview uses yellow for the original
centerline and red for estimated edge movements. Original data remain available
alongside the proposals. The bottom crop includes positions left unchanged
because neither edge passed the quality rule; it is not proof that those edges
are correct or that both are shadowed.

```sh
.venv/bin/python photo2/width_correction.py --output photo2/output/width-correction-new \
  --review-bundle photo2/review/r064
.venv/bin/python -m unittest discover -s photo2 -p 'test_width_correction.py' -v
```

The output includes corrected curves, all measurements, a self-contained HTML
review, full/preview overlays, three comparisons, a numbered map, an SVG width
plot, and the report with parameters/source/artifact hashes. R065 authorizes the
committed curated review bundle (four PNGs, SVG, HTML and hash manifest), alongside
the questions file. Bulk outputs and full-resolution overlays remain ignored.
Report SHA-256 for `width-correction-r065-final/report.json`:
`089e42c36d6d45c1104f3d4b0e7359df8bd3819ecf6cf8ce38727717692090c6`.

Nine focused controls pass: annular width, positive/no-positive trend, inadequate
calibration, clear-edge anchoring, inner/outer swap, abstention, and shadow scan
with an out-of-frame reference. Compilation passes. Two final runs reproduce all
ten artifacts byte for byte; reports equal except command paths. Five source
hashes verify. Both review exports reproduce all six review artifacts; the
manifest verifies their hashes and binds the source report. The seven earlier R063 artifacts and numerical results stay
unchanged when adding R064 review illustrations.

All proposed curves are finite and closed; paired center points remain between
their edges. No strict interior segment intersections were found within the
three proposed curves or between inner and outer curves. All clear anchors and
both/neither-clear center points remain unchanged. Original, left/lower/bottom
comparisons, full corrected preview and overview were visually inspected; the
SVG was checked as XML. These checks do not establish true boundary accuracy.

An initial run exposed a spatial holdout with inadequate vertical coverage and
out-of-frame all-NaN references; these are now explicit unavailable results. An
initial exact-zero assertion failed on floating-point rounding (~1.8e-15);
bounded blend weights and a numerical tolerance resolve it. No bead detection,
pattern lookup, new rendering or full legacy regression was needed in this step.

## Follow-up review — R066

The [twelve-transect check](TRANSECT_REVIEW.md) compares frozen assistant visual
intervals with the original/candidate curves. It supports the main correction
but leaves small local disagreements and unresolved perspective. The next step
is direct image-edge evidence with uncertainty on both boundaries, before adoption.
The original width algorithm and defaults are unchanged.

## Original next bounded task (completed as an assistant review in R066)

Use the illustrated questions and a few independently reviewed width transects
to validate or revise the reliable-edge selection and width model. Stop after
that boundary/centerline check before adopting the new geometry for bead work.
The generated-image visible-inventory task remains pending; no whole-pattern
recovery has been claimed. Stay here with gpt-6-astra / High; no `/new` needed.
