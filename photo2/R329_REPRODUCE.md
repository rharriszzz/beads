# Reproduce R329

Open `photo2/r329/results/index.html` directly; it works offline. All diagrams are
original-photo crops or plotted diagnostics. No external viewer service is used.

The delivered results are immutable evidence. These scripts write fixed R329
paths, so **run a full reproduction in a separate checkout/copy**, not over the
original delivery. In a fresh checkout of the delivered commit, first preserve
or rename its `photo2/r329/results` and `photo2/r329/development` directories.
The reproduction requires the tracked R327/R328 candidate bank and the frozen
R321/R324 model/evidence files; it does not redetect the photograph from scratch.

Use `.venv/bin/python` with NumPy/SciPy/Pillow/Matplotlib and existing repository
native kernels. Set `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`, and a writable
`MPLCONFIGDIR=/tmp/r329-mpl`. The sequence is:

```sh
.venv/bin/python -m photo2.r329.localize
.venv/bin/python -m photo2.r329.traverse
.venv/bin/python -m photo2.r329.extra_traversals
.venv/bin/python -m photo2.r329.physical
.venv/bin/python -m photo2.r329.frozen
.venv/bin/python -m photo2.r329.matched
.venv/bin/python -m photo2.r329.closed_checks
.venv/bin/python -m photo2.r329.novel
.venv/bin/python -m photo2.r329.novel_replay
.venv/bin/python -m photo2.r329.review
.venv/bin/python -m photo2.r329.finalize_science
.venv/bin/python -m photo2.r329.delivery_finalize
```

`localize` uses the original cached primary prefix to practice on97 supports,
then compares all16 saved R328 alternatives in both directions and both families.
It actually splices one patch and the complete changed-window bundle, testing
whether subsequent original patches attach. `traverse` adds rotated starts,
reversed local frames, a soft both-family support score and a weak-link intervention.
`extra_traversals` preserves the failed inward starts and wider/reverse controls.
All searches remain single-seed connected beam growth with bounded rollback.

`physical` screens every integer count, constructs a selected coarse/adaptive grid,
certifies contacts, then samples actual native support pixels for feasible scenes.
Native local reflections retain all bodies. `matched` derives each N from its own
H and family; `novel` preserves new complete windings and evaluates the unusual
H=(214,176). The count/W/radius/axial/hand/spacing parameters and timing of every
physical trial are serialized. Construction failures and unresolved certificates
are retained. `frozen` uses exact archived first-hit ownership, separate reflection
measurements, and controlled fixed-address counterfactuals.

`closed_checks` and `finalize_science` run color-period comparisons only after
recording photographic hashes. P252 is a post-hoc diagnostic, never an input.
`review` generates figures, native crops, exact count coverage CSV and compact HTML.

Verification of the delivered files can be run without new scientific search:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MPLCONFIGDIR=/tmp/r329-mpl .venv/bin/python -m photo2.r329.verify
/home/rharris/.local/bin/beads-chromium-review photo2.r329.browser_check
```

The verifier independently implements attachment/return equations instead of
calling the selector or replay function. It uses direct native convolution and
augmented least squares, literal glass support formulas, and the older Python
camera ray path. It compares47,589 prior tracked file hashes captured before work;
the four append-only handoff/log files are checked separately at delivery.
Saved generated caches depend on wall-clock contact fallback budgets, so borderline
unresolved classifications can differ with machine load; retained actual witnesses
and certified geometry must still verify. Search also has explicit time limits.

The source seal fixes scientific implementations and input hashes. Scientific
outputs, verification receipts and delivery files are separate. The failed initial
JSON serialization source/log/incomplete output are archived under `development`.
No full whole-photo shaded raster, optimized camera fit, new independent labeling,
or exhaustive photographic count search is claimed.
