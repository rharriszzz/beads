# Full R290 request received and implemented

The later complete request supersedes the preparation status below. See
R290_SPECIFICATION.md, R290_REPORT.md and R290_CHECKLIST.md for the full scope,
results and delivery. The following original preparation record is retained.

# R290 — received requirements and preparation status

Repository rharriszzz/beads; branch photo-2-strategy-v3; directory photo2.
Preparation starts from clean delivered R289 commit
69ac0f0201b538773ecbe9d0595026fa8827d4f4.

The request currently ends mid-sentence in section3:
“Before implementing the new detector, establish a permanent, extensible collection
of photographic evidence tests. The tests should address distinct mechanisms and,
taken together, cover the important situations present in the original”.
The missing remainder has been requested. The evidence-test collection and detector
must not be finalized against an invented continuation. No detector implementation,
scientific evaluation or new experiment has run during this preparation.

## Requirements received

Develop fully automatic, photograph-driven detection of the boundary of one visible
bead per invocation, initialized by an independently detected bright point or patch.
Return a reliable complete boundary when supported; preserve useful partial
boundaries when necessary; abstain when reliable determination is unsupported.
The user evaluates results afterward and does not construct or manually segment
boundaries.

All R290 scientific evaluation must use the original real photograph. No synthetic
images, synthetic bead scenes, generated photographs or POV-Ray experiments.

Nearby pixels, seams and bright features may inform the target boundary. Do not
simultaneously segment or physically reconstruct neighbors. Multiple highlights
may appear to share a region; retain uncertainty unless common ownership is
established.

Never reject a real photographed bead for an implausible shape, size, outline or
apparent geometry. Distortion, occlusion, crescents and unexpectedly large/small
regions can be real. Geometry may bound computation and signal possible errors,
but cannot override photographic evidence. Do not implement an implausible class.

Preserve the user's new confirmation: all displayed marks in R289 red-worst.png
belong to the same physical bead. R275/new-feature centroid disagreement does not
establish distinct beads. Preserve R215 and R284–R288 judgments with their original
image and coordinate references. These are evaluation evidence, never coordinate-
specific runtime rules.

Coherent dark transitions must be a primary photographic measurement. No particular
number of radial sampling directions is prescribed. Before detector implementation,
establish the permanent extensible collection of evidence tests; remaining test
requirements are pending receipt of the rest of the request.

## Preparation completed

Read current handoff/instructions/plans and latest request log. Located the R289
case/marks, original R215 answer files and R284–R288 review/specification references.
Saved the new ownership fact and hashed links to previous photographic judgments in
r290/evidence/user-judgments.json. Historical scientific artifacts remain unchanged.
This evidence registry is provenance preparation, not a frozen test selection or
a boundary ground-truth dataset.
