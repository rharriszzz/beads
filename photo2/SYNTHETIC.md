# Occlusion-aware synthetic patch benchmark — R015

**Centers alone fail this benchmark.** Internal visible bead boundaries separate
the tested depth-reflected, size and tilt alternatives under perfect segmentation.
Pitch/count/linear-twist equivalence survives even exact rendered masks. This is
a discrete observation test, not continuous parameter recovery or a photo result.

## Reproduce

```sh
.venv/bin/python photo2/synthetic_benchmark.py
.venv/bin/python -m unittest discover -s photo2 -p 'test_*.py' -v
```

The benchmark requires local POV-Ray. Outputs under `photo2/output/synthetic-benchmark/`
include `report.json`, `commands.json`, two comparison panels, per-candidate
ID images/include files/logs, and reference beauty/isolated-bead renders. These
generated files remain ignored. Use `--output` to preserve separate runs.
The report records source and output SHA-256 hashes, geometry, camera, renderer
version, library versions, original bead IDs, per-bead visibility and trial seeds.
`commands.json` retains every exact rendering command. Numeric geometry is Python;
appearance and instrumented ID materials are in `synthetic-patch.pov`. Both use the
unchanged shared `bead-shape.inc` macro.

## Known scene and measurements

Each hand has a straight orthographic patch with pitch 26, 6.5 beads/turn,
center-cylinder radius 18, phase 0.37 radians, bead radius 7, axial half-height
4.55, hole-radius ratio 0.3, roundedness 0.8 and hole-axis tilt 20 degrees.
Units are synthetic world units, **not calibrated photo pixels**. The 160 by 70
view renders at 480 by 210 pixels (three pixels/unit). The central `abs(x)<60`
ROI excludes scene truncation; the helix extends beyond `abs(x)=100`.
For original integer bead ID k, spacing d=p/b:

```text
x = k d
theta = h 2 pi k / b + phase + twist x
center = (x, r sin(theta), r cos(theta))
hole axis = (cos(tilt), sin(tilt) cos(theta), -sin(tilt) sin(theta))
```

POV-Ray resolves depth and body occlusion. An unlit, gamma-1, non-antialiased
ID pass assigns one exact RGB code to each bead. Unknown pixel colors cause an
error. Isolated reference renders use the identical camera/raster; visible pixels
must be a subset of the isolated body. Their area ratio is visible fraction.
IDs are instrumentation for deriving observations; numeric ID equality never
enters candidate center/outline scores. Original k values remain in the report.

Reference beads are certified non-intersecting by conservative enclosing spheres:
minimum center separation 17.2016 exceeds enclosing-sphere diameter 16.6976.
The double-density candidate is deliberately a stress case; its bodies can
intersect. Some other alternatives also fail the conservative sphere certificate,
which alone does not prove intersection. The report marks each separately.

Each hand has 29 reference centers with at least 12 visible raster pixels.
Twelve of these belong to the back half of the cylinder: the R014 front-half
cutoff would wrongly discard them. Fifteen negative-hand and nineteen positive-hand
bodies are partly occluded. Visible-mask centroids differ from projected true
centers by RMS 1.5336 and 1.4347 units, respectively. Thus a mask centroid cannot
silently substitute for a geometric center. Both measurements are scored separately.

Center scoring uses one-to-one assignment of unordered sets, with no charge for
extra predicted sites. Too few sites is infeasible (`null`), not a successful
partial match. Boundary scoring uses all visible instance interfaces, exterior
edges and hole rims; its symmetric distance is the mean of the two directional
mean distances. Silhouette IoU separately measures foreground union, including
holes. It does not use internal bead interfaces.

## Discrete comparison

The twelve candidates retain fixed registration except the parameter changes
explicit in their names/report. In particular the simple opposite-hand case keeps
phase fixed; its poor score cannot establish handedness after phase optimization.
The stronger depth-reflected alternative reverses hand, maps phase to `pi-phase`
and reverses tilt. It preserves projected bodies but reverses depth order.

| Alternative | Center RMSE, either hand | Boundary distance, hand -1 / +1 | Silhouette IoU, hand -1 / +1 |
| --- | ---: | ---: | ---: |
| Truth | 0 | 0 / 0 | 1 / 1 |
| Equivalent pitch/count/twist | <2e-14 | 0 / 0 | 1 / 1 |
| Depth reflection | <2e-14 | 0.7609 / 0.7506 | 1 / 1 |
| Twice the site density | 0 | 0.5934 / 0.6675 | 0.8575 / 0.8008 |
| Body radius -20% | 0 | 1.0880 / 1.0952 | 0.7025 / 0.7002 |
| Axial height +25% | 0 | 0.5635 / 0.5676 | 0.8592 / 0.8670 |
| Zero hole-axis tilt | 0 | 0.4950 / 0.4956 | 0.8743 / 0.8727 |
| Reversed hole-axis tilt | 0 | 0.4542 / 0.4542 | 0.8681 / 0.8681 |

The remaining candidates change fixed-phase hand, pitch +10%, count to 7.5 and
center-cylinder radius +15%; full results are in the report. The pitch alternative
has only 27 visible sites and cannot match all 29 centers, illustrating why
completeness must be explicit.

Depth-reflected silhouettes match exactly, so silhouette fitting alone fails this
hand ambiguity. Internal occlusion boundaries distinguish the particular reflected
alternative in the exact masks. Size and tilt also become observable in these
boundaries despite zero center error. This establishes sensitivity at the tested
parameter offsets, not unique recovery over all possible geometry or alignment.

The gauge candidate uses b'=8, p'=d b' and
`twist'=h 2 pi (1/b-1/b')/d`. Every center and hole axis is unchanged, and the
rendered ID masks are pixel-identical for both hands. No image observation can
distinguish those parameterizations in this model; an external twist/connectivity
constraint is still required.

## Missing labels and density failure

For each hand, 24 deterministic trials per condition retain 29, 14 or 7 centers
(requested missing fractions 0, 0.5, 0.75, rounded), with independent coordinate
noise of sigma 0, 0.75 or 2 units. The same chosen observations and noise are
used for all candidates. Seeds and selected original bead IDs are retained.
Missing indices are never renumbered.

With all 29 centers and sigma 2, the double-density stress candidate wins all
24 trials for each hand. Median RMSE falls from 2.7315 to 2.4963 for hand -1 and
from 2.7487 to 2.4223 for hand +1. At seven centers it is best including ties in
24/24 and 20/24 trials; even other wrong geometries sometimes win. Noiseless
centers tie truth with density, reflection, size and tilt alternatives. This is
the expected superset bias, now demonstrated with rendered visibility. It is
not a physically acceptable fitted density.

Partial-outline scores retain only the selected instances' *original visible*
boundary pixels and measure distance to all predicted boundaries. Missing objects
become unknown; deleting them does not invent new background edges. Truth and its
gauge equivalent score zero. Every other candidate is rejected by nonzero distance
even in the tested seven-instance subsets: minimum across trials/alternatives
0.1526 units for hand -1 and 0.2264 for +1. **Outlines remain exact in these trials**;
the Gaussian noise applies only to centers. A denser set of wrong predicted edges
can still exploit a one-way boundary metric. There is no calibrated rejection
threshold, statistical confidence or claim of robustness to segmentation error.

## Checks, limits and next task

Thirteen tests pass, including proper rotation and gauge/reflection identities,
the center-superset failure, ID decoding/boundary-label invariance, and actual
POV-Ray rendering of one bead completely hiding an identical rear bead. Full
benchmark runs also assert exact gauge-mask equality, reflected-silhouette equality
and visibility-mask containment. Source beauty and comparison panels were visually
inspected. Two complete runs reproduced numerical results and all 86 common image
pixel arrays, plus 24 include files byte for byte. The 84 POV-Ray PNG file hashes
change with embedded render timestamps; decoded pixels match exactly. Each run
retains its actual file hashes. The first byte-hash equality check failed for that
reason, and was followed by pixel comparison and metadata inspection.

These are straight patches, one size/phase/tilt per hand, one camera and one raster
resolution. No continuous fitting, curved geometry, blur, noisy segmentation,
material fitting, perspective comparison or real-repeat test is performed.
Beauty images are diagnostic; measurements come from perfect instrumented masks,
not extracted edges in shaded images. Legacy/photo render code is unchanged, so
the earlier legacy pixel-equality test was not repeated. PLAN Step 2 remains open.

Next: test practical boundary observations on shaded synthetic patches with
controlled blur/noise and fitted local alignment. Score extracted observations
against hidden ID-mask truth, measure rejection/ambiguity under observation error,
and retain the gauge equivalence. Stop at that validation report before photo refit.
