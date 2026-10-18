# R325 — cyclic global inference, faster execution, unresolved photographic truth

**R325 produces one conditional global candidate component, but does not establish one correct whole-bracelet reconstruction.** All 187 windows participate in a cyclic optimization before any links are accepted. The result indexes 895 of 937 photographic supports and proposes 1,826 links. A subsequent changed-window photographic stress test contests 174 of those links; excluding them leaves **23 components** for conservative downstream use. Neither the connected candidate graph nor its closing algebraic cycles certifies the photograph.

The final full pass takes **15.067 seconds before serialization, 15.565 seconds including serialization**, with **1,000.2 MiB peak RSS**. This is 2.36× faster than R324's reported 35.570-second detector stages while doing additional global and colored-first inference. The original R324 candidate topologies are preserved. R161 remains **25/25 interior associations, 45/45 interior links, zero wrong interior links**, and **33/40 associations, 65/86 recorded links overall**.

[Original-photograph review](r325/results/index.html) · [Reproduce](R325_REPRODUCE.md) · [Graph](r325/results/graph.json) · [Context disagreements](r325/results/context-check.json) · [Model interface](r325/results/model-input.json) · [Verification](r325/results/verification.json).

## 1–2. Why R324 fragmented

R324 imposed geographical chart ownership **after** a serial beam search. A candidate edge needed matching owner charts even when its source pixels, overlap votes and intervening-support checks otherwise passed. Its 48-history beam used two preceding windows, discarded earlier alternatives permanently, and did not include the last-to-first factors in the search. A single nonunanimous transition incremented the chart number, affecting other nearby edges regardless of their own evidence.

Among 140 unresolved candidates, reasons overlap:

| R324 rejection reason | Links |
| --- | ---: |
| Chart boundary | 70 |
| Competing row assignments | 55 |
| Fewer than two supporting windows | 26 |
| Possible intervening observed bead | 6 |
| **Chart boundary alone** | **56** |

Removing only that gate, with the same old beam choices and a simultaneous integer audit, changes 25 components to six, with 1,778 accepted conditional links. This demonstrates substantial **program-induced fragmentation**, not that all newly connected rows are physically correct. R325 accepts 53 of the 56 chart-only rejected links under its own global choices.

The finite local proposal bank also matters. Exact cyclic selection on the original bank yields five components, 890 indexed supports and 1,776 links. Colored initialization and bidirectional candidate reuse yield the delivered one-component candidate. Window 129, which previously had no fit, gains candidates from shared observations on both sides. No geographical seam is declared there.

The saved D6 triangular-lattice transformations do not improve the best shared-coordinate agreement at any of R324's 19 broken transitions. Thus these archived failures are not explained by a simple missed family swap or reversal alone. Several contexts assign particular observations to different rows; some have insufficient supports. New candidates and global selection reconsider those assignments. Outside R161, we cannot designate one local hypothesis as photographically wrong merely because it loses the global objective. The later multiscale disagreements demonstrate that genuine unresolved evidence remains.

All causes are distinct: chart ownership is an artificial barrier; the beam limits reconsideration; top-six retention prunes alternatives before global selection; overlap disagreement can reflect wrong rows, incompatible integer translations, or weak local affine approximation at bends. The available evidence does not uniquely separate those last physical/image causes for every observation.

## 3–4. Mathematical structure and whole-circuit participation

Three approaches were considered: a sparse mixed-integer factor problem, loopy message passing, and cyclic dynamic programming. The small retained state sets favor the last. R325 retains the original six candidates per successful window plus up to four distinct colored/bidirectional proposals. There are **1,603 hypotheses and 26,731 supported assignments** across all 187 windows. Local fits are proposals, never finalized charts.

For window state variables \(h_i\), the maximized finite objective is

\[
\sum_i U_i(h_i)+\sum_i[P(h_i,h_{i+1})+P(h_i,h_{i+2})]
+\sum_i T(h_i,h_{i+1},h_{i+2}),
\]

with every subscript cyclic. Unary scores use observed support residuals and local triangles. Pair factors compare common observed identities after the modal integer translation: `0.35 × agreeing − 2.5 × disagreeing`, with no factor below four shared observations. Triple factors penalize incompatible composition of the three modal translations by `2.5 × min(L1 residual, 4)`.

The first two states are exhaustively conditioned. Forward/backward max-sum over two-state memory includes **all three wraparound pair factors and both wraparound triple factors** before selecting the optimum. Exact max marginals retain every state within three score units of the best complete path. This avoids copying beam histories. Exactness applies to this finite candidate objective, not to all possible bead lattices or all long-range photographic factors. Longer-range consistency is checked by the resulting shared-observation graph.

Candidate edges need two windows, at least 85% window consensus, no intervening support in the recorded corridor, and foreground fraction above 0.95. Alternative window states contribute conservatively; a window containing a rival delta counts as disagreement. There is no chart membership test.

A separate **simultaneous sparse weighted L1 coordinate synchronization** checks all proposed edges using

\[
x_t-x_s+w_{st}H=d_{st}.
\]

Here \(x\) is an integer coordinate, \(w\) is geographical wrap across an arbitrary cut, and \(H\) is a free two-component holonomy. Integrality is explicitly checked, with an integer-program fallback available; this run's linear solutions were integral and had zero residual. No greedy edge insertion determines the final map. A separate symbolic traversal checks whether the evidence actually identifies \(H\). The optimizer's arbitrary unidentifiable value is exported only as a numerical gauge, never a bead count.

Both maps `A=7a+6b`, `B=6a+7b`, and both reversals survive. Equal weighted index identities such as 42 do not justify merging different planar sites. The algorithm does not force \(H=0\).

Changing the cyclic search origin by **37, 93 and 151 windows** preserves every selected alternative; max-marginal differences are below \(2.1\times10^{-12}\). This changes traversal origin on the same measurement bank, not window placement. The full ring constrains the first states mathematically. **In this photograph, removing the wrap factors changes neither the best path nor retained alternatives.** Therefore the improvement cannot be attributed to newly demonstrated long-distance closure information. The seam-free search and reconsideration mechanism work, but the end of this particular circuit does not resolve the remaining uncertain closure.

## 5. Colored-first geometry and black observations

The detector reads only the original RGB, R275 appearance supports/colors, and the existing photographic spline for geography. No maker chart, model indices, rendered positions or 3D predictions enter inference.

Additional affine candidates are first fitted using red/yellow supports only. Unoccupied lattice sites with at least two noncollinear colored neighbors predict black neighborhoods **before black supports participate in that fit**. Existing independently measured black supports are sought within 12 pixels; their locations do not set the colored-only grid. All colors then jointly refine the same affine basis and orientation. Black bright-support sigma is eight pixels versus five for colored supports; this is localization uncertainty, not a smaller black bead or separate orientation/shape law.

Across multiple overlapping windows, **156 indexed black supports** receive colored-only predictions; **one was unindexed in R324**. These are 156 geometric corroborations, not 156 newly discovered beads. The native search also finds **three faint-reflection detection records at two unique sites (40 unique original pixels; 62 pixel entries including repetition)**, not already associated with a measured observation. They remain unconfirmed body identities and do not inflate the 937-observation count. Darkness or an expected empty site alone never creates a confirmed bead. Some expected positions lie in poorly modeled/background neighborhoods; the review makes those failures visible.

Colored-only predictions, anchor assignments, native faint pixels, competing hypotheses and joint refinements are exported. Neighbor reuse is bidirectional and operates on candidate banks, including through difficult regions, rather than accepting the previous window as truth. This is one bounded augmentation/refinement pass, not a claim of convergence of unlimited alternating recovery.

## 6. Purposeful 146-support practice

The lower bend spans windows 65–93, contains 43 red, 56 yellow and 47 black observations, and includes several old ambiguous continuations. It excludes the R161 development geography. The initial solver test preceded the whole-circuit implementation. Later fresh measurements reran the same problem to isolate engineering changes.

| Practice run | Indexed | Accepted / unresolved links | Components | Total seconds | Peak MiB |
| --- | ---: | ---: | ---: | ---: | ---: |
| Current R324, fresh spectra/fits | 129 | 235 / 57 | 6 | 9.134 | 1,167.2 |
| Exact engineering optimization, same R324 inference | 129 | 235 / 57 | 6 | 4.982 | 1,018.3 |
| Global method with additional candidates | 134 | 261 / 33 | 2 | 5.629 | 1,019.2 |

All include full-photo preprocessing/support extraction, then measurements in the selected region; they do not falsely charge that startup to only a small cropped image. Candidate generation alone changes **3.837→0.792 seconds**. The first same-bank global solver test had 130 indexed supports, 240 links and three components; augmentation adds further coverage. There are zero internal integer conflicts in these runs. The optimized R324 edge lists, unresolved lists and coordinates are exactly equal to the reference run.

**No independent accuracy denominator exists for this 146-support region.** Counts describe coverage and consistency. Its changed-window stress results, including the remaining lower-bend winding gap, prevent advertising it as a verified reconstruction.

## 7–9. Full result, uncertainty and historical reference

| Quantity | R324 | R325 global candidate |
| --- | ---: | ---: |
| Photographic supports | 937 | 937 |
| Conditionally indexed | 886 | 895 |
| Interior / edge indexed | 763 / 123 | 770 / 125 |
| Unresolved observations | 51 | 42 |
| Accepted conditional links | 1,722 | 1,826 |
| Unresolved candidate links | 140 | 45 |
| Candidate components | 25 | 1 |
| Nonunanimous/insufficient adjacent transitions | 19 | 14 |
| Algebraic cycle rank | 861 | 932 |
| Certified whole-circuit families | 0 | 0 |

Both family orientations are represented around the bracelet, with **204 F0 and 214 F1 visible fragments**. These are finite visible row fragments, not 418 separately inferred geographical charts. Both families lack certified full-circuit continuation. The 932 cycles check algebra, not photographic truth.

There are 115 added links and 11 removed R324 links. All 19 previously broken geographical cuts now have conditional crossing links; 11 have unanimous adjacent overlap, eight retain competing assignments. Five additional nonunanimous transitions appear elsewhere. The review shows all 19 cuts and their exact evidence; a crossing edge does not prove every row at that cut.

A **63-window post-freeze stress test**, using 160/240/280-pixel contexts at the old breaks, upper contested bridge and winding gap, evaluates 513 accepted links. Of these, **132 are consistent in every tested context, 207 have local alternatives, and 174 are excluded by at least one context's leading hypotheses**. These reuse the original pixels and are not independent labels; a locally preferred alternative can be wrong too. Nevertheless they are real counterevidence, not erased because the global graph is connected.

The conservative model-use interface excludes those 174 links, leaving **1,652 links, 867 connected observations, 70 unresolved observations and 23 components**. An additional 207 tested links remain context-ambiguous, and 1,313 accepted links were not covered by this stress test. Consequently **895 is not a count of reliably established global identities**. The screened graph is a downstream sensitivity mask, not a second fitted solution or a new chart-splicing algorithm.

R161 is scored only after the initial global result is frozen. Its 25 interior observations and 45 recorded interior links all survive, with no wrong interior automatic edges. All 33 associated maker coordinates agree after one origin alignment. Seven reference beads and 21 recorded links remain unresolved, unchanged from R324; the full lists and proximity sensitivity are exported. The conservative context-screened export also retains all 65 previously recovered reference links and all 33 associated observations. These are historical checks with known development history, not a new independent holdout. No additional outside-reference photographic accuracy is claimed.

## 8. Closure and possible counts

The accepted candidate graph is a long connected **open lift**: it contains no nonzero geographical winding cycle. Four unresolved lower-bend edges near `(1485,3010)` would close that gap. Their dominant continuations imply \(H=(214,201)\), giving **A=2704 or B=2691**. Including competing deltas gives conditional A counts **2697/2704/2710** and B counts **2685/2691/2698**. None is accepted as N. Modular distinct-support collisions are exported separately; they can indicate wrong topology or duplicate bead observations and are not silently repaired.

The current open A/B maps span 2,703/2,692 addresses and have no duplicate unwrapped indices. Counts 2800 and 3000 accommodate those spans, but this is only a weak necessary check. The unresolved closure proposals do not match those frozen counts. They remain conditional on many unverified intervening rows, so they do not independently disprove either physical model.

## 10–11. Measured performance

| Final stage | Seconds |
| --- | ---: |
| Decode and preprocessing | 1.656 |
| Native support extraction | 1.881 |
| Spectral measurements | 3.166 |
| Original-bank hypothesis generation | 4.299 |
| Colored and bidirectional proposals | 2.807 |
| Native black-neighborhood inspection | 0.389 |
| Exact cyclic optimization | 0.277 |
| Graph evidence and simultaneous coordinate audit | 0.392 |
| All detector work before serialization | **15.067** |
| Serialization | 0.494 |
| Including output bookkeeping | **15.565** |

These are one-process wall timings, not parallel speedup. Tiny guide/setup/output bookkeeping explains the difference between listed stage sums and elapsed totals. Imports, post-freeze stress tests, documentation, browser rendering and independent verification are outside the detector timer. A second optimized full pass took 15.450 seconds before serialization; the initial unoptimized R325 pass took 20.701 seconds. The independent read-guarded complete replays took 16.842 and 18.143 seconds including process/output overhead. These are measured samples, not a convergence or throughput guarantee.

Three bottlenecks were removed:

* Batch the same tiny affine systems and collision masks rather than repeatedly dispatching scalar Python/NumPy operations. All **1,115 original R324 retained hypotheses / 18,746 assignments** preserve topology, with maximum predicted-location difference **2.51×10⁻¹² pixels**. The profiled timing was diagnostic; the unprofiled practice timing above is the performance control.
* Restrict nonmaximum suppression to the identical nonzero Fourier annulus plus a zero halo, retaining the original FFT. All 187 spectral outputs are **exactly equal**. A paired control measures 6.784→3.047 seconds for this operation.
* Apply the monotonic sRGB transfer after taking the minimum channel, avoiding a full three-channel linear-image allocation that would immediately be reduced. Native observation pixels and centroids are exact. Peak whole-pass RSS changes approximately 1,149→1,000 MiB.

The initial and optimized R325 graph, alternatives and colored predictions agree exactly apart from timing/source metadata. The last pass adds explicit colored-anchor audit fields without changing decisions. No GPU or major dependency was introduced. Candidate work is now roughly seven seconds including new proposals; preprocessing and retained 1024² FFTs are other remaining costs.

## 12. Physical-model interface and frozen comparison

`model-input.json` supplies original support IDs/pixels, observed color cues, locations, both index maps/reversals, alternatives, diagonal steps and unresolved regions. Its **default accepted constraints exclude context-contested links and use separate component gauges**. The connected global candidate coordinates remain explicitly named diagnostic alternatives, not fixed photographic labels. Untested/context-ambiguous links still require review.

The frozen R321 N3000 and N2800 native first-hit ownership ledgers were reused with source hashes; no renderer or model prediction changes the photographic inference. A comparison using **one global origin** over all 895 candidate observations exposes failures that independent R324 component gauges could absorb:

| Frozen model | Best global interpretation | Mean assigned support | Modal neighbor agree / disagree / unresolved |
| --- | --- | ---: | ---: |
| N3000 | A | 4.60% | 1,240 / 303 / 283 |
| N2800 | B | 7.82% | 1,110 / 385 / 331 |

Only 42/63 observations respectively have reliable modal owners exactly matching the best global index. Under the reference-aligned versions of those interpretations, the first mismatches are N3000 `K-1429-0302` (expected −19, modal owner −25, 75% support) and N2800 `C-1391-0312` (expected −33, modal owner −34, 85.7% support). All 16 regional drift summaries are exported. These poor global values differ from R324's strong **local seed** support fractions; they are not the same statistic. Error versus absolute guide curvature has descriptive Spearman values −0.372/−0.334 under these selected global gauges. Neither this association nor the mismatch identifies a causal curvature or shape defect: photo topology, count, placement and correspondence remain coupled.

This interface supplies useful falsifiable constraints and explicit abstentions. It does **not** justify expensive coupled fitting yet. No 3D optimization, physical reconstruction or `beads.pov` change was undertaken.

## 13. Repeating color pattern

An exact compatibility scan tests periods 1–500 under both maps and reversals, retaining conflict witnesses and the historical nonmultiple-of-13 maker constraint. Every tested period has at least one conflict under the complete conditional map; this does not establish that the true repeat exceeds 500. This is conditional on the global candidate indices and observed color cues; no hidden colors are completed. A false link or color can reject a true repeat. Global indexing remains contested, so the scan is a constraint ledger, not a recovered or adopted pattern.

## 14. What remains unresolved and delivery

The main unresolved issue is **photographic row identity**, especially changed-context disagreements at bends and the four lower-bend closure links. A connected candidate and unique arithmetic indices are insufficient. The next review should inspect the pink contested links in the original-photo viewer, especially the upper bridge, inward bend and `(1485,3010)` winding gap. The finite candidate bank, local affine approximation, support-versus-center distinction and uncalibrated consensus margins remain limitations.

Independent checks cover all 937 supports / 21,181 original pixels, all 1,603 hypotheses / 26,731 assignments, all 1,826 accepted candidate edges, 1,367 colored-first predictions, native faint candidates, both index maps, cyclic origin changes and a read-guarded exact full replay. Small exhaustive fixtures verify cyclic max marginals, a closing factor that actually changes an early choice, nonzero holonomy and unidentifiable open arcs. Additional checks cover multiscale contexts, closure proposals, conservative export and frozen-model arithmetic. Browser review checks all 19 transition selections, raw/overlay switching, native crops, desktop, narrow layout and offline use. An initial local-file canvas security failure was repaired by embedding the unchanged original JPEG bytes; failed logs are retained.

Scientific inference and context testing were sealed at **19:31:55 UTC on October 18**, before the 19:42:35 cutoff and leaving more than eight minutes for verification/documentation/delivery. Original photograph, maker annotations, earlier reports/results and `beads.pov` are preserved. Delivery receipt records the scientific commit and independently checked remote branch.

**STOP for review. No R326, pattern adoption or automatic fitting.** Keep the user-preferred Astra/High/current session; no `/new` is needed.
