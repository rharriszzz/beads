# Registration and repeat recovery: review and test plan — R026–R028

**R074 current direction:** use [local projected geometry](BLACK_REGION_METHODS.md)
as the primary black-region method and HSV as supporting evidence. Calibrate
centers/outlines on clearer neighbors and validate withheld predictions before
indexing. The R073 diagnostic has 3.16/6.32-pixel target-marker errors, so its
provisional ellipse placements cannot yet justify missing beads. The older
synthetic plans below remain history; do not consult POV patterns for this task.

**R043 update:** [joint triangle/trace constraints](JOINT_INFERENCE.md) reject
known false bridges but produce sparse, sometimes wrongly indexed patches.
Next diagnose centroid displacement versus projected-direction/support assumptions
using instrumented synthetic centers/edges; keep that diagnostic distinct from
image recovery. Stop after its causal report before another algorithm or photo fit.

**R039 update:** the centroid-versus-outline baseline is completed in
[INFERENCE.md](INFERENCE.md). Shape improves pair precision but all 192 convention
graphs retain contradictions; automatic indexing remains unvalidated. Next test
joint local triangle/lattice constraints for edge selection and signed labels,
retaining ambiguity/abstention and the fixed baseline controls. Stop at a synthetic
edge/component-index report and checks, before segmentation, sequence integration
or photo fitting. The earlier next-step descriptions below are retained history.

Select **a neighbor graph with integer index differences**, followed by
**strong-period testing of a partial word**. R028 supplies the key construction
rule: each visible bead has neighbors along the three directions with index
differences **±1, ±6 and ±7**. Use established graph traversal/difference-constraint
methods to propagate those labels; use partial-word periodicity for color repeats.
CPD is no longer the primary indexing proposal. No recovery code or new experiment
was run in this method-selection step.

R030 implements the illustrated synthetic neighbor/index check in §A, extended
to both legacy helicities; results are in [NEIGHBORS.md](NEIGHBORS.md). A bead may
have a known index and an unknown color. The graph rule comes from the maker;
automatic identification of corresponding image neighbors still needs validation.
R036 completes §B's sequence-only test with known synthetic indices; see
[SEQUENCES.md](SEQUENCES.md). The next bounded task is synthetic edge inference
from supplied visible-mask centroids, withholding truth indices/colors from edge
construction; stop after its illustrated report/checks before segmentation/refit.

R038 adds a shape cue to that next test: the maker reports almost no tilting or
sliding, rectangular-looking top beads, close spacing along direction 1 described
as "the shorter length close by", and brick-like 6/7 neighbors with short edges
together and successive layers halfway offset. Compare the centroid-only baseline
with outline/orientation cues measured from the supplied visible masks. Do not
pass true body axes, source indices or colors to edge construction. These are
qualitative construction cues, not yet a calibrated image-direction rule.
The shared bead-shape.inc defines a rounded hollow cylinder, local hole axis y;
beads.pov case 1 uses roundedness 0.8, height/diameter 0.7, relative size 1.0,
and hole/outer radius 0.14. Bead bodies rotate by chain_angle about z only;
row_angle controls their placement. Oracle mask outlines remain oracle segmentation.

R025 supplies the intended palette **red, yellow, black** and the working
assumption of error-free construction: the maker checks every pattern sequence
against the preceding one. Insufficiently visible beads are **color unknown**.
They supply no color evidence, but their sequence positions must survive.
Image-reading or correspondence errors remain possible.

## Primary sources and choice

Sources consulted on 2026-09-23; section references refer to the linked versions.

| Source | What it supplies | Decision for beads |
| --- | --- | --- |
| Sedgewick and Wayne, *Algorithms*, §4.1 ([authors' companion](https://algs4.cs.princeton.edu/41graph/)); MIT 6.006, spring 2011, lecture 17 ([difference constraints](https://courses.csail.mit.edu/6.006/spring11/lectures/lec17.pdf)) | Graph traversal/connectivity and graph representations of difference constraints. | Select traversal with signed integer edge increments and consistency checks for the maker's neighbor rule. The ±1/±6/±7 labels come from R028, not these sources. |
| Myronenko and Song, *Point Set Registration: Coherent Point Drift*, 2009 author preprint; published TPAMI 2010, §§3–4 ([paper](https://arxiv.org/pdf/0905.2635)) | Gaussian-mixture registration with soft correspondences, an outlier component and a similarity transform. | Considered but not selected: R028 supplies a direct construction-based neighbor graph. It does not establish sequence order or resolve geometric ambiguity by itself. |
| Blanchet-Sadri, Mandel and Sisodia, *Periods in Partial Words: An Algorithm*, JDA 2012, §1 ([author manuscript](https://libres.uncg.edu/ir/uncg/f/F_Blanchet-Sadri_Periods_2012.pdf)) | Strong periodicity requires agreement among all defined positions congruent modulo a candidate period; holes are unknown symbols. | Use the definition directly for a transparent finite search. The paper's main algorithm computes a Fine–Wilf length bound; we are **not** adopting or mislabeling it as a photo-recovery algorithm. |
| Sakoe and Chiba, *Dynamic Programming Algorithm Optimization for Spoken Word Recognition*, 1978, §§II–III ([paper](https://jeffe.cs.illinois.edu/teaching/compgeom/refs/Sakoe-Chiba-DTW.pdf)) | Dynamic time warping aligns already ordered feature sequences under path constraints. | Defer: image-plane nearest neighbors do not supply crochet order, and time warping is unnecessary for the error-free, fixed-index sequence gate. |
| Galbrun et al., *Mining Periodic Patterns with a MDL Criterion*, 2018, §§2–3 ([author preprint](https://arxiv.org/pdf/1807.01706)) | Periodic event-log patterns ranked through description length, including occurrence timing corrections. | Defer: timestamped events are a different input from unordered beads with unknown indices. A complexity preference alone would not certify a hidden color or the maker's repeat length. |
| SciPy, `linear_sum_assignment` ([official reference](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html)) | Rectangular minimum-cost assignment using a modified Jonker–Volgenant algorithm. | Available in the local dependency set for extracting one-to-one matches after registration, with explicit unmatched options. |

Berstel and Boasson's 1999 *Partial Words and a Theorem of Fine and Wilf* was
located through its [author-hosted indexed PDF](https://www-igm.univ-mlv.fr/~berstel/Articles/1999PartialWords.pdf),
but direct PDF and publisher opens failed. The accessible 2012 author manuscript
above supplies the definitions actually checked. No theorem from an inaccessible
full text is needed here. These papers do not establish recovery of this necklace.

## Observation and inference contract

Keep three distinct objects: an observed bead record, its candidate chain index,
and a proposed repeat slot. An observed record contains a stable observation ID,
image location/feature type, visibility/readability evidence, and color in
`{red, yellow, black, unknown}`. Its index may be unknown or have alternatives.
The fourth label describes absent knowledge, not a bead material. A dark hole,
shadow or background pixel must not count as a black bead merely because it is dark.

Unknown colors are excluded before period scoring, using an independently fixed
readability rule; a solver may not erase conflicting observations to improve its
fit. A readable bead with unresolved index cannot be inserted into an arbitrary
sequence position. Preserve candidate mappings separately. Missing entire beads
and missing color readings are distinct, and neither shortens the chain.

If another occurrence later supports a repeat slot, store that inferred slot
color separately; the originally unreadable observation remains unknown. If no
occurrence supports a slot, leave its color unknown even when a period is favored.
Exactly three colors globally does not establish any particular unseen slot.

The following application choices are our test design, not claimed results from
the cited papers.

## Neighbor graph: the selected indexing component

Represent each identifiable visible bead as a vertex. An oriented edge u→v
with label d means `index(v) - index(u) = d`, where d is one of
`{-7, -6, -1, +1, +6, +7}`. Its reverse must have label -d. Seek up to one immediate
neighbor in each signed direction. These are construction neighbors on the rope,
not simply the six closest centers in the photograph: perspective, bends and
crossings change apparent distances and can place separate rope sections nearby.
If an immediate neighbor is hidden, keep that connection missing; do not label
the next visible bead with the missing neighbor's one-step offset.

Seed any connected region at index 0. Traverse its labeled edges, adding their
integer offsets. On reaching an already labeled vertex, check the existing label
against the new sum. Every accepted edge, including non-tree edges, must agree.
The triangle +1,+6,-7 sums to zero; it provides a useful local check. This is a
standard graph-potential calculation using the maker's offsets, not a new
image-recovery algorithm. It is equivalent to solving edge difference equalities;
representing each equality as two inequalities allows the general difference-
constraint machinery, but exact labeled edges need only traversal and checking.

The result fixes indices relative to a chosen seed. Disconnected components keep
separate unknown offsets; repeated colors may later constrain those offsets but
must not be silently used as known links. Reversing all signs retains a competing
orientation unless geometry/construction distinguishes it. Missing global origin
only rotates the repeat; it does not prevent relative indexing. Check uniqueness:
different beads may not silently receive the same index in a connected patch.
Consistent cycles are necessary, not sufficient to prove an image edge is correct;
a wrong bridge or consistently misoriented region needs independent evidence.

For a full closed necklace, a traversal winding once around the chain returns
with an increment ±N, not zero in an unwrapped integer coordinate. Use local
patches or a documented seam cut for the first experiment. With known synthetic
N, compare indices modulo N and record winding cycles separately from inconsistent
local cycles. For photo 2, N=2,698 remains provisional; do not force closure modulo
that number or turn a true winding cycle into an alleged neighbor error.

Finding and signing the image edges is the remaining perception task. Use the
local rope direction and three neighbor directions, maintain reciprocal links,
and inspect triangles and longer loops. Candidate directions must follow the
rope around bends, not fixed screen axes; the distinction between the 6 and 7
families and their signs must be geometrically supported or retained as alternative
labelings. The user's rule does not itself supply a calibrated pixel-distance
cutoff, an automatic bead detector or an occlusion-bridging rule. Color is not
required to identify an edge, so unreadable colors must not remove otherwise
usable vertices. Separate touching rope sections at image crossings.

R030 clarifies the directions: ±1 runs around the small torus radius and ±6/±7
along the diagonals; helicity affects their orientation. The maker states that
unseen beads occur at the edges of the visible patch, not between visible
neighbors. Use that construction guidance rather than assuming routine internal
gaps. Synthetic threshold removal and deliberately missing-edge controls remain
separate stress tests. Inspect the actual legacy angle equations when assigning
image directions; they rotate around the rope and change with hand.

The next synthetic check will first test this graph logic with evaluator-generated
edges, then inspect the projected neighbor directions. It does not pretend that
true-index-generated edges were automatically read from a beauty image. CPD and
rectangular assignment remain possible tools if later image alignment requires
them, but no CPD implementation or benchmark is scheduled.

## Sequence component

For a fixed candidate index mapping, let D be positions with accepted observed
colors. For each trial length L, accumulate the **set of observed colors** in
each residue class `i mod L`. This is a direct implementation of the strong-period
definition cited above:

- Empty set: unsupported repeat slot, color unknown.
- One distinct color: compatible slot, with supporting observation IDs retained.
- Two or three colors: contradiction for that candidate mapping and period.

Reject contradictions in the exact synthetic gate; do not repair them by majority
vote. For real observations, flag them for correspondence/color review rather than
assert a maker's error. Extending this to calibrated color likelihoods is deferred.
No new probabilistic color model is required by the first experiment.

Compare all occurrences in a residue class, not just pairs separated by one L.
For example, `R ? Y` passes adjacent comparisons at L=1 if each comparison through
`?` is skipped, yet R and Y contradict a single repeating slot. This constructed
example is a check on the selected rule, not a photo result.

Report all compatible candidates, their support and unsupported slots. The
maker defines pattern length as the shortest repeating color block (R033); reduce
a fully specified repeating pattern to that block. With missing observations,
the smallest compatible length need not establish the true shortest block:
different completions can remain possible. Preserve that uncertainty.
The maker accepts any starting bead, stringing direction and helicity. Choose a
consistent reporting convention, treating cyclic shifts and reversal as equivalent
presentations without relabeling colors. This freedom does not establish a photo's
physical hand or validate an index mapping; retain competing image fits as needed.
At the synthetic stage N is known, so whole-repeat compatibility can be checked
exactly. Never apply that exact-count divisor filter to provisional photo N.

The current `reconstruct.py` already groups votes by original index modulo period,
keeps unknowns and uses arc holdouts. Reuse that data discipline, not its unvalidated
photo samples, majority-vote score or historical 200–400 candidate range. No change
to that preview/diagnostic code is made by this method-selection step.

## Concrete synthetic validation

All numbers below are **planned test settings**, not observations or measured
performance. Use Python 3.12 and ignored `photo2/output/` artifacts. Keep the two
views separate except for an explicitly labeled two-view diagnostic.

### A. Immediate next bounded experiment: neighbor/index audit

Use the four existing R023 views, preserving their original geometry and separate
visibility records. At each visible-area threshold T=1, 12 and 100, form vertices
from beads meeting that threshold. These vertex thresholds measure connectivity
sensitivity, not color readability. Keep bead colors out of graph propagation.

For this first, explicitly oracle-topology check, the evaluator creates an edge
only if both source indices are visible and differ by ±1, ±6 or ±7 (modulo known
N for full-ring checks). Give the traversal shuffled anonymous vertex IDs and
signed edge labels, never absolute source indices. Retain the source indices only
for evaluation. Use source-index order before PCG64 shuffles, seeds 17 and 43.

Check local lifted patches and the complete graph modulo known synthetic N.
Use each quarter-ring as an induced patch, explicitly excluding seam-crossing
edges if lifting indices to integers. Report component counts/sizes, direction
coverage, cycle residuals, duplicate-index conflicts and relative index error
against truth up to each component's seed offset. Do not align disconnected
components using evaluator truth and then claim global recovery. If topology
leaves components disconnected, describe precisely which links are missing.

Include independent small graph controls: the triangle 0→1 (+1), 1→7 (+6),
0→7 (+7); an inconsistent +6 label replacing that +7 edge; a missing edge with
an alternate path; a disconnected component; duplicate inconsistent constraints;
and a correct seam/winding case with a known N. Exact constraints must recover
relative indices or report a contradiction, never silently average/round indices.
A wrong isolated bridge can be cycle-consistent: include that negative control
and state that topology alone cannot certify its label.

Produce an enlarged synthetic panel with visible beads and the three edge families,
using distinct styles and ± labels. Show obscured neighbors as missing edges,
not connections to the next visible bead. Compare projected source-center
locations with visible-mask centroids when illustrating direction: they are
not interchangeable under occlusion (R015). Include a bend and the weak-slot
region from the 13-repeat phase-half view. This provides a concrete audit of the
maker's rule in the existing forward model; it does not test automatic edge
extraction or assign indices in photo 2.

Required checks: exact relative indices on each consistent component, zero
unexplained local cycle residuals, explicit winding handling, caught contradictions,
retained disconnected offsets, and no dependency on observed color. Record source
and artifact hashes, graph inputs, seeds and commands; run focused graph tests
and the existing suite if shared code changes. Stop after this illustrated audit
and its checks, before segmentation, photo indexing or repeat recovery.

### B. Later sequence-only experiment: known-index partial-word recovery

**Completed in R036.** `sequence_audit.py` implements this plan, plus R035's
introductory example below. See SEQUENCES.md for 72 cases, 288 holdouts, candidate
tables, completion ambiguities, negative controls and reproduction commands.
The following settings are the retained design, not a pending experiment.

R035 adds a maker-proposed introductory control: concatenate
`123333, 112333, 111233, 111123, 111112` into one 30-bead repeat, assigning
1=red, 2=yellow, 3=black. Direct enumeration confirms its shortest complete block
is 30. Use deterministic symbolic missing-color examples first; this pattern
has no measured visibility mask yet. Retain the 40/13 fixtures below for those
visibility tests. The maker's photo-2 repeat is certainly <400, and repeats below
five are considered boring (five is acceptable). That preference is not a ban
on short-period synthetic controls; the photo upper bound does not change the
known-N synthetic search domains below. Photo 2's deliberately continuous
black/yellow/red spirals were designed on custom graph paper; no exact continuity
constraint was supplied. Length 42 is a favored design because it aligns with
both diagonal steps, 6 and 7. Do not infer photo 2's period from that example.

Use `practice-pattern.json` (40 slots, 800 beads) and
`visibility-pattern-13.json` (13 slots, 780 beads), with each of the two R023 views.
Both contain three symbols, not 40 or 13 distinct colors. Their old beauty palette
is red/green/blue. For this symbolic test only, map source symbols 0/1/2 to
red/yellow/black. Do not claim the old rendered RGB values are the photo palette,
change the old fixtures, or treat symbolic relabeling as appearance validation.

1. Verify R023 source/artifact hashes. Build an indexed observation array of full
   length N, setting color unknown wherever visible area is below T. Run T=12 and
   T=100 pixels separately at the original 2400×1800 raster. These are controlled
   erasure masks, **not** validated photo readability thresholds. Color labels
   come from the authored synthetic pattern here: this is an explicit known-index,
   known-readable-color test, not segmentation or unknown-index recovery.
2. Give the sequence solver only N, original positions and masked color labels.
   Withhold the source pattern, true period and repeat-slot IDs. Enumerate every
   L from 1 through floor(N/2), recording strong-period compatibility and the
   independent N mod L closure flag. This domain requires at least two repeats
   for the benchmark; it is not a maker-supplied photo period bound. Report the
   complete candidate list and the closure-compatible subset, including aliases.
3. Split original positions into four equal contiguous quarters. For each fold,
   learn slots and candidate periods on three quarters only, freeze them, then
   predict readable held-out positions. Report correct, wrong and abstained
   predictions and the number of supported training slots. Never use held-out
   colors to select a candidate and call that same fold an independent success.
   These folds diagnose each candidate; they are not a final photo test set.
4. Add deterministic erasures to readable observations at rates 0.1 and 0.3,
   using NumPy PCG64 seeds 17 and 43 with source-index order fixed. Retain exact
   erased indices. Include an all-unknown input and a missing-complete-slot input.
   Inject one wrong observed color in a slot with another readable occurrence as
   a negative control; this simulates a reading error, not a construction mistake.
5. Include tiny independent fixtures: `R ? Y` must reject L=1; `R ? B R Y ?`
   must support R/Y/B at L=3 while leaving original unknowns unchanged; a full
   `R Y B R Y B` accepts L=3 and rejects L=1 and L=2. A slot with no evidence
   must never receive a forced color. Compare cyclic shifts and reversal without
   relabeling physical colors.

Required outcomes: the true period remains compatible in every uncorrupted
case; any contradicted period is rejected with witness positions; known supported
slot colors agree with truth; original unknowns never become observations.
The 13-repeat phase-half case at T=100 must leave its true slot 0 unsupported,
matching R023, regardless of any shorter or longer compatible candidates. The
40-repeat full-view cases must recover all slots **conditional on L=40**, as
R023 already establishes their coverage. Do not predeclare unique recovery of
an unknown period, especially after erasures or holdout.

Publish per-case candidate/support tables and one illustration of observed versus
inferred versus unsupported colors, plus an indexed provenance report. Store
commands, seeds, source/report/output hashes, candidate range and closure policy.
Run focused tests for these failure modes and the existing suite once if shared
code changes. Stop after this sequence-only experiment and report; do not add
registration implementation or a photo refit to the same step.

### C. Later appearance gate

After the graph audit, test image-derived edges against synthetic truth before
claiming automatic indexing. Separately render new beauty fixtures with
red/yellow/black POV-Ray materials and read their colors independently of encoded
IDs. Include highlights,
black holes/background confusion and resolution loss. Calibrate readability using
separate labeled examples; confirm abstention on slivers and test on held-out
regions. Until this gate succeeds, neither old RGB beauty renders nor oracle ID
masks validate color extraction from photo 2. Keep material fitting in POV-Ray.

## Checks performed in R026–R028

This is a literature/design result. Python 3.12.14 verified all seven R023 source
hashes and all 74 artifact hashes on disk. The existing report hash remains
`12ac2b92948e920b89e7da5a49ae1ecfdfcfb44c102d4c07e53606344489c7c0`.
Pattern files, instrumentation fields and the earlier geometry/sequence code were
inspected to ensure the proposed inputs exist. No new renders, period scans,
registration runs or recovery accuracy measurements were performed. Runtime tests
are unnecessary for these documentation-only changes. Documentation consistency,
links to local files and whitespace are checked before publication.

The historical hash verification can be repeated from the repository root.
R030 changed beads.pov and the visibility test, so check old source hashes against
the method-selection Git revision rather than claiming they match today's files:

```sh
.venv/bin/python - <<'PY'
import hashlib, json, subprocess
from pathlib import Path
root = Path.cwd()
out = root / 'photo2/output/legacy-visibility-verified'
report = json.loads((out / 'report.json').read_text())
baseline = 'ab7915841577c27cfb03f779cc765e556ffc9dcd'
for name, expected in report['sources'].items():
    data = subprocess.check_output(['git', 'show', baseline + ':' + name], cwd=root)
    assert hashlib.sha256(data).hexdigest() == expected, name
for name, expected in report['artifacts'].items():
    assert hashlib.sha256((out / name).read_bytes()).hexdigest() == expected, name
print(len(report['sources']), len(report['artifacts']))
print(hashlib.sha256((out / 'report.json').read_bytes()).hexdigest())
PY
```

If historical outputs are absent, reproduce them at that Git revision with the
commands in [VISIBILITY.md](VISIBILITY.md). A new run on current sources has its
own provenance. R030's [neighbor audit](NEIGHBORS.md) independently regenerates
its required historical baseline renders and both current hands.
