# R270 — brightness measures for photographic bead locations

**Recommend ICC-managed sRGB relative luminance, averaged over 7×7, for the next
photographic review.** It reaches R01284's pale patch, improves the three R00956
yellow locations, preserves the confirmed neighboring origins under the main guards,
and has fewer background exits than the alternatives in the paired synthetic test.
OKLab L is a close alternative. This recommendation is scoped to these experiments;
no detector, region growth, viewer, geometry or indexing was changed or adopted.

[Photographs, measurements and traces](review/r270/README.md) ·
[Every independent maximum](review/r270/MAXIMA_INDEX.md).

## What changed in the photograph

[Original pale-yellow photograph and numeric comparison](review/r270/R01284-pale-peak-score-comparison.png).
The reported pale raw peak C=(976,2668) is exactly 5 pixels from the old mean9
endpoint E=(980,2671). Luminance and OKLab mean7 choose **(978,2667)**, within 2.24
pixels of C and visibly on the pale highlight. The experimental V/S score chooses
(978,2668). Neighborhood maxima need not coincide with individual raw maxima.

At identical coordinates, the scores explain the change. Values here are each
score's mean7 on a convenient 0–255 scale; compare rows within a column.

| Coordinate | V | 255·relative Y | 255·OKLab L | Experimental V/S |
|---|---:|---:|---:|---:|
| Old mean7 endpoint A=(981,2673) | **241.184** | 126.575 | 203.085 | 152.622 |
| Pale raw peak C=(976,2668) | 233.265 | 147.023 | 211.151 | 166.786 |
| New Y/OKLab endpoint (978,2667) | 238.776 | **160.843** | **218.383** | 170.337 |
| New V/S endpoint (978,2668) | 239.245 | 159.814 | 218.008 | **170.469** |

Unlike V, all alternatives rank the pale patch above A. C's raw luminance is
185.657/255, above the new endpoint's 176.438/255, but its neighborhood is dimmer:
147.023 versus 160.843. Averaging therefore favors the supported bright patch rather
than the single brightest pixel. Raw values and all 5/7/9 means survive in the table
and float64 rasters; no candidate was removed by the old V-prominence cutoff.

[Upper](review/r270/R00956-upper-yellow-four-measures.png),
[middle](review/r270/R00956-middle-yellow-four-measures.png) and
[lower](review/r270/R00956-lower-yellow-four-measures.png) R00956 comparisons show
all three windows beside the original photograph. Mean7/radius16 endpoints are:

| Apparent location | V baseline | Relative luminance | OKLab L | V/S experiment |
|---|---|---|---|---|
| R00956 upper yellow | (2282,1878) | **(2284,1877)** | (2284,1877) | (2282,1877) |
| R00956 middle yellow | (2263,1898) | **(2267,1898)** | (2267,1898) | (2263,1897) |
| R00956 lower yellow | (2251,1920) | **(2255,1919)** | (2255,1919) | (2250,1920) |
| R01284 central yellow | (981,2673) | **(978,2667)** | (978,2667) | (978,2668) |
| R01284 shadowed neighbor | (1001,2677) | **(1001,2678)** | (1001,2677) | (1001,2677) |

Luminance and OKLab agree on all four bright-yellow locations at **all three
window sizes**, not just mean7. Their lower R00956 coordinate is identical across
5/7/9. The upper and middle move toward the pale central patches; V/S favors a
different part of the lower patch. These are photographic coordinate judgments,
not recovered physical centers or manually assigned runtime bead identities.

## Preserve neighboring beads

[Both origins under every measure/window](review/r270/R01284-separate-neighbors-all-measures.png).
The main raw24/mean2 policy keeps the two user-confirmed origins separate with all
four scores and all windows. No endpoint agreement merges identities.

The permissive 6-DN-equivalent mean valley still fails. At mean7, V and V/S cross
onto the central bright patch; Y and OKLab remain separate. At mean9 **all four**
permit an incorrect crossing, including Y/OKLab reaching (987,2672). Radius-only
search also crosses. A better brightness measure does not replace boundary evidence.
[These failed routes are photographed](review/r270/R01284-permissive-boundary-failures.png) and saved in full; none is adopted.

## Scores, color profile and comparable thresholds

The JPEG embeds **Apple Wide Color Sharing Profile**. Standard Y/OKLab calculations
first convert that profile to 8-bit sRGB through LCMS, using relative colorimetric
intent, then apply the sRGB inverse transfer function. The historical V and V/S
experiment retain native RGB/HSV, preserving the requested V baseline exactly.
Background and color guards always use the unchanged native image evidence.
Photographic displays use ICC-managed sRGB; source native pixels are also saved.

- **V:** maximum native RGB channel, unchanged.
- **Relative luminance Y:** linearize each sRGB channel using the 0.04045 breakpoint,
  then weight linear R/G/B by 0.2126/0.7152/0.0722. This is relative display-referred
  luminance, not recovered scene illumination. [W3C definition](https://www.w3.org/TR/WCAG21/relative-luminance.html).
- **OKLab L:** apply the published linear-sRGB matrices and cube-root cone response;
  use the L coordinate. [Author's definition and implementation](https://bottosson.github.io/posts/oklab/).
- **V/S:** `V·(1−S/2)=(maxRGB+minRGB)/2`, a deliberately simple native-RGB experiment
  with fixed coefficient. It equals HSL lightness and is not a calibrated perceptual
  model; no coefficient was fitted to the review locations.

The initial experiment treating native RGB as sRGB survives in
`native-rgb-control/`. ICC conversion changes magnitudes and some maxima, but the
Y/OKLab endpoints on the four bright-yellow examples match that control at all
three windows. The pale-patch result therefore survives proper color management.

For each score m, define its response to neutral sRGB gray as `g_m(code)`. Convert
an old d-DN allowance to the score floor
`g_m(max(0, g_m_inverse(reference) − d))`. Use d=12 for strict-climb raw retreat,
12/24 for broad raw floors and 2/6 for broad mean floors. Conversion depends on the
reference brightness, avoiding an arbitrary constant conversion of nonlinear
scales. It equates neutral-gray contrasts; colored barriers are not mathematically
identical. `threshold-reference.json` records examples and every trace records its
actual floors. A separate common-original-V-anchor/raw24 control isolates ranking
from the changed climb anchors and raw guards; its named-neighbor mean2 results
also remain separate.

Transform native pixels before averaging; do not transform averaged RGB. Retain
float64 raw scores and use exact integer sums of samples rounded to 10⁻⁹ on the
0–255 display scale. This bounds per-pixel/mean rounding error by 5×10⁻¹⁰, preserves
sub-DN variations, and makes equal-plateau decisions deterministic. No spatial
resampling changes measurements. Strict climbing permits only higher sums; broader
search exhausts admissible native paths in fixed radii 3/6/10/16, including equal or
declining steps. R269's fixed floors, color/background stops and both diagonal
corner checks remain comparable. All original 451 starts survive, plus each score's
raw/mean maxima; prominence is measured with explicit context-censor flags.

## Synthetic evidence and limits

Use a common union of image-derived raw maxima for every score: 96 preserved stress
scenes, 4 invisible-interface controls and 12 new colored-highlight scenes. The new
scenes mix white highlights with colored diffuse bodies in linear light, include
shadows and touching/overlapping neighbors, and vary palette. Ground truth is used
only after image-based eligibility and search. All raw and 5/7/9 mean maximum masks,
images, truth arrays, exclusions and selected paths are saved.

At radius16/raw24/mean2, among **1,197 common body starts** in the 96 regular scenes,
all four scores have zero cross-body endpoints. Background exits remain:

| Window | V | Relative Y | OKLab L | V/S |
|---|---:|---:|---:|---:|
| 5×5 | 2 | **0** | 3 | 3 |
| 7×7 | 5 | **1** | 2 | 3 |
| 9×9 | 3 | **1** | 3 | 3 |

The 12 colored-highlight scenes add 48 common body starts, with zero cross-body or
background endpoints under the main policy. All four scores still cross for 14/43
body starts in the deliberately invisible-interface controls. Unguarded/radius-only
failures and guarded background exits are pictured in the evidence index. The
common start union differs from R269's 500 regular body starts; its paired original-V
subset reproduces all 4,800 old synthetic groups exactly. Windows reuse starts and
are not independent trials. These tests support choosing Y for review, not a
whole-photo accuracy claim or a guarantee against merging.

## Verification and stopping point

18 reproducible tests cover standards reference values, correct linearization,
profile pairing, transform-before-average, threshold conversion, maxima/plateaus,
prominence, fractional scores, valleys and diagonal/background stops. The V run
exactly reproduces 2,706 R268 prefix paths and all 21,648 R269 photographic search
endpoints/scores. Saved traces cover 150,000 photographic and 321,360 synthetic
broader searches, plus 15,000 and 32,136 strict-climb/control traces. Independent
checks verify native sums, moves and guards, named reachable graphs/frontiers and
alternative bottlenecks. Previous evidence/source hashes remain identical.

Computation uses a shared 30-minute deadline, including the ICC-managed repeat and
verification: **22.90 minutes** through final numerical validation, with **1,195,833 selected moves**,
1,200 named graphs and 7,376 optimal-bottleneck certificates checked. Exact timing
is in `validation.json`. Stop for photographic
review. The next bounded task, only when requested, is to accept or reject the
luminance coordinates and review its remaining weak-start/background failures
before any production selection change. Keep current model/reasoning; no `/new`
is needed for this review.
