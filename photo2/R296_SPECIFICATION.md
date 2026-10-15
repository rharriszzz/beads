# R296: reusable whole-necklace Phase 2 search

Approved by the user in a new GPT-6 Astra High context. This supersedes the R295
stop for development/testing/delivery of an unattended Python optimizer only.
No Phase 1 changes, synthetic photographs, repeating-pattern inference, beads.pov
edits, production adoption or automatic next experiment.

## Design and alternatives

Profile the old objective before implementation (saved in r296/checkpoints).
Compare (1) bounded population plus coordinate/pattern search and discrete beam,
(2) differential evolution, (3) gradient-based joint fitting. Choose (1): first-hit
visibility/assignments are discontinuous, expensive full-population generations
are unnecessary, and explicit one-proposal transactions simplify exact resume.
No AI supervisor or external service is used at runtime.

Reuse R295's literal annular SDF, projection, visibility, analytic support and
annular-volume fallback. Extend station integration to the entire image-derived
reference; do not extrapolate the bounded R295 integrator. Counts derive from
photographic reference length under candidate camera/spacing, not generator N.
Keep bead zero, positive direction and signed historical -20..200 labels. Closed
hypotheses require periodic position/frame/spacing/phase and integer winding.
Retain an open-seam family because the input spline's closure is imposed in its
lineage, not proof of a physical joint. Test all spatially neighboring pairs,
including across the index seam and distant along-chain approaches.

Freeze geographically separated development/validation/reserved intervals outside
R294/R295's exposed window before implementing/tuning the objective. Existing
accepted judgments are training evidence with exact provenance and unknown physical
ownership. Old reserved R295 regions are retrospective. This is one previously
examined photograph, not new-image or globally blind confirmation.

A: global counts/hands/camera/shape/spacing starts; cheap sampled screening.
B: overlapping sections with smooth shared fields and discrete ownership beam.
C: coherent full-chain reconciliation of those fields, phase/count and packing.
D: repeated geometric/discrete updates, reproducible restarts, diverse archive.
Every promoted model must be physically certified; failures and unresolved pairs
are retained. Geometry-only forecasts are distinguished from observed supports.

Use fixed cached photographic samples, bounded support sampling, spatial trees,
and full native support checks only for final finalists. Separate training from
validation decisions. Reserved outcomes are read only with explicit final sealing;
a sealed run cannot resume. Budget stops produce a resumable development review.
Checkpoint RNG, pending proposal, population, iteration/stopping state and source/
evidence hashes atomically. A hard interruption may repeat only the unfinished
proposal. Record all completed proposals and rejection reasons.

## Delivery gates

Deterministic smoke; bounded pilot demonstrating measured progress; exact split-run
versus uninterrupted candidate sequence; physical and closure contracts; native
support/visibility checks; profiling; desktop/narrow browser review; preservation
hash check; scoped commit/push and independent remote verification. Record failures
and repairs. Document budgets, soft wall-time boundary, limitations, commands and
stopping criteria. Stop after delivering the reusable system.
