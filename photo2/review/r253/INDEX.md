# R253 evidence and reproduction

Read [the scientific report](../../GLOBAL_GEOMETRY_R253.md) first. All identities
and geometry-derived exposure are conditional. R252 source observations are unchanged.

- [Protocol](protocol.json), [split](split.csv), [positive-patch provenance](patch-provenance.json).
- [Broad count scan](scan.json), [rigid refinements](rigid.json), [four variants](ablations.json), [exact ownership registration](polished.json).
- [46-model scalar table](model-comparison.csv), [full statistics](models.json), [heldout and core-heldout scores](validation-scores.json), [color/sector metrics](color-sector-metrics.csv).
- [Every observation's cross-model alternatives](cross-model-identities.json), [maker local chart](maker-local-chart.csv), [maker graph audit](maker-chart-audit.json).
- [FFT integral](fft-count.json), [native frequency components](fft-profile.csv), [correction profiles](correction-profiles.csv), [camera sensitivity](perspective-sensitivity.json).
- [Visibility thresholds and1px replay](visibility-resolution.json), [source integrity](source-integrity.json), [numerical replay](numerical-replay.json), [prediction checks](prediction-checks.json), [tests](tests.txt), [hashes](verification.json).

Each `<model>-assignments.json` contains all310 points, proposed index, exact
surface owner, membership, full-patch support, center/surface distances, alternative
IDs and original provenance keys. `<model>-metrics.json` contains full summaries.

| Conditional model | Full native photo | All physical beads, including hidden | Visibility |
|---|---|---|---|
| N2671_h+1_rigid | [PNG](N2671_h+1_rigid-whole.png) | [CSV](N2671_h+1_rigid-predictions.csv) | [JSON](N2671_h+1_rigid-visibility.json) |
| N2671_h+1_both | [PNG](N2671_h+1_both-whole.png) | [CSV](N2671_h+1_both-predictions.csv) | [JSON](N2671_h+1_both-visibility.json) |
| N2671_h-1_rigid | [PNG](N2671_h-1_rigid-whole.png) | [CSV](N2671_h-1_rigid-predictions.csv) | [JSON](N2671_h-1_rigid-visibility.json) |
| N2679_h-1_twist | [PNG](N2679_h-1_twist-whole.png) | [CSV](N2679_h-1_twist-predictions.csv) | [JSON](N2679_h-1_twist-visibility.json) |
| N2679_h+1_rigid | [PNG](N2679_h+1_rigid-whole.png) | [CSV](N2679_h+1_rigid-predictions.csv) | [JSON](N2679_h+1_rigid-visibility.json) |
| N2679_h-1_rigid | [PNG](N2679_h-1_rigid-whole.png) | [CSV](N2679_h-1_rigid-predictions.csv) | [JSON](N2679_h-1_rigid-visibility.json) |

Full-photo cyan rings are predicted visible-area centroids. Red/yellow squares
are trusted photographed interiors. Magenta connectors indicate surface residual
>6px but run to the projected physical center; they are not surface-distance
vectors or observed bead outlines. All images retain the original pixels.

- [Origin and six directions](indexing-star.png), [anchor comparison](crop-anchor.png).
- [Right section](crop-right.png), [tight bend](crop-bend.png), [left section](crop-left.png), [worst bottom mismatch](crop-bottom-mismatch.png).
- [Count scan](count-scan.png), [hand/count/variant comparison](leading-models.png), [residuals/stretch/phase](residuals-corrections.png), [turn rate](winding-rate.png), [FFT profile](fft-count-profile.png).

Crop labels are signed relative indices for readability; CSV k is modulo N.
The two corrected nominees have different N and hand; the full-photo table also
supplies same-N rigid comparisons. Ambiguous labels are proposals, not confirmations.

Reproduce from repository root with Python3.12:

```bash
.venv/bin/python photo2/global_fit_r253.py scan
.venv/bin/python photo2/global_fit_r253.py refine
.venv/bin/python photo2/global_fit_r253.py polish
.venv/bin/python photo2/global_fit_r253.py audit
.venv/bin/python photo2/r253_diagnostics.py
.venv/bin/python photo2/r253_verify.py
.venv/bin/python photo2/r253_verify.py --resolution
.venv/bin/python photo2/r253_replay.py
.venv/bin/python -m unittest photo2.test_global_fit_r253 photo2.test_tangent_circles photo2.test_positive_registration photo2.test_visible_correspondence photo2.test_consolidate_colored_observations
.venv/bin/python photo2/r253_verify.py --manifest
```

The search exposes `--output` for ignored replay directories. Existing polish/
audit checkpoints are reused; use an empty output directory for a fresh full run.
Diagnostics functions accept an explicit output Path when imported. There is no
external service, unseeded randomness, color-sequence prior or generated appearance.
The exact surface model was historically checked against POV-Ray; this round
uses Python projection/rays and raw-photo overlays, with no new appearance render.
