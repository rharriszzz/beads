# R269 — search farther for supported brightness peaks

**Broader search improves R00956's middle and lower yellow coordinates. But search
radius alone does not explain the pale peak missed in R01284: HSV Value ranks its
orange patch above its pale highlight.** The upper R00956 yellow shows the same
limit: its 5×5/7×7 endpoints are already the highest mean V within 16 pixels.
No production detector or previous result changed.

[Original photographs, competing peaks, tables and traces](review/r269/README.md).

## 1. The R01284 peak five pixels away

[Photographic measurements](review/r269/R01284-missed-looking-peak.png) ·
[Exact five-pixel route and scores](review/r269/R01284-exact-five-pixel-route.png).

The pale raw peak **C=(976,2668)** is exactly five native pixels from R268's
9×9 endpoint **E=(980,2671)**, making it a strong match to the reported location.
Rather than assume one intended pixel, the saved map includes every competing
peak and highlights nearby mean and raw peaks too. Coordinates below are native
photograph coordinates; brightness is 0–255 DN.

| Point | Coordinate | Raw V | Mean5 | Mean7 | Mean9 | Raw prominence |
|---|---|---:|---:|---:|---:|---:|
| A: R268 mean7 endpoint | (981,2673) | 245 | 244.16 | 241.18 | 236.10 | 0 |
| B: nearby mean7 local peak | (978,2668) | 242 | 241.16 | 239.24 | 235.05 | 0 |
| **C: pale raw peak** | **(976,2668)** | **248** | **236.80** | **233.27** | **229.16** | **5** |
| D: upper raw peak | (979,2663) | 252 | 235.24 | 228.96 | 225.22 | 94 |
| E: R268 mean9 endpoint | (980,2671) | 244 | 240.96 | 240.00 | 238.47 | 0 |
| F: original seed | (983,2675) | 252 | 238.56 | 229.76 | 222.91 | 94 |

Prominence is raw-V topographic prominence. A mean maximum need not be a raw
maximum; zero here is a measurement, not missing evidence. Original raw plateaus
and prominence certificates remain available. Prominence alone cannot prefer D
over F: both have raw V252 and prominence94.

**Exact stop at E:** all eight neighboring mean9 scores are lower. The best first
step, to (980,2670), changes **238.469136 → 238.444444**, a decrease of just
**0.024691 DN**. R268 forbids it. A route to C passes raw/color guards, but mean9
ultimately falls to 229.160494. Broad search explicitly examines those alternatives:
even the unrestricted radius16 control keeps E as the highest mean9 point.
Thus removing the first-step restriction does not make C win this score.

B is another plausible nearby peak, 5.83 pixels from A. Its best admissible
mean7 route has a saddle of 238.938776: a **2.244898-DN** fall from A, before rising
to B's 239.244898. The 2-DN control blocks it; the 6-DN control reaches it but
still ranks A higher by 1.938776 DN. [Every step is pictured](review/r269/R01284-central-alternative-route.png).

**Why the photograph looks different:** HSV Value is `max(R,G,B)`, which is the
red channel at these points. C is RGB **[248,219,125]**, H45.85°, S0.496; A is
**[245,174,66]**, H36.20°, S0.731. The much stronger green/blue channels make C's
pale appearance consistent with the visual feedback, while Value ignores those
channels whenever red remains largest. This is evidence of a score mismatch,
not evidence that the pale patch is unimportant. Preserve C/D/B as alternatives;
do not silently declare A/E the best photographic bead coordinates.

## 2. R00956: which early stops can broader search overcome?

[All previously displayed supported coordinates](review/r269/R00956-all-current-supported.png).
[Upper](review/r269/R00956-upper-yellow-comparison.png),
[middle](review/r269/R00956-middle-yellow-comparison.png) and
[lower](review/r269/R00956-lower-yellow-comparison.png) show the original photograph
beside all three measurement windows. Yellow is the old path; cyan extends it.

The following mean7 results start from each named seed's R268 endpoint. The
supported display coordinate is separately tested and need not equal the seed.
Use raw-drop24 / mean-drop2 throughout; radius varies independently.

| Apparent location | R268 endpoint / mean7 | Radius3 best | Radius6 best | Radius10 best | Radius16 best |
|---|---|---|---|---|---|
| Upper yellow | (2282,1878) / 241.78 | same | same | same | same |
| Middle yellow | (2274,1902) / 237.18 | (2273,1900) / 238.78 | (2269,1899) / 239.90 | (2265,1902) / 240.86 | **(2263,1898) / 241.22** |
| Lower yellow | (2260,1925) / 238.16 | (2257,1925) / 239.47 | (2254,1925) / 241.45 | (2251,1921) / 243.43 | **(2251,1920) / 243.78** |

The middle yellow needed the raw allowance relaxed from 12 to 24 DN to reach the
better interior patch; the old running raw peak 250 imposed floor 238. The best raw saddle to the new mean7 winner
is 235, so every route fails that old floor; at least 15 DN is needed here. The lower yellow reaches its better mean7 location
even with raw12 once alternative paths and small score declines are allowed.
One saved route begins with mean 238.163→237.673, then recovers; its maximum
running raw drop remains 12 DN.
The upper yellow improves under mean9, from (2282,1877) to (2286,1879), but its
mean5/mean7 winners remain unchanged even without barriers. Those stops are a
limitation of the selected brightness score, not merely insufficient radius.

Among all ten previously displayed R00956 supported coordinates, broader search
moves 3/4/7 at mean5/7/9. R01284 moves 5/5/6 of twelve. These are coordinate
changes, not verified bead improvements. Every unchanged point and its competing
peaks remain in the numerical record.

## 3. Preserve the separate R01284 neighbors

[Separate origins and unsafe controls](review/r269/R01284-separate-neighbor-controls.png).
The user's identification of the green/blue origins as separate beads is retained
as review evidence. It never supplies a runtime label, mask or path constraint.
No convergence becomes an identity merge.

At mean7/radius16, raw24/mean2 moves the shadowed origin's R268 endpoint
(997,2677) to **(1001,2677)**, mean169.80→170.59. The central origin remains
**(981,2673)**. These proposals remain visibly separate. Relaxing the mean floor
to6 DN instead sends the shadowed proposal to **(982,2673)** on the central bright
patch: an incorrect crossing. Mean9/raw24/mean6 also crosses. Both failures are
preserved and explicitly rejected for this photographic example. A larger raw
allowance alone is not enough to protect identity; permissive mean valleys fail.

## Method and verification

Keep R268 strict climbing as the unchanged comparison. From **every one of its
451 original starts**, retain the guarded12 endpoint for each window as the search
anchor. Search closed Euclidean disks of **3/6/10/16 native pixels**; do not restart
the radius at each intermediate point. Analyze exact 5×5/7×7/9×9 V sums independently.
This produces **21,648 photographic searches** across four controls:

- Radius-only best mean: deliberately unsafe control.
- Raw12 / mean2: remove monotonic ascent while retaining a conservative raw floor.
- Raw24 / mean2: allow additional raw fluctuation; main review comparison.
- Raw24 / mean6: test a more permissive mean valley; exposes the named crossing.

Guarded searches reuse the established background/context deferrals and native
hue/saturation boundaries. Raw floors refer to the highest raw value actually
visited by the original R268 path, not a reset at its endpoint. Mean floors refer
to the R268 endpoint's mean. These are **fixed floors**, not a guarantee against
every later peak-relative drawdown. Equal and declining steps are allowed above
both floors. Both corner routes of every diagonal must pass all barriers and stay
inside the disk. No watershed, geometric model, spline, outline growth or manual
identity enters inference.

Exhaustively visit the reachable graph, then rank all reachable pixels by exact
mean sum; ties prefer smaller displacement, then y/x. Raw prominence and H/S are
reported independently rather than hidden inside a tuned composite score.
Preserve raw/mean peaks and constrained endpoints even when they lose. For the
five named examples, save direct paths and violations, shortest admissible paths,
and paths maximizing the minimum raw or mean value under the other constraints.
The saved frontier explains rejection of **all** routes, not just a failed line.

Synthetic validation reuses 96 neighboring-bead stress scenes with multiple
highlights, shading, palette/spacing changes and noise, plus four scenes with an
intentionally invisible internal boundary. Every raw maximum is inventoried;
fixed image background evidence admits 567 of 13,525 starts, including all 542
body starts. Ground truth enters evaluation only. **27,216 searches** are saved.
At radius16, raw24/mean2 gives:

| Window | Regular-scene cross-body endpoints / 500 body starts | Background exits |
|---|---:|---:|
| 5×5 | 0 | 1 |
| 7×7 | 0 | 2 |
| 9×9 | 0 | 1 |

The stronger prominence12 subset has zero cross-body/background endpoints, but
that does not remove the weak-start failures. In the four invisible-boundary
scenes, 13/42 body starts cross at each window even with guards. Broader search
therefore remains a diagnostic proposal method, not a proven per-bead selector.
[Failure images and traces](review/r269/README.md) retain these limitations.

**13 tests pass.** Replay verifies all **97,998 selected native moves**,
2,361,512 reachable-tree nodes and 740,446 blocked frontier edges. Independent
threshold reachability checks certify 1,569 alternative-path bottlenecks. Original
pixels/scores, every old maximum and all R267/R268 and production input hashes
are preserved. Reproduction commands are in the evidence index.

Stop here for review; no production change. Next bounded task, only if requested:
compare a brightness measure sensitive to the pale highlight's green/blue channels
against HSV Value, retaining the separate-neighbor checks and these broader paths.
Keep the current model/reasoning; no `/new` needed.
