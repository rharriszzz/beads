# R326 — iterative photographic feedback, compatible hypotheses, unresolved truth

**R326 implements genuine iterative reconstruction and repairs a demonstrated hypothesis-compatibility defect. It does not demonstrate more accurate whole-bracelet indexing.** Three refinement passes change the selected hypotheses and connections, including three links involving a new **provisional** native reflection. The final candidate has **937 original observations plus one provisional site, 892 conditionally indexed sites, 1,833 links and three components**. Of those indexed sites, **891 are original observations**, compared with 895 in R325.

The historical **174 contested links remain photographically unresolved**. R161 remains **25/25 interior associations, 45/45 interior links, zero wrong links;33/40 and 65/86 overall**. No count, physical reconstruction or color pattern is adopted.

[Four original-pixel comparisons](r326/results/index.html) · [Reproduce](R326_REPRODUCE.md) · [Full candidate](r326/results/full/graph.json) · [Strict model input and alternatives](r326/results/model-input.json) · [Verification](r326/results/verification.json).

## What changed, and what did not

R325 selected a cyclic solution before its changed-window stress test. That test neither generated new candidates nor changed the objective. Its graph builder also pooled max-marginal states from different complete paths. R326 measures changed sizes and offsets **before subsequent selections**, transports their fits into affected original windows, retains every old candidate, applies bounded context and longer-range penalties, and reoptimizes all 187 windows.

The initial diagnostic found 46 mutually inconsistent overlapping pairs among R325's selected whole-window hypotheses. **All 1,826 accepted R325 links individually have support in its selected cyclic path; zero are merely marginal-only links.** Thus marginal pooling alone is not the demonstrated failure. The stronger [feasibility audit](r326/results/r325-union-feasibility.json), using all 1,603 original candidates, proves that their complete 1,826-link union cannot coexist under whole-hypothesis compatibility—even allowing window abstention and requiring only one supporting window per link. The two-window version is also infeasible. This is a finite-bank representation result, not photographic ground truth.

R326 retains the exact R325 cyclic solver as a proposal and comparison baseline. A sparse binary optimization then jointly reconsiders **every retained candidate**, with at most one whole hypothesis per window, hard translation compatibility for **all shared observations**, and additional cycle cuts when required. Entire windows may abstain; assignments inside a chosen hypothesis are never trimmed to conceal a contradiction. All accepted links have one simultaneous whole-hypothesis witness and retain the original two-window, foreground and intervening-observation gates. There are no permanent geographic charts.

The binary objective sums `20 − cyclic max-marginal regret` for selected states; abstention contributes zero. Context disagreement contributes up to four unary units, and frozen-neighbor longer-range disagreement up to two. Correlated sizes are grouped by parent region; repeated windows are not counted as independent confirmation. These are explicit heuristic weights, not calibrated probabilities. The binary objective is a **surrogate**, not the original cyclic objective or an exact solution over all photographic lattices. Each delivered primary binary solve reports optimality for its represented surrogate. The final witness uses 179 whole windows and abstains on eight.

The original 1,603 hypotheses remain unchanged as a prefix; selective additions yield 3,352 hypotheses/55,289 assignments. The 778 changed contexts cover sizes 160/240/280px and tangent offsets±18px. They use local affine fits; no nonlinear bend model or measured full bead contours were established. Repeated context fits are cached. A finite expansion limit of four/four/two additional candidates per affected window remains a limitation.

## Practice and full-circuit iterations

Practice used the same 146 original lower-bend observations and windows 65–93 as R325, with 43 red, 56 yellow and 47 black supports. The R325 comparison uses exactly the same cached measurement/candidate bank, without loading maker answers.

| Practice stage | Indexed | Links | Components |
|---|---:|---:|---:|
| R325 one-pass, same bank |134|261|2|
| R326 initial compatible selection |135|269|2|
| After refinement 1 |135|269|2|
| After refinement 2 |135|269|2|
| After refinement 3 |133|264|2|

Two fresh context/refinement reruns take **16.428 and 16.439s**, with exactly equal scientific outputs. Original image measurements/candidates are cached in this practice timing; new contexts and fits are fresh. There is **no independent accuracy denominator** here. The final pass withdraws five links and loses two indexed sites relative to its initial selection. This is not advertised as an accuracy gain. Synthetic contracts separately verify that a conflicting distant-window choice can be reconsidered, rather than merely filtered after selection.

| Full-circuit stage | Total observed / provisional | Indexed | Links | Components | Compatible windows |
|---|---:|---:|---:|---:|---:|
| Exact fresh R325 baseline |937 /0|895|1,826|1|—|
| R326 initial |937 /0|888|1,825|2|177|
| Refinement 1 |938 /1|891|1,832|2|178|
| Refinement 2 |938 /1|891|1,832|2|178|
| Refinement 3 |938 /1|892|1,833|3|179|

All 187 original windows and all 16 geographical sections remain processed. Original observation IDs, locations, colors and pixels are unchanged. Conditional original-site coverage decreases by four relative to R325. There are 26 added and 19 removed links relative to R325; these counts include the representation change and provisional evidence, not just photographic corrections.

Three concrete feedback examples appear in the small review:

* Upper bridge: a 160px context at window 15 generates the candidate selected at window 13; two links involving `C-1659-0261` become eligible in pass 1.
* Inward bend: further context-derived candidates change the selected configuration in pass 3. Two previously selected links through `K-1740-1575` are withdrawn and neighboring links change. The new selected window 121 hypothesis comes from context`118-240-0`. Photographic disagreement remains.
* Faint black site: admitting an explicitly provisional native support changes the next global configuration and introduces three provisional links. A same-bank ablation masking every state that uses the new site removes exactly those three links.

A necessary negative control: **removing only the context unary penalties on the same expanded bank changes zero accepted links in all three passes**. Therefore the observed link changes cannot be credited to those penalties. Candidate generation from new photographs' contexts, whole-hypothesis compatibility and provisional evidence do affect decisions. The method is iterative, but stronger use of context evidence is still needed.

The run stops at its declared **three-pass computational allowance**. New choices still appear in pass 3; neither convergence nor candidate/evidence exhaustion is claimed. Original candidates are never pruned between passes.

## Candidate recall and R161

[Retrospective candidate audit](r326/results/candidate-recall.json) associates the original measured observations to R161 before testing candidate recall. Both R325 and R326 have 33 unambiguous associations under the fixed 18px/3px rule. **All 65 recorded links with associated endpoints, including all 45 interior links, occur in the candidate bank and in the final accepted graph.** The other 21 recorded links lack an associated photographic endpoint under that rule; this is not evidence that a correct represented row was discarded.

There are **zero available-but-unselected recorded links**, zero demonstrated graph-construction errors against R161, and zero wrong automatic reference links. Joint local recall, partial hypotheses and all per-link witnesses are exported. This is historical evaluation with known development history, not a new independent holdout. R161 labels and all 3D/pattern data are blocked from detector runtime.

## The 174 historical disagreements and broader screening

Under a strict definition requiring reconciliation of the archived counterevidence:

| Fixed historical 174-link outcome | Count |
|---|---:|
| Resolved in favor of the original |0|
| Resolved in favor of another relation |0|
| Still ambiguous |174|
| Rejected with evidence establishing neither interpretation |0|

Original and revised hypotheses are retained in [the fixed diagnostic](r326/results/historical-contested.json). No 174-link error rate is asserted. Outside the old stress-test set, the new candidate has **17 consistently supported, 1,175 ambiguous and 127 contested links** under the broader contexts. Those contexts are correlated, and local alternatives are not truth.

Across the entire final graph, the new context classification is **17 consistent, 1,441 ambiguous, 375 contested**, with no untested accepted links. A stringent fixed-correspondence interface excludes ambiguity as well as contradiction: **17 links, 30 indexed observations, 13 components, 908 unresolved sites**. Applying exactly the same new contexts and screening rule to R325 yields **the same 17 links/30 observations/13 components**. This prevents presenting a stricter mask as an inference improvement. R325's older 1,652-link/23-component interface used a smaller stress set and retained context ambiguity; it is not an equal-rule comparison.

Thus **reliable global photographic indexing has not been demonstrated to improve**. The improvement is logical compatibility and traceable reconsideration. Broader evidence exposes how little is suitable for fixed downstream correspondences under a stringent criterion. No newly incorrect outside-reference photographic connection is established without labels.

## Black beads and approximate regions

The same local geometry is used for all colors. A lightweight covariance ellipse estimates a **partially visible pigment-region envelope** from neighboring colored pixels, with local axes and variable projected dimensions. Reflection-to-center uncertainty is modeled separately; the ellipse is not a measured complete contour or a smaller black-bead shape. This proxy has **no demonstrated independent accuracy benefit** and remains exploratory.

Thirteen fresh colored-only changed-context predictions corroborate the faint site at approximately`(290.374,1410.186)`. Its 22 original pixels, three distinct colored anchors and five overlapping parent windows justify an **explicit provisional hypothesis**, not an independent new-bead detection. Original no-addition candidates remain in competition. The second 18-pixel faint site near`(2158.153,894.077)` does not meet the admission rule in the first refinement and stays unconfirmed.

The admitted site's alternatives include a separate black bead, a second reflection on an already observed bead, or glare. It is indexed conditionally and gains three links; every such link is excluded from fixed model correspondences. **Existing indexed black observations remain 308, unchanged from R325; independently confirmed new beads remain zero.** Native provenance and the no-provisional-state ablation are in [black evidence](r326/results/full/black-evidence.json).

## Closure, model interface and pattern

All four historical lower-bend endpoint pairs become **accepted conditionally** in the selected candidate, but all remain context-contested and are excluded from strict constraints. Other gaps prevent a nonzero winding cycle in the accepted two-window link graph. Closing that local gap did not establish the bracelet sequence.

The complete whole-hypothesis configurations themselves propose conditional winding: passes 1–2 give`H=(213,201)` and pass 3 gives`(214,201)`, corresponding to A/B counts 2697/2685 and 2704/2691. Eight explicit compatible alternative witnesses yield other offsets or leave winding unidentified. They therefore **weaken any uniqueness claim**. The old count alternatives remain archived; no N2800/N3000 or other count was imposed or adopted. Missing evidence is a uniquely supported lower-bend row continuation **and** sufficiently supported intervening relationships around the rest of the circuit.

[Model input](r326/results/model-input.json) includes original IDs/pixels, colors, component-relative A/B indices and both reversals, neighbor deltas, context status, unresolved edges, provisional provenance and eight explicit compatible alternatives. Four links occur only in these sampled compatible alternatives; seven additional marginal-union links remain without a sampled compatible witness. This is not proof they are impossible. Alternatives are never unioned into the primary graph.

No material improvement in reliable global indexing was established, so the conditional request for a new frozen-R321 comparison was not triggered. No 3D fit was run. A bounded exact-repeat diagnostic on the strict component gauges is very weak:492 of 500 periods have no within-component comparisons in each map. Apparent survivors are not pattern candidates. Complete repetitions and the historical nonmultiple-of 13 restriction remain; no cross-component origin or unknown colors are manufactured. The principal obstacle remains uncertain bead/row identity, followed by color ownership and missing global winding—not evidence that the true period exceeds 500.

## Timing, verification and preservation

The first uncached-context prototype took 121.752s. The cached/provisional run took 101.502s; the delivered sign-corrected exact replay took **106.356s including serialization**, with **1,201.1MiB peak RSS**. This includes fresh R325 image analysis and all three refinement passes, not just solving a saved bank.

| Delivered stage | Seconds |
|---|---:|
| Fresh exact R325 baseline, including serialization |15.138|
| Additional preprocessing for refinement |1.574|
| Refinement 1, including causal control |21.497|
| Refinement 2, including causal control |37.613|
| Refinement 3, including causal control |20.028|
| No-provisional-state ablation |about 3.5|
| Remaining graph/export bookkeeping and serialization |included in total|
| **Complete core run** |**106.356**|

Within the passes, photographic disagreement measurements take 35.833s; selective candidate generation 22.093s; context/long-range feedback 6.785s; cyclic optimization 5.265s; compatible graph/audit 1.791s; same-bank context ablations 7.155s. Stage details, including new black evidence, are in the iteration receipts. Cached fits are reused rather than regenerated. The additional eight explicit alternative witnesses cost 34.736s, making core plus that diagnostic approximately **141.1s**. Independent validation is separate:109.386s, including a 108.044s guarded fresh replay. No parallel-speedup or convergence-runtime claim is made.

Verification checks 938 supports/21,203 native pixels, all 3,352 hypotheses/55,289 assignments, every 1,833 accepted edge, 3,117 whole-hypothesis equations and 529 overlapping selected-window pairs. Independent least-squares equation residual is below 1.44e−9. It independently checks the context fits, eight alternative path scores/compatibility, both index maps, provisional exclusion, native crops, and exact repeated practice. The guarded detector reads **only** the original JPEG, R275 appearance inventory and geographic spline seed. Its fresh R325 baseline exactly reproduces the archived R325 science.

A verification failure caught a sign-convention error in **diagnostic window-offset holonomy metadata**. The sign was corrected; all hypotheses, scores, selections, links and indices are exactly unchanged. Earlier artifacts and the failed receipt are preserved, and the full guarded verification passes afterward. Five new contracts cover distant-window reconsideration, exhaustive surrogate selection, incompatible pooling, winding cycles and correlated-context duplication.

All 47,122 prior tracked files other than the additive AGENTS handoff are unchanged; the old AGENTS content is preserved byte-for-byte as a suffix. This includes the original photograph, R161, R319–R325 and `beads.pov`. Initial scientific selections were sealed before retrospective R161 scoring; only the documented sign correction and bounded diagnostic witnesses followed. Documentation, independent verification and delivery use the reserved portion of the 40-minute allowance. [Delivery receipt](r326/results/delivery.json) records commit and remote verification.

**STOP for scientific review. No automatic R327, pattern adoption or physical fitting.**
