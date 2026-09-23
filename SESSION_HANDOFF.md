# Beads session handoff

Updated 2026-09-23 for R032/R033: renamed the scene option to `Helicity`
and recorded the maker's pattern conventions. Branch **photo-2-reconstruction**,
checkout `/home/rharris/git/beads`, PC/WSL `daisy`; step entry `08ba3bb` matched
origin after fetch. Final response reports the verified publication commit.
No computer transfer requested; local state cannot establish remote inactivity.

Current supplied session: `01a0d047-ddf3-7590-ba43-60942ec7c413`, Codex
v0.155.1, gpt-6-astra / High. R032 separately records prior-session timing/tokens
for `01a0d02e-6cd9-7982-adae-0e1418129685`. No current token totals or later
usage supplied; no account inspection or model change.

**R032 questions answered in R033:** pattern length means the **shortest
repeating color block**. A written pattern containing redundant copies of a smaller
block should be simplified. The maker does not require a designated first bead,
stringing direction or helicity; choose any consistent convention. This permits
normalizing equivalent presentations, not filling unsupported colors or claiming
an uncertain image mapping is known. With erasures, the shortest compatible
period may still differ from the complete pattern's shortest period. No questions
remain pending; do not repeat these answered questions.

This step completes the pending variable rename, before the separate sequence
validation. The POV-Ray option, generated audit declarations, existing tests and
current usage examples now use `Helicity`. Geometry and defaults are unchanged.
Historical generated reports remain untouched, including their original source
hashes and commands. R030/R031's audit corresponds to Git `08ba3bb`, not the
renamed checkout; regenerate into a fresh output directory for current hashes.

R033 checks: all 25 existing tests pass, including both-hand ID/palette renders
and invalid helicity values. Byte comparisons against step-entry HEAD confirm
that beads.pov, neighbor_audit.py and test_legacy_visibility.py contain only the
identifier substitution. No new tests or full 49-render audit were needed for
this rename; old audit evidence was not regenerated. Whitespace checks pass.
Generated artifacts and `.venv` remain ignored. No sequence validation or photo
refit in this step. Publication includes the earlier R032 local records.

**R029 questions answered in R030:** ±1 runs around the torus's small radius;
±6 and ±7 are the diagonals, whose orientation depends on helicity. Inspect the
beads.pov equations for that orientation. The maker says unseen beads are at the
edges, not between visible neighbors. Preserve this construction guidance;
threshold-based vertex removal and deliberately missing-edge controls are separate
synthetic stress cases. No follow-up needed or pending. R030 authorizes the
helicity fix alongside the scheduled audit; R031 confirms continuing that work.

R025 answers to the opening questions:

1. Photo 2 has exactly three bead colors: red, yellow and black.
2. The maker carefully checks each pattern sequence against the previous one;
   there should be no mistakes. Use an error-free repeating construction as the
   working assumption. Image classification and registration may still be wrong.
3. The maker has seen beads visible only through tiny gaps: if visibility is
   insufficient to decide color, record "color unknown" and exclude that bead
   from color evidence. Preserve its position/index uncertainty; do not delete
   sequence positions or interpret unknown as a fourth physical color. A later
   repeat-based inference must remain distinct from the observed unknown.

No readability threshold was supplied; R023's pixel thresholds remain synthetic
sensitivity checks, not photo-calibrated rules. Save these as method-selection
constraints; R026 subsequently reviewed methods without implementing recovery.
Do not repeat answered questions or add a new question gate for this round.
R030 answers the direction/visibility follow-up; no questions remain pending.

Read `PLAN.md`, latest `REQUEST_LOG.md`, `photo2/progress.md` and
**`photo2/VISIBILITY.md`**; `photo2/PRACTICE.md` is its source-scene context.
`photo2/SYNTHETIC.md` remains historical evidence. Python is **3.12.14**, normally `.venv/bin/python`.
User instructions override prior plans. **Continue** launches the next bounded
step and the publication/handoff routine in AGENTS.md. Resume unfinished
publication before starting another task.

## Current capability and latest result

R030/R031 capability (option renamed in R033): `Declare=Helicity=-1` enables the opposite legacy hand; omitted
or +1 retains the original. Only the index-dependent row-angle rate changes sign;
phase, chain traversal, bead/color ordering and tangent hole axes stay fixed.
Photo2 mode retains its separate handedness control. Invalid values are rejected.

The audit covers both hands of all four R023 configurations. All 24 full-ring
visibility graphs (8 views × thresholds 1/12/100) are connected. All 240 graph
trials including two shuffles and integer-lifted quarter patches have zero relative
index errors and unexplained cycle/reciprocal/uniqueness conflicts. Phase-half
quarter 0 splits at the explicit index-seam cut; its component offsets remain
unknown. Correct modulo-N winding is recorded separately. The wrong-bridge control
passes cycle checks but is wrong against truth: image edges still need independent
validation. Colors and truth indices are absent from the propagation interface.

See **`photo2/NEIGHBORS.md`**. Reproduce:
`.venv/bin/python photo2/neighbor_audit.py --output photo2/output/neighbor-audit-final`.
It regenerates baseline scenes from Git ab79158, so no earlier output is required.
The final run binds source hashes at entry/exit, render commands and artifact
hashes; generated data stay ignored. Eight default legacy cases match historical
pixels at 480×360; four +1 ID/beauty/layout fixtures match at 2400×1800. Both hands'
ID/palette masks and colors match; analytic coordinates and winding signs agree.
Rendered markers validate the corrected projection to <0.15 pixel. Twenty-five
tests pass. Initial audit failures corrected a radians/degrees assumption in
Python (legacy geometry unchanged), then camera horizontal orientation and the
default 1.33 camera right-vector length. Initial output directories are diagnostic
only; use neighbor-audit-final. All ten final panels visually inspected. No
automatic edge detection or photo/repeat fit.

Final report SHA-256:
`d1bd07fe49675342db49fd70a7983cb3509d50f4db663b4abfaf7ced3f7ab242`.
All 11 source and 148 artifact hashes verified, plus old R023's seven source
hashes against baseline Git and 74 artifacts against disk. The four original
ID/beauty/layout arrays and visibility statistics reproduce R023 exactly.
Compilation and whitespace checks pass; 49 renders in the final audit.

Old practice/visibility source hashes no longer match current beads.pov and the
updated visibility test. Keep those historical reports unchanged. To run the old
visibility workflow again, regenerate practice into a fresh directory and supply
it via `legacy_visibility.py --practice`; do not bypass its stale-source checks.

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

**R026–R028 method choice completed:** `photo2/METHODS.md` selects a neighbor
graph with signed integer index differences, followed by strong-period testing
of a partial word for indexed red/yellow/black observations with unknowns. Primary
sources support graph traversal/difference constraints and partial-word periods.
CPD, DTW and event-log MDL were reviewed but are not the chosen indexing route.
The seven R023 source hashes and 74 artifact hashes were verified; no new period
scan, render, graph/registration test or photo fit was run.

**R027/R028 maker's indexing guidance:** every visible bead should be assigned a
bead_index by identifying its nearest neighbors along the three directions with
index differences **±1, ±6, ±7**. This answers the requested walkthrough's key
construction rule. Use it as the primary approach. Pick a seed, propagate signed
edge increments, check reciprocal edges and cycles (+1 +6 -7 = 0), and preserve
unresolved component offsets. Known index and unknown color are independent.
Do not replace a hidden immediate neighbor with the next visible bead, confuse
screen proximity across rope crossings with construction neighbors, or assume
automatic image-edge identification has already been validated. The image rules
for recognizing/signing the three families remain to be tested. Local integer
indices and full-ring indices modulo exact synthetic N require distinct seam/
winding treatment; the photo's provisional count is not an exact modulus.

Next task: **known-index partial-word repeat validation**, METHODS.md §B. Use
the known 40/13 synthetic patterns and missing/unknown observations; enumerate
strongly compatible periods, retain unsupported slots, test whole-repeat closure
only with exact synthetic N, and normalize equivalent rotations/reversals per R033
while preserving different compatible completions. This is
sequence-only validation, not automatic image-edge identification. Stop after its
synthetic report/tests, before integrating inferred image neighbors or photo refit.
Preserve the adequate 2,698 photo estimate without a divisor filter.

**Stay in this conversation**, with **gpt-6-astra / High**, for that task.
This retains the prior model recommendation, not a new measured comparison.
R032 opening questions are answered in R033; retain those conventions. Future
questions must not repeat the saved construction and presentation answers.

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
with contextualized advice questions; R024's questions are answered under R025 above.
R027/R028 supply the adjacency rule; R029/R030 supply the answered direction and
visibility follow-up, preserved above. Do not append questions at this round's end.

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
