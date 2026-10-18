# R323 — joint photographic tracking repairs the local row switches and expands coverage

**The frozen detector recovers all25 clearly interior R161 beads and all45
recorded interior links, with zero incorrect interior automatic links.** Both
2→3 and4→5 now have the correct d1 relation, the false4→3 neighbor link disappears,
maker10 is recovered, and11→14→16 remains correct. Across the larger photograph
crop, the result is **98 conditionally indexed observations**, including82
heuristically confident interior observations. This is useful expansion, not a
claim that all98 physical identities have independent validation.

[Original-photo review](r323/results/index.html) ·
[Clean diagonals](r323/results/diagonals-only.png) ·
[Failure comparison](r323/results/failure-comparison.png) ·
[Graph and alternatives](r323/results/graph.json) ·
[Reproduction](R323_REPRODUCE.md).

## Why R322 accepted the wrong continuations

R322 accepted two supported crossings as neighbors when they shared a smooth
phase contour. Its implied difference links then inherited the same phase
coordinates. Stable bandwidth controls and closing cycles checked that
construction, not whether the contour followed the same physical bead row.
The wrong2→3 and4→5 links passed both checks. Their neighboring red/yellow supports
were enough to suggest a different row interpretation, but R322 never compared
joint multi-bead alternatives before fixing those identities.

The new independently observable condition is **disagreement between a proposed
step and the relative two-family coordinates supported by several surrounding
observations in overlapping windows**. This uses photographically detected
supports, not R161 neighbor labels. A single good-looking curve or isolated
reflection pair cannot settle that disagreement.

For example, window6, x1110…1310, retains both the old-like delta(1,0) interpretation
and delta(1,−1) for2→3 and4→5. Both explain21 detected supports; the joint
multi-support scores are19.373 and20.094 respectively. The latter also supports11
complete local triangles rather than7. This small local preference is not treated
as decisive by itself. The selected states across windows4–8 agree on(1,−1) for
2→3; windows5–8 agree for4→5. Shared observations align these coordinate systems.

Window7 illustrates why joint inference matters: its local top score21.237
proposes(2,−1), while a competing score21.223 proposes(1,−1). The latter is selected
by overlap evidence, including18 shared observations agreeing with window6.
The detector therefore does not just replace one unconditional local winner with
another. [Every alternative, residual and window](r323/results/diagnosis.json)
is retained. A unique pigment/illumination cause of the original phase switch
is still not established.

## Method and runtime independence

The detector reads the unchanged original `beads-photo-2.jpg` and R275's measured
bright-support pixels, colors and locations. It uses89 existing supports and adds15 fresh white-reflection
components directly from RGB. No maker locations/links, R322 graph, fitted bead
positions, station groups, model visibility or3D renderer enter detector runtime.
The original photo SHA-256 is
`eb7c9edb62f5580ef56632872da48da92556d62b758295137068cc2404dc8fbb`.

1. Foreground chooses the local rope height within the requested crop
   `[900,0,1900,700]`. Twenty-three overlapping approximately200×200px windows
   advance40px. Their directions and phases are not assumed constant.
2. Up to10 distinct reciprocal spectral triangles propose local two-family bases.
   Observed neighboring supports propose additional bases within broad exploratory
   bounds. Such proposal bounds do not directly accept any reflection pair.
3. Each hypothesis simultaneously fits both integer coordinates and one local
   affine representative grid to several observations. Five robust assignment/fit
   iterations retain unique occupied sites, missing observations, and competing
   coordinates. Unobserved sites earn no reward and create no bead.
4. Six distinct hypotheses per window enter a48-path beam. Shared observed IDs
   provide integer translations between windows; disagreement about their relative
   coordinates incurs a penalty. The beam uses the previous two windows. Paths
   within3 score units remain credible alternatives; finite search is not a proof
   of the global optimum.
5. A proposed link needs at least two supporting windows and at least85% window
   agreement, foreground support, and no detected intervening observation in its
   interior corridor. Contradictory links remain unresolved. Other regions continue.
   Integer propagation rejects contradictions but is not a photographic certificate.

The5px colored and8px black bright-support sigmas are exploratory location
allowances, not calibrated center errors. All original reflections stay fixed.
Representative positions, their spread, local assignments and residuals are
exported separately. The black highlight on14 is never moved to make a line fit.
The same principle recovers the already visible reflection on10 without requiring
it to land on a Fourier crossing.

Foreground/color extraction retains R322's photograph-specific assumptions.
This is not a detector validated on other palettes or photographs. No full-body
segmentation or calibrated bead extent was recovered. Separator brightness ratios
are exported descriptively; they did not select the correct rows. No accepted
pair triggered the conservative intervening-observation veto, so this run does
not demonstrate its sensitivity to real skips. The demonstrated gain comes from
multi-observation and cross-family overlap evidence.

The developer knew the published R322 failures and inspected the requested raw
photo comparison. This is a **runtime data holdout**, not developer blindness.
The final detector, output and ablation were hashed before the single R161
scoring. No detector tuning followed that evaluation. The early single-spectral
prototype and its failure are preserved separately; no chart-assisted repair was
spliced into the final graph.

## Held-out R161 comparison

The interior partition is exactly R322's frozen25-bead/45-link partition. Maker
surface picks are associated with original observed supports, not hypothetical
centers. All40 beads and86 recorded links remain in the evaluation.

| Measurement | R322 | R323 |
| --- | ---: | ---: |
| Clear interior beads recovered | 24/25 | **25/25** |
| Correct interior recorded links | 38/45 | **45/45** |
| Incorrect interior automatic links | 3 | **0** |
| Maker10 | Unresolved | **Recovered** |
| Correct11→14→16 sequence | Yes | **Yes** |
| Complete inventory associated | 29/40 | **33/40** |
| Complete recorded links recovered | 50/86 | **65/86** |
| Recorded links assigned wrong family | 2 | **0** |
| Remaining recorded links | 34 unresolved | **21 unresolved** |

All33 associated relative lattice coordinates agree with the maker chart after
one origin alignment; there is no local relative-index drift in this checked
cohort. Among192 automatic links over the larger crop,66 agree with R161's
recorded or implied chart and126 have at least one endpoint outside its validated
association inventory. None of those126 is counted as independently correct.
Sixty-five agreeing links are explicitly recorded; one is chart-implied.

At association radii14/18/22px and margins0/3/5px, the33 associations,65 recovered
recorded links and zero wrong links are unchanged. A10px radius associates30 and
recovers54, still with zero detected wrong links. Bead10's distance is10.602px,
with7.975px margin to a rival. These proximity matches and original-photo review
remain provisional ownership evidence, not new maker confirmation.

[All associations, links and sensitivity](r323/results/validation.json) ·
[Original-photo held-out overlay](r323/results/heldout-validation.png).

## Expansion, coherence and unresolved regions

The requested700,000px rectangle is approximately5× the R322 rectangle's area.
The detected rope occupies only part of it. The98 supported anchors span approximately x932…1873, y237…439.
Reliable local fragments continue
through the larger crop even where nearby connections abstain.

| Larger-region quantity | Result |
| --- | ---: |
| Original photographic observations | 104 |
| Conditionally indexed in one component | 98 |
| Interior heuristic-confidence observations | 82 |
| Probable/edge indexed observations | 16 |
| Unresolved observations | 6 |
| Indexed red / yellow / black | 44 / 19 / 35 |
| F0 / F1 connected diagonal fragments | 25 / 23 |
| Fragments supported by overlapping windows | 48 |
| Supported conditional neighbor links | 192 |
| Unresolved candidate links | 17 |
| Row-assignment disagreements among those links | 11 |
| Sparse end-window abstentions | 6 |
| Consecutive window overlaps with complete coordinate agreement | 20/22 |
| Local winners changed by joint inference | 9 |
| Changes that alter shared relative topology | 7 |
| Algebraic cycle rank / conflicts | 95 / 0 |

All192 accepted edges have unanimous relative-coordinate votes within the retained
credible window states (the configured threshold was85%). Forty-eight fragments have multi-window support; this does not mean48 statistically
independent tracks. There are209 candidate-pair evidence checks,192 accepted and17
abstained, using four distinct checks: multi-observation joint fit, shared-observation
coordinate consistency, intervening-support screening and foreground continuity.
They reuse image data and are correlated. There are **zero independent labeled
accuracy checks outside R161**. Algebraic cycles and affine triangles are also
not extra independent photographic measurements.

The two imperfect consecutive overlaps are windows16→17 and17→18. They disagree
on2/12 and4/10 common supports respectively, in the x1510…1790 bend/appearance
region. The11 row-ambiguous connections are around x1559…1729, y235…342; their
exact endpoints and competing coordinates remain in the graph. Six end-window
abstentions lie near x1826…1882, y409…479. These are **suspected row ambiguities**,
not eleven confirmed wrong physical connections. No confirmed wrong R161 link
remains. No claim of zero errors across the unlabeled expansion is warranted.

Windows0…16 form an internally agreeing overlap chain, and18…22 form another;
the bridge between them needs review. Thus local support for a bead should not be
confused with certainty of its accumulated index across the difficult bridge.
The clearest independently checked result is33 associated relative coordinates,
including all25 interior beads. The82 interior labels describe the detector's
heuristic confidence, not82 externally proven physical indices.

[Full labeled overlay](r323/results/full-overlay.png) ·
[Indexed view](r323/results/indexed.png) ·
[Automatically selected uncertainty examples](r323/results/uncertainty.png).
Lines join measured evidence anchors and may kink at displaced highlights; they
are not claimed bead-center trajectories. The clean view omits bead indices.

## Does the larger region help?

Yes, in the limited sense tested. The same frozen candidate bank with independent
local winners produces107 accepted links and15 components under the same final
consensus rules. The joint beam yields192 links and one component, changing9
local winners and7 shared-coordinate interpretations. The numerical example above
shows a nearly tied local choice settled by surrounding observations.

This ablation isolates joint selection, not crop size: it is **not** a controlled
small-crop-versus-large-crop accuracy experiment. Overlap supports both recovery
and explicit abstention. Neither greater coverage nor a connected graph proves
that the unresolved bridge is physically correct. The early single-spectral,
60px-stride exploratory run retained71 indexed observations in8 components; it
changed more than one setting and is not a clean causal ablation.

## Indices, pattern readiness and frozen3D models

Coordinate `a` advances along F0; `b` along F1. The component origin is the
first lexicographically sorted connected observation, `C-0932-0412`.
Interpretation A is `7a+6b`, B is `6a+7b`; both negatives remain available.
Neither6/7 assignment, physical direction nor absolute string origin is resolved.

A spans0…280 with98 distinct occupied indices and183 unknown slots. B spans0…279
with98 occupied indices and182 unknown slots. These gaps are not declared absent
or hidden beads. There are no same-index duplicate observations in this run;
equal weighted indices would not automatically merge distinct planar sites.
All observations, colors, uncertainty and gaps remain available in the machine graph.

**Pattern analysis is deferred.** The unresolved bridge can change accumulated
indices across independent portions of the crop, and only33 identities have the
held-out local check. No repeat scan, color completion or pattern-based row repair
was used. The exploratory100–200 target was not forced:98 conditional sites,
82 interior, is the actual result.

**R319/R321 comparison is also deferred.** The corrected local photographic graph
is better evidence for a future frozen-model correspondence check. It does not
by itself identify a connectivity, projected-location, optical or physical-model
defect in those reconstructions. No models were read by detection, changed,
optimized or newly rendered. Useful expansion and validation took priority.

## Measured performance and verification

One numerical thread, existing `.venv`, native original photograph; imports,
review rendering and documentation excluded from these detector stages.

| Stage | Seconds |
| --- | ---: |
| Image preprocessing | 0.196 |
| Photographic support extraction | 1.014 |
| Local spectral analysis | 1.185 |
| Joint two-family candidate generation | 2.245 |
| Beam selection | 0.206 |
| Candidate pair votes | 0.009 |
| Row/skip/foreground photographic checks | 3.255 |
| Supported intersections, indexing and fragments | 0.003 |
| Graph validation and coordinate propagation | 0.002 |
| **Detector stage sum** | **8.113** |
| Pattern / frozen3D analysis | Not run |

The simple per-pair scan of all observations and photographic sampling is the
largest stage; local candidate fitting is second. R322's0.841s was for a smaller,
different task. No equal-task speedup or3D rendering comparison is claimed.
Guarded exact replay takes9.214s including output serialization on this machine.

Independent formulas check104 supports/2360 original native pixels, all138 saved
local hypotheses and their predictions/scores, all48 beam paths, every accepted
edge's votes/skip test/coordinates, both index interpretations and reversals,
and R161 arithmetic reconstructed from its raw series. Exact guarded replay
reads only the photo, appearance catalog and the two tracker source files; it
reproduces every scientific output, excluding timestamps/timers. A translated
coordinate fixture preserves identity; a one-row perturbation is detected. The
42-step equal-index fixture preserves distinct planar locations.

[Verification receipt](r323/results/verification.json) ·
[Prevalidation freeze](r323/results/freeze.json) ·
[Joint-selection ablation](r323/results/controls.json) ·
[Browser checks](r323/results/browser-check.json) ·
[Delivery receipt](r323/results/delivery.json).

The first development run failed only on NumPy-integer JSON serialization; its
source and failure note remain archived. Original photo, R161, R322 and older
scientific evidence are preserved;1,565 protected tracked files match their original
Git blobs ([preservation receipt](r323/results/preservation.json)). Desktop, narrow
and offline review checks pass. Scientific work started15:20:54UTC and was
sealed15:32:40UTC on2026-10-18, ahead of the15:44:54 scientific cutoff and15:50:54
delivery deadline. The remaining work is verification/documentation/delivery.

**STOP for scientific review.** Next, only if authorized: inspect the automatically
selected x1559…1729 competing continuations and the two conflicting overlaps before
using indices across that bridge for a repeat or frozen-model comparison. Keep
the user's preferred Astra/High/current session for review; no `/new` is needed.
No automatic R324, pattern adoption or new3D optimization.
