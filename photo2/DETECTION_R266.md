# R266 — automatic maxima and strict annular comparison

**Peak selection and paper deferral improve the reviewed examples. Strict annular
growth does not yet justify replacing strict R265 straight growth.** Recommend
`straight-0-selected12` as the conservative R266 comparison, with
`annular-0-selected12` alongside it. The 6-DN recovery views improve R00956 but add
questionable dark-region candidates; retain them as sensitivity results. The
3-DN views are exploratory. Previous detectors, results, reviews and viewer default
remain preserved. No verified whole-photo bead count or complete recovery is claimed.

[Evidence and inventories](review/r266/README.md) ·
[R00956 at 6 DN](review/r266/selected-R00956.png) ·
[R01284](review/r266/selected-R01284.png) ·
[R01307](review/r266/selected-R01307.png).

## What changed

Four methods were compared separately before combination: running-minimum rise
allowances, native annular fronts, peak association, and learned paper gating.
The user's later emphasis makes **0 DN / strict light-to-dark** the main setting;
1–3 DN remain diagnostics. No ring average, watershed, unrestricted flood growth,
region-wide brightness ceiling, smoothing of measured pixels or expected-count target.

Annular fronts are one-pixel shells in the native eight-neighbor (Chebyshev) metric,
starting at the maximum's visible equal-brightness plateau. Every new pixel has a
fixed inward parent based on nearest-patch raster geometry. The parent's running
minimum is inherited independently. A stopped parent permanently blocks its branch;
there is no lateral rerouting around an obstacle. Native valley/corner, first-neutral-
black, hue and saturation stops remain. Local darkness retreat keeps connected
support without filling holes. The 870-distinct-pixel pre-retreat cap remains hard.
Full traces contain layers, parents, running minima, native HSV and stop reasons.
Straight comparisons retain R265's complete Bresenham histories.

Splitting is permitted without relaxing descent. A tested split primitive cuts only
native dark-valley evidence, requires independently seeded connected pieces, and
preserves their parent/child pixels. Automatic split proposals defer the parent in
favor of independent original maxima. It is not a nearest-peak partition; no split
is forced merely because a shape forks. The strict photographic runs needed no such
post-growth split: their valley stops already block the crossing.

Peak competition is considered within 18 native pixels. Selection compares peak
brightness, prominence tier, 7×7 neighborhood brightness, support and compactness.
Suppression requires a broad bright five-pixel ribbon, bounded valley depth, and
compatible gradual shading; a more distant pair requires a brighter bridge.
Abrupt color changes, deep valleys and unsupported associations preserve alternatives.
Gray reflection hue is not treated as reliable chromatic evidence. Associations
are checked against a selected winner, without transitive merging. All 154,761
original maxima, original coordinates/masks, suppressed candidates and reasons survive.
Prominence is recorded as a tested lower bound, not a falsely precise measurement.

Background H/S/V and texture are learned from generic photograph margins, without
historical centerlines, splines, palette boxes or supplied bead positions. Confident
seed rejection precedes growth. Probable paper stops affected branches; broader
HSV agreement plus nearby smooth context causes **deferral**, not confident bead
acceptance. The first narrow model missed clipped paper; the saved refinement uses
that broader uncertainty for deferral. This remains a heuristic, not verified material
segmentation. Dim gray reflections remain eligible.

## Numerical comparisons

Growth-only controls hold prominence35, hue10° and other R265 gates fixed:

| Method / allowance DN | Supports | Hole pixels | Thin pixels | Mean perimeter / area | Reviewed paper-window pixels |
|---|---:|---:|---:|---:|---:|
| straight / 0 | 1556 | 249 | 6445 | 0.611 | 7 |
| straight / 1 | 1557 | 263 | 6973 | 0.598 | 9 |
| straight / 2 | 1557 | 296 | 7117 | 0.584 | 17 |
| straight / 3 | 1559 | 288 | 7067 | 0.567 | 17 |
| annular / 0 | 1556 | 382 | 6951 | 0.603 | 12 |
| annular / 1 | 1557 | 385 | 7932 | 0.591 | 14 |
| annular / 2 | 1557 | 457 | 8448 | 0.580 | 17 |
| annular / 3 | 1559 | 434 | 8744 | 0.565 | 17 |

Annular strict growth slightly reduces normalized perimeter (0.611→0.603), but
increases absolute fringe and hole pixels; greater area alone is not an improvement.
Allowances worsen the reviewed paper spill. These results support preserving strict
straight growth, not adopting annular or uphill allowances automatically.

Final selection inventories (counts are proposals/statuses, **not beads**):

| Strict method / recovery prominence | Selected | Suppressed | Deferred |
|---|---:|---:|---:|
| straight / 12 | 1602 | 789 | 232 |
| straight / 6 | 2337 | 2417 | 611 |
| straight / 3 | 3914 | 5288 | 1507 |
| annular / 12 | 1604 | 788 | 231 |
| annular / 6 | 2348 | 2416 | 601 |
| annular / 3 | 3933 | 5291 | 1491 |

The conservative straight result reduces retention of both original IDs in the
12 reviewed duplicate pairs from12 to0 and the reviewed paper-window pixels from7
to0. This is a scoped proxy: replacement maxima and other duplicate groups can
remain. It is not proof of one coordinate per body throughout the photograph.

- **R00956:** 6-DN recovery selects interior maxima P090532/P091867 rather than the
  former upper/middle yellow representatives. M1's nearest-coordinate distance
  improves to2.24px; the 12-DN variant remains12.21px away. Another proposal can
  remain on that body's paper-facing side. This is incomplete duplicate repair.
- **R01284:** the two documented yellow pairs are consolidated. P129034 gives a
  candidate near the shadowed-yellow miss (9.22px from its approximate landmark).
  Strict annular support is broader, with some thin branches still visible.
- **R01307:** the original duplicate-reflection pair is consolidated after handling
  gray hue uncertainty. Candidates near the upper pale and lower yellow landmarks
  improve proximity to8.60px and8.54px. Their precise body interpretation remains
  photographic judgment, not a confirmed center measurement.
- **Paper edges:** original clipped-paper examples and additional smooth paper-like
  seeds are rejected or deferred using image-derived evidence. Some ambiguous
  colored rims and dark-region candidates survive, particularly at low prominence.

## Verification, limits and reproduction

80 Python tests and 59 new Chromium checks pass; 44 preserved-viewer checks also
pass. The main comparison audits every grown support, including rejected proposals;
additional low-prominence audits and exact selection-only mask/coordinate checks
are recorded in `refined-metrics.json`. The R265 baseline reproduces exactly.
The audits verify5,639,526 accepted samples and11,288,390 stopped edges;68,538
selection records retain identical native masks/coordinates. A 50-ms forced deadline cleanly terminates a stage and saves its incomplete checkpoint.

The 96-scene stress set covers192 known bodies, same/different-color touching
neighbors, multiple highlights, shadows, neutral reflections and0–3 DN noise.
At all three final recovery thresholds, both strict methods have0 misses,
0 duplicate extras,0 background coordinates and0 cross-body suppressions in this
set; median center error is1px. Seven support pixels cross into a neighboring
footprint. The pre-selection baseline had36 duplicate extras. These controlled
scenes are easier than the photograph. The older R265 deep-separated-highlight
scenes retain uncertain duplicates; synthetic success does not verify photographic
identity. Palette rotation, translation and noise stability, all separate ablations,
source hashes, thresholds and ranked improvements/regressions are saved.

All computation shares a configurable1800-second deadline, including extensions;
checkpoints record stages, failures and source revisions. The main comparison took
734 seconds; final audits and extensions finished about22m06s into that same window. No work was padded to consume
the budget. See the final manifest for total elapsed computation-window time.

```sh
MPLCONFIGDIR=/tmp/beads-r266-mpl .venv/bin/python -m photo2.bead_detection.experiment_r266 --seconds 1800
MPLCONFIGDIR=/tmp/beads-r266-mpl .venv/bin/python -m photo2.bead_detection.stress_r266
MPLCONFIGDIR=/tmp/beads-r266-mpl .venv/bin/python -m photo2.bead_detection.recovery_r266
MPLCONFIGDIR=/tmp/beads-r266-mpl .venv/bin/python -m photo2.bead_detection.refine_r266
MPLCONFIGDIR=/tmp/beads-r266-mpl .venv/bin/python -m photo2.bead_detection.evaluate_refined_r266 synthetic
MPLCONFIGDIR=/tmp/beads-r266-mpl .venv/bin/python -m photo2.bead_detection.evaluate_refined_r266 evaluate
MPLCONFIGDIR=/tmp/beads-r266-mpl .venv/bin/python -m photo2.bead_detection.pack_r266
.venv/bin/python -m photo2.bead_detection.server
```

Open `http://127.0.0.1:8767/?run=straight-0-selected12`. The existing photograph,
cyan outlines, IDs/centroids, pan/zoom, size histogram/navigation and exact replay
remain. Two compact controls choose the comparison and include suppressed/deferred
maxima; clicking related IDs exposes selection evidence. The viewport survives
method switching. Tracked archives support replay after ignored output is cleaned,
provided the preserved default photograph/viewer work has been prepared.
Sites skill was used locally only; no deployment or external messages.

**Stopping point:** deliver this comparison and stop. Next bounded task, only when
requested: review residual duplicate alternatives and weak recovered candidates,
especially R00956's paper-facing extra and dark-region noise. No geometry, indexing,
lighting inversion or pattern work. Keep the user's current model/reasoning choice;
no `/new` is needed for artifact review. Revisit the annular approach later as directed.
