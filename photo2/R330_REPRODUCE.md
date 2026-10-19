# Reproduce R330

Open `photo2/r330/review/index.html` locally. It requires no service or network.
Historical R327/R328/R329 files are read-only inputs. Programs refuse to reuse
their scientific output directory; use new directories for independent runs.

From the repository root, use the existing `.venv/bin/python`, NumPy, SciPy,
Pillow and Playwright. These experiments use cached photographic candidates and
the saved visible-body raster, not a new detector or renderer build.

```sh
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export MPLCONFIGDIR=/tmp/r330-mpl
mkdir -p /tmp/r330-reproduction
.venv/bin/python -m photo2.r330.pattern --output /tmp/r330-reproduction/results
.venv/bin/python -m photo2.r330.diagnostics --output /tmp/r330-reproduction/photography
.venv/bin/python -m photo2.r330.refine --output /tmp/r330-reproduction/refinement
.venv/bin/python -m photo2.r330.diagnostics --followup --output /tmp/r330-reproduction/checks
.venv/bin/python -m photo2.r330.controls --output /tmp/r330-reproduction/controls
.venv/bin/python -m photo2.r330.controls --mapping-followup --output /tmp/r330-reproduction/audit
```

The six scientific commands produce independent new results. Compare parsed
JSON values, excluding timings; gzip headers need not have identical timestamps.
G's bounded searches have a 90-second per-width guard, so an unusually slow
machine can retain fewer paths; the delivered saved paths still verify exactly.
The deterministic control seeds are 330, 33001 and 33066.

The figures can be regenerated in the delivered directory with:

```sh
.venv/bin/python -m photo2.r330.review
```

This rewrites only new R330 presentation files. `--root` can point at a fresh
R330-layout directory; local report/R329 links then need the same repository
relative layout. For a fully independent rendered reproduction, use another
checkout and create the new output directories there after preserving its R330
results. Never overwrite original R329 outputs with their historical scripts.

Read-only scientific verification of the delivered artifacts, plus presentation
verification that writes screenshots/receipts under R330:

```sh
.venv/bin/python -m photo2.r330.verify
/home/rharris/.local/bin/beads-chromium-review photo2.r330.browser_check
```

The fixed local Chromium launcher supplies the existing browser cache and
environment; it does not install dependencies. The verifier checks preservation
relative to starting commit `381d27f5220f2a6adf5fbf5d6b04b49957e0b3ac` and allows only
new R330 paths/reports. A separately coded DP and integer path reconstruction
check the solver outputs. The original photograph is compared pixel-for-pixel
with every saved native crop.

Principal artifacts:

- `results/development-scan.json.gz`: complete 40 × 900 period rankings and frozen shortlist.
- `results/patterns.json.gz`: initial held-out predictions, motifs, 33 alignment runs and map/count sensitivity.
- `refinement/refinement.json.gz`: hierarchical fits, 900 section-excluded predictions, complete suspicious-observation ledger, appearance controls, six provisional color hypotheses and 210 perturbation records.
- `photography/g-replays.json.gz`: both bounded G runs, failures, traces and complete new states.
- `photography/g-differences.json.gz`: original early alternative's complete offset staircase.
- `photography/photography.json.gz`: shared colored-reference fits, H membership/reinsertion audit and F pixel-coverage trials.
- `checks/`: H bundle repairs, G pattern consequences and E regression/extension.
- `controls/controls.json.gz`: global null selections, color-weight sensitivity, unindexed inventory and duplicate/index audit.
- `audit/mapping-followup.json.gz`: own-map motif prediction on the same 900-observation cohort for 165 saved/new map cases, plus refined-motif decoding controls.
- `review/`: offline review, exact native crops, motif/conflict CSVs and browser receipts.
- `development/`: failed export artifacts and the initial strict zero-correction refinement; none is a downstream scientific input.

The source files implement reusable periodic prediction, shift-state decoding,
photographic patch recombination and appearance comparison. They do not adopt a
physical model or modify historical observation/color tables.
