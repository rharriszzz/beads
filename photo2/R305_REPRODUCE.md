# R305 reproduction and review

Run from any directory:

```sh
/home/rharris/git/beads/photo2/review/r305/launch.sh
```

The existing repository `.venv`, localhost server and WSL/PowerShell browser
mechanism are reused; default port 8305 has an available-port fallback.
`--no-browser --port 0` runs without opening a browser. Opening
`photo2/review/r305/index.html` directly works offline, including native owner
picking through lossless JavaScript run-length data. No CDN or network assets
are required. The PNG owner rasters are also retained independently.

Start at −40, use ±1/10/50, the index box or slider. Follow selected bead is on
by default and preserves zoom while centering the actual projected center.
Disable Follow to drag the photo independently. The two canvases share exactly
the same viewport. A/B/C presets isolate vectors/boundaries/both; selected-only
and neighbor boundary modes are available separately. Clicking a plot point,
gallery item or nonzero category count navigates to a concrete bead. Repeated
category clicks cycle its examples. Fully occluded positions remain selectable.

Picking prefers the rounded native pixel's first-hit owner. Outside surfaces,
it uses the nearest exact visible-boundary segment within 12 native pixels,
then projected center within 20 pixels. Nearby alternatives are listed.
Guard owners are identified as outside the requested interval; distant clicks
do not change the selection. Reflection arrows use unchanged observed centroids
and paired predicted native centroids, actual pixel displacement and arrowheads.

The code reuses R303 shape/contact/lighting and R304 forward/correspondence
construction. R305-specific modules are under `photo2/r305/`; prior code is
unchanged. Delivered geometry is immutable: `forward` refuses to overwrite it.
To reproduce new predictions, use a separate checkout and change **both** `BASE`
and `REVIEW` in that isolated copy's `photo2/r305/model.py` to new existing
output folders, with `results/` and `evidence/` beneath `BASE`. Never point a
new export at an old review directory. Tests enforce the delivered paths.

The delivered build order was:

```sh
.venv/bin/python -m photo2.r305.forward
.venv/bin/python -m photo2.r305.analyze
.venv/bin/python -m photo2.r305.diagnose
.venv/bin/python -m photo2.r305.verify
.venv/bin/python -m photo2.r305.diagnose
.venv/bin/python -m photo2.r305.contour
.venv/bin/python -m photo2.r305.owner_data
.venv/bin/python -m photo2.r305.graphics
.venv/bin/python -m unittest photo2.r305.tests
/home/rharris/.local/bin/beads-chromium-review photo2.r305.browser_check
```

`verify` replays all native positions, pixels, reflection/boundary records and
physical witnesses, checks the R304 overlap and 96 guards, then uses chunked
half-pixel sampling on every displayed bead. It writes numerical receipts and
enriches the viewer, without altering predictions. The second `diagnose` adds
those numerical results to interval rankings. `contour` attaches the saved
uncertain B15 polygon. Derived analysis/graphics may be rebuilt in place;
there is no optimization command. A full preservation snapshot precedes work.

Main machine-readable files under `photo2/r305/results/`:

- `{family}.json.gz`: every core/guard position, parameters, visible boundaries,
  3-D/projected centers, reflection peaks/centroids, threshold uncertainty,
  physical witnesses and penetration checks.
- `{family}-raster.npz`: exact native address, intensity, unknown-ray and isolated
  count arrays, inclusive bounds. Background sentinel −32768; actual signed
  bead indices are stored. `*-owners.png` encodes `index+32768` in little-endian
  R/G bytes; zero means background. `owners.js` is independently decoded/tested.
- `{family}-correspondences.json`: all original observations, pinned anchors,
  selected global pairs, 12/24/48 gap paths, competing owner residuals, no-gap
  ordinal control, rolling/group counts and outside-geography unmatched rows.
- `{family}-errors.csv`, `*-groups.csv`, `*-errors-index.svg`, `*-signed-errors.svg`:
  exportable errors and plots. PNG equivalents live in the review directory.
- `{family}-material.json.gz`, `*-colored-supports.json.gz`: frozen image-only
  paper/color cues and historic uncertain interiors, including failed supports.
- `{family}-geometry.json`, `*-numerical.json`, `*-guard-check.json.gz`:
  continuous stations, curvature/frames, convergence and full extended contacts.
- `starting-red-diagnosis.json`, `B15-contour-diagnosis.json`,
  `transition-control.json`: conditional owner fractions, unobstructed versus
  first-hit surfaces, contour sensitivity, and the single 4→24 diagnostic splice.
- `problem-intervals.json`, `gallery.json`: ranked raw/normalized group diagnostics
  and the 17 native-photo crop definitions/captions.
- `computation.json`, `verification.json`, `tests.log`, `browser-check.json`,
  `delivery.json`: timing/memory, replay, browser and remote-delivery evidence.

The model image bounds include some guard context. Numerical invariance is
reported both for the entire enclosing rectangle and the union of requested
owners in either guard evaluation. Newly exposed far-guard surfaces must not be
mistaken for changes to requested beads. All extra physical failures in guards
remain reported, with address pairs separating them from displayed failures.

Static crops are native decoded photo data, enlarged only by nearest pixels,
with an unmarked panel beside annotations. Gallery tests compare every raw crop
and unmarked panel with the source photo. Existing automatic interiors and the
B15 polygon are explicitly uncertain and incomplete. No new photographic
ownership or exact whole-bead contours are inferred. Deferred questions are
saved in the viewer/report; no additional fitting or Phase 3 is authorized.
