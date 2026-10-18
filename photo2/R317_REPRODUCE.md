# R317 reproduction

Open [the report](R317_REPORT.md) and [static photographic review](r317/results/index.html).
All physical owner labels are conditional. White curves are isolated occupied
boundaries, cyan curves visible boundaries, magenta enclosed bores, and orange
marks measured core pixels hidden by modeled neighbors. The separate -14/-15
and +11/+12 cards prevent combining measurements from different bodies.

Use the existing Python 3.12 `.venv` from the repository root:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MPLCONFIGDIR=/tmp/r317-mpl .venv/bin/python -m unittest photo2.r317.tests photo2.r316.tests photo2.r315.tests photo2.r314.tests photo2.r314.tests_extra
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MPLCONFIGDIR=/tmp/r317-mpl .venv/bin/python -m photo2.r317.verify
/home/rharris/.local/bin/beads-chromium-review photo2.r317.browser_check
```

Verification rewrites only the R317 verification receipt. Run from the delivered
checkout; subsequent edits should use an isolated checkout for history checks.
The browser wrapper is machine-specific; elsewhere use installed Playwright Chromium.

The sealed initial epoch is `results/search.json`; its exact source is
`results/search-source.py`. The additional radial-cant epoch is separate in
`results/refinement.json`. Every proposal is in `results/trials/`, including
bounds, demonstrated intersections and unresolved physical tests. No old trial
was modified by the follow-up. Selected model files retain the original trial IDs.

To replay any proposal, load its parameters, use `r317.model.Chain` and the frozen
R314 evidence engine, certify every full-chain spatial pair, and call the original
R315 `refined_trace`. `r317.search.evaluate` defaults to the unchanged R316 class;
for the radial-cant epoch explicitly bind `search.Chain = r317.model.Chain`, as
`refine.py` and `attribution.py` do. The new class at zero cant exactly reproduces
R316. R316's original source and delivered outputs remain unchanged.

For a full repeat, use a disposable checkout and preserve the delivered R317 output
first. `search` has a 780-second cap, `refine` a separate 390-second cap; the actual
saved search may finish sooner. Results depend on the measured runtime cutoff.
The generators are not restart interfaces and overwrite R317 outputs:

```bash
.venv/bin/python -m photo2.r317.search
.venv/bin/python -m photo2.r317.refine
.venv/bin/python -m photo2.r317.finalize
.venv/bin/python -m photo2.r317.review
.venv/bin/python -m photo2.r317.plots
.venv/bin/python -m photo2.r317.attribution
```

`finalize` reuses R316 export and scoring functions with the declared R317 class
bound in memory; it writes only R317 results. Selected exports are re-rendered by
R315 and independently compared with RayLayers on every native target-grid ray.
Independent Python sampled rays, separate support formulas, original-photo crop
pixels, all metrics/brackets and historical-file preservation are then checked.
Contact certificates establish nonintersection, not mechanical equilibrium or
photographic truth. Original peak-minimax machinery stays unchanged; an empty
reliable correspondence cohort means unavailable maximum error, never zero.

The final `polish.py` epoch, if present, is capped at 180 seconds and runs after
`refine` and before `finalize`. `polish.json` supplies the final selected IDs;
`jacobians.json` retains the available columns, probe IDs, matrices, linear
predictions and trust steps. The initial and radial-cant selections stay sealed.

After `polish`, run `python -m photo2.r317.select_review` before `finalize`.
This adds the post-search all-six-preserved Pareto candidate without changing the
sealed A/B/C minimax selections. `review-selection.json` records its explicit
constraints and tie-break. The final review has eight models and 48 early-core cards,
plus the separate physical-index alternatives and remote/worst-region comparisons.
Run `summary` and `report` after `attribution` to reproduce the numerical report.

## Post-deadline radial-angle archive audit

The supplement appended to `R317_REPORT.md` is a separate documentary audit;
the original report generator does not reproduce it. Do not regenerate the
delivered report in place. Reproduce the archive-only audit with:

```bash
.venv/bin/python -m photo2.r317.supplement_audit
```

This reads all 1797 sealed trials, proves that the twelve shared-cant controls
change only `radial_cant` relative to their saved parents, reports the outward
sign convention beta = −historical cant, and checks saved frame consistency.
It writes only `r317/results/supplement-audit/audit.json` and `tables.md`.
It performs no placement, ray tracing, contact search or optimization.
The historical focused3 export has nonzero `trajectory_mix` and is explicitly
excluded from the R316 alpha/beta frame audit; it is not modified or discarded.
An initial overbroad zero-trajectory assertion caught this distinction before
any output was written. The revised audit records the exclusion.

The existing R317 seven-contract suite checks bit-identical zero cant, unchanged
centers, rigid frames, the inward-positive historical sign and layered/reference
ray agreement. The original verification receipt remains the historical record;
do not overwrite it by rerunning the full historical verifier after supplement
edits, because its original preservation policy predates this report append.
The supplement delivery receipt separately records its limited verification.
The original deadline has not been silently extended. Larger-angle and new
field experiments require a renewed allowance and separately preserved outputs.
