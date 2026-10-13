# R267 photographic maxima audit

[Findings and explanation](../../LOCAL_MAXIMA_R267.md).
Numbers label native maximum pixels; P IDs label plateaus, never bead identities.
The production detector and all previous evidence are unchanged.

Start with the originals and numbered tables:

- [R00956 original](R00956-original.png), [all maxima](R00956-all-square7.png),
  [table](R00956-TABLE.md), [fixed-background candidates](R00956-fixed-background-square7.png).
- [R01284 original](R01284-original.png), [all maxima](R01284-all-square7.png),
  [table](R01284-TABLE.md), [fixed-background candidates](R01284-fixed-background-square7.png).
- [Every R266 selection explained](SELECTION_EXPLANATIONS.md), including all six
  straight/annular × 12/6/3-DN saved variants and exact weighted score terms.
- [Neighbor-failure photograph](R01284-neighbor-failure.png).

Latest user steering: discard small ambiguous regions. Final candidate-review
views use the established background plus **support ≥12 native pixels**:
[R00956](R00956-fixed-background-size12-square7.png),
[R01284](R01284-fixed-background-size12-square7.png).
The parallel `hue-only-size12-*.png` views test the existing learned paper hue
alone; its broad band also removes some tinted reflections, so it is not adopted
as a production background replacement. All six means have both views.
`hue-size-candidate-decisions.csv`, `hue-size-growth-sizes.json` and
`hue-size-summary.json` preserve every exclusion and the exact fixed parameters.
`*-hue-size-selection.json` keeps both candidate and suppression inventories.

For each crop, six `all-{square5,square7,square9,disk2,disk3,disk4}.png` maps show
**every** native maximum pixel with nonoverlapping labels and ranking colors.
The matching `rank-*.csv` files are independently ordered by that measurement.
`all-maximum-pixels.csv` contains unrounded means/ranks, peak V, exact prominence,
H/S, original representative flag, old status/reason/suppressor, old mixed score
and median/quartile, and separate displayed coordinate. `plateaus.json` preserves
full equal-V plateaus, including crop-crossing plateaus. Native originals are
saved alongside nearest-neighbor enlargements; analysis never uses enlargements.

`comparison.png` shows raw/selected12/ungated mean7 points. `old-seeds.png` and
`straight-0-selected{6,3}-seeds.png` are legibly numbered prior-seed maps.
`candidates-*.png` / `selection-experiment.json` deliberately bypass eligibility
gates as an all-raw control. `fixed-background-*.png`, `fixed-background.csv` and
`fixed-background-selection.json` hold existing background tests and recorded
paper deferrals fixed. Do not infer bead counts from either diagnostic inventory.
`fixed-background-summary.json` states the exact reuse and pre-growth limitation.

`r266-statuses.json` preserves all six runs' original selection statuses, scores,
background evidence, peak/display coordinates, support sizes and prominence gate.
`r266-local-associations.json` preserves the original selected12 direct bridge
measurements. `selected-decision-ledger.{json,csv}` explains every selected record;
`table-validation.json` explicitly flags retained records with stale suppression
reason strings. Actual status/membership takes precedence over those old strings.

`coordinate-comparisons.{json,csv}` compares every selected12 seed with the highest
mean within its **unverified** direct-compatible neighborhood, separately for all
six methods. `pair-controls.json` saves accepted/rejected bridge evidence. This
is not a bead grouping: the neighbor-failure photograph shows an unsafe match.
`frozen-growth.json` and `frozen-growth-comparisons.csv` preserve masks/stops and
old-mask equality checks for the unchanged growth control. `frozen-growth.png`
shows original/old-seed/new-seed panels with native unsmoothed mask edges.
No outline parameters were changed or optimized.

`manifest.json` contains input/source hashes, full-photograph maxima equality,
label checks and definitions. `control-summary.json` summarizes frozen replays.
`validation.json`, `tests.log` and `artifact-hashes.json` contain final checks and
provenance. Reproduce with the report's commands; all numerical work is Python.
No viewer/site changes, external messages, subagents or deployment were used.
