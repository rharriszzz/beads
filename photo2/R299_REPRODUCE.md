# R299 reproduction and review

From WSL, run:

```sh
photo2/review/r299/launch.sh
```

This selects the repository `.venv`, starts localhost on port8299 (or a free port),
and dispatches the Windows default browser through PowerShell when available.
No activation or remembered URL is needed. Ctrl+C stops the server. Use
`--no-browser --port 0` for an automated launch. The review also works offline.
The geometry tab loads the unchanged R298 review, including its controls, failures
and overlays. Reflection controls share its raw/overlay crop and navigation design.

Delivered outputs are frozen. Reproduce in a separate copy/worktree with Python3.12
and the existing NumPy/SciPy/Pillow/Matplotlib/Playwright environment. Do not run the
measurement or experiment commands over the delivered results. No new dependency
is needed. Set `MPLCONFIGDIR=/tmp/beads-r299-mpl OPENBLAS_NUM_THREADS=1` for the
commands below. Use the same observation screen and source files, never reselect
points in response to errors.

1. `python -m photo2.r299.measure` reconstructs all810 R276-based measurements and
   the52-point photo-only selection. Its timestamp is excluded from exact replay.
   `visual-screen.json` records the pre-fit seven ambiguous yellow mixtures.
2. `python -m photo2.r299.experiment fixed` freezes five independent baseline owner
   ledgers before any light fit, then executes300 light evaluations across15
   controls. Each baseline receives22 directional,19 finite and19 extended trials.
3. `python -m photo2.r299.experiment joint` runs33 physical geometry trials and231
   light evaluations: camera/axis-only, shape/helix-only and their combination.
   No per-bead adjustment. The chosen trial15 changes global phase by−0.15rad.
4. `python -m photo2.r299.export` exports19 native comparisons, full chain positions,
   independent contact witnesses, every reflection and competing owner, exact visible
   sample footprints, residual CSVs and the offline debugger data. Native source
   integration uses5×5 nodes; every eighth observation additionally uses half-pixel
   rays and9×9 nodes. `analyze` separates angular convergence on the same fine grid.
5. `python -m photo2.r299.analyze` produces descriptive spatial/orientation diagnostics
   and figures; it never fits parameters. Frozen extent-censoring diagnostics are
   in `results/extent-censoring-audit.json`.

Tests and checks:

```sh
MPLCONFIGDIR=/tmp/beads-r299-mpl OPENBLAS_NUM_THREADS=1 .venv/bin/python -m unittest photo2.r299.tests photo2.r298.tests -v
MPLCONFIGDIR=/tmp/beads-r299-mpl OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r299.verify
/home/rharris/.local/bin/beads-chromium-review photo2.r299.browser_check
git diff --check
```

Verification rebuilds all52 primary reflections for all19 models, all positions,
full-chain physical certificates and visible sample runs; replays a complete22-trial
light fit and all33 trial certificates; remeasures all810 original records; checks
52 raw crops and every protected historical file. Browser checks exercise actual
launch.sh from another directory, all models/locations, raw invariance, tables,
links, plots, desktop/narrow/offline and the preserved R298 tab. Windows dispatch
is mocked; an actual Windows GUI was not opened during tests.

Technical corrections are retained: first measurement call passed run lists to a
mapping-only helper; first verifier compared shadow counts from primary surfaces
with counts that also included competitors. Neither changed measured points or fit
results. The original distance diagnostic was mislabeled as a lower bound; it is
now correctly named distance to sampled visible surface. It is not a rigorous
continuous-surface bound. Source checkpoint and before/after hashes are retained.

The model is a shared half-vector lobe with geometric visibility, not a calibrated
camera-response/PSF/microfacet model. Native discrete peaks may switch between
near-equal maxima. Numerical convergence is reported separately from photographic
error. No additional fitting is authorized by these reproduction instructions.
