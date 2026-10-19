# R331 — predictive lattice structure, unresolved actual design

**104/208 predicts real, organized color structure in the conditional lattice;
it is not an acceptable recovered shortest design under the maker's constraint.
B/207 is arithmetically admissible but predicts poorly. No design-compatible
exact pattern is recovered.** A/306 and B/305 are the strongest compatible-length
predictive candidates in this bounded scan, but are much weaker, share exactly
the same observed residue partition, leave over 100 residues unseen, and do not
divide their conditional counts. The unresolved conflict implicates the working
indexing/count interpretation or a more complicated spatial alias; it does not
justify replacing the maker's information.

[Compact photographic review](r331/review/index.html) ·
[Four-problem presentation](r331/review/presentation.html) ·
[Presentation PDF](r331/review/presentation.pdf) ·
[Reproduce](R331_REPRODUCE.md) · [Independent checks](r331/verification.json) ·
[All period scores](r331/results-final/periods.csv).

R328's working 900 observations / 1862 links / H=(214,201) remain unchanged.
No old observation, source, pixel, label, alternative, failed experiment or
provisional hypothesis is overwritten. There is no new detection, growth search,
physical fitting or rendering. The input commit is `422a85e`.

## Arithmetic and the actual 208/207 relationship

The maker's shortest-repeat restriction in INITIAL_QUESTION.md is a construction
constraint. A predictive period can summarize some visible structure without
being the physical shortest repeat. Exact repetition additionally requires
divisibility of the true physical count and compatibility with every true color;
the reconstructed count and labels here are conditional.

| Convention | Index | Conditional N from H=(214,201) | Exact divisors in 200–399 | Maker-compatible |
|---|---|---:|---|---|
| A | 7a+6b | 2704 | 208, 338 | Neither |
| B | 6a+7b | 2691 | 207, 299 | Both |

Independent integer enumeration confirms these lists. 2704=13×208=8×338;
2691=13×207=9×299. The maker excludes shortest lengths divisible by 13,
**not total counts divisible by 13**. If the working A count and the approximate
200–399 range were both exact, A admits no compatible shortest design.
B remains arithmetically possible, not photographically established.

From the actual lattice definitions:

```text
A − B = a − b = d
A + B = 13(a + b)
B ≡ −A (mod 13)
Δa = (7ΔA − 6ΔB)/13
Δb = (−6ΔA + 7ΔB)/13
```

Simultaneous ΔA=208 and ΔB=207 requires
`(Δa,Δb)=(214/13,201/13)=H/13`, a fractional lattice vector.
Thus “A/208 becomes B/207” is not an integer change of labels per repeat.
Only thirteen such fractional steps sum to the measured conditional winding.

The saved observations give a sharper empirical result:

| Observed separation | Number of pairs | Actual lattice displacement, every pair | Other convention | Same recorded color |
|---|---:|---|---|---:|
| A+104 | 738 | (8,8) | B+104 | 577/738, 78.2% |
| A+208 | 623 | (16,16) | B+208 | 585/623, 93.9% |
| B+207 | 605 | (17,15) | A+209 | 89/605, 14.7% |
| B+299 | 519 | (23,23) | A+299 | 88/519, 17.0% |
| A+306 / B+305 | 627 | (24,23) | Same observed pair set | 315/627, 50.2% |

These overlapping pairs are correlated, not independent trials. Each observed
A+208 pair advances its B/207 residue by **one**, since ΔB=208≡1 mod207.
For `A=208q+r`, `B mod207=(q+r−d) mod207`. The measured A+208 pairs have
Δd=0, so their phase drift is exact. This directly contradicts a simple
unchanging B/207 motif explanation on those assignments. B/207's poor prediction
is therefore not merely a failure to adjust one global origin.

104/208 follows eight/sixteen steps along the local (1,1) lattice direction,
returning to the same phase modulo13. This explains a geometric opportunity for
aliasing and why doubling 104 can separate alternating color halves. It does
**not** show that geometry alone creates the colors. A 13-phase baseline has only
.0297 nats predictive gain, far below 104/208; stronger phase-preserving controls
also fail to reproduce the advantage. The supported interpretation is organized
spatial/color structure plus possible indexing errors. The actual non-13 design
that would generate it remains unidentified; a pure visibility-only account is
insufficient under the tested controls.

## Fair cached-data comparisons

The scan reuses R330's `dataset`, weighted residue counts, Dirichlet prediction
and development selection code. All 20 saved maps × both conventions are scanned
at 104 and every length 200–399: 8040 map-period development fits. Both working
conventions then receive leave-one-section-out prediction for all 201 lengths;
all maker-compatible exact divisors of other saved maps receive the same check:
419 fits total. All target scoring uses the same 900 working observation IDs;
missing candidate associations receive the training frequency baseline. Additional
candidate observations are not allowed to improve that score.

Training excludes the entire target photographic section. A stronger guard also
excludes its two adjacent sections. All new evaluations are **exploratory reuse
of R330 observations**, even where target exclusion is computationally exact.
There is no fresh blind test or new independently labeled photographic cohort.

Main weights remain 1 for red/yellow, .55 for black, .25 for the provisional site.
They are sensitivity assumptions, not measured classification confidence.
The primary flat comparison uses identical shrinkage strength3 and scores log
gain over training color frequencies. The description penalty is
`.1 × P × log(3) / total_weight`. Hierarchical models additionally charge their
parent length. Held-section prediction penalizes unsupported extra parameters
through shrinkage as well. Hierarchical A/208 uses parent104/strength1 as in R330;
B/207 uses the legal proper-divisor parent69, explicitly a different prior.
The flat comparison remains the principal fair cross-length comparison.

| Working map/model | Log gain, nats/weighted observation | Hard agreement with original labels | Exact own-count repeat? | Maker-compatible shortest length? |
|---|---:|---:|---|---|
| A/104 flat | .6088 | 82.67% | Yes | No |
| A/208 flat | .5745 | 86.56% | Yes | No |
| A/208 hierarchical104 | .8260 | 91.89% | Yes | No |
| B/207 flat | −.0557 | 35.89% | Yes | Yes |
| B/207 hierarchical69 | −.2211 | 29.44% | Yes | Yes |
| B/299 flat | −.1348 | 30.00% | Yes | Yes |
| A/306 flat | .1277 | 51.67% | No | Yes, length only |
| B/305 flat | .1277 | 51.67% | No | Yes, length only |
| A/222 flat | .1135 | 50.67% | No | Yes, length only |
| B/220 flat | .1068 | 50.44% | No | Yes, length only |

A/306 and B/305 induce **identical residue partitions on all 900 observations**;
their complete held-section probability arrays are identical. They are one
observed-data explanation expressed two ways, not two independent discoveries.
Both are cut-sensitive because they do not divide N. Across five cyclic cuts
their log gains range about .103–.131. Exact-divisor 104/208/207/299 scores are
cut-invariant. These controls prohibit promoting a useful unwrapped prediction
into an exact necklace design.

No maker-compatible exact divisor among the other 19 saved maps scores positively
in this test. The best is saved-16 A: N2718/L302, −.0156 nats. This does not exclude
L302 or any other physical design globally: those labels and maps are uncertain,
and the finite bank is not exhaustive. The observation classes and candidate maps
were not independently validated on the full photograph.

With adjacent sections excluded, A/104 falls to .4696, hierarchical A/208 to
.6767; A/306 and B/305 retain .1238. A/222 and B/220 fall to .0012/.0032.
B/207 improves to .0458, still far below the leading aliases; B/299 remains
negative at −.0637. Removing nearby training conflicts can help an incorrect or
inconsistent mapping, so that small B/207 improvement is preserved rather than
hidden. It is not recovery of the motif.

At black weights .25/.55/1, hierarchical A/208 scores .7520/.8260/.8543;
B/207 flat scores −.0192/−.0557/−.0929. Colored-only prediction gives .6062 for
hierarchical A/208 and .0235 for B/207. Equal-section weighting leaves A/208 at
.8266 and A/306/B305 at .1263. Thus black visibility and section imbalance matter,
but neither accounts for the large gap. A one-step bounded minority-downweighting
consensus changes A/208 only .0001 nats and does not rescue B/207. No minority
observation is deleted or relabeled by that fit.

Per-section scores, per-color scores, descriptive section standard errors and
all complexity scores are serialized. Twelve geographic sections are correlated
units; the standard errors are not calibrated confidence intervals for physical
truth. Hard agreement and log gain answer different questions and are both shown.

## Stronger null controls

Two controls each repeat the **full 40-map × 201-period development selection**
in 19 deterministic trials. Their observed maximum selection score is .44050.

| Null | What it preserves | Largest null selection score | Nulls reaching observed |
|---|---|---:|---:|
| Per-section index translation by 13×integer | Every local relative index, observation, color, weight, ordering and phase13 in each section, for every map | .11179 | 0/19 |
| Circular color/weight rotation within section × working geometric phase | Exact working-phase color/weight totals and most ordering within each phase lane | .01453 | 0/19 |

The first breaks relations between sections while preserving **all** their
internal photographic correlations. It is not a legal alternative whole graph;
that is intentional for a null. The second preserves the working map's phase
exactly, not necessarily another map's differing phase assignments, and breaks
some cross-lane body correlations. Both retain more relevant phase structure
than unconstrained label rotations. Fixed-model A/104 and hierarchical A/208
also exceed every corresponding null score. The finite empirical tail is 1/20
for each global comparison. Nineteen trials do not support a finer p-value, an
exhaustive alias rejection, or photographic correctness certification.

## Error-tolerant recovery: improvements and honest failure modes

Three useful mechanisms are implemented: weighted robust periodic consensus,
hierarchical probabilistic motifs, and a constrained observation-level latent
model. The latter compares unchanged/color-substitution/index-shift states with
fixed priors .80/.12/.08, offsets ±1/±6/±7, cached distant-section appearance votes
and a frozen target-section-excluded motif. It abstains unless one state beats
unchanged by2, the runner-up by1.5 and has at least .5 normalized state mass.
Those masses are model scores, **not calibrated correction probabilities**.
Several offsets can produce the same color; index-type evidence is reported
separately from a unique exact edit. Any proposed edit is checked against frozen
incident links; no graph-changing edit is adopted.

Deterministic copies of observations in four held sections receive isolated
substitutions, color bursts, isolated ±1/±6/±7 index changes, +1/+6/+7 index bursts,
or withheld observations. The image and cached appearance evidence stay fixed.
That is appropriate for synthetic classification/export errors, but easier than
discovering new body identities in a photograph. The original noisy labels and
indices are the evaluator reference, not newly established truth.

Selected A/208 results, summed over the four sections:

| Perturbation | Appearance-aware latent model | Motif-only latent model | Regional Viterbi, penalty6 |
|---|---|---|---|
| 24 isolated color substitutions | 24 restored; 3 unchanged targets edited | 15 restored; 0 unchanged targets edited | 0 restored; no shifts |
| 48 color-burst observations | 41 restored; 2 unchanged targets edited; 0 index edits | 25 restored; 0 unchanged targets edited | Explains 42 as shifts; 7 other targets shifted |
| 144 isolated index changes | 52 index-type flags; **0 unique exact restorations** | 0 exact restorations | 0 exact restorations |
| 144 index-burst observations | 51 index-type flags; 0 unique restorations | 0 exact restorations | 56 exact restorations; 23 other targets shifted |

The appearance model proposes 3 color edits in the clean 303-observation control;
the motif-only model proposes none. These count as false proposals relative to
the frozen reference even if a historical label might actually be wrong. Reused
targets across perturbations are not independent trials. The complete 416-record
ledger includes B/207's poor behavior: Viterbi shifts 294/303 clean B/207 targets.
This demonstrates why a decoder should not be trusted merely because it can
align colors to a weak motif. Under A/208 withheld observations induce no shifts;
under B/207 Viterbi's existing false shifts persist. Unknown positions never
generate evidence of a physically missing bead.

A separate frozen-neighbor equation check recovers 138/144 A and 126/144 B
isolated **bookkeeping** index errors with no false index correction, but none of
the sustained bursts. It requires ≥2 and ≥75% agreeing neighboring equations.
This is a useful export/integrity safeguard, not proof against coherent wrong
photographic rows: the selected working graph already satisfies its equations,
and competing G continuations satisfy their own equations. The two mechanisms
must remain separate. Combining appearance/graph integrity reduces a known
failure mode; it does not solve uncertain topology.

Nine exact duplicate-ID injections are all flagged; no observation is merged or
deleted. This only tests deduplication of identical IDs. The real close pair
E5-1499-3037 / K-1508-3038 remains an unresolved distinct-ID duplicate/neighbor
case from R330, not a solved association. Saved G alternatives, rather than
arbitrary single-coordinate edits, represent row-continuation uncertainty.

## G reconsidered without treating 208 as the actual design

All 44 saved R330 width128 G candidates are reevaluated on their own A/B maps,
common 900 targets, with entire target sections withheld. The five local G
targets additionally exclude section0 **and adjacent sections11/1**. No target
color chooses a new G map or trains its local prediction. Candidate ranking here
remains exploratory because the bank and length choices are already exposed.

| Map | A/208 hierarchical | B/207 flat | B/299 flat | A/306 (=B/305 here) |
|---|---:|---:|---:|---:|
| Working H214,201 | .8260 | −.0557 | −.1348 | .1277 |
| Best photographic G, G-0 H214,200 | .6474 | −.0405 | −.1305 | .1369 |
| Same-winding G-28 H214,201 | .7251 | −.0365 | −.1264 | See full ledger |

Under B/207, the three same-winding candidates improve slightly on working but
all remain negative (−.0365 to −.0387). For the five G targets trained outside
sections11/0/1, their mean log gain is −.3268 versus working −.0205. No B/207
same-winding candidate becomes a strong local and global explanation.
The best arbitrary G B/207 score is −.0209 on G-26; its own N2683 is not divisible
by207. No change is justified by that score.

The weak 305/306 diagnostic is less hostile to G than208: G-0 improves .0092 nats,
and G-9 reaches .1420, versus working .1277. **This changes the interpretation of
the R330 conflict:** failure against208 cannot serve as a design-based veto on
G's locally better geometry. However, these 305/306 fits still do not establish
exact cyclic compatibility or a recovered design; their local held-G gain is
weak. They justify preserving G, not a larger search or adoption.

The independent photographic comparison remains exactly R330's cached result:
same 11 references, quadratic colored-pigment fit, target misses working
21.41/21.21/20.28/28.60 px versus alternative9.10/9.51/10.01/24.84.
Wider contexts remain sensitive, especially the fourth target. These measure
partial colored regions, not black-body centers. The presentation shows the
same original context, neighboring diagonal rows, all target IDs, both A/B
indices and the prediction vectors. Original global photographic score still
favors working; target-local geometric preference is not overall score victory.

## Color proposals and four visual review problems

The six provisional red→black hypotheses remain NEW-1706-342, E5-2306-2092,
E5-1616-2970, E5-1111-2848, E5-1360-1455 and E7-0290-1001. Their cached appearance
evidence is unchanged. A/208 held-section black probabilities are .860–.927;
B/207 gives .096–.267 and favors no black reading at any of the six sites.
That difference is motif dependence, not photographic disproof of dark material.
R330's strict appearance tier accepted none; its weaker exploratory tier still
defines their provisional status. No color is verified or adopted here.

The new latent A/208 model retains those six and flags C-1284-0332 red→black,
NEW-1927-2829 black→red and NEW-451-650 red→black. These additional flags have
weaker/variable appearance controls and remain **unverified model flags**, not
recommended corrections. The review includes identical working/hypothesis
contexts and IDs/indices for all nine. There are no proposed unique real index
corrections; multiple explanations remain plausible.

The requested presentation frames four concrete problems as review tasks:

1. **G row continuation:** compare the first red sequence with the neighboring
   yellow diagonals; the alternative's lower local target error competes with
   downstream consequences.
2. **Black/color association:** inspect visible dark material at NEW-1706 and
   compare black and red sequences in the **same [0,+1] direction**. Three dark
   inspection areas and separate colored rows are annotated. Supports are not
   measured centers, and boxes are not inferred body outlines.
3. **Inward-bend diagonal/count sensitivity:** compare C-1721→K-1740 in both
   assignments using adjacent yellow directions and dark-body context. Cached
   native predictions favor working, but the competing windows124–126 replay
   completely and change N. A visually supported family choice would matter.
4. **F material correspondence:** compare actual colored pixels with saved model
   boundaries before/after the common +8/−4px raster translation. It improves the
   reference from59% to99% while two other targets remain near49%. A visibly wrong
   ownership association would redirect correspondence work; the crop does not
   identify the physical parameter responsible.

These are explicit evidence-reading tasks in a ten-slide presentation, with
separate label/evidence slides where needed. They do not manufacture a required
yes/no answer or ask the user to certify a physical model. Each uses literal
original pixels and matched contexts; captions describe only drawn features.
The F raster comes from an incompatible frozen N3000 diagnostic, clearly labeled;
no new physical fitting is implied.

## Unknowns, verification and stopping point

Full-data conservative consensus retains 154/208 entries for A/208, 19/207 for
B/207, 11/299 for B/299 and 46 entries for either A/306 or B/305. Unknown counts
are respectively54,188,288,260 and259. All 207/299 residues have at least one
observation; their unknowns mostly reflect insufficient agreement/support.
A/306 has104 wholly unobserved residues; B/305 has103. No unknown is filled to
complete a design. CSVs list every residue and source observation ID/index.
A new reliably associated/color-read occurrence, or a verified changed row
continuation, could resolve a residue; more motif-driven relabeling would not
supply independent truth.

Evidence accounting:

- **Independently recomputed:** integer A/B arithmetic, 1361 alias-pair witnesses,
  419 common-cohort period fits, 274 own-map G fits, 22 hierarchy/guard fits,
  five additional pair counts, 104 graph-metadata perturbations, 25 exact RGB
  crops and preservation against the R330 baseline. This tests code/provenance,
  not photograph interpretation.
- **Exploratory:** every R331 predictive score, stronger null, sensitivity,
  post-scan 305/306 comparison, perturbation result and visual review selection.
  R330's original held-out result remains historical; it is not reopened as a
  new blind test. No newly independently labeled photographic evidence exists.
- **Conditional on uncertain assignments:** every N, exact-divisor statement
  about the necklace, motif entry, G consequence and proposed color change.
  The maker facts remain construction information, separate from inferred maps.

Main analysis takes37.0s on cached inputs; the first preserved epoch took39.6s.
The final 416-record error study takes.76s, initial version.54s. Independent
numerical verification takes about5.7s. Two small implementation corrections
(provisional-site sensitivity weight and robust parent retention), the original
epochs, and an empty-color-cohort export failure are preserved under development.
No broad parameter search, new bank or physical render was used. These are
cached-data costs, not detector speedups or convergence estimates.

**Most valuable next investigation:** a bounded, color-independent body and
diagonal-correspondence audit at **G**, comparing the same lattice direction in
nearby colored and black sequences, then replaying only the already implicated
windows if a concrete assignment is supported. The maker/count conflict cannot
be solved by optimizing a motif inferred from the same uncertain map.

Stop for review after scoped commit/push and remote confirmation. No automatic
R332, count/winding/pattern adoption or model/session switch; keep the user's
current session. Delivery receipt records the actual pushed commit.
