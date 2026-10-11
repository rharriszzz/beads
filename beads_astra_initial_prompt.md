# Independent strategy review: reconstruct a crocheted bead-rope necklace from a real photograph

You are the principal scientific/technical investigator for this task, working in `https://github.com/rharriszzz/beads`. Please use your strongest available reasoning, with the mindset of a researcher in inverse problems, computer vision, computational geometry, graph inference, and physical rendering.

**This is an independent strategy review, not a request to continue the previous coding session.** I have spent approximately six months trying automatic and manual approaches. The software has made useful local progress, but repeated iterations have ended in narrow questions whose answers I cannot confidently supply. I suspect some of these questions arise because earlier methodological assumptions were wrong. Your primary responsibility is to discover and challenge such assumptions, not merely extend the last implementation.

**Your deliverable in this first session is a defensible strategy and a precise, bounded next experiment. Do not implement that experiment until I authorize it.** You may inspect and run existing code to understand its behavior, provided the runs are non-destructive and clearly labeled. You should not need my help to choose ordinary algorithms, parameters to investigate, or experiments.

## 1. Git and execution safety

1. Inspect the current repository, remotes, current branch, HEAD, working-tree status, stashes, and any untracked user files. Do not discard, overwrite, stash, or rebase unrelated work.
2. The published starting point as of 10 October 2026 was `photo-2-reconstruction-v2` at commit `b28b99e8ae224d0a597b69049160f43563b29540` (R232). **Check for newer work** rather than assuming this is still the latest state.
3. The user has **already created and switched to `photo-2-strategy-v3`**, based on the remote `photo-2-reconstruction-v2` branch, and copied this prompt and `beads_reconstruction_strategy_handoff.md` into the repository. **Verify** the branch, its base, working-tree state and local files. Do not create another branch, switch branches, or reset anything unless you discover a concrete problem and explain it to the user.
4. Treat `photo-2-reconstruction-v2` and all other branches as preserved historical evidence. Do not modify them. `bead_map` and `hsv_tools` are read-only reference repositories for this task.
5. This prompt overrides the old instruction in `AGENTS.md` to keep asking frequent small illustrated questions and to resume the previous narrowly bounded task. Continue to honor its relevant safety, scientific-provenance, and project-convention instructions.
6. Make **documentation-only** changes in this first phase. Prepare a short, self-contained `STRATEGY_REVIEW.md` on the new branch, with source links and a runnable experimental specification. Do not refactor or replace the detector, alter `beads.pov`, modify the source photograph, or launch an open-ended optimization. A scoped commit and push of the new review document are acceptable if your normal Git permissions and safety checks allow them; verify the branch and remote tip before reporting success.

`beads_reconstruction_strategy_handoff.md` should be present in the repository next to this prompt. Read it if present. It is advisory, not authoritative, and you should be willing to disagree with it after examining the evidence.

## 2. The actual scientific objective

The central image is **`beads-photo-2.jpg`**, a photograph of a real crocheted bead-rope necklace made by me. The eventual goal is to extend or adapt `beads.pov` and Python tools so that the photograph can be explained by a physically consistent scene and, crucially, to recover the **shortest repeating color sequence along the original bead string**, with explicit uncertainty about what the image does not determine.

Potential outputs include:

- A plausible **noncircular planar centerline** of the rope, separate from the 3-D placement of its beads.
- Reliable observations of individual visible bead bodies, distinguishing positive interior pixels from glints, shadows, visible centroids, and actual physical bead centers.
- Local and eventually global helical placement, neighbor relationships, occlusion, helicity, total bead count, and full-string `bead_index` assignments.
- The shortest repeating red/yellow/black pattern compatible with verified observations and whole-repeat closure. Unknown and hidden colors must remain unknown unless the global constraints truly establish them.
- Eventually a POV-Ray rendering that approximates the photograph's geometry, camera, background, shadows, lighting, and bead appearance.

**Visual similarity is not enough.** A render colored by sampling photograph pixels does not demonstrate recovery of full-string indices or the true repeating pattern. Some aspects of the inverse problem may be non-identifiable from one photograph; be explicit about that.

### Maker-established construction and image facts

Read `INITIAL_QUESTION.md` in full and distinguish these facts from old numerical estimates:

- The necklace is a crocheted bead rope, approximately **6.5 beads per turn**, one bead per stitch. The beads were strung beforehand in a repeated sequence.
- Neighbor differences along the original string fall in the **±1, ±6, and ±7** families. Local orientation/handedness and actual associations must be inferred; do not treat guessed graph edges as observed fact.
- The **major centerline lies in the plane of the paper/table** but need not form a circle. The beads have three-dimensional rounded, hole-bearing surfaces and occlude one another. Some visible parts are not approximately oval.
- Beads have similar sizes, with red, yellow, and black bodies in photo 2. The image contains cast shadows, uncertain seams, highlights, and potentially strongly overlapping paper/bead HSV measurements. Black beads can be located but are often harder to interpret.
- Camera geometry and lighting are not measured. The photo was probably taken fairly close with an iPhone. Do not infer a point light from specular spots or regard EXIF focal length alone as a calibrated pose.
- The necklace contains a whole number of repeats of the designed pattern. For **photo 2**, the shortest repeat is **less than 400 beads** and **not divisible by 13**. The older estimate of 200–400 is not a hard lower bound. Total bead counts such as 2,698 or 3,592 in the experiments are hypotheses, not measured truths.
- Absolute pattern origin, chosen string direction, and naming convention are not important so long as a consistent convention is documented.

## 3. Critical warning about synthetic POV-Ray images

This is particularly important because several previous agents have proposed restarting from synthetic renderings.

**Do not make the existing circular `beads.pov` renders the primary reconstruction route or a proxy for success on photo 2.** The actual photographed necklace can have a strongly noncircular major path, unknown camera position, ambient or spatially extended lighting, real shadows, complex reflections, real manufacturing variations, and an unknown pattern not closely related to any of the built-in synthetic examples.

Use synthetic scenes to verify mathematical and software mechanisms: mapping between full-string index and bead placement, the ±1/±6/±7 families, handedness, visibility/occlusion, noise sensitivity, and controlled failures. Make synthetic tests deliberately more photorealistic and harder when useful, but **passing them does not establish reliability on a real photo**.

An old plan in `image-to-pattern-2` asserts that `beads-photo-4.jpg` depicts a known case-4 pattern. Verify that correspondence before treating it as ground truth. If valid, it is a valuable *secondary real-photograph* validation case. It does not replace the goal of solving photo 2.

The **principal empirical evaluation must use actual photo-2 pixels** and must detect failure modes that existing synthetic tests miss.

## 4. Existing history you must interrogate, not blindly inherit

The three key repositories are:

- `https://github.com/rharriszzz/beads` — all published branches, especially `photo-2-reconstruction-v2`, `photo-2-reconstruction`, `image-to-pattern`, `image-to-pattern-2`, and `pattern`.
- `https://github.com/rharriszzz/bead_map` — earlier centerline and mask-based bead detection.
- `https://github.com/rharriszzz/hsv_tools` — interactive HSV exploration and hand-assisted masks.

There are relevant Fourier experiments in `fft-image-explorer`, referred to by `photo2/FFT_EXPLORER_NOTES.md`; consult them if useful. Do not assume an FFT is mandatory.

Read these **before drawing conclusions**, but do not spend the whole session paraphrasing long chronological logs:

- `AGENTS.md` and `INITIAL_QUESTION.md`
- Current sections at the top of `SESSION_HANDOFF.md` and `PLAN.md`
- `METHODS.md`, as a method catalog, not a compulsory sequence
- `photo2/PRIOR_WORK.md`
- `photo2/STEP2_EXPLAINED.md`
- `photo2/SEED_METHOD_COMPARISON.md`
- `photo2/SEED_METHOD_REVIEW.md`
- The code used for R230–R232, including `refine_colored_masks.py`, `compare_seed_methods.py`, and `review_seed_complementarity.py`
- At least one prior substantial **geometry/correspondence** experiment, such as `VISIBLE_CORRESPONDENCE_PILOT.md`, `POSITIVE_PATCH_REGISTRATION.md`, `LOCAL_SURFACE_FIT.md`, or `NEIGHBOR_ANGLES.md`
- The older `image-to-pattern-2` plan and `photo-2-reconstruction/METHODS_AND_PLAN.md`, especially recorded failure modes.

Also inspect **the original photograph and representative unaltered close-ups**, not just conclusions in Markdown. Clearly label whether a statement comes from a maker-confirmed observation, direct measurement, model prediction, or synthetic test.

### Current recorded stopping point (R232)

At R230 I rejected the earlier displayed seed points: visually, many were located **between beads**, not in their interiors. The exact fraction was a qualitative estimate, not a measured full-photo error rate.

At R231 the agent compared:

- **M1:** local brightness peaks; 537 full-photo proposals;
- **M2:** deeper points in permissive color-supported masks; 926 proposals;
- **M3:** pixels with a small tested color/brightness neighborhood; 431 proposals;
- **M4:** crossed local color/brightness profile support; 599 proposals.

In R232 I found M4 relatively promising on two reviewed patches; M1 and M3 sometimes found different apparent beads. **This was not approval of all M4 points, of their uniqueness, or of the whole detector.** The active question Q232.1 asks whether `(943,388)` and `(946,377)` are on the same yellow bead. You do **not** need to obtain that answer before reconsidering the strategy.

A serious warning: the old visually rejected detector also passed the existing owner-known synthetic ownership checks. The synthetic tests therefore failed to reproduce important real-photograph errors.

Earlier work has valuable maker-confirmed interiors, saved visible-part marks, correspondence hypotheses, local neighbor graphs, candidate centerlines, alternative helicities and bead counts. Preserve them and distinguish **supported anchors** from speculative fits. The count, helicity, full-string indices, closure, and shortest photo-2 pattern remain unverified.

## 5. Questions the strategic review must answer

Do not assume that more precise hue thresholds, one more seed heuristic, or asking me more pairwise questions is necessarily the right next step.

1. **Where is the earliest unsupported assumption?** Draw a dependency chain from background estimation to centerline, visible bead observations, local graph, global index/closure, shortest pattern, and rendered appearance. Identify which dependencies are essential and which can be bypassed.
2. **Is the current seed-first architecture appropriate?** Can geometry, visibility, periodic spatial structure, neighborhood constraints, or definite interior patches provide a stronger starting point? Explain what would falsify each approach.
3. **What can one actual photograph determine?** Separate identifiable local geometric quantities from globally ambiguous bead index, helicity, total count, colors of hidden bodies, and pattern origin. Identify evidence that could break each ambiguity.
4. **What previous results should be retained?** Look for genuine high-quality maker-confirmed observations, forward-model components, useful spline/FFT measurements, and reproducible tests. Identify earlier methods that were rejected or insufficiently validated.
5. **What is the smallest real-photo experiment that would change the architectural decision?** It should reveal whether the currently favored M4 strategy is genuinely useful, whether a different strategy performs better, and why.

You should compare at least **three genuinely different families of solutions**, not three small parameter changes. Possibilities include:

- Improved appearance-driven points/instance proposals, with the existing frozen M4 output as a baseline.
- **Geometry-aware local inference** using a flexible planar rope tangent, bead scale, ±1/±6/±7 neighbor structure, missing-body hypotheses, and optional local 2-D Fourier direction/spacing clues.
- Positive-patch or occlusion-aware local model matching with unknown/unsupported boundaries retained as unknown.
- A hybrid that alternates image evidence and structural consistency, without prematurely fitting the entire necklace.
- Broader image-model fitting or inverse rendering *only where existing evidence makes it identifiable*.

You are free to propose a better alternative. Do not select geometry-first merely because this prompt mentions it; argue from real-photo evidence and falsifiable predictions.

## 6. Real-photo evaluation and independent checks

Design a **small but representative real-photo benchmark**, not an enormous manual annotation project. It could contain approximately 6–10 photo-2 crops spanning:

- clear red/yellow interiors;
- same-color adjacent bodies;
- black bodies and displaced specular reflections;
- cast shadow or low-light edges;
- ambiguous gaps;
- different local necklace tangent directions or curvature;
- at least one area where the current method visibly fails.

Avoid using only visually easy or previously optimized areas. Separate exploratory/training crops from **held-out real-photo crops**, and state the limitations if no independent held-out sample is possible.

The agent can prepare overlays and provisional bead identities itself. I can provide a **small amount of high-leverage visual validation**, but I should not need to mark hundreds of centers or select algorithm parameters.

Define body-level measurements where possible:

- proportion of proposed points confirmed inside a visible bead rather than paper/gaps;
- fraction of clearly visible distinct bodies covered by ≥1 valid candidate;
- extra/duplicate proposals on one body;
- real bodies missed, by color and difficulty;
- correctly supported local neighbor relations and unresolved or contradictory graph edges;
- robustness to modest parameter changes, illumination variation, and location along the rope;
- uncertainty/abstention and runtime.

Do not call a proposal count a bead count. Do not promote pixel-test success, a smooth spline, synthetic evaluation, or beautiful overlays into verified photo identities. Do not manufacture precision/recall numbers without ground truth.

Propose concrete **stop/go criteria in advance** and at least one adverse or falsification test. A method that safely abstains is better than one that invents definitive bead identities.

## 7. Collaboration model: automate implementation, not scientific judgment

My difficulty is that mostly automated sessions eventually demand tiny judgments that depend on dubious prior choices, whereas mostly manual sessions stop when I cannot formulate the next technical instruction.

The desired division of responsibility is:

- **You** identify hypotheses, choose and justify meaningful experiments, implement bounded experiments once approved, test, visualize, diagnose failure, and propose the next technical decision.
- **I** provide maker-only construction facts and a limited number of perceptual assessments that would materially change the strategy.
- At a **major architectural fork**, stop with a clear explanation and recommendation. At ordinary coding or parameter-selection decisions, proceed independently within the approved experiment.

Do **not** ask repeated questions of the form “are these two nearby pixels on the same bead?” unless the answer changes a specific scientific choice. If visual help is genuinely needed, preferably supply a small batch of annotated raw-image examples, each with a clear reason that the answer matters. Recommend your own default response or next test.

When I say a result is visibly wrong, treat it as evidence that an **upstream premise may be wrong**. Audit causality, rather than repairing the latest threshold repeatedly.

A "continue" message in any future session should resume the **approved scientific objective**, not automatically reactivate a superseded low-level TODO.

## 8. Deliverables for this initial session

Create `STRATEGY_REVIEW.md` with these sections (aim for a crisp decision document; link to large existing logs rather than copying them):

1. **Executive recommendation**, in plain English, including the one most valuable next experiment.
2. **Current state:** confirmed achievements, promising but provisional methods, and unverified claims; cite files and experiment IDs.
3. **Dependency/assumption audit:** identify one to three likely strategic errors or bottlenecks; explain the evidence for and against each.
4. **Competing architectural approaches:** assumptions, advantages, failure modes, and predictions that distinguish them on the *real photograph*. Recommend one, perhaps as a hybrid.
5. **Bounded next experiment:** exact real-image inputs, frozen M4 baseline, proposed new method, outputs, evaluation/holdout, checks, a success/failure gate, and a practical stopping point.
6. **Roadmap after that gate:** how local bead identities might lead to helical correspondence, total count, shortest repeat, and eventual inverse rendering; list unresolved identifiability issues.
7. **What you need from me:** preferably no questions; otherwise at most a few truly decision-changing questions, grouped and illustrated.
8. **Handoff to an implementation agent:** a short, unambiguous task definition that can be given to GPT-6.1 Sol after approval, with exact files, tests, scope boundaries, and reporting requirements.

At the end of your response to me, provide a short summary that I can understand without reading code: **what you think should change, why, the experiment that would demonstrate it, and precisely what will be different if it succeeds or fails.**

**Stop after delivering the strategy review.** Do not begin another round of seed tuning or the full reconstruction; do not ask me to choose a low-level method. Tell me explicitly whether you recommend proceeding with the experiment on this branch and what one-sentence approval I can give to authorize it.
