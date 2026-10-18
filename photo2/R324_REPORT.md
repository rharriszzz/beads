# R324 — the complete photographic circuit, conditional charts, and a bounded physical comparison

**Every geographical section was processed. The result is 886 conditionally indexed photographic supports in 25 components, not a solved whole-necklace index chain.** The frozen R161 result remains 25/25 interior beads and 45/45 interior links, with zero wrong interior links. Both requested bridge continuations remain ambiguous after additional context. Frozen physical models disagree with some independently recovered relative relationships. Graph-conditioned fitting yields only small gains; no reconstruction or pattern is adopted.

[Compact original-photo review](r324/results/index.html) · [Reproduce](R324_REPRODUCE.md) · [Full graph](r324/results/graph.json) · [Verification](r324/results/verification.json) · [Physical verification](r324/results/physical-verification.json).

## 1. Whole-circuit coverage

The original 2540×3182 photograph was decoded once for the primary pass. The R250 image-derived spline was regenerated solely as a geographical guide: length 9,235.59px, minimum foreground clearance 33.24px, no guide sample on classified paper. Every one of its 2,000 samples lies within 27.71px of a processed window center. Original-photo inspection confirms coverage of the upper arc, both outer bends, lower loop, inward bend and return. This checks the guide's suitability for window placement, not its accuracy as a physical centerline.

There are **187 ordered, overlapping 200px windows**, with 35px strides at stronger curvature and the requested upper bridge, otherwise 60px. Local frames rotate continuously with the directed image tangent. **186 windows retain joint lattice hypotheses.** Window129, near (1601,1488), fails the reciprocal-triangle test; its observations and neighboring successful regions remain. No enormous whole-image Fourier window was used. Processing does not stop at this failure or at a chart disagreement.

All16 equal-arc geographical sections have processed windows. Exclusive per-section counts, including unresolved supports, appear below and in [coverage/diagnosis](r324/results/analysis.json). This is coverage of the visible rope, not evidence that every physical bead is visible or recognized.

| Arc section | Windows (retained) | Indexed interior | Indexed edge | Unresolved | Links |
|---|---:|---:|---:|---:|---:|
| 00 | 11 (11) | 50 | 10 | 0 | 129 |
| 01 | 12 (12) | 45 | 7 | 4 | 98 |
| 02 | 10 (10) | 48 | 6 | 1 | 109 |
| 03 | 10 (10) | 51 | 3 | 4 | 109 |
| 04 | 9 (9) | 52 | 5 | 0 | 117 |
| 05 | 10 (10) | 50 | 4 | 3 | 109 |
| 06 | 12 (12) | 51 | 13 | 6 | 130 |
| 07 | 13 (13) | 44 | 10 | 7 | 98 |
| 08 | 14 (14) | 45 | 9 | 4 | 110 |
| 09 | 11 (11) | 47 | 14 | 1 | 124 |
| 10 | 16 (16) | 48 | 0 | 4 | 68 |
| 11 | 13 (12) | 48 | 11 | 2 | 110 |
| 12 | 10 (10) | 47 | 10 | 4 | 108 |
| 13 | 16 (16) | 47 | 8 | 6 | 99 |
| 14 | 10 (10) | 45 | 5 | 2 | 101 |
| 15 | 10 (10) | 45 | 8 | 3 | 103 |

Sections start near the upper x1000 region and follow the directed circuit. Observations and links are counted once by nearest guide arc; overlapping window membership is not summed.

## 2. Inventory and photographic graph

| Quantity | Result |
|---|---:|
| Original photographic supports | 937 |
| Conditionally indexed | 886 |
| Indexed interior heuristic / indexed edge | 763 / 123 |
| Unresolved supports | 51 |
| Indexed red / yellow / black | 317 / 262 / 307 |
| F0 / F1 connected fragments | 208 / 218 |
| Accepted conditional links | 1,722 |
| Unresolved candidate links | 140 |
| Disconnected indexed components | 25 |
| Incompatible or insufficient chart transitions | 19 |
| Saved local hypotheses / assignments | 1,115 / 18,746 |

All937 locations retain stable original observation IDs, observed color cues, native supporting pixels, measured location meaning, local hypotheses and alternative rows. Indexed nodes additionally retain component coordinates, both 7a+6b and 6a+7b interpretations, both reversals and diagonal fragments. The 51 unresolved supports remain in the inventory. **A bright-support centroid or a fitted representative grid point is never called a measured physical bead center.** Black reflections receive the inherited larger exploratory location allowance, not exclusion or forced movement. Colors are automatic cues, with inherited and fresh provenance; they are not a solved pattern.

The two families are jointly fitted to several observed supports. Six local candidates compete in a 48-path beam, retaining states within three score units of the retained best path. This is a finite heuristic, not exhaustive posterior inference. Shared IDs establish integer translations. Only fully agreeing credible overlaps with at least four shared observations pass the chart-transition gate. Across failed transitions, nearest-window geographical ownership prevents accepted graph edges from propagating an index. Twelve triangular-lattice symmetries are diagnosed as alternatives; **none is silently applied to make a disagreement disappear**. Global family exchange and reversal remain conditional.

Links retain R323's multi-window voting, foreground and intervening-support checks. Evidence is correlated across overlapping windows. No unsupported crossing manufactures an observation. There are no independent accuracy labels outside R161. The words “confident bead” in the inherited machine schema mean heuristic interior detection, not externally certified identity.

## 3–4. Remaining breaks and the R323 bridge

The 19 failed transitions and all140 unresolved links have exact coordinates and reasons in the graph and coverage map. The inward bend around x1600–1800, y1450–2000 is particularly fragmented. The largest local component contains320 observations; smaller components continue beyond uncertain sections.

The two requested upper-bridge pairs were examined with **21 additional windows**, using sizes160/240/280px, neighboring centers and up to ten alternative local spectral bases. This took5.87s including independent preprocessing. These contexts were chosen before model comparison, not to favor a model prediction.

* `C-1559-0252 → C-1582-0272`: the primary circuit beam accepts (1,0), but additional contexts retain (1,0) and (1,1) within the declared local score allowance. The latter can represent a skipped/changed continuation. **The extra evidence contests the primary beam's confidence; this pair is not resolved.**
* `K-1721-0308 → C-1729-0337`: the primary pass abstains; larger contexts retain several row/skip alternatives, including (1,−1) and (1,0). It also remains unresolved.

The primary frozen graph is preserved rather than retrospectively rewritten. [Bridge alternatives](r324/results/bridge.json) and [conservative-use policy](r324/results/bridge-use-policy.json) accompany it. No accumulated index beyond x1510 is used as a reliable fitting constraint. An initial fitting epoch that included the conditional bridge is archived intact under `development/bridge-conditional-fit`; the delivered fitting results were rerun with that exclusion. Independent unlabelled photographic surface guards beyond the bridge remain active.

## 5–6. Closure and total bead count

The return overlap agrees on14/14 shared observations with translation(0,0). That reconciles two nearby local charts, **not a supported path through the entire necklace**. Nineteen intervening breaks prevent accumulation of one whole-circuit offset. Origins and family choices remain independent across disconnected sections; no bead count was chosen to absorb a conflict.

All861 algebraic graph cycles close, with no accepted contradictory cycle. This is partly enforced by construction and does not certify photographic topology. The exact42 relationship is checked for both assignments: A maps(6,0) and(0,7) to42; B maps(7,0) and(0,6) to42. Those are distinct planar sites and are not merged. No same-index duplicate occurs in either delivered component map. Missing index slots remain unknown, not inferred absence. [Closure ledger](r324/results/closure.json).

**The photograph currently supplies a collection of conditionally well-supported sections, not a whole-circuit relative-index map or N.** Even N is not imposed. Physical count controls are model experiments, not photographic count measurements.

## 7. Frozen R161 accuracy

The detector was frozen before the R324 reference evaluation. The same fixed25-bead/45-link interior partition and all40 beads/86 recorded links were retained.

| Check | R324 |
|---|---:|
| Interior beads associated | 25/25 |
| Recorded interior links recovered | 45/45 |
| Wrong interior automatic links | 0 |
| All maker beads associated | 33/40 |
| All recorded links recovered | 65/86 |
| Unresolved recorded links | 21 |

All33 associated relative coordinates agree after component-origin alignment; maker10 and11→14→16 remain recovered. Sixty-six automatic links agree with recorded or implied R161 coordinates; the other1,656 have unvalidated endpoint identities. This is a runtime data holdout with developer knowledge of prior findings, not developer blindness. The later cache optimization reproduces the entire frozen scientific output exactly. The bridge revisit did not tune against reference scores.

## 8–9. What the frozen models get right and wrong

R319 best-full, R321 geometry-best N3000 and R321 photo-sized-rescue N2800 were reconstructed with unchanged saved parameters and matched their saved centers/projections before any fitting. Every physical body participates in first-hit surface ownership. All21,181 photographic support pixels are traced. Per-component origin, both6/7 assignments and both reversals compete over the model's full address range; competing origins are saved. R319 retains its historical open topology and is not treated as a closed physical solution.

The seed is27 interior observations at x1180–1505, y200–390, selected before model scoring. The reported support fraction measures the portion of each original bright support owned by its assigned modeled bead. It is distinct from whole-body segmentation or reflection agreement.

| Frozen model | Preferred seed interpretation | Mean assigned seed support | +6/+7 links agreeing / disagreeing / unresolved | Seed reflection maximum |
|---|---|---:|---:|---:|
| R319 best | B | 35.7% | 638 / 336 / 291 | 53.297px |
| R321 N3000 | A | 74.8% | 870 / 198 / 197 | 32.523px |
| R321 N2800 | B | 92.3% | 793 / 232 / 240 | 20.059px |

The link counts cover both diagonal families throughout the photograph under separately fitted component gauges; difference links are separately retained. A comparison is called unresolved unless each endpoint has a modeled modal owner covering at least60% of its support. **These are model/photo compatibility counts, not new photographic accuracy measurements.** Mapping an edge algebraically to6/7 is not counted as success by itself: its independently traced model surface owners must have the expected difference. Different component origins can conceal no global closure claim because none is made. The frozen seed renders retain 2/1/0 unresolved shadow pairs for R319/N3000/N2800 respectively, with zero unresolved camera rays; these are not erased from the ledgers.

Representative first contradictions among associated R161 observations, ordered from the mapped photographic reference `C-1497-0271`, are:

* R319, maker37 / `NEW-1442-248`: the coherent map expects−12; modeled−18 owns88.4% of the observed support, while−12 owns11.6%.
* R321 N3000: its best whole-seed compromise already assigns the reference maker39 to−6, while modeled0 owns100% of that support. The alternative origin aligning the reference is retained but fits the full seed worse.
* R321 N2800, maker25 / `C-1391-0312`: expected−33; modeled−34 owns85.7%, while−33 owns14.3%.

These demonstrate disagreement between a fixed relative map and visible placement. They do not uniquely identify a wrong physical bead, shape law or illumination model. Conversely N2800 often covers the assigned support correctly yet still displaces its predicted reflection substantially: optical and ownership errors are separable. Projected-center-to-anchor vectors are shown descriptively and never scored as measured center errors.

Within the strict upper extension, fitted modal-index discrepancy slopes are−13.67, +8.43 and +3.09 addresses per100 assigned addresses respectively. They are conditional descriptive slopes, not measured stitch strain or recovered count. Over the whole circuit, error versus absolute **photographic-guide curvature** has Spearman coefficients +0.140, −0.020 and +0.005. R319's lowest/highest-curvature quartile disagreement fractions are23.5%/43.8%; the R321 models show no consistent curvature concentration. Observations/edges are spatially dependent, and gauges were selected using these same surfaces, so no causal significance claim follows. [Complete discrepancy, drift and curvature ledger](r324/results/analysis.json).

Supported red/yellow interiors, chromatic separators, paper and uncertain exterior brackets from the frozen R314 evidence are also evaluated as separate local guards in fitting. Broader supports have no newly validated complete boundaries; none are invented. Frozen R319/R321 historical boundary ledgers remain unchanged.

## 10. Bounded coupled fitting

The accepted-use epoch uses the closed N2800 R321 construction, a fixed diagonal-derived B map and fixed shared light/camera. Every geometry change rederives the contact radius and checks all physical beads. Variables are radius, axial thickness, phase, longitudinal registration and two small periodic centerline coefficients; there are no independent bead translations or fitted local phase/spacing/tilt fields. Count2799/2801/2700/2900 controls preserve the map and closed winding rule. A uniform-spacing control demonstrates actual penetration, but this does not prove the density law physically correct.

There are **37 saved initial trials and14 expansion trials**, including failures and controls. The two100-address Jacobians and one200-address Jacobian use bilateral measured secants and joint minimax proposals. Six-variable derivatives do not certify an optimum; some centerline columns have very small responses. The initial bridge-conditional51-trial epoch is separately preserved, giving102 audited trial records in total.

| Delivered scope | Consecutive modeled targets | Supported correspondences / reliable reflections | Before / best passing reflection maximum |
|---|---|---:|---:|
| Local expansion | −99…0, exactly100 | 36 / 30 | 20.0592 / 20.0076px |
| Wider expansion | −149…50, exactly200 | 53 / 46 | 28.5579 / 28.5434px |

All2,800 bodies remain in visibility, shadow and nonintersection calculations. Targets without photographic evidence are still modeled; the table does not claim100/200 independently recognized visible beads. Missing reflections make the maximum unavailable/infinite, never favorable.

Passing means explicit **baseline-relative tolerances**, not zero regression or reconstruction acceptance. For100 targets, mean assigned support changes87.689→87.274%; local material omission4.930→4.994%; separator conflict50.0→51.316%; exterior-bracket p954.0→4.2px. These small permitted losses are reported, not hidden inside the reflection objective. The final100-address render also retains two unresolved shadow pairs (zero unresolved camera rays), so its tiny optical gain is a conditional numerical result. The wider support mean changes69.391→69.009%. Larger joint proposals lower the reflection maximum more, but fail individual supports, separators, exterior boundaries or retained100-address constraints. All failures remain.

**The correspondences make previous ambiguity testable, but this bounded experiment does not establish that incorrect assignments were the sole cause of the old optimization stall.** Neither the tiny gains nor a failed six-variable local search establishes model inadequacy. No geometry is adopted.

## 11. Model feedback without circular validation

Each frozen model's modal owner difference at both bridge pairs is exported as a **model-generated hypothesis**, with its support fraction. The previously selected original-photo multiscale windows supply an independent check of those proposals. They remain ambiguous. No model preference changes a photographic coordinate, graph edge, confidence label or color. The original-photo bridge crops are displayed beside the primary graph; the contradictory contexts remain available.

## 12–13. Performance and runtime planning

One numerical thread, serial workloads. Imports, documentation and review rendering are outside primary detector stages.

| Photographic operation | Original / cached seconds |
|---|---:|
| Decode and global fields | 1.639 / 1.600 |
| Support extraction | 9.268 / 2.042 |
| Rotated local spectral analysis | 8.900 / 8.436 |
| Joint hypotheses | 21.642 / 21.242 |
| Beam and transport audit | 1.587 / 1.777 |
| Link photographic checks | 13.040 / 0.103 |
| Total before serialization | **56.446 / 35.570** |

Catalog SHA caching removes repeated file reads; caching the float foreground removes a full-image conversion per link. KD-tree queries replace all-observation corridor scans. Original RGB is decoded/preprocessed once per pass; normalized fields are sampled in rotating windows. The cache control is an exact same-output comparison. Joint hypothesis generation is now dominant. Hypothesis reuse across newly added windows is not yet implemented; no speculative pruning speedup is claimed.

Optimized cost is0.190s/window or0.0380s/recognized support; beam+graph extension on the saved candidate bank is approximately2.04s. The bridge revisit costs5.87s. Primary peak RSS is1,148.7MiB; independent guarded replay including serialization is37.59s. Frozen construction/support/correspondence/native comparisons for all three models take3.29s total; per-model support tracing is0.12–0.14s and discrete gauge search0.38–0.43s.

The native whole-bracelet benchmark exposed another repeated scan: every target traversed the full ray array to find its pixels. Stable grouping by owner reduces the matched evaluation **13.279→8.441s**, reproducing all1,722 visible principal-lobe predictions, every camera owner and intensity exactly. Camera tracing remains the largest cost. The full native timing scene retains97 unresolved shadow pairs and zero unresolved camera rays; exact before/after agreement preserves that uncertainty, rather than certifying every shadow. This is not a comparison to the different R323 task or a claim of faster ray kernels.

Count/radius/axial/centerline/registration changes are individually timed in [runtime-plan.json](r324/results/runtime-plan.json). Every geometry cache key includes all parameters, scope, observations and mapping. Geometry-changing trials have0 cache hits/37 misses. Seven discrete offset controls reuse predictions with7 camera hits/0 misses; unavailable owners outside the rendered target pool remain missing. No stale count/shape cache is reused.

Measured native construction+evaluation costs are approximately0.360s/100,0.708s/200 and8.5s/all after grouping. Actual coupled sensitivity costs, including support and guard work, are about6.7s per12-probe100-address Jacobian and10.7s per12-probe200-address Jacobian. The runtime model uses approximately0.557/0.891/8.692s per coupled evaluation; the full-objective guard overhead is extrapolated from the measured local guard, not independently benchmarked for every possible global objective.

Serial **low / expected / high planning workloads are0.65 / 4.30 / 24.71 hours**, including explicitly assumed1.5/2/3 overhead allowances. The budgets allocate respectively(10,20,10), (50,100,50), and(200,300,200) six-variable iterations to100/200/all-target phases, with14 evaluations per iteration. These iteration counts are user-planning scenarios, **not empirically established evaluations needed for convergence**: only two100-address and one200-address epochs were completed. Wider searches, derivatives, retries and independent validation could cost more. No parallel speedup or multi-hour search was launched.

## 14. Pattern readiness

A color-only exact-repeat scan of periods1…200 was performed on the27-observation reference geography, retaining both assignments and reversals and leaving unknown slots unknown. Period78 survives with only four compared pairs in each interpretation; many other periods have fewer or zero comparisons. Moreover78 conflicts with the recorded maker constraint that the full repeat is not divisible by13. It is therefore **not a supported whole-pattern candidate**. The complete repeat can be longer than this local span. No global N, complete repeat, hidden color completion or pattern-driven graph repair is justified. [Conditional constraints](r324/results/pattern-constraints.json).

## Verification, preservation and stop

Independent arithmetic checks937 supports /21,181 native pixels, all1,115 hypotheses /18,746 assignments, all1,722 accepted links,204 saved triangular-transform alternatives and raw R161 coordinate relations. A read-guarded exact replay accesses only the original photo, R275 appearance catalog and R250 spline seed. The local return seam and42 identity are checked without asserting full closure.

Across both fitting epochs,102 trial records and100 optical cohorts are audited. Independent literal support formulas check386,400 witnesses over47 unique geometries; two retained uniform-spacing penetration witnesses are reconstructed. Original Python camera/shadow paths check840 samples across seven frozen/selected models, and739 original-photo reflection centroids are reconstructed. Numerical correctness does not add independent photographic labels.

All2,311 protected files, including the original photo, `beads.pov`, R161 and all R319–R323 science, match their original Git blobs. Desktop, narrow and offline browser checks pass. The initial source comment correction, serialization failure, verifier adapter failure and superseded conditional-bridge epoch are retained. Scientific proposals are sealed in [scientific-seal.json](r324/results/scientific-seal.json); the requested start was15:46:06UTC, science cutoff16:10:06UTC and delivery deadline16:16:06UTC on2026-10-18. Verification, documentation and delivery retain more than six minutes.

**STOP for scientific review.** Next review the contested upper bridge, the inward-bend breaks and the concrete frozen-model ownership contradictions before authorizing a broader coupled search. No automatic R325, pattern adoption or `beads.pov` change. Keep the user's preferred Astra/High/current session for review; no `/new` is needed.
