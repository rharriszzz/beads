# Beads reconstruction workflow

Read `SESSION_HANDOFF.md`, the latest `REQUEST_LOG.md` entries, and the relevant
experiment notes before continuing. User instructions override historical plans.

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
- Work toward one useful capability or resolved question per step. Preserve
  enough context to avoid repeating failed approaches; document size is not a goal.
- Keep generated images, include files and environments out of Git. Preserve
  source inputs and a command that recreates every reported result.
- Update the handoff with results, checks/skips, limitations and one next task.
  A computer switch needs an explicit transfer of local unpublished changes and
  task ownership. A clean checkout alone cannot establish remote inactivity.
- Commit/push only when authorized by the user. This repository does not inherit
  the vortex lab's automatic publication meaning for the word `Continue`.

The old `image-to-pattern/plan.md` is historical. Its uncompleted inverse gates
remain useful evidence, but this branch follows the user's photo-2 forward-model
task; do not switch branches or overwrite the pre-existing untracked package.
