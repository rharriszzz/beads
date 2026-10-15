# R293 priority coverage and evaluation

Source: original photograph and unregistered image-derived centerline. No physical bead quotas or indexing.

| Evidence category | Result | Limit |
|---|---:|---|
| Independent features / within26px / within40px | 1545 / 784 / 1204 | Not physical bead counts |
| Well-observed proxy within26px | 769 | Illumination/contrast/resolution, not mask accuracy |
| Neutral/reflection-like patches within26px | 235 | Not certified black owners |
| stations | 385 | Windows/pairs/references; no completeness claim |
| illuminated_feature_stations | 385 | Windows/pairs/references; no completeness claim |
| any_feature_stations | 385 | Windows/pairs/references; no completeness claim |
| both_side_stations | 358 | Windows/pairs/references; no completeness claim |
| separator_supported_both_side_stations | 303 | Windows/pairs/references; no completeness claim |
| lit_windows_without_feature | 0 | Windows/pairs/references; no completeness claim |
| human_clear_failure_stations | 6 | Windows/pairs/references; no completeness claim |
| opposite_side_pairs | 932 | Windows/pairs/references; no completeness claim |
| separator_supported_pairs | 328 | Windows/pairs/references; no completeness claim |
| ambiguous_near_feature_pairs | 271 | Windows/pairs/references; no completeness claim |
| legacy_near_locations_without_close_feature | 28 | Windows/pairs/references; no completeness claim |

## New frozen population

| Split | Cases | Context strata | Other-feature inclusion flags | Bank flags | Median / worst parameter IoU | Human accuracy |
|---|---:|---|---:|---:|---|---|
| development | 24 | {'red': 7, 'yellow': 9, 'unknown': 8} | 2 | 2 | 0.984 / 0.137 | Pending |
| reserved | 24 | {'yellow': 7, 'unknown': 8, 'red': 9} | 3 | 0 | 0.993 / 0.385 | Pending |

## Coverage limits

All385 sampled photographic windows contain an illuminated feature. This is not evidence of complete bead coverage: multiple highlights, unrepresented surfaces and ownership remain unresolved. 28 old near-centerline locations have no accepted independent R289 feature within8px (22 black-context,6 red-context). These are historical location discrepancies, not28 verified missing beads. The initial narrow arc-window false gap is preserved in checkpoints; final windows use actual26px Euclidean footprints and a40px local arc guard.

All T1–T8 run for every new candidate. Human-reviewed old central clear-photo failures remain separate from lower-priority weak/peripheral uncertainty. Difficult physical silhouettes are not required for photographic interiors/reflections. No fresh physical truth labels, calibrated localization/ownership precision, full photographic completeness or subthreshold-feature recall is established.
