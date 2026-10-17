# R310 reproduction

No optimizer is invoked. The primary workflow loads unchanged R306/R309/R297 whole
models and saved native rasters, analyzes both directions, finishes Part A, then
checks curvature, generates review artifacts and independently verifies them:

```bash
python3 photo2/phase2_position_diagnosis.py
photo2/review/r310/launch.sh
```

It automatically selects this checkout's `.venv` and bounds numerical library
threads. Python performs systematic analysis without an AI supervisor. Results
are deterministic except timestamps/timing. It writes only R310 artifacts.
The saved models, parameters, photograph and historical observations remain read-only.
A failed stage can be rerun with `--stage partA`, `--stage curvature`,
`--stage review` or `--stage verify`; curvature requires the Part A completion
record. Whole models remain represented even for local isolated-projection controls.
An isolated-bead query is a visibility diagnostic, never a changed fitted model.

```bash
/home/rharris/.local/bin/beads-chromium-review photo2.r310.browser_check
```

The browser check uses the actual launcher, native-coordinate raw panels, all three
models, ±320-index navigation, click-to-recenter, model switching at fixed photo
coordinates, competing-owner buttons, every atlas image, narrow view and offline
loading. The trusted wrapper permits the localhost socket needed by Chromium.
No observed Windows browser launch is claimed.

Start independent review at `r310/results/summary.json`, then
`partA.json.gz`, each `*-partA.json.gz`, `partA-controls.json.gz`,
`individual-discrepancies.csv`, `prefixes.csv`, `geographic-prefixes.json`,
`neighbor-vectors.json.gz` and `curvature.json.gz`. The complete source models are
linked by path and SHA256; every Part A file includes its unchanged parameters.
The viewer keeps full native boundaries for all7475 bodies; the ordered atlas uses
identical photographic crop coordinates for all models. Index labels are conditional.

`verification.json` independently compares original Python rays and isolated
projections, all saved positions,640 outward steps/model plus each reference,
and native boundary segments, photographic pixels and arithmetic. It also checks
pre-run preservation hashes. Root handoff documents may only be additive.
`source-manifest.json` records final implementation hashes, and `delivery.json`
records the independently verified scientific push.

The fixed normalization is D=36.878px (R309 B14 measurement rounded as requested),
with conservative ±6px reference-size uncertainty. Raster distances are to native
pixel-center material sets, not hidden physical bead centers. No physical neighbor
identity or center uncertainty is fabricated from an interior centroid/highlight.
All comparison evidence has been seen historically; no fresh blind validation.
Stop after review delivery. No fit, Phase3 or color-pattern inference.
