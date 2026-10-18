# R318 reproduction

Read [the report](R318_REPORT.md), [protocol](R318_SPECIFICATION.md) and
[compact review](r318/results/index.html). All bead labels are conditional.
White dots are observed connected reflection centroids; arrows end at modeled
visible principal centroids. Red marks the maximum error, not a selected average.

From the repository root, using the existing Python environment:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m unittest photo2.r318.tests photo2.r317.tests
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m photo2.r318.verify
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m photo2.r318.diagnose
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/r318-mpl .venv/bin/python -m photo2.r318.report
```

Verification rewrites the new R318 verification receipt and selected numerical
controls, never historical R317 results. Use an isolated checkout to preserve
delivered receipt timestamps. No browser or network is needed to inspect PNGs,
CSV, JSON or the small static HTML page.

`results/epoch.json` and `results/epoch2/epoch.json` freeze the same 22 photographic
observations and localization rule with distinct one-to-one provisional maps.
`observations.json.gz` retains every automatic candidate, its raw-image window,
connected supports, peak ties, threshold alternatives and exclusion reasons.
`photo-mask.npz` is the automatically derived rope mask, not a model silhouette.
`epoch2/assignment-control.json` and `transfer-control.json` compare changed maps
at identical geometry and explicitly disallow geometric-gain credit.

Every search vector and result, including infeasibility, is in the corresponding
`trials/` directory. `initial-*` files preserve pre-followup selections and native
arrays. `jacobians.json.gz` keeps feasible finite-difference probes and coupled
minimax trust steps. Source archives retain the initial directional epoch and
later coupled-control implementation. Finite and extended light controls are
separate fixed-geometry records, not silently folded into the search count.

To replay a saved trial without optimizing, load its parameters and the matching
epoch, instantiate `photo2.r318.optics.Engine(epoch)`, and call `evaluate(params)`.
The reported `emax_px` is recomputed from all frozen rows. A missing prediction
has `maximum_is_infinite=true`; it is never a zero displacement. Internal finite
penalties are search controls, not the reported physical maximum.

Do not rerun the automatic selection, preparation or search over delivered
outputs. Their commands are generators, and the search contains the original
absolute scientific cutoff. A genuinely new experiment needs new outputs,
explicit dates and authorization. Reproduction should replay retained settings.

The original R312 shadow kernel is used only for its exact inherited legacy
shape (hole .14, rounding .8, exterior false). Thickness/radius and coherent pose
can vary; all bodies remain present. The R315 refined camera tracer resolves
relevant camera rays. Independent checks use original uncompiled camera/shadow
marching, separate support formulas, R314 connected components, and a half-pixel
camera lattice. Unresolved Python rays and shadow pairs are explicitly counted.

The photo diameter is an uncertain automatic visible-basin estimate; modeled
projected widths and fixed baseline normalization are separately reported.
Neither correspondence changes nor an enlarged fitted diameter can be counted
as geometric progress. No physical identity chain, optical material calibration,
or complete reconstruction is established.
