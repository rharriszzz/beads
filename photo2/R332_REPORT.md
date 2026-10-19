# R332 — 141 more indexed observations and 423 more working links

**The additive reconstruction now has 1,041 indexed observations and 2,285
working links, versus900/1,862.** It preserves every original observation,
coordinate and link. The active inventory gains126 native-supported observations:
57 red,37 yellow and32 black. Fifteen previously recorded observations gain
coordinates, including all four previously unindexed black records. Sixty-five
additional black candidate groups remain explicitly provisional and visible.

[Offline interactive viewer](r332/review/index.html) ·
[Complete before/after tiles](r332/review/index.html#tiles) ·
[Counts](r332/results/summary.json) · [Reproduction](R332_REPRODUCE.md) ·
[Independent checks](r332/verification.json).

These are working photographic additions submitted for review, not a certified
complete census of physical beads. No repeating-pattern search, physical-model
fit, renderer or winding search was used. The baseline is R331 commit `4b6c9a2`.
The user's positive review supports the particular displayed R331 labels/links;
it does not certify unreviewed assignments. Those working assignments are retained.

## What was missing from the illustration

R331 deliberately selected small ID lists and drew coordinate neighbors in only
two families. The complete baseline already contained938 recorded observations,
900 indexed observations and1862 working links, including485 third-family links.
All938 records, including38 unindexed records and the original provisional black
site, are now visible. Actual working edges and coordinate-only relationships
are separate viewer layers.

| Exact R331 named context | Labels shown / already recorded there | Working links shown / already present there |
|---|---:|---:|
| G | 13 /25 | 17 /48 |
| F | 8 /29 | 5 /58 |
| Inward | 10 /18 | 12 /34 |
| Black-direction example | 9 /18 | 11 /33 |

Thus12–21 already recorded labels and22–53 already accepted links per displayed
context were absent from those illustrations. These contexts overlap, so their
counts must not be summed as distinct discoveries. All drawn coordinate-neighbor
relationships in those four working panels were actual working edges. The audit
distinguishes omissions from wrongly displayed links; none of these counts is a
new bead or new scientific link.

Only **six** neighboring endpoint pairs implied by the baseline coordinates lacked
a working edge. One now passes the original native link tests; five remain
blocked/ambiguous. Separately, the retained connected-patch bank contains2385
absent endpoint-pair/direction hypotheses:2318 competing local row/directions,
66 with an unindexed endpoint and one coordinate-compatible unselected neighbor.
These native-tested local alternatives are retained in their own machine-readable
ledger and optional viewer layer. They are not pooled into the working graph or
counted as correct links merely because a local hypothesis proposed them.

## Actual reconstruction gains

| Quantity | Baseline | Final / addition |
|---|---:|---:|
| Active recorded observations | 938 | 1064, +126 |
| Indexed observations | 900 | 1041, +141 |
| Previously recorded observations newly indexed | — | 15: 11 yellow,4 black |
| New inventory observations | — | 57 red,37 yellow,32 black |
| Indexed red / yellow / black | 321 /269 /310 | 378 /317 /346 |
| Accepted working F0 links | 693 | 835, +142 |
| Accepted working F1 links | 684 | 824, +140 |
| Accepted working difference links | 485 | 626, +141 |
| All accepted working links | 1862 | 2285, +423 |
| Added links between original inventory observations | — | 43 |
| Added links involving new inventory observations | — | 380 |
| Original records still unindexed | 38 | 23 |
| Additional provisional observation groups | — | 263, including65 black |
| Known unindexed records with provisional coordinate proposals | — | 10, already among the23 |
| Other unassociated native candidate groups | — | 273 |
| Purely geometric vacancy predictions | — | 227, not observations |
| Current neighboring pairs without an accepted link | 6 | 5 |

The273 provisional proposal groups comprise263 additional groups plus10 known
unindexed records; they are not273 extra accepted beads. The original faint
provisional black observation also keeps its original status. All314 original
black records now have working coordinates, including that original provisional
site; this does not mean every visible black body has been recovered.

**Detection provenance matters.** Of126 observations new to the current inventory,
122 are recovered or conservatively associated with earlier retained detector
evidence. Four are fresh native-material extractions without a nearby retained
candidate point or overlapping retained support pixels:2 red,1 yellow,1 black.
The latter is a strict cache-comparison definition, not proof that no historical
experiment ever recorded any peak on those physical bodies. Native remeasurement
can rediscover an old candidate; it is not credited as a new detection simply
because its support centroid differs. The graph stores nearest cached candidates
and every overlapping cached support used in this accounting.

## Implemented procedure

The program starts from the immutable R328 coordinates/edges and reads the
R266 strict straight-growth selected12/selected6 supports and R275 inventory and
band-edge candidates. This supplies2603 cached candidates without rerunning a
detector. R325's old observation adapter read only R275's810 retained bright
supports and supplemental bright components; it deliberately omitted the broader
R266 candidate bank, uncertain body evidence and out-of-band candidates. Earlier
window clearance and connected-parent selection also left38 known records without
coordinates. These restrictions explain specific omissions without assuming a
physical bead was missing.

Each pass:

1. Fit a robust local curved coordinate-to-support map to nearby fixed working
   observations, excluding the target. Lift neighbors consistently across the
   existing H seam. For black targets, also compare a colored-only prediction
   where enough colored anchors exist.
2. Associate a cached candidate with an unoccupied lattice site only when the
   nearest assignment is distinct, the residual is bounded, two native-supported
   direction families agree and a shared-neighbor triangle is already supported.
3. Inspect actual connected native red/yellow/dark-material pixels, not just a
   predicted location. Learn appearance from existing observations at radii8/12/16;
   unstable new color readings remain provisional. Re-anchor an off-material cached
   peak to a measured material representative when supported, retaining its original
   source location. The representative is not a physical bead center.
4. Apply the original31-sample foreground and intervening-observation gates to
   proposed links. Reject additions that would contradict an original working
   link corridor. There is no two-window admission requirement or artificial
   geographic boundary. Geometry alone never establishes a new body or link.
5. Search vacancies predicted by multiple neighbors for additional native body
   evidence, then use accepted additions in the next pass. New provisional observations
   never become anchors or occupy an accepted site.

The selected passes add127,13,1, then0 assignments. Growth stops there.
The final all-observation integrity screen retains all141 additions and423 new
links: no duplicate lattice occupancy, disconnected addition, intervening-support
conflict or original-edge withdrawal remains. H=(214,201) and all original
relative coordinates remain fixed; this round makes no new physical-count claim.

The original R328 graph and all alternate histories remain separate reproducible
inputs. The small returned set of locally compatible cached hypotheses is positive
evidence for association, not permission to overwrite another working row.

## Black beads: actual recovery beyond a strong-reflection rule

Black candidates use the same local lattice geometry as colored candidates,
including colored-only predictions and multiple neighboring families. Native
dark-material pixels, component extent, local boundary/texture sectors and
foreground evidence accompany the assignment. Dark material without enough
independent geometric/body evidence remains provisional; a dark patch alone
does not establish a black bead.

The32 new accepted black observations include7 native-body recoveries evaluated
without a highlight threshold. Cached weak candidates are also eligible: for
REC266-P050477, REC266-P038462 and REC266-P045647, the maximum encoded channel
value in the inspected native radius12 context is only.235/.290/.200. A strong
isolated specular reflection is plainly not an admission requirement in these
examples. The `black-dim-left` tile shows these weak candidates with neighboring
colored bodies and all three direction families.

The viewer supplies same-family colored reference links for new black candidates,
native dark-material pixels on selection, and the distinct geometric prediction.
The `new-black-body` tile shows a native dark-body recovery among colored neighbors.
Black support/reflection coordinates are never reported as measured physical
centers; partial material spans are not claimed complete bead dimensions.

The65 provisional black groups stay visible by default. Their ambiguity can concern
color, native material extent, competing sites or continuation evidence. They are
not silently discarded for lacking a bright reflection and do not propagate
unchecked around the circuit.

## Complete and readable review

The offline viewer loads the original2540×3182 photograph and provides pan, zoom,
native1:1, stable-ID selection/recentering and clickable observation information.
Separate switches control three directions; original/new accepted links;
coordinate-only neighbors; cached competing row links; historical-reference,
working, provisional, unindexed, unassociated-candidate and pure-prediction markers.
Historical reference is explicitly distinguished from newly confirmed truth.

At broad zoom markers replace overlapping full-ID labels. Magnification enables
numbered or full-ID labels. Eleven complete static before/after contexts have
numbered observation keys/CSVs for every marker. Before images show **all** baseline
observations and all actual working links, rather than repeating R331's selection.
Amber squares in G/F/inward identify indexed baseline records omitted from that
R331 panel; cyan rings identify new accepted observations; magenta triangles mark
provisional candidates. Both panels use identical original pixels and label numbers.

The named contexts are G, F/upper, upper bend, inward bend, H/lower, lower bridge,
left black, outer black, lower-left, dim-left black and a new dark-body context.
[Regional counts](r332/review/regional-counts.json) give accepted additions,
known unindexed records, provisional and unassociated candidates separately for
each. They count inspected proposals, not all physically visible beads. A region
can gain substantial display completeness while gaining few new detections;
H/lower is one such example. No percentage of all physical beads recovered is
claimed because no justified whole-physical-bead denominator exists.

## Failures, correctness and independent checks

The initial threshold-color run is preserved and rejected as the final result:
it mislabeled some shaded yellow material as red. Multi-scale learned appearance
and deferral improve this. A second epoch, expanded-cache epoch and final native
location epoch remain preserved, with source snapshots. Final inspection also
found cached peak representatives just off their supporting material; the final
run retests those at measured native representatives, yielding fewer but better
located additions and **more black recoveries** than the preceding epoch.

The earlier expanded-cache epoch's larger1067/2359 total is not the delivered
graph. Counts from that stage must not be mixed with final1041/2285.
The final source/proposal ledger retains unsuccessful and competing proposals.
Fifteen additional provisional aliases were removed from the extra-candidate
display because they coincide with occupied sites/nearby records; their evidence
and reasons remain. Many other cache candidates are rejected or deferred for
occupied sites, weak native support, unstable color or original-link interference.
These are proposal decisions, not independently confirmed counts of false
physical beads or proven duplicates.

Retrospective coordinate exclusion recovers the correct site for113/113 sampled
baseline observations:40 black,37 red,36 yellow. This measures consistency with
the exposed working lattice, not new photographic truth. The frozen R161 regression
remains33/40 associated observations,25/25 interior;65/86 recorded links,45/45
interior;zero wrong links on those fixed associations. It is not a new blind test.

After freezing the final graph, extending the same radius18/margin3 proximity
evaluation to the enlarged inventory gives **36/40 associations and74/86 recorded
links, with zero wrong links** on associated endpoints. The three added associations
are maker28→REC266-P015647,29→R332-R-0004-0003 and35→REC266-P014934. This adds three
historically labeled observations and nine recorded-link recoveries while retaining
the old regression. The maker's arbitrary surface picks and proximity association
remain conditional; these already exposed labels were not read by recovery and
do not constitute a fresh blind photographic test. [Full post-freeze ledger](r332/results/extended-reference.json).

Independent code checks all900 original coordinates,938 original observations,
1862 original links,1041 distinct occupied sites modulo H,2285 integer edge
equations and final native corridors, every new target-excluded regression,
38368 native material pixels for141 additions, connectedness and11 literal crops.
These checks reproduce numerical/photo provenance; they do not independently
certify every new body identity. Browser checks exercise the actual viewer and
its filters, pan/zoom, recentering, pixel overlays, desktop/narrow/offline operation.

Selected recovery takes71.5s; the three preserved earlier epochs take14.2/45.5/68.9s,
about200.2s total cached recovery work. Finalization and verification are separately
timed in their receipts. There is no expensive search bank, motif scan or physical
render hidden in these costs.

**Stopping point:** review the new observations and links in the complete viewer,
especially dim-left black and the65 provisional black groups. The next useful
work, after review, is to resolve the specific provisional groups that the expanded
native contexts make visually identifiable. R332 stops here; no automatic R333
or model/session switch. Delivery records the scoped commit and remote confirmation.
