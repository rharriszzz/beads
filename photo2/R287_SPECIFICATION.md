# R287 — evidence-based J versus M selection

Isolated Phase1 experiment in rharriszzz/beads, photo-2-strategy-v3. R287 supersedes
R286's stopping point only for this bounded assignment. Preserve all old scientific
implementations, inputs, inventories, outputs and failed experiments unchanged.

## User decisions and interpretation

|Case|Latest user assessment|
|---|---|
|P5, three neighboring yellows|Original J good; original S bad; B good|
|P2, red centerline|J too small; S good; B equally good, not better|
|C05, central red|S/M/B acceptable but not great; others very bad|
|C02, edge-region example|All bad; too close to necklace edge for substantial further effort|

M and B produced identical masks on all five original reviewed colored examples,
but differ elsewhere. B has a demonstrated internal-shading false split. M is the
preferred fuller candidate for investigation; B remains a diagnostic control.
Do not claim B improved P2 when it reproduced S. C02 includes the saved weak-edge
comparison; retain the original anchor/context too so review targeting is explicit.
Reviewed coordinates/judgments select evaluation only, never runtime decisions.
No more manual bead labels requested.

## Permanent measurement principles

Photographic brightness, color and meaningful dark separations govern colored
interior measurements. Retain genuine diffuse material, exclude neighboring beads,
stop at contextual seams, avoid interpreting internal shading as physical identity.
Supports need not be entire silhouettes; connect to appropriate native evidence.
Compactness, smoothness and morphological pruning are secondary aids. Neither
remove narrow material simply for width nor admit all material reachable by a
bright detour. A coherent dark seam between separately illuminated surfaces should
generally prevent common ownership. If image evidence cannot distinguish a seam
from internal shading, retain uncertainty.

Black means specular-reflection regions only. R1/R2/R4 remain acceptable; keep R2
as the existing experimental default without major redesign. Separate reflections
and unknown ownership survive; Phase2 identifies their physical sources.

Centerline priority: attempt every visible crossing bead and relevant nearby
observations, including both sides when the image-derived line passes between
beads. Seek two or three distinct reliable observations where supported, no fixed
station quota. Edge beads need only be clear and convincing; difficult/shadowed
edges remain unresolved. No central tradeoff to rescue C02.

## Central question, evidence and planned hypotheses (before implementation)

Can photograph-only evidence choose among prefer J, prefer M, both comparably
supported, neither reliable/abstain? Preserve J/M separately for every cue and
save all evidence/reasons. No global color-based choice, large classifier or
high-dimensional fitted score. No naive union/intersection hybrid.

H1: J truncation can be indicated by a sustained bright/pigment continuation
across J's boundary into M-only material, provided that added material has no
coherent intervening seam or competing-marker ownership conflict. A large area
alone is not evidence. Specular-to-diffuse contrast should explain the threshold.
H2: a spatially coherent valley across multiple nearby native routes, with locally
supported illuminated features on both sides, can reveal M merger risk even when
a brighter detour exists. Multiple markers alone do not certify multiple beads.
H3: local inside/outside boundary transitions and modest perturbation stability
can veto unreliable candidates; neither maximizing gradient nor stability alone
proves correctness. A highlight-core contour can have stronger gradients.
H4: both and abstain are scientifically necessary outputs. Ambiguous differing
interiors must not be forced into a single owner. Edge uncertainty is cheap to
retain; central unresolved observations remain important coverage gaps.

Planned interpretable experiment: unchanged J/M/B controls; local evidence ledger
for native inner/outer boundary samples, connected dark/bright boundary stretches,
multiple parallel marker-to-marker intensity profiles, diffuse-only gains/losses,
context-supported marker positions and material compatibility. Compare two simple
selection policies if needed: evidence ranking versus conservative veto/partial
ordering. Preserve first policy/results if a more conservative revision is needed.
An optional hybrid is allowed only for independently evidenced material; omit it
if choices/uncertainty suffice rather than inventing an area-maximizing union.

Stability must include brightness, contrast, smoothing, local background, seed
position and search size for BOTH candidates. Save actual perturbed masks/metrics,
state conditional feature assumptions, flag radius clipping. Do not interpret a
computational circle as a measured dark boundary. Hold-out parameters are frozen.

## Development and independent selection

Development includes exact P5/P2/C05 and low-priority C02 edge comparison, with
original native coordinate conventions; inspect C04 unresolved merger and C07
overlapping cues. Include same-body overlapping proposals, weak visible seams,
J diffuse truncation, plausible disagreements and crossing losses. Preserve their
alternative explanations. Original S is contextual evidence, not a new candidate.

Before new selector results, automatically freeze approximately12–20 new real-photo
regions (target16), central-heavy, varied red/yellow, crossings, same-color groups
and opposite-side pairs. Use only pixels, prior photo-only cues and image-derived
curve. Spatially exclude previously examined crops; choose reproducible hash/strata,
never favorable selector performance. Save any selection feasibility adjustment
before seeing candidate outcomes. Include neighboring cues to expose duplicates,
not merely isolated good anchors. Freeze selector source/parameters before opening
confirmation outputs. No silent retuning; any subsequent development version must
retain the first confirmation and be explicitly separated.

## Evaluation and review outputs

Compare always-J, always-M, B, evidence selector and optional justified hybrid.
For every reviewed and confirmation example show raw native and enlarged pixels,
J/M contours and exact fills, selector decision/reasons, B, seed/photographic
centroid, coherent dark-seam routes and diffuse-material diagnostic, uncertainty.
Include a small front-page review with deeper panels/atlases available.

Measure J/M agreement/IoU and differences, preference/both/abstention frequency,
boundary transitions, retained diffuse material, apparent seam leakage, illumination
and seed/domain sensitivity, clipping, duplicate/overlapping ownership, support-near
and measured crossings, signed opposite sides and longitudinal groups. Count
observations separately from overlap groups and verified distinct bodies. Explicitly
assess whether any new distinct bead is genuinely recovered; selection alone may
not create new observations. No real numerical precision/recall without independent
truth. Synthetic mechanism/physical controls may help but cannot outweigh actual
photo failures. Report wrong-looking choices and unjustified decisiveness, not only
success. Do not maximize area, smoothness, compactness or observation counts.

## Architecture/provenance and working process

Phase1 independent colored interiors/reflections; Phase2 physical geometry, camera,
shared light, total count/helicity, visibility and measured color; Phase3 weighted
pattern with >3 complete repetitions and no partial repetition. No Phase2/3 work,
model-derived center/index/visibility or pattern input to Phase1 selection. Preserve
importance, photographic and color reliability, predicted visibility, physical
identity confidence, discovery phase and source observation history separately.
All Phase1 observations remain important; unresolved identities remain unknown.

Maintain checkpoints for requirements/selection, baseline diagnosis/evidence,
selector design/development (including failed policies), frozen confirmation,
quantitative/coverage review, final recommendation and verification. Save parameters,
hypotheses, exact data, failures and next steps. After compaction reread these files;
do not simplify the assignment, abandon experiments, or use /new to save context.

## Delivery and required stop

Deliver documented latest reviews, an interpretable evidence selector, separate
controls, dark-seam/diffuse explanations, all reviewed cases, independent central
confirmation, quantitative uncertainty/coverage, compact photographs, reproduction,
scientific tests and updated permanent contract/checklist/handoff/recommendations.
Optional hybrid need not be included if not justified. Preserve prior outputs.
Commit/push scoped changes, verify remote commit, leave worktree clean. STOP for
user assessment; no adoption of production Phase1, automatic R288, global physical
reconstruction or pattern inference. Keep current model/reasoning; no /new needed.
