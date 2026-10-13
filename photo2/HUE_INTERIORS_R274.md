# R274 — hue-aware colored interiors

**570 accepted interiors: 201 black, 116 red, 253 yellow. All 524 previously trusted
locations survive.** There are 574 trusted location proposals in total; 4 have uncertain
larger interiors and remain selectable as cyan points without accepted outlines.
Every black mask, peak and reflection-ownership decision is unchanged.

[Viewer](hue_inventory_r274/index.html) · [whole photograph](review/r274/whole-photo.png) ·
[inventory](review/r274/inventory.json) · [reproduction/evidence](review/r274/README.md).

## What changed

R273 allowed 32° of seed-relative hue drift and 18° between adjacent saturated pixels.
A gradual color transition could pass both tests while brightness stayed adequate.
R274 compares each reliable native hue with **this bead's own measured core hue** and
with the photograph's learned opposite-color prototype. Growth stops unless the
pixel favors the current bead by at least 2°. That decision is independent of whether
luminance rises, falls, or stays almost constant. Red and yellow use the same rule.

Prototypes are recomputed from image-only R272 candidates: red 352.4144°, yellow 35.3446°
in this ICC-corrected photograph. Those numbers and all review crop coordinates are
outputs, not runtime inputs. Hue distances wrap around 360°. Reliable color votes need
S≥0.35 and channel spread S×V≥0.055. Lower-saturation highlights do not vote as if their
hue were a reliable material color.

A bounded highlight continuation requires low saturation, brightness≥max(0.04,20% of
seed Y), distance ≤ 8 pixels from the seed and ≤ 6 pixels from non-paper, strongly chromatic,
seed-consistent support. It repairs a rejected ring around a neutral highlight in the
component test. Confident and uncertain paper remain barriers; the R273 experimental
background relaxation remains disabled.

R273's low native brightness floor, same-color valley checks, 870-pixel pre-cleanup ceiling,
removal-only opening/retreat, 0.84 solidity and competing-location checks remain. Thus
moderate darkening is allowed; the new stopping evidence is explicitly **color**.
Measured masks stay connected and separate from display-smoothed contours. No watershed,
old splines, bead geometry, manually assigned identities or physical-string indexing.

## Photographic comparisons and stopping evidence

Each comparison shows the original, R273, the selected hue rule, and color evidence.
Orange squares flag R273 pixels closer to the global opposite-color prototype; these
are **color-conflict indicators, not independently labeled bead boundaries**. The cyan
line and white marker identify the sampled path and new stopping pixel. Contact crops
are selected automatically from color conflicts near opposite-color proposals.

- [Yellow contact 1](review/r274/yellow-1-highlight-palette.png): trims the redward
  extension below the yellow bright interior. [Native hue/Y trace](review/r274/path-1.png).
- [Yellow contact 2](review/r274/yellow-2-highlight-palette.png): retains the long yellow
  support but stops earlier at its reddish lower transition.
- [Yellow beside red](review/r274/yellow-3-highlight-palette.png): stops on hue before
  R273's later brightness-valley decision. [Trace](review/r274/path-3.png).
- [Red beside yellow](review/r274/red-5-highlight-palette.png): a small boundary correction
  at the yellow-facing tip; this is a small incursion, not evidence of a large merged bead.
  [Trace](review/r274/path-5.png).
- [Larger red-labeled conflict](review/r274/red-4-highlight-palette.png): the old region
  spans a yellow-looking area. The new large interior is withheld and its location is
  retained. Color/ownership is ambiguous here; this is **not** presented as a successfully
  redrawn red bead. Its prior red label is not newly certified.

At all five selected new stopping pixels, R273's brightness floor passes and its valley
trigger is false. The rule stops because of hue, not a substituted brightness threshold.

| Automatic ID | Prior color | Hue at new stop | Native ICC Y | Later R273 stop |
|---|---|---:|---:|---|
| C-1196-0273 | yellow | 10.24° | 0.09425 | color-boundary |
| C-1423-3004 | yellow | 10.83° | 0.10316 | color-boundary |
| C-1977-2780 | yellow | 10.00° | 0.09344 | first-valley |
| C-1007-1515 | red | 21.85° | 0.39690 | first-valley |
| C-0267-0926 | red | 20.61° | 0.16401 | first-valley |

[Exact step records](review/r274/review-paths.jsonl.gz) preserve H/S/V, native Y, 3×3 mean Y,
coordinates, old/new endpoints and stopping reasons. [Paired masks/counts](review/r274/paired-interiors.csv)
retain every accepted or excluded proposal. Photographs support a conservative
color-boundary improvement; they do not establish pixel-perfect physical outlines.

## Rules compared

| Rule | Red interiors | Yellow interiors | Trusted points without accepted interior |
|---|---:|---:|---:|
| r273 | 116 | 207 | 0 |
| seed-hue18 | 124 | 264 | 13 |
| palette | 114 | 251 | 8 |
| contrast | 113 | 244 | 22 |
| seed-palette | 116 | 253 | 4 |
| local-contrast | 113 | 248 | 11 |
| path-contrast | 111 | 141 | 96 |
| highlight-palette | 116 | 253 | 4 |

`seed-hue18` narrows a fixed hue tolerance. `palette` and `contrast` use global color
prototypes; they over-trim some orange/shaded yellow interiors. `seed-palette` uses
local core hue instead. `local-contrast` adds weighted local-hue/look-ahead tests;
`path-contrast` emphasizes spatial hue jumps and sustained drift. Those additional
stops can fragment otherwise plausible supports; they are retained as controls.
**Selected: highlight-palette**, local core-versus-rival competition plus the bounded
highlight continuation. Selection uses one rule everywhere, never a per-bead choice.

The comparisons retain broad supports: median paired yellow area is 83.54% of R273 for
locations accepted in both versions; median paired red area is unchanged. This is a
boundary correction, not a return to the small R272 bright cores.

| Color | Accepted interiors | Retained masks changed | Retained unchanged | Newly accepted interiors | Old interiors now uncertain |
|---|---:|---:|---:|---:|---:|
| red | 116 → 116 | 13 | 100 | 3 | 3 |
| yellow | 207 → 253 | 206 | 0 | 47 | 1 |
| black | 201 → 201 | 0 | 201 | 0 | 0 |

“Changed” is measured pixel difference, not an automatic claim that every changed
outline is better. All 323 R273 colored locations remain; 3 red and 1 yellow now have uncertain
interiors. 47 new yellow and 3 new red interiors come from previously excluded automatic
R272 proposals. Those inherited exclusions and every original maximum remain available.

## Location and interior are separate records

Stable IDs persist. `locations` records point measurements, prior source and confidence;
`beads` contains only accepted, measured interiors with exact masks/areas/centroids,
ICC peaks/RGB/HSV, bright patches and separate closed display contours. R273 trusted
coordinates are preserved exactly even when a new interior peak differs. The viewer
shows both measurements explicitly. Inventory numbers enumerate location proposals,
not a modeled string.

Cyan points remain visible and selectable for uncertain interiors. ID jump works for
them, with a plain explanation and no invented area. Smallest/largest/Nth/previous/next
use only accepted native mask areas, with deterministic ID ties. Selecting a location
without an accepted region has no fictitious size rank. Excluded, untrusted candidates
remain in the optional separate layer. No diagnostic tabs or extra controls were added.

## Validation and limits

45 Python tests and 49 checks of the actual viewer JavaScript pass. Independent validation
checks 570 native masks, 574 locations, unchanged 201 black regions, exact measurement/centroid
calculations, nonoverlap, all 524 prior trusted coordinates and 162 preserved R273 file hashes.
The selected inventory is reproduced exactly from image pixels through R272/R273/R274.
Real browser rendering remains deferred after the known sandbox failure; Node DOM/canvas
checks are explicitly not a rendered-browser validation.

35 new contact/background scenes and 164 preserved stress scenes give zero selected false
locations, duplicate extras, background pixels or neighboring-body pixels. End-to-end
recall on the 35 new scenes is 13/30 red and 13/30 yellow, limited by inherited location gates;
this is not a whole-photo recall claim. Several neutral-highlight/soft-transition cases
never reach R274 because R272 rejects the candidate. They remain documented misses.

To isolate the requested boundary behavior, additional component tests hold locations
**automatically detected in the equal-Y scene** fixed while changing only hue transitions,
shading or highlights. In the gradual, almost-equal-Y interface, R273 grows 1018/1198-pixel
regions that fail its size limit; R274 gives two separate 577-pixel interiors with no
foreign pixels. A neutral highlight changes the old yellow mask to an unusable 5 pixels;
the new rule retains 490. Same-color shading and dimming retain the same areas in both
methods. [Smooth color boundary](review/r274/synthetic-soft-boundary.png) ·
[Highlight](review/r274/synthetic-neutral-highlight.png) ·
[exact component results](review/r274/component-evaluation.json).

R273 is preserved in full. Stop after commit/push for review of the contact photographs
and retained points with uncertain interiors. Keep the current model/reasoning; no
`/new` is needed. No automatic geometric or indexing phase follows.
