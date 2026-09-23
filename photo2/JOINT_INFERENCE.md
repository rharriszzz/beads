# Joint triangle and three-direction tracing — R043

Local lattice constraints reject the known false bridges, but lose too many
correct edges to support necklace indexing. At T12 the shape rule raises pair
precision from **95.45% to 96.86%**, while recall falls from **55.61% to 16.73%**.
The displayed 611–613 shortcut is rejected, but its correct 611–612–613 path is
also absent. This experiment does not establish visual ambiguity for a person.

[Whole ring with the R041 location boxed](output/joint-audit-verified-2/whole-ring-joint.png),
[eight-view comparison](output/joint-audit-verified-2/comparison.png),
[R041 detail](output/joint-audit-verified-2/r041-location-joint.png),
[crossing comparison](output/joint-audit-verified-2/crossing-comparison.png).

## Reproduce and provenance

From the repository root, using Python 3.12 and the existing local dependencies:

```sh
.venv/bin/python photo2/joint_audit.py --output photo2/output/joint-audit-new
.venv/bin/python -m unittest discover -s photo2 -p 'test_*.py' -v
```

Default inputs are the paired R039 `output/inference-audit-verified/` and
R030/R031 `output/neighbor-audit-final/`. Output must be new or empty.
If the ignored inputs are missing, recreate the render audit using NEIGHBORS.md
and its baseline inference using INFERENCE.md, then supply both matching paths:

```sh
.venv/bin/python photo2/neighbor_audit.py --output photo2/output/neighbor-input-new
.venv/bin/python photo2/inference_audit.py --input photo2/output/neighbor-input-new --output photo2/output/inference-input-new
.venv/bin/python photo2/joint_audit.py --input photo2/output/inference-input-new --render-input photo2/output/neighbor-input-new --output photo2/output/joint-audit-new
```

These missing-input commands were inspected, not rerun. Final evidence is under
`photo2/output/joint-audit-verified-2/`; report SHA-256:
`3e2672183f55b93bb258f3f7acd8bb365184f6ba6efc3827a2c4810b0e874f71`.
Ten current source hashes, seven baseline source hashes/208 baseline artifacts,
and eleven current/historical render source hashes/148 render artifacts were
checked. The baseline report must bind the exact supplied render report.
The new report retains actual commands, versions, parameters, both input-report
hashes, all trial files and 114 artifact hashes. Input/truth files are referenced
through the verified manifests; their missing-index lists are preserved unchanged.

## Fixed rule and scope

`joint_neighbors.py` accepts anonymous visible-mask centroids and optional mask
covariances. No source indices, colors, physical axes, helicity, camera, source
layout or total bead count enters inference. The masks remain supplied by the
renderer: this is not segmentation from a beauty image. The maker's advice to
trace all three directions motivates this experiment; it is not evidence that
these particular image rules implement the maker's visual judgment correctly.

The rule is a conservative local heuristic, not a global lattice optimizer:

1. Reuse R039's ellipse-based tangent reference and optional covariance steering.
   Consider the nearest 12 neighbors within 1.6 times the third-neighbor distance;
   include distance ties at the 12th boundary so anonymous IDs cannot choose them.
2. Permit adjacent sector labels within 12 degrees of the original angular
   boundaries. Keep candidates within 1.15 times the nearest distance in each
   endpoint/direction slot; require reciprocal label eligibility. This retains
   nearby label/neighbor alternatives without looking up source truth.
3. Enumerate signed three-family triangles satisfying `1+6=7` (including equivalent
   signs), excluding nearly collinear triangles with sine below 0.08. Also enumerate
   two-step, same-family continuations with turn at most 35 degrees and length
   ratio at most 1.8. These geometric assumptions can fail under projection.
4. Score each candidate as twice its occupied triangle-side count plus its
   continuation-endpoint count. Both kinds of support must be present. Select
   only a unique best score for each endpoint/direction, require reciprocal
   selections, and abstain if multiple labels survive for one pair. Keep all
   candidates, tied scores and unreciprocated alternatives in the report.
5. Repeatedly remove edges lacking a fully retained triangle or continuation.
   Save every removal round. Follow the remaining edges into maximal paths and
   cycles for each of the 1/6/7 families, keeping their component offsets unknown.

The constants were fixed before the new scored runs; no threshold search or
truth-based repair followed the scores. The second convention reverses 1 and
swaps 6/7 while preserving the same pairs. Global reversal remains unresolved.
Alternative diagnostics explicitly reference the first convention's candidate IDs.
The paths concatenate local two-edge support; they do not optimize long rows or
reason about full projected bead boundaries, depth or occlusion order.

## Rendered-view results

The table uses shape features and each of eight views once (seed 17). Thresholds
and views overlap; the second shuffle checks relabeling, not independent evidence.
The centroid-only comparison and every trial are retained in summary.csv/report.json.

| T | Rule | Correct / proposed pairs | Pair precision | Pair recall | Best signed precision* |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | Baseline | 6,014 / 6,479 | 92.82% | 51.80% | 77.99% |
| 1 | Joint | 1,297 / 1,338 | 96.94% | 11.17% | 93.87% |
| 12 | Baseline | 6,149 / 6,442 | 95.45% | 55.61% | 82.24% |
| 12 | Joint | 1,850 / 1,910 | 96.86% | 16.73% | 94.40% |
| 100 | Baseline | 6,078 / 6,167 | 98.56% | 60.85% | 89.04% |
| 100 | Joint | 2,571 / 2,608 | 98.58% | 25.74% | 97.32% |

*Evaluation-only best convention and global reversal per view. The solver never
makes this choice. Pair precision ignores the signed label; even a correct pair
can receive a wrong index difference. Improvement is not uniform: T12 shape
precision for the opposite-hand 13-repeat half-phase view falls to 91.75% from
95.75% (rounded chart: 91.7% and 95.8%).

At T12 the joint shape candidates contain 7,707 true pairs among 8,618 distinct
pairs. Requiring both initial motifs leaves 4,033 true pairs among 4,364. Reciprocal
score selection leaves 3,929 among 4,223; repeated support pruning leaves 1,850
among 1,910. There are 11,057 available true pairs. Thus both initial geometric
support assumptions and cascading pruning remove substantial correct evidence.
This localizes the loss to stages; it does not yet separate centroid displacement,
projection-induced curvature and the support rules as causes.

Forty of 192 joint convention graphs still contain an inconsistent nontrivial
component; all 192 baseline graphs did. Consistency is insufficient: for T12
shape, even using the evaluator's best convention per view, the 33 consistent
nontrivial components contain **66 wrong relative indices among 846 nonseed
vertices**, allowing reversal independently per component. Convention +1 alone
has 380/846 wrong. The former is an optimistic diagnostic, not a solver-selected
recovery result. The graph also leaves 3,349 vertices isolated across those views.
Both convention results, duplicate indices, cycle conflicts, per-component errors
and unknown offsets remain explicit. Exact synthetic N is used only afterward
for winding diagnostics, alongside separate integer propagation with no modulus.
No provisional-photo-count modulus or pattern-divisor filter is used.

## Controls and retained limits

- Ideal 200-point brick ring: both feature modes recover all 520 signed edges and
  all 199 nonseed relative indices. This remains an authored 2-D lattice control.
- Three removed interior detections: both modes keep 480/504 true edges with zero
  false pairs, compared with the baseline's 504 true edges plus four false bridges.
  The surviving nontrivial component has 188 correct nonseed indices; eight
  retained detections are isolated. Missing-detection stress is not a claim about
  the maker's ordinary visible patch.
- Superposed rings: shape keeps 594/1,040 true pairs and zero false pairs; centers
  keep 350/1,040 and zero false pairs. The baseline shape result has 96 cross-sheet
  links and eight additional wrong same-sheet pairs. Rejection leaves a large
  gap at the artificial crossing. This is 2-D point-cloud superposition without
  rendered occlusion, and does not validate real crossing separation.

The global ellipse frame, centroid displacement by occlusion, lack of full-outline
fitting, fixed projected smoothness thresholds and conservative pruning remain
limitations. Some displayed orange edges reflect the retained convention mismatch;
panels preserve convention +1 and use only a documented global reversal for
correctness colors, just as the baseline did. No source-truth relabeling is hidden.

## Checks and next task

All 47 tests pass, including eight new checks for signed/nondegenerate triangles,
continuation geometry, ideal exact recovery, retained support, maximal trace
coverage, coordinate/permutation invariance, convention symmetry, invalid inputs
and abstention on indistinguishable duplicated observations. All 48 paired
shuffles preserve signed source-pair sets. Compilation and whitespace pass.
Two final runs reproduce all 114 artifacts byte for byte; reports agree except
command output path. All new source/artifact hashes match. Ten legacy-selected
crop panels were inspected through contact sheets; the opposite-hand weak-slot
crop, comparison chart, crossing chart and whole-ring plot were inspected at full
size. The R041 location detail was also inspected in the development run.

One audit run failed while serializing an added crossing diagnostic as a NumPy
integer. Converted that scalar to Python int and reran both full audits successfully;
no inference logic or thresholds changed. Development/failed outputs remain
ignored separately. No failed unit test. No scene/material change or new visibility
render/full legacy audit; the suite includes existing small renderer checks.
No photo segmentation, sequence integration or fitting was performed.

Next bounded task: diagnose the geometric assumptions on the same synthetic
vertices. Compare visible-mask centroids with projected body centers from the
saved layout and `neighbor_audit.projected_centers`, and measure where known true
1/6/7 continuations violate the fixed turn/spacing/support rules. Mark representative
losses in whole-image context. Body centers and true edges are **instrumented
diagnostic inputs**, not recovered observations or a permitted truth leak into
the image solver. Stop after a causal comparison/report, before another inference
algorithm or photo fitting. Recommend **gpt-6-astra / High, fresh /new** for this
distinct diagnostic step; preserve the maker's answered advice and tentative
±6/±7 rectangular color paths without another question at this round's end.
