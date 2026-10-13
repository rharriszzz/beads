# R268 climbing evidence

[Concise report](../../CLIMBING_MAXIMA_R268.md) ·
[Current selected points and scores](CURRENT_POINTS.md) ·
[Every starting point pictured](START_CARDS.md).

Start with these photographs:

| View | R00956 | R01284 |
|---|---|---|
| Original | [photo](R00956-original.png) | [photo](R01284-original.png) |
| Current supported points, guarded mean7 | [paths](R00956-current-selected12-paths7.png) | [paths](R01284-current-selected12-paths7.png) |
| R267 foreground/size candidates, guarded mean7 | [paths](R00956-r267-candidates-paths7.png) | [paths](R01284-r267-candidates-paths7.png) |
| All starts, guarded mean7 | [overview](R00956-all-paths7.png) | [overview](R01284-all-paths7.png) |
| All numerical endpoints | [CSV](R00956-endpoints.csv) | [CSV](R01284-endpoints.csv) |

Equivalent path views exist at5/9. White squares=start, cyan=path, orange=end.
The all-start overviews can be dense; the numbered contact cards show every start
separately with5/7/9 paths, no overlapping text labels. A route leaving the main
crop is shown in full on its card, not silently clipped from the numerical record.

Useful paired witnesses show original / unguarded / guarded at all three sizes:

- [R00956 upper yellow](R00956-upper-yellow-witness.png),
  [middle yellow](R00956-middle-yellow-witness.png),
  [lower yellow](R00956-lower-yellow-witness.png).
- [R01284 central yellow convergence](R01284-central-yellow-witness.png),
  [shadowed-neighbor crossing](R01284-shadowed-neighbor-witness.png).
- [Initial-guard synthetic cross-body failure](synthetic-failure-legacy-cross-body.png),
  [body-to-background failure](synthetic-failure-body-to-background.png),
  [unobservable-interface failure](synthetic-failure-no-visible-interface.png).

Numerical files:

- `starts.json`:451 unique coordinates and3,163 original source records; stable S
  IDs are local to each crop. P IDs identify old maxima, not bead identities.
- `parameters.json`: exact sum/tie/plateau rules, six guard variants, existing
  learned background parameters and separate confident/context stop definitions.
- `*-score-images.npz`: raw V, exact sum5/7/9 rasters and background stop codes
  (0=allowed,1=confident,2=existing context uncertainty); `origin` is global native
  x,y. The saved extents cover every visited point with measurement context.
  `*-mean{5,7,9}.png` are rounded grayscale displays; NPZ sums are authoritative.
- `*-traces.json.gz`: window→variant→start ID; every actual step records x/y,
  raw V, H/S, exact sum/mean and running raw peak. `blocked` records attempted
  higher-score neighbors/reasons. `plateau` is a diagnostic description, never
  an equal-score move. `stop` distinguishes barriers from true local maxima.
- `*-endpoints.csv`: starts/endpoints, all three before/after means, raw V, score
  gain, step/displacement counts, stop reason, nearest original maximum and
  nearest current supported point. Original-maximum lookup covers the full photo.
- `*-convergence.json`: exact endpoint and separate equal-plateau groups for every
  variant. `convergence-review.{json,csv}` and `convergence-summary.json` compare
  raw/current/R267-active origins; no groups become bead identities.
- `current-selected12-comparison.csv`, `curated-witnesses.json`: precise values
  and final blocking edges behind the concise report and paired figures.
- `synthetic-inputs.npz`, `synthetic-truth.npz`:100 known scenes, truth withheld
  from inference. `synthetic-results.csv` retains every scene/window/control and
  separates all raw body starts from the prominence12 subset.
- `synthetic-traces.jsonl.gz`: one trace per line with scene/window/variant,
  image-derived start index, withheld start/end truth and full trace.
  `synthetic-failure-witnesses.json` contains the illustrated failure traces.
- `legacy-color-definition.json`, `legacy-color-photo-hashes.json`: preserve the
  initial two-bright-pixel color guard as `legacy-color12`; its photographic
  trace hashes reproduce exactly. `synthetic-failure-pre-fix-cross-body.png` is
  the original illustration before this repair; the labeled legacy witness is
  the current comparison.
- `photo-summary.json`, `synthetic-summary.json`, `tests.log`, `validation.json`,
  `input-hashes.json`, `artifact-hashes.json`: numerical checks and preservation.
  All old R267 evidence and production sources are untouched.

Reproduce from the repository root (Python3.12 environment):

```sh
MPLCONFIGDIR=/tmp/beads-r268-mpl .venv/bin/python -m photo2.bead_detection.experiment_r268
MPLCONFIGDIR=/tmp/beads-r268-mpl .venv/bin/python -m photo2.bead_detection.synthetic_r268
MPLCONFIGDIR=/tmp/beads-r268-mpl .venv/bin/python -m photo2.bead_detection.review_r268
MPLCONFIGDIR=/tmp/beads-r268-mpl .venv/bin/python -m unittest photo2.bead_detection.test_climb_r268 > photo2/review/r268/tests.log 2>&1
MPLCONFIGDIR=/tmp/beads-r268-mpl .venv/bin/python -m photo2.bead_detection.validate_r268
```

No viewer/site changes, production detector changes, external messages, subagents,
watershed, old geometric model, outline optimization or manual bead identities.
