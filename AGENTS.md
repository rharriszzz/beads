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
  R108: background separation serves a useful smooth spline that excludes cast
  shadow. Do not require pixel-perfect masks before later geometry refinement;
  prioritize broad shadow-induced bias, supported coverage and explicit uncertainty.
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
  R111: explore FFTs for background/shadows and for directions/spacings/helicity,
  but adoption is optional and not a gate before useful index/color work. Target
  bead_index and color for every clearly visible body; keep observation IDs,
  local component indices and resolved full-string indices distinct. Unresolved
  visible bodies remain in coverage accounting instead of being dropped.
  R117 supersedes a black-bead exclusion: black bodies are locatable, roughly
  twice as difficult per the maker, not unusable. Establish a 5–12-body patch;
  use Python placement/projection or walk the six neighbor directions around
  the necklace. R118–R119's outward anchor is in the minor-circle direction,
  away from the rope's local centerline; validate its exposure separately.
  R120–R121: ignore edge/behind-edge beads in active fitting and walking; target
  substantial central bodies, including black. Preserve excluded regions and
  missing slots without requiring their resolution or compressing indices.
  R122–R125: signed direction counts (n1,n6,n7) are useful discussion labels,
  especially for a bead's +/-1, +/-6 and +/-7 neighbors; they need not be the
  fitter's internal coordinates. Derive index = origin+n1+6*n6+7*n7 when supported.
  Different path triples can name the same bead; check weighted sums, retain
  stable observation IDs and mark tentative edges. Source-loop indices
  in calibration are not inferred photo labels. Runtime selection must remain
  image-derived, not fixed color ranges/coordinates. Clear colored beads may seed
  the patch, but the earlier three-body-only shortlist is no longer the goal.
  R127–R128: no camera elevation estimate is supplied. Specular reflection couples
  camera and lighting. Photo was made with an iPhone, likely fairly close; test
  perspective using available metadata without treating unknown crop/distance
  as calibrated intrinsics. A fitted camera/phase gauge is not measured elevation.
  R112: photo-2 repeat length is not divisible by 13; this is not a restriction
  on total bead count or generic synthetic tests. With verified exact N, test
  divisors for the shortest repeat compatible with all visible observations.
  Preserve unknown slots and conflict witnesses; visible-only indices do not
  establish N without closure. Do not claim a recovered pattern from proposals.
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
