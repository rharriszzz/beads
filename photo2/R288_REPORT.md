# R288 — understand J/M and repair a demonstrated merging defect

**W, the evidence-required watershed, is the strongest R288 direction for review.**
It removes a specific source of abrupt merging while retaining broad diffuse red
interiors. Its benefit repeats on new central regions. It does **not** resolve all
photographic ownership, remove N11's questionable upper extension, or make the
five-way selector reliable enough for production. All failures remain visible.

The equally important first deliverable is
[**J_AND_M_EXPLAINED.md**](J_AND_M_EXPLAINED.md), approximately 2,700 words covering
mathematics, actual functions, parameters, comparison, failures and limitations.
It was completed and hash-recorded before new segmentation code. Start the
[compact photographic review](review/r288/index.html) with N07/N11, the causal
interface diagnostic, N06, and independent Q06/Q14. No production inventory,
physical reconstruction, pattern or historical experiment was replaced.

## Explanation and preserved scientific decisions

J uses a local peak-relative isophote and an inherited A-support background ring.
M uses diffuse pigment intensity, context-supported maxima, watershed basins and
maximum-saddle merging. The explanation distinguishes measured pixels from imposed
priors, gives equations and a numerical bright-detour example, and explains why
an image feature or basin is not a certified physical bead. It attributes B's
shallow-shading failure to B rather than inaccurately declaring it an M failure.

Latest user decisions remain authoritative: P5 J/B good, S bad; P2 J too small,
S/B equally good; C05 S/M/B acceptable but imperfect; C02 all bad and not worth
substantial peripheral rescue. M and B match the five original colored cases but
differ elsewhere. Narrow material is not removed merely for shape. Black remains
reflection-only R2 with R1/R4 alternatives; no black-body inference or new redesign.

## What caused the N07/N11 instability

[The detailed diagnosis](R288_DIAGNOSIS.md) and original-M replay show a discrete
logic failure: **fewer than three interface pixel pairs defaults to merging**.
A very dark two-pair connector therefore permits joining surfaces that would be
separated if one more dark pair existed.

|Case|Observed change|Demonstrated mechanism|
|---|---|---|
|N07|M515 → 1325 under background-low|A newly eligible two-pair connection has maximum saddle/reference .1665, yet the minimum-three rule merges it; the upper group joins transitively|
|N11|M694 → 2018 under background-high|Raising the threshold reduces an existing three-pair interface to two; ratio remains .2417, all pairs dark, but separation becomes false|
|N06|Nominal M1148 merges yellows|The target/neighbor interface has two pairs and ratio .1974; a perturbation producing three pairs separates it|

N11's nine markers remain present. N07's target persists; additional eligibility
and unions explain its expansion. These particular failures are not established
missing-marker defects like the earlier P5/S failure. The darker diffuse target
material remains useful even when an alternative parameter setting admits a neighbor.

N11's **nominal upper extension is a separate unresolved issue**. Its top 24 native
support pixels have median Y .0549, hue about 6 degrees and high saturation. They
shift toward yellow relative to central red but still pass the learned red gate.
Twenty-one survive at least 85% of the original perturbations. Direct continuity
also supports most of the extension. Stability therefore cannot establish ownership,
and removal based only on thinness or a prettier contour would not be justified.

## Three targeted alternatives

|Method|Construction and rationale|Observed limitation|
|---|---|---|
|E — ensemble-supported interior|Five original-M estimates: baseline, sigma±.15 and background±.02 diffuse. A connected 4/5-frequency core can extend to 3/5-frequency material only through supported direct pigment/intensity routes. No J mask enters construction.|Correlated M failures survive. Nested perturbations still cause large changes in N11/P5; stable questionable material remains.|
|W — evidence-required watershed|Keep M's diffuse field and repaired markers. Merge only with affirmative bright interface evidence; retain dark interfaces regardless of pair count. Coherent central-plus-nearby valleys add persistent cannot-links through later unions.|Missing/ambiguous cues, stable extensions and internal shading can still defeat ownership. A dark short connector is evidence, not a physical identity certificate.|
|H — local chromaticity diagnostic|Learn a diffuse normalized-linear-RGB distribution from nearby pigment; restrict W to its regularized color ellipsoid, with bounded highlight continuation.|Excludes the selected peak in N07/N11, producing empty supports. Reject as a default; no borrowing a nearby component to conceal failure.|

E is a construction from controlled photographic measurements, not a J/M union
or intersection. Its frequency is not an ownership probability. W preserves all
markers/interfaces/union decisions. H's statistical distance is an engineering
criterion, not a calibrated probability; real within-bead color variation violates
its single-distribution assumption.

**The first W version failed a meaningful control.** Four lateral routes were dark
around a genuine narrow bright connection. The first 4-of-5 corridor rule split
both shallow shading and narrow bright material, repeating the concern behind B.
Its source and development outputs are preserved. Before confirmation, W was
revised to require the central route itself to be dark as well as neighboring
routes and consistent valley position. It then preserves these controls while
separating a deep valley. A bright central bridge through a real seam remains a
possible ambiguity; this revision is not a universal seam detector.

All six perturbation families are recomputed for every candidate: gain, contrast,
smoothing, background, seed and domain. E's five inner estimates are rebuilt for
each of the 14 outer perturbations. HSV/paper/palette/initial A remain fixed, so
these are conditional sensitivity tests rather than physical relighting. Native
supports and contours are separately stored. No compactness or area reward is used;
the inherited 12–870-pixel guard remains a diagnostic eligibility bound.

## Development results and what did not improve

|Anchor|J|M|E|W|H|Minimum perturbation IoU, M → W|
|---|---:|---:|---:|---:|---:|---|
|N07|288|515|515|515|0|.389 → .968|
|N11|167|694|694|694|0|.333 → .952|
|N06|457|1148|576|576|573|.497 → .986|
|P2|200|495|495|495|495|.947 → .947|
|P5|511|664|664|664|660|.507 → .979|
|C05|248|527|527|527|523|.944 → .944|

For N07, W retains the good fuller measurement instead of returning the undersized
J mask. N11's large perturbation mergers are removed, **but its nominal upper
extension remains exactly unchanged**. Do not call that extension corrected.
N06 loses the neighboring yellow contribution. P2/P5/C05 preserve their useful
nominal M masks. The recorded outcome “new interior W” describes a newly supported
construction, not necessarily a different nominal pixel set: W=M exactly on five
of these six anchors.

E fails under nested perturbations despite matching good nominal masks: N11 minimum
IoU .437 and P5 .524. H's empty red outputs are an independent failed alternative.
These failures remain in the comparison and are not hidden behind the selected W.

The five-way interpreter permits J, M, both, a new E/W construction, or abstention.
It records supported diffuse material outside J separately from M's instability,
and never unions retained alternatives. H is diagnostic only. On 21 development
cues it gives 7 new constructions, 8 M, 4 J, 1 both and 1 abstention. That success
on development did not justify assuming the interpreter was reliable elsewhere.

## Independent confirmation: 15 new regions, 69 cues

Selection was frozen before new outputs: eight crossing anchors, four same-color
neighbor anchors, one opposite-side anchor and two additional near anchors. One
red-flanking stratum had no eligible spatially independent cue; no rules were relaxed.
Anchors are hash-ranked high-source photographic candidates, with native median
exposure >.025, support-near geometry, centers >100 pixels from prior reviewed
centers and >80 pixels from one another. All colored cues within 36 pixels remain,
including uncertain/rejected sources. Center separation does not imply every
context pixel is disjoint. Sources/parameters were frozen before confirmation.
**No confirmation retuning occurred.**

Strong evidence beyond development:

- **Q06:** M1151 visibly joins two yellows; W588 retains the target. Its neighboring
  proposal also changes M1123 → W548. This is not just repeating the old P5 crop.
- **Q01 high red neighbor:** M1181 → W593 removes an upper neighboring red. Another
  yellow cue changes M743 → W491, separating its lower neighbor.
- **Q04/Q09 red neighbors:** M1368 → W587 and M1026 → W553 remove visible mergers.
- **Q03/Q05/Q07/Q09/Q11 anchors:** broad diffuse red measurements remain. Q08/Q10
  preserve smaller M/W interiors where J includes neighboring yellow material.

Failures and uncertainty are decisive too:

- **Q14:** J123 is again selected over fuller M/W515. A +10% contrast perturbation
  makes W1321, so all fuller candidates fail stability checks. All 392 M-only pixels
  pass direct continuation, but the adequacy rule only counts that evidence when a
  new candidate passes its stability checks. Thus the intended independent J defect
  is still partly coupled to candidate validity. This is the R287 fallback problem
  recurring under a new condition. It must remain visible, not be patched on this set.
- **N11:** the original upper extension remains; photographic ownership is unresolved.
- **Q01 rejected cue:** the interpreter still prefers M644 on tinted dark/reflection
  material, despite an implausible colored support. Q04/Q09 also retain tiny red
  interpretations of apparent dark-bead reflections. These are upstream cue/color
  and ownership failures that the basin repair does not fix.
- **Q15 high-source yellow:** a plausible nominal 426-pixel support still abstains.
  Source-high status does not override uncertainty; useful measurements can be lost.
- Q01's anchor retains a small side extension. W is not a general tail-removal rule.

The images and complete cue atlases show these cases. Visual judgments are review
evidence, not an independently calibrated accuracy dataset.

## Quantitative evidence and centerline accounting

|All 69 confirmation cues|J|M|B|E|W|H|
|---|---:|---:|---:|---:|---:|---:|
|Nonempty within operational bounds|67|64|65|66|69|61|
|Detected coherent-seam conflicts|8|6|5|4|0|0|
|Minimum perturbation IoU <.70|10|20|14|16|6|17|
|Domain IoU <.90|17|7|5|6|3|8|
|Mean minimum perturbation IoU|.842|.785|.842|.815|.891|.745|

H's empty masks count as failed stability comparisons, not as successful empty
predictions. All nonempty native supports are connected. W has three window-contact
proposals despite staying within the area ceiling. Zero detected seam conflicts
means zero by the saved image-based proxy, not verified zero leakage. The proxy
shares image evidence with the new method and is not independent ownership truth.

All M/W baseline marker ledgers are identical. Thirteen M proposals contain
multiple merged marker labels, versus four W proposals. Seventeen windows contain
short dark interfaces. Across repeated windows the ledger records 1,519 maximum
entries, five context projections and 887 unsupported entries; these are processing
events, not unique markers or missing beads. Unsupported maxima often represent
other material. True missing/redundant body markers and false partitions cannot be
counted without independent ownership truth; overlap and the preserved shading
controls provide diagnostics instead. See `marker-audit.json`.

W retains 12,500/13,606 (91.9%) of the fixed R287 direct-route-supported M-only
pigment proxy. E retains 98.6%, H67.2%. Maximizing that retention would favor E even
when it retains neighbors: some removed proxy pixels belong to the merger regions.
These are measured photographic continuations, not labeled true-body material.
W's mean centroid displacement from M is 1.63 pixels across all cues; large
corrections can reflect removal of a neighbor rather than worse localization.

|Confirmation coverage|J|M|W|R287 selector|R288 interpreter|
|---|---:|---:|---:|---:|---:|
|Retained observations|69|69|69|58|62|
|Support-near|45|45|45|44|45|
|Measured support-crossings|22|26|24|23|24|
|Near overlap groups, IoU≥.5|45|44|45|44|45|
|Overlapping pairs|12|6|4|3|3|
|Near-duplicate pairs|0|2|1|1|1|
|Opposite-side flanking pairs|6|1|2|2|2|

Raw-method columns include defective proposals; interpreter columns exclude
abstentions. Both counts one observation with separate alternatives, requiring
agreement for robust near/crossing geometry. Signed support extents and arc
intervals determine coverage, not just nearest centroids. Groups and flanking
pairs are photographic diagnostics, not verified distinct bodies.

The two M→W crossing losses occur in Q04/Q06 merger corrections. They are not
proof that real crossing beads vanished, nor proof that W now covers every one.
The new interpreter retains one more near/crossing observation than R287 on this
same set, but still makes poor choices on weak cues and Q14. It returns 18 new
constructions, 39 M, 3 both, 2 J and 7 abstentions. No new cue detector ran:
**zero new distinct physical beads are certified; real precision/recall and complete
centerline recovery remain unknown.**

## Reproducibility, preservation and recommendation

[Reproduction and evidence map](R288_REPRODUCE.md), [specification](R288_SPECIFICATION.md),
[checklist](R288_CHECKLIST.md) and six checkpoints preserve the chronology. Original
J/M/B controls replay exactly on all 21 development cues. The failed first W rule
and E/H failures remain. Black R2/R1/R4 data are hash-preserved, not re-estimated;
the cited 144 reflection replays belong to the earlier R286 experiment.

128 scientific tests pass (20 new plus 108 historical), including dark-versus-shallow
controls, preserved false splits, explanation-before-code evidence, frozen selection,
full perturbations, native connectedness, schema/unknown physical identity and
alternative-mask handling. Both independent rerun files match exactly. All 10,672 historical scientific blobs
and 45 native crops pass preservation checks. Chromium passes 79 images, 25 tables,
27 sections and 129 local links in desktop/narrow views; receipts are saved alongside
the data. Only the explicitly updated permanent
Phase 1 specification is excepted from historical scientific-file preservation.

**Recommend W's affirmative-merge and short-dark-interface repair for user review.**
It has a causal explanation, retains diffuse material and repeats useful separation
on new photographs. Do not adopt E, H or the five-way interpreter as a production
default. W itself still needs ownership evaluation, especially weak color cues,
internal texture and stable extensions. No complete inventory is replaced.

After user review, the next bounded proposal is to keep the seam/union repair fixed
and test independent adequacy/feature-quality evidence: J's discarded diffuse
material must stay recorded even when every fuller mask is unstable, and a tinted
reflection must not gain colored-body credibility from a stable watershed. N11's
extension should remain a competing photographic explanation until local evidence
supports a decision. This is a proposal, not an automatic next round.

STOP for review. No R289, global physical fit or pattern search. Keep the current
model/reasoning; no `/new` needed.
