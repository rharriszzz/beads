# R319 reproduction

Read [the report](R319_REPORT.md), [protocol](R319_SPECIFICATION.md) and
[static review](r319/results/index.html). All indices remain conditional.

The historical photo and R312–R318 files are unchanged. Use an isolated checkout
for commands that rewrite R319 verification timestamps or review artifacts.
The existing `.venv` supplies NumPy/SciPy/Pillow/Matplotlib/Playwright.

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m unittest photo2.r319.tests
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m photo2.r319.verify
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r319.linear_certificate
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r319.analyze
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/r319-mpl .venv/bin/python -m photo2.r319.review
/home/rharris/.local/bin/beads-chromium-review photo2.r319.browser_check
```

`experiment.py`, `refine.py`, `contact_fit.py`, `small_patch.py`, `iterate.py` are
campaign generators with original absolute cutoffs. **Do not run them over the
delivered trial directory**: a new campaign requires new output paths and renewed
time authorization. They are not advertised as restart-safe services. Each setting
was atomically serialized before selection; unsuccessful settings are retained.

Replay an individual trial with its saved `parameters` and the frozen
`photo2/r318/results/epoch2/epoch.json`. Standard/narrow settings use
`photo2.r319.local_model.Chain`, installed as `photo2.r318.optics.Chain` in the
isolated replay process, then `Engine(epoch).evaluate(parameters, True)`.
The local class exactly reduces to R318 at zero added fields and includes generic
shadow tracing for nonlegacy profiles. No historical module on disk is changed.
`bound_controls.RelaxedCompact` is **only** for the explicitly labeled numerical
rate-veto controls; its physical separation test remains mandatory.

`trials/` keeps all1018 primary parameters/outcomes. `bilateral-sensitivity.json.gz`
records163 coordinates×four probes; units/scales, one-sided fallbacks and both
central differences are explicit. Roughness is an angular width in **degrees**
mapped to a specular exponent; the initial generated variable metadata called it
an exponent parameter, a metadata error corrected in source and this report.
`all-reflection-responses.csv` includes all feasible per-observation vectors/errors,
peak changes and predicted-error comparisons. Missing/unrendered physical failures
are in `trial-ledger.csv`, never substituted by zero. The CSV explicitly records its parent trial; coordinate rows use their current
iteration parent, and coupled steps use the serialized parent binding.

Each minimax JSON contains the scaled44-row Jacobian, variables, trial references,
solver state and predicted errors. Full-plane NPZ files bind the separating normals,
pairs, margins and their linearized changes. `linear-target-certificates.json`
contains supporting-hyperplane LP dual lower bounds for the specified affine model
and box, not certificates about nonlinear geometry. Sources regenerate them.

`profile-discrete-controls.json.gz`, `relaxed-rate-controls.json.gz`,
`geometry-light-factorial.json.gz` and `correspondence-controls.json.gz` are separate
experiments. Frozen alternative maps are scored at identical geometry and are never
silently mixed with the primary epoch. `half-grid-sensitivity.json.gz` contains the
40-direction sampling control with exact connected-component localization in doubled
coordinates. Selected half-pixel replay independently uses R314's component routine.

`per-body-outline-response.json.gz` records actual visible support and occluders
for all948 feasible primary settings on one fixed photo crop; isolated counts are
counterfactual diagnostics only. Frozen pigment cores, chromatic separators and
material/paper brackets come from R314/R315. No photograph segmentation is regenerated.
The complete small-catalog audit retains candidate exclusions and support alternatives;
it does not establish physical indexing. Review PNGs retain native image coordinates,
and `raw-photo.png` contains exact original RGB pixels.

The verification command compares all old tracked files to the start commit
`18d953b380fe5e89461fe0582dcb2b846eea314d`; new R319 additions are excluded while modifications/deletions of historical
tracked files remain forbidden.
No optimizer runs are required to read the report or open `results/index.html` offline.
