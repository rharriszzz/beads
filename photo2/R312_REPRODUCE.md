# R312 reproduction

Work on `photo-2-strategy-v3` in `rharriszzz/beads`. Existing `.venv` supplies
Python 3.12, NumPy, SciPy, Pillow and matplotlib. Numerical threads are fixed to
one by the entry point. Use a **new output directory** for new experiments.

```sh
python3 photo2/phase2_minimax.py --output /tmp/r312-new --profile-only
python3 photo2/phase2_minimax.py --output /tmp/r312-new --stage 1 --seconds 1800
python3 photo2/phase2_minimax.py --output /tmp/r312-new --stage 1 --seconds 1800 --resume
```

The delivered experiment reuses the completed initial profiling files. The
additional exact/caching preflight is `python -m photo2.r312.preflight` under
`.venv`, with the same thread environment. It is not fitting. Stage 1 source is
archived exactly, including the initial entry point. The later `--native-only`
entry option configures Stage 2's existing native search phase in response to
the preflight, without changing Stage 1 search calculations.

Save Stage 1 static diagnostics before starting Stage 2:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MPLCONFIGDIR=/tmp/beads-r312-mpl .venv/bin/python -c 'from pathlib import Path; from photo2.r312.delivery import stage_diagnostics; stage_diagnostics(Path("/tmp/r312-new"),1)'
python3 photo2/phase2_minimax.py --output /tmp/r312-new --stage 2 --native-only --seconds 1800
python3 photo2/phase2_minimax.py --output /tmp/r312-new --stage 2 --native-only --seconds 1800 --resume
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MPLCONFIGDIR=/tmp/beads-r312-mpl .venv/bin/python -m photo2.r312.local_refine --output /tmp/r312-new --seconds 600
python3 photo2/phase2_minimax.py --output /tmp/r312-new --finalize
```

Source bundles are written automatically for new runs. Exact Stage 1 source in
the delivered run was archived before the Stage 2 performance update.
Source/evidence/environment mismatches reject a resume. SIGTERM
or SIGINT finishes the current trial and atomically checkpoints. A complete
orphan trial is recovered without rerendering. A directory lock rejects another
writer. A sealed stage cannot resume. Budgets are cumulative wall allowances;
hardware/load and time limits mean exact proposal counts are not promised.
Seeds, complete parameters, proposal-plan hashes and all executed vectors are
saved. Initial Stage 2 retains Stage 1 fixed maps; the contingent full-chain epoch
saves correspondence-only controls and freezes new full-chain maps before fitting.
All fitted continuous parameters can change. Local refinement also supports
`--resume`. Finalization runs verification in a fresh process automatically;
`python3 photo2/phase2_minimax.py --verify` reruns only that audit if needed.

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MPLCONFIGDIR=/tmp/beads-r312-mpl .venv/bin/python -m unittest photo2.r312.tests -v
```

Open `photo2/r312/results/campaign/index.html` or individual static PNGs directly.
No browser application or interactive viewer is needed. Each stage contains
top-20 JSON/CSV/PNG, missing observations, outward thresholds, signed error plots,
native before/after overlays, regional outcomes and a performance ledger.
Historical experiments/source photographs and `beads.pov` are preserved.
