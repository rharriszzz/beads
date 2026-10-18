# Reproduce R321

Use the existing `.venv` from repository root, with one numerical thread:

```sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
.venv/bin/python -m unittest photo2.r321.tests
.venv/bin/python -m photo2.r321.validate
```

The second command audits saved artifacts without launching another search.
It independently reconstructs the22 observed centroids from original RGB,
checks every trial's frozen map/max/missing convention, expands actual-glass
penetration witnesses, checks closure and selected neighbor endpoints, and
validates benchmark arithmetic, images, links and preservation hashes.

Selected scenes and gap certificates can be reconstructed with:

```sh
.venv/bin/python -m photo2.r321.deliver
.venv/bin/python -m photo2.r321.straight_audit
.venv/bin/python -m photo2.r321.report
```

These regenerate R321 artifacts. Copy `photo2/r321/results` first to preserve
historical runtimes/receipts. They do not modify the photograph, beads.pov or
R312–R320 sources/results. The viewer is `photo2/r321/results/index.html` and
opens directly from disk. Browser checks:

```sh
/home/rharris/.local/bin/beads-chromium-review photo2.r321.browser_check
```

For isolated performance reconstruction, run **without other numerical jobs**:

```sh
.venv/bin/python -m photo2.r321.benchmark
```

This repeats24 old/new matched-input construction comparisons and18 native
100/200/all evaluations. All physical bodies remain present. Compiled ray
libraries are warmed; process startup is excluded. The performance CSV contains
matched construction costs; JSON contains separate native operation timings.
The first cost-plan serialization failed on mixed integer/string dictionary
keys after all measurements had saved. Only serialization was repaired; the
original measurements were reused, not silently replaced.

## Construction and historical epochs

`model.py` retains the R320 camera/shape/closed conventions and adds a fixed-knot
periodic cubic B-spline centerline and explicit `packing_spacing` mode.
Absent mode means historical uniform placement; `curvature-density` uses
`spacing.py`. `packing.py` implements the explicit straight radial-support root,
curved +1 plane inequalities and deterministic radius correction. `gaps.py`
tightens upper distances with actual outer-side segments; it does not change
geometry or acceptance. `verify.py` independently doubles density-integration
resolution, derives analytic normals and uses original Python camera/shadow code.

Trials0000–0083 used the initial uniform-spacing numerical radius/plane solver,
archived in `results/initial-numerical-packing.py`. Trials0084 onward retain the
same family maps while testing the algebraic root/plane stencil and density law.
Every trial stores its exact final parameters, spacing mode (absence=uniform),
construction history, contact classification, gap brackets, timings and available
photographic diagnostics. No candidate silently disappears when its reflection
map loses a prediction. `results/initial-upper-bounds` retains the looser original
selected upper-distance records before the actual-side-segment improvement.

The exploratory CLIs `campaign`, `continue_campaign`, `centerline`, `refine` and
`joint` are historical bounded-search drivers, not an automatic restart protocol.
Do not rerun them into the delivered trial directory: use a copied checkout or
separate output directory. `refine.py` reflects recovery after a missing-Emax
assumption failed; the original log is retained. It is not a promise to reproduce
historical wall time or candidate ordering from a blank directory. Saved input
parameters and independent replay are the authoritative scientific reproduction.

The primary exact scientific inputs are count/radius/axial, fixed hand and
registration, small centerline coefficients; R is derived without a photo
objective. Future changes to the density law require a new explicit experiment,
not changing the meaning of these archived trials. No R322 is authorized.
