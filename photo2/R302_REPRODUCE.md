# R302 reproduction and review

From the repository, run `photo2/review/r302/launch.sh`. This reuses R301's native
photo debugger and the existing localhost/WSL browser launcher, on port8302 (or
an available port). `--no-browser --port 0` serves without browser dispatch.
The HTML also opens offline. Historical R301 and earlier debuggers remain intact.

The delivered experiment is sealed. Do not run another fitting pass in its output
directory. It used `.venv/bin/python -m photo2.r302.experiment diagnose`, then
`fit`, then `.venv/bin/python -m photo2.r302.export`. The four starting vectors,
random seeds, bounds, feature scales, evidence, objective and clock allocation
are saved under `r302/evidence` and `r302/results`. No separate environment
installation or synthetic campaign is needed.

The 600-second numerical cap includes the predictor audit and sensitivity work,
then equal clock allocations for four hierarchical fits and four accurate-DE
controls. The final20 seconds are reserved for bounded-call overrun. No new
candidate begins after its deadline. Native exports and verification occur after
selection and do not change it. Clock-limited search is machine dependent;
saved proposal vectors allow exact objective and physical replay without rerunning
the optimizer. The complete proposed histories are retained, including rejected
positions and all alternatives. The program does not automatically resume a
sealed experiment or extend its budget.

Run checks with:

```sh
.venv/bin/python -m unittest photo2.r302.tests
.venv/bin/python -m photo2.r302.verify
/home/rharris/.local/bin/beads-chromium-review photo2.r302.browser_check
```

R302 fixes bead radius to one arbitrary unit. `scale` is pixels per bead radius;
`axial` is axial-width/face-diameter; `pitch` is effective centerline arclength
per bead radius per address. It is **not string elongation**. `spacing` bounds
a smooth local effective-advance correction by±2% everywhere, including guards.
`curve` is signed circular curvature, with no arclength increase from bending.
This phenomenological correction does not model crochet thread paths or prove
their inextensibility. No zero-net-effective-pitch constraint is imposed.

For assumed total count N, the constant turn interval is
`[6.5*N/(N+6.5), 6.5*N/(N-6.5)]`. N=2000 is a conditional minimum-count scenario,
not an inferred count and not a bound valid for every larger N. Tighten it with
the actual N if known. A single region cannot establish global accumulated twist.

S1's seven training and three retrospective comparison reflections retain their
R301 coordinates, ambiguity, colors and split. B15's contour is uncertain, its
eight vertices and two extents are dependent measurements of one feature. The
194 material/paper samples are correlated coverage evidence, not194 independent
beads or geometric constraints. Four dark valleys and withheld material bands
are post-seal diagnostics; none supplies a certified physical neighbor identity.

`diagnosis.json.gz` stores the native/coarse comparison, matrices, singular
vectors, per-parameter and joint perturbations and numerical timing.
`fit-freeze.json` records selected parameters before comparison evaluation.
`native-manifest.json.gz` and the debugger retain observations, competing
correspondences, surfaces, all153 positions and contact witnesses. Older baseline
rows retain their original scientific outputs. `verification.json` and
`delivery.json` record checks and remote delivery. Stop after R302.
