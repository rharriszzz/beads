# R330 — predictive partial color pattern and localized correction hypotheses

**A 104-position partial repeat predicts 143 withheld observations without a disagreement. A 208-position refinement explains substantially more of the sequence, and exposes likely color-classification errors. Six red-to-black corrections now have separate photographic support, but remain provisional. G's locally preferred geometry can be incorporated into shorter complete reconstructions; none yet improves both the photographic and pattern evidence.**

[Compact original-photo review](r330/review/index.html) · [Reproduction](R330_REPRODUCE.md) · [Verification](r330/verification.json) · [All suspicious observations](r330/review/suspects.csv) · [208-position motif evidence](r330/review/motif.csv).

No human decision is required now. There is no useful unresolved visual choice that needs to be delegated to the user. No original observation, pixel, ID, color label, saved alternative, working graph or physical model is changed. This experiment follows the new authorization to continue beyond R329's stopping point. The working reconstruction remains 900 indexed observations, 1862 links, one component, and 38 unindexed observations.

## Evidence and separation of error mechanisms

Inputs are the frozen R327/R328 photographic bank and all 20 saved R328/R329 maps, including the human-review supplement and photographic diagnostics. Reference C-1302-0316 remains lattice/index zero. Convention A is `7a+6b`; B is `6a+7b`. Both directions and origin changes are equivalent relabelings for periodic prediction; this invariance is checked numerically. New connected-growth candidates use the original seed, overlap, distinct-site, primitive-edge and return constraints.

| Mechanism | Treatment in R330 |
|---|---|
| Color substitution | Separate pixel-appearance audit and provisional color overlay; never overwrite a historical label |
| Uncertain color | Disagreement among appearance controls remains uncertainty; classifier votes are not calibrated probabilities |
| Wrong index | Penalized ±1/±6/±7 shift proposals; independently tested against photographic attachments |
| Wrong lattice/row continuation | Actual saved-patch recombination and full suffix replay, especially G/H |
| Duplicate or missed observation | Inventory and index-collision audit; no automatic merging or deletion |
| Correlated regional errors | Whole photographic sections held out; burst perturbations and correlated null controls |
| Unobserved sequence position | No color emission, no claimed empty physical position, and no edit deleting a physical bead |

The original A mapping has no duplicate index modulo 2704 among its 900 observations. One support pair lies within 12 pixels: E5-1499-3037 / K-1508-3038, distance 10.668 pixels; they are not both indexed. This is an unresolved duplicate/neighbor candidate, not evidence of a duplicate bead. All 38 unindexed observations are retained in the inventory. Nothing establishes that a physical bead is absent.

## Implemented methods and their limits

| Method | Implementation | Strength and failure mode |
|---|---|---|
| Weighted approximate periodicity | Per-residue weighted color counts, Dirichlet shrinkage toward training color frequencies; period 1–900, 40 map/convention combinations | Fast, tolerates minority substitutions and sparse positions. A row shift contaminates many residues; a short period can blend two halves of a longer motif. |
| Hierarchical periodic prediction | A 208-position distribution shrinks toward its 104-position parent; 416 shrinks toward 208 | Shares evidence where the longer motif is sparse. Improves 208 prediction substantially; can retain parent bias. This is exploratory follow-up after opening the initial test. |
| Piecewise index alignment / Viterbi | 96 photographic bins; offsets −21…+21; transitions 0, ±1, ±6, ±7; penalties 3, 6, 10; frozen motif and unused outer-section colors during shift selection | Recovers sustained index bursts in real-data perturbations. Cannot repair isolated index mistakes at these penalties; color bursts can masquerade as shifts. Proposals have no authority to change the graph. |
| Robust consensus / RANSAC | Considered; weighted majority implemented, random minimal-motif sampling not implemented | A sparse 208-entry motif needs many sample observations; random subsets would often leave entries unidentified and reuse the same photographic evidence. Section-level consensus and null controls give a clearer bounded test here. |
| General edit-distance alignment | Considered; the narrower shift-state model is implemented | Free insert/delete operations risk confusing unobserved positions with missing physical beads or overfitting correlated errors. Explicit observation splitting/merging remains unimplemented. |

The recurrence is a standard hidden-state dynamic program; the adaptation uses index-offset states rather than speech states. Background references: [Rabiner's original HMM tutorial](https://www.ece.ucsb.edu/Faculty/Rabiner/ece259/Reprints/tutorial%20on%20hmm%20and%20applications.pdf) and [Fischler and Bolles' original RANSAC paper](https://www.sri.com/publication/artificial-intelligence-pubs/random-sample-consensus-a-paradigm-for-model-fitting-with-applications-to-image-analysis-and-automated-cartography-2/). Neither paper is evidence about this bracelet.

Main weights are 1 for recorded red/yellow, .55 for black, .25 for the provisional site. These are explicit sensitivity assumptions, not measured classification probabilities. Lower black weight avoids treating every weak black cue as equally reliable; weights .25/.55/1 are also tested. Motif uncertainty is preserved rather than filling every residue with its plurality color.

## Initial selection and genuinely unused sections

Divide the photographic circuit into 12 fixed station sections. Sections 2, 5, 8 and 11 are excluded from map/period selection. The other eight are split into two alternating groups, each predicted from the other. Rank by predictive log gain over training color frequencies, minus `0.1 × P × log(3) / development_weight`. This explicit modest description penalty discourages long motifs; predictive shrinkage supplies an additional sparsity penalty.

Freeze six best map-period pairs and additional distinct periods before opening the four held-out sections. Every observation occurs once in an evaluation, regardless of how many overlapping growth windows reused it. Sections are conservative support units, not independently labeled photographic ground truth. Features and maps still come from one photograph.

| Selected working-A period | Development log gain | Original held-out log gain | Conservative known motif entries |
|---:|---:|---:|---:|
| 104 | .4630 | .5715 | 50 |
| 208 | .3819 | .5309 | 79 |
| 52 | .2958 | .3435 | 10 |
| 26 | .2360 | .2523 | 5 |
| 16 | .1208 | .1102 | 0 |
| 2 | .1127 | .0940 | 0 |

Log gains are natural-log units per weighted observation, relative to the frequency baseline; they are not accuracy percentages. The shorter periods capture partial structure or class alternation, not complete patterns.

The period-104 conservative motif has ≥80% weighted agreement, support in ≥3 training sections and smoothed winning probability ≥.60. It predicts **143/296 held-out observations (48.3% coverage), all correctly against the original labels**:

| Recorded color | Held-out observations | Confident predictions | Agree / disagree |
|---|---:|---:|---:|
| Red | 108 | 63 | 63 / 0 |
| Yellow | 92 | 55 | 55 / 0 |
| Black | 96 | 25 | 25 / 0 |

This is useful partial recovery, not 100% reconstruction accuracy. The remaining 153 held-out observations are not certified by this result.

The penalized selected score is .44050. In 39 within-section circular-label nulls on the selected map, no null exceeds it. A separate, stronger control repeats **the full 40-map × 900-period selection** in each of 19 nulls; the largest null score is .01892. The finite empirical tail bounds are 1/40 and 1/20 respectively, not calibrated global significance claims. These nulls retain section color totals and most local label order, while breaking long-range alignment. They do not preserve every relationship between pigment, visibility and geometry.

## Why 208 is a stronger full-motif candidate than 104

At period 104, index-zero yellow C-1302-0316 and index-104 red P5-1645-0309 occupy the same residue. Several analogous conflicts separate when the repeat doubles. On all original observations, weighted plurality mismatch falls from **12.08% at 104 to 4.78% at 208**; raw plurality disagreements fall from 116 to 44. These are in-sample diagnostics, not validation.

The following follow-up predictions leave each entire section out in turn. They were designed after the original held-out result was examined, so **they are exploratory computational cross-validation, not another blind test**.

| Model | Weighted log gain | Hard color agreement on all 900 original labels |
|---|---:|---:|
| Flat 104 | .6088 | 82.67% |
| Flat 208 | .5745 | 86.56% |
| Hierarchical 208, parent strength 1 | **.8260** | **91.89%** |
| Hierarchical 208, strength 3 | .7692 | 90.67% |
| Hierarchical 416, strength 1 | .8244 | 89.56% |

The 416 model gains no clear predictive advantage at the main weighting and uses a longer motif. With black weight .25 it has a small log-score advantage over 208; with weight 1, 208 again leads and reaches 94.44% hard agreement. Thus 208 is the leading economical candidate, not a uniquely established exact period. A hierarchical prior uses the same training observations at two resolutions; those levels are not separate evidence.

The displayed 208 motif uses a less prior-sensitive consensus rule: ≥80% weighted agreement, ≥3 observations and ≥3 photographic sections. It retains **154 entries and 54 unknowns**. `R/Y/B` mean red/yellow/black; `?` is unknown. Each line below is 52 consecutive residues, starting at reference index zero:

```text
Y?YY?YBYBY?YRBYBBYRRBY?YRBR?YYRBBR?YRBRBRBR?R?R?RRBR
R?R??BRBRY?RBBRYB?R?RYB?YRRY?Y?YRY?Y??YY?YBYBYBY???Y
R?YB?YRR?Y?YRBRBY?RB?R??RBR?RB?BRR?R?RBBRBR?RBR?R??R
R?RYRBRBRY?RBBRY?YRBRYB?YRRY?Y?YRY?Y??YY?YBYBY?Y??YB
```

The full-data motif is a proposed consensus, not a truth label for its own contributors. Applying its support rule with each target section excluded yields 621 confident predictions: 600 agree and 21 disagree. By color: red 251/271, yellow 203/203, black 146/147. All support IDs, original coordinates, indices, distinct repeat numbers and sections are serialized. The unmodified original labels are the scoring reference, including suspected errors.

For the working A winding, 2704 allows 26 repeats of 104 or 13 repeats of 208. These counts describe the conditional map, not 26 or 13 independently observed complete motifs: only 900/2704 positions are indexed. Exact cyclic 208 repetition is arithmetically compatible with N2080, 2288, 2496, 2704, 2912, 3120, 3328 or 3536 within the earlier 2000–3600 range. These other counts do not acquire photographic witnesses by passing arithmetic. Approximate/incomplete motifs do not require count divisibility.

All saved maps and both conventions retain their own counts. For 104, original outer-section log gains range from .316 to .572 across them; working A leads. Early A gives .407. A later own-map 208 control evaluates all 40 original map/convention combinations, 44 new G candidates and 81 H paths; working A and paths reproducing its map lead. The refined 208 decoder also selects zero shifts at all three penalties. Reverse direction and cyclic origin shifts preserve likelihoods and conflicts exactly. No count, N2800/N3000 or period252 is assumed. The 1–900 scan includes 252 but does not shortlist it.

## Pattern-guided investigation and proposed color corrections

The partial motif directs inspection, but does not automatically turn a conflict into an error. A separate appearance audit uses RGB quantiles in radius-8/12/16 neighborhoods and 15/31/51 nearest appearance examples from other sections. It uses original noisy color labels, not proposed motif labels. It excludes the target section from training. Votes remain uncalibrated and correlated across settings; neighborhood measurements are not physical bead centers or complete body boundaries.

The strict rule, ≥80% vote in **every** setting plus independent-section motif agreement, produces zero jointly supported corrections. An explicitly exploratory tier requires the same winning color in all nine controls, a minimum vote ≥55%, mean vote ≥75%, and ≥3-section motif support. This yields six reversible red→black hypotheses:

| Observation | Original `(x,y)` | A index | Residue208 |
|---|---|---:|---:|
| NEW-1706-342 | (1705.088,343.122) | 124 | 124 |
| E5-2306-2092 | (2305.636,2091.818) | 695 | 71 |
| E5-1616-2970 | (1616.857,2970.857) | 1036 | 204 |
| E5-1111-2848 | (1111.000,2846.000) | 1212 | 172 |
| E5-1360-1455 | (1361.333,1455.667) | 1857 | 193 |
| E7-0290-1001 | (288.833,1001.667) | 2333 | 45 |

The matched review shows each original crop, shared primitive links and unchanged support/index labels. Reddish specular material on a dark bead is a plausible cause of these original red classifications. The photograph was inspected, but there is no new independent human annotation dataset. The hypothesis overlay changes colors only, with no index or geometry adjustment.

Training the motif with these six hypotheses improves prediction on the remaining unchanged observations by about .0078 nats at 104 and .0062 at 208. This is **feedback consistency, not independent confirmation**, because the proposals were partly pattern-selected. Original strict results and failed attempts remain archived.

Ranked regions for further work:

1. **G, upper row near NEW-1621/P5-1645:** independent local geometric preference conflicts with broad pattern evidence. Highest-priority indexing/row ambiguity.
2. **Six listed color sites:** coherent pattern-plus-appearance evidence; most promising reversible classification improvements.
3. **Outer/lower cluster near NEW-2186-2343, NEW-2199-2298, NEW-2257-2004 and NEW-2259-1961:** motif favors black, appearance controls are mixed or favor red. Color substitution, support association and pattern error remain competing explanations; no correction.
4. **H, C-1144-2947 and adjacent lower continuation:** omitted association is localized to parent-candidate membership; expanded references favor working overall but remain model-sensitive.
5. **NEW-1519-2976 / NEW-1927-2829:** red→yellow and black→red motif suggestions respectively; appearance controls vary with neighborhood. Preserve uncertainty.
6. **F, frozen-model upper colored regions:** registration explains part, but not all, of material mismatch; physical geometry/correspondence unresolved.

Every cross-section disagreement, including weaker ones, is in the [machine-readable refinement](r330/refinement/refinement.json.gz) and [CSV](r330/review/suspects.csv), with IDs, xy, proposed indices and ±1/±6/±7 alternatives. Uncertain motif positions are not labeled reconstruction failures.

## G — shorter coherent alternatives, and why they are not adopted

Expanded shared colored anchors preserve the local alternative preference for the first three targets. With 11 common references and quadratic fitting, working errors for P5-1645, C-1669, NEW-1697 and E5-1671 are 21.41/21.21/20.28/28.60 pixels; alternative 9.10/9.51/10.01/24.84. Wider cohorts improve the fourth working prediction and can reverse that target's preference. These are partial-pigment extrapolations, not calibrated physical deformation fits.

Require the early alternative's relative assignments for the first black support and those four colored targets, retain the original prefix through window9, then search only windows10–35 using existing connected patches. Width32 finds 12 distinct complete maps; width128 finds 44. Original suffix attachments and all 17 returns are actually replayed.

The earliest reconnection uses **windows10–14**, yielding H=(214,200). Thus G's local advantage does **not** require adopting the historical H=(214,176) path. The best photographic-score candidate changes 833 coordinates and introduces 394 observations whose recorded-color probability falls by more than .2 under an externally section-trained 208 motif; mean log change is −.5135. This is a substantial diagnostic conflict, not proof of physical incorrectness.

Three complete candidates retain H=(214,201). The best pattern-preserving one reconnects after window26, changes 60 observations, and still loses .0434 nats/observation compared with the working map. These transferred-motif comparisons alone could unfairly penalize a candidate's changed phase. A further control therefore **refits the motif separately on each candidate map**, excluding each test section, with a common 900-observation target cohort; absent candidate indices receive the frequency baseline, and additional observations are listed separately. The best photographic G candidate scores .6474 nats, the best same-winding G candidate .7251, versus working .8260. Thus the conflict survives own-map refitting, not just transfer of the original motif. None has established a joint photographic/pattern improvement, so no tracker correction is adopted. All candidate states remain separate and reproducible.

The historical early alternative has unchanged `a` and `b` differences covering every integer 0 through −25: 67 observations agree, 103 occupy intermediate offsets, and 730 retain −25. Final offsets are −150 in A / −175 in B. This is a sequence of row-coordinate changes across windows10–34, **not one constant early index offset**. It does not prove 25 physical mistakes; alternative local basis choices can generate the staircase.

## H — missing association audited and bounded repairs replayed

C-1144-2947 appears in 80 nearby parent hypotheses, but in none of the four selected lower-alternative parents at windows79–82. It was not merely lost during component extraction. There are 73 single-patch reinsertion attempts; all fail attachment. Joint four-window search produces 81 complete candidates with the observation restored: 73 H=(214,201), six H=(213,202), two H=(213,201). The latter two require other assignment/coverage changes; simply appending the missing observation is not valid.

Expanded measurement coverage resolves the earlier quadratic rank deficiency. At the widest tested cohort there are 11 fixed shared colored references. Baseline quadratic target errors working/lower are: C-1125 4.20/23.56, C-1119 13.44/21.74, C-1098 8.79/17.28, NEW-1074 15.01/15.52 pixels. The omitted observation's working prediction misses 1.84 pixels. Affine tests favor working throughout the expanded contexts. The intermediate nine-anchor quadratic fit instead favors the alternative on some targets; its working errors reach 47 pixels. This failure is retained, not averaged away.

The original working assignment remains the stronger current interpretation; the omitted lower alternative is now better diagnosed and repairable as a candidate, but is not independently disproved or adopted. Pattern predictions are supplementary and never replace the conflicting geometric controls.

## F — registration versus correspondence, bounded material test

Reuse R329's actual visible-body raster with all 3000 frozen model bodies. Test common 2D translations on a ±12px, 2px grid, address shifts −7…+7, and their combinations. Each colored region retains its actual measured pigment pixels. Fit a shared configuration only at the index-zero yellow reference, and inspect transfer to two other colored targets.

Reference-only registration selects `(dx,dy)=(8,−4)` with no address change. Coverage rises from **59.33/39.41/20.16%** to **99.08/49.13/49.44%** for reference/C-1391/C-1422. Address change alone selects zero and makes no improvement. Thus a shared translation explains much of the reference mismatch but leaves roughly half the other measured colored material outside assigned bodies. This bounded test weakens a pure shared-translation explanation; it does not distinguish all geometry, projection, occlusion and correspondence errors. Translated image footprints are not a new physical fit or collision certificate. No black highlight is used as a body-center measurement, and no exact first physical error is claimed.

## E — regression retained, extension limited

The established colored-row test still accepts the working single-family bridge and rejects the closest alternative's mixed-family bridge. Its original 0.55–9.08 versus 24.43–32.60px ranges are preserved. Period calculations never override that diagnostic.

An automatic extension tests 155 distinct changed colored bridges using same-family references shared by both candidate maps and excluding the target. Three locality widths produce 39 working-only family matches, 28 alternative-only, two matching both, 20 matching neither, and 66 unresolved family classifications. This demonstrates that similar issues occur beyond E, but also exposes reference/curvature sensitivity. It uses baseline pigment extraction rather than E's complete mask sensitivity suite and is **not deployed as a universal growth filter**.

## Controlled errors on real extracted data

No synthetic images or fabricated bracelet sequence is generated. Ten seeded repetitions corrupt copies of the actual sparse 900-observation sequence. “Recovered” means restored to its original extracted label/index, which itself may be wrong. In the index-burst tests, the motif is trained outside the known injected region; this is an easier diagnostic than jointly discovering an unknown pattern and unknown error location. The decoder still has to locate and estimate the offset from emissions.

| Perturbation | Result |
|---|---|
| 9 substitutions (1%) | 161/161 well-supported reference motif entries retained in every run; 76/90 injected labels recovered |
| 27 substitutions (3%) | 159–161/161 entries retained; 238/270 labels recovered |
| 54 substitutions (6%) | 158–161/161 entries retained; 471/540 labels recovered |
| Sustained +1 shift | At penalty6, 575/575 affected observations restored across ten bursts |
| Sustained +6 shift | 545/575 restored; no false shifts outside the imposed bursts |
| Sustained +7 shift | 565/575 restored; no false shifts outside the imposed bursts |
| One isolated +1 index error | 0/10 restored at penalty6; the regional model refuses such small changes |
| Color-only burst | All ten runs infer shifts at penalty6: a demonstrated confounding failure |
| Observations withheld in a burst | No inferred shifts at penalty6; no physical deletion is invented |

For substitution tests, even the unperturbed reference motif could recover only 84/90, 254/270 and 522/540 of those randomly selected original labels, respectively. The method must not be credited with correcting errors it never had sufficient baseline evidence to identify. Stronger alignment penalties reduce recovery of some +6/+7 bursts. No shift is proposed on the primary period104 map at any tested penalty.

## Verification, cost and remaining limits

[Independent verification](r330/verification.json) checks source hashes and historical preservation, target-section exclusion, count/origin/reversal arithmetic, a separately coded Viterbi recurrence, every new complete path's attachment/return equations, actual frozen-raster coverage trials and exact original-photo crops. [Browser verification](r330/review/browser-verification.json) covers desktop, narrow layout, local links, overlays and offline rendering. These are numerical/provenance checks, not photographic truth certification.

Successful initial pattern scan and conditional controls take 8.87 seconds; the global 19-null search takes 79.95 seconds. The successful G widths32/128 take 12.43/46.84 seconds; full photographic diagnostics 63.06 seconds. Refinement and 210 perturbation records take under one second after imports. These are cached-data timings, not detector or renderer speedups. Earlier G runs totaling 60.55 seconds encountered an export-only NumPy integer serialization failure; the repeated search and failed source/output are retained. Refinement export failures and the strict zero-correction epoch are also preserved. No failed output feeds later inference.

The hypotheses are useful progress: a predictive partial motif, plausible color mistakes, much shorter coherent G alternatives, a specific H omission mechanism, a partial F registration explanation and an intact E regression. They do not establish the final full pattern, bead count, globally correct indices or physical reconstruction. Long motifs, weak black evidence, correlated photo measurements, selected parent topology, local extrapolation, observational duplicates and hidden positions remain limitations. No automatic next round is authorized by this report.
