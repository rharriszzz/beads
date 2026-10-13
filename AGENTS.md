# Beads photo-2 workflow

Read SESSION_HANDOFF.md, the latest REQUEST_LOG.md entries, PLAN.md and the
relevant experiment before continuing. Current user instructions override old plans.
This branch starts at origin/master 020303e (the remote has no main branch).
Historical work remains on photo-2-reconstruction; see photo2/PRIOR_WORK.md.

R272 authorizes measured interiors and a minimal standalone viewer; see
photo2/TRUSTED_INVENTORY_R272.md and photo2/trusted_inventory_r272/index.html.
Uniform image-only gates yield 255 measured proposals from preserved R271's 453;
181 yellow/74 red, no fabricated black category. Black reflection-only logic is
tested synthetically. Native masks/counts/centroids/ICC peaks remain separate from
smoothed display contours. IDs are source-image location IDs, not string indices.
Strict paths, color/brightness, retreat, stability and ownership gates may withhold
a region even for a trusted location. Preserve all exclusions. User prioritizes
counting failures of each requirement despite otherwise reliable evidence, especially
background/illumination; never optimize detection count. Diagnostic single-gate
omission finds 1 background/23 brightness/45 uneven-light otherwise-passing cases;
none is promoted. 12 tests/32 browser checks and native/synthetic validation pass.
Stop after delivery. Next only requested review of interiors and failure examples;
no geometry/indexing. Historical results/viewers remain unchanged. No /new needed.

R271 clarifies the active objective: a widespread highly reliable subset from one
automatic algorithm, not all visible beads or maximum count. See
photo2/TRUSTED_LOCATIONS_R271.md. Use original-plus-cyan-dot photographs; uncertain
candidates separately with plain reasons. R01284's shadowed neighbor is real but
its location is untrusted; global brightness criteria exclude it automatically.
No reviewed coordinates or manual identities enter selection. Isolated mean7 Y
experiment requires brightness, broad illumination support, size, contrast,
background clearance, multi-window/search stability and unambiguous maxima.
453 proposals across 15/16 image areas await review; all 40,483 candidates/reasons
survive. No quotas, count optimization, geometry or indexing. Production unchanged.
Next only when requested: review false trusted dots and geographic gaps. Stop after
delivery; keep current model/reasoning, no /new needed.

R270 compares brightness measures; see photo2/BRIGHTNESS_COMPARISON_R270.md.
Recommend ICC-managed sRGB luminance/7×7 for photographic review only. Preserve
native V baseline, all independent maxima, original starts and full competing paths.
Y/OKLab reach the pale R01284 patch and improve R00956 yellow coordinates; main
raw24/mean2 guards preserve the named neighbors. Mean6/9×9 still crosses with all
scores. Synthetic background/invisible-interface failures remain explicit. 18 tests,
1,195,833 checked moves and exact old V replay pass; prior evidence is unchanged.
No production adoption or growth/viewer/geometry/indexing changes. Stop after
commit/push; next review photographs only when requested. No /new needed.

R269 extends R268 peak-location review: see photo2/BROADER_PEAK_SEARCH_R269.md.
Broader radius3/6/10/16 search improves middle/lower R00956 coordinates; all original
maxima/paths survive. Pale R01284 peak (976,2668) is exactly5 pixels from mean9
endpoint: raw248>244 but mean9 229.16<238.47. HSV Value ignores stronger G/B channels
there; do not equate highest mean V with the best photographic coordinate.
User confirms central/shadowed origins are separate beads. Raw24/mean2 keeps the
named proposals separate, mean6 crosses incorrectly. This fact is review evidence,
not runtime manual identity. No production detector or outline change.13 tests and
all97,998 selected moves pass; old evidence hashes match. Stop after delivery.
Next only if requested: brightness-score comparison sensitive to pale highlights,
with preserved competing peaks and separate-neighbor checks. No geometry/indexing.

R268 supersedes the R267 next-step restriction: see photo2/CLIMBING_MAXIMA_R268.md.
Native 5/7/9 mean-V climbing improves some coordinates but does not establish one
endpoint per bead. Preserve all 451 starts, 8,118 photographic traces and six guard
controls. Equal-score plateaus are diagnosed without equal moves. Unguarded 9x9
can cross adjacent yellows; guarded12 prevents the named crossing but weak starts
and invisible boundaries remain limitations. 13 tests and 360,078 checked moves
pass; production and old evidence remain unchanged. Background remains fixed.
Next only when requested: review competing/converged foreground endpoints and
weak-start failures before adopting a selector. No outline optimization; stop after
delivery. Synthetic truth is evaluation-only and never a photographic runtime input.

R267 audits all native maxima before growth; see photo2/LOCAL_MAXIMA_R267.md.
241 plateaus/298 maximum pixels in R00956/R01284, all six neighborhood means,
exact prominence, photographic maps and original selection reasons are saved.
Low-prominence interior candidates were excluded before the mixed R266 score.
Averaging gives useful alternatives but the old bridge can cross adjacent yellow
areas; no revised detector adopted. Frozen growth retains irregular support.
Background is established per user steering; keep it fixed, no new FFT/background
or outline optimization. Next only when requested: pre-growth candidate retention
and adjacent-bead separation. Stop after delivery; preserve all previous results.

R267 later steering: user says hue alone suffices for background in this photo and
asks to discard small ambiguous regions. Final review candidates exclude frozen
supports below12 native pixels (existing recovery cutoff); all evidence survives.
Both fixed-background+size and literal existing-paper-hue-band+size controls are
saved at all six averaging scales. Recommend the fixed-background+size review;
the broad hue-only band also removes some tinted reflections, so it is not silently
adopted. No production detector or outline rule changed; background remains fixed.

R266 supersedes the R265 next-step restriction: see photo2/DETECTION_R266.md.
Strict light-to-dark0 DN is primary;1–3 DN are diagnostic only. Annular comparison
uses one-native-pixel fixed-parent shells, irreversible stopped sectors and optional
native-valley split proposals. Preserve R265; do not automatically adopt annular.
Recommend saved straight-0-selected12 conservatively; annular-0-selected12 and6/3-DN
recovery alternatives remain available. All maxima/suppression/deferral evidence
survives. Runtime inputs are the photograph and parameters, never review coordinates.
80 Python tests and44 preserved +59 new browser checks pass. Named failures improve,
but residual duplicates, weak recovered candidates and paper-facing artifacts remain;
no whole-photo bead count or complete recovery claim. Stop after delivery; revisit
annular only when requested. No geometry, indexing, lighting inversion or patterns.

R265 supersedes the R264 next-step/default instructions below. Read
photo2/DETECTION_REPAIR_R265.md and photo2/FIRST_DARK_R265.md. User requires
straight native seed-to-pixel paths and stopping at black without seeking the
next bright region. Black-bead shading progresses through gray; not HSV zero.
Use repaired_detect: local connected retreat, learned HSV seed gate,870 cap,
strict descent,hue10°. Neutral-black means V≤min(81 DN,.5×seed peak) with low
saturation/channel spread; preserve dim gray reflection seeds. Trace full straight
histories and gray fractions; do not classify every dim colored pixel as black.
The v1 comparison remains in straight_detect_r265 and review/r265; final added
step is review/r265-first-dark.64 tests pass. Residual paper contamination,
M1–M5 misses and12 reviewed duplicate pairs remain; no whole-photo success claim.
Next review those residual seed/identity failures; do not launch another phase
without the user's instruction. Final viewer work is output/r265-first-dark/joint.

Historical R264: R264 hue comparison is delivered: see photo2/HUE_COMPARISON_R264.md.
Recommend saved8° provisionally; preserve10°/12° alternatives and the unchanged10°
detector baseline. Six main review crops show12 apparent duplicate extras and
4 stronger +1 tentative misses at5°/8°; >=10° loses one additional red location.
These are scoped visual judgments, not a whole-photo census. Leaf sensitivity
changes coordinates; no retreat repair was applied. Optional Q264.1 remains pending.
Next proposed bounded task: explicit retreat-repair comparison, not another hue
search, ownership partition, geometry, indexing or pattern work.

R263 size limit: user accepts the estimated30×29 native-pixel bead rectangle
(870px bounding-box area) as the basis for a HARD do-not-exceed region limit of
870 distinct native pixels. See photo2/BEAD_SIZE_REFERENCE.md. This is an operational
ceiling, not a measured global maximum. Minimum size is separate and may use more
arbitrary tunable criteria. The guard is implemented before retreat; an eligible
871st pixel flags/rejects the proposal and preserves stops. Current R263 default
has no watershed, strict brightness descent, prominence35, minimum peak0, hue10°.
See photo2/PARAMETER_SEARCH_R263.md.1,552 supports are not a verified bead count.
Completed R264 hue sweep:5°,8°,10°,12°,15°,20°, all else fixed. User observes
red/yellow look more similar in shadows; assess those transitions separately.
The prior15-minute search is finished; do not restart it automatically.

R235 Stage 1 overrides older central-body/sliver exclusions: distinct red/yellow
patches with roughly >=10% of unobstructed projected bead area and convincing
color qualify. Black eligibility requires an obvious reflection plus dark-body
evidence; no-reflection black remains deferred, not a Stage 1 detector miss.
Keep observed patches, representatives, centroids, reflections and inferred
centers distinct. See photo2/STAGE1_PILOT.md for the completed four-section pilot.
Stop for review before global indexing. Make routine technical decisions;
ask visual questions only when their answers materially affect conclusions.

R261 supersedes radial growth as the default. Use the native-pixel detector and
replay in photo2/PIXEL_DETECTION_R261.md. No detection blur, rays, interpolation,
or angular smoothing; display smoothing never changes masks. Preserve all maxima,
noise rejections, adjacent-pixel predecessors and irreversible stop reasons.
Multiple supports remain ambiguous; do not treat 3,204 supports as a bead count.
No manual bead-marking request. Next review duplicates/missed visible locations,
not full outlines, geometry or global indexing. R259/R260 remain historical.

R260: prioritize good per-bead image coordinates, not pixel-complete masks. Compact
support is sufficient when its location reliably identifies one bead. Black growth
stops at the first fully dark perimeter surrounding a reflection, not the full body.
Keep supported locations, area centroids, bright patches and physical centers distinct.
The user explicitly authorizes greater stopping sensitivity across the photograph.
The requested strict-darkening/retreat and relative-hue/dark-clue comparisons are
saved separately from the default detector; do not conflate their sampled signals
or interpret possible dark material as a confirmed black bead.
See photo2/DETECTION_REVIEW_R260.md; review coordinate comparisons and missed/duplicate locations next.

R236: user reports actual session status as GPT-6 Astra, reasoning High and will
report changes. Do not identify the active model from older recommendations;
distinguish user-supplied status from recommendations for future work.

- Work on one aspect at a time. Present 3–6 methods before selecting a new phase's
  implementation. Ask frequent, small illustrated questions; preserve answers.
  Put questions in tracked files and commit their curated supporting images.
- Background includes all visible paper, including necklace shadows and gaps.
  Prefer color-independent evidence; do not hard-code magenta as the definition.
  R106: all supplied computed/actual images place the bracelet in the middle with
  substantial margins. Use this generic framing prior for background initialization;
  no numeric margin width or bead coordinates are supplied. Enclosed paper and
  gaps remain background even without a connection to the image border.
  R108: background separation serves a useful smooth spline that excludes cast
  shadow. Do not require pixel-perfect masks before later geometry refinement;
  prioritize broad shadow-induced bias, supported coverage and explicit uncertainty.
  R096 notes shadowed-paper/bead HSV overlap; retain texture/context and explicit
  uncertainty rather than forcing a color-only threshold.
  R100–R102 confirm the maker's labeled evidence and identify the overlapping
  white-balanced HSV map; see photo2/HUE_TRANSITIONS.md before reusing ranges.
  Local hue changes can still help; preserve circular hue and image/unit conventions.
- R103: final inference must have little prior knowledge of the image's colors or
  bead locations. Hand-selected routes and saved color ranges are diagnostic/
  validation references, not final runtime priors. Estimate appearance and location
  from each input; test changes of palette, background and placement before claiming
  generality. Do not silently promote diagnostic coordinates or hue boxes into code
  that is presented as automatic reconstruction.
- User R093 rejects the later edge correction's implausible indents and bumps.
  Show raw crops next to candidate outlines and uncertainty before propagating
  those outlines. Do not smooth away real bead-scale scallops indiscriminately.
  R105: when a local boundary is ambiguous, search farther along the necklace
  in either direction for reliable boundary evidence, then bridge using smoothness
  at the larger necklace scale. Keep bead-scale scallops separate. Mark inferred
  stretches distinctly; smoothness alone does not verify an anchor or a gap.
- For shape/geometry/helicity, first read the quick model in photo2/PRIOR_WORK.md.
  Necklace centerline lies in the paper/table plane. Beads are three-dimensional.
  Keep helicity separate from section direction relative to the global camera.
- Use Python 3.12 (.venv/bin/python) for analysis and POV-Ray for scene appearance.
  Material means POV-Ray pigment/finish/normal/interior, not physical composition.
- Preserve missing indices and color uncertainty; test inverse claims against
  known synthetic examples. Photo-sampled rendering is not recovered bead order.
  Ignore slivers in active inventories; historical beads1 marker 211 is excluded.
  R111: explore FFTs for background/shadows and for directions/spacings/helicity,
  but adoption is optional and not a gate before useful index/color work. Target
  bead_index and color for every clearly visible body; keep observation IDs,
  local component indices and resolved full-string indices distinct. Unresolved
  visible bodies remain in coverage accounting instead of being dropped.
  R117 supersedes a black-bead exclusion: black bodies are locatable, roughly
  twice as difficult per the maker, not unusable. Establish a 5–12-body patch;
  use Python placement/projection or walk the six neighbor directions around
  the necklace. R118–R119's outward anchor is in the minor-circle direction,
  away from the rope's local centerline; validate its exposure separately.
  R120–R121: ignore edge/behind-edge beads in active fitting and walking; target
  substantial central bodies, including black. Preserve excluded regions and
  missing slots without requiring their resolution or compressing indices.
  R122–R125: signed direction counts (n1,n6,n7) are useful discussion labels,
  especially for a bead's +/-1, +/-6 and +/-7 neighbors; they need not be the
  fitter's internal coordinates. Derive index = origin+n1+6*n6+7*n7 when supported.
  Different path triples can name the same bead; check weighted sums, retain
  stable observation IDs and mark tentative edges. Source-loop indices
  in calibration are not inferred photo labels. Runtime selection must remain
  image-derived, not fixed color ranges/coordinates. Clear colored beads may seed
  the patch, but the earlier three-body-only shortlist is no longer the goal.
  R127–R128: no camera elevation estimate is supplied. Specular reflection couples
  camera and lighting. Photo was made with an iPhone, likely fairly close; test
  perspective using available metadata without treating unknown crop/distance
  as calibrated intrinsics. A fitted camera/phase gauge is not measured elevation.
  R112: photo-2 repeat length is not divisible by 13; this is not a restriction
  on total bead count or generic synthetic tests. With verified exact N, test
  divisors for the shortest repeat compatible with all visible observations.
  Preserve unknown slots and conflict witnesses; visible-only indices do not
  establish N without closure. Do not claim a recovered pattern from proposals.
- Explain measurement paths: raw context, interior endpoints and reasons, sampling
  route, then measurements and limitations. Highlights are not boundary markers.
- Inspect machine, branch, upstream, status and stashes before writes. Preserve
  unrelated work. Synchronize deliberately; no rebase/autostash by default.
- Record supplied requests and actual outcomes in the append-only request log.
  Preserve source hashes, parameters and reproduction commands. Keep routine
  generated outputs and environments ignored; curated question images are tracked.
  INITIAL_QUESTION.md consolidates the opening request and construction facts;
  METHODS.md is the reusable procedure index. Keep proposals, evidence and maker
  facts distinct, and link experiments instead of duplicating their full records.
- Update plan/log/handoff at each bounded step. Add/commit/push scoped work unless
  qualified by the user; verify remote tip and final status before claiming delivery.
- End with a concrete next task, stopping point, model/reasoning recommendation
  and whether to use /new. User controls model/session switching. Do not invent
  supplied status or usage. No computer ownership transfer is implied by checkout.
- A standalone "continue" resumes the unfinished bounded step, then follows this
  routine and stops. Do not automatically advance to the next aspect.
