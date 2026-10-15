# R291 completed human review — findings and proposed R292

The user accepts a proposal in 13 of the 14 reviewed Start Here examples. R291
has made useful progress, particularly in avoiding neighboring material. Its
clearest remaining failure is inadequate enforcement of photographic separators,
not a demonstrated general lack of information in the photograph.

This document records analysis only. **R292 is proposed, not approved or
implemented. Stop for user approval.** Detector sources, parameters, scientific
results, production methods and the live review ledger remain unchanged.

## Review evidence and limits

The completed ledger contains 15 events for 14 cases. Q14 was revised from A to B;
the final revision is used below. Final answers are 11 A, two B, and one
wrong-clear. There are no partial, insufficient-photograph or not-sure answers.
All optional diagnostic and pair-ownership fields are empty. Causal explanations
below therefore distinguish the user's verdict from implementation inspection and
our interpretation of the actual photograph.

The original append-only ledger, including every revision and displayed candidate,
is preserved byte-exact after decompression in
[completed-review-2026-10-15.jsonl.gz](r291/evidence/completed-review-2026-10-15.jsonl.gz).
Its uncompressed SHA-256 is
`0634abdece7e50809ce677de2ff564d3251172d2fc5646bcb1eb89fd6712f4b9`.
[completed-review-analysis.json](r291/evidence/completed-review-analysis.json)
records final answers, native coordinates, feature IDs, immutable candidate/crop
hashes, original-image hash, revisions, candidate sizes and diagnostic metrics.
The 14 snapshot JSONs and PNGs equal the already tracked review-package files
byte-for-byte; those paths are recorded instead of duplicating the snapshots.
The live `r291/feedback/` directory remains untouched and separate from this archive.

All 14 cropped pixel arrays were checked against the original EXIF-oriented
`beads-photo-2.jpg`, hash
`eb7c9edb62f5580ef56632872da48da92556d62b758295137068cc2404dc8fbb`.
All immutable candidate digests, crop hashes and displayed-candidate contents
match the feedback events. No new inference or synthetic evaluation was run.

| Case | Native target (x,y) | Final answer | R290 pixels | R291 A / B pixels |
|---|---|---|---:|---:|
| Q14 | 449,731 | B, revised from A | 191 | 295 / 314 |
| P3 | 1362,2969 | A | 479 | 444 / — |
| reserved-yellow-01 | 1879,2795 | A | 1542 | 469 / — |
| fresh-yellow-02 | 1408,1447 | A | — | 415 / — |
| reserved-yellow-04 | 2154,2545 | A | 715 | 417 / — |
| red-worst | 1288,2129 | A | 481 | 390 / 642 |
| reserved-yellow-05 | 1759,1886 | Wrong despite clear photograph | 1726 | 781 / 1019 |
| P2 | 1235,312 | A | 764 | 495 / — |
| N06 | 1452,2043 | A | 3458 | 388 / — |
| yellow-multiple-2 | 1032,2748 | A | 2856 | 415 / — |
| development-yellow-03 | 349,860 | B | 654 | 394 / 408 |
| development-yellow-05 | 906,2545 | A | 618 | 373 / — |
| fresh-unknown-01 | 2140,878 | A | — | 88 / — |
| diagnostic-02 | 1018,393 | A | 54 | 40 / — |

Pixel counts identify the candidates and changes; size is not a correctness
criterion. A B preference does not itself establish that A is substantially wrong.
The selected Start Here sample is not an unbiased accuracy sample for all 68
cases. Fifty-four cases remain unreviewed. There are no paired human correctness
scores for R290, exact reference contours, centroid truth or new explicit
same/different-bead answers. Existing red-worst same-physical-bead evidence remains
valid and evaluation-only; centroid disagreement never establishes different beads.

## Successful mechanisms and combinations

**Coherent darkness plus multiscale edges** supports the accepted N06 and
yellow-multiple-2 proposals. Their R290 overlays spread extensively into nearby
beads. R291 retains a target-focused region instead. This is the strongest evidence
of useful separation progress. The extra highlight still inside yellow-multiple-2
is not, by itself, an ownership error or a new explicit pair-ownership judgment.

**Multiscale illumination edges plus material transitions** work together in
accepted P3, reserved-yellow-01, reserved-yellow-04, fresh-yellow-02 and
development-yellow-05. Different portions receive different evidence. The result
supports complementary local measurements rather than demanding darkness around
every side or choosing among unrelated whole-mask algorithms.

**Diffuse-material continuity combined with darkness constraints** supports the
accepted red P2 and red-worst proposals. R291 avoids neighboring extensions in
the R290 overlays while retaining useful target material. These acceptances are
especially valuable because the automatic support scores remain low.

**Softer treatment of dark interruptions** produces the preferred B for Q14 and
development-yellow-03. B adds only 19 and 14 pixels respectively. This is consistent
with recovering material interrupted by internal shading, but is not an isolated
causal test: B changes both direct-stop penalty and competing-point strength.

**Reflection-edge measurements** yield accepted A in fresh-unknown-01 and
diagnostic-02. Preserve those user verdicts. The saved regions outline illuminated
reflections; their acceptance does not establish surrounding dark-body silhouettes
or physical centers, in accordance with the existing Phase 1 black contract.

These are successful combined outputs, not proof that every contributing method
is necessary. No controlled ablation isolates each mechanism. The junction and
termination fields in method E annotate context but do not constrain the current
optimization. Success near an occlusion cannot be attributed to E solving it.

## General failure mechanisms

### Excluding another bright point does not enforce the measured separator

The clearest demonstrated failure is reserved-yellow-05. The user rejects A and B
while calling the photograph clear. A excludes the two protected neighboring
feature centers, yet its extension reaches neighboring yellow material.

The saved separator toward H-1727-1875 at (1727,1875) is already marked supported.
Its five dark trough/reference ratios are approximately .129, .211, .336, .404
and .354, with aligned positions. Convert the saved local trough coordinates by
adding the candidate box origin, then test their nearest native pixel against A:
three of the five are inside the mask. The bypass diagnostic nevertheless reports
none. It checks the competing feature's center, not separator crossing. The current
regression test also only checks exclusion of that center.

This is an algorithmic failure despite useful photographic measurement. A bright
detour can still admit material around a point constraint. The remedy should use
the actual supported seam and its context, not add more special thresholds or
draw an assumed straight barrier through sampled minima.

### Internal darkness and external separation remain confounded

The two preferred B proposals favor modest continuation beyond the stricter A.
Conversely, globally preferring B enlarges the rejected yellow merger and extends
red-worst beyond its accepted A. A global dark-stop relaxation cannot resolve both.

The missing distinction is contextual: does the interruption belong to an internal
shadow/hole, or does a coherent edge continue as the target's external boundary?
Straight source-relative access alone cannot establish that distinction. The two
parameter changes bundled into B must be isolated before attributing its successes.

### Material similarity is mistaken for target ownership

The saved, unreviewed red-multiple-1, development-red-06 and development-yellow-07
overlays show new neighboring connections compared with R290. These are photographic
assessments from this analysis, not additional human labels. Matching hue and
brightness can support continued material without establishing one physical bead.

Tinted reflections and paper expose the same weakness more severely: fresh-red-01
borrows nearby red material, and fresh-unknown-02 expands into paper. Source-local
material inference and ownership must remain distinct. Large area is a symptom,
not grounds to reject photographed objects as geometrically implausible.

### Support, stability and correctness are different quantities

Accepted P2 has only 28% supported sides and accepted red-worst 44%. Rejected
reserved-yellow-05 scores 62% for A and 81% for B. All primary statuses remain
partial/unresolved despite the accepted examples. Lowering a support threshold
would promote failures as well as successes.

Accepted diagnostic-02 has nominally 100% supported sides but minimum perturbation
IoU .455: its +15% unary-weight solve changes substantially. Its displayed boundary
can be good while measurement robustness remains poor. Conversely, known mergers
can be stable. Neither stability nor support is calibrated correctness.

## R291 versus R290 and photographic sufficiency

The strongest improvements combine actual overlay changes with acceptance of the
new proposal: N06 and yellow-multiple-2 avoid extensive mergers; reserved-yellow-01
and reserved-yellow-04 reduce neighboring extensions/tails; P2 and red-worst yield
accepted target contours; Q14's preferred B recovers diffuse material omitted by
R290. The user did not separately score the old contours, so this is not a measured
round-to-round accuracy difference.

Unreviewed red-multiple-1 and development-red-06 remain important regressions, and
development-yellow-07 gains neighboring material. P5, N07 and N11 become more
conservative, but their removed pixels cannot be counted as confirmed corrections;
target truncation remains possible. Retain those unresolved comparisons.

No reviewed case establishes genuinely insufficient photographic evidence. The one
explicit failure is wrong-clear. The accepted dark cases support useful reflection
measurements while leaving full bead extents unestablished. Keep algorithm failure,
insufficient measurement and unavailable full silhouettes distinct. Do not infer
photographic insufficiency merely because an optimizer or local test fails.

## Proposed focused R292 — requires approval

Test one improvement to the existing framework: **make coherent separator arcs
constrain the target region while distinguishing them from internal shading.**

1. Keep R291's complementary measurements. Follow dark/multiscale edges along
   their actual photographic paths, using material transitions and junction context
   where informative. Do not substitute straight chords or shape assumptions.
2. Detect when a region straddles a supported separator or travels around an
   unresolved end. Use context to distinguish external separation from internal
   shadows before imposing strong constraints. Preserve supported partial arcs and
   unresolved ends without inventing closure.
3. Isolate the two changes currently bundled into B. Test local continuation around
   disputed interruptions instead of relaxing darkness and ownership throughout the
   region. Keep accepted P2/red-worst behavior and Q14/development-yellow-03 B as
   opposing regression requirements.
4. Use the 13 accepted proposals as evaluation references and the rejected yellow
   case plus documented mergers as permanent failure categories. Human contour
   acceptance is not exact pixel truth. Case coordinates, IDs and prior verdicts
   must never become runtime rules.
5. Treat exposed R290/R291 cases as development or retrospective evidence. Select
   and freeze new original-photo holdouts before examining their outcomes; freeze
   the method before evaluating them. Run all T1–T8, emphasizing separator integrity,
   internal/external ambiguity, target inclusion/exclusion and sensitivity. No
   synthetic scenes, physical reconstruction, indexing or production adoption.

The experiment should demonstrate fewer separator crossings/neighbor inclusions
without losing accepted target material. Increased area, support, smoothness or fewer
abstentions is not success. Report changed accepted contours as possible regressions
and stop for a small review of changed failures and changed successes. Do not ask
the user to repeat judgments of unchanged candidates.

## Verification of this analysis

Read-only analysis verified 14 immutable candidate digests, 14 crop hashes, 14 exact
original-photo pixel arrays, and byte equality of all 14 packaged candidates/crops
with the feedback snapshots. The archived ledger decompresses to the exact original
bytes. Final-answer counts and per-case metrics can be reproduced by loading its
JSON lines, selecting the last revision for each case, and reading the candidate
paths in completed-review-analysis.json. Native coordinates and hashes are explicit.
No detector, viewer or scientific-output change is included; existing inference and
browser tests were not rerun for this documentation/evidence-only delivery.
