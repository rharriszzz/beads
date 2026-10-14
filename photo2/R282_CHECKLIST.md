# R282 requirement traceability checklist

Specification: [R282_SPECIFICATION.md](R282_SPECIFICATION.md). Written before code.
Status records delivery of implementation/evaluation, not proof of scientific success.

| ID | Requirement | Status | Implementation | Tests/results/review |
|---|---|---|---|---|
| G1 | Actual three-phase pipeline, all exercised before tuning | Delivered | [implementation](r282/run.py) | [evidence](r282/first-pass/pipeline-complete.json) — All three executed before repairs; final37-file exact replay |
| G2 | Phase independence and immutable provenance | Delivered | [implementation](r282/common.py) | [evidence](r282/results/audit.json) — 2519 immutable measurement links; Phase3 upstream hashes |
| G3 | Shared record: all requested metadata and uncertainty | Delivered | [implementation](r282/common.py) | [evidence](r282/tests.py) — Required metadata on1092 observations/8500 physical records |
| G4 | Real-photo/easy-central priority; no manual labeling | Delivered | [implementation](r282/phase1.py) | [evidence](review/r282/phase1-cases.json) — Six real-photo cases; no manual labeling or absent-world experiment |
| P1.1 | Photograph-only, many reliable detections | Implemented; accuracy unverified | [implementation](r282/phase1.py) | [evidence](r282/results/phase1-summary.json) — 692 high/31 medium; heuristic reliability, not calibrated precision |
| P1.2 | Centerline/near-centerline coverage and retained gaps | Measured; completeness unmet | [implementation](r282/phase1.py) | [evidence](review/r282/phase1-gaps.png) — 96.39% station proximity; remaining gaps retained |
| P1.3 | Yellow wandering/nearly split support explicitly repaired | Repair demonstrated locally | [implementation](r282/phase1.py) | [evidence](review/r282/C-0603-1587-attempts.png) — A bridges neighbors; C374px connected/solidity.959 |
| P1.4 | Several A/B/C repairs on yellow, black and red cases | Delivered | [implementation](r282/review.py) | [evidence](review/r282/phase1-cases.json) — Six cases, A/B/C plus raw/enlarged/baseline/first pass |
| P1.5 | Separate black logic: dark body/enclosure and reflection ownership | Implemented; ownership uncertain | [implementation](r282/phase1.py) | [evidence](review/r282/K-0603-1624-attempts.png) — Dark collar/enclosure;140 high and122 unresolved black |
| P1.6 | Compact native masks, centroids, raw/enlarged comparisons | Delivered | [implementation](r282/common.py) | [evidence](r282/results/audit.json) — 1085 exact connected masks/centroids; raw PNGs |
| P1.7 | High/medium/unresolved/rejected counts and reasons | Delivered | [implementation](r282/phase1.py) | [evidence](r282/results/phase1.json.gz) — 692 high/31 medium/352 unresolved/17 rejected with reasons |
| P1.8 | Easy and problematic before/after tests; no completeness claim | Delivered; limitations retained | [implementation](r282/tests.py) | [evidence](review/r282/index.html) — Named difficult cases plus automatic easy cases; no completeness claim |
| P2.1 | Physical model fitted to reliable anchors; distinct centers | Implemented; fits weak | [implementation](r282/phase2.py) | [evidence](r282/results/phase2.json) — 692 anchors,180 optimization/177 heldout; three center types separate |
| P2.2 | Competing total counts/hands, physical validity, alternatives | Delivered; no unique answer | [implementation](r282/geometry.py) | [evidence](r282/results/phase2.json) — Ten count/hand fits, nine certified; four complete exports |
| P2.3 | Shared-light/specular-side sanity, not sole identity cue | Tested; poor agreement | [implementation](r282/phase2.py) | [evidence](r282/results/N1950-h-1-light.json) — Shared train-fitted light; wrong owners and angular errors retained |
| P2.4 | Every-bead visibility/occlusion and image-derived color | Delivered conditionally | [implementation](r282/phase2.py) | [evidence](r282/results/N1950-h-1-inventory.json.gz) — Every physical bead; first-hit visibility and image RGB sampling |
| P2.5 | Invisible=0; black/dim/ambiguous reliability handled | Delivered conditionally | [implementation](r282/phase2.py) | [evidence](r282/tests.py) — Invisible unknown/zero; unreflected black low confidence |
| P2.6 | Full model inventories, Phase1 links and identity uncertainty | Delivered; identity uncertain | [implementation](r282/phase2.py) | [evidence](r282/results/audit.json) — 8500 records/four alternatives;2519 unchanged links |
| P2.7 | Fit/support/color tests; good and uncertain photo examples | Delivered; mismatch visible | [implementation](r282/pov.py) | [evidence](review/r282/N1950-h-1-examples.png) — Native examples and independent POV appearance/geometry checks |
| P3.1 | Weighted pattern candidates from Phase2 only | Delivered | [implementation](r282/phase3.py) | [evidence](r282/results/phase3.json) — Visibility × color × identity weights |
| P3.2 | More than3 full repeats, no partial repeat: exact divisor rule | Delivered | [implementation](r282/phase3.py) | [evidence](r282/tests.py) — Exact N%L=0 and N/L>=4;112 saved period cases audited |
| P3.3 | Leading alternatives, unknowns, conflicts, failed candidates | Delivered; no accepted pattern | [implementation](r282/phase3.py) | [evidence](r282/results/N1950-h-1-patterns.json) — All candidates, unknowns, exclusion reasons and conflict witnesses |
| P3.4 | Sensitivity to uncertain beads/count/hand | Delivered; unstable | [implementation](r282/phase3.py) | [evidence](r282/results/phase3.json) — Strict subset changes leaders; count/hand alternatives retained |
| P3.5 | Pattern tests and sequence views; no upstream contamination | Delivered | [implementation](r282/tests.py) | [evidence](review/r282/N1950-h-1-patterns.png) — Known-pattern regression, uncertainty and upstream hash assertions |
| V1 | Compact static phase1/2/3 picture review and optional viewer | Delivered | [implementation](r282/review.py) | [evidence](r282/results/browser-check.json) — 22 rendered panels; six raw/enlarged A/B/C cases |
| V2 | Preserve failures/prior evidence; hashes and reproduction | Delivered | [implementation](r282/audit.py) | [evidence](r282/README.md) — 8916 old files exact; both earlier integrated runs and failed attempts retained |
| D1 | Final report/checklist/plan/log/handoff/methods | Delivered | [implementation](R282_INTEGRATED.md) | [evidence](../SESSION_HANDOFF.md) — Report/checklist/log/plan/handoff/methods updated |
| D2 | Scoped commit/push, remote verification, bounded next task | Delivery commit; remote checked after push | [implementation](r282/README.md) | [evidence](R282_INTEGRATED.md) — Scoped branch photo-2-strategy-v3; stop after delivery; next bounded task recorded |
