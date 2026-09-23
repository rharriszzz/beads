# Beads session handoff

Updated 2026-09-23 after R024 opening questions/status. Branch: **photo-2-reconstruction**,
checkout `/home/rharris/git/beads`, PC/WSL `daisy`. R024 entry `a3f130f` matched origin;
R023 completed the illustrated visibility step. The final
response reports the verified delivery commit. No computer transfer requested;
local Git/process inspection cannot establish other-machine inactivity.

R024 opens the new round; no method review or experiment has started. Current
supplied session is `01a0d01f-e860-71b3-9e18-4bfc4162d0cc`, gpt-6-astra / High.
Prior-session timing/token totals belong to `01a0d004-cac1-7443-88ad-b2ff19ab6dfa`;
see REQUEST_LOG for separate attribution. Stay in this conversation for answers
and the planned method-selection task; no additional /new is needed now.

Opening questions pending (asked through the question tool):

1. For photo 2, which bead colors were intentionally used, including similar
   shades that reconstruction should keep separate?
2. Are stringing repeats checked/corrected before crochet, or should recovery
   allow occasional extra, missing or wrong-color beads? Any known photo-2
   exceptions? This asks about errors, not the already answered whole-repeat rule.

Save replies here; do not repeat these questions or assume answers. They inform
the observation/error model without creating an approval gate.

Read `PLAN.md`, latest `REQUEST_LOG.md`, `photo2/progress.md` and
**`photo2/VISIBILITY.md`**; `photo2/PRACTICE.md` is its source-scene context.
`photo2/SYNTHETIC.md` remains historical evidence. Python is **3.12.14**, normally `.venv/bin/python`.
User instructions override prior plans. **Continue** launches the next bounded
step and the publication/handoff routine in AGENTS.md. Resume unfinished
publication before starting another task.

## Current capability and latest result

R023 traces actual legacy bead indices and repeat slots through two practice
phases for the 40-color/800-bead example and a 13-color/780-bead example. The
tracked scene and photo settings are unchanged. Separate generated ID passes
match original-palette silhouettes/colors exactly. Every 40-repeat slot has
at least ten >=100-pixel occurrences in each view. The 13-repeat phase-half
view exposes slot 0 only through small gaps: four >=12-pixel occurrences, none
>=100; strongest #533 exposes 69/4094 pixels (1.6854%). Some quarter-ring sections
miss several slots. These oblique full-ring views do not produce an entirely
hidden slot at the 1-pixel threshold; no universal completeness claim follows.

Reproduce with `.venv/bin/python photo2/legacy_visibility.py` after R017 practice
outputs exist. Final inspected run: `photo2/output/legacy-visibility-verified/`.
See `VISIBILITY.md` for exact reproduction, results, coverage chart, full index
traces and weak-slot close-up. The report preserves all missing indices, source
positions, per-bead pixel counts, per-slot support, commands and hashes. Its SHA-256
is `12ac2b92948e920b89e7da5a49ae1ecfdfcfb44c102d4c07e53606344489c7c0`.
Seventeen tests, compilation, source/artifact hash checks and 16 isolated-body
checks pass. Two runs agree on original numerical results, four geometry CSVs and
22 common rendered pixel arrays. Improved figure labels and four additional
isolated checks were added for the final run. All four trace views, coverage
chart and weak-slot close-up inspected. No recovery, segmentation, literature
review or photo refit. No repeat default-render regression because original
sources are unchanged; R017 source/artifact hashes verified instead.

R017: ran actual legacy `beads.pov` with an invented 40-bead color repeat, 20
groups and two within-case clock values. A small optional pattern override keeps
legacy geometry/materials/camera intact. Results: 800 beads, 123 turns; repeat
occurrences advance 54 degrees around the rope, showing why hidden colors may
be exposed in other occurrences. Full renders and corrected overlap crops were
inspected. This is direct forward-render practice, not an inverse experiment.
See **`photo2/PRACTICE.md`**; reproduce with
`.venv/bin/python photo2/practice_legacy.py`. Generated output is ignored under
`photo2/output/legacy-practice/`, with commands, hashes and renderer logs.
Default legacy before/after renders are pixel-identical; 13 existing tests,
compilation and report source/artifact hash checks pass. Existing renderer gamma
and version-placement warnings remain. No photo fit or color recovery occurred.

The initial Python/POV-Ray forward model renders photo 2 with a saved closed
spline and provisional paper/light/glossy bead materials. Legacy mode remains
preserved. The baseline 2,698 beads, 415 turns and 6.5 beads/turn are hypotheses.
R022: the user says the provisional bead estimate is good enough. Keep 2,698
for current work; do not revise it merely to match R021's usual necklace range.
It remains an estimate, not an exact count constraining pattern divisibility.
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
**That benchmark validates no hand, count, radius, material or repeat for the
photo. R022 separately accepts the provisional count as adequate for current work.**

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

**R016 user constraints supersede the unrestricted geometry search.** Beads are
pre-strung, then crocheted one per chain stitch. Additional twist is small and
limited to matching the ends. Assume bead size/proportions and hole direction
from legacy `beads.pov`; fit image scale. Ask the user about construction details.
PLAN R016 records source values and exceptions. These are authorized assumptions,
not recovered measurements. R015's arbitrary 20-degree tilt and 0.3 hole ratio
are not the required reference geometry. Its unrestricted parameter redundancy
does not establish impossibility under the construction constraints.

**R019 answers from the maker:** the user personally designed and made photo 2's
necklace. They have never designed a multiple-of-13 pattern, but may in future;
retain that synthetic counterexample without treating it as expected for photo 2.
Every crochet stitch is identical and the maker need not worry about rounds.
The half-step advance emerges from how each stitch attaches to the preceding
row. Do not describe this as deliberate alternating rounds or ask the answered
round-count question again. Exact repeat length and attachment mathematics are
still unspecified. No experiment starts from this record-only request.

**R021 answers:** photo 2 settled naturally into the photographed position.
Do not infer zero local twist from this. The maker always uses an integer number
of complete pattern repeats, enough for 700–800 bracelet beads or 3,000–5,000
necklace beads. Require N = kL (integer k) when fitting total count and repeat
length; these ranges are usual construction guidance, not exact photo-2 counts.
R022 supersedes the proposed count revision: 2,698 is an adequate working estimate.
Do not restrict repeat lengths to divisors of that provisional number.
The user believes sufficient information is present and expects an established
algorithm to work. Seek primary-source methods for periodic sequence recovery
with missing observations before custom recovery development; no method has
been selected or validated by this clarification. R023 has now completed the
bounded visibility check; see the results above.

Next task: **review established image-registration and periodic-sequence methods
in primary sources**, choose an approach compatible with unknown bead indices,
missing slots, uncertain colors and whole-repeat closure, and specify a small
synthetic validation using these known legacy renders. Stop with a justified
method choice and concrete test plan, before implementing recovery or photo
refitting. Do not automatically resume the unrestricted R015 model. Continue
with the adequate 2,698-bead working estimate; do not revisit it merely because
of the maker's usual necklace range or restrict periods to its exact divisors.

R023 recommended a fresh `/new`; R024 supplies the new session. **Stay here** for
the opening answers and that distinct method-selection task. Use
**gpt-6-astra / High**, retaining the prior recommendation. This is a task-based
recommendation for scientific/visibility
reasoning, consistent with [official reasoning guidance](https://developers.openai.com/api/docs/guides/reasoning)
checked through OpenAI Docs in R016, not a measured model comparison. User-supplied
prior usage and current status are now separately attributed under R024. No current
usage was invented, model switched or account inspected.

At step end, update plan/log/handoff, add/commit/push scoped changes, verify live
remote tip and final local status, report branch/commit and exclusions, recommend
next model/level and fresh-versus-current conversation, then stop.
**R020 supersedes R018:** begin each work round with two or three focused questions
and enough saved context to answer without remembering the previous session.
Do not append new questions at round end. Save answers here and in the request log;
these are not extra approval gates. R020's questions have now been answered by
R021's natural placement and whole-repeat construction guidance above. Do not
repeat them or invent specific bead edits at the join. R023 continued the round
after those answers, without another question gate. Open the next work round
with contextualized advice questions; R024's pending questions are saved above.

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
