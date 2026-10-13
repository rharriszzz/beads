# R270 evidence

[Scientific report](../../BRIGHTNESS_COMPARISON_R270.md) · [All independent maxima](MAXIMA_INDEX.md)

Start with the [pale-peak score comparison](R01284-pale-peak-score-comparison.png) and [separate neighboring origins at every score/window](R01284-separate-neighbors-all-measures.png), plus [permissive boundary failures](R01284-permissive-boundary-failures.png). Photographic displays use ICC-converted sRGB. Historical V and experimental V/S use original native RGB; standard Y/OKLab use ICC-converted sRGB, as documented in color-profile.json. The initial all-native-as-sRGB experiment survives in native-rgb-control.

| Example | Original photograph and all four measures |
|---|---|
| R00956 upper-yellow | [5/7/9 paths and endpoints](R00956-upper-yellow-four-measures.png) |
| R00956 middle-yellow | [5/7/9 paths and endpoints](R00956-middle-yellow-four-measures.png) |
| R00956 lower-yellow | [5/7/9 paths and endpoints](R00956-lower-yellow-four-measures.png) |
| R01284 central-yellow | [5/7/9 paths and endpoints](R01284-central-yellow-four-measures.png) |
| R01284 shadowed-neighbor | [5/7/9 paths and endpoints](R01284-shadowed-neighbor-four-measures.png) |

All previously displayed supported coordinates: [R00956](R00956-current-supported-four-measures.png), [R01284](R01284-current-supported-four-measures.png).

- `candidate-points.json`, `*-candidate-measurements.csv`: union of every independent raw/mean maximum and prior candidates, cross-score values, prominence/context censor flags and original HSV/background evidence.
- `*-fields.npz`: source native RGB, ICC-managed sRGB, fixed native HSV/background, unrounded float64 score rasters, raw 1e-9-unit integer scores and exact 5/7/9 sums.
- `starts.json`, `legacy-starts.json`: all original starts, plus each measure’s own independent raw/mean maximum pixels. No V-prominence gate.
- `photo-climbs.jsonl.gz`: every guarded/unguarded prefix, step, score, blocked alternative and stationary-plateau diagnosis.
- `photo-searches.jsonl.gz`, `search-endpoints.csv.gz`: every radius/policy/measure result and selected route. Named examples also preserve full reachable predecessor trees and blocked frontier edges.
- `focus-results.json`, `focus-candidate-decisions.csv`, `alternative-paths.jsonl.gz`: every named-example endpoint and candidate decision; direct violations, shortest admissible and greatest raw/mean-bottleneck paths.
- `pale-peak-matched-coordinates.{csv,json}`, `common-guard-comparison.csv`: matched-point score rankings and original-V-anchor/raw-guard control.
- `native-rgb-control/`: preserved initial experiment treating native RGB as sRGB; it isolates the newly inspected ICC-profile issue.
- `synthetic-inputs.npz`, `synthetic-truth.npz`, `synthetic-fields/`, `synthetic-starts.json`, `synthetic-results.csv`, `synthetic-*.jsonl.gz`: complete known-scene arrays, all raw/mean maximum masks and paired paths. Truth is evaluation-only.
- `input-hashes.json`, `artifact-hashes.json`, `validation.json`, `tests.log`, `budget.json`: old evidence preservation, exact baseline replay, numerical checks and shared 30-minute compute deadline.

Reproduce (Python 3.12 environment):

```sh
MPLCONFIGDIR=/tmp/beads-r270-mpl .venv/bin/python -m photo2.bead_detection.experiment_r270
MPLCONFIGDIR=/tmp/beads-r270-mpl .venv/bin/python -m photo2.bead_detection.synthetic_r270
MPLCONFIGDIR=/tmp/beads-r270-mpl .venv/bin/python -m photo2.bead_detection.review_r270
MPLCONFIGDIR=/tmp/beads-r270-mpl .venv/bin/python -m unittest photo2.bead_detection.test_brightness_r270 > photo2/review/r270/tests.log 2>&1
MPLCONFIGDIR=/tmp/beads-r270-mpl .venv/bin/python -m photo2.bead_detection.validate_r270
```

For a fresh run, archive the completed R270 directory first; experiment_r270 initializes a 30-minute deadline only when budget.json does not exist. Production detector, growth, viewer, bead geometry and indexing remain untouched.

Coordinate convention: photographic paths, starts and endpoints use full-photo native
(x,y). Plateau `canonical` entries within climb diagnostics use the saved field's
local coordinates; add that field's origin to recover full-photo coordinates.
Synthetic coordinates are local to the synthetic image.

Synthetic review: [colored highlights](synthetic-colored-highlight-comparison.png), [luminance background exit](synthetic-Y-raw24-mean2-background.png), [invisible boundary](synthetic-Y-raw24-mean2-invisible-boundary.png).
