# R266 evidence

[Report](../../DETECTION_R266.md). Coordinates are native photo pixels; supported
coordinates, area centroids, original maxima and physical bead centers are distinct.
No expected bead count or manual bead locations enter detection.

- `metrics.json`, `coordinate-comparison.json`: 15 separate/joint growth and seed
  controls; all 0/1/2/3-DN running-minimum comparisons, audits and review proxies.
- `refined-metrics.json`: final strict selected12/selected6/selected3 comparisons,
  exact preserved-mask checks and additional native audits.
- `synthetic.json`, `synthetic-truth.npz`, `stress.json`, `refined-synthetic.json`:
  R265 scenes and additional known-truth bodies; `stability.json` saves palette,
  translation and noise perturbations. Synthetic truth is never detector input.
- `missing-seed-prominence.json`: global h-maxima at3/6/12/20/35 DN near existing
  review landmarks; these coordinates select diagnostics only.
- `ranked-examples.json` and `auto-improvements-*` / `auto-regressions-*`: automatic
  largest perimeter/area changes. These are shape proxies, not physical-center error.
- `conservative-R00956.png`, `conservative-R01284.png`, `conservative-R01307.png`:
  raw photograph, R265 strict, final strict straight and annular with12-DN recovery.
  `selected-*` show the6-DN sensitivity. Other identically sampled crops cover
  distributed color transitions, paper contamination and large coordinate shifts.
- Each run directory preserves `regions.json.gz` (all original maxima, statuses,
  masks, coordinates, suppression/deferral evidence) and `coordinates.csv`.
  Unmodified native traces are in parent `traces.tar.gz`; selected runs explicitly
  reference their parent with `trace-source.json`. Packaging verifies the complete
  decompressed tar hash before removing the redundant generated uncompressed tar.
- `refinement-pilot-source.py` preserves the first association refinement before
  smooth-paper-context deferral and gray-reflection correction. The detector itself
  preserves the initial stricter association ablation.
- `checkpoint.json`, `deadline-test.json`, `manifest.json`, `final-manifest.json`:
  original absolute computation deadline, stage results, source/photo hashes,
  parameters and final timing. `recovery-controls.json` and `refinement-status.json`
  record additional trials; a completed stage is never inferred from partial files.
- `final-tests.log`, `browser-baseline-checks.json`, `browser-r266-checks.json`:
  Python and real Chromium validation. Viewer screenshots show native replay and
  inspectable suppressed/deferred candidates, not physical identity verification.

Use the report's commands to reproduce. `experiment_r266 --resume` retains the
original absolute deadline and refuses completed stages with a changed fingerprint.
An early source-change checkpoint reflects the user's strict-descent steering;
subsequent stages use the revised comparison. No deadline was silently reset.
