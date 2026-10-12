# R263 parameter search evidence

[Report](../../PARAMETER_SEARCH_R263.md) explains the target, search, failure cases,
limitations and reproduction. All coordinates are native photograph coordinates.

- `search.json`, `parameter-grid.csv`: prominence/noise trials and all256 peak cutoffs.
- `sensitivity.json`, `sensitivity-grid.csv`: one-at-a-time parameter changes.
- `adaptive.json`, `adaptive-*-peak-grid.json`: automatically chosen follow-ups,
  reasons, regression flags and exact minimum-peak profiles.
- `bounded/`: **delivered default**, generation `90b4284f50a29ced`, strict growth,
  prominence35, hue10°,870-pixel pre-retreat ceiling. Full catalog in
  `regions.json.gz`, all1,595 traces in `growth-traces.tar`, `coordinates.csv`,
  `rank-size.csv`, `labels.npz`, `size-distribution.png`, `summary.json`, five
  flagged `overgrowth-candidates.json`, browser screenshots/checks.
- `bounded/*-native.png`, `bounded/*-native.csv`, `bounded/r260-comparisons.json`:
  source pixels and final-versus-R260 comparisons for R01307,R00956,R01284 and
  the motivating pair; no forced bead correspondence.
- `bounded/hue20-to10.json`: native areas, centroids and pixel changes for all
  common retained IDs;59 added and3 lost candidates when tightening20°→10°.
- `bounded-hue20/`, `bounded-hue20-source.py`: preserved earlier20° production
  result and its exact detector source. Run the snapshot with explicit `--image`
  and `--output` paths because its archive location changes its inferred root.
- `bounded-validation.json`, `bounded-isolation.json`: full native-pixel audit
  and byte-identical isolated replay of the delivered result. Corresponding
  `bounded-hue20-*` files preserve the first production checks.
- `biggest-problem.png`, `biggest-problem-closeup.png`, `biggest-problem.json`,
  `biggest-problem-pixels.csv`:186→17,095-pixel failure and exact native pixels.
- `hsv-line.png`, `hsv-line.csv`, `hsv-line.json`:301-pixel native diagnostic line
  across bead/shadow/paper; H, circular hue difference, S, V and membership.
- `shadow-hue-diagnostics.json`: learned-paper compatibility diagnostics.
- `size-audit.json`, `top-native-pixel-axes.png`: saved-file size audit and native
  coordinate crop. Accepted870-pixel ceiling is an operating rule, not a global
  measured bead maximum; see [size reminder](../../BEAD_SIZE_REFERENCE.md).
- `*-regions.json.gz`: retained native runs, coordinates and peak values per trial.
- `*-overlaps.json`, `native-comparisons.json`: exact overlaps and coordinate changes.
- `*-native.png`, `*-native.csv`: original/overlay crops and every pixel's memberships.
- `strict-candidate/`: complete1,533-region candidate, all maxima, histogram,
  coordinates, label/membership rasters and all1,568 compressed growth traces.
- `*-validation.json`, `isolation.json`, `browser-checks.json`: completed audits.
- `*.log`: complete child output, including the incomplete signal9 trial.
- `manifest.json`: hashes; source image and detector hashes are in trial summaries.

Routine full trial outputs and traces remain under ignored `photo2/output/search-r263`.
The strict candidate and both bounded production runs are additionally archived
here for reproducibility. No matching count is represented as verified
one-coordinate-per-bead coverage. Current defaults use the conservative strict
adaptive choice with the subsequently requested870 ceiling and10° hue limit.
Historical experiments remain frozen. `curate_bounded` archives and compares
existing production outputs without running detection.
