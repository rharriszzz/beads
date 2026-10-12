# R260 coordinate-focused review evidence

[Review report](../../DETECTION_REVIEW_R260.md) · [viewer launch](../../bead_detection/README.md)

Generation `219a6fe6c2b98f00`; baseline R259 `40eaf236aa363f0c` remains preserved
in the sibling `r259` directory. No previous review or result was overwritten. Baseline code is commit `24c5ba6`.
Initial review sheets and their selected IDs are saved with the `initial-` prefix.

- [coordinates.csv](coordinates.csv): ID, supported location x/y, exact centroid,
  pixel count, evidence kind and heuristic confidence for every retained region.
- [regions.json.gz](regions.json.gz): all retained/rejected records, exact pixel
  runs, contours, maxima, statistics, location semantics and parameters.
- [comparison.json](comparison.json): all common centroid movements, gained/lost
  IDs and reproducible review sample selections.
- [sensitivity.json](sensitivity.json) and [rise comparison](rise-comparison.png):
  0.045/0.025/0.015 Value-rise comparisons and angular-filter ablation.
- [largest shifts](largest_shifts-1.png), [second sheet](largest_shifts-2.png):
  raw/before/after support and white region-centroid crosses.
- Recovered regions: [sheet1](recovered-1.png), [sheet2](recovered-2.png),
  [sheet3](recovered-3.png). All17 additions are shown.
- Largest, smallest, spatial and coordinate-edge-case sheets are alongside these.
- [size-distribution.png](size-distribution.png), [rank-size.csv](rank-size.csv),
  [labels.npz](labels.npz), [summary.json](summary.json), [validation.json](validation.json),
  [browser-checks.json](browser-checks.json) and [provenance.json](provenance.json)
  preserve the complete run and verification.

Mask runs use inclusive `[y,x_first,x_last]`. Coordinates are native EXIF-oriented
pixels, x right/y down. A supported location and an area centroid are distinct;
neither is a physical center. Dark-region area is reflection support only. Read
`dark_blur_sigma` when reproducing each dark-perimeter check. Ambiguous bright
patches are retained without claiming black material or a complete colored body.

Reproduction from the repository root:

```bash
.venv/bin/python -m photo2.bead_detection.detect
.venv/bin/python -m unittest photo2.bead_detection.test_detection -v
.venv/bin/python -m photo2.bead_detection.validate --isolation
PLAYWRIGHT_BROWSERS_PATH=/tmp/beads-debugger-browsers .venv/bin/python -m photo2.bead_detection.browser_smoke
.venv/bin/python -m photo2.bead_detection.review_r260
.venv/bin/python -m photo2.bead_detection.curate
```

The detector does not read this review directory. `review_r260` reads both saved
runs to make diagnostic comparisons. `curate` now defaults to R260 so the frozen
R259 evidence is protected. Runtime caches still use `photo2/output/detection-r259`
for continuity; generation/source hashes invalidate stale data.


### Strict-darkening and hue/dark-clue tests

These are separate experiments, not the default viewer's detector. Each saved
variant includes all 1,494 original automatic candidates, with their *production*
retained/rejected status preserved. There is no new acceptance decision or overlap
competition. Summary comparisons use the 1,057 current retained IDs.

- [strict-summary.json](strict-summary.json), [strict-validation.json](strict-validation.json).
- `strict-{native,smoothed}-{14,30}.json.gz`: strictly decreasing Value at every
  ray sample, followed by 14% or 30% intensity-drop retreat and raster exclusion.
- `strict-{native,smoothed}-30-color.json.gz`: additionally stop at persistent
  relative hue drift or dark/low-chroma evidence. Event reasons and HSV are saved.
- Matching `strict-*-coordinates.csv` files contain every tested ID, its original
  status, supported coordinate, centroid and pixel count.
- Raw/current/strict examples: [sheet1](strict-comparison-1.png),
  [sheet2](strict-comparison-2.png).
- Hue/dark guard outliers: [hue sheet](strict-color-comparison-1.png),
  [dark-clue sheet](strict-color-comparison-2.png),
  [selection IDs](strict-color-review-ids.json).

The seed-only fallback is explicit; small support alone is not a failed location.
Strictness refers to the stated sampled signal. Native and smoothed tests must
not be conflated. Possible black-material clues also admit shadows; no material
classification or physical center follows. See the report for exact thresholds.

```bash
.venv/bin/python -m unittest photo2.bead_detection.test_strict -v
.venv/bin/python -m photo2.bead_detection.strict_r260
.venv/bin/python -m photo2.bead_detection.validate_strict
.venv/bin/python -m photo2.bead_detection.curate
```
