# R300 reproduction

Open the review with `photo2/review/r300/launch.sh` from WSL. It selects the repository
virtual environment, serves localhost (port8300 or a free port), and dispatches the
Windows default browser when available. Ctrl+C stops the server. Use
`--no-browser --port 0` for automated use. The review and original debug tabs also
work offline; original R299's historical strict targets are not current criteria.

No new dependencies, fitting, observation selection or ownership matching is needed.
All outputs are retrospective diagnostics. Use Python3.12 and the existing `.venv`.

```sh
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m unittest photo2.r300.tests -v
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r300.verify
/home/rharris/.local/bin/beads-chromium-review photo2.r300.browser_check
```

The verifier replays the complete analysis in a temporary directory and byte-compares
JSON/CSV, replays all104 crossed-control predictions at native resolution, checks
all988 saved records against their unchanged sources, and hashes the protected
historical tree including live feedback. The new controls already contain separate
full-chain certificate replays of both unchanged geometries. Test logs and receipts
are saved in `r300/results`; the original artifacts are never overwritten.

For separate analysis outputs:

```sh
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r300.analyze --output /tmp/beads-r300-replay
MPLCONFIGDIR=/tmp/beads-r300-mpl OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r300.plots --results /tmp/beads-r300-replay --output /tmp/beads-r300-plots
```

`crossed_controls` refuses to overwrite its frozen result. Reproduce the predictions
with the verifier. `protocol` likewise refuses to replace the pre-analysis snapshot.
`review` builds only the new R300 HTML/data bundle; older debuggers stay intact.

Methods: prediction-minus-observation vectors, photographic arclength from the
original anchor, 16 fixed arc bins, deterministic1,000-bin resampling per trend,
Theil–Sen/leave-bin-out/origin sensitivity, and separate family index seams. Trends
are descriptive; resampling is not calibrated physical uncertainty. The reported
finite quantiles do not penalize missing predictions numerically; missing IDs/counts
are separate. The ledger retains both peaks and centroids and original local face
normalization. Local index-equivalent displacement and telescoping differences do
not establish physical integer correspondence or closure.
