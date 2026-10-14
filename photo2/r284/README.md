# R284A — isolated Phase 1 alternatives

Run from repository root with Python 3.12 in `.venv`. No replacement inventory or
Phase 2/3 output is written. `r284` is the module name because the authorized
Chromium launcher accepts numeric round directories; the experiment is **R284A**.

```bash
.venv/bin/python -m photo2.r284.run
.venv/bin/python -m photo2.r284.controls
.venv/bin/python -m photo2.r284.benchmark
.venv/bin/python -m photo2.r284.assess
.venv/bin/python -m photo2.r284.review
.venv/bin/python -m photo2.r284.focus
.venv/bin/python -m unittest photo2.r284.tests photo2.r283.tests photo2.r282.tests
.venv/bin/python -m photo2.r284.audit
/home/rharris/.local/bin/beads-chromium-review photo2.r284.browser_check
```

`run --output /tmp/another-r284a` independently reproduces 19 inference/cue files.
`audit` uses `/tmp/beads-r284a-replay`, compares those bytes, verifies native crops,
and hashes every pre-round tracked photo2/source-photo Git blob against `fb26cd9`.
The source freeze includes all current module sources and upstream input hashes.
Do not change sources between the final `run` and `audit`.

`methods.py` consumes image features and a cue bank, with no case names, reviewed
coordinates, old color assignments, physical identities, or pattern inputs. The
inherited image-derived seeds are only candidate cues. `run.py` chooses three
requested crops from R283 selection rules and five automatic crops before inference.
It uses the unchanged centerline only for cases/accounting. `assess.py` and `focus.py`
contain evaluation-only reviewed locations; neither is imported by inference.

`review-assessment.json` is the agent's qualitative reading of saved photographs,
not verified pixel truth. First-pass source, masks, cue ledgers and three images
remain in `first-pass/`; they show broad-cue paper false positives and ownership
partition failures before stronger cue gates and native straight-path stopping.
The final C colored rule still fails visibly; it is retained for comparison.

`benchmark` uses 16 previously certified POV-Ray scenes from R283. Their pixels,
materials and geometry are unchanged. They are retrospective development controls,
**not fresh held-out validation**. Appearance inference is serialized before the
identity raster/classes are opened by the evaluator. No new Phase 2 model fit runs.

Outputs: [review](../review/r284a/index.html), [report](../R284A_REPORT.md),
[requirements](../R284A_CHECKLIST.md), exact masks/cue dispositions in `results/`,
CSV with centroid/signed extent/station/secondary information in the review folder.
