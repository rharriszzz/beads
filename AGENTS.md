# Beads photo-2 workflow

Read SESSION_HANDOFF.md, the latest REQUEST_LOG.md entries, PLAN.md and the
relevant experiment before continuing. Current user instructions override old plans.
This branch starts at origin/master 020303e (the remote has no main branch).
Historical work remains on photo-2-reconstruction; see photo2/PRIOR_WORK.md.

- Work on one aspect at a time. Present 3–6 methods before selecting a new phase's
  implementation. Ask frequent, small illustrated questions; preserve answers.
  Put questions in tracked files and commit their curated supporting images.
- Background includes all visible paper, including necklace shadows and gaps.
  Prefer color-independent evidence; do not hard-code magenta as the definition.
  R106: all supplied computed/actual images place the bracelet in the middle with
  substantial margins. Use this generic framing prior for background initialization;
  no numeric margin width or bead coordinates are supplied. Enclosed paper and
  gaps remain background even without a connection to the image border.
  R096 notes shadowed-paper/bead HSV overlap; retain texture/context and explicit
  uncertainty rather than forcing a color-only threshold.
  R100–R102 confirm the maker's labeled evidence and identify the overlapping
  white-balanced HSV map; see photo2/HUE_TRANSITIONS.md before reusing ranges.
  Local hue changes can still help; preserve circular hue and image/unit conventions.
- R103: final inference must have little prior knowledge of the image's colors or
  bead locations. Hand-selected routes and saved color ranges are diagnostic/
  validation references, not final runtime priors. Estimate appearance and location
  from each input; test changes of palette, background and placement before claiming
  generality. Do not silently promote diagnostic coordinates or hue boxes into code
  that is presented as automatic reconstruction.
- User R093 rejects the later edge correction's implausible indents and bumps.
  Show raw crops next to candidate outlines and uncertainty before propagating
  those outlines. Do not smooth away real bead-scale scallops indiscriminately.
  R105: when a local boundary is ambiguous, search farther along the necklace
  in either direction for reliable boundary evidence, then bridge using smoothness
  at the larger necklace scale. Keep bead-scale scallops separate. Mark inferred
  stretches distinctly; smoothness alone does not verify an anchor or a gap.
- For shape/geometry/helicity, first read the quick model in photo2/PRIOR_WORK.md.
  Necklace centerline lies in the paper/table plane. Beads are three-dimensional.
  Keep helicity separate from section direction relative to the global camera.
- Use Python 3.12 (.venv/bin/python) for analysis and POV-Ray for scene appearance.
  Material means POV-Ray pigment/finish/normal/interior, not physical composition.
- Preserve missing indices and color uncertainty; test inverse claims against
  known synthetic examples. Photo-sampled rendering is not recovered bead order.
  Ignore slivers in active inventories; historical beads1 marker 211 is excluded.
- Explain measurement paths: raw context, interior endpoints and reasons, sampling
  route, then measurements and limitations. Highlights are not boundary markers.
- Inspect machine, branch, upstream, status and stashes before writes. Preserve
  unrelated work. Synchronize deliberately; no rebase/autostash by default.
- Record supplied requests and actual outcomes in the append-only request log.
  Preserve source hashes, parameters and reproduction commands. Keep routine
  generated outputs and environments ignored; curated question images are tracked.
  INITIAL_QUESTION.md consolidates the opening request and construction facts;
  METHODS.md is the reusable procedure index. Keep proposals, evidence and maker
  facts distinct, and link experiments instead of duplicating their full records.
- Update plan/log/handoff at each bounded step. Add/commit/push scoped work unless
  qualified by the user; verify remote tip and final status before claiming delivery.
- End with a concrete next task, stopping point, model/reasoning recommendation
  and whether to use /new. User controls model/session switching. Do not invent
  supplied status or usage. No computer ownership transfer is implied by checkout.
- A standalone "continue" resumes the unfinished bounded step, then follows this
  routine and stops. Do not automatically advance to the next aspect.
