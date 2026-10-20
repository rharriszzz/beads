# R339 — simpler black evidence and three newly supported positions

[Photographic review](r339/review/index.html) · [All remaining source records](r339/review/ledger.html) · [Reproduce](R339_REPRODUCE.md) · [Independent checks](r339/verification.json)

The strict conditional 208 block improves from **176 supported / 24 conflicting / eight insufficient** to **179 / 21 / eight**. Your three corrections resolve positions **27 and 34**. Three additional independently supported red-to-black changes resolve **92** and reduce disagreement at 112 and 196. No bead identity, native coordinate, lattice coordinate, link or winding changes.

## Exact maker decisions and preserved reconstruction

The original R338 photograph keys resolve all six numbered references exactly. Feature 12 in the MAT25-K-2270-1942 photograph is **NEW-2259-1961**, not feature 12 in a different image. The [decision ledger](r339/maker/decisions.json) retains the original color, native support, lattice coordinate, own-panel key and authority.

| Named R338 photograph | Own feature | Stable ID | Decision |
|---|---:|---|---|
|NEW-2185-1265|1|NEW-2185-1265|red → black|
|NEW-1221-2081|1|NEW-1221-2081|red → black|
|NEW-1530-3049|1|NEW-1530-3049|black confirmed|
|D40-K-2081-2611|1|D40-K-2081-2611|black confirmed|
|MAT25-K-2270-1942|1|MAT25-K-2270-1942|black confirmed|
|MAT25-K-2270-1942|12|NEW-2259-1961|red → black|
|R332-B-0098-0092|completed association|R332-B-0098-0092|body, color and displayed links confirmed|

All maker-confirmed colors are protected, including specifically displayed earlier approved R331/R336 regions and the R334–R336 corrections. This yields 107 active protected records, with 49 black, 32 red and 26 yellow labels. Three excluded colored maker examples remain excluded; they are not added as active training/test observations. The protection list is explicit in the frozen overlay.

Baseline and final both have **1,058 records, 1,040 indexed observations and 2,287 links**, one connected reconstruction and H=(214,201). All native XY, lattice AB, IDs, original observation fields, adjacency dictionaries, phantom/duplicate exclusions and accepted unusual gaps are preserved. Only six indexed colors change: three by maker review and three below. Indexed colors change from 357 red / 316 yellow / 367 black to **351 / 316 / 373**. The original records and intermediate maker-only layer remain available; no history is overwritten.

## A simpler black test, including a rejected trial

The selected procedure replaces the old two reflection extents, morphological lobe tracking and annuli with a common body aperture and one scalar brightness comparison:

1. At the existing observation, use a circular aperture with radius 0.40 times local common all-color support spacing. Clip it at neighboring indexed supports' geometric bisectors. This is a sampling aperture, not a claimed measured bead center or complete body boundary. Identity and association remain inherited photographic constraints.
2. Use **maximum RGB channel** as brightness. Exclude the upper 20% brightness tail, retaining ties. Measure the mean brightness of the remaining material. No hue, selected reflection component, centroid movement or visible-highlight requirement enters this step.
3. Compare with the nearest five eligible black and five colored recorded bodies within 220px, requiring at least three of each. Reference medians are frozen before target decisions. All seven current maker-review targets are excluded from reference training, as is each target itself.
4. With black reference brightness B and colored brightness C, use `s=(target−B)/(C−B)`. If C≤B, abstain. Black requires s≤0.25; not-black requires s≥0.75; the intervening range is unknown. Geometry coverage requires at least 50 retained pixels, half the aperture area and six sectors. These common eligibility checks apply to every pigment.
5. For a **new color correction**, require the same black conclusion at the predeclared 0.35 / 0.40 / 0.45 spacing apertures, sufficient physical-outline clearance and native confirmation that samples belong to the existing body. Edge-near, unindexed or unstable cases abstain. The outline criterion is the unchanged R338 physical screen, not the 710-node connectivity proxy.

The upper-tail mask is a conservative bright-pixel exclusion, not a semantic declaration that every removed pixel is reflection or that every remaining pixel is glass. A diffuse reflection can remain and cause abstention. No dark mask, sample or score can create or merge an identity. The three actual changes were checked in native context against neighboring bodies; all fixed supports are unchanged. A uniformly dark patch remains measurable with zero excluded highlight pixels, demonstrating that a reflection is not a classifier requirement. Channel permutation leaves this brightness measure invariant.

The first bounded trial instead used weighted luminance. It proposed ten nonblack→black changes, including visibly red bodies C-0309-0966, C-0313-1445 and C-1899-0420. Red material can have much lower weighted luminance than nearby yellow material. That trial is **rejected**, including the stable false proposal at C-1899-0420. Replacing the scalar with maximum-channel brightness removes those proposals without changing the aperture, contrast boundaries or adding case-specific exceptions. The failed data and native illustrations remain under [development](r339/development/README.md). No further parameter search was conducted.

The old three-radius/two-extent black-first procedure is recomputed on all 1,058 active records for comparison. It remains a historical benchmark; it is **not stacked onto the new acceptance rule**. Within the conservative interior domain, retain the simpler maximum-channel rule for new corrections. Preserve existing labels outside that domain. The evidence does not establish superior whole-photograph accuracy or justify deleting historical uncertainty.

## Global comparison and application

| Same target set | Old: agree / disagree / abstain | Stable simple: agree / disagree / abstain |
|---|---:|---:|
|107 maker-reviewed active colors|63 / 0 / 44|31 / 0 / 76|
|Same 51 maker-reviewed physical-interior colors|32 / 0 / 19|31 / 0 / 20|
|33 historical R161 working-color references|25 / 0 / 8|9 / 0 / 24|

The all-target maker comparison has different edge coverage: the simple method deliberately abstains outside its physical-interior domain. On the **same eligible interior controls**, both methods show zero disagreements and similar coverage. These are previously exposed maker decisions and a small retrospective sample, not a fresh blind estimate. R161 working-color agreements are not new maker pigment certifications. Existing labels partly derive from the old method, so agreement with the full working inventory cannot fairly prove that the old method is more accurate.

Across all active records, the central simple aperture gives 127 black / 230 not-black / 701 unknown. Requiring aperture stability gives 346 decided records and 712 abstentions; all 346 lie in the 450-record physical-interior screen. The old method decides 699 and abstains on 359 overall; within those same 450 interior records it decides 258 and abstains on 192. These are coverage counts, not accuracy percentages.

Five previously nonblack records are central-aperture black suspects. Three are stable and have convincing native body support; all three old two-extent results were unknown:

| Observation | Original → final | Simple normalized scores at 0.35 / 0.40 / 0.45 | Outcome |
|---|---|---|---|
|NEW-1247-2991|red → black|.162 / .188 / .179|Correct existing dark body; bright patch separate from the surrounding glass.|
|NEW-2156-1135|red → black|.179 / .201 / .219|Dark material belongs to the existing body between colored neighbors.|
|NEW-2235-1476|red → black|.107 / .138 / .172|Native body remains dark across all common aperture sizes.|
|E5-2272-1815|yellow retained|.204 / .240 / .285|Larger aperture is unknown; no correction.|
|NEW-1702-1860|red retained|.187 / .226 / .251|Larger aperture is unknown; no correction.|

No black→colored changes or additional yellow→black changes are forced. NEW-910-2406 and E9-2263-1691 have dark-looking raw samples but fail the physical-interior screen; their red labels remain. The [comparison data](r339/comparison/comparison.json) and [fixed photographic freeze](r339/results/freeze.json) separate proposals, accepted changes, protected labels and abstentions. All three accepted native contexts appear as completed, non-question panels in the review.

## Fixed 208 analysis after the photographic freeze

| Fixed cohort | R338: supported / conflict / insufficient | Maker-only | Photographic final |
|---|---|---|---|
|Unchanged 1,040 active indexed IDs|176 / 24 / 8|178 / 22 / 8|**179 / 21 / 8**|
|Original R336 1,039 IDs|176 / 24 / 8|178 / 22 / 8|179 / 21 / 8|
|Frozen 710 graph proxy|149 / 6 / 53|150 / 5 / 53|151 / 4 / 53|
|Fixed 450 physical-outline interior IDs|68 / 6 / 134|69 / 5 / 134|70 / 3 / 135|

R339 adds no observations, so the current expanded R338 cohort remains fixed at 1,040 rather than growing. Separate original 1,039 and smaller fixed cohorts show that progress does not come from selecting away disagreements. The physical subset's conflict at112 becomes insufficient after NEW-1247-2991 is corrected; the **full** position112 still conflicts. That subset change is not another recovered position.

The strict rule is unchanged: a supported entry needs at least three unanimous recorded colors spanning at least three geographic sections. Any actual opposite-color record retains a conflict. Maker corrections settle27 and34; automatic NEW-2235-1476 settles92. Positions112 and196 lose one red disagreement each but remain unknown. The eight insufficient positions remain insufficient. [pattern208.json](r339/analysis/pattern208.json) retains the incomplete sequence and every source ID; no majority fill is made.

Held-out recorded-label agreement on the identical 1,040 observations:

| Fixed predictor and holdout | R338 | Maker-only | Photographic final |
|---|---:|---:|---:|
|Flat208, guarded geography|89.808%|92.115%|92.596%|
|Hierarchical208, guarded geography|92.404%|94.135%|94.231%|
|Flat208, whole cyclic occurrence|96.058%|96.346%|96.827%|
|Hierarchical208, whole cyclic occurrence|96.250%|96.538%|97.019%|

The hierarchy pools evidence at residue104 without asserting an exact104 repeat. Full scores partly improve because target labels changed. On the separate **1,034 unchanged-color targets**, flat guarded agreement improves90.232%→92.650%, and whole-occurrence hierarchical agreement96.809%→97.002%; those gains arise through changed training evidence rather than changing those targets' labels. They remain same-photograph, exposed cross-validation, not independently certified photographic accuracy.

A post-freeze predictor trained on original other occurrences predicts black for all six corrected records (6/6 agreement). The original frequency baseline also predicts black for all six. This is consistency with208, not distinctive proof of it or a new blind discovery test. Neither the repeat predictor nor its expected colors entered photographic correction, reference selection or classifier tuning.

## Remaining review and actual conflict records

The compact review has five groups, 25 numbered native/current-diagram panels and149 literal native crops. Each question target is feature1 in **its own named photograph and immediately matched diagram**; full stable-ID keys and optional original-sample overlays are available. No maker-confirmed target is re-questioned. All29 unknown positions have a source ledger.

The high-value interior questions are196 (E5-2272-1815),190 (E5-2139-2470, NEW-1702-1860, NEW-1036-2833) and86 (NEW-903-2501). The retained lower-priority edge-near questions are112 (NEW-910-2406, REC266-P106767) and157 (E9-2263-1691). Position92 is solved and is no longer a question. At190, independently confirmed different pigments on correctly associated bodies would be evidence against exact208; there is no instruction to make them all black.

All remaining full-cohort conflicts, with complete stable observation IDs:

| Position | Current color counts | Contributing observation IDs |
|---:|---|---|
|4|black:2, red:2|K-0603-1624; K-1296-1491; R332-R-0196-0188; REC266-P054157|
|9|yellow:4, red:1|C-1007-2744; C-1180-2153; C-1580-2981; C-1766-1792; R332-R-0147-0142|
|22|black:4, red:1|D40-K-1772-1751; K-0990-2705; K-1219-2134; MAT25-K-1538-2998; NEW-1251-1537|
|29|yellow:4, red:1|C-1001-2678; C-1226-1539; C-1250-2138; E5-1792-1727; NEW-1519-2976|
|35|yellow:4, red:1|C-0978-2667; C-1263-2116; C-1775-1706; E5-1503-2999; REC266-P074746|
|80|black:4, red:1|K-1354-3005; K-1410-2057; MAT25-K-0915-2520; NEW-1942-2725; REC266-P076585|
|83|yellow:5, red:2|C-0315-0867; C-0870-0396; C-1032-1519; C-1582-0235; E5-0355-1525; R332-R-0037-0040; REC266-P035619|
|86|black:4, red:1|D40-K-1329-3022; D40-K-1424-2037; K-1943-2759; NEW-2237-2128; NEW-903-2501|
|101|yellow:3, red:1|C-0272-1512; C-0990-1588; C-1677-1513; REC266-P100583|
|102|black:3, red:1|K-0970-1557; NEW-1681-1498; NEW-290-1494; NEW-343-803|
|112|black:3, red:2|D40-K-1874-2821; K-1506-2006; NEW-1247-2991; NEW-910-2406; REC266-P106767|
|127|yellow:2, red:1|C-0900-1612; C-1592-1479; R332-R-0125-0118|
|131|black:3, red:1|D40-K-2217-2280; K-1841-2884; NEW-2100-921; NEW-2251-1608|
|138|black:4, red:1|D40-K-1589-1970; K-1813-2878; NEW-2199-2298; NEW-948-2311; RF70T-K-1163-2935|
|154|black:3, red:1|K-0802-1592; NEW-1493-1439; NEW-199-1335; NEW-451-650|
|157|black:4, red:1|D40-K-2191-2368; E9-2263-1691; K-1774-2936; R332-B-0029-0027; R332-B-0109-0107|
|169|black:6, red:1|K-1172-0348; K-1845-0412; K-2161-1039; K-2209-2420; K-2303-1728; R332-R-0077-0077; REC266-P031642|
|184|black:4, red:1|D40-K-1701-1890; K-1072-2198; K-1683-2959; MAT25-K-1060-2836; NEW-2136-2445|
|189|yellow:7, red:1|C-1067-2156; C-1243-0349; C-1691-3004; C-1882-0479; C-2168-2478; C-2288-1794; E5-2165-1110; R332-R-0197-0183|
|190|black:2, yellow:2, red:2|D40-K-1077-2175; E5-2139-2470; K-1667-2990; NEW-1036-2833; NEW-1702-1860; REC266-P054537|
|196|yellow:1, black:4|E5-2272-1815; K-1663-3006; MAT25-K-2142-2497; NEW-1092-2152; NEW-2156-1135|

A=7a+6b, N=2704 and13 repetitions of208 remain the leading **conditional** interpretation. No new total-count, row-continuation, shortest-complete-pattern or winding claim follows from these pigment changes. Multiples of13 remain allowed. The next investigation should use the five concrete visible-body questions, with an uncertain answer retained as uncertain; a genuinely confirmed opposite-color pair requires association/coherent-index investigation instead of a majority recoloring.

## Verification and delivery

Independent checks verify1,919 historical scientific/photo/model hashes; all exact maker panel mappings; six and only six color changes;107 protected active maker colors; all1,058 native positions,1,040 coordinates and2,287 primitive links;1,313,083 native aperture pixel-samples;607,971 old-method ring pixel-samples; maximum-channel invariance under channel permutation; a reflection-free measurable dark patch;12 cohort/layer pairs;48 independently implemented held-out predictor checks;509 own-panel key rows; and149 pixel-exact native crops. The checks certify arithmetic, provenance and implementation, not independent truth for every working body.

Fresh end-to-end replay matches all generated scientific results, original-pixel crops and review code exactly apart from measured runtime. It takes54.209s with2,590.39MiB peak child RSS; the experiment includes recomputing the old benchmark globally. Actual Chromium checks pass offline and at390px width, including all keys, case navigation, zoom/pan, photo links, sample overlays and the29-position ledger, with no page errors or failed requests. See [independent receipt](r339/verification.json), [performance](r339/performance.json) and [browser receipt](r339/review/browser-verification.json).

Scoped sources, outputs, review, report and handoff are committed and pushed on `photo-2-strategy-v3`; independent remote verification is in [delivery.json](r339/delivery.json). **STOP after R339 for maker review; no automatic R340.**
