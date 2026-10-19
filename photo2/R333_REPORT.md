# R333 — repeated staircase spirals and a concrete interruption atlas

**The photograph supports recurring black–red and black–yellow staircase structures.**
Their long direction combines the two diagonal neighbor families; the third
primitive family is mainly transverse in these traces. A bounded search favors
three-step diagonal runs for black–red and two-step runs for black–yellow, with
nearby alternatives retained. These are useful local rules, not uniquely
identified physical strands. Seventeen regular traces have at least two distant
measured counterparts, covering201 indexed observations. The more inclusive
59-trace atlas covers592 observations.

Repeated neighborhoods expose **19 significant recorded-color disagreements**.
Three red-to-black hypotheses also pass a separate photographic appearance
screen; one is new relative to R330's six proposals. There are128 prioritized
unknown working sites, including50 with native candidate or known-unindexed
support matching the repeated feature. No observation, color, coordinate, link,
winding or physical model has been changed.

The full shortest stringing sequence remains unidentified. The leading useful
partial motif is still the maker-incompatible208 structure, now with **166 known
positions and42 unknowns**, versus154/54 in R331. Maker-compatible305/306 aliases
explain much less and fail closure under their own current windings. The new
spiral evidence localizes errors and clarifies what208 describes; it does not
justify declaring it the maker's actual repeat.

[Interactive photograph + graph paper](r333/review/index.html) ·
[Detailed matched problems](r333/review/index.html#cases) ·
[Whole unwrapped lattice](r333/review/index.html#unwrapped) ·
[Ranked error/gap ledger](r333/diagnosis/ledger.csv) ·
[All period scores](r333/periods-selected/periods.csv) ·
[Reproduction](R333_REPRODUCE.md) · [Independent checks](r333/verification.json).

## Inputs, conventions and evidence boundaries

Baseline is `d726ef590e56bfaa29f54f8ba142a054ba88019e` on
`photo-2-strategy-v3`:1064 recorded observations,1041 indexed,378 red/317 yellow/
346 black,2285 links and conditional H=(214,201). All R332 uncertainty,263
additional provisional groups and saved alternative histories are preserved.
The positive R331 user review applies to the displayed labels/links, not the
unreviewed R332 additions. This round uses cached observations and original RGB;
there is no new detector, growth bank, physical fitting or rendering campaign.

Coordinates are R332's relative(a,b), reference C-1302-0316. F0=(1,0),
F1=(0,1), difference=(1,−1). A=7a+6b and B=6a+7b; thus the families represent
7/6/1 under A and6/7/−1 under B. Both reversals are checked. The rotated strip
uses s=a+b and d=a−b; only equal-parity(s,d) pairs are lattice sites. The viewer
also offers literal graph-paper(a,b) axes. These transformations do not establish
physical centers or exact stringing counts.

The maker's new black–red/black–yellow information motivates the two palettes.
Alternation, exclusive black membership, uniform widths and a particular slope
are **not** input assumptions. Unknown colors remain unknown.

## Discovering the structures

Three complementary implemented approaches were evaluated:

1. **Palette connected components.** These identify regions, but do not identify
   unique strands:522 black–red and416 black–yellow vertices have degree>2 in
   the respective induced graphs. Largest components contain32 and37 nodes.
   The full component inventory is retained rather than called a recovered spiral.
2. **Flexible directional path cover.** Dynamic programming in each of six
   directed neighbor cones rewards length and color transitions, with a small
   turn penalty. Greedy extraction supplies nonexclusive palette traces, requiring
   at least six measured nodes and at least two of each palette color. It never
   fills a gap or invents an edge. Opposite traversal and all cones are preserved.
3. **Regular staircase search plus repeated patches.** Exhaustively test108
   orientation/run-pair templates per palette: three cones, two run lengths1–6,
   every cyclic step phase, up to32 steps. Every step must be a working link.
   Trace extraction then retains measured runs of at least eight nodes. Distant
   copies of the same shape and colored neighborhood determine the stricter
   repeat-supported subset.

The flexible search finds27 black–red segments of6–17 nodes and20 black–yellow
segments of6–18. Together they cover537 distinct observations:189 red,149 yellow,
199 black. Twenty-five black observations participate in both palette covers.
The leading cone uses F0/F1; other cones produce only6–7-node mixed segments.
Reverse greedy extraction changes segmentation, confirming that endpoint choices
and strand identities are not unique.

The regular search selects F0³/F1³ for black–red and F0²/F1² for black–yellow.
For black–red,2/2 is close(1.086 versus1.104 search score); for black–yellow,
3/3 is also plausible(.736 versus.782). The score is the mean excess continuation
length above five nodes across all1041 starting observations, maximizing over
step phase. It is not a probability. Directions are learned, not imposed by the
maker's recollection.

| Measured regular traces | Segments | Node-length range | Summed node incidences | Summed link incidences | Distant-repeat-supported segments |
|---|---:|---:|---:|---:|---:|
| Black–red | 37 | 8–16 | 422 | 385 | 12 |
| Black–yellow | 22 | 8–15 | 245 | 223 | 5 |

Shared nodes/links make incidence totals unsuitable as distinct-bead totals.
The59 traces cover592 distinct observations(56.9%). A repeat-supported trace
requires **two** geographically separated copies, each with≥6 measured matching
locations,≥85% recorded-color agreement and≥4 measured corresponding edges.
These17 traces cover201 distinct observations(19.3%). All accepted trace edges
are measured working edges; **zero inferred continuation edges** enter this count.
Copies are comparisons within one photograph, not independent ground truth.

The observed mixed-palette widths in fixed-s slices are mostly2 or3 recorded
sites: black–red112 width2/61 width3/one width4; black–yellow85/51/one. These
partial widths are censored by visibility/inventory and are not complete physical
band widths. Regular traces share black junctions and branch alternatives; no
exclusive assignment or unique physical intersection is asserted.

## Repetition, controls and continuation rules

An independent two-dimensional translation scan finds **698/748 matching colors
at displacement(16,16),93.3%**. Displacement(8,8) gives672/872,77.1%.
Both palettes therefore share a spatial repeat with a weaker half-repeat.
Under either convention,(16,16) adds208; the half-repeat adds104. This gives the
old periodic finding a concrete graph-paper interpretation: recurrence of the
same colored staircase neighborhoods along the rope. It does not prove that
208 is a complete stringing repeat or that the working lattice is exact.

A strict spatial-copy predictor excludes the target geographic section **and
both neighboring sections**, requires≥3 supporting observations in≥3 remaining
sections and≥80% agreement. It qualifies228/1041 targets:209 agree with the
recorded color and19 disagree. It abstains on813. These228 predictions and all
source IDs are serialized; the19 disagreements are the observed-break ledger.
The broader spatial probability model also reports full-cohort held-section-out
scores, without turning abstentions into known motif entries.

Controls matter here. Palette paths alone are not decisive: phase-lane rotations
can create longer flexible covers. Repeating the full regular-template search
in19 local-order/phase-preserving controls gives an empirical tail of.10 for
each selected palette score. Thus the exact2/2 versus3/3 distinction is tentative.
The much stronger spatial recurrence is harder to reproduce: among39 geographic
circular-label controls, each selecting its best of241 eligible translations,
the greatest agreement is56.1%, below93.3%. These finite controls do not preserve
every possible2D pigment/visibility correlation and do not certify the map.

## Interruptions and reversible explanations

The ledger separates observed rule failures from unknown working sites. The
regular endpoint atlas records **236 continuation alternatives** at118 endpoints:
123 hit a different recorded palette,65 have a same-palette branch and48 reach
an unknown site. Most are not automatically errors; a different palette can be
a designed boundary, and greedy/regular path termination is not bead absence.
The19 strong observed disagreements satisfy the independent-copy rule above.

The native appearance screen learns from other geographic sections using RGB
quantiles in radius8/12/16 disks and15/31/51 nearest labeled examples. A color
hypothesis requires agreement with the distant spatial expectation, the same
winner in all nine appearance controls, a minimum vote≥.55 and mean vote≥.75.
These are transparent review thresholds, not calibrated error probabilities.
Dark context may contain shadows or seams; no highlight or prediction is used
as a measured black-body center.

| Observation | Native support(x,y), rounded | Recorded → hypothesis | Independent status |
|---|---|---|---|
| C-1284-0332 | (1284,331) | red → black | New relative to R330's six proposals; four distant copies agree |
| E5-1616-2970 | (1617,2971) | red → black | Prior R330 hypothesis, re-supported here; three copies |
| NEW-1706-342 | (1705,343) | red → black | Prior R330 hypothesis, re-supported here; three copies |

Exact coordinates, both indices, all original labels, votes, same-direction
neighbors and comparable examples are in the ledger JSON and illustrations.
The remaining16 observed breaks are unresolved color/body-association/index/
design-rule alternatives. They are not recommended relabelings. The contrasting
NEW-1927-2829(black versus expected red) and REC266-P146299(red versus expected
yellow) are explicitly illustrated, preserving alternatives to a universal
red-to-black explanation.

Four overlapping groups contain multiple rule failures. Each gets ten coherent
patch translations, preserving internal equations while testing every boundary.
None is admissible under the retained graph. For example, shifting the11-node
NEW-2060-796 patch by(0,−1) improves the spatial likelihood by1.73 but violates12
boundary links and collides with an occupied site. Explaining two disagreements
that way would require independent photographic evidence to replace those links.
No isolated index edit is accepted.

The128 significant unknown working sites divide into:

- 44 with a matching-color native provisional candidate;
- 6 with a known unindexed observation candidate;
- 30 with a competing-color native candidate;
- 48 with no recorded native body at that proposed site.

These are site hypotheses in the exposed envelope, **not128 confirmed missing
visible or physical beads**. Candidate association rejection reasons remain in
each record. Unknown/occluded, adjacent-body confusion, inventory omission and
an incomplete spiral rule remain competing explanations. No native candidate
has been promoted and no purely predicted color is painted onto an observation.

The bounded feedback iteration applies only the three color hypotheses in a
separate training layer. On1038 unchanged targets, A208 hierarchical prediction
improves by only.00113 nats per weighted observation; A306/B305 slightly worsens.
This does not solve the maker conflict. A second pass finds no new independent
appearance or topology evidence, so propagation stops. Hypothesis labels are
never evaluation truth.

## What the period search establishes

All200 lengths200–399, including the15 multiples of13 as diagnostics, plus104
are searched on both conventions of all20 saved maps. Alternatives use the
same900 original observations; R332 additions are not invented on unreviewed
alternative maps. All185 maker-eligible lengths are retained. Full R332
leave-one-geographic-section-out fits, guarded fits, distinct-occurrence fits,
black-weight controls, reverse/origin checks and cyclic-cut controls are saved.
Forty-four cached G alternatives receive176 own-map comparisons.

| R332 predictor | Geographic log gain over color frequency | Hard agreement with original labels | Full-data known / unknown motif positions |
|---|---:|---:|---:|
| Ordinary color-frequency predictor | approximately0 | 36.3% | — |
| Lattice phase13 | .0340 | 43.0% | — |
| A104 flat | .6123 | 81.8% | 69 /35 |
| A208 flat | .5943 | 85.4% | 166 /42 |
| A208 hierarchical,104 parent | **.8073** | **91.3%** | same166 /42 consensus |
| A306 flat | .1242 | 50.2% | 44 /262;87 wholly unobserved |
| B305 flat | .1242 | 50.2% | 44 /261;86 wholly unobserved |
| B207 flat | −.0561 | 36.9% | 15 /192 |
| B299 flat | −.1354 | 32.5% | 15 /284 |

Scores are natural-log units per weighted observation(red/yellow1,black.55,
original provisional site.25), not photographic accuracy. Hierarchical208 still
gains.6957 when both adjacent sections are excluded. Distinct-occurrence flat208
gains.6032, agreement86.3%; “14 occurrences” includes incomplete boundary pieces,
not14 independently observed complete repeats. All R333 selections and these
cross-validation analyses are exploratory reuse, not a newly blinded test.

The frozen old900-observation motif confidently predicts105 of141 R332 additions
at208:98 agree and7 disagree. At104 it predicts90:83 agree and7 disagree.
R332 did not use a motif for extraction, but these are exposed-data incremental
checks, not independent certification of its additions. The conservative full
208 motif gains12 known positions relative to R331; none of its42 remaining
unknowns is automatically filled.

A306 and B305 induce **exactly the same observed partition**: all541320
observation-pair equivalence decisions agree. Their tied predictive scores are
one alias, not two independent discoveries. They correspond to a weaker
spatial displacement(24,23), unlike the strong(16,16) recurrence. Neither divides
its own N(2704/2691). A306's score varies.094–.132 with the cyclic cut; B305
.096–.131. Their small fitted agreements cannot establish a whole necklace.

For current A, the only200–399 exact divisors are208/338, both excluded by the
maker's non13 fact. Current B permits207/299, both predict poorly. Across all
saved maps, all18 maker-compatible exact-divisor fits have negative gain; the
best is saved-16-A/P302,−.0156. This rejects these saved map/period combinations,
not the maker's design or every possible lattice interpretation.

Thirty-eight stronger null trials repeat all40-map×201-period selections while
preserving either whole-section relative geometry/phase13 or phase-lane local
label ordering. Their best selected scores remain below the historical working
A104 score. A joint period-plus-spatial predictor tests incremental information:
A104/208 improve the spatial baseline, whereas every shortlisted non13 candidate
reduces its guarded predictive score. Thus the current spiral explanation does
not secretly recover305/306 as a full design.

Piecewise integer-phase inference tests sparse shifts at penalties1/3/6/12.
At the main6/12 penalties it selects no changes. The weak1 penalty proposes an
11-observation shift for306/305 but breaks nine existing boundary equations.
All shifts remain rejected diagnostic layers. Existing alternative windings and
G replays are evaluated on their own coordinates, not silently overwritten to
make the desired period fit.

**Specific missing evidence:** resolving the42 unknown208 slots would improve
that partial tile but would not satisfy the non13 fact. A maker-compatible answer
also needs a supported transverse/phase continuation that changes the current
same-phase(16,16) recurrence, or a verified coherent row/winding alternative.
The most actionable present cases are the repeated-feature interruption groups
and matching provisional bodies in the atlas. Merely choosing the plurality
color at every conflict cannot supply that evidence.

## Visualization, verification and cost

The offline viewer synchronizes the original photograph and colored lattice by
stable IDs. It supports zoom/pan/click/recenter, three direction switches,
regular/flexible traces, the repeat-supported subset, provisional markers,
uncertain continuations, separate hypothesis rings, A/B/reversal and saved-map
comparisons. Alternative maps explicitly omit R332 additions without saved
coordinates. Invalid old-direction equations are shown separately in magenta.
At every scale the observation color remains its original recorded color.

Sixteen detailed cases provide matched photograph/lattice panels, a target box,
explicit expected-versus-recorded color, one or two competing explanations and
two comparable native contexts. All markers have complete ID/coordinate keys.
Forty-eight literal RGB crops are stored separately from enlarged annotations.
Eight overlapping standalone SVG panels show the full working lattice on graph
paper, with unknown sites clearly marked. Browser desktop/narrow/offline checks
exercise both views and the real controls.

Independent code verifies2285 edge equations,106 measured paths/1123 link
incidences, all216 exhaustive staircase scores,404 full-cohort period fits,
2891 motif entries,241 translation statistics,2363 alias pairs,541320 partition
decisions, all1041 guarded predictions,19 appearance audits,128 gap records,
40 coherent patch alternatives and48 literal crops. Period-score disagreement
is at most5.6×10⁻¹⁷. All111 sealed historical input files remain exact, and a
baseline diff permits only scoped R333 files and handoffs. These are numerical
and provenance checks, not new human photographic truth.

Selected stage times after imports: flexible/spatial analysis4.56s, regular
staircase search9.39s, period analysis38.05s, diagnosis1.16s, plus the short
follow-up and6.26s final figure generation. Independent verification takes9.92s.
[Fresh replay/performance receipt](r333/performance.json) records57.73s end-to-end and a510.1MiB peak, with process wall
times and peak memory with exact parsed scientific equality, excluding only
measured seconds. Two earlier period export failures are preserved with sources:
one exposed missing unseen-residue padding, the other duplicated output metadata.
Their null work took about38s each and yielded no adopted result. The first fresh replay also exposed set-order-only differences in patch exports; sorting patch iteration fixes reproducibility without changing decisions. Its failure and costs remain archived. The initial
lattice exploration and unsuccessful controls are retained. This is a bounded
cached-data workload, not a detector speedup or convergence guarantee.

R333 stops for review after scoped commit/push and independent remote confirmation.
No final shortest repeat, physical count, winding change or correction is adopted.
No automatic R334 or model/session switch is authorized.
