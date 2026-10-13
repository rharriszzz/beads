# R269 photographic evidence

[Concise report](../../BROADER_PEAK_SEARCH_R269.md)

Also compare all previously displayed supported coordinates: [R00956](R00956-all-current-supported.png) and [R01284](R01284-all-current-supported.png). `current-supported-comparison.csv` records each outcome.

Start with the [missed-looking central peak](R01284-missed-looking-peak.png), [exact five-pixel route](R01284-exact-five-pixel-route.png), [nearby mean-peak route](R01284-central-alternative-route.png), and [separate-neighbor controls](R01284-separate-neighbor-controls.png).

| Example | Original and 5/7/9 paths | All competing points | Measurements and exact decisions |
|---|---|---|---|
| R00956 upper-yellow | [comparison](R00956-upper-yellow-comparison.png) | [numbered photo](R00956-upper-yellow-all-peaks.png) | [table](R00956-upper-yellow-PEAKS.md) |
| R00956 middle-yellow | [comparison](R00956-middle-yellow-comparison.png) | [numbered photo](R00956-middle-yellow-all-peaks.png) | [table](R00956-middle-yellow-PEAKS.md) |
| R00956 lower-yellow | [comparison](R00956-lower-yellow-comparison.png) | [numbered photo](R00956-lower-yellow-all-peaks.png) | [table](R00956-lower-yellow-PEAKS.md) |
| R01284 central-yellow | [comparison](R01284-central-yellow-comparison.png) | [numbered photo](R01284-central-yellow-all-peaks.png) | [table](R01284-central-yellow-PEAKS.md) |
| R01284 shadowed-neighbor | [comparison](R01284-shadowed-neighbor-comparison.png) | [numbered photo](R01284-shadowed-neighbor-all-peaks.png) | [table](R01284-shadowed-neighbor-PEAKS.md) |

Numerical files retain all 451 original starting coordinates and their sources. Every original R267 raw maximum is present in the competing-point inventory; new mean maxima and old R268 endpoints remain separate types. No proposal receives a manually assigned bead identity.

- `*-all-competing-points.csv`, `all-competing-points.json`: raw V, all three means, exact raw prominence, H/S, RGB and original IDs.
- `*-search-endpoints.csv`: all four radii and four policies for all starts/windows.
- `photo-search-traces.jsonl.gz`: every winning route, reconstructible predecessor tree to every reachable point, and every blocked frontier edge with reasons. Tree predecessors are flat indices in the saved graph shape/origin.
- `focus-candidate-decisions.csv`: accept/reject reason and certified bottleneck capacities for every nearby competing point in each named example/control.
- `focus-alternative-paths.jsonl.gz`: direct route and its violations, shortest admissible route, best raw-bottleneck color-only route, best mean-bottleneck raw/color route and best raw-bottleneck mean/color route.
- `r268-final-eight-neighbors.csv`: the exact eight alternatives at each old stopping point.
- `*-score-images.npz`: original native RGB, HSV, V, exact score sums and unchanged background codes across the full search halo.
- `synthetic-starts.json`, `synthetic-results.csv`, `synthetic-search-traces.jsonl.gz`: every raw synthetic maximum, image-only eligibility, all controls and full selected traces; ground truth is evaluation-only. Original scene arrays remain in R268.
- `input-hashes.json`, `artifact-hashes.json`, `validation.json`, `tests.log`: preservation and numerical checks.

Reproduce from the repository root:

```sh
MPLCONFIGDIR=/tmp/beads-r269-mpl .venv/bin/python -m photo2.bead_detection.experiment_r269
MPLCONFIGDIR=/tmp/beads-r269-mpl .venv/bin/python -m photo2.bead_detection.synthetic_r269
MPLCONFIGDIR=/tmp/beads-r269-mpl .venv/bin/python -m photo2.bead_detection.review_r269
MPLCONFIGDIR=/tmp/beads-r269-mpl .venv/bin/python -m unittest photo2.bead_detection.test_search_r269 > photo2/review/r269/tests.log 2>&1
MPLCONFIGDIR=/tmp/beads-r269-mpl .venv/bin/python -m photo2.bead_detection.validate_r269
```

Production detector, previous evidence, outlines, geometry and indexing remain unchanged.

Synthetic failure review: [unrestricted cross-body](synthetic-cross-body-radius-only.png), [guarded background exit](synthetic-background-raw24-mean2.png), [unobservable boundary](synthetic-unobservable-raw24-mean2.png).
