# How to reason about visible beads — guidance for future sessions

Read the quick model first. Then use the task table to choose the amount of detail
needed. This records the maker's R084–R085 corrections and the experiments they
prompted; it is intended to change how later analysis is done, not just preserve
pictures. The maker explicitly requested an abstract explanation and more detailed
levels for different tasks. New user instructions take precedence.

## Level 1 — Quick model

**We see the exposed part of a three-dimensional bead, after other beads hide
parts of it. We do not generally see an isolated oval.** A bead's physical shape
can stay fixed while its visible outline changes substantially. Two things matter:
where the bead lies around the rope's small cross-section, and the camera's view
of that part of the necklace. Its neighbors determine which edges are exposed.

Around a toroidal necklace, the local viewing direction changes around the major
circle. A broad face can become a cap, a crescent, a notched portion, a tiny remnant
or fully hidden. Rotating a fixed two-dimensional template does not explain all
these changes. The visible portion's center is not necessarily the projected
physical center; either center can differ from a highlight.

**Keep major-circle viewing angle separate from minor-circle progression.**
Helicity controls the direction of progression around the rope's minor circle.
As we move around the necklace's major circle, the current section turns relative
to the camera. We need that local viewing angle to know which family of visible
bead shapes to expect. Knowing helicity does not supply the section's viewing
angle; knowing the viewing angle does not supply the direction of minor winding.

For an image-analysis task, first estimate the local section orientation/view,
then compare plausible exposed shapes at different minor phases. Use helicity
to interpret their progression and neighbor overlap. The maker confirms the necklace lies flat on paper on a table. Keep its major
centerline planar. Estimate the section's direction within that plane relative
to the fixed camera; do not introduce independent out-of-plane section tilts.
The camera may view the paper obliquely, which is a single global camera/plane
relationship. The beads' 3D shapes and minor-circle placement remain intact;
planarity does not force all individual bead centers to the same height.

**Helicity also changes which neighbors cover which edges.** It can leave the total
visible area almost unchanged while changing the left/right cut-ins and overlap.
Read these changes relative to the local rope direction. The effect is subtler
than changing which side of the rope a selected bead occupies.

**Color and shape provide complementary evidence.** Saturation/value changes
along a path between visible bead interiors can help locate a boundary. A dark
valley alone is not enough: shading, highlights, outside background and occlusion
also change S/V. A white highlight can lie inside a blue or black bead. Use the
expected visible shape and the neighboring portions to interpret the path.

A useful working description is:

> visible portion = projected bead surface left exposed by neighboring beads;
> appearance on that portion = pigment + finish + lighting + image sampling.

Keep these two descriptions separate, then test their agreement. Pixel area is a
supporting scale check, not a body-count, shape or helicity test. Continue ignoring
slivers in active inventories under R069; this lesson does not reopen ownership.

## Level 2 — Choose the evidence for the current task

| Task | What to use | What the evidence does not establish |
| --- | --- | --- |
| Explain a shape or review a boundary | [Full-circle atlas](review/r085/review.html), especially fixed-phase columns and aligned-tangent shapes | That a specific JPEG region is one bead, or has a known index |
| Separate neighboring same-color regions | S/V paths between visible interiors, controls within one body, and plausible exposed-shape/overlap hypotheses | That every intensity trough is a bead seam, or every highlight is a center |
| Review region size / ignore slivers | Nearby substantial visible portions at comparable local views; inspect masks and palette first | That half-median or twice-median area decides physical identity |
| Fit local geometry or visible masks | Estimate section angle relative to camera first; then bead shape, minor phase and occluding neighbors | A universal oval or a globally fixed image-space offset |
| Compare helicities | [Aligned same-position examples](review/r084/helicity-shapes.png), plus consistent overlap across several neighbors | That a large-area score or one illustrative patch is a validated helicity classifier |
| Assign neighbors or chain indices | Distinguish image adjacency from chain adjacency; retain missing/hidden indices and both plausible hands | That the next visible region is index +1; ±1/±6/±7 offsets are specific to the calibrated 6.5-bead model |
| Fit color/material | Sample supported interiors, separate highlights/shadows, use POV-Ray pigment/finish/normal/interior parameters | Physical bead composition, or color truth from one bright pixel |
| Infer a repeating sequence | Establish usable observations and geometry first; test on known synthetic examples and carry uncertainty | Recovered order/pattern from photo-sampled colors or renderer IDs |

For an ordinary boundary review, Levels 1–2 and the relevant illustration are
enough. Read the technical level when designing measurements, fitting a model,
changing code or evaluating inverse claims. Do not rerun the sweeps just to
relearn these observations.

## Level 3 — Detailed analysis recipes and distinctions

### A. Generalize shapes by pose, not by one average outline

Use two coordinates for this calibration: major-circle angle θ and minor-circle
phase φ. In the R084/R085 convention, θ=360i/676 and
φ=(Helicity ×360i/6.5) modulo 360, with negligible/zero phase as documented.
Changing Helicity reverses the minor progression while leaving θ and the major
section's orientation fixed at a given index. R085 chooses Helicity=+1.

The section angle relative to the camera is the relevant viewing quantity.
For this fixed camera and torus, θ determines the local section orientation and
therefore its view. For the photographed necklace, follow the actual planar
centerline rather than assuming a perfect circle. Its local tangent within the
table plane, together with the fixed camera-to-plane relationship, determines
the section view. An image-space angle may require perspective correction, but
there is no independent local out-of-plane bend or tilt to fit. R086 explicitly
corrects the assistant's earlier suggestion of such a freedom.

Thus generalize over planar section direction and minor-circle phase. Estimate
any unknown camera obliquity globally. Do not explain a bad visible-bead fit by
lifting or tilting sections away from the paper without new maker evidence.
 There are 13 distinct φ values over two
small-circle turns. These are known synthetic coordinates, not inferred JPEG
indices. A real necklace may require a different planar centerline, scale, circumference,
phase, camera and in-plane local correction; the torus calibration is not a photo fit.

Hold φ approximately fixed while comparing θ around the necklace. Then hold the
local view approximately fixed while comparing φ. This separates two sources of
shape change that were mixed in the original uncertain-mask reviews. Compare
both original image orientation and tangent-aligned shapes. Keep projected size
visible when examining perspective; explicitly state any later scale normalization.

Preserve hidden states. At a visibility transition, do not interpolate a visible
bead through an occluder, invent a missing observation, or join small patches to
a neighbor merely to obtain a smoother outline. R085 records every modeled index;
its small rendered portions are calibration evidence, not new active inventory entries.

For a JPEG candidate, propose local shape/view/overlap hypotheses and evaluate
against the pixels. Keep multiple hypotheses if the camera, phase or border is
uncertain. Do not select a source index or look up the JPEG's source pattern to
make an image-only decision appear successful.

### B. S/V must be measured along the proposed connection

This is **the next method to implement and evaluate**, not an already completed
R084/R085 detector. R082 only measured V across short hand-selected suspected
seams. Do not describe that as a saturation/value path method between beads.

1. Select endpoints inside the two proposed visible bead interiors. Do not
   silently use brightest pixels, mask centroids or hidden geometric centers as
   equivalent endpoints. Show the selected endpoints and full path on the image.
2. Follow a stated straight or curved path between them. Sample RGB and compute
   V=max(R,G,B), S=(max−min)/max, with S=0 when max=0. Record whether channels use
   0–1 or 0–255, image encoding, interpolation and smoothing. Plot S and V against
   distance along the same path. These descriptive values are not a calibrated
   perceptual/material model.
3. Compare a candidate seam with paths wholly within a bead, including a
   highlight and a shaded part. Include both same-color and different-color
   neighbors. A highlight can raise V and lower S within one physical body;
   a shadow can lower V without changing identity. Do not force one profile shape.
4. Vary path placement modestly and inspect nearby parallel paths. Verify that
   the purported internal seam does not come from the outside silhouette or
   white background. Save contrary evidence as well as a favorable trace.
5. Interpret the transition together with the expected exposed contours of both
   portions and their occluding neighbors. Report whether the evidence improves
   a boundary decision. Stop before changing masks/IDs unless that is the
   authorized task and the evidence supports it.

The all-white/one-black experiment has almost no saturation variation. Its pigment
contrast makes shape easy to inspect, but cannot by itself validate colored-image
S/V discrimination or same-color segmentation.

### C. Compare helicity without conflating shape and displacement

At the same index, changing hand usually moves the bead to a different minor-circle
position. That is a useful animation, but not an isolated shape comparison.
For this exact 6.5-bead scene, indices divisible by 13 put the black bead at the
same position/orientation for either hand; neighboring overlap then changes.
R084 uses those indices for its aligned close-ups. This equivalence is specific
to the chosen geometry/phase convention, not a rule for arbitrary necklaces.

Inspect the sides of the visible outline where neighbors cut in, and the
relationship among several adjacent portions. R084's eight aligned examples
have less than 2.6% area difference but response-mask intersection/union only
0.832–0.875. This explains why a size-only audit misses a visible helicity cue.
Do not turn those eight illustrative measurements into an accuracy claim for
an inverse classifier. Both helicities still need consideration in ambiguous
image-only fits; the maker's one-hand R085 shape atlas does not resolve them.

### D. Know which kind of mask you are using

| Evidence | Meaning and limitations |
| --- | --- |
| R084 black-bead beauty image | One black pigment among white pigments, with original lighting/finish and antialiasing. Highlights remain visible on black. |
| R084 pigment-response mask | Decrease relative to a pixelwise maximum of the same 26 frames, thresholded at 3/10/25. Useful appearance evidence; can omit clipped highlights and include edge sampling changes. Not an exact silhouette. |
| R085 object-label mask | Pixel ownership from one emission-only, gamma-1, non-antialiased POV-Ray render with the same geometry. A sampled synthetic silhouette including occlusion, not shaded-image segmentation and not continuous subpixel truth. |
| Existing JPEG inventory mask | An image-analysis hypothesis with known color/boundary limitations. It must not inherit the certainty or source indices of the calibration masks. |

A same-scene geometry check can use synthetic labels openly. An image-only
inventory or inverse evaluation must keep those labels/source patterns out of
its decisions. Preserve that separation in names, reports and illustrations.

## Evidence and reproduction map

- [R084 black-bead walks](BLACK_BEAD_WALK.md): eight locations, 26 consecutive
  indices, both helicities, 416 beauty renders; paired animations and close-ups.
- [R085 full-circle shapes](FULL_CIRCLE_SHAPES.md): one added object-label render,
  all 676 known positions, 483 nonzero masks, 193 hidden at 1200×900; full-circle
  atlas and comparison against the earlier 208 +1 appearance frames.
- [Historical visibility calibration](VISIBILITY.md): instrumentation checks and
  missing-index lessons. Its old numerical counts belong to different scenes.
- [R082 diagnostic](BEADS6_BOUNDARY_DIAGNOSTIC.md): useful saved measurements,
  but its area cuts and short V transects do not implement the approach above.

Current limitations remain in SESSION_HANDOFF.md. Beads6 144/189, beads3 122/405,
beads5 188 and the other existing warnings are not resolved by these synthetic
experiments. No active inventory is verified complete and chain indices stay null.
