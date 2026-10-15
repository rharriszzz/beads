# R293 analysis of completed R292 judgments

The local feedback is available and complete for all11 Start Here cases:11 events,
all revision1, four A acceptances, three partial judgments and four wrong-clear
judgments. No B, insufficient-photograph or not-sure answers, optional diagnostics
or pair-ownership answers were recorded. Original events, candidate masks/contours,
separator arcs, coordinates, image/crop hashes and prior provenance are preserved
byte-exact after decompression in
[r293/evidence/completed-r292-review.jsonl.gz](r293/evidence/completed-r292-review.jsonl.gz).
[Analysis/provenance](r293/evidence/r292-review-analysis.json) includes full history,
final answers and exact original tracked candidate/crop paths. All11 immutable
snapshots/crops were checked against the package and native original pixels.
The live feedback and every previous experiment remain unchanged.

| Case | Final user answer | Distance to image-derived centerline | Interpretation / priority |
|---|---|---:|---|
| reserved-yellow-05 | A |31.8px|The principal separator repair is accepted; useful nearby evidence|
| fresh-red-01 | A |26.8px|Small illuminated target region accepted; red context does not establish physical red material|
| reserved-yellow-03 | Partial |29.6px|Useful segments, region not fully established; retain independent feature|
| reserved-red-03 | Partial |15.7px|Central partial measurement, not a discarded observation|
| holdout-red-02 | Partial |42.2px|Useful partial context; full peripheral extent deferred|
| holdout-yellow-01 | Wrong-clear |37.8px|Clear-photo neighboring-material failure, not insufficient photograph|
| holdout-red-01 | Wrong-clear |38.6px|Clear-photo background/neighbor inclusion remains|
| holdout-unknown-01 | A |31.6px|Useful reflection region accepted; physical dark-body center remains unknown|
| development-red-06 | Wrong-clear |3.9px|High-priority central failure; must not be hidden by peripheral deferral|
| red-multiple-1 | A |11.1px|Acceptance preserved despite10 paired-bank flags; automatic warning is not ownership truth|
| reserved-red-01 | Wrong-clear |47.3px|Outside primary point reach; retain clear-photo failure, defer whole silhouette|

The optional explanations are empty, so the mechanism descriptions above come from
saved pixels/implementation and are not additional user-supplied labels. The A
judgment concerns the displayed candidate, not an exact pixel truth mask or a
physical identity assignment.

What works: the rejected R291 yellow detour becomes an accepted R292 proposal;
separation plus local evidence can avoid including a neighboring surface. The
fresh-red-01 change also yields an accepted illuminated region. Accepted
holdout-unknown-01 confirms that a useful reflection observation does not require a
dark-body silhouette or stable inferred physical center.

What remains: same-color material/illumination can join adjacent surfaces; tinted
reflection/background ambiguity can corrupt region ownership; eliminating direct
valley crossings does not establish a correct whole region. The partial judgments
credit real photographic evidence rather than declaring a photograph unusable.
Development-red-06 is a clear central counterexample to blanket adequacy.

The previous analyst description of red-multiple-1 as a remaining merger must not
supersede the user's A acceptance. Its10 automatic paired-bank flags are retained as
a contradiction/diagnostic, not promoted to a human rejection or a runtime exception.
Conversely, zero direct crossings in other cases did not prevent partial/wrong
judgments. No boundary counter is calibrated precision.

R291's13/14 accepted proposals and R292's4/11 acceptances have different selected
case populations. R292 deliberately emphasized unresolved repairs and failures and
excluded unchanged accepted cases. The fractions therefore do not establish a drop
in general accuracy. All13 R291 references survive R292's declared tolerance, and
R293 changes none of the77 R292 proposals. No repeated judgments are requested.

Eight of the11 R292 review targets lie outside the26px point-reach convention,
although some visible material may still reach the core band. Their distances to
the photograph border are192–836px. This was largely an arrangement/context-boundary
study, not literal clipping at the photograph border. Neither descriptor establishes
quality: clear nearby observations remain useful; uncertain central ones stay central
gaps. R293 shifts the evaluation denominator to well-observed centerline features.
