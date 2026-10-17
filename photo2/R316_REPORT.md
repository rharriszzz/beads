# R316 — correct layered prototype, useful local recovery, no reconstruction adoption

**The first negative core can be substantially repaired with coherent shared geometry,
but the complete 200-bead reconstruction is still not convincing.** The final diagnostic
raises its single-owner material coverage from 28.6% to **85.1%**, while recovering
+8 to approximately baseline coverage. Six early cores average **59.3% → 77.4%**.
Independent paper, boundary, worst-core and correspondence problems remain. No geometry
is adopted and no valid principal bright-spot minimax is established.

[Photographic review](r316/results/index.html) · [same-geography comparison](r316/results/review/before-after.png) · [occlusion ledger](r316/results/ledger.json.gz) · [protocol](R316_SPECIFICATION.md) · [reproduce](R316_REPRODUCE.md) · [verification](r316/results/verification.json) · [delivery](r316/results/delivery.json).

**How accurately can silhouettes replace camera rays?** The prototype uses the R314
support gradient to form an inscribed convex polygon and intersecting support lines
to form a circumscribed polygon. Angular refinement continues until the maximum
outer-vertex distance to the inner polygon is ≤0.025 native pixels. Convexity makes
that a continuous outer-to-inner Hausdorff bound in exact arithmetic; floating-point
geometry and pixel occupancy remain separately tested. A small conservative guard
also covers the marcher's hit tolerance. Pixels between the polygons require rays.
A projected capsule encloses the possible bore: its pixels require rays too, so
holes are never filled as opaque glass. Refinement-cap failures fall back explicitly.
Legacy nonconvex occupancy and all finite-perspective cameras retain exact rays.
The saved models' tiny perspective is **not rounded to orthographic**.

A spatial index finds projected overlaps. For a separating normal n from A to B,
a positive support gap g implies `(tB−tA)(n·eye) ≥ g` on any common orthographic
ray. This establishes pair order from actual geometry, not center depth. Mask
subtraction uses each pair independently. A three-body fixture has **0 in front of 1,
1 in front of 2, and 2 in front of 0** in different image regions. Center sorting
mislabels 18 pixels; both new methods match the oracle. Unproved separation uses rays.
The fixture uses slender synthetic solids, not a proposed necklace geometry.

Eight saved/control models cover **686,428 identical native target-grid coordinates**,
with zero hybrid or isolated-layer owner disagreements against R315, zero unknown
oracle rays, and zero disagreements on **16,744 known original-Python sampled rays**.
Further fixtures cover face-on holes, edge/oblique views, near tangency, a 0.0001-unit
contact gap and the regional cycle. Independent Python unknowns are retained, not
counted as agreement. All tested identical owner rasters have zero maximum and p95
raster-contour displacement. These finite checks do not prove unrestricted correctness;
the original renderer remains the reference and all fitting used R315 refined rays.

**How quickly?** Cold polygon construction is currently slower. Representative
single-pass target-grid timings, seconds, are below; the full breakdown is in
[benchmarks](r316/results/benchmarks.json). R314's shorter time includes its unresolved
rays and is not an equivalent resolved answer.

| Model | R314 compiled | R315 refined | Hybrid cold | Isolated ray layers cold | Cached layer composition |
|---|---:|---:|---:|---:|---:|
| Saved R306 | 0.297 | 0.375 | 0.378 | 0.588 | 0.0041 |
| Convex orthographic control | 0.252 | 0.384 | 1.088 | 0.488 | 0.0039 |
| Tilted convex control | 0.226 | 0.368 | 2.837 | 0.599 | 0.0038 |

The convex orthographic case needs fallback on 10,476/84,367 pixels. Its expensive
part is support-polygon construction, not mask subtraction. The benchmark process's
cumulative peak RSS is about **279 MiB**, not per-method isolated peak memory.
Forty same-inner-polygon overlap tests give identical Boolean and continuous-clipping
occupancy: clipping plus rasterization takes 0.717s total versus 0.000097s for AND
on already cached masks. This is a representation comparison, not a whole-render
speedup; mask generation is excluded from the AND timing.

A useful narrower acceleration **does** work. On the same 317,856 frozen photographic
coordinates, a local phase or orientation proposal reuses **237/272 individual layers**.
Rendering falls from 0.550/0.541s to 0.189/0.125s; including geometry, complete contact
certification and development scoring, **0.652→0.290s (2.24×)** and
**0.648→0.232s (2.80×)**. These final timings ran sequentially without another computational job; the earlier timing records are also retained. Translation or radius changes invalidate all affected layers
and are slower cold. Repeating an unchanged frame is much faster but is not a fitting
speedup. Cached orthographic silhouettes also survive pure image translation exactly.
[Cache timings](r316/results/cache-benchmark.json) distinguish each case. No 10×
proposal speedup or default renderer replacement is claimed.

**Which beads incorrectly obscure the early features?** The automatic ledger records
all candidate occupied masks, first-hit occluders, overlapping layers, sampled depth
margins, conditional +1/+6/+7 neighbors, separating-gap bounds and nearby paper
brackets. The 36 enlarged cards use the actual photograph and complete best-candidate
isolated contours, checked not to touch crop edges. Counts refer to the stated crop;
overlap counts can overlap, while first-hit removal counts are disjoint.

In R306, the first-negative best isolated candidate −9 covers only 48.1%; −7, −8 and
−1 hide 55, 43 and 30 of its core pixels. Removing occlusion cannot repair its absent
surface. At +8, candidate +8 covers 93.9% in isolation; +7 and +14 hide 39 and 20
pixels. At the +12 feature, candidate +11 covers 66.4% in isolation but +12 hides
238 pixels. These are model-index statements, not recovered physical identities.

**Why was the first negative isolated projection wrong, and does joint geometry help?**
The initial 183-evaluation deterministic experiment tests shared diameter/thickness,
tilt and three convex exterior profiles before compact placement/orientation controls.
It retains 146 certified settings, 37 actual penetrations and a 95-member Pareto set.
The R315 narrow parent plus **15% greater axial thickness and +8° shared tilt** raises
first-negative visible coverage to 59.3%; a separately tested **+3px x translation**
then reaches 82.3%. Radius and bore remain unchanged in this useful branch. This
establishes a correctable projection/placement restriction, not the true glass shape.
The remaining 14.3% isolated deficit is still real in the final diagnostic.

That intervention worsens +8 to 58.9%. A separate 45-control positive-side experiment
recovers it to 77.7% while preserving the negative gain. Its scalar diagnostic winner
instead worsened +8 to 39.5%; that failed selection is preserved as `positive-followup`.
An explicit simultaneous-constraint selection retains the useful alternative. A final
27-control negative-neighbor test preserves first-negative ≥80%, +8 ≥75%, development
paper ≤0.5%, and comparison paper/bracket limits before maximizing the next-negative
core. Fourteen settings satisfy those local constraints. The resulting `joint-recovery`
uses compact phase increments at −13/+13, coherent −10°/+10° orientation bumps and
one compact station change. No individual bead is independently moved or resized.
All 255 evaluated controls, including repeated seeds, are saved; no random campaign
or redundant global/low-frequency phase search was performed.

| Fixed core; maximum visible single-owner fraction | R306 | R315 narrow | Negative repair | Final joint recovery |
|---|---:|---:|---:|---:|
| Reference | 84.8% | 81.2% | 83.3% | 87.9% |
| First negative C-1477-0290 | 28.6% | 52.2% | 82.3% | **85.1%** |
| Next negative R282-1459-0316 | 57.3% | 41.0% | 53.6% | **71.9%** |
| Early +8 | 78.2% | 74.5% | 58.9% | 77.7% |
| Early +12 | 58.2% | 69.5% | 63.3% | 63.3% |
| C-1559-0252 | 48.6% | 67.3% | 71.4% | 78.6% |

**Important correspondence distinction:** final first-negative candidate −7 has
85.7% isolated and 85.1% visible coverage. At the *next* negative core, candidate
−15 has **98.6% isolated but only 3.1% visible**: −14/−8/−7 hide 212/56/14 pixels.
The table's 71.9% belongs instead to visible candidate **−14**. These must not be
combined into one recovered bead. Layering exposes the ambiguity rather than
allowing isolated overlap to establish identity.

**Do the gains survive across the same 200-bead interval?** Every selected export
contains all 200 native target grids and full-necklace contact/occlusion, plus the
same 40 measured cores and all fixed photographic coordinates. Unmeasured bodies
remain unmeasured. Final added phase-rate maximum is 0.03954rad/address (4.09% of
2π/6.5), with 0.584% added station-rate maximum. These are exploratory bounds, not
measured strain. Complete-chain separation certifies; its smallest saved plane
margin is 0.000163 source units, a certificate bound, not measured clearance or
mechanical equilibrium. Universal +1/+6/+7 contact is neither required nor inferred.

| Whole fixed evidence | R306 | R315 narrow | Final joint recovery |
|---|---:|---:|---:|
| Development material explained | 90.08% | 88.98% | 90.74% |
| Development paper occupied | 0.148% | 0.314% | 0.228% |
| Development mean core single-owner coverage | 69.78% | 70.47% | 72.13% |
| Development supported seam conflicts | 44.72% | 29.27% | 33.33% |
| Development finite bracket p95 | 9.0px | 10.0px | 9.0px |
| Development worst-core p95 | 13.60px | 13.14px | 13.42px |
| Comparison material explained | 88.94% | 87.78% | 90.62% |
| Comparison paper occupied | 1.537% | 1.746% | 0.970% |
| Comparison mean core single-owner coverage | 55.87% | 57.66% | 56.14% |
| Comparison seam conflicts | 37.31% | 26.87% | 26.87% |
| Comparison finite bracket p95 | 15.6px | 15.6px | 14.3px |
| Comparison worst-core p95 | 9.85px | 10.30px | **10.77px** |

All 414 brackets remain finite, but the maximum excess worsens 57→62px. Development
paper intrusion and comparison worst-core error regress against R306; the final
model fails absolute material, seams, core and exterior readiness. The comparison
cohort is previously exposed diagnostic evidence, not fresh validation. Historical
50px-sentinel fields remain in inherited metric records for transparency; selection
and this table use R315 finite full-line brackets.

**Most valuable next correction:** constrain coherent relative placement/orientation
using the exposed +12 boundary and the next-negative −14/−15 separation together.
+12 still lacks a good complete isolated explanation, while the next-negative near-
complete isolated alias is almost entirely hidden. The evidence does not uniquely
identify shape versus orientation versus packing, nor prove a mathematical barrier
to joint improvement. It does rule out ray uncertainty or a faster compositor as
sufficient remedies. A mechanically credible joint placement law must explain these
neighboring surfaces simultaneously; another bore adjustment or identity relabel
cannot do that. This is a proposed next scientific question, not authorization for
another round.

Original R314 connected patches, faint lobes, ties and peak-minimax API are unchanged;
all inherited bright observations remain available. No illumination, refraction,
color pattern, physical index chain or valid principal Emax is claimed. Verification
replays selected geometry, independent full-chain support witnesses, original Python
rays, exact metrics and raw-photo crops. Static desktop/narrow/offline checks and
38 contracts are recorded. Earlier failures and all prior science are preserved. Raw-pixel verification caught
an enlarged +8 crop crossing the frozen image-array edge; explicit crop bounds
and recorded crop origins repaired it. The failed panel/log and a subsequent
crop-origin JSON type error are retained in `review-preflight-failure`. These
presentation failures never changed fitting coordinates or metrics.
Work began 22:22:46 UTC; scientific experiments ended before 22:34 UTC, leaving more
than the required six-minute delivery reserve. Final commit, remote check and elapsed
wall time are recorded in the receipt. **Stop for scientific review. No automatic R317.**
