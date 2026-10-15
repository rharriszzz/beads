# R290 reproduction and review

From `/home/rharris/git/beads`, using the existing `.venv` with NumPy, SciPy,
Pillow and the existing image utilities. No install or renderer is needed.

## Open the review

```bash
photo2/review/r290/launch.sh
```

Open http://127.0.0.1:8290/. If the port is occupied, use
`photo2/review/r290/launch.sh --port 8291` and open that port. Stop with Ctrl-C;
rerunning the same command resumes saved answers. Feedback goes to
`photo2/r290/feedback/`, not the versioned scientific results. Use `--feedback PATH`
only to select a different persistent answer directory. Keep that directory and
its snapshots when backing up feedback. The export button downloads the full
answer/revision ledger with exact candidate masks/contours and image hashes.

Keys1–5 choose A/B/neither/insufficient/not-sure. Arrows navigate. The selected
bright point has a white cross; numbered circles identify points available in the
ownership controls. The gray square is the historical case-selection anchor,
not a detector input. Toggle edges/points for an unobstructed photograph; wheel
zooms and drag pans. B is disabled when no meaningful alternative was generated.

## Verify saved science without altering it

```bash
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/beads-r290-mpl .venv/bin/python -m unittest photo2.r290.tests -v
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/beads-r290-mpl .venv/bin/python -m photo2.r290.audit --replay
/home/rharris/.local/bin/beads-chromium-review photo2.r290.browser_check
```

The replay generates both collections and native crops in a temporary directory,
checks exact hashes against the saved science and removes temporary copies.
It never reruns selection, changes parameters or opens user feedback. The audit
updates its verification receipt and coverage matrix. Chromium creates test answers
only in a separate temporary directory and validates reopen/revision/undo/export.

For a retained independent data replay:

```bash
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/beads-r290-mpl .venv/bin/python -m photo2.r290.run development --output /tmp/beads-r290-replay
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/beads-r290-mpl .venv/bin/python -m photo2.r290.run reserved --output /tmp/beads-r290-replay
```

The reserved command verifies the frozen source hashes before inference. Do not
rerun `select` or `freeze` over the existing collection. Those commands intentionally
refuse to replace their freeze files. There is no authorized reserved retuning.

## Evidence map

- `r290/evidence/tests.json`: permanent T1–T8 definitions created before code.
- `collection.json`: frozen58 cases, full R289 patches, native positions, split,
  selection anchors/rules, source image/ICC hashes and missing selection slot.
- `development-observations.json`, `provenance-corrections.json`: photographic
  situation observations and explicit correction of two old-name interpretation errors.
- `user-judgments.json`: preserved R289 red-worst ownership and original
  R215/R284–R288 judgment links/hashes. Never a detector input.
- `r290/detector.py`: final edge-resistance solve, all local tests and outputs.
- `results/algorithm-frozen.json`: code/dependency/data hashes and pre-reserved freeze.
- `results/development.json.gz`, `reserved.json.gz`: all automatic inference,
  exact masks, segment evidence, arcs, alternatives and uncertainty.
- `results/crops/`: exact unpainted native crops; review has identical copies.
- `results/coverage.json`, `R290_COVERAGE.md`, `review/r290/coverage.html`: permanent
  category/case/evidence/outcome/missing-coverage matrix.
- `checkpoints/`: three failed scientific versions and their complete data.
- `results/development-regressions.json`: every earlier/final development status
  and candidate size as a diagnostic ledger, never ground-truth accuracy.
- `results/audit.json`: preservation, exact replay, status counts and limitations.
- `review/r290/data/`: immutable packaged candidates with provenance annotations;
  `manifest.json` gives each displayed candidate's exact digest.
- `serve.py`: local append-only feedback service; `review/r290/app.js`: batch UI.
- `results/browser-check.json`, `tests.log`, `delivery.json`: separate technical
  validation and remote delivery records.

Coordinates are EXIF-transposed original native pixel centers: x right, y down.
Mask runs are `[y, inclusive-x0, inclusive-x1]`; crop endpoints are exclusive.
Contours use half-integer pixel-square sides. Inference uses ICC-managed sRGB and
linear Y; review shows original decoded RGB without color conversion or resampling
in the saved PNG. Browser enlargement uses nearest-neighbor display only.

All58 primary cases are partial/unresolved. No complete-boundary precision or
trustworthy centroid accuracy has been demonstrated. No synthetic evaluation,
production replacement or automatic next round is included.
