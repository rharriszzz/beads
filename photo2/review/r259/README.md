# Frozen R259 detection evidence

[Report](../../AUTOMATIC_DETECTION_R259.md) · [launch and reproduction](../../bead_detection/README.md)

Final run: `40eaf236aa363f0c`, detector `r259-dark-perimeter-v2`.
The maker's clarification is applied: black regions stop at the first complete
dark perimeter and do not estimate full black-body extents.

| Artifact | Contents |
| --- | --- |
| [regions.json.gz](regions.json.gz) | Complete 1,040 retained and 454 rejected records, all 1,498 maxima, patch runs, region runs, contours, centroids, HSV statistics, ambiguity/reasons, parameters and hashes |
| [labels.npz](labels.npz) | Native 3182 × 2540 int32 label raster; zero unassigned, positive value is the numeric part of the region ID |
| [summary.json](summary.json) | Counts, size summary, histogram values and provenance |
| [rank-size.csv](rank-size.csv) | All retained IDs in descending pixel-count order |
| [size-distribution.png](size-distribution.png) | Histogram and rank-versus-size plot |
| [whole-regions.jpg](whole-regions.jpg) | Whole-photo overview, reduced for review |
| [example-1.png](example-1.png), [example-2.png](example-2.png), [example-3.png](example-3.png) | Original/outlined crop pairs, rendered at 2× for inspection |
| [browser-whole.png](browser-whole.png), [browser-detail.png](browser-detail.png) | Actual Chromium screenshots |
| [validation.json](validation.json) | Full-photo mask/dark-perimeter audit and isolated-photo replay |
| [browser-checks.json](browser-checks.json) | 28 actual Chromium checks |
| [provenance.json](provenance.json) | Artifact/code/source hashes and preserved local-review hash |

Coordinates use EXIF-oriented native pixels (x right, y down); masks use integer
pixel centers. `pixel_runs` are inclusive `[y, first_x, last_x]` spans. Polylines
close explicitly. Pixel count, centroid and statistics come from the exact mask,
not the simplified contour. `area_px2` equals pixel count. H is circular degrees;
S/V are normalized to [0,1]. `Mxxxxx` identifies an initial maximum/bright patch;
`Rxxxxx` identifies a candidate region. They are separate namespaces and carry
no historical or string index. Region IDs may have gaps when only retained regions
are displayed. Always quote the generation ID with a review ID.

`growth_boundary` is the sampled pre-retreat valley for colored proposals and
the first-dark-perimeter contour for black support. `proposed_boundary` precedes
overlap competition; `contours` and `pixel_runs` are the final measurement support
(rejected candidates preserve their rejected support). Dark-perimeter V is measured
on Gaussian-smoothed Value to tolerate pixel noise. All retained black perimeters
are ≤0.32; contrast must also exceed 0.14. This is a photometric rule, not proof of
material or a measured physical black-bead border.

Read the compressed JSON with Python:

```python
import gzip, json
with gzip.open('photo2/review/r259/regions.json.gz', 'rt') as source:
    data = json.load(source)
```

Regenerate the run and evidence using the launch README commands, then run
`.venv/bin/python -m photo2.bead_detection.curate` after successful validation and
browser checks. Routine decoded images and caches remain ignored. The original
JPEG remains the tracked source; the compressed run preserves all numerical output.
