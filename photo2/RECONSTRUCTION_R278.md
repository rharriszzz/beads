# R278 — corrected construction, independent inventory and conditional correspondence

**The radius correction resolves the sampled ±1 collision failure, but does not by itself resolve ±6 packing or photographic indexing.** Fourteen new closed-loop candidates have separating-plane witnesses for every possible collision pair. None yet explains substantially every photographed bead. All historical inventories, models and the source photograph remain preserved.

[Whole-photo comparison](review/r278/intended_N2696_h+1_p1.300_f0_tilt-8-overlay.jpg) · [review and reproduction index](review/r278/README.md) · [physical-model table](review/r278/comparison.csv) · [image-only positions](review/r278/phase1-positions.csv)

## Phase 1: photograph only

The frozen inventory has **900 locations and 897 measured interiors**: all 810 R275 locations/807 masks unchanged, plus 90 outside-band proposals (63 black, 23 yellow, 4 red). The target remains 658 locations. No new centerline-target candidate passed the final identity checks. The 63 prior residual peak groups, 12 short station intervals, 24 small colored supports and band-edge cases remain explicitly reviewable; they are not a completeness denominator.

Compared multiscale LoG features, chromatic distance cores, dark enclosure and secondary-highlight continuity. The full-photo search measures 4,200 features and attempts 2,191 native proposals. A failed wide control admitted 425 additions including shadowed paper and weak color fragments. An enclosure-only control retained 117, including dim/transitional doubts. Both survive separately. Selected additions require intact broad colored enclosure with coherent learned hue, sufficient illumination/extent, or a strong neutral reflection with dark enclosure. Small inset-core rescues remain candidates, because their local color does not establish separate bead identity.

The expanded domain exposed an inherited fallback hazard: an upstream size rejection could be lost during a hue fallback. The R278 wrapper rechecks the 870-pixel native limit; old outputs and historical algorithms remain unchanged. These requirements are conservative engineering gates, not a claim of general photo completeness. No reviewed coordinates, physical spacing, predicted sites, model colors or string indices enter Phase 1. The reference centerline records target membership only. Brightness maxima, patch centroids, interior centroids and unknown physical centers remain separate in the position ledger.

All 87 known synthetic scenes ran with an empty trusted inventory and automatic palette learning. New recovery detects 98/156 known bodies: black 28/32, red 45/62, yellow 25/62; zero selected false/duplicate/wrong-color locations or background/other-body mask pixels. Low yellow recall is explicit. This tests the new recovery path, not end-to-end photographic correctness. Full-photo regeneration reproduces the inventory, candidate decisions and feature files byte-for-byte.

## Radius, spacing and physical clearance

`Rope(..., radius_convention="intended")` uses `.96*4*sin(pi/6.5)=1.784536980648071`; default `legacy` remains `2.110915748921366`. The choice propagates into circular placement, source row spacing, loop dimensions, annular surfaces, visibility bounds and contact calculations. The new spline construction sets physical loop length before camera registration. A normalized world-unit adapter reuses the legacy exact surface evaluator; it does not shrink a rendered image.

At N=2696, source row pitch and zero tilt, legacy has 2696 sampled ±1 and 2696 ±6 penetrations. Intended radius has 0 ±1 and 2671 ±6 penetrations. Updating the radius-dependent pitch shortens the source loop, so the remaining axial packing cannot be diagnosed by shrinking bead silhouettes alone.

Tested coherent pitch multipliers and one shared hole-axis tilt. A −8° signed circumferential tilt trades ±6 against ±7 clearance and allows a 1.30 pitch factor at high count. Untilted candidates use 1.35–1.45. These **30–45% global pitch increases are exploratory structural hypotheses**, not maker-confirmed dimensions or "small strain." Local fitted strain remains separately bounded, arclength-zero-net, with fixed loop length and integer winding closure. The spline is noncircular, planar and smoothly adjustable. Its R258 warm start and camera have historical photographic information; phases, twist harmonics and local fields are reset before the new fits. No historical string identities are imported.

Contact auditing checks both directions against the exact annulus at 16,384 surface samples per bead for the exported models, across every bounding-sphere neighbor pair. More strongly, filling the annular hole gives a convex outer envelope with analytic support. Stored plane normals separate every possible pair by a positive margin; all other pairs are excluded by bounding spheres. This is a sufficient floating-point geometric certificate for the stated idealized shapes, with a 1e-6-unit safety threshold; it is not interval-arithmetic formal verification or proof that these are the photographed beads.

## Equal-budget geometry comparison

All rows use the same 24 full-circle phase starts and 136 objective evaluations (145 allowed), with train-only positive interiors and the same bounded parameter search. Assignments maximize native visible positive-pixel ownership one-to-one, with unmatched dummy assignments. Fit uses 12 deterministic pixels/interior; comparison uses up to 48; exported ledgers audit every native interior pixel. Training and withheld assignment are separate; final ledgers use a single global assignment and report disagreements. The cost uses whole observations equally, not pooled pixel count. No nearest-highlight-to-center loss is used.

| N | Hand | Pitch / source | Tilt | Focal px | Evaluations | Train ownership | Withheld ownership | Min separating gap |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1950 | +1 | 1.45 | 0° | 0 | 136 | 67.0% | 64.9% | 0.1400 |
| 1950 | +1 | 1.45 | 0° | 9598 | 136 | 65.8% | 66.6% | 0.1332 |
| 1950 | -1 | 1.45 | 0° | 0 | 136 | 66.3% | 67.7% | 0.1334 |
| 1950 | -1 | 1.45 | 0° | 9598 | 136 | 66.3% | 65.0% | 0.1245 |
| 2080 | +1 | 1.40 | 0° | 0 | 136 | 65.3% | 66.6% | 0.0493 |
| 2080 | -1 | 1.40 | 0° | 0 | 136 | 68.5% | 65.6% | 0.0533 |
| 2300 | +1 | 1.40 | 0° | 0 | 136 | 64.9% | 63.7% | 0.1164 |
| 2300 | -1 | 1.40 | 0° | 0 | 136 | 65.1% | 64.8% | 0.1164 |
| 2600 | +1 | 1.35 | 0° | 0 | 136 | 65.8% | 63.4% | 0.0491 |
| 2600 | -1 | 1.35 | 0° | 0 | 136 | 65.6% | 62.5% | 0.0644 |
| 2696 | +1 | 1.30 | -8° | 0 | 136 | 68.3% | 65.8% | 0.1147 |
| 2696 | +1 | 1.35 | 0° | 0 | 136 | 65.9% | 62.2% | 0.0818 |
| 2696 | -1 | 1.30 | -8° | 0 | 136 | 63.0% | 64.4% | 0.1040 |
| 2696 | -1 | 1.35 | 0° | 0 | 136 | 61.0% | 59.6% | 0.0800 |

Held-out geographic sectors and buffers exclude R278 parameter updates, not the historical warm start. The later count/camera/tilt comparisons are exploratory after inspecting earlier results. A count grid plus bounded search does not establish a unique count or global optimum. The N2080 negative-hand fit slightly leads training ownership; its opposite hand does better on withheld ownership. The high-count positive-hand tilted fit is competitive. The historical R276 mixed/contact models are audited against the same current observations in `historical-comparison.json`; their different historical fit budgets are not disguised as equal-budget controls.

## Complete conditional prediction ledgers

Every generated bead has a model index, ±1/±6/±7 neighbors, 3D center, projected center, sampled visible support, visible centroid, associated observation if any, pixel-derived color and status. Four competing models have full exports. A 2px visibility grid may miss tiny slivers; zero samples is explicitly not proof of complete occlusion. Unknown/grazing rays are retained. Indices are conditional generator addresses with an arbitrary origin, not recovered physical string identities.

Color uses actual inset visible pixels and hue distributions learned from measured training interiors. Black requires reflection plus dark-body evidence. Geometry-assisted candidates additionally need an independent stable image feature and adequate visible support; they never become retrospective Phase 1 detections. Conflicting surface colors downgrade otherwise high-support correspondences. Unknown is retained for insufficient evidence. No repeating pattern is used.

| Model | Confident conditional matches | Ambiguous | Geometry-assisted candidates | Predicted unconfirmed | Independent unexplained* |
|---|---:|---:|---:|---:|---:|
| intended_N2080_h-1_p1.400_f0 | 334 | 534 | 41 | 1166 | 32 |
| intended_N2080_h+1_p1.400_f0 | 291 | 569 | 54 | 1162 | 40 |
| intended_N2696_h+1_p1.300_f0_tilt-8 | 287 | 600 | 58 | 1747 | 13 |
| intended_N2696_h-1_p1.300_f0_tilt-8 | 255 | 629 | 49 | 1760 | 16 |

*Includes the three preserved location-only observations, which have no invented interior. The categories are conditional evidence accounting, not a verified visible bead census. Large numbers of tiny predicted surfaces and unconfirmed bodies are a warning, not successful recovery.

## Shared lighting and discrepancies

Geometry and positive-support correspondences are frozen before each lighting diagnostic. Twenty identical direction trials fit yellow training reflections; a single distant direction and fixed 6° lobe transfer to red and black. Missing highlights retain an explicit 30px sentinel and count. These are brightness-patch predictions, not inferred physical centers.

| Model | Held-out yellow RMS px | Red RMS px | Black RMS px |
|---|---:|---:|---:|
| intended_N2080_h-1_p1.400_f0 | 16.97 | 14.09 | 13.33 |
| intended_N2080_h+1_p1.400_f0 | 15.57 | 12.53 | 16.03 |
| intended_N2696_h+1_p1.300_f0_tilt-8 | 12.95 | 8.93 | 9.84 |
| intended_N2696_h-1_p1.300_f0_tilt-8 | 12.85 | 11.48 | 13.91 |

The high-count tilted model transfers shared lighting better than the lower-count candidate, but the positive-interior fit still leaves extensive ambiguity. The worst crops show clear black reflections with no plausible owner, large colored interiors split between candidate surfaces, and tiny visible predictions that cannot establish an independent body. Likely contributors are incorrect row pitch/count/phase, the assumed bead aspect ratio and hole-axis orientation, residual spline/camera bias, and uncertain ownership of small photographic patches. These are hypotheses to test, not adjudicated causes. The geometric clearance improvement does not compensate for photographic failures.

POV-Ray renders use the unchanged source bead macro with the explicit corrected radius and saved 3D transforms, one shared parallel light, and gray for uncertain model colors. Display materials are illustrative, not radiometric calibration.

## Validation and stopping point

50 scientific tests, plus 18 R275/local-surface regression checks, pass. The scientific tests cover both radius conventions, dimensional propagation, both helicities with fixed major traversal, closure, neighbor modulo indexing, positive-support assignment, legacy ray replay, unit-change invariance, tilted frames, perspective registration, exact surface samples and separation witnesses. The 87 image scenes, native measurement/ledger audit, byte-exact Phase 1 replay and byte-exact 31-file saved-model replay are separate checks. Original photograph, all 810 coordinates/807 masks and 4,721 prior tracked files are unchanged; the only shared-code edit is the explicit optional radius convention in `bead_placement.py`. All prior R276 alternatives survive.

This delivers significant progress in both phases, a physically separated family of candidates and reproducible complete conditional ledgers. **It does not complete reliable physical indexing or predict the verified identity of substantially every visible bead.** Next resolve the pitch/aspect-ratio/orientation ambiguity using geographically distributed exposed bodies and connected ±1/±6/±7 photographic ownership, keeping the frozen observations fixed. Do not begin repeating-pattern inference. Keep the current model/reasoning; no `/new` is required for reviewing these results.
