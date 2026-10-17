# R308 pre-run specification

The maker authorizes a new bounded full-circuit experiment after R307. The source
photo, centerline evidence, all earlier scientific artifacts and conditional
identities remain unchanged. No pattern, Phase 3 or production adoption.

The 1,200-second fitting clock starts before evidence loading and includes all
initial model evaluations, global sensitivities, response sweeps, basin search,
local optimization, contact checks and checkpoint writing. Export and independent
verification are measured separately. Native step-one optics only; no coarse
candidate screening. Initial five whole-chain evaluations are also the actual
representative evaluation benchmark, avoiding a repeated profiling campaign.

Compare R306/R307 primary and R306's three other discrete families. At the best
initial training model, measure two-sided derivatives in scale, axial shape, minor
radius, camera elevation/roll, phase, longitudinal registration, tilt, and open
turn rate. Pivoted QR selects eight influential independent columns; save the
full SVD and couplings. Closed turn rate is discrete winding, not differentiated.
Use the existing physical parameter domains, not unconstrained bead movement.

Stage 1 receives approximately 56% of fitting time, holds all correction fields
fixed, and records broad phase (-pi…pi), registration (±13px), two additional
sensitivity-selected response curves, a phase/registration grid and the strongest
other coupled grid. Investigate several minima without requiring monotonic paths
between basins. Native fixed-owner damped least squares refines up to three basins.
Stage 2 receives approximately 23% and tests low-amplitude Fourier components
(modes1–4) of all three existing periodic32-knot fields. Select eight economical
correction directions. Stage 3 jointly alternates four globals/four correction
directions per block until the budget or four stagnant complete blocks.

New corrections relative to the global-only solution have maximum interpolated
amplitudes2px axis offset, .06rad phase, .002 fractional local spacing, plus a
hard maximum projected center displacement of10% of reference face diameter.
At the R306 start that is about3.1px; .06rad rotates the minor radius by about
7% of a bead diameter. These are conservative exploration bounds, not measured
string-strain limits. All inherited interpolated±2% spacing/phase-rate constraints
and complete-chain support certification remain hard. A mean-square amplitude
and second-difference penalty discourages unnecessary correction complexity.
No independent per-bead motion/orientation; shared light remains fixed so it
cannot disguise wrong body placement. Existing evidence does not certify +1/+6/+7
physical neighbor identities; their geometric relationships are exported as
conditional predictions, not invented photographic residuals.

R307 photographic residual definitions are retained, with equal geographic weight
within region and reflection groups. Native modal region owners are assigned only
for basin evaluations; derivatives retain owners. All original observations and
missing lobes survive. Each local accepted step must improve training loss without
exceeding baseline changes: paper+.005, coherent ownership−.01, bidirectional
boundary+.25px, colored omission+.01, RMS+.4px, and no extra missing lobes.
These are engineering protections, not confidence intervals or proof of fidelity.

Dense native training evaluation seals stage candidates before retrospective
comparison. Report R307's unchanged common metrics, component distributions,
regional errors and fixed-original-owner missingness. Require the existing5%
comparison-boundary and2 percentage-point coherent-ownership gains, no substantial
component/regional regression and no added missing original-owner lobes before
claiming substantial improvement over either R306 or R307. All historical
comparison evidence is exposed, never fresh validation. Preserve baseline if this
fails. The required(1110,336) location is evaluation-only, never a separate fit.

## Pre-comparison adaptive final-joint amendment

The initial schedule stagnated after829.247 seconds, without an accepted gain.
Unit-scale global perturbations lose1–6 fixed native lobes; the second/first
residual-difference ratio is0.86–2.14. Before any new comparison outcomes or
selection seal, add shrinking trust radii to Stage3 within the SAME1200 seconds.
The decision, unchanged objective/geometry/guard conditions, old source/checkpoint
and exact new source hashes are recorded in r308/evidence/adaptive-protocol.md,
before-adaptive-joint/, and adaptive-transition.json. This is a bounded numerical
amendment, not an extra campaign or a changed photographic acceptance standard.
The current standalone entry includes this final-joint adaptation automatically.

## Verified numerical-uncertainty repair within the same budget

At1033.904 cumulative fitting seconds, SIGTERM checkpointed the adaptive run.
A direct native trace identified separator S25's false boundary: unresolved sample72
was owner−1 and scored as an edge. A0.06-degree tilt perturbation resolves that
sample and jumps the apparent separator error5.31→9.62px. The original ray arrays
are preserved in evidence/separator-discontinuity.json. Unknown rays must not be
treated as verified gap boundaries or rewarded as empty paper. The repaired
objective excludes transitions touching unknown samples, excludes contour edges
touching unknown samples, and treats unknown paper rays conservatively as occupied.
Evidence, weights, physical model and hard guards are unchanged. The source/state
transition is recorded in evidence/unknown-ray-repair.json. Only the remaining
original fitting allowance is used; old and corrected losses are not interchangeable.
A stale saved signal-status flag on resume was also cleared; original trials remain.
