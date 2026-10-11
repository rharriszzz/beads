# Bead-rope reconstruction: independent strategy review and handoff

**Review date:** 10 October 2026  
**Primary target:** `beads-photo-2.jpg` in [`rharriszzz/beads`](https://github.com/rharriszzz/beads), branch [`photo-2-reconstruction-v2`](https://github.com/rharriszzz/beads/tree/photo-2-reconstruction-v2), reviewed remote tip `b28b99e8` (5 October 2026).  
**Scope:** Review of the GitHub branches and project documents; not a new image-processing experiment. I inspected the recorded experiments and relevant code, but did not rerun them or independently measure the original photograph.

## Executive conclusion

**Use GPT-6 Astra (High reasoning effort) to reconsider the strategy, then GPT-6.1 Sol for bounded implementation.** The underlying problem is not the model's ability to write Python. It is maintaining a valid *inverse-reconstruction strategy* as many locally plausible steps accumulate.

**Do not start from the circular POV-Ray renderings as if they were close substitutes for the photograph.** They are useful for checking geometry, indexing, renderer semantics, and algorithms on known answers. The *primary evidence and success criterion* must come from real photographs, particularly photo 2. The actual necklace is not constrained to a circular centerline; real illumination, perspective, shadows, occlusion, and bead appearance differ materially from the renderer. Its unknown design need not match any of the eight built-in POV-Ray patterns.

**My recommended next experiment:** On several representative **real-photo** patches, compare the current M4 candidate detector against a **geometry-aware local bead model** using the known helical neighbor families (±1, ±6, ±7), optional directional FFT cues, and reliably visible bead interiors. Score *distinct visible bodies found* and *false/duplicate assignments*, not just how many pixels or candidates a heuristic returns. Do **not** alter the global reconstruction until this comparison distinguishes approaches.

## 1. What the project must ultimately recover

From a single photograph of a crocheted, approximately 6.5-beads-per-turn rope necklace:

1. Separate paper (including shadows) from the necklace well enough to constrain a **noncircular planar centerline**; an exact foreground mask is not a prerequisite.
2. Locate and characterize visibly exposed bead bodies, their colors, and uncertainty. A specular highlight, visible-region centroid, detector seed, and physical 3-D bead center are *different quantities*.
3. Establish the local helical arrangement and **±1/±6/±7 neighbor relationships**, then assign physical full-string `bead_index` values despite hidden/partly hidden beads. Keep both helicity signs and unresolved correspondences until evidence distinguishes them.
4. Resolve the necklace's total bead count and chain closure sufficiently to test repeating patterns. Find the shortest compatible color block, leaving unsupported colors **unknown** rather than invented. For this photo, the maker reports a repeat shorter than 400 and not divisible by 13.
5. Approximate camera, paper, geometry, lighting and POV-Ray pigment/finish sufficiently to reproduce image appearance. This is an important *later* consistency check, not evidence that recovered sequence labels are correct by itself.

This is an **inverse problem with partial visibility**. Some hidden colors or absolute index conventions may remain unidentifiable from one photo. A scientifically sound result may be a set of compatible solutions plus clear residual ambiguities.

## 2. How the work arrived here

| Period / code | Valuable progress | Why it was not enough |
| --- | --- | --- |
| [`hsv_tools/main`](https://github.com/rharriszzz/hsv_tools) and [`bead_map/main`](https://github.com/rharriszzz/bead_map) (2025) | Interactive HSV masks; attempts at a spline and bead locations | Shadowed paper overlaps bead colors, and the estimated borders/centerline can follow shadows or fragmented masks. Useful diagnostics, not trustworthy geometry on their own. |
| [`beads/pattern`](https://github.com/rharriszzz/beads/tree/pattern), [`image-to-pattern`](https://github.com/rharriszzz/beads/tree/image-to-pattern) | Superpixels, color quantization, lattice/ordering experiments, generated-image checks | Appearance segmentation and projected grid-to-chain indexing did not produce a verified real-photo reconstruction. |
| [`image-to-pattern-2`](https://github.com/rharriszzz/beads/tree/image-to-pattern-2) | Clear milestones, per-stage metrics, calibration patterns and a proposed known-pattern real-photo check (`beads-photo-4.jpg`) | Largely a strategy document rather than a demonstrated solution. Photo 4 can be an *additional real-photo control* if its asserted case-4 correspondence is verified; it does not make photo 2 equivalent to a POV-Ray circular rendering. |
| [`photo-2-reconstruction`](https://github.com/rharriszzz/beads/tree/photo-2-reconstruction) | Background/curve experiments; manually reviewed bead candidates on generated images; explanations of pose, occlusion and uncertainties | Approximate photo-2 centerline, but no proven complete bead inventory, full-string labels or recovered pattern. |
| Current [`photo-2-reconstruction-v2`](https://github.com/rharriszzz/beads/tree/photo-2-reconstruction-v2), R092–R232 | Preserved maker's construction facts; tested FFT and paper evidence; local helical geometry, alternate counts/hands; confirmed positive interiors/marks; automatic colored masks; audited detector failures | Recent work has returned to finding trustworthy **interior seed pixels** before more region growth or image/model correspondence. This is still an *upstream measurement bottleneck*, not full pattern inference. |

The prior geometry and user-confirmed pixel evidence should **not** be discarded. Nor should a historical local fit or successful generated-image test be treated as verification of the real photograph. In particular, the recorded model comparisons have not established the exact total count, helicity or bead indices.

## 3. Current precise stopping point (R232)

R230: The maker visually rejected an earlier seed selection; roughly half the displayed locations appeared **between** beads rather than securely inside them. The selection relied on permissive color support and smoothed brightness; a gap can inherit an apparently acceptable seed score. Such a seed can corrupt all subsequent region growth.

R231 compared four **image-derived** alternatives:

| Method | Main signal | Whole-photo candidate points | Central concern |
| --- | --- | ---: | --- |
| M1 | Smoothed diffuse-brightness peaks | 537 | Misses dim bodies; not actually a specular-reflection detector |
| M2 | Distance into an allowed-color area | 926 | Connected color areas can make gaps look like deep interiors |
| M3 | Small tested color/brightness neighborhood | 431 | Rejects legitimate yellow bodies in one reviewed region |
| **M4** | Crossed local brightness/color profiles | **599** | Looks promising but can miss dim/flat beads and confuse multiple nearby bodies |

In R232, the maker rated **M4** relatively well in two displayed crops; M1 and M3 sometimes cover different apparent misses. This is **a provisional visual preference**, not acceptance of 599 correct unique beads. The agent compared whether to supplement M4 with M1 or M3. Its current question, Q232.1, asks whether two candidate positions 11.40 pixels apart, `(943,388)` and `(946,377)`, lie on the same yellow bead. No production detector has been replaced.

**Critical validation gap:** Four owner-known synthetic test scenes showed good coverage by M4, but even the **old photo-rejected seeds** passed their synthetic ownership checks. Those tests did not reproduce the real-photo failure. Improving synthetic numbers alone will not resolve the central uncertainty.

**Still not demonstrated:** reliable real-photo one-candidate-per-visible-body inventory; stable ±1/±6/±7 correspondence around the necklace; accepted count, helicity, closure, shortest repeat or final lighting/material fit.

## 4. Why the real photograph must drive the solution

- **Noncircular layout:** Replace a circular major path with a flexible *closed planar spline* `C(s)` fitted to photo evidence. Construct the bead cross-section and its helical phase in the **local tangent frame** of `C(s)`. This preserves the forward placement logic without requiring the necklace to form a circle.
- **Unknown projection:** Camera angle, scale, local foreshortening and lens/crop parameters matter. Lens metadata provides a starting bound, not a measured camera pose.
- **Illumination:** Diffuse/extended and potentially multiple light sources, ambient fill, cast shadows and variable specular reflections make brightness peaks unreliable as universal bead centers. Estimate lighting jointly only after geometry is adequately constrained; do not make point-light reflections a geometric assumption.
- **Occlusion:** Visible bodies are partial 3-D surfaces. Some lack usable highlights or complete boundaries; neighboring beads can produce non-oval, crescent-like shapes. An image region need not map to a whole bead silhouette.
- **Unknown sequence:** Built-in `beads.pov` case patterns are *not plausible default answers* for photo 2. Recover the sequence from image-derived identities and the crochet topology; use known patterns only as calibration or independent tests.
- **Ambiguous appearance:** Shadowed red and paper can overlap in HSV; black bodies are locatable but require different evidence. Accept positive interior patches and uncertain gaps instead of requiring perfect color-based segmentation.

Synthetic scenes remain valuable as *unit tests*: verify index/neighbor math, both helicity conventions, camera projection, occlusion, and failure cases. Introduce deformed centerlines, broader/multiple lights and different palette/backgrounds to test assumptions **after** failures are observed in real photos. Their scores should be reported separately from real-photo scores, never substituted for them.

## 5. Competing methods for the next stage

**A. Incremental M4 improvement (baseline).** Improve profile confidence and add M1/M3 proposals only when independent evidence supports an uncovered body. Fastest change and preserves recent work. **Risk:** all share overlapping appearance/mask assumptions; unions and distance suppression do not establish physical bead identity. Useful as the comparison baseline, not necessarily the long-term architecture.

**B. Geometry-aware local lattice inference (preferred experiment).** Begin with only high-confidence positive interior points; infer the local necklace tangent, apparent bead scale, ±1/±6/±7 direction families, possible helical hand and neighboring body hypotheses. Use local directional **2-D FFT/band-pass peaks** (the maker's previously successful cue) when helpful, but compare against direct spatial seam/spacing measurements. Fit a small graph/model with robust outlier rejection; allow missing bodies and unknown colors. Ask whether geometry correctly recovers bodies omitted or duplicated by M4 on *held-out real-photo crops*. **Risk:** uncertain centerline, foreshortening and partial occlusion can yield multiple locally consistent graphs. Preserve multiple hypotheses rather than forcing one.

**C. Positive-patch / shape-assisted instance segmentation.** Predict a bead's visible support from a local 3-D occlusion hypothesis, and use **small, definitely interior pixels** as positive constraints; include negative evidence only where reliable. This can avoid the unsolved exact dark-seam-versus-cast-shadow question. **Risk:** model-dependent outlines can appear persuasive while wrong. Test first-hit visible-body ownership on real patches and varied render controls before propagation.

**D. More extensive inverse rendering / joint fitting.** Generalize the forward model to a spline, camera, bead orientation, and extended/multiple lighting, then alternate between image correspondences and rendered predictions. Powerful once seeded with reliable bodies; **premature and highly underdetermined** without them. Do not optimize camera, spline, total count, bead correspondences and lighting simultaneously from an unreliable set of seeds.

These approaches need not be mutually exclusive. A likely successful pipeline uses **A as an appearance proposal source, B for structural consistency, C for visibility/ownership validation, and D for later global refinement**. The ordering and contribution must be justified by *real-photo* evidence, not by architectural elegance.

## 6. One bounded, decision-making experiment

1. **Freeze a comparison baseline** at `b28b99e8`. Retain existing raw source images, annotated evidence, R231/R232 candidates, prior positive-patch facts and all experiment records. No automatic promotion of M4, earlier region masks or model indices to truth.
2. **Create a small real-photo evaluation set:** approximately 6–10 varied crops of photo 2, including clear red/yellow interiors, same-color neighbors, black bodies, highlights, ambiguous gaps, shadow and changing tangent direction. An assistant can prepare overlays/labels; the maker need only review a manageable sample of *visible bodies/relationships*, not thousands of pixels. Keep a held-out subset, and distinguish maker-confirmed labels from assistant guesses.
3. **Evaluate M4 exactly as delivered** on this set: number of marked visible bodies with a candidate, fraction of candidates inside an actual body, bodies with multiple candidates, candidates between bodies, and misses stratified by color/illumination. Define scores at the **body** level. Record ambiguity separately rather than treating it as an error or a success.
4. **Implement a minimal B prototype** on the same patches: local scale/tangent estimation, candidate ±1/±6/±7 neighbor graph, confidence and explicit gaps, with optional FFT cues. Do not first build an entire new renderer. Compare on *held-out real crops* against M4, and report errors/alternative graphs, not only visual overlays.
5. **Decision gate:** If structural constraints recover distinct bodies with meaningfully fewer false gap/duplicate assignments, continue with local geometry and index inference. If they do not, identify the specific failed premise—visibility, orientation, scale, appearance or observation quality—and revise it. Do not merely retune a threshold or ask another unrelated single-pixel question.

The early goal is a **high-precision local anchor set**, not complete detection. A reliable subset can make neighbor inference possible; global missing-body recovery comes later. No arbitrary numerical acceptance target should be retroactively chosen after observing the results.

## 7. How to stop the recurring “small questions” trap

`AGENTS.md` currently says to **“Ask frequent, small illustrated questions”**. This is consistent with the earlier interactive workflow, but it now encourages local yes/no questions (such as Q232.1) while leaving the higher-level method unchallenged.

**Proposed replacement policy:**

- At every stage boundary, deliver a *one-page decision memo*: objective, current evidence, 3–5 distinct methods, underlying assumptions, likely failure modes, exact real-photo experiment, predicted differentiating observations, and stop/go criterion.
- The agent must **recommend and justify a method itself**, rather than ask the maker to choose among untested algorithms. Ask for maker-only information (e.g., whether two regions visibly belong to the same bead) only when it would change the decision, and preferably batch such questions in one annotated panel.
- A prior result marked *provisional* must never silently become a premise in the next stage. Track **maker facts / measured image facts / assistant inferences / synthetic-only validations** separately.
- Treat major user corrections (for example, “the seeds are between beads”) as a trigger to **audit and possibly roll back the premise that generated the seeds**, not only to refine the next filtering threshold.
- Keep detailed append-only logs for reproducibility, but also maintain **one short living strategy brief**. `SESSION_HANDOFF.md`, `PLAN.md`, and `METHODS.md` already contain extensive history; they are not a substitute for an independent current strategy evaluation.

## 8. Instructions for an Astra review session

> Read this handoff; then inspect `AGENTS.md`, `INITIAL_QUESTION.md`, the top of `SESSION_HANDOFF.md` and `PLAN.md`, `photo2/SEED_METHOD_REVIEW.md`, and the relevant source/scripts. Review older branch ideas only as needed.
>
> **First deliver a design-decision memo, not code.** Explain what the current detector can and cannot establish on the real photograph. Critique the assumptions that led to R230–R232. Compare at least three genuinely different methods, including a noncircular, geometry-aware approach using the known ±1/±6/±7 structure and optional directional FFT. Propose one bounded experiment on *real photo 2*, its independent body-level evaluation, and a stopping rule. Use synthetic POV-Ray data to test mechanics, but never treat a successful synthetic test or a known built-in color pattern as evidence that photo 2 has been reconstructed. Preserve prior confirmed maker observations and uncertainty. Recommend a method and explain why; ask no low-level question unless the answer is essential to that choice.
>
> Once the decision memo is reviewed, the implementation agent may carry out the agreed **single bounded experiment**, report the measured real-photo failures and improvements, and stop before broad refactoring or advancing another phase. Do not claim full-string indices, helicity, total count or pattern without independent evidence.

**Model division:** Astra High for this strategic review and later go/no-go decisions; Sol High (or Medium for routine scripting) for implementation, tests and documentation. Re-evaluate with the *same real-photo scorecard*. OpenAI currently describes Astra as its most capable model and Sol as near-Astra at lower cost; that is a prior about capability, **not empirical proof** that Astra will solve this particular inverse problem better.

## 9. Primary references (pinned where possible)

- [Current instructions](https://github.com/rharriszzz/beads/blob/b28b99e8ae224d0a597b69049160f43563b29540/AGENTS.md), [initial maker facts](https://github.com/rharriszzz/beads/blob/b28b99e8ae224d0a597b69049160f43563b29540/INITIAL_QUESTION.md), [latest handoff](https://github.com/rharriszzz/beads/blob/b28b99e8ae224d0a597b69049160f43563b29540/SESSION_HANDOFF.md), [methods collection](https://github.com/rharriszzz/beads/blob/b28b99e8ae224d0a597b69049160f43563b29540/METHODS.md).
- [R230: why original seeds failed](https://github.com/rharriszzz/beads/blob/b28b99e8ae224d0a597b69049160f43563b29540/photo2/STEP2_EXPLAINED.md); [R231: M1–M4 and controls](https://github.com/rharriszzz/beads/blob/b28b99e8ae224d0a597b69049160f43563b29540/photo2/SEED_METHOD_COMPARISON.md); [R232: M4 and supplement review](https://github.com/rharriszzz/beads/blob/b28b99e8ae224d0a597b69049160f43563b29540/photo2/SEED_METHOD_REVIEW.md).
- [Earlier geometry/shape lessons](https://github.com/rharriszzz/beads/blob/b28b99e8ae224d0a597b69049160f43563b29540/photo2/PRIOR_WORK.md), [FFT implementation notes](https://github.com/rharriszzz/beads/blob/b28b99e8ae224d0a597b69049160f43563b29540/photo2/FFT_EXPLORER_NOTES.md), [positive evidence and local fitting](https://github.com/rharriszzz/beads/blob/b28b99e8ae224d0a597b69049160f43563b29540/photo2/POSITIVE_PATCH_REGISTRATION.md).
- [Old reconstruction methods](https://github.com/rharriszzz/beads/blob/2c4c116bf7f7b9e8c773358a97740dcd77879a8a/METHODS_AND_PLAN.md); [earlier gated plan and known-photo suggestion](https://github.com/rharriszzz/beads/blob/402663eb579a8b66abe553cc3c917ab8f0cbc7c0/image-to-pattern/plan.md); [`bead_map`](https://github.com/rharriszzz/bead_map), [`hsv_tools`](https://github.com/rharriszzz/hsv_tools).
- [Current OpenAI model selection guidance](https://developers.openai.com/api/docs/models) and [Sol model description](https://developers.openai.com/api/docs/models/gpt-6.1-sol).

*Reviewed published branches: `beads/{master,pattern,image-to-pattern,image-to-pattern-2,archive/image-to-pattern-2-wip,photo-2-reconstruction,photo-2-reconstruction-v2}`, `bead_map/main`, and `hsv_tools/main`. Branch summaries reflect the available committed files, not unpushed local work.*
