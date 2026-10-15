# R292 — observed photographic separator constraints

R292 corrects the demonstrated separator-crossing mechanism in
`reserved-yellow-05`: all three formerly included R291 dark-trough samples are
outside the new target region. Its neighboring extension is removed. The result
is automatically generated and awaits the user's judgment; smaller area is not
proof of correctness.

The 13 accepted R291 references survive within the declared review tolerance:
**eight pixel-identical, five with one-pixel-deep changes, none materially changed**.
Q14 and development-yellow-03 reproduce accepted B exactly. Red-worst changes by
one added pixel. This is regression evidence, not new human acceptance of R292.

The broader problem is not fully solved. Some source-connected regions still
include material on both sides of an observed seam by passing around an unresolved
end. New holdouts expose clear remaining mergers and paper/reflection ambiguity.
All 77 primary proposals remain partial/unresolved; no failed method is interpreted
as proof that the photograph itself is insufficient. Production is unchanged.

Launch from the repository root:

```bash
photo2/review/r292/launch.sh
```

Open **http://127.0.0.1:8292/**. **Start Here contains 11 cases**, prioritizing the
old clear-photo failure, other repaired crossings, difficult holdouts and remaining
regressions. Unchanged accepted cases need no repeat answer. The original photograph
is beside the annotated crop. Toggle **Separators only** to judge the measurement
without the proposed outer contour; toggle all markings with H. Green denotes a
constrained observed arc, pink an internal/ambiguous alternative, and open endpoint
circles mean unresolved continuation. Thin cyan/orange outer edges retain supported
versus uncertain distinctions. Raw native pixels, zoom/pan, six one-click answers,
optional diagnostics, undo/history/export/reopen and pair-ownership reuse remain.
Feedback is separately versioned under `r292/feedback/`; no machine-generated human
answers or copies of old boundary judgments are inserted into it.

## Collection, development and freeze

All 68 exposed R291 cases are development/regression evidence. Before detector
development, selection froze nine new accepted R289 features: four red-context,
four yellow-context, one unknown-context. Targets are hash-ranked using
`SHA256(R292-reserved:featureID)`, at least 100 native pixels from all 68 old targets
and earlier new targets. The second unknown slot was unavailable; its rule was not
relaxed. Larger contexts can overlap and this is one historically studied photo,
not independent scene validation. Context color is a feature-selection proxy,
not physical bead identity.

Collection freeze: **2026-10-15T14:46:13Z**. Method/source freeze:
**2026-10-15T14:59:23Z**, before opening the nine holdout outcomes. No inference
source or parameter changed after that freeze. Prior R290/R291 code, results,
feedback and the archived complete human ledger are preserved. The first full
valley-only development run and the illumination-extension probe, with their
sources and failures, remain under `r292/checkpoints/`.

## What the B ablation establishes

A full 2x2 experiment on all 68 exposed cases independently changes R291's direct
stop penalty (4.5 versus 2.7) and competing-point sink capacity (1e8 versus 5000).
It reproduces saved R291 A and every displayed B exactly in their original context.

- Relaxing darkness alone reproduces the accepted B for Q14 (314 pixels) and
  development-yellow-03 (408 pixels). Weakening the peer anchor alone leaves A
  unchanged in both cases.
- The same global darkness relaxation expands red-worst from its accepted 390
  pixels to 642, with mask IoU .6075 to accepted A.
- Darkness-only changes 36 cases; peer-only changes eight. Effects can interact.

This supports retaining strong peer exclusions and making continuation local.
It does not prove that darkness relaxation is correct everywhere.
[Exact factor outcomes](r292/results/r291-B-ablation.json.gz).

## Revised single-target algorithm

The runtime takes the original ICC-managed photographic pixels, one independent
bright patch and contextual independent features. It never receives case names,
categories, old contours, manual ownership, user judgments or a physical model.
No size, roundness, convexity or geometric plausibility rejection is used.

1. **Keep R291 A–E measurements.** Coherent dark profiles, multiscale illumination
   edges, material direction, bright continuity and junction/termination annotations
   retain their original meanings. R291's binary target objective supplies an initial
   proposal and coherent five-track corridor candidates. Neighboring features are
   context in one binary target solve, not simultaneously reconstructed beads.
2. **Follow actual local observations.** Around each supported corridor, sample a
   rotated one-pixel lattice. Normal profiles compare the local minimum with maxima
   at 3/5/7 pixels on each side. A valid dark anchor needs a bilateral valley with
   ratio below .65, illuminated sides and local edge evidence. Dynamic programming
   follows adjacent measured samples, allowing up to two pixels of normal movement
   per one-pixel tangent step, with a weak .025 regularizer. Search orientation and
   extent bound computation; they are not object-shape acceptance requirements.
3. **Use complementary evidence at dark-seam ends.** A tracked arc can continue
   through coherent multiscale/color transitions, discounting illumination edges
   contradicted by bright-material continuity. It cannot start from illumination
   alone. At the first unsupported continuation, the supported path ends. No chord
   joins the five old minima, no unsupported gap is bridged, and no endpoints are
   extended into a fabricated closed contour.
4. **Retain internal-darkness alternatives.** Darkness connected beyond a two-pixel
   dilation of the initial target proposal supports an exterior interpretation.
   An arc needs at least 60% of its samples on such dark components before strong
   enforcement. Enclosed darkness stays a shadow/hole alternative. Contradiction
   with the independently measured bright core prevents enforcement. This exterior
   test depends on an imperfect initial proposal; it is evidence, not ownership
   truth, and can still misclassify connected shading. No certified hole labels are
   available. Six exposed arcs and one holdout arc remain unenforced alternatives.
5. **Enforce the observed bank, not just a highlight center.** Constrained valley
   pixels and their one-pixel peer-facing bank receive strong non-target capacity
   in the same graph. Only these observed locations are constrained, rather than
   a half-plane, straight end chord or inferred full neighbor mask. This removes
   the narrow detour admitting adjacent yellow material in reserved-yellow-05.
   Unsupported endings remain unresolved; material can still route around them.
6. **Make continuation local.** A darkness-softened solve with the same strong
   separator/peer constraints proposes interruption alternatives. For each added
   connected component, measure the old cut and proposed replacement edge. Relax
   its unary cost only if at least half the old cut conflicts with illuminated
   continuity, replacement has strictly more supported sides, and the number of
   unresolved replacement sides does not increase. Re-solve the graph with only
   those local relaxations. This reproduces the two accepted B contours, rejects
   red-worst's 251-pixel unsupported extension and retains its one-pixel edge change.
   It is an evidence hypothesis, not a calibrated correctness score; some mergers
   still pass it. B, where meaningfully different, retains strict interruption
   treatment with the same separator constraints.

The tracker saves measured paths, normal direction, darkness/illumination sample
counts, exterior-connection evidence, contradictions and unresolved endings. Every
candidate still receives T1–T8 and exact native contour-side measurements. Supported
outer segments need photographic A/B/C justification; unsupported closure stays
uncertain. Reflection boundaries remain distinct from unknown black-body silhouettes
and physical centers. No visible-region/physical centroid is certified.

## Crossings, remaining detours and regressions

The old bypass test checked only another bright point. R292 separately measures:

- **Direct crossing:** valley pixel and both sampled banks (±2px) inside the target.
- **Both banks inside:** both sampled banks inside, whether the valley is included
  or excluded. An excluded valley with both banks still in the source-connected
  region flags a possible route around an unresolved end.

| Diagnostic | 68 exposed cases: R291 reference → R292 | Nine new holdouts: initial R291 objective → R292 |
|---|---:|---:|
| Direct crossing samples | 165 → 0 | 33 → 0 |
| Both-bank inclusion samples | 171 → 31 | 35 → 14 |
| Cases with remaining end-around samples | 5 after | 4 after |
| Observed arcs / constrained arcs | 179 / 173 | 26 / 25 |
| Median minimum parameter/context IoU | .986 | .980 |
| Worst minimum IoU | .455 | .217 |

These are sampled diagnostic counts; overlapping arcs can share locations. Direct
crossings are mechanically prevented at constrained locations, so zero is an
implementation result, not proof of correct bead ownership. The both-bank counter
prevents that zero from concealing the remaining mergers. R291 comparison uses
user-selected A/B where accepted, otherwise A. New holdouts have no saved R291
baseline; their before column is the initial R291 objective in the same R292 context.

[Every case and numeric change](r292/results/case-comparison.csv),
[full comparisons](r292/results/comparison.json),
[summary](r292/results/summary.json), [situation matrix](R292_COVERAGE.md).

| Human-accepted R291 reference | R292 change |
|---|---|
| Q14 B; development-yellow-03 B | Exact accepted masks reproduced automatically |
| N06 A; yellow-multiple-2 A; development-yellow-05 A; reserved-yellow-04 A; diagnostic-02 A; fresh-unknown-01 A | Exact accepted masks preserved |
| P2 A | Two pixels removed, one-pixel-deep difference |
| P3 A | Two added / 11 removed; IoU .9709; one-pixel-deep differences |
| red-worst A | One pixel added |
| reserved-yellow-01 A | One pixel added |
| fresh-yellow-02 A | Three pixels added |

“Material change” is a review trigger: mask IoU below .97 or any added/removed pixel
more than two pixels from the other mask. It is not an acceptance criterion. None
of the 13 accepted references crosses that trigger, so none is re-requested. Their
comparisons remain accessible in the viewer and the preserved-reference list.

The corrected reserved-yellow-05 proposal has 301 pixels versus R291 A's 781;
photographic separation, not area reduction, motivates the change. Fresh-red-01,
reserved-yellow-03 and reserved-red-03 also lose large neighboring extensions and
are included for human assessment. Some removals may still truncate target material.
N11 loses a small upper extension and remains unresolved, not a certified correction.

**Remaining failures are explicit.** Red-multiple-1 still joins the upper red region
around an unresolved end despite zero direct crossings. Development-red-06 expands
from 1409 to 1564 pixels: a visible regression in neighboring extension that passed
the local continuation evidence test. Reserved-red-01 and reserved-red-06 retain
paired-bank connections. Fresh-unknown-02 remains a large false paper-associated
region (15340 pixels) reaching the analysis cap; the algorithm does not reject it
on geometric grounds or pretend the frame is an observed edge. These are algorithmic
and ownership failures, not established photographic insufficiency.

Frozen holdout-red-01/02/04 and holdout-yellow-01 retain mergers/background borrowing;
holdout-yellow-04 has no tracked separator and still joins neighboring material.
Holdout-yellow-02 may truncate the visible yellow surface despite high stability.
Holdout-yellow-03 looks more target-focused but is not human-verified. Holdout-red-03
and holdout-unknown-01 outline reflections with min IoU .625/.217, respectively;
their dark-body extents remain unknown. No holdout repair was made.

## Review, reproducibility and stopping point

Start Here: reserved-yellow-05; fresh-red-01; reserved-yellow-03; reserved-red-03;
holdout-red-02; holdout-yellow-01; holdout-red-01; holdout-unknown-01;
development-red-06; red-multiple-1; reserved-red-01. Selection ranks diagnostic
crossing repairs, residual bank connections and instability, includes one expanded
existing merger and a difficult reflection, and excludes unchanged accepted
references. It is a review sample, not an unbiased accuracy estimate.

[Start Here photographic comparisons](r292/results/start-comparison-01.png),
[second sheet](r292/results/start-comparison-02.png),
[third sheet](r292/results/start-comparison-03.png). All 77 original native crops and
automatic A/B proposals remain available. Historical feedback is preserved; R292
feedback has separate hashes, exact displayed contour/separator provenance and full
revision history. No tracing or manual segmentation is required.

Validation: 13 focused real-photo contracts; all 77 native crops match the original;
both result collections replay byte-for-byte and all 77 replay PNGs match;
11698 historical photographic/scientific files and 29 feedback files remain unchanged.
Actual Chromium checks cover all 77 cases, the 11-case playlist, separate separator
view, raw image, zoom/pan, six answers, optional diagnostics, ownership reuse,
revision/undo/export/reopen, preserved judgments and desktop/narrow layouts. Receipts
are under `r292/results/`; see [reproduction instructions](R292_REPRODUCE.md).

Technical preparation failures are recorded separately from scientific outcomes:
packaging initially assumed every case had a non-null R291 comparison, which is
false for new holdouts. The subsequent coverage command correctly failed because
packaging had not produced its input. Presentation-only handling was corrected;
no frozen inference source or outcome changed.

No synthetic images, renderer, Phase 2/3 fitting, indexing or production adoption.
Commit/push verification is recorded separately. **Stop for user evaluation; no R293.**
