# R258 review artifacts and numerical summary

[Scientific method and limitations](../../BEAD_DRIVEN_R258.md) · [Debugger instructions](../../bead_debugger/README.md)

Only seven B pixels are maker-confirmed bead2 support. The 49-pixel union was rejected. Full visible area and boundary IoU remain unknown.

## Primary comparison

Ownership means below are averages over observations, using exact native rays on retained positive samples. Bodies are **conditionally distinct proposals**, not verified counts. Entire component groups are held out. Averages include unassigned proposals.

| Section / variant | Train ownership | Held-out ownership | Explained distinct candidates (all) | Physical cost | Max curve movement px |
| --- | ---: | ---: | ---: | ---: | ---: |
| origin A | 0.714 | 0.826 | 4/10 | 0.000000 | 0.00 |
| origin B | 0.734 | 0.758 | 5/10 | 0.000000 | 0.00 |
| origin C | 0.789 | 0.681 | 7/10 | 0.000000 | 9.66 |
| origin D | 0.811 | 0.761 | 6/10 | 0.000000 | 11.77 |
| straight-black A | 0.810 | 0.780 | 9/11 | 0.000000 | 0.00 |
| straight-black B | 0.812 | 0.784 | 9/11 | 0.000000 | 0.00 |
| straight-black C | 0.793 | 0.822 | 8/11 | 0.000000 | 6.41 |
| straight-black D | 0.766 | 0.794 | 9/11 | 0.000000 | 6.37 |
| bend A | 0.682 | 0.819 | 3/4 | 0.000000 | 0.00 |
| bend B | 0.728 | 0.850 | 3/4 | 0.000000 | 0.00 |
| bend C | 0.698 | 0.900 | 3/4 | 0.000000 | 3.06 |
| bend D | 0.824 | 0.853 | 3/4 | 0.000098 | 19.26 |
| opposite A | 0.722 | 0.731 | 4/8 | 0.000000 | 0.00 |
| opposite B | 0.809 | 0.757 | 4/8 | 0.000000 | 0.00 |
| opposite C | 0.855 | 0.941 | 8/8 | 0.001202 | 11.29 |
| opposite D | 0.832 | 0.983 | 8/8 | 0.000037 | 10.67 |

## Explicit post-hoc complexity control

C2 and C4 were tried after the primary held-out regression was observed. These are exploratory controls, not untouched validation.

| Control | Confirmed bead2 pixels owned | Train ownership | Held-out ownership | Max curve movement px |
| --- | ---: | ---: | ---: | ---: |
| R258_origin_C2 | 7/7 | 0.743 | 0.809 | 5.21 |
| R258_origin_C4 | 7/7 | 0.786 | 0.762 | 8.26 |

[C2 raw/old/new bead2 comparison](bead-2-compact-comparison.png). Equivalent clean comparisons are saved for beads0–7.

## Matched count and helicity screens

Each row averages four section holdouts after separate local fits: eight phase starts and220 joint-search evaluations per section, identical evidence, with no predetermined identities. These are not globally closed photo-identity solutions.

| N | h−1 held-out mean | h+1 held-out mean |
| ---: | ---: | ---: |
| 2674 | 0.7563 | 0.8785 |
| 2681 | 0.7092 | 0.8205 |
| 2696 | 0.7463 | 0.8571 |
| 2700 | 0.7507 | 0.8661 |

Both hands/counts remain viable; no exact N, hand, globally verified numbering or repeated color pattern is claimed. Untested counts2670–2700 are not excluded.

## Files

- `results.json`: all primary fit parameters, scores, per-observation residual distributions and spatial cross-evaluation.
- `alternatives.json`: all32 count/hand/section fits and exact evidence scores.
- `compact-controls.json`: C2/C4 exploratory controls.
- `*-evidence.json`: pixels, stable detector IDs, uncertainty, geographic boxes and group splits.
- `bead2-reviewed-support.json`, `questions.json`: maker correction, explicit seven-pixel support and answer history.
- `R258_*.json`: serialized absolute curve knots, camera, phase, winding, count, hand and explicit namespace.
- `model-index.json`:28 additive debugger models; old three models remain unchanged.
- `sensitivity.json`, `ablations.json`: one-parameter tests, bead dimensions and fitted-parameter removals.
- `native-neighbors.json`: native footprint areas/centroids for0–7 and every ±1/6/7 neighbor.
- `index-occlusion.json`: hypothetical index substitutions and explicit ownership limitations.
- `assignment-stability.json`, `fixed-neighbor-correspondences.json`: changed conditional indices and frozen fresh-A match audit.
- `curve-displacements.json`, `packing.json`, `global-summary.json`: geometric changes, six-neighbor distances and partial global curve.
- `synthetic-curve.json`, `synthetic-phase.json`, `validation.json`, `browser-verification.json`: validation.
- `provenance.json`, `artifact-hashes.json`, `immutable-inputs.json`: reproduction inputs and integrity.

## Reproduce

```bash
.venv/bin/python -m photo2.bead_debugger.refit --budget 400
.venv/bin/python -m photo2.bead_debugger.alternatives_r258
.venv/bin/python -m photo2.bead_debugger.compact_r258
.venv/bin/python -m photo2.bead_debugger.audit_r258
.venv/bin/python -m photo2.bead_debugger.global_r258
.venv/bin/python -m photo2.bead_debugger.report_r258
.venv/bin/python -m photo2.bead_debugger.package_r258
.venv/bin/python -m unittest photo2.bead_debugger.test_debugger photo2.bead_debugger.test_surface photo2.bead_debugger.test_refit
node photo2/bead_debugger/static/logic.test.mjs
PLAYWRIGHT_BROWSERS_PATH=/tmp/beads-debugger-browsers .venv/bin/python -m photo2.bead_debugger.browser_smoke --output photo2/output/debugger/smoke-r258
.venv/bin/python -m photo2.bead_debugger.server
```

Python3.12 and existing dependencies. Fresh detection can be reproduced with `python -m photo2.bead_debugger.generate`; normal server startup verifies its cached provenance. Generated native ownership NPZ files are under ignored `photo2/output/debugger/r258/`; the debugger exports selected native owners in each ZIP. Reviews are never automatically consumed by the fitter.
