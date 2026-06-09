# Photo → Bead Pattern: Plan v2

Goal: given a photograph of a crocheted bead-rope bracelet lying loosely on a table,
recover the linear repeating `color_pattern` (and `ngroups`, palette) in the format
consumed by the `#case` blocks of `beads.pov` in the `beads` repo.

This is the second major attempt. The first lives on the `image-to-pattern` branch of
the `beads` repo (`image-to-pattern/plan.md` and the `image_to_pattern/` package).
Read its progress notes before writing code: they are an honest record of what was
tried and how it failed. Treat that history as evidence, not as instructions.

## Context and assets

- Forward model: `beads.pov` (beads repo). Key math: `beads_per_row = 6.5`;
  `nbeads = ngroups * pattern_length`; `nrows = floor(0.5 + nbeads/6.5)`; bead placed
  by `chain_angle = 360*(bead_index/nbeads + ...)` and
  `row_angle = 360*(bead_index/exact_beads_per_row + ...)`.
  The rope is a helix: consecutive beads advance ~1/6.5 of a turn; rows alternate 6/7.
- Rendered fixtures: `beads1.jpg`–`beads8.jpg` (beads repo) are POV-Ray renders of
  the 8 `#case` patterns. Known ground truth, but synthetic lighting/background.
- Real photos: `beads-photo-1.jpg`–`beads-photo-11.jpg` (beads repo) are photographs
  of physical bracelets on magenta paper.
- **Known correspondence:** `beads-photo-4.jpg` is a photo of a bracelet made with
  the same pattern as `beads.pov` case 4 (rendered in `beads4.jpg`). It is the one
  real photo with a known answer — the most valuable single image in the project.
  Other render↔photo pattern matches (with n ≠ m) may exist but are unconfirmed;
  identifying any would expand the ground-truth set cheaply.
- Synthetic data on demand: POV-Ray can render any pattern, and a fast pure-Python
  "flat render" of the visible lattice can be built from the layout math.
- Prior code worth examining: `image_to_pattern/layout.py` + its tests in
  `beads:image-to-pattern` (bead_index → (row,col), 6/7 alternation, all 8 canonical
  POV patterns encoded for testing). The tests pass, but do not assume the math is
  correct — verify it against `beads.pov` independently, and feel free to rewrite it.
- Human-in-the-loop color tools that already exist: `hsv_tools` repo
  (`hsv_picker.py`, `hsv_counts.py`) and the JSON color-config format documented in
  `beads:image-to-pattern/image-to-pattern/color_config.md`.
- Centerline work that exists in the `bead_map` repo (`bead_map.py`,
  `bracelet-pattern-extractor.py`): known to have serious bugs — it finds the
  bracelet edges badly because it is confused by the bracelet's shadows on the
  paper. Useful as a reference for the approach, not as working code.

## Lessons from v1 (history, not law)

- Fully automatic color separation (several k-means / histogram-peak variants) never
  reached usable accuracy on these images; the human-seeded direction (hsv_tools,
  color-config JSON) was created in response and showed more promise.
- End-to-end match rate was the only metric for most of v1, which gave no signal
  about *which* stage was failing. Per-stage metrics arrived late.
- Work moved to hard images before any easier case had been solved end to end, so
  there was never a trusted baseline to regress against.

## Open problems likely needing innovation

The plan deliberately does not prescribe methods here. These are the areas where
fresh research and experimentation are expected:

- Separating bead colors reliably under real lighting (gloss, shadow, background).
- Distinguishing the bracelet from its own cast shadow on the paper — the known
  failure mode of the existing centerline code.
- Finding individual beads in the photo, including partially visible ones.
- Recovering the helical bead ordering — mapping visible beads to positions in the
  one-dimensional chain when roughly half the beads are hidden.
- Inferring the repeating pattern from incomplete, noisy observations.
- Knowing when an answer is right — validation that doesn't depend on already
  knowing the pattern.

## Design principles

1. **Gated milestones.** Do not start a milestone until the previous gate passes
   numerically.
2. **Measure every stage.** Each stage emits a metric and a debug image written to
   `debug-output/` (PNG files, never only interactive windows — must work headless
   on WSL). If a stage cannot be scored, it cannot be trusted.
3. **Append-only progress log.** Keep `progress.md` in this directory: every
   experiment gets an entry with what was tried, the metric, and the conclusion —
   failures included. Never rewrite or delete entries. The v1 log is the only reason
   this v2 plan could be written.

## Milestones and gates

- **M0 — Establish the layout core.**
  New package `pattern_from_photo/` on this branch. Bring over or rewrite the layout
  math and the canonical POV pattern tables from `beads:image-to-pattern`
  (existing tests pass, but verify the math against `beads.pov` independently
  rather than trusting it). Add a pure-Python
  flat render (pattern → image of the visible lattice) for cheap synthetic data.
  *Gate:* layout tests pass on macOS and WSL, including at least one new test
  derived directly from `beads.pov` rather than from the v1 code.

- **M1 — Synthetic round trip.**
  Recover patterns from flat renders, then from the existing POV renders
  `beads1.jpg`–`beads8.jpg` (generate more, varying lighting/background, if useful).
  *Gate:* exact `color_pattern` recovery (period and colors) for all 8 POV cases.

- **M2 — The known photo.**
  Run on `beads-photo-4.jpg`, the one real photo with a known answer (case 4).
  Hand-label its visible beads first so every stage can be scored, not just the
  end result. As a side task, compare recovered patterns (or even just palettes)
  from the other photos against the 8 POV cases to hunt for additional unconfirmed
  render↔photo matches; each one found expands ground truth for free.
  *Gate:* exact pattern recovery on `beads-photo-4.jpg`, with a per-stage accounting
  of where errors occur on any failed attempt along the way.

- **M3 — Unknown-pattern photos.**
  Run on the remaining `beads-photo-*.jpg`, plus calibration-bracelet photos
  if available. Hand-label a small ground-truth set on one or two of them so
  intermediate stages can be scored even though the final pattern is unknown.
  *Gate:* recovered pattern is stable under perturbation (e.g., randomly dropping
  20% of detected beads gives the same answer) and survives visual comparison with
  the photo.

- **M4 — Write it up.** README with CLI usage, any human-annotation workflow, and a
  results table per image.

## Calibration bracelets (new branch in the `beads` repo)

Suggested branch name in `beads`: **`calibration-patterns`**. Add new `#case`
blocks (and renders) for patterns designed to make image analysis easier:

1. **Lighthouse** (Rick's idea): all beads color A except a single bead of color B.
   Isolates geometry completely: the odd bead's reappearances along the rope reveal
   beads-per-turn and helix phase with zero color ambiguity.
2. **Ruler**: color B at every k-th bead (k coprime to 13 = 2×6.5, e.g. 11),
   color A elsewhere — many geometric anchors per window.
3. **Barber pole**: strict A/B alternation (period 2) — any ordering/phase error is
   instantly visible.
4. **Photo-realistic render variant** (optional): table-colored background,
   softer/angled lighting, and if feasible a non-circular centerline, to narrow the
   synthetic-to-real gap. Keep it a separate .pov include.

If a physical lighthouse or ruler bracelet gets crocheted and photographed on the
usual table, that photo becomes the most informative geometry asset in the project.

## Environment and portability (macOS + WSL2)

- Python 3.11+, venv: `python3 -m venv .venv && . .venv/bin/activate &&
  pip install -r requirements.txt`. Same commands on both platforms.
- Likely dependencies: numpy, opencv-python, scikit-image, scipy, matplotlib.
  No GNU-vs-BSD shell tool differences in any required path; any shell helpers must
  be POSIX `sh` compatible. Prefer Python entry points over shell scripts.
- All debug/visual output saved as PNG to `debug-output/` (gitignored). Interactive
  tools may use OpenCV HighGUI or Tk (native on macOS, WSLg on WSL2), but no
  pipeline stage may *require* a display.
- For WSL, keep clones inside the Linux filesystem (`~/git/...`), not `/mnt/c/...`,
  for performance and to avoid permission surprises.

## Instructions for Claude Code

- Work on the branch and repo where this plan lives (`image-to-pattern-2` in the
  `beads` repo). Treat other branches and the `hsv_tools` and `bead_map` repos as
  read-only references; the calibration patterns described above may go on this
  branch or on a separate `calibration-patterns` branch.
- Enforce the gates. If a gate fails, iterate inside that milestone and log every
  attempt in `progress.md` (append-only) with its metric.
- Commit small and often; keep tests green; run the test suite on both platforms
  before declaring a milestone done (a Mac and WSL are both available).
