# R316 reproduction

Open [the static review](r316/results/index.html) and read [the report](R316_REPORT.md).
The 36 photographic cards retain raw native pixels at 3× nearest-neighbor scale.
White is isolated occupied contour, cyan visible contour, magenta enclosed bore,
and orange the candidate's measured-core pixels hidden by modeled neighbors.
Candidate identity remains conditional. Exact arrays and all overlapping candidates
are linked; no occluder is removed from a delivered reconstruction.

From the repository root, use Python 3.12 in `.venv`, with
`MPLCONFIGDIR=/tmp/r316-mpl OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1`:

```bash
.venv/bin/python -m unittest photo2.r316.tests photo2.r315.tests photo2.r314.tests photo2.r314.tests_extra
.venv/bin/python -m photo2.r316.verify
/home/rharris/.local/bin/beads-chromium-review photo2.r316.browser_check
```

The verification command rewrites only its R316 receipt. Historical-preservation
checks require this delivered checkout; later changes should be verified in an
isolated checkout. The browser wrapper is machine-specific; elsewhere run
`photo2.r316.browser_check` with Playwright Chromium installed. The review is offline.

For complete recomputation, first preserve the delivered results, then use a separate
disposable checkout. These generators overwrite **R316 outputs**, not historical
sources, and are not restart interfaces:

```bash
.venv/bin/python -m photo2.r316.benchmark
.venv/bin/python -m photo2.r316.fixtures
.venv/bin/python -m photo2.r316.clipping
.venv/bin/python -m photo2.r316.experiment
.venv/bin/python -m photo2.r316.followup
.venv/bin/python -m photo2.r316.recovery
.venv/bin/python -m photo2.r316.cache_benchmark
.venv/bin/python -m photo2.r316.review
.venv/bin/python -m photo2.r316.verify
```

Run timing commands without concurrent computational jobs. `experiment` stops
proposals at 300 seconds and exports afterward; the delivered initial epoch has
183 evaluations. Follow-ups have 45 and 27 fixed controls. Every delivered setting
is independently replayable using `experiment.evaluate(parameters, data, engine)`
without rerunning a search. Source hashes and the original parent commit are in
`verification.json` and `start.json`.

`renderer.Hybrid.trace` returns owner/unknown plus certification/fallback statistics.
It is a restricted numerical prototype, not a default replacement renderer.
`RayLayers.trace` returns exact isolated masks and depths and composes ownership
without global sorting. Its cache keys bind camera, shape, individual placement and
coordinates. Geometry changes can reuse only identical unaffected body layers;
changing the coordinates invalidates them. Warm repeated-frame timings are not
proposal speedups. Current caches are in-memory, single-process and bounded.

`benchmark-initial-failure.log` retains the refinement-cap failure; the final code
falls back on those bodies. The earlier NumPy batched-solve shape error was repaired
by making the right-hand side an explicit column vector. Neither failure entered
fitting. All geometry experiments used unchanged R315 refined tracing, so the new
renderer cannot alter their scientific conclusions.

`review-preflight-failure` retains the rejected enlarged crop and its verification
log. Current review generation asserts every crop coordinate lies inside the frozen
array and records crop origins for independent raw-pixel verification.
