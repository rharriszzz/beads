# R304 review and reproduction

From the repository, run:

```sh
photo2/review/r304/launch.sh
```

It uses `.venv/bin/python`, binds localhost (normally port 8304, with an available
port fallback), and attempts the existing Windows PowerShell / WSL browser
launcher. `--no-browser --port 0` starts a server without opening a browser.
Opening `photo2/review/r304/index.html` directly also works offline.

Select a model, step through ten panels of 35 positions, and use the slider or
±1 buttons for individual addresses. Zoom 1× is one native pixel per canvas
pixel; larger zoom uses nearest-pixel display. The raw photo is always separate.
Click an observation for unchanged coordinates, quality, uncertainties, the
global pairing and competing owners. Click a bead for its saved surface,
reflection, physical and numerical status. Select different overlay layers
independently. Both index and photographic-arc plots are downloadable.

The delivered forward records are immutable inputs to review. Commands used:

```sh
.venv/bin/python -m photo2.r304.forward
.venv/bin/python -m photo2.r304.analyze
.venv/bin/python -m photo2.r304.plots
.venv/bin/python -m photo2.r304.verify
.venv/bin/python -m unittest photo2.r304.tests
/home/rharris/.local/bin/beads-chromium-review photo2.r304.browser_check
```

`forward` refuses to overwrite existing model exports. For a fresh forward run,
use a separate repository checkout and a separate output destination (change
`BASE` and `REVIEW` in that isolated copy); do not delete or replace delivered
scientific artifacts. `verify` replays all native rasters, positions, boundary
segments and contact witnesses, then evaluates the entire region on a half-pixel
grid without changing geometry. It writes verification receipts only.
`analyze` and `plots` rebuild derived comparisons and viewer data from the saved
predictions; they never fit parameters. No new detections are required.

Machine-readable files under `photo2/r304/results/`:

- `{model}.json.gz`: every core/guard address, 3-D/projected centers, axis/phase,
  visible area, reflection, boundary segments, physical witnesses and provenance.
- `{model}-raster.npz`: native owner addresses, intensities, unknown-ray mask,
  isolated projected counts and bounding rectangle. Background sentinel −32768.
- `{model}-guard-check.json.gz`: full pixel comparison with 96 rather than 64
  guards per side and extended contact checks.
- `{model}-correspondences.json`: original-coordinate pairs, signed residuals,
  all gaps, alternative owners, gap-cost controls, no-gap ordinal control,
  rolling summaries and seven 50-position groups.
- `{model}-material.json.gz`: frozen photographic material/paper tests and native
  outer-envelope comparisons, with uncertainty and eligibility retained.
- `{model}-numerical.json`: per-address half-pixel convergence and lobe ambiguity.
- `{model}-groups.csv`, `{model}-errors-{index,arc}.svg`: exportable tables/plots.

Models are `primary`, `hand-minus`, and `calibrated`. Each starts from its own
R303 shared S1 result. Their conditional addresses are not established physical
identities, and their 350-address geographic extents differ slightly. R294's
red crossing is a landmark only. The preserved photographic observations span
the primary interval; an alternative can leave some unmatched near its end.

No photograph, historical observations, feedback or prior scientific results are
changed. `evidence/preservation.json.gz` records the pre-work hashes. The
initial analysis-order check and interrupted verification are retained as
implementation diagnostics, not hidden discarded scientific fits. R304 contains
no fitting, FFT evidence, new synthetic campaign or color-pattern inference.
