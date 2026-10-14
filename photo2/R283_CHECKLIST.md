# R283 requirements and evidence

R283 retains the three-phase architecture and all R282 artifacts. Scientific
success is separate from implementation. No additional maker labels are requested.

| Requirement | Implementation/evidence | Status |
|---|---|---|
| Photo-only distinct-body ownership, symmetric conflicts, retained alternatives | [ownership](r283/ownership.py), [pair ledger](r283/results/ownership.json), [native inventory](r283/results/phase1.json.gz) | Implemented; 561 high, all1092 preserved; real precision uncalibrated |
| Attempt C principal; B yellow sensitivity; native masks/stable IDs | [ownership](r283/ownership.py), [pair ledger](r283/results/ownership.json), [native inventory](r283/results/phase1.json.gz) | Implemented; 561 high, all1092 preserved; real precision uncalibrated |
| Independent valid synthetic scenes, precision/recall/duplicates/purity/color/centroids | [benchmark](r283/benchmark.py), [fresh confirmation](r283/results/confirmation-results.json) | Tested: 148/151 pure distinct,148/389 recall;3 mixed-body failures |
| Both sides, support extent/local scale, crossing supports, no station-count census | [coverage](r283/coverage.py), [results](r283/results/coverage.json) | Implemented:323 high near,24 flanking pairs; no completeness claim |
| Automatically explain all eight old gap panels | [eight explanations](r283/results/coverage.json), [pictures](review/r283/index.html) | Delivered; all8 retain unresolved evidence, no demonstrated curve defect |
| Freeze Phase1 before local fitting; easy automatic region | [local fit](r283/local.py), [development](r283/results/local/evaluation.json), [second region](r283/results/local-confirmation/evaluation.json) | Tested; best3/4 then2/4, no accepted identities; all failures retained |
| Both hands, source radius, shared pose, packing and withheld predictions | [local fit](r283/local.py), [development](r283/results/local/evaluation.json), [second region](r283/results/local-confirmation/evaluation.json) | Tested; best3/4 then2/4, no accepted identities; all failures retained |
| Common distant light, yellow-first camera comparison, retained failures | [local fit](r283/local.py), [development](r283/results/local/evaluation.json), [second region](r283/results/local-confirmation/evaluation.json) | Tested; best3/4 then2/4, no accepted identities; all failures retained |
| Integrated inventories, visibility/color/provenance/uncertainty | [integration](r283/integrated.py), [Phase2](r283/results/integrated/phase2.json), [Phase3](r283/results/integrated/phase3.json) | Complete:10 fits,8280 records,2085 unchanged measurement links; no pattern accepted |
| Phase3 exact divisors, four full repeats, maker period rule, no upstream changes | [integration](r283/integrated.py), [Phase2](r283/results/integrated/phase2.json), [Phase3](r283/results/integrated/phase3.json) | Complete:10 fits,8280 records,2085 unchanged measurement links; no pattern accepted |
| Raw photos beside overlays; bottom captions explaining symbols/problems | [review](r283/review.py), [28 captioned panels](review/r283/index.html) | Delivered; original pixels, distinct model edges, preserved A/B/C links |
| Tests, replay, historical hashes, browser | [tests](r283/tests.py), [audit](r283/results/audit.json), [browser](r283/results/browser-check.json) | Verification recorded in linked artifacts; original R282 tests retained |
| Report, handoff, request log, scoped commit/push and remote verification | [report](R283_REPORT.md), [reproduction](r283/README.md), project handoff/log | Scoped delivery; remote verified after push |

## User review decisions (qualitative, not identity ground truth)

Yellow C-0603-1587: B and C good, slight preference for C. Black K-0603-1624:
prefer C. Red C-0565-1588: prefer C. Eight gap pictures: old metric unclear;
replace its explanation and analysis. These IDs are documentation/review only.

## Methods selected before implementation

Ownership compares (1) symmetric shared native material, (2) photo-only
peak/trough separation and reflection connectivity, (3) B/C measurement stability.
Do not merge based on color/distance alone. Retain ambiguous graph edges without
claiming each connected component is one bead. Coverage compares centroid26px
diagnostic, nearest support extent and signed local-scale support relationships.
Local geometry compares cold shared-pose fits, exact support ownership refinement,
and common-light constrained pose ranking; no independent bead movements.
Synthetic seed283501 and fixed rules are saved before held-out rendering.
