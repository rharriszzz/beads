# Image-space neighbor baseline — R039

Measured bead-outline orientation improves neighbor-pair precision on the eight
saved synthetic views. It does **not** yet support reliable relative indexing:
all 192 tested convention graphs contain contradictions. This resolves the first
centroid-versus-shape comparison while keeping automatic photo indexing open.
The maker's minimal-tilt and rectangular-face guidance is saved under R038.

## Reproduce

From the repository root with Python 3.12:

```sh
.venv/bin/python photo2/inference_audit.py --output photo2/output/inference-audit-new
.venv/bin/python -m unittest discover -s photo2 -p 'test_*.py' -v
```

The output directory must be new or empty. Default input is
`photo2/output/neighbor-audit-final/`, the preserved R030/R031 both-hand audit.
If absent, recreate it in a fresh directory and pass it explicitly:

```sh
.venv/bin/python photo2/neighbor_audit.py --output photo2/output/neighbor-input-new
.venv/bin/python photo2/inference_audit.py --input photo2/output/neighbor-input-new --output photo2/output/inference-audit-new
```

The fallback renderer command was inspected, not rerun in this step. Current
sources or their recorded historical versions at Git `08ba3bb` must match the
input manifest; all 148 input artifact hashes are checked. A regenerated input
report has its own recorded hash. Do not overwrite historical reports or bypass
source verification. [NEIGHBORS.md](NEIGHBORS.md) documents the source renders.

Final inspected output: `photo2/output/inference-audit-verified/`. Report SHA-256:
`e27feb373c35931b023e89ab0ece93f5955d3ebf0b16e73d2021b58847153438`.
The report records command, versions, parameters, seven current source hashes,
input provenance and 208 artifact hashes. A second run in
`photo2/output/inference-audit-reproduced-verified/` has all 208 artifacts byte-identical;
reports agree except the command's output path.

## Inputs and fixed inference rule

The evaluator decodes the existing instance-ID renders and computes each visible
mask's centroid and pixel covariance. At T=1, 12 and 100 visible pixels, selected
instances are independently shuffled with PCG64 seeds 17 and 43. The two solver
interfaces receive anonymous coordinates, or coordinates plus mask covariance.
They receive no source indices, colors, body axes, camera, helicity or total N.
Input and evaluation-only truth files are separate. Every omitted source index
is retained in the latter; unknown color never removes a vertex in this test.

These are **oracle instance masks**. Their boundaries and membership are supplied
by the renderer, not detected from a beauty image. Pixel thresholds are existing
synthetic visibility settings, not calibrated photo readability rules. Covariance
measures the visible fragment, not necessarily the complete bead's orientation.

`infer_neighbors.py` implements a deliberately simple, fixed heuristic:

1. Estimate a covariance ellipse from the entire centroid cloud. Rotate its
   gradient by 90 degrees to obtain a consistent local tangent reference. This
   assumes one approximately elliptical ring; it is not a general rope tracker.
2. In the shape variant, choose whichever mask eigenaxis is closest to that
   reference, only if covariance eigenvalue ratio is at least 1.3 and angular
   difference is at most 30 degrees. Otherwise retain the position-based frame.
   This tests an outline cue; it does not identify the physical hole axis or fit
   the full rounded-cylinder boundary. It does not assume every mask is rectangular.
3. Consider at most 12 nearest centroids, within 1.6 times the third-neighbor
   distance at the source vertex. Classify a displacement as transverse ±1 when
   its tangent component is at most 0.32 of its length. Other displacements enter
   the two diagonal families according to tangent/transverse signs.
4. Retain two conventions: positive transverse displacement is +1, or -1, with
   the corresponding 6/7 swap. Also preserve the possibility of global reversal.
   Exactly unresolved diagonal boundaries abstain. If a sector's second candidate
   lies within 1.15 times its closest distance, preserve the alternatives and
   abstain. Otherwise propose the nearest candidate in that sector.
5. Keep an edge only if both endpoints propose it with reciprocal signs. Preserve
   all rejected, ambiguous and nonreciprocal proposals for review. Do not repair
   proposals with evaluator truth or force graph consistency.

These constants are heuristic test settings, not recovered measurements or a
parameter search. They were fixed before inspecting rendered-view scores. Review
of the crossing control exposed an exact diagonal-boundary tie; it now abstains
symmetrically under both conventions. No truth-based threshold optimization was
performed. The rule can still bridge a missing immediate neighbor incorrectly;
the missing-interior control deliberately demonstrates this failure.

## Results

The table combines eight views once each (seed 17). Seeds test relabeling, not
additional evidence; thresholds and views also overlap. Pair precision asks
whether a proposed pair is truly separated by 1, 6 or 7 in the known synthetic
chain, ignoring the proposed label. Recall divides correct pairs by all true
neighbor pairs with both endpoints retained at that threshold.

| T | Rule | Correct / proposed pairs | Pair precision | Pair recall | Best signed-label precision* |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | Centers | 6,706 / 7,595 | 88.29% | 57.77% | 74.26% |
| 1 | Shape | 6,014 / 6,479 | 92.82% | 51.80% | 77.99% |
| 12 | Centers | 6,778 / 7,461 | 90.85% | 61.30% | 78.90% |
| 12 | Shape | 6,149 / 6,442 | 95.45% | 55.61% | 82.24% |
| 100 | Centers | 6,712 / 7,114 | 94.35% | 67.20% | 85.62% |
| 100 | Shape | 6,078 / 6,167 | 98.56% | 60.85% | 89.04% |

*This is an **evaluation-only upper diagnostic**: choose the better retained
convention and global reversal separately for each view, then count exactly
correct signed labels over all proposals. The solver never makes that selection.
Even that favorable choice leaves substantial label errors. Both alternatives,
reversal scores and absolute-family confusion counts remain in the report.

At T12, the screen-bend region (either endpoint farther than 0.8 image half-width
from the centroid-cloud mean x) improves from 1,688/1,838 correct pairs, 91.84%,
to 1,379/1,409, 97.87%. Proposals touching a mask smaller than 100 pixels improve
only from 492/808, 60.89%, to 441/658, 67.02%. These regions overlap and are
simple evaluator diagnostics. Small area is a proxy for a sliver, not a measured
occluded fraction or a calibrated color-readability rule.

[Eight-view comparison](output/inference-audit-verified/precision-recall.png),
[original-hand bend](output/inference-audit-verified/repeat-40-h+1-phase-0-right-inferred.png),
[rectangular-face / weak-slot crop](output/inference-audit-verified/repeat-13-h+1-phase-half-r023-inferred.png).
Ten crop panels retain the original audit's bend and weak-slot selections; these
selections affect illustration only. Panels show convention +1, arrows labeled
by that convention, and an explicitly evaluator-selected global reversal for
coloring correctness. Orange edges in opposite-hand panels therefore include
unresolved convention mismatches. They are not secretly relabeled as successes.

## Relative indices and controls

All 96 input/mode trials × two conventions have at least one inconsistent
component. Exact propagation uses known synthetic N for seam/winding diagnostics
**after** inference. Its raw tree potentials are retained for error diagnosis,
marked `diagnostic_only_unvalidated_edges`; no consistent subset is silently
promoted to recovered indices. Disconnected component offsets remain unknown.
No photo modulus or provisional-count divisor constraint is used.

Consistency is insufficient even for small disconnected components. For T12,
seed 17, convention +1, the shape rule produces 40 consistent nontrivial
components containing 69 nonseed vertices; 46 of those relative indices are
wrong even allowing reversal separately per component. The corresponding
center-only counts are nine components, 17 nonseed vertices and 12 wrong.
These are conditional diagnostics, not accuracy claims for accepted recovery.
Both conventions' component membership, conflicts, duplicate indices, winding
and per-reversal errors are retained. No truth offsets join components.

Three authored 2-D controls are separate from the POV renders:

- A 200-point staggered brick ring has 520 available edges. Both rules recover
  every pair and every signed label under convention +1, with one consistent
  component and zero relative-index errors. This validates the rule on its ideal
  lattice, not on bead projections.
- Removing three interior detections leaves 504 true edges. Both rules propose
  508 edges, including four false bridges, and the graph becomes inconsistent.
  This is an artificial missing-detection stress, not a claim that unseen beads
  normally occur inside the maker's visible patch.
- Superposing two brick rings produces 104 cross-sheet links among 736 center
  proposals and 96 among 790 shape proposals. These are false neighbors. The
  solver receives no sheet identities. This is a 2-D crossing stress outside the
  single-ring frame assumption, **without rendered occlusion or physical bead
  geometry**. The saved eight legacy views have no rope crossing, so they alone
  cannot validate crossing separation.

[Crossing stress illustration](output/inference-audit-verified/crossing-stress.png).

## Checks, limits and next step

All 39 repository tests pass, including seven new controls for ideal-lattice
indices, permutation/rigid-motion invariance, reciprocal alternatives, bad inputs,
analytic rectangle moments, exposed missing-detection failure and crossing sign
symmetry. All 48 paired-shuffle comparisons agree on signed source-pair sets.
Compilation, whitespace, seven current source hashes, eleven historical input
source hashes and all 148 input artifact hashes pass. All 208 new artifacts are
byte-reproducible. The ten crop panels were inspected in contact sheets; the
original-hand bend was also inspected at full size, and the summary and crossing
figures at full size. No failed runtime assertion/test occurred. One development
patch had unmatched context and made no changes; it was reapplied with corrected
context. Development outputs remain ignored separately from final evidence.
The staged whitespace check subsequently caught an extra fixture EOF blank line.
After removing it, both audits were regenerated in the verified directories above;
all 208 artifacts also match the earlier inspected run byte for byte. No logic
changed, so the runtime suite was not repeated for this whitespace-only correction.

No scene or material changed. No new visibility render or 49-render legacy audit
was necessary; the full test suite includes its existing small renderer checks.
No photo segmentation, indexing, color reading, repeat search or fit was run.
This baseline does not establish that the photograph is insufficient or that the
maker's neighbor rule fails. Its present image-direction and nearest-choice
heuristics are not reliable enough.

Next bounded task: test **joint local triangle/lattice constraints** for edge
selection and ±1/±6/±7 assignment, using `1+6=7`, mask orientation, retained
alternatives and abstention. Keep this fixed baseline and failure controls for
comparison; select edges without source truth and score component-relative
indices afterward. Stop after the synthetic report/checks, before photo
segmentation, sequence integration or fitting. Use gpt-6-astra / High with a fresh
/new for that distinct algorithm step.
