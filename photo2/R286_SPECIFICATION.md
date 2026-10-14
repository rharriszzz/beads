# R286 — reliable dark separation and centerline recovery

Active isolated Phase 1 research round on rharriszzz/beads, photo-2-strategy-v3.
This specification preserves the complete scientific requirements and review
judgments before implementing candidates. R286 supersedes prior stopping points
only for this bounded round. Preserve R285 and all historical implementations,
results, photographs and inventories. Do not adopt a production detector here.

## Objective and photographic priority

Distinguish normal shading within a bead from genuine dark separation between
adjacent beads. Growth must stop at meaningful separating darkness. A bright detour
around a dark seam must not automatically override separation evidence. Conversely,
dim diffuse red material remains valid beside an isolated strong reflection.
Do not maximize area, counts, compactness or aesthetic smoothness. Establish
photographically supported interiors and reliable distinctness with uncertainty.

Permanent centerline priority: attempt every bead whose visible body crosses the
image-derived centerline and the relevant nearby beads. When the line passes
between two beads, both are eligible. Increase reliable local coverage toward two
or three observations where actual geometry supports it; never impose a quota.
Prioritize completeness with high precision and explicit uncertainty. At necklace
edges only the clearest obvious beads are required; difficult, shadowed, partial
or ambiguous edge observations may remain unresolved. P4 is a useful separation
test but lower priority than central cases. Never trade central quality for an
edge example. Use photographic support geometry, signed side and station, not
closest centroid or a fitted physical identity, to account for near observations.

## User decisions — supersede earlier preferences

| Case | Review decision |
|---|---|
| P1 / R285 e01 lower yellow | J better; S acceptable |
| P2 / e02 red centerline bead | J poor; S good |
| P3 / e04 yellow brightness-profile case | J better; S slightly worse |
| P4 / e07 two yellow beads near edge | J bad; S acceptable; edge priority secondary |
| P5 / v04 multiple yellow beads | J acceptable; S seriously misses dark separations |
| P6 black reflections | R1, R2, R4 approximately equally acceptable |

These are evaluation/development guidance, never coordinates, desired masks or
certified physical identities in general inference. No manual-label request.
The crucial test is solving P5 without shrinking P2 back to J's narrow core.

## First experiment: explain P5 before replacement implementation

Use original native photograph and saved R285 v04 evidence. Trace:
1. Source cue, refinement and local intensity reference.
2. Diffuse field and smoothing.
3. Learned yellow-material mask.
4. Native dark pixels between the visible neighboring beads.
5. Watershed seeds, feature consolidation and merged basins.
6. Each relevant saddle score and its reference.
7. Actual path/connection or graph reasoning allowing the merger.
8. Whether a brighter route bypasses the visually obvious seam.
9. Whether missing/consolidated markers prevent separation.
10. Whether clipping or background estimation contributes.

Produce raw/native diagnostic images showing bead interiors, dark areas, proposed
seams, intensities, S's merged regions and the precise permitting connection.
Explain in ordinary language. Separate demonstrated causes from plausible but
untested hypotheses. Do not tune a threshold merely until P5 looks acceptable.

## At least three genuinely different candidate methods

Choose mathematically distinct mechanisms, not three nearby thresholds. Possible
families: persistent spatial dark-seam barriers; watershed retaining strong
separation evidence with careful marker consolidation; valley/topology-constrained
growth requiring justification to cross saddles; optional joint neighboring-support
segmentation. An alternate bright route must not erase established separation.
Do not equate multiple peaks with multiple physical beads. Keep ambiguous ownership
when illumination and identity cannot be distinguished photographically.

Preserve diffuse pigment material independently of isolated specular peaks. Use
local background, neighbor and color evidence; do not require every valid pixel
to approach the peak. Test P2 explicitly. Preserve unsuccessful algorithms,
parameters, masks, numerical results and reasons for failure.

## Required review and independent confirmation

P1–P5: original J, original S and every new candidate on identical native crops
and coordinates. Show raw/native/enlarged photographs, initial cue, native support
outlines and filled interiors, photographic centroid, gained/lost pixels,
brightness profiles, detected dark separations, leakage and truncation. Keep
native measurements distinct from any derived/display contour.

Automatically select additional photo regions before examining new-method results.
Prioritize well-exposed centerline-crossing colored beads, near-centerline
neighbors, same-color groups with dark separations, red strong-highlight/broad
pigment interiors, and line-between-beads cases. Include a smaller secondary edge
stratum. Development and confirmation regions must be spatially separate. Freeze
methods/parameters before opening confirmation outputs. Unexpected failure is
reported; any retuning requires a separately recorded development iteration.
No physical centers, indices, maker correspondence charts or pattern hypotheses
may establish observations. Historical image-only measurements and image-derived
centerline are allowed. Whole-body crossing can remain uncertain from interiors.

P6: preserve reflection-only observations and uncertain ownership; R1/R2/R4 all
acceptable. Choose a stable accurate retained method, keep alternatives. Verify
stability, do not spend R286 mainly optimizing reflection smoothness. Never infer
black-body extent from reflection position; Phase2 owns that correspondence.

## Measurements and evidence limits

Measure leakage across photographed dark separations; retention of diffuse
material; merging of neighboring same-color regions; fragmentation/multiple
candidates for one body; connectedness; meaningful intensity-boundary agreement;
centroid stability; local-illumination sensitivity; search-domain clipping;
centerline/near coverage; ambiguity and abstention. Report observation counts
separately from verified distinct beads. State when photographic ownership is not
automatically verified. No compactness/area/smoothness optimization. Use physically
valid synthetic scenes for shading/separation mechanisms when helpful, with
identity truth hidden from inference; actual photographs remain the primary test.

## Architecture and records

Phase1: independent red/yellow photographic interiors and black specular-reflection
locations. Phase2: physical geometry, count, helicity, camera/common light,
visibility and photo-supported color reading. Phase3: weighted physical-inventory
pattern with more than three complete repeats and no partial repeat. Neither
later phase may manufacture or alter Phase1 observations. Do not optimize either
later phase in R286. Preserve their implementations/provenance.

Keep importance, photographic/color reliability, visibility, phase of discovery,
physical identity confidence, native support, measured position and evidence links
separate. All Phase1 observations remain important, including unresolved ones.
No calibrated probabilities without independent calibration. No physical bead
center or certified identity in a pure photographic record.

## Checkpoints and delivery

Save technical Markdown checkpoints after (1) P5 diagnosis, (2) candidate design,
(3) five colored tests, (4) independent confirmation, (5) black stability,
(6) final recommendation. Record hypotheses, exact parameters/implementation,
results, failures and next action. If compacted, reread this specification,
permanent contract and current checkpoints. Do not weaken requirements for context.

Deliver root-cause explanation and diagnostic image; three distinct methods;
P1–P5 native comparisons; P6 stability; independent photographic confirmation;
quantitative successes/failures; centerline recovery accounting; preserved failed
experiments; concise visual review; updated requirements/checklist/handoff/log;
reproduction and scientific tests; recommendation for next Phase1 direction.
Commit/push scoped changes, verify remote tip and final status. STOP for user
assessment, no automatic R287, inventory replacement or global reconstruction.
Keep current model/reasoning; no /new needed. User controls session/model changes.
