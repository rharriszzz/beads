# R311 reproduction

From branch`photo-2-strategy-v3` in`rharriszzz/beads`:

```sh
python3 photo2/phase2_basin_search.py --audit-only
python3 photo2/phase2_basin_search.py --output /tmp/r311-new --seconds 2400
```

The entry point selects the existing repository`.venv` and fixes numerical thread
counts. It needs the unchanged tracked historical evidence and current numpy,
scipy, Pillow and matplotlib environment. It creates no dependency environment.
Default output is`photo2/r311/results/campaign`; do not reuse the delivered sealed
directory for new fitting. The principal broad schedule and deterministic seeds
are in`photo2/r311/search.py`; existing geometry adapters/finite boxes are in
`model.py`. Default finalization automatically allocates at most600 additional
search seconds for four-variable sampling around qualifying discovered basins.
That contingent stage, its trigger and its own source hash are recorded separately.
`--no-review` stops after the initial budget;`--review-only` performs the contingent
stage if needed, seals finalists, then exports/evaluates/verifies/plots them.

```sh
python3 photo2/phase2_basin_search.py --output /tmp/r311-new --seconds 2400 --resume
python3 photo2/phase2_basin_search.py --output /tmp/r311-new --review-only
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MPLCONFIGDIR=/tmp/beads-r311-mpl .venv/bin/python -m unittest photo2.r311.tests -v
```

SIGTERM or SIGINT finishes the current native trial and checkpoints. A later resume
requires unchanged scientific source/evidence/environment and preserves cumulative
time. A complete trial published before a killed checkpoint is recovered without
rerendering it. Completed trial files are atomic deterministic gzip JSON. Source
hashes, frozen start models, parameter vectors, contact/score outcomes, forecast
errors and stop decisions remain inspectable. Another writer is rejected by a
directory lock. A sealed search cannot resume after comparison exposure.

After the sealed experiment, restart source binding was expanded to the older
geometry dependencies. Their hashes match the start-of-experiment preservation
manifest. An AST comparison confirms that only the fingerprint function changed;
proposal generation, evaluation and stopping code are identical. Exact fitting
code is retained in`r311/evidence/search-used-for-fitting.py`, with the original
checkpoint/source manifest and the explicit source-binding-upgrade receipt.
The five real scope/recovery contracts were rerun after this metadata change.

Finalization resumes after interruption by reusing completed per-model exports and
metrics. Trial selection is sealed first. Dense final measurement/verification,
the archive audit, baseline preflight and recovery tests are separately timed from
search. Browser validation is separate from scientific rendering.

Open`photo2/review/r311/index.html` directly for offline review, or:

```sh
bash photo2/review/r311/launch.sh
```

The launcher serves the checkout on localhost:8311; visit
`http://127.0.0.1:8311/photo2/review/r311/index.html`. It binds only localhost and
stops with Ctrl-C. It does not launch a different campaign. The review includes
raw pixels, conditional native-owner picking, visible boundaries, projected
centers, original photographic locations and all response maps. No internet
resources are needed. Raw pixels remain on a separate canvas from annotations.

All prior experiments, source photograph, observations,`beads.pov`, bead geometry,
physical construction and Phase3 remain preserved. The new report does not convert
conditional overlaps or fixed mathematical owners into verified physical identity.
