# R271 — trusted location review

Each cyan dot is one automatically accepted location. There are no paths, IDs,
rank labels or outlines on these photographs. The unmarked original is beside it.
These are proposed trusted image locations, not physical bead centers or a bead census.

- [Whole photograph](whole-photo-trusted.png)
- [R00956](R00956-trusted.png)
- [R01284](R01284-trusted.png)
- [Shadowed neighbor: separately excluded](R01284-excluded-shadowed-neighbor.png)
- [Acceptance rule and results](../../TRUSTED_LOCATIONS_R271.md)

All areas, in photograph order (rows top to bottom, columns left to right):

| Row | Left | Left middle | Right middle | Right |
|---|---|---|---|---|
| 1 | [Photo](area-1-1.png) | [Photo](area-1-2.png) | [Photo](area-1-3.png) | [Photo](area-1-4.png) |
| 2 | [Photo](area-2-1.png) | [Photo](area-2-2.png) | [Photo](area-2-3.png) | [Photo](area-2-4.png) |
| 3 | [Photo](area-3-1.png) | [Photo](area-3-2.png) | [Photo](area-3-3.png) | [Photo](area-3-4.png) |
| 4 | [Photo](area-4-1.png) | [Photo](area-4-2.png) | [Photo](area-4-3.png) | [Photo](area-4-4.png) |

## Excluded candidates

Orange dots appear only in these separate diagnostic photographs. Each caption explains why the rule withheld the location.

- [Photograph](excluded-area-1-1.png): Too much of the neighborhood is in deep shade.
- [Photograph](excluded-area-1-2.png): Reasonable neighborhood or search settings choose different locations.
- [Photograph](excluded-area-1-3.png): Too much of the neighborhood is in deep shade. The bright signal falls too much when the neighborhood gets larger.
- [Photograph](excluded-area-1-4.png): Too much of the neighborhood is in deep shade.
- [Photograph](excluded-area-2-1.png): Too much of the neighborhood is in deep shade. The bright signal falls too much when the neighborhood gets larger.
- [Photograph](excluded-area-2-2.png): Reasonable neighborhood or search settings choose different locations.
- [Photograph](excluded-area-2-3.png): The broader search finds a brighter location elsewhere. Two nearby bright peaks lack a clear separating dark valley.
- [Photograph](excluded-area-2-4.png): Too much of the neighborhood is in deep shade. The bright signal falls too much when the neighborhood gets larger.
- [Photograph](excluded-area-3-1.png): Reasonable neighborhood or search settings choose different locations.
- [Photograph](excluded-area-3-2.png): Reasonable neighborhood or search settings choose different locations.
- [Photograph](excluded-area-3-3.png): The 9×9 patch touches paper or uncertain background.
- [Photograph](excluded-area-3-4.png): The 9×9 patch touches paper or uncertain background.
- [Photograph](excluded-area-4-1.png): The 9×9 patch touches paper or uncertain background.
- [Photograph](excluded-area-4-2.png): Two nearby bright peaks lack a clear separating dark valley.
- [Photograph](excluded-area-4-3.png): Reasonable neighborhood or search settings choose different locations.
- [Photograph](excluded-area-4-4.png): Reasonable neighborhood or search settings choose different locations.

## Numerical evidence

`trusted-locations.json` contains the accepted set. `all-candidates.jsonl.gz` and
`candidate-measurements.csv.gz` retain every mean7 maximum plateau, its native
pixels, measurements, decision and reasons. `search-traces.jsonl.gz` preserves
all 18 stability routes for candidates that pass the inexpensive gates. Later
checks are deliberately not run for obvious exclusions; `search_checked` says so.
`candidate-and-background-maps.npz` preserves native maxima and fixed background.
`synthetic-*` uses known scene identities only after selection for evaluation.
`review-checks.json` compares old named coordinates only after detection.

Reproduce in the existing Python 3.12 environment:

```sh
MPLCONFIGDIR=/tmp/beads-r271-mpl .venv/bin/python -m photo2.bead_detection.experiment_r271
MPLCONFIGDIR=/tmp/beads-r271-mpl .venv/bin/python -m photo2.bead_detection.synthetic_r271
MPLCONFIGDIR=/tmp/beads-r271-mpl .venv/bin/python -m photo2.bead_detection.review_r271
MPLCONFIGDIR=/tmp/beads-r271-mpl .venv/bin/python -m unittest photo2.bead_detection.test_trusted_r271 > photo2/review/r271/tests.log 2>&1
MPLCONFIGDIR=/tmp/beads-r271-mpl .venv/bin/python -m photo2.bead_detection.validate_r271
```

Archive the existing R271 directory before reproducing, to preserve this delivery.
