# R340 — fixed material darkness with automatic glass regions

[Offline native-pixel review](r340/autoregion/review/index.html) · [Reproduce](R340_REPRODUCE.md) · [Exact evaluation](r340/autoregion/evaluation.json) · [Reversible overlay](r340/autoregion/graph.json.gz)

**The fixed3×3 /73.5 test is useful for interior corrections, but automatic region ownership is not universally reliable.** It passes the original48 references and recognizes54/55 maker-confirmed black beads across113 maker labels. A separate edge-yellow stress case supplies an actual raw shadow false positive. The unchanged edge screen abstains there. No threshold adjustment, classifier voting, average-darkness statistic or reflection analysis was added.

The strict conditional208 block improves **179 supported /21 conflicting /8 insufficient →181 /19 /8**, on identical1040 indexed observations. Your correction resolves196; independent interior evidence resolves86. Position190 improves but remains conflicted. No unknown entry is filled by majority vote.

## One region, one measurement

The only active pigment implementation is [recognize.py](r340/autoregion/recognize.py). It predicts **one rectangular material region**, using the existing support and common local bead spacing. Spacing is the median native length of accepted primitive links within100px, recomputed independently in verification. Four rectangle boundaries are normalized by that spacing and fitted by componentwise medians of the odd-numbered24 manual examples. Labels and brightness do not fit these boundaries. The final bounds relative to support, in spacing units, are `[+.1600, −.1698, +.3362, +.1315]`. There is no per-bead region adjustment.

Within that rectangle, choose the complete contiguous3×3 patch whose **maximum over all27 RGB values** is smallest. Black is strictly below **73.5**. The same measurement and threshold from the completed48-bead diagnostic are unchanged. A bright lobe can remain in the rectangle; no lobe detector is run.

An initial inscribed-disk region lost useful rectangle corners and sometimes contained no complete3×3 patch. It missed six maker black beads overall and abstained on70 measurements. Its source, model, all1058 outputs and error images are preserved as `explore.py`, `geometry-model.json`, `trial-1.json` and `trial-1-*`. The **single geometry refinement** restores the rectangle directly from the same24 annotations. No radius/threshold sweep followed.

The complete final pigment module is16 physical lines /13 nonblank lines, including its docstring and import; it contains12 executable AST statements excluding imports, docstrings and function definitions. Its geometry fitter is included. Data loading, frozen eligibility, native inspection and reporting are explicit separate operations, not hidden pigment rules. The earlier stopped, uncommitted R340 mean-based experiments remain preserved and unused. Current delivery is exclusively `r340/autoregion/`; previous diagnostic directories are unchanged.

## Tests beyond the original48

Raw region scores are retained everywhere; automatic decisions are restricted to the **unchanged450-observation physical-interior screen** and established indexing. Edge-near observations abstain. This is inherited eligibility, not a new segmentation/classifier threshold.

| Reference set | Raw TP / TN / FP / FN | Raw abstentions |
|---|---:|---:|
|Original48:24 black,24 colored|24 /24 /0 /0|0|
|Additional65 maker labels:31 black,34 colored|30 /34 /0 /1|0|
|All113 maker labels|54 /58 /0 /1|0|
|Additional37 colored:34 maker +3 visual dark-red controls|0 /37 /0 /0|0|

Maker-black raw recall is **98.18%**. The three visually verified dark-red controls are C-0309-0966=120, C-0313-1445=132 and C-1899-0420=193; they are not relabeled as maker confirmations.

The automatic/manual rectangle intersection and both scores are recorded individually for all48. All48 comparisons were inspected. **18/48 selected patches lie wholly inside the original small manual rectangle**;30 select other pixels, so matching classifications alone does not establish matching ownership. The comparison sheets retain the exact differences. Manual rectangles are reference samples, not complete body contours.

Only odd24 fit geometry. Even24 and additional65 have independent labels, but their disk-stage errors were exposed before the one refinement. These are retrospective generalization checks, **not pristine blind accuracy estimates**. The three posthoc native stress cases below did not alter the algorithm.

## Actual errors and native pixels

| Observation | Reliable interpretation | Automatic score | Separate genuine-glass witness | Automatic policy |
|---|---|---:|---:|---|
|K-1740-1575|Maker black|90: false negative|22|Interior; retain authoritative black|
|RF70T-K-2172-1154|Recorded black, corroborated by native inspection|101: missed black|30|Interior; preserve recorded black|
|K-2183-1053|Recorded black, corroborated by native inspection|139: missed black|15|Edge: abstain|
|C-1253-2928|Visually verified yellow body; not new maker ground truth|58: raw false positive|162|Edge: abstain; preserve yellow|

The three black misses retain bright body shoulders in their automatic rectangles; dark glass lies farther right. C-1253-2928 instead samples the upper/right dark boundary beyond the visible colored glass. These are **region-placement errors**, not evidence against the material-darkness distinction. Manual witnesses diagnose them and are **not substituted into automatic decisions**. The review shows unaltered native crops, automatic/manual boxes, exact3×3 RGB values, current adjacency, and own-photograph number-to-ID keys. No already reviewed maker color is asked again.

Across the119 maker/visually reviewed diagnostic bodies, raw results are54 TP /61 TN /1 FP /3 FN. The posthoc stress cases make this a diagnostic denominator, not a random accuracy sample. After the existing eligibility screen:23 TP /35 TN /0 FP /2 FN, with59 abstentions. Whole-inventory truth is unavailable; agreement with stored labels is not photographic accuracy.

On the **same113 maker labels and same physical screen**, R339's selected method gives17 TP /18 TN /0 FP /0 FN /78 abstentions; R340 gives23 /32 /0 /1 /57. R340 newly recognizes seven black controls that R339 abstained on, including E5-2272-1815, but loses K-1740-1575. The saved earlier complex benchmark is also tabulated in evaluation.json. It is not voted with the new method.

## Global overlay and pattern

All **1058 active observations** receive a saved raw measurement. Automatic results are **141 black /309 not-black /608 abstentions**, versus122 /224 /712 for R339's stable selected procedure. There are19 raw positive disagreements with nonblack stored colors: one maker correction, four adopted interior corrections, and14 outside the fixed eligibility domain. Three recorded-black raw misses remain black. Not-black does not choose red versus yellow.

All six new nonduplicate maker decisions are retained. **E5-2272-1815 changes yellow→black**; the other five confirm black. Four independently inspected changes are accepted:

| ID | R339 → overlay | Score | Fixed208 position, checked only after freeze |
|---|---|---:|---:|
|E5-2139-2470|yellow→black|46|190|
|NEW-1036-2833|yellow→black|53|190|
|NEW-1702-1860|red→black|39|190|
|NEW-903-2501|red→black|49|86|

The [freeze ledger](r340/autoregion/freeze.json) retains before labels, maker authority, native ownership judgments, original pixels and source hashes. No body, coordinate, link, row continuation, unusual gap, duplicate/phantom exclusion or winding changed. The graph still has1058 records /1040 indexed /2287 links /H=(214,201).

| Fixed cohort | R339 supported/conflict/insufficient | Maker only | Final |
|---|---|---|---|
|Full1040|179 /21 /8|180 /20 /8|**181 /19 /8**|
|Original1039|179 /21 /8|180 /20 /8|181 /19 /8|
|Frozen710|151 /4 /53|152 /3 /53|153 /2 /53|
|Physical450|70 /3 /135|71 /2 /135|73 /0 /135|

Zero remaining physical450 conflicts does **not** remove the19 full-cohort conflicts. Remaining positions are **4,9,22,29,35,80,83,101,102,112,127,131,138,154,157,169,184,189,190**. Every actual source ID is exposed in the review and [pattern analysis](r340/autoregion/pattern-analysis.json). At190, REC266-P054537 remains recorded red and outside eligibility; at112, NEW-910-2406 and REC266-P106767 remain unresolved; at157, E9-2263-1691 remains outside eligibility. Their raw black scores do not authorize automatic changes.

For the same1035 unchanged-color targets, flat208 geographic held-out agreement moves93.04%→93.53%; whole-occurrence agreement97.29%→97.49%. These evaluate recorded-label prediction, not photographic classification truth. The A mapping,2704 count,208 repeat and13 repetitions remain conditional; no new count, period or winding search occurred.

Independent checks cover all1058 native scores, recomputed neighboring spacing,2287 equations,1040 distinct quotient sites, all113 authoritative colors,2496 strict cohort entries, nine literal review crops and2272 unchanged historical files. A fresh four-stage replay matches eight scientific products, excluding only runtime/UTC and dependent hashes. Offline desktop/mobile review checks are recorded beside the review.

Use this simple method for conservative interior photographic proposals with native confirmation. The demonstrated ownership errors prevent treating it as an unrestricted replacement for reliable existing labels. No further classifier feature was added. **Stop for review; no R341.**
