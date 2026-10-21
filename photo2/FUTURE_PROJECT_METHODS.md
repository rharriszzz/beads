# Better investigations: methods learned from the bead project

R348, based on the [retrospective](RETROSPECTIVE.md), the R347 delivery at
[5d605663](https://github.com/rharriszzz/beads/commit/5d6056634009310bd2d47744527f9db43f0809c9),
and a [bounded graph sensitivity check](r348/SENSITIVITY.md). These are recommendations,
not new reconstruction results. No time-saving estimates or universal accuracy
claims are implied. “Strongly supported” below means the history directly exposes
the relevant failure mechanism; it does not mean an alternative full project has
been run and measured.

The most consequential change would be to organize work around **claims that can
be tested**, with a small trusted real-data reference and an explicit decision
after each experiment. A detector score, executable renderer, preserved artifact
or more elaborate optimizer is useful when it advances such a claim. It does not
establish the claim by existing.

## 1 Choose the abstraction from the deliverable

Write down the desired output and what must be known to produce it. For a color
word, the key unknowns are discrete body identities, neighbor families, string
order and pigment. A precise camera, complete segmentation and calibrated glass
are not prerequisites. For a physical rendering, those continuous unknowns become
important, but should be introduced with constraints that identify them.

Use the representation that retains relevant information while exposing its
uncertainty. Image pixels establish appearance; graph edges establish proposed
relationships; integer coordinates expose consistency; a symbolic word exposes
periodicity. A centerline can help locate patches without being a measured
physical axis. Avoid forcing every layer to inherit the certainty of the previous
one. A small graph plus partial word was practical once the maker's neighbor rule
and manual direction series existed; it was not necessary to await the final
renderer. [Manual chart analysis](LABEL_SERIES.md),
[joint photographic inference](R323_REPORT.md), [connected growth](r328/grow.py).

Before building a general system, try a compact explanatory prototype: can several
trusted patches and an incomplete symbolic pattern resolve any held-out order or
color? Compare that with what a physical model adds. The cost is a small amount
of deliberate annotation and two simple baselines. It is working when an error
can be attributed to identity, topology, color or geometry, rather than answered
only by another combined image loss. If neither abstraction predicts anything
independently, improve measurements or obtain another view before adding detail.

## 2 Separate three kinds of failed reconstruction

These diagnoses require different interventions. A bad fit alone distinguishes none.

| Diagnosis | Evidence needed | Small discriminating test | Appropriate response |
|---|---|---|---|
| **Search or numerical failure:** a valid solution is representable but the implemented inverse procedure misses it | A known feasible parameter/assignment combination with better accurate evaluation than the returned fit | Evaluate the generating truth directly; fix owners first; then initialize near truth and perturb selected blocks; compare cheap and accurate forward evaluations | Repair search, approximation, bounds or numerical treatment before enlarging the real-data campaign |
| **Representation or model failure:** the admissible model cannot satisfy the required observations/physics | A justified contradiction or controlled relaxation that identifies an excluded necessary behavior; finite search failure is insufficient | Try an interpretable added freedom on a trusted local case; check whether it resolves a specific contradiction while preserving others | Revise the representation or constraints; do not buy more iterations of the unchanged search |
| **Measurement nonidentifiability:** distinct valid solutions explain available evidence | Competing physical/topological solutions meeting the same checks, or an exact gauge symmetry | Profile competing hypotheses, compare predictions in a withheld region or new view, and identify the observation on which they differ | Report an equivalence class or conditional result; acquire discriminating evidence rather than demand a unique number |

R301 is a concrete first-category warning: the exact generator replays synthetic
positions with zero error while inverse searches miss the known geometry, including
known-owner cases. Its coarse predictor also moves or misses lobes. That exposes
search/approximation failure; it does not establish that the real image uniquely
identifies the truth. [Truth checks](r301/results/synthetic-truth-check.json),
[recovery results](r301/results/synthetic-analysis.json), [search](r301/search.py).

An **objective/measurement-target failure** cuts across that table: the model may
contain a good reconstruction and the optimizer may correctly minimize its loss,
while the loss rewards the wrong scientific answer. Count agreement in R263 and
reflection improvements accompanied by missing material in R301 illustrate this
possibility. Check independent task constraints before blaming either model
capacity or optimizer convergence. Optimizing the surrogate more accurately can
make this failure worse.

R321 supplies a narrower model/constraint example: changing the spacing law removes
collisions in a closed candidate. The older collision is not proof that no physical
necklace can close. R160's two refitted family interpretations and the scale/camera
gauge illustrate measurement ambiguity. R319's affine minimax bounds apply only
to its local secant model and box; they do not certify a nonlinear model's global
failure. [R321](R321_REPORT.md), [two-family refit](INTERIOR_REFIT.md),
[R319 limits](R319_REPORT.md).

## 3 Build a small evidence reference before broad automation

Create a stratified set of clear bodies and difficult but answerable examples:
different regions, colors, occlusions and shadow conditions. Record stable source
IDs, exact original pixels, view/region, proposed body grouping, owned pigment
patch, neighbor direction, authority and remaining alternatives. Mark genuinely
unreadable cases unknown. A manual body annotation can validate a detector without
becoming its runtime input. Reserve distinct bodies/regions for checking; repeated
pixels and aliases of one body do not create new observations.

Keep **feature → body → site → string index → pattern prediction** as explicit
relations. Each may be one-to-many or uncertain. Store role eligibility separately
for pigment, indexing, counting, obstruction and geometry. For example, a weak
glint may remain a useful lighting feature while supplying no distinct-body
constraint. R336 made this distinction actionable; R343 showed that general
approval of a diagram must not become explicit pigment truth. [Typed evidence](r336/evidence.py),
[role handling](r336/revise.py), [authority correction](R343_REPORT.md).

The cost is annotation and provenance maintenance. The benefit should be visible
as fewer duplicate/phantom identities, interpretable disagreements and measurable
performance on bodies not used for method selection. Maintain a small clear-body
sentinel set as well as a difficult-case set: otherwise regression review can
gradually concentrate on peripheral examples that cannot answer the main question,
as R293 found. A reference selected from one repeatedly studied photograph remains
exposed development evidence, even when a later round calls its labels “held out.”

For dark edges, distinguish absent evidence from evidence of absence. A clear
black body need not have a bright specular reflection. A dark paper/edge component
with neither reliable body ownership nor usable reflection context should not
force a body or pigment label. Apply that rule before checking pattern agreement;
do not discard an otherwise sound contrary observation because it is inconvenient.
The [R348 sensitivity example](r348/SENSITIVITY.md) demonstrates why pigment null,
identity uncertainty and node deletion need separate accounting.

## 4 Make experiments choose between explanations

Before running an experiment, specify the claim, competing explanations, fixed
inputs, deliberate intervention, independent observable and possible decisions.
For example: “Is local regression caused by camera, bead shape, station
normalization or phase?” changes one mechanism at a time while preserving the
same observations. R297's paired interventions answered this more directly than
another longer combined search. [Paired diagnosis](R297_DIAGNOSIS.md),
[saved comparisons](r297/results/paired-diagnosis.json.gz).

Use different controls for different questions:

| Control | What it diagnoses | Qualification |
|---|---|---|
| Known-answer forward/inverse case, known owners first | Can the implemented search find a representable answer? | Test identifiable outputs or gauge-equivalent solutions; exact recovery of unidentifiable parameters is an invalid demand |
| Synthetic scenes exhibiting a recorded real failure | Does the proposed repair address that failure mechanism? | First verify the old broken method fails this fixture; R231's old seeds passed its synthetic ownership controls |
| Geographic/whole-occurrence holdout | Does structure predict separated observations instead of memorizing neighbors? | Exclude aliases and correlated adjacent context; record historical exposure; do not relabel targets to improve prediction |
| Matched simpler baseline and ablation | Is complexity or a new component doing useful work? | Use the same target set, eligibility, starts and budget; report abstentions and rejected cases |
| Competing orientation, topology, period or null model | Is the favored explanation distinctive? | Test coherent alternatives and their own closure; frequency alone can explain black-heavy corrections |
| Perturbations and region-specific comparisons | Is the result stable and does an average hide a failure? | Perturb within defensible measurement/numerical uncertainty, not an arbitrary adversarial range |

Preserve failures and use them to define the next test. Stop an experiment when
its planned alternatives cannot be distinguished with the current observable;
do not substitute a conveniently improved score. Reserve compute and annotation
effort for a named unresolved decision. This costs planning and sometimes one
additional control; it works when a negative result changes what is tried next.

## 5 Audit optimization before spending on it

Build a parameter map: meaning, units, gauge, physical constraint versus numerical
bound, actual active code path, expected output effect, initialization and tested
joint range. Perturb each proposed variable through the actual evaluator, including
both signs and more than one scale. A field in a saved JSON object is not evidence
that the forward model uses it. Check periodic wrapping and coupled normalization.
R319 found inactive legacy parameters and nearly duplicate response columns;
R311 found a much smaller effective search than the nominal boxes suggested.
[Inactive-key checks](r319/tests.py), [space audit](r319/results/search-space-audit.json),
[coverage audit](r311/results/audit/coverage.json).

Use small known-answer inverse problems before global fitting. Evaluate truth
under both accurate and screening predictors, then test near-truth recovery,
dispersed starts and discrete alternatives. Add unknown ownership only after the
known-owner case is understood. Compare recovered visible geometry and predictions
as well as parameter values; report gauges rather than penalizing equivalent
solutions. If cheap approximations change rankings, retain diverse hypotheses
for accurate evaluation instead of accurately refining only the cheap winner.

When enlarging the domain, preserve actual local station maps, phase progression
and projected surfaces, not just parameter names. Compare old-region predictions
before starting optimization. Reparameterization must either embed the old fit or
explicitly record why it cannot. Protect trusted local constraints with regression
checks and show geographic tradeoffs separately. R297's normalization changed the
old metric; its preservation term made a real tradeoff visible, not cost-free.

For discrete and continuous variables, start separated when topology is supported
directly by the image: infer several graph hypotheses, then fit continuous geometry
for each. Alternate only when each stage has an observable cross-check and retains
losing coherent alternatives. Combine them in a factor/constraint formulation when
dependencies are explicit and the small problem can be audited. Avoid joining the
best edges from mutually incompatible whole-patch hypotheses; R326 exposed exactly
that error. A larger optimizer does not repair inconsistent inputs.

The cost is a preflight suite and a compact search ledger. It is working when
inactive variables, missed starts, boundary causes and local regressions are found
before a large run, and when search failure is reported separately from model
inadequacy. No finite sampling ledger certifies global optimality.

## 6 Preserve decisions as well as files

Keep immutable experimental products, original evidence and failed epochs. Add a
short current claim register with columns: claim, status, premises, supporting
source, counterexample/alternative, exposure, next discriminating evidence, and
superseded decision. Statuses should distinguish measured, maker-judged,
conditionally derived, predicted, rejected and unknown. Link to the detailed
archive instead of copying it into every handoff.

Before a new round, consult this register and reuse relevant cached measurements.
R332 associated 122 of its 126 additional observations from older caches; the
missing work was often association and presentation rather than new detection.
Preservation would have helped more if those sources and unresolved relations
had remained visible in an operational inventory. [R332 accounting](r332/results/summary.json).

Version the question as well as the answer: original view, feature number,
precise claim and evidence basis. R347's Q1 selected yellow but explicitly relied
on the reconstruction and requested exclusion; a parser looking only at the
dropdown would manufacture confirmation. Keep old and new cohorts alongside
color corrections and removals. An improved percentage after exclusion must show
its denominator and what excluded evidence would have said. [Raw maker answers](r347/answers/maker-2026-10-20.json),
[assessment](r347/answers/ASSESSMENT.md).

This adds modest editorial work to already strong provenance machinery. Check
that a new investigator can find the current claim and its strongest challenge
without reading every round, and that no superseded assumption remains a hidden
filter. Preserve stop points and scoped authorization; improve the scientific
decision inside each stop rather than automatically launching the next refinement.

## 7 Practical workflow for another bead object

### Acquire information appropriate to the task

If the object is accessible, record the maker's known construction facts and any
original chart separately from guesses. Photograph on a matte, distinguishable
background with enough resolution to see bodies and neighbor relationships. Keep
original files and color profiles; avoid clipped highlights and unexplained
resampling. Include a scale and neutral/color reference when dimensions or color
transfer matter. A reference does not undo occlusion or severe mixed illumination.

For **pattern only**, overlapping views obtained while rotating or gently turning
the tube are often more informative than a perfect single view. Use broad, stable
illumination to reveal pigment; a supplementary lighting direction can expose body
boundaries. Maintain identifiable overlap and record the handling so cross-view
aliases are not counted as new beads. If the object deforms, share identity/order
between views but do not force a rigid 3D registration. For an existing single
photo, keep a partial answer and seek only views that distinguish remaining alternatives.

For **physical reconstruction**, first photograph a stable arrangement from known
or calibratable views. Include scale, camera/lens information when available,
and the full background shadow. Separate shots that change lighting from shots
that change shape. Additional views can break depth/camera ambiguities but may
introduce deformation; state which situation applies. Controlled diffuse and
directional-light shots can separate pigment questions from highlight geometry.
These acquisition suggestions are practical proposals, not tested results from
this project's single-photo inversion.

### Pattern recovery track

1. **Create a small trusted graph.** Mark several clear patches across the object,
   assign body IDs and color/unknown states, and annotate actual neighbor directions.
   Preserve original pixels and a few explicit “same body / different body” examples.
   Keep reflections and support centroids as features, not physical centers. Test
   automatic proposals against these annotations before expanding extraction.
2. **Derive the construction map.** Verify the number of beads per turn and the
   crochet convention from reliable local triangles or maker knowledge. The 6/7
   case admits primitive steps (1,0), (0,1), (1,−1) and candidate maps 7a+6b or
   6a+7b. Do not assume every object uses this turn count or that projected nearest
   neighbors are consecutive string beads. Enumerate direction/sign alternatives
   and separate display origin from physical string start.
3. **Carry row alternatives through overlap.** Fit local row hypotheses jointly
   to several bodies and both directions. Require reciprocal/triangle consistency,
   unique-body occupancy and overlap agreement. Keep coherent alternatives with
   their source pixels; use later context and bounded rollback to resolve them.
   Unknown edge cues should not become mandatory blockers. Check bridges and
   return paths explicitly before calling a graph closed.
4. **Build partial string observations.** Attach each reliable color to a proposed
   string address with provenance; preserve unknown colors, alias groups and
   alternative sites. Verify integer equations and circuit translations. Closure
   of a selected graph is a conditional fact, not a physical bead census. Without
   a justified total, do not restrict periods to divisors of a guessed count.
5. **Compare repeat hypotheses.** For each coherent indexing/orientation, group
   colors by candidate residue and list contradictory witnesses. Reject periods
   only with usable evidence or a stated construction prior. A partial word can
   refute some periods without observing every address. Do not impose the old
   “not divisible by 13” preference on another object. Use a stated practical
   search range and label uniqueness within it; exact complete repeats are an
   assumption that may fail for construction defects or end regions.
6. **Use robust constraints for error diagnosis.** A weighted mismatch formulation
   or constraint solver can rank jointly consistent row/period hypotheses, with
   explicit penalties for bad measurements, duplicates and unassigned sites.
   Preserve raw labels and show which constraints each hypothesis violates.
   Repetition supplies redundancy, resembling error correction, but repeated
   colors are not a designed error-correcting code: correlated misindexing can
   agree perfectly. Correct a source only after independent body/pigment review;
   otherwise mark the candidate's completion as inferred. This robust joint solver
   is promising future work, not a component proved superior by R348.
7. **Validate away from the fitted patch.** Withhold separated geographic regions
   and whole occurrences, including aliases and immediate correlated context.
   Compare against color frequency, shorter periods and competing orientations.
   Inspect literal source crops for contradictions; obtain an additional view or
   chart when the photograph cannot answer. Direct human inspection of a few
   decisive bodies is often a better experiment than another whole-photo classifier.
8. **Deliver both evidence and chart.** Provide the ordered word with observed,
   maker-confirmed, tentative and unknown entries distinguished. For the verified
   6.5-bead convention, use x=a−b, y=a+b, 2k=x+13y. Alternate six/seven central
   symbols, label row and string indices, show start/end cuts and the staggered
   seam. Seven actual horizontal same-k extensions on each side aid diagonal
   reading; never count them as extra beads or observations. For a different
   circumference, derive the corresponding lattice instead of reusing 6/7 blindly.
   [Reusable layout specification](GRAPH_PAPER_6_5_BEADS.md),
   [sequence-only layout code](r344/graph_paper.py).

Stop image recognition when remaining hypotheses differ only at unreadable
locations, no new independent body/order evidence is being added, and the best
next discriminator is a view, chart or physical observation. A maker can accept a
well-supported provisional chart while its uncertainty remains explicit. Claim an
exact intended pattern only with evidence appropriate to that claim: for example,
an authentic matching chart, or independently supported colors and ordering that
exclude coherent alternatives. Complete fit to selected labels alone is not that
standard. A physical assembly claim also has to allow deviations from the chart.

### Separate full-reconstruction track

Begin from the accepted pattern evidence and retained correspondence alternatives.
The pattern track need not wait for these steps.

1. Audit the bead macro, units, shape/radius conventions and frame/helicity against
   a few physical dimensional measurements. Distinguish legacy source parity from
   measured bead geometry. Test straight, curved and closed packing with actual
   nonintersection checks before optical fitting.
2. Use silhouettes and reliable body boundaries for coarse camera/centerline/scale
   fitting. Fix a scale gauge and account for perspective if views justify it.
   Add bead poses/spacing gradually; preserve successful local fits and forbid
   hidden normalization changes when expanding the domain. Test known-answer
   recovery for each newly active parameter block.
3. Fit a shared illumination model to the **whole-necklace cast shadow** on the
   background, including both sides and different orientations. Estimate paper
   reference away from the entire shadow, guard material/silhouette pixels, and
   withhold geographic stations. Geometry height and light extent can compensate,
   so compare alternative plausible geometries instead of calling one lamp unique.
4. Then refine shared materials, roughness and specular features with verified
   ownership and accurate forward checks. Keep pigment sampling separate from
   highlight fitting. Reject improved highlights that worsen boundaries, material
   coverage or physical validity; do not compensate a bad pose with per-bead lights.
5. Evaluate aligned whole images and enlarged regions, silhouette/material coverage,
   fixed and alternative owner comparisons, global shadow profiles, and independent
   views if available. Report a plausible rendering separately from recovered
   physical parameters. Rendering realism cannot authenticate hidden bead order.

R345's actual bead macro and separation verification and R346's global paper-shadow
profiles are useful foundations, not drop-in physical truth for another object.
[Scene generator](r345/render.py), [geometry verification](r345/output/independent-verification.json),
[whole-shadow method](r346/shadows.py).

### Reuse and simplify deliberately

| Existing component | Reuse | Change before a new project |
|---|---|---|
| HSV picker and native pixel inspectors | Interactive exploration, hue wrapping, exact sample provenance | Recalibrate to the new photo; never equate masks with bodies |
| Old bead_map ordering/skeleton approach | At most rough localization or visualization | Replace nearest-neighbor traversal with construction-aware graph/string order |
| Stable IDs, source aliases, role-aware ledgers, native crops | Strong foundation for annotation and review | Use one compact schema; keep authority and evidence basis explicit |
| R323 joint rows, R326 compatibility, R328 connected patches | Reusable algorithmic ideas and saved failure fixtures | Extract small tested modules; avoid importing all historical heuristics and photo-specific thresholds |
| R330/R337 partial-word and holdout analysis | Residue grouping, witnesses, null/alternative comparisons | Accept arbitrary turn/period hypotheses and correlated observation groups; state count premises |
| R344 pattern_layout and graph-paper math | A comparatively clean, sequence-only presentation component | Parameterize the object's circumference; retain unknowns and distinguish display copies |
| R339–R343 material tools | Simple baselines and examples of owned-glass sampling | Replace fixed offset/73.5 threshold with new calibration; manual cores are not automatic accuracy |
| Late physical optimizer stack | Failure fixtures, accurate evaluator and parameter audits | Simplify around active, identifiable variables and known-answer recovery; do not restart the entire stack unchanged |
| Immutable artifacts, independent replay, literal/native review | Preserve these practices | Keep scientific acceptance separate from software correctness and browser delivery |

A modest annotation-plus-graph approach could plausibly have reached a useful
pattern much earlier: the manual chart was small, R323 recovered its interior
topology, R328 supplied a working global circuit, and R332 reused older candidates.
That is evidence of practicality, not proof that early annotations would have
settled every winding or shaded color. The strongest counterfactual is avoiding
full optical inversion as a prerequisite for pattern recovery. A complete automated
method would still need representative real examples, robust abstention and
validation on new objects. Human reference data can accelerate that development
without becoming an unreported permanent dependency.

## 8 Early-warning framework: evidence, diagnostic, decision

Use these as diagnostic triggers, not automatic verdicts that a direction is wrong.
Choose the smallest test that distinguishes the suspected mechanisms. The decision
rules below are claim-based; tolerances and useful effects must come from measurement
uncertainty and the task's needs, rather than arbitrary universal percentages.

### 1 A better primary score accompanies worse independently visible correctness

**Observe:** component/region ledgers or literal crops show missing material,
wrong bodies or collisions while the optimized score falls. **Possible causes:**
wrong target, reassignment hiding error, biased denominator, or a genuine Pareto
tradeoff. **Small test:** evaluate the same models against fixed independent
silhouette/material/identity sentinels and an owner-fixed control; expose each
component rather than immediately retuning weights. **Decision:** stop adoption;
revise the objective or claim if the omitted constraint is essential. Continue
only with an explicit acceptable tradeoff. **Example:** R301 improved reflections
while worsening material omission; R263 matched count while losing dark supports.

### 2 Convenient synthetic tests pass but motivating photo failures persist

**Observe:** the rejected old method passes the same controls as the new one.
**Possible causes:** missing shadows/occlusions/merged surfaces in fixtures, an
incorrect test target, or genuine domain differences. **Small test:** reproduce
one inspected real failure and build the smallest fixture exhibiting that ownership
error; compare old and new with identical measurements. **Decision:** downgrade
the existing synthetic pass to an implementation check. Reconsider the feature
representation if representative failures persist. **Example:** R231's synthetic
ownership controls did not separate the rejected seeds from repairs.

### 3 Known-answer inverse recovery fails

**Observe:** accurate truth replay fits better than returned solutions, including
known-owner cases. **Possible causes:** inaccurate screening, inactive variables,
bad bounds/scales, missed basins, numerical discontinuity; exact parameter
nonuniqueness is another possibility. **Small test:** compare accurate and cheap
truth evaluations, start near truth, fix correspondence, and inspect predictions
up to gauge. **Decision:** stop expanding the corresponding large real-data search
until the failure is understood or the scientific claim is explicitly reduced.
Do not infer model impossibility. **Example:** R301. A successful forward render
alone never validates inversion.

### 4 Search logs contain many trials but little effective exploration

**Observe:** repeated starts, narrow actual ranges, all-column gates rejecting
whole derivative blocks, inactive fields or near-parallel response columns.
**Possible causes:** implementation inactivity, poor parameterization, coupling
or finite-budget search failure. **Small test:** output-difference probes through
the actual code, joint response maps and a dispersed-start comparison including
earlier useful fits. **Decision:** revise search/coordinates before adding more
parameters or claiming a local optimum. Boundary hits require checking physical
versus numerical limits; widening every bound is not a remedy. **Examples:**
R311's missed basins and R319's inactive keys/coupled responses.

### 5 Small perturbations change the physical or combinatorial answer

**Observe:** plausible sampling apertures, initialization, half-grid tracing or
small parameter changes switch owners, colors, rows or periods. **Possible causes:**
sampling discontinuity, threshold boundary, multiple minima or weak identification.
**Small test:** rerun only the disputed local comparison at accurate resolution
and with fixed identity, retaining all alternatives. **Decision:** repair the
numerics if predictions converge; otherwise preserve uncertainty and seek a
discriminating observation. **Examples:** R319's bilateral/half-pixel checks and
R339–R343's material-window ownership checks. Stability is useful, but a stable
wrong sample is still wrong.

### 6 A local success disappears when the problem grows

**Observe:** the old patch changes before any new fitting, or successive extensions
lose previously demonstrated constraints. **Possible causes:** global normalization,
phase transport, coordinate gauge changes, extrapolation or legitimate model
conflict. **Small test:** replay old predictions immediately after extension and
toggle the new normalization/phase components individually. **Decision:** repair
transfer or expose the contradiction before expanding again. **Example:** R297
isolated station normalization and phase effects; archival preservation alone had
not protected the local solution.

### 7 Locally plausible relationships have no global witness

**Observe:** inconsistent cycles, duplicated occupancy, divergent return translations,
or edges individually supported by mutually exclusive patch choices. **Possible
causes:** wrong row, artificial chart boundary, incompatible pooling or false body
identity. **Small test:** a compact contradictory cycle or whole-hypothesis
compatibility check, with the actual photographic overlap displayed. **Decision:**
revise the discrete representation/selection; do not smooth geometry to absorb
integer errors. **Examples:** R322's row switches, R324's chart fragmentation,
R326's incompatible union. Algebraic consistency remains necessary, not sufficient.

### 8 More detections provide little new trustworthy coverage

**Observe:** counts rise while new IDs reuse bodies, old cache features reappear,
or geographic/residue coverage and reference recall do not improve. **Possible
causes:** duplicates, reflection multiplicity, wrong count target or failure to use
existing observations. **Small test:** deduplicate source/body groups and compare
coverage on the same trusted reference; tabulate genuinely new measurements
separately from new associations. **Decision:** pivot from detection to association
or evidence integration when those are the bottleneck. **Examples:** R263's count
trap and R332's 122 cached versus four fresh observations.

### 9 A prediction starts validating its own evidence

**Observe:** vacancy-seeded pixels become alleged body proof; expected colors
enter labels/calibration; a reconstruction-assisted answer is called independent.
**Possible causes:** circular evidence generation or authority/provenance loss.
**Small test:** hide model/pattern overlays, inspect exact source pixels and owned
body context, and separate raw answer fields from explanatory notes. **Decision:**
quarantine the affected inference role and run a bounded exclusion sensitivity
test; retain the original source. **Examples:** R336's real pixels on nonexistent
beads, R343's approval-scope correction and R347 Q1. A genuine pixel is not a
genuine bead identity.

### 10 Equally successful fits imply different answers

**Observe:** several hands, row histories, counts or physical parameters satisfy
the same evidence. **Possible causes:** actual ambiguity, gauge symmetry or
insufficiently discriminating metric. **Small test:** show the competing predictions
at a location/view not used to fit them. **Decision:** report the alternatives;
seek that observation or narrow the claim. More optimization is appropriate only
if a documented search defect prevents fair comparison. **Examples:** R160's
refitted families and R328/R329's coherent alternative row histories. R347's
finite A/208 uniqueness narrows one explicitly fixed family, not all physical graphs.

### 11 Complexity grows without independent benefit

**Observe:** more stages, parameters or exceptions improve development explanations
but not a fixed comparison of correct bodies/order/colors or held-out geometry.
**Possible causes:** overfitting, an unnecessary prerequisite or a broken basic
measurement. **Small test:** matched simple baseline plus ablation on the same
cases, including its abstentions and new failures. **Decision:** retain complexity
only for a demonstrated task-relevant benefit; simplify or pivot to the missing
evidence. **Example:** R339's simpler material sampling fixed some cases the
complex extent procedure abstained on, but did not dominate every control. R343
then showed ownership, not another color formula, was decisive for Q101.

### 12 Reports proliferate without a changed scientific decision

**Observe:** each round improves software or explains the prior failure, while
the same unresolved claim and counterexample survive; figures still do not show
the source evidence needed to decide. **Possible causes:** fragmented objective,
poor diagnostics or unavoidable lack of information. **Small test:** write the
current claim, strongest counterexample, what changed, and the next observable
that would discriminate mechanisms. If no such observable can be named, more of
the same experiment is unjustified. **Decision:** reconsider the representation,
obtain external evidence, or stop at a qualified result. **Examples:** R332's
display audit, R329's corrected native comparison, and R347's unnecessary return
to an unreadable edge cue. Failure reports remain valuable when they actually
constrain the next decision.

### Continue, stop, reconsider or pivot

**Continue** when a stated uncertainty has been reduced on credible evidence,
earlier essential successes survive, and the next experiment distinguishes named
alternatives. **Stop adoption** on essential physical violations, circular evidence
or unexplained regression even if a scalar score improves. **Stop scaling** when
known-answer inversion or basic identity controls fail. **Reconsider** when repeated
iterations yield only development-score gains with the same independent failure;
require a new causal hypothesis before repeating them. **Pivot representation**
when a simpler structural formulation predicts what a detailed one cannot;
**pivot evidence acquisition** when several coherent solutions remain equivalent
on available data. **Abandon a direction as a prerequisite** when its output is
not necessary for the task and has no demonstrated discriminating benefit.

These are broadly applicable gates, not a fixed number of permitted rounds.
Project-specific judgments include which constraints are essential, plausible
measurement uncertainty, how much annotation is acceptable, and when a provisional
deliverable is useful. State those choices before evaluating candidates. A clearly
bounded numerical repair may be worthwhile without improving the final answer
immediately; label it enabling work, specify the failure it removes, and verify
that removal before returning to the larger inference.

An AI coding agent should surface a trigger when it first becomes visible. Its
progress report should say what claim advanced, what regressed, what the failure
does and does not establish, and the smallest discriminating next test. It should
not silently turn an optimization failure into “the data are insufficient,” or
count passing unit/browser checks as scientific acceptance. Within authorized
scope it can run the small diagnostic; a pivot requiring new scientific work
should be proposed concretely rather than begun automatically.

## 9 Ranked changes to working methods

| Priority and confidence | Past problem and earliest practical use | How it could change the trajectory | Cost and effectiveness check |
|---|---|---|---|
| **1. Separate deliverables; establish a trusted graph and partial word early. Strong support for the sequencing lesson; speed counterfactual remains qualitative.** | Optical prerequisites delayed useful structure; practical after the manual 1/6/7 chart, well before R322 | Reach a testable pattern hypothesis while preserving later automation/rendering goals | Modest annotation and graph tooling; judge independent row/color predictions and unresolved alternatives |
| **2. Gate large inversion on known-answer recovery and representative real failures. Strong support.** | R231's non-discriminating fixtures; R301's failed synthetic recovery | Prevent expensive real-photo fitting from being mistaken for validated inversion | Small fixtures and accurate truth checks; old failures must be exposed and repairs must survive them |
| **3. Treat identity, pigment and prediction as different evidence. Strong support.** | Multiple features per body, R336 phantoms, R343 authority, R347 Q1 | Reduce self-confirmation and unnecessary edge disputes; permit principled abstention | Explicit schema/roles and native review; track false bodies, aliases and independent evidence basis |
| **4. Protect independent task constraints and earlier local successes. Strong support.** | R263 count loss, R297 transfer regression, R301 highlight/material tradeoff | Reject metric improvements that worsen the actual reconstruction before adopting them | Small fixed sentinel suite and component/geographic reports; old physical predictions survive or tradeoffs are explicit |
| **5. Audit active search, units, coupling and basins. Strong support.** | R311 missed starts/basins and R319 inactive/near-redundant variables | Distinguish search limitations from model failure without expanding blindly | Preflight probes and actual coverage ledger; effects and joint exploration are demonstrated |
| **6. Keep a current claim register alongside immutable history. Strong support for the problem; organizational remedy unmeasured.** | R332 unused cached observations, repeated unclear diagnostics and stale authority | Make prior constraints operational and direct new work at a named uncertainty | Short maintained table, links and cohort deltas; newcomers can locate the current claim/counterexample and avoid repeated tests |
| **7. Add human-guided constraint solving and targeted new views. Promising, partly demonstrated.** | R323/R328 joint topology helped; R347 leaves chart verification available | Resolve informative ambiguities without solving every shaded pixel | A small solver/annotation interface and acquisition effort; compare coherent alternatives and new-object validation, not in-sample completion |
| **8. Fit global shadow separately when rendering is required. Strong support for R346; earlier timing is a qualified counterfactual.** | Local specular fits did not recover the broad paper shadow | Constrain shared illumination from a different observable | Global silhouettes and uncontaminated paper reference; held-region shadow improvement with geometry sealed |

Preserve the project's best practices: transparent negative reports, stable source
provenance, exact native crops, immutable failed epochs, scientific input seals,
independent replay and the ability to revisit earlier hypotheses. Their value is
clear in this retrospective and the R348 deletion test. Improve their connection
to decisions; do not replace them with undocumented manual edits or a single
opaque end-to-end score. No evidence here supports a numerical estimate of time
saved or the claim that one preferred optimizer would have solved the project.

## 10 Reusable checklist for AGENTS.md or an initial research prompt

```text
Before a campaign:
- Define the deliverable, claim, premises and an observable acceptance check.
- Build a small trusted real-data reference; distinguish feature, identity,
  relationship, measurement and prediction. Record unknowns and exposure.
- Compare a simple baseline and coherent alternatives before adding complexity.
- For inversion, verify truth replay and known-answer recovery up to gauge.
  A failed known-answer case blocks scaling until its mechanism is understood.
- Audit active parameters, units, bounds, coupling and actual start coverage.

For each experiment:
- State competing explanations, the intervention and what each outcome changes.
- Preserve source evidence and historical artifacts; save derived alternatives
  separately. Never let a proposed answer validate its own measurements.
- Compare the same target cohort and independent component/geographic checks;
  report exclusions, abstentions, aliases and prior-data exposure.
- Recheck earlier successful predictions after extension or reparameterization.
- If score improves but essential correctness worsens, stop adoption and diagnose.

At the decision point:
- Report what advanced, what failed, and whether this is search failure,
  model inadequacy, measurement ambiguity, or still undiagnosed.
- If the same independent counterexample survives, do not repeat the same
  campaign without a new causal test. Prefer the smallest discriminating test.
- If several solutions remain equivalent, report alternatives and identify
  new evidence that separates them; do not manufacture uniqueness.
- Update a short claim/counterexample/next-evidence register, linked to artifacts.
- Propose substantial pivots explicitly; respect task scope and stop instructions.
```

For this necklace, these rules lead to a bounded conclusion: R347/R348 strongly
support the same complete candidate word under stated indexing premises, and Q1
is unnecessary to the retained graph's constraints. Independent chart/object
validation remains a distinct evidential step. The rules do not authorize a new
reconstruction campaign to remove that qualification.
