# R286 reproduction

Use repository root, branch photo-2-strategy-v3, Python3.12 `.venv/bin/python` and
installed POV-Ray. Dependency versions are saved in `r286/results/environment.json`.
Original photograph and all old scientific files must match baseline
8448689b68df9fa0a57f3f4e9450434e116f5f00, except the explicitly revised permanent
`PHASE1_MEASUREMENTS.md`. No network inference or physical-model input in real
segmentation. Native RGB crops preserve original pixels; numerical intensity is
ICC-managed sRGB linear luminance as in earlier rounds.

The frozen selection and candidate-freeze.json are scientific evidence. Do not
rewrite them during review or tune methods against the confirmation images.
The chronological preparation was: diagnose; select automatic confirmation before
new results; design/implement; run development; write checkpoint3/freeze hashes;
run confirmation. Reproduction uses the already-frozen files.

```bash
.venv/bin/python -m photo2.r286.diagnose
.venv/bin/python -m photo2.r286.run --output /tmp/beads-r286-replay
.venv/bin/python -m photo2.r286.run --stage confirmation --output /tmp/beads-r286-replay
.venv/bin/python -m photo2.r286.reflections
.venv/bin/python -m photo2.r286.mechanisms
.venv/bin/python -m photo2.r286.synthetic
.venv/bin/python -m photo2.r286.evaluate
.venv/bin/python -m photo2.r286.review
.venv/bin/python -m photo2.r286.review confirmation
.venv/bin/python -m photo2.r286.atlas
.venv/bin/python -m photo2.r286.context
.venv/bin/python -m photo2.r286.package
.venv/bin/python -m unittest photo2.r286.tests photo2.r285.tests photo2.r284b.tests photo2.r284.tests photo2.r283.tests photo2.r282.tests
.venv/bin/python -m photo2.r286.audit
/home/rharris/.local/bin/beads-chromium-review photo2.r286.browser_check
```

The context command recomputes the previously reviewed right yellow as a
supplementary control; it does not add a confirmation region. `select` can reproduce
the selection, but is not needed for frozen reruns. The browser launcher is the
project's explicitly authorized local-review command, exactly as written.

Results map:
- `P5-diagnosis.json`, `P5-fields.npz`: old exact fields/labels/routes and missing markers.
- `selection.json`, `candidate-freeze.json`: selection and immutable inference hash.
- `development.json.gz`, `confirmation.json.gz`: exact runs/masks/contours/centroids,
  source cues, nativeY, marker/interface ledgers, illumination/domain sensitivity,
  shared record fields and unknown physical identities. Coordinates are native x,y;
  origin=seed−48, mask window97×97; domain comparison65×65.
- `two-sided-context`: original third yellow and131px group crop.
- `evaluation.json`: scalar summaries, dark-profile pairs/routes, overlap/duplicate
  diagnostics, signed-support/arc coverage and dim-S material retention.
- `mechanisms.json`, `synthetic`: mathematical controls and separately rendered
  physical scenes, with evaluation truth hidden until inference save.
- `reflection-stability.json`:144 exact reflection replays and original metrics.
- `test-results.json`, `audit.json`, `browser-check.json`: verification evidence.
- `review/r286/index.html`: compact front page; expandable all-method panels,
  every-cue atlases, profiles, exact native crops and preserved failures.

Algorithm source is `r286/methods.py`; unchanged diffuse/material measurements
come from `r285/methods.py`. J uses unchanged R284B colored extraction. No historical
manual bead identities, maker chart, fitted physical centers or pattern hypotheses
enter those functions. Synthetic geometry is renderer/evaluation-only.

Real-photo reliability is unrated. Area/connectedness/stability/overlap numbers are
not precision, recall or certified distinct-bead counts. Tests preserve known
failures rather than changing expected scientific outcomes to conceal them.
