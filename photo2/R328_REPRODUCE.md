# Reproduce R328

Open `photo2/r328/results/index.html` directly. The slider begins with the single
seed at step -1, then shows the connected patches growing around the original
photograph. Raw and overlaid crops compare R327 and R328. Files work offline.

The detector deliberately reuses R327's local photographic candidate bank. Its
input SHA256 is recorded in every receipt. It uses observations, local candidates,
stations and period; it does not use the earlier selected graph or winding in
search. The export stage reads the earlier graph solely to describe changes.

To repeat the final search with exactly the saved pair checks and patch scores,
write to a NEW directory:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MPLCONFIGDIR=/tmp/r328-mpl .venv/bin/python -m photo2.r328.grow --output /tmp/r328-repeat --width 256 --budget 180 --prepared photo2/r328/development/final256/prepared.json.gz
```

Omit `--prepared` to rebuild the local connected patches and native pair checks
from the cached R327 candidate bank and original photograph. This does not rerun
R327 candidate discovery. The declared overall allowance was 600 seconds for all
searches; `--budget` limits an individual replay, checked between windows.

Export and verify a fresh result without altering the delivery:

```sh
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/r328-mpl .venv/bin/python -m photo2.r328.export --run /tmp/r328-repeat --output /tmp/r328-export
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/r328-mpl .venv/bin/python -m photo2.r328.verify --output /tmp/r328-export
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/r328-mpl .venv/bin/python -m photo2.r328.evaluate --output /tmp/r328-export
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/r328-mpl .venv/bin/python -m photo2.r328.tests
```

`evaluate` is the only new module that reads historical R161 labels, after the
scientific seal. It cannot change the working graph. Exported HTML uses repository
relative links; place it at a matching repository depth or adjust those links for
a browser review of `/tmp` output. Scientific verification of `/tmp` is independent
of the HTML location.

For the delivered review:

```sh
/home/rharris/.local/bin/beads-chromium-review photo2.r328.browser_check
```

The browser may need execution outside the process sandbox. Its launcher argument
handling was corrected after the scientific seal; the earlier source is preserved
as `development/browser-before-helper.py`. No scientific source or result changed.

`grow.py` contains the complete growth selection. `prepared.json.gz` records every
connected candidate subpatch, omitted parent assignments, photographic score terms,
and pair check. `search.json.gz` records frontier alternatives, changed earlier
choices, failed attempts and rollback events. `graph.json.gz` records the chosen
attachment order, original/unwrapped coordinates and selected edge witnesses.
The alternative consequences retain all 16 completed runner-up windings, including
lower-bend changes and original native prediction/response measurements.

All evidence is conditional on the reused detection/candidate bank. Shared parent
photographic contexts are correlated. Replaying measurements is not independent
bead-identity validation. The report separates the provisional circuit from the
historical independent subset and records the computational limits.
