# Both legacy helicities and supplied-neighbor index audit — R030/R031

`beads.pov` now supports both helicities. Exact graph propagation recovers the
relative indices in all eight tested views when supplied with the correct
±1/±6/±7 edges. This validates index propagation and its error checks, not finding
those edges automatically in a photograph. Photo 2's hand and pattern remain
unresolved; its adequate working count remains 2,698.

## Reproduce

```sh
.venv/bin/python photo2/neighbor_audit.py --output photo2/output/neighbor-audit-final
.venv/bin/python -m unittest discover -s photo2 -p 'test_*.py' -v
```

The audit reads the pre-change scene from Git commit
`ab7915841577c27cfb03f779cc765e556ffc9dcd`, checks that the shared bead macro is
unchanged, and regenerates all required renders. No previous output directory is
needed. Keep that commit available in local Git history. The report records
source/artifact SHA-256 hashes, Python/NumPy/Pillow versions, all POV-Ray commands,
geometry CSVs, anonymous graph inputs, evaluation-only source indices, graph
results and diagram selections. Sources are hashed at the start and checked again
at the end. Generated files stay under ignored `photo2/output/`.

## Helicity convention and construction directions

R032/R033 rename the option to `Helicity`; historical R030/R031 generated files
use the previous name and remain unchanged. The recorded audit used commit
`08ba3bb`; its source hashes do not describe the renamed checkout. Use a fresh
output directory when rerunning the audit with current sources.

Use `Declare=Helicity=-1` for the opposite hand. Omission or `=1` preserves
the original scene. Values other than exactly +1 and -1 are rejected. This is a
legacy-only option; `Photo2=1` retains its separate Python/settings handedness.

For index i, exact beads/row e and clock phase r, the angles in degrees are:

```
chain_angle = 360 * (i/N + r*0.1666)
row_angle   = 360 * (Helicity*i/e + r)
```

Only the small-radius winding rate changes sign. Clock phase, large-circle
traversal, integer index/color ordering, body dimensions and tangent hole axes
stay fixed. The signs name this equation, not a claimed physical right/left hand
for the photograph. Whole turns still close the ring for either sign.

The maker's R030 explanation agrees with the source: ±1 advances around the
small radius; ±6/±7 lie on the diagonals, with orientation depending on hand.
At exactly 6.5 beads/turn, positive offsets 1/6/7 have principal small-radius
increments +55.3846/-27.6923/+27.6923 degrees for the original hand, reversed
for the other hand. Their large-circle increments are all positive. The 800-bead
fixture closes with 123 turns, so its diagonal increments differ slightly.
The displayed directions also change with position around the bent rope.

The maker says unseen beads occur at visible-patch edges, not between visible
neighbors. This is saved construction guidance. Removing low-pixel vertices and
deliberately deleting edges are distinct synthetic stress tests, not evidence
that interior hidden beads are routine in the photo. No connection jumps over
an absent immediate neighbor.

The audit preserves the literal source expression `sin(180/beads_per_row)` for
bead radius: POV-Ray's sine argument is in radians, whereas `vaxis_rotate` takes
degrees. An initial Python cross-check mistakenly converted this expression to
degrees; it failed and was corrected. No bead-dimension correction was made to
the legacy scene.

## Graph experiment and results

The evaluator selects visible vertices at thresholds 1, 12 and 100 pixels. It
supplies immediate edges for each ±1/±6/±7 offset only when both endpoints remain.
PCG64 seeds 17 and 43 permute source-index-sorted vertices to anonymous IDs. The
solver receives only vertices, signed edges and (for the full ring) exact synthetic
N. It receives neither colors nor true indices. Truth is checked afterward,
independently relative to each component's seed. Disconnected components retain
unknown offsets; evaluator truth never joins them.

All 24 full-ring configurations are connected; both shuffles recover every
relative index modulo exact N. The table gives vertices in that single component:

| Invented repeat | Hand | Phase | T=1 | T=12 | T=100 |
| --- | ---: | --- | ---: | ---: | ---: |
| 40 / N=800 | +1 | 0 | 566 | 547 | 515 |
| 40 / N=800 | +1 | half | 574 | 550 | 493 |
| 40 / N=800 | -1 | 0 | 571 | 550 | 494 |
| 40 / N=800 | -1 | half | 568 | 545 | 513 |
| 13 / N=780 | +1 | 0 | 563 | 538 | 489 |
| 13 / N=780 | +1 | half | 551 | 532 | 494 |
| 13 / N=780 | -1 | 0 | 564 | 537 | 489 |
| 13 / N=780 | -1 | half | 555 | 530 | 497 |

The four quarter-ring patches per view are lifted to integers with index-seam
edges excluded. In phase half, the geometric 0–90-degree quarter crosses that
index seam and therefore has two components. All other quarters have one.
These separate offsets are retained rather than joined using truth. Across the
240 trials (8 views × 3 thresholds × 2 shuffles × 5 regions), there are no
relative-index errors, missing reciprocal edges, duplicate-index conflicts or
unexplained cycle residuals. Graph files retain every missing neighbor direction,
component membership, per-family edge count and triangle/cycle count.

Full-ring traversals record nonzero cycle sums that are integer multiples of N
as winding. They are not local contradictions. No modulus based on the provisional
photo count is used. Raw tree potentials/winding-edge counts can depend on the
seed; component-relative residues and connectivity agree under both shuffles.

Independent controls catch contradictory triangles, conflicting duplicate
constraints, duplicate index assignments, missing reciprocals and a wrongly
lifted closed ring. They retain a missing-edge alternate path and disconnected
components. A wrong bridge deliberately passes all cycle checks while assigning
the wrong relative offset: truth 0,1,20,26 becomes 0,1,7,13. Thus a consistent
graph alone cannot certify a perceived image edge. Reversing every sign likewise
preserves consistency; propagation alone cannot select helicity.

## Illustrations and renderer checks

The output contains eight enlarged bend panels, one per view/hand, plus two
panels at R023's weak-slot bead #533. Each compares beauty with the same crop
annotated with signed solid/dashed/dotted edges. Missing edges have no arrows;
outlined endpoints for missing beads explicitly show evaluator-known positions.
Circles are projected source centers, crosses are measured visible-mask centroids,
and gray segments show their displacement. They are not interchangeable.

- [Original-hand weak-slot panel](output/neighbor-audit-final/repeat-13-h+1-phase-half-weak-neighbors.png)
- [Opposite-hand same-index panel](output/neighbor-audit-final/repeat-13-h-1-phase-half-weak-neighbors.png)
- [Original-hand bend](output/neighbor-audit-final/repeat-40-h+1-phase-0-bend-neighbors.png)
- [Opposite-hand bend](output/neighbor-audit-final/repeat-40-h-1-phase-0-bend-neighbors.png)

Projection uses the actual camera's left-handed coordinates and default right
vector length 1.33, not an exact 4/3. Initial diagrams exposed a horizontal flip;
an isolated-marker check then caught the small aspect-ratio discrepancy. The
corrected projection agrees with three rendered marker centroids within 0.15 pixel
(required tolerance 0.25 pixel). These isolated marker centroids test projection;
they do not imply occluded bead centroids are accurate source centers.

All eight default legacy cases are pixel-identical before/after at 480×360 with
an interior clock value per case. For all four original R023 configurations,
explicit +1 also reproduces historical beauty pixels, full ID arrays and geometry
CSV values exactly at 2400×1800. For all eight both-hand views, the ID foreground
and palette foreground agree exactly, and every ID pixel has the correct source
palette color. Exported coordinates match independently evaluated placement
equations, both winding slopes have the expected sign, phase is preserved, and
opposite hands have different positions. The audit uses 49 POV-Ray renders.

The invented legacy beauty palette is red/green/blue; it is not a fit of the
photo's red/yellow/black appearance. The visibility thresholds are sensitivity
settings, not calibrated color-readability rules. Existing beauty gamma/version
warnings remain; instrumentation uses explicit gamma and no antialiasing.

Twenty-five tests pass, including invalid-helicity parse checks and both-hand
palette/ID rendering. Compilation and whitespace checks pass. All 11 source and
148 artifact hashes match disk; final report SHA-256 is
`d1bd07fe49675342db49fd70a7983cb3509d50f4db663b4abfaf7ced3f7ab242`.
All ten final panels were visually inspected. The old R023 report's seven source
hashes were verified against baseline Git and all 74 artifact hashes against disk;
its four original ID/beauty/layout arrays and visibility statistics match the new
+1 outputs. Earlier audit directories contain development diagnostics, including
incorrect projection panels; use `neighbor-audit-final` for final evidence.

No segmentation, photo indexing, sequence recovery, material
fit or photo refit occurs in this step. Next is METHODS.md §B: validate strong
partial-word periods with known synthetic indices and unknown colors, stopping
before connecting it to automatically extracted image neighbors.
