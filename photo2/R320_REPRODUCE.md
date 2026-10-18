# Reproduce R320

From repository root, use the existing `.venv`. Numerical threads were fixed:

```sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
.venv/bin/python -m unittest photo2.r320.tests
.venv/bin/python -m photo2.r320.pilot
.venv/bin/python -m photo2.r320.search
.venv/bin/python -m photo2.r320.refine
.venv/bin/python -m photo2.r320.controls
```

Do not run searches concurrently with timing measurements. For each case 0,1,2
and scope 100,200,all, run in a fresh process:

```sh
.venv/bin/python -m photo2.r320.benchmark --case 0 --scope 100
```

Saved frozen benchmark epochs are reused. If absent, the geometry-support map is
constructed first and its initialization cost is separate. Process-cold timings
clear the centerline cache, but use precompiled C++ libraries on disk; Python
startup/imports and evidence loading are outside the evaluation timer. Native
rays are 1px. The second geometry changes radius and a 0.25px centerline harmonic.
Exact-geometry cached timings change only the common light azimuth. Every
benchmark saves target-body count, all represented bodies, actual observation
count, rays, unknowns, operation timings and process high-water memory.

```sh
.venv/bin/python -m photo2.r320.performance
.venv/bin/python -m photo2.r320.deliver
.venv/bin/python -m photo2.r320.report
.venv/bin/python -m photo2.r320.validate
```

These commands regenerate R320 artifacts in place; copy `photo2/r320/results` to
another location first if comparing historical runtimes. They never modify the
original photograph, beads.pov or R312–R319 outputs. Independent support and
analytic orientation formulas, original Python camera/shadow comparisons and
seam-neighbor clearance brackets live in `r320/audit.py`.

The preliminary timing archive contains overlapping-work measurements; a second
archive retains a caught benchmark loop-control defect. Neither enters the final
performance table. The duplicate-epoch-key failure log is likewise retained.
Final benchmark contracts require six rows and all three cache modes per case.

The repaired clearance audit constructs actual annular support points at axial-normal degeneracies; the initial invalid upper-distance artifacts remain in `results/clearance-initial-failure/`.
