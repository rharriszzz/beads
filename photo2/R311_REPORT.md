# R311 — broader existing-global basins

**The broader search found missed basins with strong first-error repairs and partial whole-necklace gains. No finalist provides a substantial improvement across the whole circuit; no adoption.** No new bead geometry, local correction or Phase 3 was introduced.

[Photographic review](review/r311/index.html) · [Response maps](review/r311/maps.html) · [Full technical account](R311_DETAILS.md) · [Reproduce](R311_REPRODUCE.md).

The strongest partial candidate is **R306-2733-first-errors (trial 663)**: first-error coverage reaches **85.9/81.4%**, reflection RMS improves **0.240→0.231D**, ownership **61.18→61.92%**, and paper occupation **4.52→4.41%**. However, boundary RMS worsens **6.04→6.76px**, and section 13 loses **18.9 ownership points**. This is a promising missed basin with a measured global tradeoff, not a completed repair. [Full partial-result ledger](r311/results/campaign/partial-basin.json).

## Actual versus allowed coverage

The audit reads **6,075 archived trials**. R306 had 1,082 structural screens without optical evaluation; R307/R308 concentrated on small neighborhoods. R309 used **58 shared trials**, omitted the unchanged R297 anchor as a principal start, and rejected all **41 coupled derivative blocks** at its all-column gate. R307 had 355/884 derivative sides with additional missing lobes; R308 had 233/290 and 23 unavailable columns. These are overlapping diagnostics, not exclusive rejection counts. Exact repeats, starts, discrete families, bound/contact rejections and optical sampling are in the [audit](r311/results/audit/coverage.json) and [per-family ranges](r311/results/audit/ranges.csv).

Exact physical intervals are unknown for most globals: positive dimensions/scale, camera above the plane, periodic angles, construction twist and joint contact/camera validity are the real constraints. The finite boxes below are engineering controls. Union endpoints do not imply joint coverage. Historical phase endpoints are saved unwrapped scalars; phase is periodic and wrapped in the plots. Units: phase radians; elevation/roll/tilt degrees; minor world units; scale px/world unit; axial is an affine multiplier with H/D=.7×axial. Registration s0 is scaled world arclength, not a fixed 2D image translation.

| Global | R306–R309 actual union | Earlier numerical box | R311 attempted union | R311 finite box |
|---|---|---|---|---|
| phase | -2.929…5.587 | [-3.141592653589793, 3.141592653589793] | -3.120…3.100 | [-3.141592653589793, 3.141592653589793] |
| s0 | -12.000…18.716 | [-40, 40] | -40.000…41.238 | [-40.0, 40.0] |
| elevation | 51.319…79.708 | [40, 88] | 30.000…88.000 | [20.0, 89.5] |
| roll | 0.000…40.183 | [-70, 70] | -70.000…70.000 | [-90.0, 90.0] |
| tilt | -5.604…2.750 | [-12, 12] | -30.000…30.000 | [-45.0, 45.0] |
| minor | 3.845…4.485 | [3.5, 5.4] | 3.000…6.000 | [2.5, 6.5] |
| scale | 8.238…9.198 | [7, 10.5] | 6.500…11.000 | [5.5, 12.0] |
| axial | 0.775…1.000 | [0.45, 1.12] | 0.451…1.225 | [0.3, 1.4] |

The search preserves R297's original placement and inherited fields, alongside R306-primary and 2733; R309 and both hand-plus/topology controls remain distinct. Counts, winding, shared light, perspective and all inherited correction fields stay frozen. Closed principal phase uses N/winding; R297 retains its legacy turn correction. Untested combinations of these frozen quantities remain a limitation.

## Response maps and basins

Executed **911 unique vectors**, **562 certified feasible**, in **50.10 search minutes** (initial 40 min plus contingent at most 10 min). Trial types:`{'basin-sobol': 155, 'map': 464, 'refine': 128, 'sobol': 158, 'start': 6}`. Bounds/penetration/unresolved/numerical outcomes:`{'bounds-rejected': 2, 'feasible': 562, 'unresolved-separation': 15, 'witnessed-penetration': 332}`. Broad schedule:639/849 slots; skipped exact repeated evaluations:11. Audit, preflight, recovery and final verification are separately timed.

Five broad pairs, scrambled four-variable Sobol sampling, adaptive pair subdivision and basin-centered four-variable sampling evaluate distant joint proposals directly. No derivative or missing-highlight veto gates discovery. Red crosses witness penetration; orange marks are unresolved contact checks; blank cells are untested. Feasible but photographically poor models remain scored.

| Pair | Evaluated planned cells (three principal starts) | Certified feasible |
|---|---:|---:|
| phase/s0 | 84/105 | 72 |
| phase/elevation | 111/147 | 66 |
| roll/elevation | 106/147 | 62 |
| minor/scale | 104/147 | 39 |
| tilt/elevation | 75/105 | 19 |

| Distinct finalist basin | Count / hand / topology | Changed globals relative to its parent | Complete contact certificate |
|---|---|---|---|
| R306-2405-global (trial 796) | 2405 / -1 / open | phase=-1.509 (Δ-1.722); s0=8.900 (Δ+3.184); elevation=56.184 (Δ-4.224); roll=-43.795 (Δ-74.978); tilt=0.336 (Δ+0.349); minor=4.071 (Δ-0.094); scale=8.670 (Δ-0.049); axial=0.930 (Δ+0.086) | 7143 pairs; minimum margin 0.034371units |
| R306-2405-first-errors (trial 163) | 2405 / -1 / open | phase=-1.582 (Δ-1.795); s0=20.000 (Δ+14.284) | 7166 pairs; minimum margin 0.277093units |
| R306-2733-global (trial 43) | 2733 / -1 / closed | minor=4.000 (Δ-0.203); scale=9.500 (Δ+1.095) | 8199 pairs; minimum margin 0.007235units |
| R306-2733-first-errors (trial 663) | 2733 / -1 / closed | phase=0.144 (Δ-2.301); s0=33.771 (Δ+33.771); elevation=55.467 (Δ+2.147); roll=-52.359 (Δ-76.654) | 8190 pairs; minimum margin 0.067869units |
| R309-2733-global (trial 750) | 2733 / -1 / closed | minor=4.078 (Δ-0.125); scale=8.986 (Δ+0.562) | 8199 pairs; minimum margin 0.026550units |
| R309-2733-first-errors (trial 755) | 2733 / -1 / closed | minor=4.328 (Δ+0.125); scale=8.986 (Δ+0.562) | 8199 pairs; minimum margin 0.016844units |
| R306-2204-plus-closed-global (trial 690) | 2204 / 1 / closed | tilt=7.500 (Δ+7.500) | 5623 pairs; minimum margin 0.253738units |
| R306-2204-plus-closed-first-errors (trial 691) | 2204 / 1 / closed | elevation=67.129 (Δ+5.000); tilt=7.500 (Δ+7.500) | 6087 pairs; minimum margin 0.183658units |
| R306-2002-plus-open-first-errors (trial 696) | 2002 / 1 / open | s0=14.250 (Δ+10.000) | 3912 pairs; minimum margin 0.374385units |

[All vectors and outcomes](r311/results/campaign/trial-vectors.csv), [basin ledger](r311/results/campaign/basins.json) and [four-variable maps](review/r311/basin-multivariate.png) retain the failed alternatives. Discrete sampled components/minima do not prove isolated continuous basins.

## First positioning discrepancies

A pure phase/registration move (trial 163) repairs negative overlap **31.7→81.0%**, positive **79.0→98.8%**, and reference **80.2→97.7%**. Its whole-development score is **+7.9%** (worse). Thus an earlier search missed a locally promising joint basin; this alone is not a global repair. [Native before/after](r311/evidence/phase-registration-example.png).

| Model | Reference visible% | Negative visible / best isolated% | Positive visible / best isolated% |
|---|---:|---:|---:|
| R297-2337-baseline | 94.7 | 85.7 / 85.7 | 96.6 / 96.9 |
| R306-2405-baseline | 80.2 | 31.7 / 46.5 | 79.0 / 94.0 |
| R306-2405-global | 39.7 | 76.1 / 84.5 | 92.5 / 98.8 |
| R306-2405-first-errors | 97.7 | 81.0 / 81.0 | 98.8 / 100.0 |
| R306-2733-baseline | 92.1 | 67.6 / 67.6 | 36.5 / 98.6 |
| R306-2733-global | 97.7 | 73.0 / 73.0 | 52.7 / 99.3 |
| R306-2733-first-errors | 89.8 | 85.9 / 85.9 | 81.4 / 81.4 |
| R309-2733-baseline | 92.6 | 70.4 / 70.4 | 35.7 / 100.0 |
| R309-2733-global | 95.7 | 74.2 / 74.2 | 43.2 / 100.0 |
| R309-2733-first-errors | 95.2 | 70.2 / 70.2 | 48.6 / 96.9 |
| R306-2204-plus-closed-global | 87.5 | 46.0 / 46.0 | 97.6 / 97.6 |
| R306-2204-plus-closed-first-errors | 92.4 | 58.2 / 58.2 | 97.8 / 99.8 |
| R306-2002-plus-open-first-errors | 88.5 | 81.2 / 81.2 | 31.4 / 65.7 |

All six original interiors, competing owners, isolated overlap, resolved occlusion/unknowns and adjacent conditional ±1/6/7 bodies are retained in the review. No photographic physical centers or verified index chain are invented. Patch-directed finalists preserve the trusted reference and stay within 15% of baseline whole-development score; every proposal still describes the entire necklace.

## Whole-necklace comparison

Fixed **D=36.878px**, R309's B14 reference with conservative ±6px uncertainty, is not a measured largest bead. Interior percentages average regions; paper/omission average regional frozen cues. Boundaries use complete native exteriors against 16 uncertain observed contours. All 811 catalog observations survive. First-error targets intentionally enter search even in old comparison geography; later dense comparison is retrospective and partly exposed, not a fresh holdout. [Exposure ledger](r311/results/campaign/exposure.json).

| Model | Reflection RMS / P95 / max(D) | Boundary RMS / max(D) | Interiors% | Paper / color omission% | Missing strong | Fixed-owner penalized RMS(D) / missing |
|---|---|---|---:|---|---:|---|
| R297-2337-baseline | 0.276 / 0.416 / 0.681 | 0.208 / 0.519 | 65.47 | 2.69 / 33.98 | 0 | 0.276 / 0 |
| R306-2405-baseline | 0.247 / 0.383 / 0.486 | 0.135 / 0.353 | 59.98 | 6.84 / 29.94 | 0 | 0.247 / 0 |
| R306-2405-global | 0.251 / 0.398 / 0.481 | 0.202 / 0.513 | 64.63 | 5.88 / 28.43 | 0 | 3.454 / 58 |
| R306-2405-first-errors | 0.253 / 0.390 / 0.461 | 0.170 / 0.451 | 59.91 | 7.08 / 29.92 | 0 | 1.229 / 53 |
| R306-2733-baseline | 0.240 / 0.379 / 0.603 | 0.164 / 0.444 | 61.18 | 4.52 / 31.72 | 0 | 0.240 / 0 |
| R306-2733-global | 0.265 / 0.411 / 0.612 | 0.189 / 0.522 | 65.41 | 10.08 / 24.57 | 0 | 0.493 / 29 |
| R306-2733-first-errors | 0.231 / 0.363 / 0.619 | 0.183 / 0.444 | 61.92 | 4.41 / 30.38 | 0 | 5.602 / 66 |
| R309-2733-baseline | 0.243 / 0.382 / 0.614 | 0.166 / 0.444 | 61.95 | 4.54 / 30.84 | 0 | 0.243 / 0 |
| R309-2733-global | 0.255 / 0.402 / 0.662 | 0.178 / 0.490 | 64.45 | 6.98 / 27.14 | 0 | 0.391 / 15 |
| R309-2733-first-errors | 0.264 / 0.408 / 0.558 | 0.189 / 0.522 | 64.03 | 9.86 / 25.02 | 0 | 0.402 / 15 |
| R306-2204-plus-closed-global | 0.286 / 0.438 / 0.524 | 0.183 / 0.584 | 56.93 | 7.64 / 31.18 | 0 | 0.344 / 6 |
| R306-2204-plus-closed-first-errors | 0.282 / 0.425 / 0.515 | 0.204 / 0.500 | 57.83 | 7.67 / 31.64 | 0 | 0.761 / 25 |
| R306-2002-plus-open-first-errors | 0.286 / 0.460 / 0.553 | 0.202 / 0.531 | 55.88 | 7.24 / 34.79 | 0 | 0.432 / 5 |

Fixed controls retain each family's original conditional owners, with 48px missing-lobe penalties. Reassignment alone cannot improve unchanged native material placement; raw fixed-index regression also cannot, by itself, disprove better geometry when identities are unverified. [Every component/gate](r311/results/campaign/acceptance.json), [dense residuals](r311/results/campaign/metrics/) and [regional outcomes](review/r311/regional-outcomes.png) expose the tradeoffs. Combined passes:0; material/photographic passes excluding the raw fixed-index control:0.

Earlier mechanisms were restrictive; R311 demonstrates wider coverage and a real local repair under the existing geometry. The tested global outcomes above decide whether it extends to the necklace. A negative result remains limited by finite sampling, frozen fields/light/turn and discrete hypotheses; it is not proof that new physical geometry is necessary.

## Verified delivery and stop

Five contracts include real SIGTERM/resume and orphan-trial recovery. Original-Python replay verifies **36566 positions, 102635 contact witnesses, 560584 native rays, 338795 optical rays and 2040274 boundary segments**. Frozen fields, complete boundary edges, viewer/native owners, raw pixels and 20668 prior tracked files pass. [Scientific receipt](r311/results/campaign/verification.json); browser/remote receipts are separate.

**Stop for maker review.** No adoption, new geometry, local correction, Phase 3 or automatic R312. Review the local/global tradeoff and untested coverage before another experiment. Keep the current model/session; no `/new` is needed.
