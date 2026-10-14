# R284B — Improve Phase 1 Photographic Measurements, Boundaries, and Reflection Detection

This specification preserves the user's assignment before algorithm changes.
Work in `rharriszzz/beads`, branch `photo-2-strategy-v3`, primarily under `photo2`.

This assignment continues R284A. The user has reviewed the three principal comparison pictures and provided detailed feedback.

**Do not simplify or abbreviate these requirements to conserve context.** If context becomes scarce, preserve the work in repository files and use compaction as necessary.

## 1. Before starting: preserve the requirements and working context

Read the current project instructions and handoff, together with:

- `photo2/R282_SPECIFICATION.md`
- `photo2/R282_INTEGRATED.md`
- `photo2/R283_REPORT.md`
- `photo2/R284A_REPORT.md`
- The relevant Phase 1 implementation and its tests
- The R284A photographic comparisons and numerical results

Before modifying the algorithms, create an R284B Markdown specification that preserves:

- The complete scientific requirements below.
- The user's explicit photographic review decisions.
- The distinction between Phase 1 photographic measurements and Phase 2 physical interpretation.
- Known failures of the previous algorithms.
- The intended experiments and evaluation criteria.
- The requirements for the final review package.

Also update the project handoff so that future sessions can recover the current scientific objectives without reconstructing them from conversation history.

### Context management

Maintain a concise but technically complete working record as the experiments proceed.

At meaningful checkpoints, save:

1. What was attempted.
2. Why it was attempted.
3. The parameters and implementation used.
4. What the results showed.
5. What failed and why.
6. Which hypotheses remain plausible.
7. What should be done next.

Preserve failed experiments as well as successful ones.

If context compaction becomes necessary, continue using the saved specification, working notes, results, and implementation as authoritative references.

After compaction, reread the relevant project files and current experimental notes before continuing.

Do not silently abandon an experiment or simplify the task merely because context is limited.

Do not use `/new` solely because the context window is becoming smaller.

## 2. Fundamental Phase 1 design — permanent requirement

The following distinction is essential and must be preserved in the permanent project specifications, code documentation, tests, and handoff.

### Red and yellow beads

Phase 1 identifies reliable photographic interiors and representative photographic locations.

The measured support should be a compact, well-supported portion of the visible bead. It does not have to reconstruct the entire physical bead silhouette.

### Black beads

**Phase 1 identifies and measures the specular reflections of black beads.**

It does **not** attempt to recover the entire black bead, reconstruct its dark body, or estimate its physical silhouette.

A reflection is a measured image feature, not a complete bead boundary.

The Phase 1 black-reflection detector should:

- Find the visible specular highlight.
- Measure its native photographic location.
- Estimate its boundary accurately.
- Preserve its intensity and shape information.
- Distinguish separate reflections where the evidence allows.
- Preserve uncertainty about whether multiple reflections belong to the same bead.

Do not enlarge a reflection into speculative surrounding dark material.

Do not infer the complete bead outline from the reflection.

### Phase 2 responsibility

Phase 2 fits physical bead geometry to the photographic measurements.

It determines which physical bead corresponds to each observed reflection, whether a reflection is at the expected location, and whether a common lighting model explains its position.

A Phase 1 reflection must not be silently converted into a certified physical bead identity.

### Phase 3 responsibility

Phase 3 infers the repeating bead-color pattern from the Phase 2 physical inventory and its uncertainty.

Neither Phase 2 nor Phase 3 may retroactively manufacture or alter independent Phase 1 observations.

## 3. User review — picture 1: two-sided centerline

Review: `photo2/review/r284a/two-sided-focus.png`

The user prefers **Method A**.

However, beads numbered 1 and 2 still have undesirable tails extending toward the lower left.

### Required investigation

Determine why these tails survive Method A's thickness-core pruning.

Examine the underlying native pixels, not merely the outline drawing.

Investigate:

- Narrow branches joining adjacent bead interiors.
- Connected regions extending into shadows or neighboring material.
- Local brightness saddles between distinct beads.
- Morphological operations that preserve unwanted protrusions.
- Changes in the measured centroid caused by residual tails.

Develop and compare several approaches to removing these tails.

Potential strategies include:

- Adaptive neck removal based on local support thickness.
- Local brightness-gradient barriers.
- Boundary regularization constrained by photographed material.
- Region separation using nearby competing photographic evidence.

These are suggestions, not mandatory implementations.

Correct the underlying support. Do not merely make its displayed outline look smoother.

Preserve genuine bead material and avoid truncating substantial valid interiors.

### Centerline requirements

The reviewed scene includes:

- Bead 1, the lower yellow bead with an unwanted tail.
- Bead 2, the red bead on the left through which the centerline passes.
- Bead 3, the yellow bead on the right.

All three should remain represented as distinct photographic observations when independently supported.

The centerline may pass through a bead or between multiple beads.

The system must recognize all beads whose visible bodies cross the centerline, and should aim to recover two or three distinct relevant beads near many centerline stations.

Do not arbitrarily enforce exactly two or three beads at every station.

Do not use physical-model bead identities to validate Phase 1 detections.

### Required outputs

Show:

- Original Method A.
- At least two additional tail-removal alternatives, preferably three if useful.
- Exact native support for each.
- Enlarged photographic comparison.
- Centroid changes.
- Amount of material removed.
- Remaining leakage or truncation.
- Your assessment of the best approach.

## 4. User review — picture 2: black specular reflections

Review: `photo2/review/r284a/duplicate-focus.png`

The user considers **R283 and R284A Method A** good starting points.

The previous recommendation to use Method C for black beads is **not the user's preference**.

### Required improvement

The existing boundary around the upper black bead's specular reflection is too irregular.

The user wants the boundary to remain in approximately the same location but become substantially smoother and more consistent with the actual specular intensity distribution.

Remember: **the target is the specular reflection itself, not the black bead's body.**

Consider genuinely different extraction techniques, including:

1. Subpixel contours derived from a smoothed intensity field.
2. Adaptive local isophote extraction.
3. Edge-aware segmentation around the reflection maximum.
4. Regularized contour fitting constrained by native brightness gradients.

Do not impose arbitrary circular or elliptical boundaries unless supported by the pixels.

Avoid making a contour smoother at the expense of moving it away from the actual reflection.

Preserve the underlying native-pixel measurement separately from any subpixel contour used for visualization or geometric interpretation.

### Upper and lower reflections

The user has clarified:

- The upper highlighted area is a good reflection on a black bead.
- The lower highlighted area is a secondary reflection on a black bead.
- The red bead to the right of the upper black bead is a more useful neighboring comparison.

Preserve the lower feature as a secondary photographic reflection.

Do not automatically count it as another physical bead.

Do not assume that its ownership is established merely because another reflection is nearby.

### Required outputs

Show the original photograph, R283 measurement, Method A measurement, and at least three alternative reflection-contour methods.

For each, show:

- Reflection peak or representative location.
- Native intensity support.
- Boundary or subpixel isophote.
- Local brightness profile.
- Smoothness and geometric stability.
- Difference from the original reflection location.
- Handling of the nearby secondary feature.

Explain which approach gives the most faithful measurement.

## 5. User review — picture 3: wandering magenta outline

Review: `photo2/review/r284a/abstention-focus.png`

The user considers **Method B the smoothest**, but believes that all existing methods follow the photographic brightness profile poorly.

Do not interpret this as approval of Method B's overall ownership algorithm. Its tendency to split a single bead into multiple detections remains a concern.

### First deliverable: explain the existing algorithm

Before implementing replacements, write approximately **300–500 words** explaining:

- How the photographic seed is selected.
- How the algorithm identifies pixels that may belong to a bead.
- How brightness, hue, saturation, gradients, and local background affect region growth.
- How connectedness, opening, erosion, thickness and shape constraints affect support selection.
- Why outlines can develop spikes, tails and wandering branches.
- Why contours can become flat, clipped, crescent-shaped or inconsistent with the brightness structure.
- How neighboring beads of similar color interfere.
- What the current method does well.
- Which assumptions may be inadequate.

Save this explanation in the R284B documentation.

### Second deliverable: compare alternative approaches

Develop at least **three genuinely different brightness-aware boundary methods**.

A fourth is desirable if it tests an independent idea.

Possible approaches:

**A. Edge-aware region growth**

Grow photographic support using intensity, hue and local gradient consistency, with stopping conditions at plausible bead boundaries.

**B. Competitive geodesic or watershed segmentation**

Allow nearby independently detected photographic features to compete for pixels, while retaining uncertainty and preventing one body from being fragmented into several false beads.

**C. Active contours or level sets**

Use image gradients and a smoothness penalty to find plausible boundaries, starting from reliable interior evidence.

**D. Local brightness-profile or isophote modeling**

Model the intensity structure of an individual bead and choose a contour supported by local transitions.

These methods should represent distinct mathematical approaches, not threshold variations of one algorithm.

Do not hardcode the reviewed bead's location or desired outline into inference.

### Required outputs

For each method, show:

- Original unmodified pixels.
- Initial seed and support.
- Final measured support.
- Boundary contour.
- Relevant brightness/gradient profile.
- Centroid.
- Leakage into adjacent material.
- Evidence of truncation or artificial contour distortion.
- Whether the method would incorrectly split a bead.

Preserve failed alternatives.

Recommend the best approach according to photographic evidence, not aesthetic smoothness alone.

## 6. General validation

Keep this round focused on Phase 1.

Apply the candidate methods to additional automatically selected real-photo examples beyond the three reviewed regions.

Include:

- Clearly visible red beads.
- Clearly visible yellow beads.
- Black reflections.
- Adjacent same-color beads.
- Beads crossing the centerline.
- Beads flanking the centerline.
- Examples with strong and weak reflections.

Use reproducible, photograph-only selection criteria.

Evaluate separately:

### Colored beads

- Correctly confined photographic support.
- Native boundary and brightness agreement.
- Unwanted tails and protrusions.
- Connectedness.
- Distinct-body separation.
- Centroid stability.
- Retained valid material.
- False partitions of one bead.

### Black reflections

- Peak and representative position stability.
- Intensity-profile agreement.
- Contour smoothness.
- Separation from neighboring highlights.
- Secondary-reflection preservation.
- Independence from speculative dark-body contours.

Use synthetic tests where they genuinely help validate the mathematical methods. Synthetic performance should not substitute for inspection of the actual photograph.

Do not maximize accepted candidate counts at the expense of reliability.

## 7. Centerline coverage and evidence

Preserve the user's goal of identifying every bead whose visible body crosses the centerline and obtaining better near-centerline coverage.

However, maintain the distinction between what Phase 1 can measure and what Phase 2 must infer.

For red and yellow beads, measured interiors can provide evidence of centerline crossing, but a compact interior may not include every pixel of the full bead.

For black beads, Phase 1 measures the specular reflection. It may not be possible to determine from Phase 1 alone whether the complete physical black bead crosses the centerline.

Record this uncertainty instead of manufacturing a bead outline.

If the line passes between two beads, both must be eligible as near-centerline observations.

Do not treat a single observation close to the line as proof of complete local coverage.

Retain the existing two-sided accounting, support geometry, and unresolved evidence.

## 8. Reliability, importance and provenance

Preserve the shared bead-record structure established in R282 and refined in R283.

Keep separate:

- Importance.
- Photographic measurement reliability.
- Color reliability.
- Visibility.
- Physical identity reliability.
- Phase of discovery.
- Source observations and subsequent interpretation.

All Phase 1 observations remain important, including unresolved ones.

For black beads, explicitly label the measured support type as a **specular-reflection region**, not a body interior.

A reflected highlight's measured centroid must not be presented as the physical bead center.

A smooth contour must not automatically receive a high reliability score.

Reliability should depend on the quality of actual photographic evidence and distinct-feature ownership.

Do not claim calibrated probabilities without independent supporting measurements.

## 9. Independence rules

Do not use:

- Historical manually supplied neighboring bead identities.
- Maker-confirmed physical correspondence charts.
- Phase 2 fitted physical centers.
- Physical-model bead indices.
- Phase 3 color-pattern hypotheses.

None of those may establish or certify Phase 1 bead detections.

Existing image-only photographic observations, image-derived centerline information and photographed pixels are permitted.

Reviewed examples and user feedback may guide evaluation and method development, but the final general algorithm must not depend on hardcoded reviewed coordinates.

## 10. Working style and experiments

Make routine technical decisions independently.

Investigate the reasons for failures before adjusting thresholds.

Try alternative algorithms when the first approach performs poorly.

Preserve unsuccessful results and explain what they reveal.

Do not hide uncertainty or report a cosmetically smoother contour as scientific improvement without photographic justification.

Keep the existing three-phase pipeline operational, but do not use this round to optimize Phase 2 global fitting or Phase 3 pattern scores.

Do not replace the production Phase 1 inventory until the alternatives have been compared and the user has chosen a preferred direction.

### Experimental checkpoints

Save scientific notes after:

1. The current-algorithm diagnosis.
2. The tail-removal comparison.
3. The black-reflection comparison.
4. The brightness-profile comparison.
5. The additional real-photo validation.
6. The final recommendation.

These checkpoint documents should survive context compaction and future sessions.

## 11. Final deliverables

Deliver an isolated R284B experiment containing:

1. A permanent specification of the Phase 1 colored-bead versus black-reflection distinction.
2. A 300–500-word explanation of the current boundary-generation method.
3. Several tail-removal alternatives for picture 1.
4. At least three smooth reflection-contour alternatives for picture 2.
5. At least three genuinely different brightness-aware segmentation methods for picture 3.
6. Side-by-side original-photo comparisons.
7. Additional automatically selected photographic test cases.
8. Quantitative comparisons and explicit failure explanations.
9. A recommendation for the strongest approaches.
10. A small, clear visual review package.
11. Reproduction instructions and scientific tests.
12. Updated project specification, handoff and requirement checklist.

Keep the previous R283 and R284A implementations and results unchanged.

Commit and push scoped changes to `photo-2-strategy-v3`, and verify the remote commit.

### Required stopping point

After completing the experiments and review package:

**Stop and wait for the user's selection of methods.**

Do not silently merge the alternatives into the main Phase 1 detector or begin another round of work.

Do not ask the user to manually label more beads.

The goal of R284B is to obtain photographic measurements that are both **spatially accurate and physically interpretable**:

- Compact, genuinely supported colored interiors.
- Smooth and accurately localized black-bead specular reflections.
- Correct handling of neighboring beads and multiple reflections.
- Better evidence for every bead crossing or near the centerline.

The Phase 1 measurements must be trustworthy before the subsequent physical reconstruction can be trustworthy.

## 12. Implementation/evaluation plan recorded before coding

The preceding sections retain the complete assignment. This section adds the initial
experimental plan; changes require checkpoint notes and preserved failed outputs.

1. Diagnose native A masks, distance transforms, morphology and luminance profiles.
   Write the 300–500-word algorithm explanation before replacement code.
2. Tail comparison: original A versus thickness-neck separation, intensity/gradient
   barrier trimming, and curvature regularization constrained to measured material.
3. Reflection comparison: smoothed-field subpixel isophote; adaptive local intensity
   split; gradient-driven regularized contour. Preserve native intensity support
   separately; never attach dark collars. Treat upper/lower as separate photographic
   features with unknown physical owner, never duplicate physical bead records.
4. Colored brightness comparison: edge-aware flood, marker-controlled watershed
   with basin/ambiguity diagnostics, active-contour/level-set support, and adaptive
   intensity-profile support. Use identical automatic cues and broad material guards.
5. Select additional real examples by image-derived quality/color, peak strength,
   same-color adjacency and signed support geometry; record selection before method
   evaluation. Quantify mask changes, retained bright material, centroid shifts,
   boundary gradient alignment, contour roughness and perturbation stability.
6. Keep original and new observations as schema-compatible experiment records.
   Importance high; native center/intensity measures distinct from physical center;
   photographic reliability independent of smoothness; ownership unknown when weak.
7. Use small analytic synthetic intensity/saddle/noise controls for mathematical
   behavior and localization; do not substitute body-truth synthetic scores for
   native photographic inspection. Freeze all scalar and raster outputs for replay.
8. Deliver three principal comparison pages plus a compact additional-case gallery,
   exact masks/subpixel contours/profiles, quantitative CSV/JSON and concise captions.
   Test schema, isolation, no dark expansion, native/subpixel separation, stability,
   preservation and exact replay. Commit/push; stop for choice.

Known failures carried forward: R283 leaves wandering masks under abstention;
R284A A leaves broad lower-left tails; B can partition one body into many supports;
C rays form artificial notches/crescents; C's dark-collar measurement is incompatible
with the newly permanent reflection-only requirement. Prior synthetic precision
is not real-photograph calibration. Interior crossing is not full-body crossing.
