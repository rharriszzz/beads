# R327 — photographic working choices with correction and rollback

**The selected working reconstruction has 893 indexed supports, 1837 links and 2 components.** Relative to R326 it adds 10 links and withdraws 6; every old candidate and decision remains available. Alternative affine fits are no longer automatic vetoes. The independent reference remains **25/25 interior associations, 45/45 interior links, zero wrong**, and 33/40 associations / 65/86 links overall. No whole-circuit accuracy gain or physical bead count is established.

[Native-photo review](r327/results/index.html) · [Shared-geometry correction](r327/results/shared-shape-review.html) · [Reproduce](R327_REPRODUCE.md) · [Working graph](r327/results/graph.json.gz) · [Independent reference subset](r327/results/established-subset.json) · [Reversible decision ledger](r327/results/decision-ledger.json.gz).

## Concrete working decisions

The upper bridge retains its R326 connections. The inward bend restores working continuations through **K-1740-1575**, including links to C-1721-1566 and C-1770-1577. The six new inward-bend relations and four links through C-1977-2780 compete in one compatible whole-window configuration. Six old links are withdrawn, including three through NEW-1681-1498. Their old assignments, alternative predictions, neighboring evidence for and against the change, and rollback configurations remain in the ledger.

Across the 16 added/withdrawn decisions, **11 have closer endpoint cross-predictions**, **three trade worse local prediction for neighboring support/global compatibility**, and **two have little local prediction separation**. The latter five are not described as photographic disproof of the old relation. All 162 retained relations from the historical 174-link dispute set are explicitly working choices. Model disagreement does not exclude them.

The weak black site near **(290,1410)** retains its 22 original pixels, colored-anchor provenance and **three provisional links**. Separate bead, secondary reflection and glare remain explicit alternatives. There are **310 indexed black supports including the provisional site**; no independently confirmed new black bead is claimed. Original observation locations and pixel lists are unchanged.

## What photographic evidence now chooses

The original two-window, foreground and intervening-support gates remain unchanged. No connected-graph target, expected N, maker chart, pattern or fitted 3D model enters selection. Context disagreement has **zero penalty** and remains descriptive.

Each candidate predicts a support from other supports while excluding the target from the fit. Shared affine and regularized curved predictions are evaluated against observed locations and native color/reflection response. Black targets use colored anchors alone whenever six are available. All colors share geometry; the 5/8-pixel sigmas concern support localization, not different bead sizes. This is cross-prediction within a previously discovered candidate bank, **not independent validation**.

Support utility is `0.75 × geometric support + 0.25 × native-response ratio`. All native response maps use the same 3-pixel Gaussian; black uses linear white minimum, red uses red excess, and yellow uses red/green excess over blue. Missing response loses a positive reward; darkness is not proof of absence. Runs of at least four beads receive a capped length reward weighted by the geometric mean of every member's support. Baseline unary is `0.35 × retained discovery score + support sum + 0.35 × run reward`.

**A first working choice exposed a mistake in that objective.** It selected 1,945 links and H=(214,123), including sheared neighbor directions: coordinate fits could explain the same supports while declaring a longer direction to be immediate adjacency. Visual review identified this failure. The entire result, sources, review and diagnostics are preserved under `development/before-shape`.

A shared local shape metric now comes from native colored pigment regions and applies equally to black and colored hypotheses. It softly penalizes declared neighbors longer than the third shortest primitive lattice direction in that metric. No fixed angle, equal spacing, bead radius, or count is imposed; no hypothesis is deleted. The penalty is `assigned_supports/3 × sum(max(0, log(declared_length/third_shortest_length)))`.

A raw-mask audit then caught contamination in R326's inherited broad pigment envelope: neighboring pigment and pink paper could turn it into a crop-shape proxy. That failed mask and native illustration are preserved under `development/broad-pigment-mask`. Final red/yellow chromaticity masks exclude paper and unlike pigment, yielding **613 measured regions / 371616 pigment-pixel records** across 187 local metrics. They remain **partial visible pigment regions**, sometimes including adjoining same-color material, not complete bead contours. The 19-pixel crop and covariance eigenvalue limits 16..100 are declared proxies. [Native mask examples](r327/results/native-pigment-check.png) show exactly what is measured.

The tighter masks preserve the corrected working assignments exactly. The correction returns the working winding to **H=(214,201)** without a count prior. This is a demonstrated correction of an objective/geometry failure, not independent certification of every final neighbor.

## Global selection, refinement and budget

All **3,352 R326 hypotheses** are retained within a final **5,945-hypothesis bank**. The run adds 348 contexts to the archived 778. Lower-bend practice retains 135 indexed supports / 269 links through nine passes, versus R326's final 133 / 264; no independent practice accuracy is claimed.

Thirty full-circuit passes include a solver correction. The inherited cycle cuts included irrelevant shared path prefixes and could exhaust their repair allowance. Minimal conflicting-cycle witnesses improve whole-hypothesis reconsideration while preserving all overlap and winding constraints. Synthetic exact-enumeration and tail-plus-cycle tests pass. Final selection uses **179 whole windows with eight abstentions**; it does not force graph connectivity.

Cyclic max-marginal regrets remain a proposal surrogate. Saved compatible witnesses, R326 and the new proposal compete under a single fixed photographic-plus-overlap objective. The final shared-shape selection compares **34 configurations**; the primary scores **4984.913**, against **4977.689** for R326 under the same final objective. All eight separately pursued lower-bend alternatives also score lower. This is best among tested witnesses, not exhaustive photographic MAP or a calibrated probability.

The initial refinement plus incumbent comparison used **595.921s** of its declared 600-second allowance. The two review-driven shape/mask corrections used **37.338s + 37.408s**, within their separate 120-second allowance. Total measured inference/refinement is **670.667s**. Core peak RSS was 2,073.0 MiB. Diagnostics, browser review and verification are separately timed. Important choices changed near the first budget limit; final mask correction leaves choices unchanged, but overall convergence is not claimed. There remain **587 unmeasured scheduled contexts** across 181 parent windows. The precise remaining schedule is exported; the older graph field `pending_contexts` counts eligible parents at the last pass start.

## Controls and active winding investigation

Final-mask causal controls use the same bank and solver:

| Removed contribution | Added links | Removed links |
|---|---:|---:|
| without_shared_shape | 543 | 438 |
| without_native_response_in_direct_and_sequence_terms | 0 | 4 |

The no-shape control reuses a previously solved identical objective only after checking **every restored unary** against the archived bank. Removing native response removes it from both direct utilities and sequence quality. The unablated control exactly reproduces the final primary. Earlier discovery/sequence controls remain labeled by their broad-mask epoch. None of these selection effects establishes accuracy.

Eight distinct lower-bend hypotheses were forced into compatible whole-window witnesses, with explicit abstentions. Their observed-support predictions, native responses, changed links, conditional counts and mean errors are retained. The final mask leaves the primary states unchanged; all alternative fixed working scores were recomputed under it. Cyclic gaps retain their explicit broad-mask *generation* scope and are not presented as final-mask scores.

| Alternative | Window/state | Conditional H | Final fixed objective | Common-support error, primary → alternative px |
|---|---|---|---:|---:|
| 1 | 74/2 | [] | 4892.872 | 3.676 → 3.765 |
| 2 | 73/2 | [[213, 203]] | 4888.207 | 3.676 → 3.738 |
| 3 | 73/29 | [[214, 201]] | 4956.794 | 3.676 → 3.711 |
| 4 | 74/5 | [] | 4890.008 | 3.675 → 3.743 |
| 5 | 73/24 | [[212, 203]] | 4912.450 | 3.674 → 3.764 |
| 6 | 74/17 | [] | 4892.122 | 3.677 → 3.762 |
| 7 | 74/0 | [[213, 203]] | 4918.589 | 3.676 → 3.751 |
| 8 | 73/6 | [[213, 203]] | 4917.874 | 3.676 → 3.760 |

The strongest alternative scores **4956.794**, below the primary. Different abstentions and correlated contexts prevent treating these errors as independent accuracy comparisons. The working H=(214,201) corresponds conditionally to A=2704/B=2691, with both reversals retained. The two-window link graph still lacks a certified whole-loop winding. **No N is adopted.** Alternatives are available, not unioned into the primary or used to trigger blanket abstention.

## Independent subset, verification and preservation

The independent historical subset contains the **45 recovered recorded interior links**, with the 20 recovered peripheral reference links separate. The other 21 recorded links lack associated endpoints under the fixed rule. R326's 17-link context-consensus mask is not promoted to ground truth. R161 was evaluated after the initial seal and was already exposed before the review-driven correction; this is explicitly continued development, not a fresh blind holdout. No labels enter the shape correction or selection, and the final primary preserves the same reference recovery.

Verification checks all 3352 old hypotheses, 938 observations / 21,203 support pixels, all 1,837 working edges, 533 selected overlap equations, 95,659 cross-prediction records, 16,299 run records, and eight compatible alternatives. Independent augmented least squares and direct native-pixel convolution verify 51 predictions; maximum affine difference is 2.45e-11px. All native pigment pixels, covariances, 187 metrics and primitive-direction penalties are independently recalculated. Target-exclusion, faint-support, shared-geometry, corrupted-sequence, shear and compatibility contracts pass. Native crops and desktop/narrow/offline reviews pass.

Original photograph, R161, R319–R326, earlier science and `beads.pov` remain unchanged. Earlier failed serialization, cycle-search output, first working graph and broad pigment masks remain losslessly available. No 3D fit, physical-model adoption or pattern inference was performed.

**Delivered: one selected reversible working reconstruction, photographic decision evidence, explicit winding alternatives and a separate independently supported subset. Stop for review; no automatic further round.**
