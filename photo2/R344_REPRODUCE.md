# Reproduce R344

Base: R343 `6fa108f7c378bdecf55fcaad8fc99387869f8188`, branch `photo-2-strategy-v3`.
All new science is under `photo2/r344/`. Stopped untracked R340 experiments are untouched and unused.

From the repository root:

```bash
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r344/freeze.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r344/analyze.py
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/beads-r344-mpl .venv/bin/python photo2/r344/present.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r344/verify.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r344/report.py
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/beads-r344-mpl .venv/bin/python photo2/r344/replay.py
/home/rharris/.local/bin/beads-chromium-review photo2.r344.browser_check
```

`R344_RUN_ROOT` redirects scientific outputs. `replay.py` runs freeze/analyze/present/verify/report in a fresh `/tmp` directory and compares ten decoded scientific products plus seventeen exact rendered/text/review artifacts. Browser checks are separate and actually exercise native-photograph links, the 13-repeat matrix, 208-position grids, local keys, before/after colors, offline reload and phone layout.

The overlay changes only the two explicitly named red pigments to maker-yellow. Original records and prior authority statements are retained. All identities, XY, coordinates, links, roles, exclusions and winding remain unchanged. Black recognition, including its 73.5 threshold, is untouched. No photographic pigment classifier runs in this experiment.

Strict support reuses the existing R337 motif rule: uncontradicted color with three observations in three fixed geographic blocks. Tentative completion is a separately labeled recorded-color plurality. It has no effect on the photographic ledger. Each tentative entry exports every native source, authority, raw counts, geographic blocks, alternative colors, a qualitative confidence statement, and an explicitly uncalibrated shrinkage score.

Nine fixed model specifications compare training-only frequency, phase13, A104, A208, A208 with104-parent hierarchy, A338, B207, B299 and A306 alias. This is not an exhaustive period search. Historical smoothing/tie rules are unchanged. All models use the same leading-A occurrence folds; geographic folds exclude the test block and both cyclic neighbors. Producer calls reuse R337 prediction helpers; the independent verifier uses direct counted dictionaries instead. All probability vectors and group denominators are exported.

Seven strict cohorts keep original1039 IDs, current1041 IDs and frozen710 IDs separate, with both historical and corrected labels. Matched unchanged-color targets exclude only the two new corrections, while full comparisons retain them. Proper-divisor witnesses use only strict entries. Their minimality result is conditional on the indexed208-word and does not establish physical closure.

The report is regenerated from the numerical tables by `report.py`. Exact native crops are compared with the original JPEG. Numerical verification and replay do not supply independent physical bead/color ground truth. The recommended targeted rephotography is explicitly future work and is not executed.
