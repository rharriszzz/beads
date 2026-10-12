# R262 preserved evidence

[Report](../../NO_WATERSHED_R262.md). Generation `b75c79224c041afb` preserves all
native maximum candidates, exact supports and centroids, histogram and traces.

- `regions.json.gz`: full candidate catalog and retained/rejected support records.
- `labels.npz`: unique labels, -1 for overlaps, and `membership_count`.
- `growth-traces.tar`: all 7,543 compressed acceptance/predecessor/stopping histories.
- `pair-comparison.json`, `pair-no-watershed.png`: exact motivating-pair comparison.
- `full-validation.json`, `isolation.json`, `browser-checks.json`: completed checks.
- `manifest.json`: artifact hashes. Source photograph hash is in `summary.json`.

Independent overlapping supports are not counted as verified beads. Other detector
issues were deliberately left unchanged for separate work.
