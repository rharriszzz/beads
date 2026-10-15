# R287 reproduction and evidence map

Run from repository root with Python3.12 `.venv/bin/python`. Branch:
`photo-2-strategy-v3`; prior baseline `f676c850d569aaddcb3735e480080094b6a56399`.
The photo, ICC conversion, old J/M/B inputs and all prior scientific files are
preserved. Permanent PHASE1_MEASUREMENTS.md is the intentional historical-audit
exception requested by the user. Environment versions are recorded in results.

Chronology matters: requirements/hypotheses, automatic16-region selection, v1
development failure, recorded v2 measurement change, v2 development, source/selection
freeze, independent confirmation. Do not overwrite the first-policy evidence or
refreeze against confirmation. The saved selection is reused for reproduction.

```bash
.venv/bin/python -m photo2.r287.run --output /tmp/beads-r287-replay
.venv/bin/python -m photo2.r287.run --stage confirmation --output /tmp/beads-r287-replay
.venv/bin/python -m photo2.r287.evaluate
.venv/bin/python -m photo2.r287.mechanisms
.venv/bin/python -m photo2.r287.review
.venv/bin/python -m photo2.r287.review confirmation
.venv/bin/python -m photo2.r287.diagnostics
.venv/bin/python -m photo2.r287.package
.venv/bin/python -m unittest photo2.r287.tests photo2.r286.tests photo2.r285.tests photo2.r284b.tests photo2.r284.tests photo2.r283.tests photo2.r282.tests
.venv/bin/python -m photo2.r287.audit
/home/rharris/.local/bin/beads-chromium-review photo2.r287.browser_check
```

Use the browser launcher as that exact standalone command; no wrapper or added
arguments. Existing project permission covers local Chromium review. No network
or model inference is needed for the scientific scripts.

Code:
- `candidates.py`: replay-compatible unchanged J/M/B baseline plus14 explicitly
  conditional perturbations. Initial photo-only A support remains J's ring input.
- `evidence.py`: inner/outer boundary sampling; five-route marker corridors;
  direct diffuse-continuation routes. No review coordinates or physical identities.
- `selector.py`: simple four-way v2 policy; no color/coordinate/identity argument.
- `selector_v1.py`, `evidence_v1.py`: failed first policy preserved unchanged.
- `select.py`: frozen reproducible photograph-only region strata; `common.development`
  uses old case IDs only for evaluation, not inference.
- `run.py`: shared records, original native support, all perturbation masks, source
  and measured centers, importance/unknown reliability/visibility/physical identity.

Data:
- `results/selection.json`, `freeze.json`: exact regions, inputs, rules and source hashes.
- `development-v1.json.gz`: first failed policy on26 cues, all results retained.
- `development.json.gz`, `confirmation.json.gz`:26/63 cues × J/M/B, original nativeY,
  exact global pixel runs, contours, centroids,14 perturbations per candidate,
  boundary samples, marker ledger, multiple intensity routes and selector reasons.
  Origin=seed−48; native97×97 field. Coordinates are x-right/y-down native pixels.
- `evaluation.json`: choice counts, all candidate metrics, pair overlaps, support
  near/crossings/flanking pairs. Both keeps alternatives, not a merged support.
- `mechanisms.json`: controlled monotone shading/dark seam/narrow material and
  deliberately unidentifiable deep-texture counterexample. Not physical rendering.
- `black-preservation.json`: R286 reflection-only source hash and previous144-replay
  provenance. R287 does not re-estimate black measurements.
- `test-results.json`, `audit.json`, `browser-check.json`: verification records.
- `review/r287/index.html`: compact review with every anchor and every nearby cue,
  native97/145 crops, exact fills, original S links, profiles and explicit failures.

Recreating v1 does not require changing files: import its `measure`/`decide` against
saved original fields/candidates/stability. The archived v1 data are the authoritative
first run; v2 cannot overwrite them. No hybrid support was attempted because choosing
or retaining independent alternatives was better justified than pixel union/intersection.

Conditional stability limitations: HSV/paper/palette/initial A are fixed; gain and
contrast affect intensity, not full physical lighting/color. Seed offsets keep A
fixed and use93px M domains to remain inside the saved97px window. Profile lines
are sampled smoothed fields; dots use nearest original nativeY pixels. All native
supports and original decoded RGB crops remain separately available.

No numerical real-photo precision/recall or full crossing-bead completeness is
established. Abstention preserves the source observation and its importance. Later
physical/pattern interpretations must link these observations and never rewrite them.
