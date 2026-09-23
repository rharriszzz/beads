# Beads session handoff

Updated 2026-09-23 after R015. Branch: **photo-2-reconstruction**, checkout
`/home/rharris/git/beads`, PC/WSL `daisy`. Entry commit `01dd173` matched origin;
R015's scoped source/docs are prepared for authorized commit/push. The final
response reports the verified delivery commit. No computer transfer requested;
local Git/process inspection cannot establish other-machine inactivity.

Read `PLAN.md`, latest `REQUEST_LOG.md`, `photo2/progress.md` and
**`photo2/SYNTHETIC.md`**. Python is **3.12.14**, normally `.venv/bin/python`.
User instructions override prior plans. **Continue** launches the next bounded
step and the publication/handoff routine in AGENTS.md. Resume unfinished
publication before starting another task.

## Current capability and latest result

The initial Python/POV-Ray forward model renders photo 2 with a saved closed
spline and provisional paper/light/glossy bead materials. Legacy mode remains
preserved. The baseline 2,698 beads, 415 turns and 6.5 beads/turn are hypotheses.
"Material" means fitted POV-Ray appearance properties, not physical composition.

R014 added 103 provisional visual center/color labels and a fixed-observation
both-hand comparison. Withheld RMSE 6.2728 versus 6.4124 px does not select a hand;
labels are incomplete, not human-reviewed, and indices stay unknown. Read
`photo2/GEOMETRY.md` for partial-holdout limits and pitch/count/twist equivalence.
Do not treat photo-sampled appearance or temporary matching as recovered order.

R015 adds `synthetic_benchmark.py`, `synthetic-patch.pov`, tests and SYNTHETIC.md.
Known non-intersecting straight reference patches have 29 visible centers per hand;
12 per hand lie behind the cylinder's front half. POV-Ray measures actual visibility
using exact ID and isolated-bead renders. Centroids differ from true centers by
RMS 1.5336/1.4347 synthetic units; they must not be silently interchanged.

Center-only scoring favors the double-density stress case under noise, and cannot
separate tested body size, hole-axis tilt or depth reflection. Exact internal
visible boundaries distinguish these alternatives, including tested seven-instance
subsets. Depth-reflected silhouettes remain identical. The pitch/count/twist gauge
preserves every body and full rendered mask: no image can resolve it in this model.
**No hand, count, radius, material or repeat is accepted for the photo.**

This benchmark compares twelve discrete candidates per hand at fixed registration,
using perfect instrumentation. Noise applies to centers only; outlines stay exact.
It does not validate segmentation of beauty images, continuous fitting, bend
geometry, perspective or photo-scale accuracy. Dense geometry can intersect and
is explicitly a stress case, not an acceptable physical fit. Partial one-way edge
scores can still favor extra predicted edges. PLAN Step 2 remains open.

Run:

```sh
.venv/bin/python photo2/synthetic_benchmark.py
.venv/bin/python -m unittest discover -s photo2 -p 'test_*.py' -v
```

Default outputs: `photo2/output/synthetic-benchmark/`; final verified local run:
`photo2/output/synthetic-benchmark-verified/`. Each run has `report.json`, exact
render commands, 84 rendered images, two comparison panels and generated includes.
The report binds source/artifact hashes, geometry, environments, bead IDs,
visibility and trial settings. Source inputs reproduce all outputs.

Thirteen tests pass, including an actual POV-Ray full-occlusion check; py_compile
passes. Two full runs reproduced numerical scores, 86 common image pixel arrays
and 24 include-file byte strings. PNG file hashes differ because POV-Ray embeds
render timestamps; actual hashes are retained, with decoded equality verified.
All final report source/artifact hashes match. Beauty and both-hand comparison
panels were inspected. No shared/legacy source changed, so the prior legacy pixel
test was not rerun. No photo refit, material fit, camera comparison, shaded-image
segmentation or repeat search occurred. Generated outputs and .venv stay ignored.

## Next task and stopping point

Test **practical boundary observations from shaded synthetic patches** with
controlled blur/noise and fitted local alignment. Compare extracted observations
against hidden ID-mask truth and measure whether alternatives are rejected or
correctly left ambiguous under observation error. Keep pitch/count/twist equivalence
explicit. Stop at a reproducible validation report and focused checks; do not
refit the real photograph or resume repeat search in that bounded step.

Use **gpt-6-astra / High** and a fresh **`/new`** in `~/git/beads`; supply `/status`
and **Continue**. This is a task-based recommendation for scientific/visibility
reasoning, consistent with [official reasoning guidance](https://developers.openai.com/api/docs/guides/reasoning)
checked through OpenAI Docs in R015, not a measured model comparison. User-supplied
prior usage and current status are separately attributed under R015. No current
usage was invented, model switched or account inspected.

At step end, update plan/log/handoff, add/commit/push scoped changes, verify live
remote tip and final local status, report branch/commit and exclusions, recommend
next model/level and fresh-versus-current conversation, then stop.

## Preserved history

Step 1: `63ba75c`; material clarification: `1d836cd`; R014 geometry: `01dd173`.
R006/R010 establish publication authorization, R013 the Continue shortcut.
The all-branch Markdown review is complete in `photo2/BRANCH_REVIEW.md`; do not
repeat it. Old `image-to-pattern/plan.md` is historical, with useful inverse gates.

The six former untracked files remain archived byte for byte on
**archive/image-to-pattern-2-wip**, commit
`debec4056a30a2206f73a30b40dec8aab9bb3b79`. `photo2/archive-manifest.json`
records hashes/sizes. Remote delivery was verified under R012 after a GitHub
internal-server-error retry. Original `image-to-pattern-2` remains `402663e`.
Do not restore the archive without a task-specific reason. No stashes or user
files were discarded.
