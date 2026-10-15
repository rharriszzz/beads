# R296 — reusable whole-necklace Phase 2 optimizer

The entry point is [`phase2_autofit.py`](phase2_autofit.py). It launches the
repository Python environment automatically and runs without an AI supervisor.
[Commands and operational details](R296_REPRODUCE.md),
[specification](R296_SPECIFICATION.md),
[pilot browser review](r296/results/pilot/review/index.html).

The delivered capability is a bounded, resumable search over documented physical
and photographic hypotheses. Its candidate count and correspondence labels remain
conditional. The photograph has not yielded a verified complete bead inventory,
unique helicity, physical join, calibrated camera or complete ownership solution.

## Model and search

R294/R295's short integration grid cannot simply be extended by adding indices.
R296 replaces that placement integration with a full-length monotone station map,
while inheriting R295's literal rounded annular surfaces, SDF rays, camera projection
and analytic support. The 9235.59px image-derived reference is cached, as are camera
plane reconstructions and invariant photographic samples.

Closed candidates enforce periodic axis, tangent frame, phase, spacing and integer
minor winding. All spatially close physical pairs are checked, including across
the index seam and nonlocal approaches. Open candidates retain a small explicit
seam opposite bead zero and unrestricted minor winding. The photographed path has
bright patches within 27.24px of every sampled axis point, supporting examination
of a continuous loop-shaped arrangement. The reference itself was made periodic
in its earlier image-only lineage; this cannot prove a physical connection beneath
occlusion. Both topology families survive. The open family's cut location is fixed;
other hidden joins and out-of-plane axes are outside the current parameter family.
See [topology evidence](r296/results/topology-evidence.json).

Bead zero and positive direction retain the R294 reference. Signed historical
−20…200 labels are present in every complete model. The remaining indices span
one full necklace; the closed seam wraps modulo the candidate count. Any changed
historical assignments are exported explicitly. Same-numbered indices in different
count/hand families do not necessarily denote the same physical bead.

Count bounds derive from image-reference length under the two R295 camera/spacing
families: **1905–3250**, with actual pilot hypotheses **1949–2826**. The historical
POV-Ray generator's total count is never a constraint. Thirty-two global starts
include both R295 families, both seam families, count changes and distinct camera,
phase and paired shape hypotheses. The initial literal N2540 extension of the
R295 primary demonstrates collisions outside its earlier fitted section; it is
preserved and rejected. A thinner hand+ extension and lower-count hand− models
provide feasible full-chain starting points.

The autonomous loop has four explicit stages:

1. **A:** 32 global starts, physical gating and inexpensive sampled screening.
2. **B:** overlapping periodic phase/spacing/axis fields, targeting important
   training-region failures. Every update is checked and evaluated globally.
3. **C:** common geometry/count/winding reconciliation and field smoothing.
4. **D:** reproducible count/phase restarts and additional camera/dimension trials.

B/C/D repeat in 64-proposal cycles. Integer ownership is recomputed using a bounded
beam over connected photographic region graphs, with unmatched and ±1/6/7 rivals.
Multiple reflections/compatible regions may share an owner. Color contradictions,
measured valleys and projected ordering provide soft penalties, without a repeating
color pattern or a one-reflection-equals-one-bead assumption.

An eight-member population preserves best feasible hand/topology representatives
plus distinct parameter basins. Selection is **0.65 training + 0.35 validation**
score. Poor coarse proposals are skipped, with a periodic bypass to limit screening
bias. Documented stagnation rules reduce step sizes; convergence, validation
stagnation, lack of a feasible start and user budgets terminate automatically.
No algorithm selection, model invention or human feedback is required mid-run.

## Photographic evidence and withholding

The evidence freeze precedes objective development. Existing Phase1 supports are
copied without changing their pixels, representatives, colors or uncertainty.
There are 1543 eligible independent patches from the preserved1545-record archive,
424 historical automatic colored interiors, and23 accepted candidate versions.
The latter are qualitative judgments with exact provenance, not23 certified beads.
Rejected R293 candidate masks are not targets. Reflection acceptances retain their
reflection-only meaning.

| Split | Independent patches | Larger region measurements |
|---|---:|---:|
| Training |1239|363|
| Validation |87|21|
| Reserved |84|21|
| Buffer |133|42|

Six geographically separated intervals lie outside the entire R294 inspected
window and accepted human cases. A60px longitudinal buffer is augmented by a35px
Euclidean exclusion check; the measured nearest training/withheld support distance
is55.95px. R295's old reserved cases are retrospective. This remains one previously
examined photograph; new geographical withholding does not make it globally blind
or constitute new-image confirmation.

The objective combines owner-balanced patches, substantial material containment,
region graph compatibility, bright continuity, photographic edges, color conflict,
reliable paper contradiction, first-hit occlusion and the original bead-0 anchor.
Darkness alone does not prove empty background. The inherited photographic palette
and paper diagnostics are cached measurements, not a new Phase1 detector. Native
full-support evaluation is separate from sampled search scores.

Budget stops generate development reviews and leave reserved outcomes unread.
Final sealing writes an immutable model/source freeze before reserved evaluation
and prevents further optimization of that run. Subsequent runs must treat the
already-exposed reserved outcomes as retrospective. The program cannot enforce
what a person remembers when selecting a new run or seed.

## Pilot and verification

The final pilot evaluates192 proposals:32 A,96 B,32 C and32 D. It preserves152
fine-evaluated eligible candidates,19 physical rejections,9 duplicates,8 coarse
screen rejections and4 parameter-bound rejections. The sampled selection score
improves **0.408613→0.426942** from the best global start to candidate188.
Training larger-region containment improves **60.88%→62.96%** and validation
**71.88%→74.93%**. These are useful numerical search gains, not recovered ownership.
Some contradictory-evidence metrics worsen; the complete score components and
failure locations remain visible.

The selected pilot candidate has2337 conditional sites, hand−, closed topology and
360 minor turns, with radius1.78454, axial multiplier1.015, tube radius3.96,
scale8.46 and camera elevation60°. The opposite hand, open seam and different count
families are retained. Stored legacy `pitch` and closed-family `turn` values are
initializer metadata: actual closed progression is N/winding, and actual spacing
is exported as `closure.effective_pitch` plus per-site stations. The local fields
further vary spacing; the true total bead count has not been established.

Nineteen contracts cover full-domain placement, historical labels, closed
position/frame/phase/spacing, open topology, seam-inclusive independent support,
actual interpenetration, unresolved volume budgets, geographic provenance, reserved
access guards, inherited rays, deterministic starts, population diversity, atomic
writes, exact resume, sealed/source-change refusal, budgets, actual SIGTERM and
exclusive run-directory locking and standalone-review evidence integrity. A real daemon restart also interrupted the pilot
after102 completed candidates. That recovery and a64→192 resumed run preserve
identical complete scientific candidate records, RNG and population. A final locked
CLI run is checked against both histories; elapsed time is excluded from equality.

Final native metrics, contact/visibility audits, performance measurements and
browser receipts are saved under `r296/results`; delivery verification is recorded
in `delivery.json`. All prior scientific files, observations and feedback are
checked against the pre-development preservation manifest.

## Native results and retained failures

The baseline below is candidate8, the best global-stage model, fixed before any
reserved outcome. Native evaluation traces every original support pixel.

| Evidence | Global baseline | Refined candidate188 |
|---|---:|---:|
| Training larger regions: mean / compatible |61.24% /76 of363|63.25% /83 of363|
| Validation larger regions: mean / compatible |72.38% /5 of21|74.54% /8 of21|
| Reserved larger regions: mean / compatible |62.14% /3 of21|64.80% /6 of21|
| Reserved patches: mean / compatible |74.41% /50 of84|79.41% /57 of84|
| Validation compatible patches |67 of87|66 of87|

1454/1815 native modal assignments remain stable from this global baseline,
including unmatched cases. This is conditional stability, not physical identity.
Across all evaluated observations, central containment averages84.82% (950 records)
and peripheral67.73% (865). Twenty-nine assigned observations belong to surfaces
with modeled visibility below10%; their mean containment is62.97%. These strata
mix observation kinds and are not bead-count or accuracy estimates.

The primary has763 sites linked to compatible supports,1574 unsupported sites,
and602 sites below10% modeled visibility. All2337 sites remain exported. Native
visibility traces1,040,179 pixels with591 unresolved rays, retained explicitly.
Its7006 independently recomputed support planes have minimum gap0.026672 source
units. All four exported families pass30557 pair checks in total; the open hand−
model has2438 sites and both hand+ alternatives2709. The true count remains unknown.
The primary's actual average pitch multiplier is1.34332, with local variation.

**The broader fit regresses on R295's old local window.** On the identical123
historical patches, mean containment falls92.35%→86.27%; on36 larger interiors it
falls71.51%→63.11%. Only39/159 modal assignments remain unchanged. The complete
comparison records every old/new conditional index. E5-1633-0278 near33 improves
50.46%→77.55% but remains below the80% compatibility threshold. C-1729-0337 near65
regresses61.86%→41.37%. C-2038-0658 falls96.70%→77.36% and changes195→182.
This is not a production replacement for R295 or evidence that these new identities
are correct. The original R295 results remain intact.

The final locked/guarded pilot takes184.5s; native export of four models adds63.1s
and peaks at about833MiB resident memory. The final source reproduces all192
candidate records across both interruption histories and17 native scientific
exports byte-exact against the first seal. The audit rechecks all positions and
contact witnesses,16000 selected native visibility rays,100 complete native
supports, and original-photo pixels. Chromium passes11 images/28 links, model
selection, original toggle, zoom, desktop and narrow layouts.19 tests and separate
stagnation/convergence stopping checks pass.13047 prior scientific files and69
feedback files are unchanged.

## Practical limits and stopping point

This family uses a planar image-derived axis, common camera and bead dimensions,
smooth shared local fields and a limited seam model. It cannot resolve an incorrect
axis family, invent a different bead shape, establish light/ownership truth, or
certify weak photographic evidence by continued optimization. Native first-hit
visibility is a geometric prediction. Support-plane and volume certificates use
floating-point margins, not interval arithmetic. Unsupported and poorly visible
sites remain in complete exports; retained-family position spread is not a
confidence interval.

No Phase1/Phase3 code or data, beads.pov, prior experiment or production model is
changed. No synthetic photographs, renderer or repeating color sequence is used.
The stopping point is delivery of this reusable optimizer and its bounded pilot.
The next action is the user's chosen unattended run or review; further scientific
model development requires a new request. Keep the user-supplied GPT-6 Astra High
context for any later diagnosis; no new context is needed to run the Python program.

A final provenance-only repair makes standalone review repeat the frozen-input
checks used by search and also binds photographic-cue content to checkpoints.
The first sealed models and source are preserved. The repaired program replays the
same192 proposals; scientific search/evaluation functions, final parameters and
native scientific exports are checked against the first seal. This is deterministic
software verification, not a second independent reserved experiment. No objective,
parameter family or selected model was changed in response to reserved outcomes.

## Computation

Before implementation, ten R295 objective calls took0.639s under cProfile, with
4344 rays per call. Repeated centerline loading was avoidable; support/contact and
first-hit tracing dominated. The full-chain objective caches reference/camera
splines and photographic measurements, uses spatial trees and vectorized inherited
rays, and samples supports at two resolutions. Measured full-chain candidate costs
are0.616s coarse/45806 rays and1.025s fine/84464 rays under cProfile. These are
different evaluation workloads, so their scores and timings are not interchangeable.
Fine evaluation includes the ownership beam; coarse screening skips it. Full native
support/visibility checks are reserved for finalists. No unmeasured parallel
speedup is claimed; the delivered search is serial and transactional.

The smoke search takes about seven seconds for eight proposals. The192-proposal
pilot takes about three minutes of cumulative search. Native evaluation/export
adds separate overhead and is not included in the search budget. Candidate records
and final exports consume disk space incrementally; long runs retain completed
scientific results rather than discarding failed alternatives.
