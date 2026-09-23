# Beads session handoff

Updated 2026-09-23. Working branch: **photo-2-reconstruction**, source/base
`402663eb579a8b66abe553cc3c917ab8f0cbc7c0`. Local checkout is
`/home/rharris/git/beads`, PC/WSL `daisy`. Step 1 was committed and pushed as
`63ba75c` under REQUEST_LOG R006; material clarification was pushed as `1d836cd`.
R010 establishes recurring end-of-step publication verification and model/session
recommendations; this workflow update is prepared for scoped publication.
No computer transfer was requested. Verify another session's release before
concurrent edits; local Git does not reveal its unpublished work or processes.

Read `PLAN.md` for the full objective and Step 1 boundary, `REQUEST_LOG.md` for
all supplied instructions, and `photo2/progress.md` for evidence and failures.
The initial forward model is implemented and checked; real repeat and helicity
are unresolved. The latest code uses **Python 3.12**, `.venv/bin/python`.

## Current capability

`beads.pov` selects photo mode with `Declare=Photo2=1`; its original mode remains.
Python generates a closed spline layout, diagnostics, observations and POV include
data. POV-Ray renders magenta textured paper, area illumination and three glossy
opaque bead proxies. `photo2/README.md` gives commands and coordinate definitions.
All image coordinates are original pixels; physical scale is unknown.

Run:

```sh
.venv/bin/python photo2/reconstruct.py --render --width 800
.venv/bin/python -m unittest discover -s photo2 -p 'test_*.py' -v
```

The comparison is `photo2/output/comparison.png`; the five-section unwrap is
`photo2/output/unwrap-sections.png`. Outputs and `.venv` are ignored and recreated
from tracked source inputs. The copied centerline carries checksums; the source
FFT-explorer checkout is no longer a runtime dependency. Analysis JSON contains
source/image hashes, settings, environment versions and both-sign rankings.

## Evidence and limitations

Five focused tests pass on Python 3.12.14. They establish periodic spline/frame
behavior, handedness reflection, selective color classification, categorical
missing-data period recovery and unknown-residue retention. They do not validate
inverse image recovery. A legacy frame at clock 0.32 is pixel-identical before
and after extracting the shared bead macro. New mode has been rendered at
800x1002 and inspected; no Mac or animation tests were run.

The 2,698 model beads, 415 turns and 6.5 nominal beads/turn are hypotheses derived
from a texture-peak pitch and the old forward model. Current bead orientation,
twist and spacing are visibly too regular. "Material" specifically means POV-Ray
pigment, finish, normal and interior properties (R008). The existing glossy
opaque settings are initial values; fitting them to the photo remains work. The best
period scores are only about 0.45 versus majority baselines 0.41–0.43, with
different observations for each sign. No period or helicity is accepted.

The old inverse attempts failed at color/geometry/order stages. Read
`photo2/BRANCH_REVIEW.md` before borrowing them. The user instructed reading all
branch Markdown except POV-Ray/physical Navier–Stokes and workflow-only lab.
This was completed by distinct blob, with scope recorded in that review.

## Next task

Label visible bead centers/colors in several separated sections of the unwrapped
rope, including both bends and straight sections; fit pitch, circumference
count, phase, local twist and hole-axis tilt against a common observation set.
Report residuals on held-out patches and compare both hands without changing
the observations. Stop after that geometry comparison or an evidenced ambiguity;
do not promote a repeat merely because it improves the rendered appearance.

This needs geometric/inverse reasoning, so Astra/high remains a suitable choice
from the user's supplied catalog. Once fitting equations and acceptance checks
are settled, a specified implementation can use Sol/medium or high. No model
switch or delegation occurred; availability should be checked in the next session.

## Next session and end-of-step reporting

For the next geometry-fitting step, use **gpt-6-astra / High**, starting a fresh
conversation in `~/git/beads`. The user will use `/new` and `/status`; preserve
the supplied status excerpt in the request log with session attribution. Initial
task prompt: "Read SESSION_HANDOFF.md and continue with the next step."
No need to reopen this completed setup step or repeat the all-branch review.

At each step end, update records, add/commit/push the scoped changes, verify the
live remote branch tip and local status, then explicitly report delivery and
the next model/level plus whether to use `/new`. Preserve the unrelated files
listed below and distinguish them from undelivered task work. A fresh chat is
recommended here because setup is complete and geometry fitting is a new phase.

Official OpenAI documentation confirms `/new` starts a fresh chat in the same
CLI session and `/status` displays session information. Start Codex with the
correct workspace; `/new` itself is not a directory-change command:
[developer commands](https://learn.chatgpt.com/docs/developer-commands?surface=cli).

## Preserved user work

`beads-render.png` and `image-to-pattern/pattern_from_photo/` were untracked at
entry and must remain untouched and excluded from this step's commit. There
were no stashes. The full legacy test suite has optional GUI/image-analysis
dependencies not required by this new isolated pipeline and was not run.

R011 requests a suggested cleanup method. Recommended, not yet executed: create
`archive/image-to-pattern-2-wip` from the original `image-to-pattern-2` branch,
commit all six files there as unfinished work, push and verify their preservation,
then return to `photo-2-reconstruction`. This clears those untracked files here
while preserving the original branch and the work. Stay in this conversation
for that small task; Sol/Medium is sufficient if a model change is desired.
