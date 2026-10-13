# R272 evidence

[Open the minimal viewer](../../trusted_inventory_r272/index.html) ·
[Report](../../TRUSTED_INVENTORY_R272.md) ·
[Complete inventory JSON](inventory.json) · [Measurement CSV](inventory.csv)

Open the viewer HTML in a browser. It works directly from disk; no build or server
is required. Keep the viewer directory beside `review/r272`. If serving the repo,
the URL is `/photo2/trusted_inventory_r272/`.

- [Smallest interior](smallest.png), [median interior](median.png), [largest interior](largest.png).
- [R00956](R00956-interiors.png), [R01284](R01284-interiors.png).
- [Whole viewer](viewer-whole.png), [selected largest](viewer-largest.png), [photo without overlays](viewer-photo-only.png).
- [Known synthetic black reflection](synthetic-black-reflection.png).

Excluded diagnostic examples, never promoted to the inventory:

| Failed screening requirement | Example 1 | Example 2 | Example 3 |
|---|---|---|---|
| Background | [Photo](audit-background-nearby-1.png) | [Photo](audit-background-nearby-2.png) | [Photo](audit-background-nearby-3.png) |
| Brightness | [Photo](audit-insufficient-light-1.png) | [Photo](audit-insufficient-light-2.png) | [Photo](audit-insufficient-light-3.png) |
| Even illumination | [Photo](audit-uneven-light-1.png) | [Photo](audit-uneven-light-2.png) | [Photo](audit-uneven-light-3.png) |

`inventory.json` contains all accepted measurements, native inclusive mask runs,
raw/smoothed outlines, parameters and confidence evidence. `inventory.js` is the
same data wrapped for the offline viewer. `photo-srgb.png` is an ICC-corrected
copy of the source photograph, with no spatial resampling or painted annotations.

`location-candidates.jsonl.gz` retains every automatic location candidate and its
original acceptance/rejection reasons. `region-candidates.jsonl.gz` retains all
453 region-stage decisions, including rejected partial measurements.
`single-gate-diagnostics.jsonl.gz` records all 878 diagnostic counterfactuals,
remaining failures and provisional regions. These are not accepted inventory beads.
`requirement-failures.json` gives all per-requirement counts with stage caveats.
`synthetic-region-candidates.jsonl.gz` and `synthetic-ownership.json` retain known
scene results. Synthetic identities enter evaluation only.

`tests.log`, `validation.json`, `browser-checks.json`, input hashes and artifact
hashes record verification and preservation. R270/R271 remain untouched.

Reproduce in the existing Python 3.12 environment, archiving this R272 output first:

```sh
MPLCONFIGDIR=/tmp/beads-r272-mpl .venv/bin/python -m photo2.bead_detection.experiment_r272
MPLCONFIGDIR=/tmp/beads-r272-mpl .venv/bin/python -m photo2.bead_detection.audit_requirements_r272
MPLCONFIGDIR=/tmp/beads-r272-mpl .venv/bin/python -m photo2.bead_detection.synthetic_inventory_r272
MPLCONFIGDIR=/tmp/beads-r272-mpl .venv/bin/python -m photo2.bead_detection.review_r272
MPLCONFIGDIR=/tmp/beads-r272-mpl .venv/bin/python -m unittest photo2.bead_detection.test_inventory_r272 > photo2/review/r272/tests.log 2>&1
MPLCONFIGDIR=/tmp/beads-r272-mpl .venv/bin/python -m photo2.bead_detection.validate_inventory_r272
PLAYWRIGHT_BROWSERS_PATH=/tmp/beads-debugger-browsers MPLCONFIGDIR=/tmp/beads-r272-mpl .venv/bin/python -m photo2.bead_detection.browser_r272
```

The Playwright command uses the already installed local Chromium. The browser may
need permission to run outside the execution sandbox; no external service is used.
