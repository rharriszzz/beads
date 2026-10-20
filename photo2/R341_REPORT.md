# R341 — global native-glass audit, twelve corrections,191 supported positions

[Interactive photographic review](r341/review/index.html) · [Reproduce](R341_REPRODUCE.md) · [Per-observation audit](r341/native-audit.json.gz) · [Correction ledger](r341/corrections.json)

**Every active black and red record was audited:378 black and356 red, with324 yellow controls.** Twelve independently supported red→black corrections improve the strict conditional208 block from **181 supported /19 conflicting /8 insufficient to191 /9 /8** on the identical1040 observations. All identities, native coordinates, lattice coordinates, accepted links, maker colors and exclusions remain unchanged.

The fixed3×3 /73.5 measurement remains effective. Geometry alone still cannot certify ownership at every rope edge;44 measurements abstain after explicit native inspection. Four high-value questions are presented, with original pixels, local stable-ID keys and matching current adjacency diagrams. Correct classifications are kept outside the question queue.

## Modest geometry experiment

Two alternatives were declared and evaluated against the R340 rectangle:

- A **circular core**, radius one-quarter of common local neighbor spacing.
- An ellipse with semiaxes0.30/0.20 spacing, oriented by the local native image of primitive direction(1,−1). The local affine map uses accepted neighboring primitive-link vectors, without color or string-period information.

Both retain the R340 geometry-only material-window midpoint offset. Nearby recorded bead locations clip the search to an inset Voronoi cell. Only complete3×3 patches wholly inside that one region are eligible. Choose the patch minimizing the maximum of all27 RGB values; **black remains strictly below73.5**. No averaging, reflection analysis, segmentation, aperture voting, identity recentering or threshold tuning occurs. [recognize.py](r341/recognize.py) contains the complete computation.

Selection used the original48 references plus the four explicitly requested R340 failures. Both new alternatives give27 true-black /23 true-colored /2 false-black on these52 development cases, with no missed black. The ellipse gives no advantage, so the **simpler circle is selected**. No further geometry search followed.

The remaining **64 maker examples**, excluded from R341 model selection, give **30/30 black and34/34 colored correct raw results**. These labels were historically exposed in R340; this is held-out model selection within R341, not a newly discovered blind photographic test.

| Known case | R340 score | R341 score | Native conclusion |
|---|---:|---:|---|
|K-1740-1575|90|24|Owned black glass recovered|
|RF70T-K-2172-1154|101|29|Owned black glass recovered|
|K-2183-1053|139|16|Owned black glass recovered; existing edge eligibility retained|
|C-1253-2928, yellow|58|44|Still selects boundary darkness; abstain, preserve yellow|

The wider core introduces a raw false-black at maker-red **C-0505-1557=57**, above its actual red glass. Yellow **C-1264-2957=43** and dim red **E5-1178-2887=73** also supply independently inspected boundary failures. None is recolored. These failures concern **which pixels were selected**, not a demonstrated failure of73.5 on confidently owned colored glass.

## Complete color audit and reference results

All1058 original-native contexts were inspected in a saved23-sheet atlas, including every automatic abstention. All19 raw label disagreements were separately inspected with larger unaltered/marked contexts. Expanded inspection of all50 initial ownership flags confirms six additional owned not-black patches, leaving44 uncertain. The atlas-only epoch is preserved under `r341/development/atlas-only/`; no color correction differs between epochs. [Native judgments](r341/native-judgments.json) explicitly record this revision and the twelve accepted corrections. They are photographic inspection annotations, not extra classifier rules or a hidden pattern vote.

| Existing color | Records inspected | Native-audited black /not-black /abstain |
|---|---:|---:|
|Black|378|377 /0 /1|
|Red|356|12 /320 /24|
|Yellow|324|0 /305 /19|
|Total|1058|**389 /625 /44**|

The sole audited-black abstention is the very dim **PROV326-290-1410** material boundary; its established working identity and black label remain. No active recorded black bead now has a bright raw measurement. That is not proof that every dark geometric sample is genuine glass.

The autonomous classifier retains the unchanged physical-interior/indexing eligibility: **143 black /307 not-black /608 abstentions**. The larger native-audited coverage above requires the explicitly recorded visual ownership checks. These two outputs must not be conflated.

| Same113 active maker labels | TP /TN /FP /FN | Abstentions |
|---|---:|---:|
|R340 raw|54 /58 /0 /1|0|
|R341 raw|55 /57 /1 /0|0|
|R340 autonomous, same eligibility|23 /32 /0 /1|57|
|R341 autonomous, same eligibility|24 /32 /0 /0|57|
|R341 after native ownership audit|55 /53 /0 /0|5 colored|

All55 maker-confirmed black beads are recognized by the raw and native-audited test. The original48 now give47/48 raw agreements because of C-0505-1557; its authoritative red is protected. The other three historical maker-colored exclusions were also tested as **reference-only controls**: all raw not-black, all still excluded/abstained, no role admissions. Thus all116 available maker-color records are accounted for. Raw agreement at a historically excluded source does not itself certify glass ownership.

Whole-inventory photographic accuracy is not known. Matching an old label or passing a maker test does not independently prove correct material selection. The review exposes actual RGB samples and every retained ownership uncertainty.

## Frozen reversible corrections

All twelve following bodies have visibly attributable dark glass and pass the same fixed measurement. All were previously raw R340 suspects outside its automatic eligibility; this round's full native audit supplies the missing ownership review. The changes arise from that review, not merely from widening the classifier.

| ID | Before→after | Score | Conditional208 position, checked after freeze |
|---|---|---:|---:|
|E9-2263-1691|red→black|32|157|
|NEW-1251-1537|red→black|36|22|
|NEW-2136-2445|red→black|58|184|
|NEW-2199-2298|red→black|36|138|
|NEW-2251-1608|red→black|32|131|
|NEW-451-650|red→black|27|154|
|NEW-910-2406|red→black|30|112|
|R332-R-0196-0188|red→black|65|4|
|REC266-P054157|red→black|40|4|
|REC266-P054537|red→black|46|190|
|REC266-P076585|red→black|37|80|
|REC266-P106767|red→black|47|112|

[graph.json.gz](r341/graph.json.gz) is a separate overlay on R340. Original records and all prior provenance remain. Indexed colors become337 red /313 yellow /390 black. Record count1058, indexed count1040, links2287, one reconstruction and H=(214,201) are unchanged. E5-2272-1815 and every earlier maker decision remain authoritative.

## Pattern result and what prevents completion

Photographic classifications and native judgments were frozen and hashed **before** the R341 pattern computation. No predicted color selected a correction.

| Identical cohort in both layers | R340 supported/conflict/insufficient | R341 |
|---|---|---|
|Full1040|181 /19 /8|**191 /9 /8**|
|Original1039|181 /19 /8|191 /9 /8|
|Frozen710 connectivity cohort|153 /2 /53|155 /0 /53|
|Physical450|73 /0 /135|73 /0 /135|
|Same1002 native-owned indexed sources|185 /12 /11|195 /2 /11|

The source-selection differences between rows are **not additional recoveries**. The full result remains191/9/8. In particular, the nine full-cohort conflicts are not erased by omitting uncertain sources.

Positions **4,22,80,112,131,138,154,157,184,190** resolve. Remaining conflicts are **9,29,35,83,101,102,127,169,189**; every responsible ID is linked in the review and [analysis](r341/pattern-analysis.json). The eight insufficient positions **43,62,75,82,89,140,147,186** have recorded single-color evidence but lack the required three geographically distinct supports. No majority-filled entry is adopted.

The remaining disagreements consist of seven red/yellow groups and two black/red association cases. At102, the red support NEW-1681-1498 lies near the upper edge of recorded yellow C-1677-1513; the selected dark patch is not established as its own material. At169, R332-R-0077-0077 is a partial-body/neighbor-boundary question. NEW-563-1633 similarly lies near maker-yellow E5-0562-1620 but remains unindexed. No identities or indices are changed to exploit these findings.

There is **no pair of contradictory maker-confirmed colors at one residue**. Positions9 and35 retain red/yellow disagreements even among native-owned samples, but the darkness test does not certify red versus yellow pigment. Position29 retains maker-authoritative red NEW-1519-2976 against four working yellow records. Filling either group by majority would conceal the problem. If the retained colors and associations are all confirmed correct, **exact208 under the current indexing is contradicted**, while a strong spatial recurrence could still exist.

On the identical1028 unchanged-color targets, flat208 geographic held-out agreement improves **94.46%→96.21%**; whole-occurrence agreement **98.64%→98.83%**. Hierarchical104-parent geographic agreement improves96.01%→97.18%, and whole-occurrence98.83%→99.03%. These measure held-out prediction of recorded colors, not photographic accuracy or proof of physical stringing order.

A=7a+6b, total2704 and13 repetitions remain conditional. No new winding, physical fit or pattern-length search was launched. The most valuable next step is the **four native review questions**, then targeted association/pigment resolution and additional independent coverage of the eight insufficient positions. The actual shortest complete sequence remains unrecovered.

Independent verification checks both alternatives'2116 native scores and complete masks, all1058 neighbor fits, unchanged2287 primitive equations,1040 distinct quotient sites, all maker labels,2080 strict cohort entries, eight held-out prediction calculations and21 literal native crops. Historical2367 scientific files are hash-preserved. A fresh replay reproduces scientific JSON, native atlas/crops and offline HTML; actual desktop/mobile/offline controls and local keys are checked separately. **Stop after delivery for review; no R342.**
