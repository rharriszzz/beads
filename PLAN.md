# Photo-2 reconstruction plan

The goal is to extend `beads.pov` to reproduce `beads-photo-2.jpg` using Python
and POV-Ray, fit bead colors and POV-Ray materials, and identify helicity
and a repeating sequence of roughly 200–400 beads. Appearance fitting and
sequence identification are separate claims. Instructions are in `REQUEST_LOG.md`.

## Whole plan

1. **Establish a reproducible forward model and evidence baseline.** Pull the
   workspace repositories, create a branch, read prior work, use Python 3.12,
   bring in the saved closed spline with provenance, render adjustable paper,
   lighting and beads, save photo comparisons and diagnostics, preserve the
   legacy renderer and create request/experiment/handoff records.
2. **Fit the bead geometry to visible evidence.** Label centers and colors in
   several separated photo patches, including both bends and straight sections.
   Assume bead proportions and hole orientation from legacy `beads.pov` (R016).
   Fit image scale, rope width, pitch, circumference count and phase under the
   crochet connectivity and small closure-twist constraints. Compare both hands.
   Decide whether the orthographic approximation is sufficient. Measure residuals
   and hold out patches; do not use arbitrary nearest-neighbor chain ordering.
3. **Fit paper, lighting and POV-Ray materials.** Use background-only patches
   and bead interiors/highlights/shadows. Separate illumination from pigment
   estimates where possible. Fit pigment color/filter/transmit, finish diffuse,
   specular/phong, roughness and reflection, normal texture, and interior IOR
   where relevant. Compare opaque/translucent and glossy/frosted settings by
   their rendered agreement with the photo. R008 defines material in this sense.
4. **Recover and validate the repeat.** Preserve hidden/uncertain positions in
   the helical index sequence. Search 200–400 jointly with remaining layout
   ambiguity; use categorical evidence, held-out repeats, support/confidence
   maps, perturbation checks and synthetic known-pattern image round trips.
   Test documented photo-4/case-4 correspondence when needed. Accept a pattern
   only if the evidence distinguishes it from alternatives; report unresolved
   positions and symmetries instead of inventing beads.
5. **Render the recovered model and deliver.** Feed the inferred repeating
   sequence into the forward model, compare full image and held-out crops,
   retain sources/parameters/checks, and produce a higher-resolution final
   render after geometry and inference are validated.

Stages can inform each other, but each result must retain its evidence and
limitations. A visually plausible image alone cannot pass Step 4.

## Completed baseline: Step 1, plus exploratory Step 4 diagnostics

This step produces a runnable initial scene and a reliable place to continue.
It includes repository synchronization, all-branch Markdown review, Python 3.12
setup, sourced spline, shared bead geometry, procedural paper, area light/fill,
three material proxies, photo-sampled color preview, both-sign 200–400 candidate
ranking, focused tests, legacy render regression, written plan/request/handoff,
and the user's authorized add/commit/push.

Completion criteria:

- The photo-2 entry point renders headlessly with recorded settings and inputs.
- The closed spline/arc-length geometry passes finite/continuity checks; visual
  inspection and a mirror comparison catch gross coordinate mistakes.
- Synthetic missing-data tests recover a known repeat without losing indices
  or depending on palette numbering; no real-pattern success is implied.
- A legacy scene renders identically to the pre-change scene.
- All current instructions, actual results, limitations and one next task are
  recorded; scoped source/docs are committed and pushed, with user files excluded.

Stop this step after those checks and publication. Do not claim the exact bead
count, helicity, fitted POV-Ray material parameters or repeating pattern is
established. The exploratory period ranking establishes a baseline and tests
the data path only.
No animation, physical necklace measurement or Mac validation is in this step.

## R014 step: fixed-observation geometry comparison — complete at ambiguity

Created a provisional 103-center/color dataset across three straight and three
bend patches. Compared both hands on identical annotations, with shared geometry
trained on three patches and 27 withheld centers after partial calibration of
three separate patches. Full results and equations: `photo2/GEOMETRY.md`.
Withheld errors are 6.27/6.41 px and inconsistent across patches; neither hand
is accepted. Pitch/count/linear-twist have an exact degeneracy. Hole-axis tilt,
body dimensions and camera adequacy are unmeasured by these centers. Numerical
fits condition on zero local twist and front-half visibility. No change to
scene defaults or repeat claims. Step 2 as a whole remains open.

## R015 step: synthetic occlusion benchmark — complete at limited discrimination

Added a both-hand POV-Ray benchmark with exact instance/isolated masks and known
body geometry. Center-only scoring favors dense stress geometry under noise and
cannot distinguish depth reflection, size or tilt here. Exact internal boundaries
distinguish those discrete alternatives; silhouette alone does not resolve depth
reflection. The pitch/count/twist gauge remains pixel-identical. Missing-label
trials retain unknown indices; mask centroids and true centers are separate.
Details, checks and limitations: `photo2/SYNTHETIC.md`. No photo settings changed.
This is fixed-registration candidate discrimination with perfect masks, not
continuous geometry recovery; Step 2 remains open.

## R016: construction constraints and source authority

User guidance: beads are pre-strung, then a slipknot is added, then crocheted one
bead per chain stitch. The first three rows require dexterity. Additional twist
is small, no more than joining the ends requires. Ask the user about construction
uncertainties; no numerical twist bound or precise stitch-to-row map was supplied.
Use legacy `beads.pov` for assumed bead size/proportions and hole direction.
The user explicitly authorizes invented repeating patterns for synthetic tests.

Inspected source: local y is the hole axis; rotation by `chain_angle` about z
makes it tangent to the central circle, independent of `row_angle`. Hole/body
radius ratio is 0.14. Most cases use height/diameter 0.7, roundedness 0.8 and
relative size 1.0, with case-specific exceptions. All eight cases use nominal
6.5 beads/row. `nrows=round(nbeads/6.5)` and `exact_beads_per_row=nbeads/nrows`
close the helix with a small distributed adjustment. Image scale still needs
fitting; these are source assumptions, not newly recovered photo measurements.

R015 instead used hole ratio 0.3, height ratio 0.65 and tilt 20 degrees; current
photo settings use provisional height ratio 0.78. No code/settings change in
R016. Preserve that benchmark's evidence, but its unrestricted twist redundancy
does not prove ambiguity under the user's construction constraints. Repeated
colors in different visible sections can supply evidence for hidden repeat slots.

## Next bounded step within Step 2

Build a deterministic known repeating-pattern synthetic test using legacy bead
geometry/orientation and closure, extending existing Python/POV-Ray tools. Keep
original bead/stitch indices, repeat truth and rendered visibility. Test recovery
of hidden repeat slots from multiple visible occurrences at fixed known layout.
Validate shaded-image observations with controlled blur/noise and fitted local
alignment against hidden mask truth. Measure recovery and unresolved slots; this
does not yet establish joint geometry/order recovery from the photo. Stop at a
reproducible report and focused checks before photo refitting or real-repeat
claims. R016 records guidance only; this experiment has not started.
