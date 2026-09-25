# Beads reconstruction workflow

Read `SESSION_HANDOFF.md`, the latest `REQUEST_LOG.md` entries, and the relevant
experiment notes before continuing. User instructions override historical plans.

## One-word continuation

When the user says **Continue** as a task instruction (case-insensitive, with
optional punctuation), read the current handoff and carry out its next bounded
step under the workflow below. Check repository/machine state, record the
request, explain this step's scope, complete the work and relevant checks, update
the plan/log/handoff, add/commit/push scoped changes, verify delivery, and report
the next model/level and whether to use `/new`. Then stop at the step boundary.
Resume unfinished work before starting a later step. Explicit qualifications,
such as "Continue without pushing", override the default. Quoting or discussing
the word does not launch work. This shortcut does not change models or run UI
commands; the user controls `/new`, `/status` and model selection.

## Working rules

- Use Python 3.12, normally `.venv/bin/python`. Keep dependencies local to beads.
- Inspect branch, working tree, upstream, stashes and local machine identity
  before writes. Preserve unrelated/untracked work. Synchronize deliberately;
  prefer fast-forward pulls without rebase or autostash on clean tracked branches.
- Record supplied requests and outcomes in the append-only request log. Record
  actual checks, failures, assumptions and evidence; do not invent observations.
- Keep numerical geometry/analysis in Python and scene appearance in POV-Ray.
  Use deterministic inputs and retain image/source hashes and parameter values.
- "Material" means POV-Ray pigment/finish/normal/interior properties fitted to
  the photo. Physical bead composition is outside the objective (R008).
- Do not equate a photo-sampled render with recovered bead order or a pattern.
  Retain missing bead indices, color uncertainty, competing helicities and
  validation on known synthetic patterns before making inverse claims.
- R069: ignore all slivers/fragments in active inventories; do not spend steps
  resolving their ownership. Compare visible pixel area with nearby bodies,
  especially for small regions near an edge. Keep beads1 marker 211 excluded.
  Preserve historical records and missing indices without absorbing ignored
  pixels into neighbors. See `photo2/INVENTORY_SELECTION.md` for the current
  numerical heuristic; suspected bright point-source lighting is not verified.
- Work toward one useful capability or resolved question per step. Preserve
  enough context to avoid repeating failed approaches; document size is not a goal.
- Keep routine generated outputs, include files and environments out of Git.
  **R065 exception:** commit questions and their curated supporting images;
  use images to illustrate questions whenever helpful. Preserve source inputs,
  hashes and a command that recreates every reported result and illustration.
- Update the handoff with results, checks/skips, limitations and one next task.
  R071: keep a short current progress table at its top, linking each generated
  image's active inventory and unresolved issues. Read this and the latest step
  before historical entries. Scope observation IDs/exclusions to their image.
  For a new palette, review foreground, colors and region masks before applying
  the local-area rule; a bad mask is not evidence of a sliver. Carry warnings
  forward explicitly and keep source-pattern lookup out of image-only review.
  A computer switch needs an explicit transfer of local unpublished changes and
  task ownership. A clean checkout alone cannot establish remote inactivity.
- R006/R010 establish the end-of-step routine: add, commit and push scoped work,
  unless the user qualifies that authorization. Verify push success, remote
  branch tip and final local status before confirming delivery. Report the
  branch/commit and any intentionally excluded files; do not call unpushed work
  pushed or stage unrelated files merely to make the checkout clean.
- At every completed step, recommend the next model and reasoning level, give
  its concrete task and stopping point, and explicitly recommend a fresh `/new`
  or staying in the conversation. The user starts in `~/git/beads`, chooses
  model/level and supplies `/status` output. Record supplied status with session
  attribution; redact secrets, distinguish old/new session data and never invent
  missing usage. No automatic model switch or account inspection.
- Read saved answers before each round. **R065 supersedes the earlier question
  delivery rule:** put future questions in a tracked file, with enough context
  to answer and supporting images where useful; commit the file and images.
  Keep questions focused (normally two or three), avoid repeating answered
  questions, and link the file for the user instead of scattering questions in
  chat. Preserve answers and pending questions in the handoff so a fresh /new
  does not require the user to remember earlier conversations. Questions are
  not extra approval gates for already authorized work. R064 specifically asks
  for this round's questions at the end, with illustrated problems.

The old `image-to-pattern/plan.md` is historical. Its uncompleted inverse gates
remain useful evidence. R059 currently prioritizes generated JPEG inventories
before photographs or pattern inference; the photo-2 forward model remains the
underlying project. The former untracked v2 package/render were preserved on
`archive/image-to-pattern-2-wip` under R012; see `photo2/archive-manifest.json`.
Do not restore archived work into this branch without a task-specific reason.
