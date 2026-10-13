# R273 — reflection ownership and broader photographic interiors

**524 retained proposals: 201 black, 116 red, 207 yellow.**
All 323 retained colored masks are larger than their R272 counterparts;
median paired area increases **3.66×**. Median colored area is
516 native pixels; the paired perimeter/√area metric decreases
22.5%. Six weaker black reflections are suppressed.
These are image-derived proposals, not a verified physical-bead census.

[Simple viewer](interior_inventory_r273/index.html) · [whole photograph](review/r273/whole-photo.png) ·
[exact inventory](review/r273/inventory.json) · [reproduction and evidence](review/r273/README.md).

## The premature stopping was a method defect

The user is correct: the old computed masks were **not** the limit of photographic
support. R272's bright-level/straight-path restrictions produced undersized, ragged
regions. Early R273 controls exposed a second defect: growth escaping in one direction
caused a higher brightness cutoff everywhere. In R00956's middle yellow proposal,
the 15% and 25% cutoffs reached the context boundary; a 35% retry reduced the region
to353pixels, cutting away visibly darker interior in otherwise safe directions.
R01284's central yellow similarly retried at25%, retaining335pixels.

The delivered method removes that global brightening fallback. It traces each direction
through native pixels toward dark/color boundaries and backs up to the trough before
a neighboring rise. It permits darker interior without assuming that every boundary
is confidently recoverable. Failed growth remains a **method/ownership uncertainty**,
not a claim that the photograph contains no supporting evidence.

[**R00956: original / R272 / new**](review/r273/R00956.png) ·
[**R01284: original / R272 / new**](review/r273/R01284.png) ·
[red median example](review/r273/red-median.png).

| Automatic location ID | R272 pixels | Delivered pixels |
|---|---:|---:|
| C-2284-1877 | 222 | 544 |
| C-2267-1898 | 269 | 570 |
| C-0978-2667 | 153 | 555 |
| C-0969-2696 | 111 | 505 |

The R01284 shadowed neighbor is automatically excluded: its attempted growth remains
open/oversized and irregular. No reviewed coordinate or assigned bead identity enters
the algorithm. The lower R00956 yellow location absent from R272 is not recovered by
this refinement; all original R272 location exclusions remain available.

## Alternatives tested on the whole photograph

Same869 automatically recomputed R272 proposals, same ICC photo and background model,
same black competition, exact870-pixel ceiling and ownership checks. No expected count
or geographic quotas. Different retained subsets mean median ratios alone cannot rank
methods; inspect the paired photographs and per-ID CSV.

| Colored construction | Retained red / yellow | Median colored pixels | Paired area ratio |
|---|---:|---:|---:|
| connected | 202 / 278 | 303 | 2.34× |
| star-color | 209 / 280 | 311 | 2.48× |
| star-valley | 207 / 210 | 363 | 3.20× |
| lower-floor | 148 / 208 | 336 | 2.49× |
| wider-color | 152 / 207 | 307 | 2.31× |
| shallow-valleys | 167 / 252 | 288 | 2.16× |
| dark-envelope | 169 / 275 | 257 | 2.06× |
| relative-valley | 78 / 144 | 616.5 | 4.30× |
| relative-valley-wide | 54 / 131 | 621 | 4.12× |
| first-valley | 162 / 264 | 378.5 | 2.49× |
| relative-valley-inset | 88 / 181 | 597 | 4.04× |
| relative-valley-safe | 79 / 189 | 526 | 3.49× |
| remedy-shape | 116 / 207 | 516 | 3.66× |
| remedy-background | 81 / 189 | 525.5 | 3.49× |
| remedy-combined | 120 / 207 | 516 | 3.66× |

Connected growth and star-color admit brighter fallback cutoffs when a component leaks.
The old star-valley stops after a rise of8% of the original peak; it can retain a tail
past a dark trough. Lower-floor, wider-color, shallow-valleys and dark-envelope isolate
threshold relaxations. First-valley backs up to a trough but retains global retries.
Relative-valley removes those retries and measures a rise relative to the trough.
The wide control uses50% rather than25% recovery. Inset backs off one native step from
the detected trough; **remedy-shape** additionally uses a two-step inward cleanup to
account for the 3×3 valley measurement at mixed boundary pixels. All alternatives,
including failures, survive in compressed records and photographic comparisons.

## Red losses investigated and a remedy implemented

The pre-remedy inventory retained only79of363red proposals.114failed only the
0.88solidity gate;159failed the open/size gate, often together with shape. Inspection
found both plausible near-threshold interiors and real growth defects. The user asked
for remedies to be implemented now, rather than left as proposals.

**Selected: lower the uniform solidity minimum to0.84**, preserving every photographic,
size and ownership check. Red acceptance becomes116(net+37), yellow207(net+18), black201.
The rechecked ownership conflicts remove3old red and1old yellow regions, rather than
silently accepting all additions. A separately tested uncertain-background continuation
adds little and leaves ambiguous photographic cases; it is implemented as an optional
control but **not enabled in the delivered inventory**.

[Full diagnosis, implemented comparisons and remaining remedies](RED_LOSSES_R273.md) ·
[red additions](review/r273/red-remedy-addition-1.png).

## Delivered colored rule

1. Start at each R272 accepted native ICC-luminance peak; retain its image-learned color.
   Test256 native straight paths to the perimeter of a radius32-pixel square.
2. Require the existing image-derived background test to pass. Chromatic pixels need
   saturation≥0.20 and hue within32° of the learned bead hue; adjacent saturated samples
   cannot jump more than18°. A small bright neutral highlight allowance remains.
3. The native luminance floor is `max(0.008, 0.035 × peak Y)` and is **never raised**.
   ICC-corrected Y uses proper sRGB linearization. Neutral dark material is a barrier.
4. Track a 3×3 mean-Y minimum along each native path. Once below60% of peak Y, a rise
   greater than `max(0.003, 0.25 × minimum)` identifies a competing bright region.
   End one native step inside that first trough. Color/background/dark-floor barriers
   also stop a path. No interpolation or modeled bead shape is used.
5. Take the seed-connected native union, opening with a radius2 disk, then two inward
   cross erosions. Cleanup only **removes** pixels from newly computed photographic
   support; growth is not restricted to the old R272 mask. Reject open growth,
   >870 pre-cleanup pixels, <45 remaining pixels, holes, loss of the seed, or solidity
   <0.84. The convex hull is used only to measure solidity, never to fill the mask.
6. Withhold regions containing another observed R272 peak, or overlapping another
   otherwise accepted region. No ownership partition or silent merging is performed.

This is a broad confidently interior support under explicit rules, not a proof of the
mathematically largest interior or a recovered physical boundary. Directional sampling,
color drift, unresolved valleys and the historical size ceiling still cause exclusions.
The red-context failure crop is retained separately from successful red examples.

## Black-reflection ownership

Nine controls combine radii8/12/16 with strongest-wins, margin-tested competition,
and deferral of every close group. Delivered radius12 requires one dominant reflection:
all others must have ≤75% of its peak ICC Y and ≤85% of its peak-to-shell contrast.
Rank by peak Y, then contrast and stable ID. Require a non-paper dark bridge and group
diameter≤12; chains or uncertain/similar reflections defer the entire group.
Winner-only16 keeps197 black supports; margin16 keeps195, deferring six ambiguous
candidates. Margin12 keeps201 of207, suppressing six weaker reflections.

[Suppressed reflection example](review/r273/black-ownership-06.png) ·
[all six groups](review/r273/black-review-groups.json) ·
[black controls](review/r273/black-controls.json).

Accepted black masks, first dark enclosing perimeters and measurements are unchanged.
The rule is an ownership heuristic: it can suppress or defer genuinely separate close
beads. It does not establish that every remaining photographic reflection is unique.

## Validation and limitations

36 Python tests and31 checks of the actual viewer JavaScript pass. Full-photo validation
independently checks all native measurements, connected masks, exact areas/centroids,
maximum ICC Y/RGB/HSV, closed outlines, nonoverlap,201unchanged dark shells,869retained
decisions and148preserved R272 file hashes. Re-running the selected algorithm exactly
reproduces the inventory. Smoothed display contours do not change measured masks.

| Known synthetic bodies recovered | 52 R272 scenes | 112 preserved R270 scenes |
|---|---:|---:|
| black | 28/32 | 32/32 |
| red | 24/32 | 9/24 |
| yellow | 4/32 | 15/45 |

Selected-rule false locations and duplicate extras are zero in these fixtures;
foreign region pixels total **0**. Earlier relative variants each expose a
one-pixel neighboring-body intrusion in different touching examples; their records
are preserved. Four dedicated black fixtures test weaker/similar highlights, separate
beads and intervening background. Similar/unclear close reflections are withheld.

Low synthetic yellow recall is explicit: the R272 generator's16×19-radius ellipses
have about955pixels, exceeding the retained870-pixel ceiling when expanded nearly to
the edge. They are now excluded instead of silently replacing the requested broad
interior with a bright core. Smaller native fixtures exercise nonempty yellow regions.
The historical stress set additionally exposes pale-color and invisible-interface
failures. These tests do not certify photographic ownership or whole-photo recall.

The viewer uses only the requested ID/size/Nth/previous/next/pan/zoom controls, cyan
outlines/peaks, photo-only view and an optional excluded layer. Size ordering uses
exact native counts with ID ties. Real browser rendering remains unverified: R272's
Chromium launch was blocked by sandbox permissions. Following the user's instruction
to skip work needing new approval, the saved R273 browser check is deferred; Node
checks are not described as rendered-browser validation.

R272 reports, photographs, inventories, detectors and viewers remain unchanged.
No geometry, physical-string indexing, watershed, old splines or hand-assigned runtime
identities. Stop after commit/push. Next task is photographic review of dark-edge reach,
red exclusions and the six black ownership decisions; no automatic next phase.
Keep the current model/reasoning; no `/new` is needed for that review.
