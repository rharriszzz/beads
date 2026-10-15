# R291 launch and reproducibility

From `/home/rharris/git/beads`, use the existing `.venv`; no new dependencies,
renderer, external service or generated photograph is required.

```bash
photo2/review/r291/launch.sh
```

Open **http://127.0.0.1:8291/**. Start Here presents14 cases. The other54 are optional
and available in All cases. Stop with Ctrl-C and relaunch to resume answers.
Use `--port 8292` if needed, or `--feedback PATH` to choose another persistent answer
directory. The default is `photo2/r291/feedback/`, separate from R290 and Git-ignored.
Back up that entire directory and snapshots; export downloads all assessments,
displayed candidates and revisions.

One click selects good A/B, useful partial segments, wrong despite clear photo,
genuine lack of photographic information, or not sure. Diagnostics are optional.
Keys1–6 answer, arrows navigate, H hides/restores all marks. Wheel and +/− zoom;
drag pans. The white TARGET ring identifies the starting feature. Ownership view
alone shows neighboring labels and optional same/different-bead controls. Recorded
pairs are reused across cases. Alternative differences, old R290 outlines and
internal dark edges are optional overlays. Nothing requires drawing or placing points.

## Verify saved results without replacing them

```bash
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/beads-r291-mpl .venv/bin/python -m unittest photo2.r291.tests -v
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/beads-r291-mpl .venv/bin/python -m photo2.r291.audit --replay
/home/rharris/.local/bin/beads-chromium-review photo2.r291.browser_check
```

Replay writes all three stages and their real-photo crops into a temporary directory
and compares exact hashes. It does not refreeze parameters, alter saved inference,
regenerate starts or modify user feedback. The audit updates its verification and
coverage receipts. Chromium writes test feedback only under `/tmp`, not either
experiment's real feedback folder.

For retained independent outputs:

```bash
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/beads-r291-mpl .venv/bin/python -m photo2.r291.run development --output /tmp/beads-r291-replay
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/beads-r291-mpl .venv/bin/python -m photo2.r291.run reserved --output /tmp/beads-r291-replay
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/beads-r291-mpl .venv/bin/python -m photo2.r291.run retrospective --output /tmp/beads-r291-replay
```

Do not overwrite the selection or freeze files. Both commands refuse replacement.
Reserved/retrospective inference verifies frozen source hashes before starting.
The original17 R290 reserved cases are retrospective, not fresh R291 validation.
The ten new hash-selected targets were frozen before implementing the method.

## Artifact map

- `R291_SPECIFICATION.md`, `R291_DIAGNOSIS.md`: scope and pre-implementation diagnosis.
- `r291/evidence/collection.json`:68 exact starts and41/17/10 allocation, original
  photo/ICC hashes, selection rule and100px new-target exclusion.
- `historical-hashes.json.gz`, `r290-feedback-hashes.json`: preservation baseline.
- `evidence.py`: A–E local measurements, direct profiles and separator evidence.
- `detector.py`: one binary target graph, complementary assembly and per-side reasons.
- `results/algorithm-frozen.json`: source/parameter freeze before new reserved results.
- `development.json.gz`, `retrospective.json.gz`, `reserved.json.gz`: all automatic
  proposals, exact pixel runs, supported/unresolved arcs, local evidence, alternatives
  and perturbation/context sensitivity.
- `results/crops/`: unmodified decoded native photographic crops; review copies match.
- `results/comparison.json`: every old/new case, newly located/lost supported sides,
  other-feature inclusions, separator conflicts and sensitivity. No precision claim.
- `results/start-here.json`:14 cases, fixed quotas, ranking values and selection reasons.
- `results/coverage.json`, `R291_COVERAGE.md`, `review/r291/coverage.html`: permanent
  situation coverage and all-eight-test outcomes with missing new-holdout categories.
- `checkpoints/initial/`, `checkpoints/continuity-balance/`: two failed versions,
  full development results and diagnostic photographic overviews.
- `results/*-overview.png`: final photographic diagnostic sheets; regenerate with
  `.venv/bin/python -m photo2.r291.gallery development` or `reserved`/`retrospective`.
- `review/r291/data/`, `manifest.json`: exact displayed candidates and version digests,
  readonly prior user evidence and R290 comparisons. Regenerate the package using
  `.venv/bin/python -m photo2.r291.review`; this never creates human answers.
- `serve.py`: separately versioned append-only feedback; `review/r291/app.js`: UI.
- `results/tests.log`, `audit.json`, `browser-check.json`, `delivery.json`: test,
  replay, browser and remote-delivery receipts.

Coordinates are original EXIF-oriented native pixel centers, x right/y down. Pixel
runs are `[y,inclusive-x0,inclusive-x1]`; contour sides use half-integer coordinates.
Crops use exclusive upper endpoints. Measurements use ICC-managed sRGB/linear Y;
saved raw crops use the original decoded RGB. Browser enlargement uses nearest
neighbors only. A source bright feature remains distinct from a physical bead ID.

All primary proposals remain partial; complete correctness is still for human
assessment. Do not substitute support fractions, stability or reduced area for truth.
No automatic improvement round follows this delivery.
