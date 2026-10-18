# R327 — reversible photographic working reconstruction

**R327 selects a working reconstruction rather than using alternate affine fits as vetoes.** The delivered primary has **891 indexed supports, 1945 working links and 2 components**. It retains all 938 observations, including the faint black-site hypothesis, and every R326 candidate. There are **549 added and 437 withdrawn links** relative to R326. These are working decisions, not a demonstrated accuracy gain or an established physical lattice.

[Native-photo review](r327/results/index.html) · [Reproduce](R327_REPRODUCE.md) · [Working graph](r327/results/graph.json.gz) · [Independent reference subset](r327/results/established-subset.json) · [Decision ledger](r327/results/decision-ledger.json.gz).

## Evidence and decisions

R326's context-disagreement penalty is removed entirely. Alternate local assignments remain available as **model disagreement**, not photographic contradiction. The original two-window, foreground and intervening-support gates remain unchanged; no connectivity target or count prior is introduced.

For every candidate, each measured support is predicted from other supports, excluding the target from the fit. Affine and regularized curved predictions are both evaluated. Black targets use colored anchors alone when six are available. The same shared geometry applies to all colors; the 5/8-pixel sigmas describe support localization, not different bead sizes. R326's colored-region envelope and faint native support remain available; no complete black silhouette is claimed.

Predictions are tested against measured positions and original RGB. Linear white response supports black reflections; red excess and yellow response support colored beads. All use the same 3-pixel Gaussian. Each support contributes `0.75 × geometric prediction support + 0.25 × native response ratio`. Low response loses a positive reward; darkness does not become proof of absence. Supported sequences of four or more beads contribute a capped length reward multiplied by the geometric mean of every member's evidence. Candidate unary is `0.35 × retained discovery score + support sum + 0.35 × sequence reward`. Weights are declared heuristics, not calibrated likelihoods.

This is **target-excluded cross-prediction**, not independent validation: target observations previously influenced candidate discovery. Repeated windows are correlated. The curved scoring model does not turn the finite affine proposal bank into an exhaustive nonlinear reconstruction.

The [evidence classification](r327/results/evidence-classes.json) distinguishes observed pixels, conditional prediction mismatch, potential intervening support/background, model disagreement, and missing support. No newly established image contradiction is fabricated. Every withdrawn link keeps its old witnesses, competing assignments, target predictions, and the strongest neighboring observations for and against the change. The local endpoint comparisons are:

* selected configuration trades worse local prediction for other supports/global compatibility: **102**.
* little local prediction separation; global compatibility/other supports decide: **776**.
* selected configuration predicts these observed supports more closely: **108**.

A globally selected local loss is explicitly labeled as such. It is not described as evidence that the old link was wrong. Both old and new configurations remain recoverable.

## Refinement and the best working incumbent

Lower-bend practice retains **135 indexed supports / 269 links** through nine refinements, versus R326's final 133 / 264 on that practice region. One hypothesis changes in the last practice pass without changing links. Practice is not an independent accuracy test.

Full refinement preserves **3,352 old hypotheses** and grows to **5945 hypotheses**. It measures **348 new contexts**, retaining 778 old contexts. The initial 20-pass diagnostic is archived. It exposed an inherited compatibility-search weakness: cycle cuts included an irrelevant shared path prefix and repeatedly exhausted their allowance. Minimal conflicting-cycle witnesses and a 24-cut cap allow stronger joint reconsideration without changing photo thresholds or relaxing compatibility. A synthetic tail-plus-cycle test checks that irrelevant prefix windows are absent.

The solver still proposes through cyclic max-marginal regrets; this is a surrogate. To prevent regret changes from discarding a stronger incumbent, **32 saved compatible configurations, including R326, compete under one fixed objective**: native photographic unaries plus the original cyclic overlap/triple factors, with empty windows contributing zero. The selected source is `photo2/r327/results/iteration-29.json.gz`. Its score is **5039.727**, versus **4978.545** for R326 under exactly this objective. Photographic unary increases from 3747.945 to 3817.527; overlap contribution decreases from 1230.600 to 1222.200. This is not a calibrated accuracy measure or exact full-bank MAP.

Pass 29 is retained over pass 30; pass 30 withdrew three links for a lower fixed objective. All chosen assignments have one simultaneous whole-hypothesis witness, with explicit abstentions. The graph is not forced connected. **145/174** historically disputed relations are now retained as working choices; neither agreement nor selection certifies them.

The cumulative adaptive run takes **585.194s**, and fixed-incumbent comparison **10.728s**, totaling **595.921s within the 600-second allowance**. Peak RSS is 2073.0 MiB. Important choices changed near the budget limit; convergence is not claimed. There remain **587 unmeasured scheduled size/shift contexts across 181 parent windows**. The graph's older `pending_contexts` field counts eligible parent windows at the last pass start; the precise remaining schedule is exported separately.

## What the controls establish

These comparisons use the exact same final bank and the same solver. Differences below are against a fresh full-objective proposal, not against a different saved incumbent:

| Removed contribution | Added links | Removed links |
|---|---:|---:|
| discovery_only | 434 | 543 |
| without_native_pixel | 0 | 0 |
| without_sequence | 434 | 543 |
| without_native_response_in_direct_and_sequence_terms | 0 | 0 |

The `without_native_pixel` control removes only the direct pixel unary; the last control also removes native response from sequence quality. This distinction prevents claiming a complete pixel ablation when pixel information remains in another term. Changes caused by selecting the saved incumbent are separately recorded. Sequence weighting has a substantial effect; effect on selections is not proof of higher accuracy.

## Lower-bend winding and black supports

The primary whole-hypothesis witness proposes **H=[[214, 123]]**. The accepted two-window graph and the broader window witness are distinct; neither is declared a uniquely established physical winding. Both 6/7 assignments and reversals remain available, with no N imposed or adopted.

Eight explicit forced lower-bend hypotheses are pursued into compatible whole-window witnesses. Their forcing bonuses are removed from scores. Every changed support carries primary and alternative predicted positions, native responses and errors; the review shows lower-bend overlays and largest prediction changes. Mean errors below compare the same observed IDs, but configurations have different abstentions and correlated contexts, so these are diagnostic consequences, not accuracy rankings.

| Alternative | Window/state | Conditional H | Fixed working objective | Common-support mean error, primary → alternative px | Changed support predictions |
|---|---|---|---:|---:|---:|
| 1 | 73 / 39 | [[212, 127]] | 4917.070 | 3.649 → 3.712 | 62 |
| 2 | 71 / 22 | [[213, 124]] | 4987.260 | 3.653 → 3.678 | 38 |
| 3 | 73 / 37 | [[212, 127]] | 4916.333 | 3.650 → 3.724 | 64 |
| 4 | 73 / 2 | [[213, 127]] | 4891.701 | 3.649 → 3.703 | 63 |
| 5 | 73 / 24 | [[212, 127]] | 4915.943 | 3.648 → 3.731 | 64 |
| 6 | 73 / 6 | [[213, 127]] | 4891.278 | 3.649 → 3.711 | 62 |
| 7 | 74 / 0 | [] | 4925.435 | 3.653 → 3.726 | 63 |
| 8 | 74 / 2 | [] | 4925.142 | 3.653 → 3.732 | 64 |

The strongest tested alternative has objective 4987.260, compared with primary 5039.727. Alternative counts and local continuation choices are kept in [the winding evidence](r327/results/lower-bend-alternatives.json.gz), never unioned into the primary. A different winding is actively evaluated rather than used as an automatic abstention rule.

The weak site near (290,1410) retains its **22 original pixels**, neighboring colored-anchor provenance and separate-bead/secondary-reflection/glare alternatives. The primary includes **3 links involving that provisional site** and **310 indexed black supports in total**. These remain working body-identity hypotheses; independently confirmed new black beads remain zero.

## Independent reference and verification

The working configuration is frozen before R161 evaluation. R161 retains **25/25 interior associations and 45/45 interior recorded links**, with **0 wrong interior links**; overall **33/40 associations and 65/86 links**, with **0 wrong reference links**. This historical reference has been seen during prior development and is not a new blind holdout. The independently recorded interior subset and peripheral reference links are exported separately. R326's 17-link context-consensus mask is not relabeled as established truth. No new independent whole-circuit labels or accuracy gain are claimed.

Verification passes: **3352 preserved old hypotheses**, 938 observations / 21203 native support pixels; 1945 working edges with original gates and simultaneous witnesses; 95659 cross-prediction records; 16299 sequence records; 51 independent augmented-least-squares predictions plus direct original-pixel Gaussian/bilinear checks; and 8 compatible alternatives. Maximum independent affine difference is 2.45e-11px. Meaningful contracts cover target exclusion, curved geometry, colored-only black prediction, weak native response, sequence corruption, exact small compatibility optimization, and minimal cycle cuts. Desktop, narrow, offline and expandable review checks pass.

Counterfactuals/reference analysis take 297.428s; the full same-bank causal control takes 50.851s; independent verification takes 4.493s. These are separately measured diagnostics, not extra candidate-search allowance or a parallel speedup claim. Native crops are exact. Original photograph, R161, R319–R326, all older science and `beads.pov` remain unchanged. The failed initial NumPy-scalar serialization, initial compatibility diagnostic and pre-incumbent continuation are preserved.

**Delivered for review: one selected reversible working reconstruction, explicit alternatives and a separate independent-reference subset. No physical-model fit, pattern adoption, or automatic further round.**
