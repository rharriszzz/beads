# R322 — useful photographic diagonal recovery, with a demonstrated interior row switch

**Partial automatic recovery; no expansion, 3D diagnosis or pattern inference.**
The image-only tracker recovers **24/25 clearly interior maker beads (96%)** and
**38/45 interior recorded links (84.4%)**, but makes **three wrong interior links**.
It recovers the historical **11→14→16** black-highlight case. A smooth, stable
appearance band nevertheless switches bead rows near the left red/yellow region.
This is a failure of the current automatic tracker, not evidence that the physical
necklace or a legitimate 3D representation is impossible.

[Static photographic review](r322/results/index.html) ·
[Clean diagonal overlay](r322/results/diagonals-only.png) ·
[Conditional indices and colors](r322/results/indexed.png) ·
[Failure and recovery close-ups](r322/results/failure-and-recovery.png) ·
[Machine-readable graph](r322/results/graph.json) ·
[Reproduction](R322_REPRODUCE.md).

## 1–4. What was recovered directly from the photograph?

The frozen experiment traces **11 F0 band fragments and 9 F1 band fragments** in
the original R161 viewing rectangle, in native photograph coordinates. F0 is the
cyan down-right photographic family, corresponding to historical d2; F1 is green
up-right, corresponding to d3. These are **candidate bead diagonals**, not twenty
validated complete bead sequences. Eight fragments in each family contain at
least two supported crossings. Two F0 fragments contain none; a short fragment in
each family contains only one. Fragment IDs are unique integer labels within each
family, not stitch indices or counts of steps along that fragment.

There are **34 geometric crossings**:

| Frozen classification | Count | Interpretation |
|---|---:|---|
| Confident bead | 25 | Interior, supported appearance, unique assignment and stable crossing |
| Probable bead | 5 | Supported appearance but near an edge |
| Ambiguous or unresolved | 1 | Competing appearance/crossing assignment |
| Unsupported geometric crossing | 3 | No assigned photographic observation; **not confirmed absence** |

The thirty supported crossings carry **12 red, 8 yellow and 10 black** appearance
cues. These colors come from measured pigment/brightness evidence, not an inferred
pattern. The confidence labels concern detection/association under the declared
heuristic; they do **not** certify index correctness. In particular two supposedly
confident crossings receive wrong row coordinates.

Of the **29 supported crossings associated with the maker's 40 beads**, **27** have
exactly the correct relative lattice coordinates after one origin alignment;
**two do not**. These 27 are a retrospective held-out check, not a newly selected
independent successful cohort. The remaining supported crossing is outside the
maker's numbered inventory but inside the same viewing rectangle. Its identity
has not been validated by R161. No full automatically trustworthy indexing is
claimed, and no incorrect node was silently removed.

## Method, provenance and the R171 conceptual correction

The required historical records were reviewed, including the 40-bead/86-link
R161 chart, its 47 consistent cycles, its unresolved numerical family assignment,
and R171/R173's explanation of the displaced reflection on bead14. R250's FFT
records describe reciprocal directions, not bead-to-bead angles; R277's station
motifs are not physical string indices. Those distinctions are preserved here.

The tracker uses the original `beads-photo-2.jpg`, SHA-256
`eb7c9edb62f5580ef56632872da48da92556d62b758295137068cc2404dc8fbb`.
Only the historical viewing rectangle `[1180,130,1540,520]` selects geography.
The review crop `[1180,215,1540,385]` is magnified5× using exact pixel replication.
No synthetic image is used.

1. Original RGB separates approximate rope material from pink paper. Locally
   normalized log brightness reduces broad illumination/color amplitude variation.
2. A padded spectrum retains competing peaks and reciprocal triangles. The selected
   normals are `(0.01953125,-0.029296875)` and
   `(0.0263671875,0.01953125)` cycles/pixel. Their sum agrees with a third peak
   within `0.0009765625` cycles/pixel. Every candidate triangle remains in the graph.
3. Complex demodulation with a35px Gaussian window produces spatially varying
   phase fields. Phase contours trace curved bands; amplitude/gradient/foreground
   checks break unsupported fragments. No single straight line is imposed on the
   region. Fixed28px and42px controls were saved before validation.
4. Crossings are supported by **33 reused R275 image-only bright-patch observations
   and four freshly detected bright components**. R275 station groups, body
   outlines, black collars and physical identities are not used. Supplemental
   components are detected across the image patch, not manufactured at crossings.
5. A common18px allowance associates bright supports with crossings. It is an
   exploratory location-uncertainty allowance, not a measured bead-center error.
   All colors use the same allowance; narrow black highlights do not imply small
   beads. Alternative nearby observations remain explicit. A one-to-one assignment
   prevents one bright observation from certifying two crossings.

Thus neither precise bead centers, complete segmentation nor black-bead outlines
are prerequisites. The curves come from continuous multi-bead image structure;
selected reflection points are never joined through a pairwise angle gate.
The preliminary new pigment-mask prototype split shaded yellow regions into red
fragments; its source/results are preserved and were replaced by the older
image-only measurements **before** the held-out evaluation.

Runtime independence is audited: the final detector reads only the photograph,
R275 appearance catalog and its own source for hashing. It reads **no maker graph,
maker locations, R319/R321 positions, model-selected cohort or fitting code**.
The developer had read the requested historical summaries, so this is a runtime
data holdout, not a claim of developer blindness to that history.

## 5. Held-out recovery, with interior evidence reported first

Interior means photo-mask clearance≥18px at the maker's surface pick, fixed before
scoring. This operational partition is imperfect because picks are not centers;
all40 beads remain in the denominator below. It never depends on whether a link
is correct. The user's instruction to prioritize interior evidence is therefore
not used to hide the three interior errors.

| Quantity | Clear interior | Entire R161 inventory |
|---|---:|---:|
| Maker beads | 25 | 40 |
| Automatically supported and associated | **24 (96%)** | **29 (72.5%)** |
| Unresolved maker beads | 1 | 11 |
| Recorded links | 45 | 86 |
| Correctly directed recorded links recovered | **38 (84.4%)** | **50 (58.1%)** |
| Recorded links given the wrong family | 2 | 2 |
| Recorded links abstained/unresolved | 5 | 34 |

Among **56 automatic accepted conditional links**, **51 agree with the maker
chart**, **three disagree**, and **two have unvalidated endpoint identities**.
Fifty agreeing links are explicitly recorded in R161; the remaining one agrees
with its implied chart. The third wrong automatic link is not a recorded R161
edge, which explains why there are three wrong automatic links but two recorded
links assigned the wrong family. Implied difference links remain distinguished
from independently traced F0/F1 links.

Evaluation matches arbitrary maker surface picks to appearance observations, not
to hypothetical bead centers. All29 associations have margins above10px to the
nearest rival in the matching table and were inspected on the original-photo
validation overlay. This visual inspection is by the same assistant, not new
maker confirmation. At association radii14,18 and22px and margins0,3 and5px, the
29 matches, 50 recovered links and three wrong links are unchanged. Radius10px
abstains on two additional associations, recovering43 links, and still exposes
all three errors. The association sensitivity does not erase the failure.

[Every bead and recorded link](r322/results/validation.json) ·
[Original-photo association overlay](r322/results/heldout-validation.png).

## 6. First error: an appearance band switches rows in the clear interior

The first error, ordered by the smaller maker bead number, is **2→3** near
`(1211,304)→(1224,337)`: the frozen F0-02 track calls it d2, while the maker graph
records d1. **4→5**, near `(1228,280)→(1240,310)`, is also called d2 instead of d1.
The resulting **4→3** difference link is wrong as well. The real multi-bead yellow
row **1→4→8→11** and neighboring red/yellow row **2→5→9** make the continuation
error visible without requiring exact centers.

Under origin X017 (maker23), beads2 and4 have residual chart coordinates
**`(Δa,Δb)=(0,-1)`**. Their index errors are−6 in interpretation A and−7 in B.
The other27 associated beads have zero coordinate residual. This is a row-identity
error; no global translation, global reversal or exchange of6/7 removes it.

The wrong crossings are numerically stable: bandwidth28/42 shifts are
**0.702/0.591px for bead2** and **0.866/0.493px for bead4**. Smoothing stability and
unique appearance association therefore fail as correctness certificates.
The appearance phase is not a guaranteed material-row coordinate. The observed
row switch is established; a unique causal attribution to pigment, illumination
or texture is **not** established by this round.

The remaining unresolved *interior* maker bead10 already has a fresh black
reflection observation (`NEW-1265-270`). It lacks a supported crossing in the
frozen bands. It is not omitted for lack of a reflection or because that reflection
failed a theoretical pair-angle test. Six appearance observations remain
unassigned to crossings; all are retained in the diagnostic ledger.

Conversely, **11→14 and14→16 are both recovered as F1/d3**. Bead14's old reflection
observation stays where the photograph put it. R171's point-angle mistake has been
avoided, but a different row-continuation failure remains.

[Exact mismatch and coordinate ledger](r322/results/diagnosis.json).

## 7–8. Expansion, integer algebra and remaining6/7 ambiguity

The automatic graph has30 supported vertices,56 accepted conditional links, one
connected component and **27 independent cycles**, with zero algebraic conflicts.
The independently reconstructed R161 graph retains40 vertices,86 links and47
consistent cycles. The automatic cycles close **partly by construction from phase
coordinates**; they demonstrably coexist with wrong photographic links. They are
not independent evidence that the recovered rows are correct.

Let `a` count steps along F0 and `b` along F1. The F0 curve's constant coordinate
is `b`; the F1 curve's constant coordinate is `a`. Display fragment IDs are separate
from these coordinates. The arbitrary automatic origin is **X017**, at approximately
`(1365.8,296.0)`, associated afterward with maker23.

- A: `k−k0=7a+6b`; in the user's notation `(u,v)=(b,a)`.
- B: `k−k0=6a+7b`; in the user's notation `(u,v)=(a,b)`.
- Both global reversals are retained. `F0−F1` gives+1 in A and−1 in B.

Neither family assignment is selected by the validated local relations. Global
index origin and physical orientation remain unresolved. No total bead count is
inferred. Equal weighted indices at distinct planar coordinates are recorded as
possible wrapping identifications, not automatically merged or called collisions.
The42-index relation is tested explicitly; no such identification occurs among
this run's supported crossings. Longer closure is untested.

The predeclared interior expansion gate requires90% bead/link recovery and zero
wrong interior links. It fails on link recovery and the three errors. **No region
beyond the initial R161 rectangle was searched and no50–100-bead claim is made.**
The retrospectively consistent27-bead subset was not used to bypass that gate.

## 9–11. What does this establish about R319 and R321?

**No new photographic comparison with those models was performed.** Their reports
were reviewed, but their positions never entered the detector. The prerequisite
of a trustworthy independently recovered automatic lattice was not met.

| Requested frozen model | Same local connectivity? | First model/photo disagreement | A–E classification |
|---|---|---|---|
| R319 best conditional geometry (`best-full`) | Not evaluated | Not established | E: insufficient trustworthy automatic topology |
| R321 geometry-best, N3000 | Not evaluated | Not established | E: same prerequisite failure |
| R321 photo-sized-rescue, N2800 | Not evaluated | Not established | E: same prerequisite failure |

E here explains the deferred diagnosis, not a newly observed model mismatch.
There is no evidence from R322 selecting incorrect correspondence, incorrect
physical topology, geometric placement or optics as the old models' cause.
No concrete old-model coding defect or mathematical counterexample was found,
and no R319–R321 source/result was modified or silently repaired.

## 12–13. Pattern readiness and the remaining obstacle

**Pattern inference is deferred.** There was no repeat-length scan, no color
completion, no adoption and no pattern-based repair of a photographic connection.
The local indexing errors and unresolved family/origin choices make such a scan
premature. Prior short motifs remain motifs, not verified physical repeats.

The next obstacle is **preserving bead-row identity when a smooth image band
transfers to a neighboring row**. A next authorized experiment should retain joint
path alternatives through several supported bead surfaces and neighboring cells,
using spectral phase as directional evidence rather than row identity. It should
explicitly test whether a candidate continuation skips a photographed bead or
changes rows, including black reflections with uncertain body location. The
failed links must remain held-out failures; simply splicing them using R161 and
calling the result automatic would not solve the problem. No such repair or next
round was launched.

## Measured cost, independent checks and delivery

Final isolated detector stages, seconds (existing environment, one numerical
thread; no rendering):

| Stage | Seconds |
|---|---:|
| Image decode/preprocessing | 0.0833 |
| Spectral direction analysis | 0.0572 |
| Curved-band tracing, including28/42px controls | 0.2998 |
| Crossings, catalog/native evidence and assignments | 0.4000 |
| Graph consistency | 0.00086 |
| **Stage sum** | **0.8412** |
| Pattern search | Not run |
| Frozen3D comparison | Not run |

A later guarded replay took1.116s including serialization, with1.002s in the
measured stages. These timings describe this local image task, not a measured
speedup over an equal-workload3D reconstruction. Imports and human review are
outside the detector stage timing. Held-out evaluation timing is saved separately.

Independent arithmetic verifies every graph edge and index alternative, the
40/86 maker graph, all50 recovered recorded links, all three wrong links,
**37 observations /795 original native support pixels**, raw review pixel identity,
and deterministic replay. A runtime file-access guard verifies the detector's
input separation. Eight verification contracts include a deliberately corrupted
cycle and the7×6=6×7 identification. Verification is by independent formulas in
this session, not an external human review.

The audit caught an adapter defect: R275 pixel-run endpoints are inclusive; the
first export used an exclusive Python range. The corrected support export preserves
**all33 existing catalog observations and every scientific decision exactly**:
tracks, positions, colors, crossings, indices, links and controls. The original
source, outputs, prevalidation freeze and first held-out evaluation are archived
under `r322/development/frozen-v1`; the correction has a separate receipt. It is
not post-validation tuning. A tuple/list serialization mismatch in the replay
checker was also fixed without changing the detector.

[Independent verification](r322/results/verification.json) ·
[Freeze and correction provenance](r322/results/freeze.json) ·
[Pixel-decoder correction](r322/results/support-decoder-correction.json) ·
[Browser checks](r322/results/browser-check.json) ·
[Commit/push receipt](r322/results/delivery.json).

Start07:56:22UTC, scientific cutoff08:20:22UTC, delivery deadline08:26:22UTC,
2026-10-18. The final validation/documentation period began before the cutoff.
Original photo, annotation files, `beads.pov` and all previous scientific results
are preserved. **STOP for scientific review. No automatic R323 or final pattern.**
