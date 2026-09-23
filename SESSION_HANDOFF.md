# Beads session handoff

Updated 2026-09-23 after R014. Branch: **photo-2-reconstruction**, checkout
`/home/rharris/git/beads`, PC/WSL `daisy`. Entry commit `f6fb3b3` matched origin;
R014's scoped source/data/docs are prepared for authorized commit/push. The final
response reports the verified delivery commit. No computer transfer requested;
local Git/process inspection cannot establish other-machine inactivity.

Read `PLAN.md`, latest `REQUEST_LOG.md` and `photo2/progress.md`. Python is
**3.12.14**, normally `.venv/bin/python`. User instructions override prior plans.
**Continue** launches the next bounded task and the full publication/handoff
routine in AGENTS.md. Resume unfinished publication before starting another task.

## Current capability and latest result

The initial Python/POV-Ray forward model renders photo 2 using a saved closed
spline, adjustable paper/light and provisional glossy bead materials. Legacy mode
is preserved. Commands and coordinates are in `photo2/README.md`.

R014 adds `photo2/geometry-labels.json` (103 provisional visual center/color
labels, six straight/bend patches) and `photo2/fit_geometry.py`. See
**`photo2/GEOMETRY.md`** before further geometry work. Labels are assistant visual
estimates, not human-reviewed or complete segmentation; original indices stay
null, and colors do not enter geometry scoring.

Both hands use the same observations. Shared pitch/count/radius fit 51 training
centers; three separate patches calibrate local phase/offset on 25 left-half
centers and withhold 27 right-half centers. This is partial patch holdout, not
prediction of whole patches without calibration. Withheld RMSE is 6.2728 px for
negative versus 6.4124 px for positive; patch preferences disagree. Original-photo
residuals are similar. Typical annotation uncertainty is estimated at 4 px, with
worse dark/edge beads possible. **No hand, count, radius or repeat is accepted.**

The sparse point-set objective favors dense models and does not account for true
occlusion. Distinct seeds find competing geometry. Exact tests show that pitch,
beads/turn and unconstrained linear twist can change together without changing
any centers; reported fits fix twist to zero as a convention. Hole-axis tilt and
bead dimensions cannot be estimated from centers alone. There are no reliable
hole-rim landmarks. A front-half visibility assumption breaks an otherwise exact
projected-hand symmetry, but has not been validated as an image model.

Run:

```sh
.venv/bin/python photo2/fit_geometry.py
.venv/bin/python -m unittest discover -s photo2 -p 'test_*.py' -v
.venv/bin/python photo2/reconstruct.py --render --width 800
```

Geometry outputs are `photo2/output/geometry-fit/report.json` and six
`*-comparison.png` files with source/labels/both fits. The report binds source,
image and label hashes, settings, environments and results. All generated outputs
and `.venv` remain ignored; tracked inputs reproduce them. Nine focused tests
pass. Two complete deterministic geometry runs reproduced the numerical result.
No render code changed in R014, so the earlier legacy pixel-equality check was
not rerun. No Mac, animation, camera comparison, synthetic-image recovery,
material fitting or real-repeat validation was done in this step.

The baseline still has 2,698 beads, 415 turns and nominal 6.5 beads/turn: these
remain hypotheses, not updated measurements. Its exploratory repeat scores near
0.45 used different observations per sign and are not a controlled comparison.
"Material" means fitted POV-Ray properties (R008), not physical composition.
Do not equate photo-sampled appearance or temporary fit assignments with order.

## Next task and stopping point

Build a small **occlusion-aware synthetic patch benchmark** in POV-Ray with
known bead IDs, body dimensions, hole-axis tilt and both hands. Use Python to
score visible centers and body outlines, exposing density bias and missing-label
sensitivity. Determine which observations recover or correctly reject the known
geometry. Stop after a reproducible benchmark report and focused checks, or an
evidenced ambiguity. Do not refit real-photo geometry or resume repeat search
in that bounded step. PLAN Step 2 remains open.

Use **gpt-6-astra / High** and a fresh **`/new`** in `~/git/beads`; supply `/status`
and **Continue**. This is a task-based recommendation for geometric/visibility
reasoning, consistent with [official reasoning guidance](https://developers.openai.com/api/docs/guides/reasoning)
checked through OpenAI Docs in R014. It does not claim a measured model comparison.
The user's supplied current model/status/usage is recorded with session
attribution under R014; no model switch or account inspection occurred.

At each step end, update plan/log/handoff, add/commit/push scoped changes, verify
live remote branch tip and final local status, and report branch/commit,
intentional exclusions, next model/level and fresh-versus-current conversation.

## Preserved history

Step 1: `63ba75c`; material clarification: `1d836cd`. R006/R010 establish the
recurring publication authorization, R013 the Continue shortcut. The all-branch
Markdown review is complete in `photo2/BRANCH_REVIEW.md`; do not repeat it.
Old `image-to-pattern/plan.md` is historical; its inverse gates remain useful.

The six former untracked files (prior PNG plus five `pattern_from_photo` files)
are archived byte for byte on **archive/image-to-pattern-2-wip** at
`debec4056a30a2206f73a30b40dec8aab9bb3b79`. `photo2/archive-manifest.json`
records hashes/sizes and the archive identity. Archive push succeeded after a
GitHub internal-server-error retry and its remote tip was verified under R012.
The original `image-to-pattern-2` stays at `402663e`; do not restore the archive
without a task-specific reason. No stashes or user files were discarded.
