# R272 — trusted interiors and a simple inventory viewer

[Open the viewer](trusted_inventory_r272/index.html) ·
[Machine-readable inventory](review/r272/inventory.json) ·
[Flat measurement table](review/r272/inventory.csv) ·
[Examples and diagnostics](review/r272/README.md)

**255 of R271's 453 location proposals qualify for this expanded inventory:**
181 yellow, 74 red, and no black beads. All are found by the same image-only
pipeline across the photograph. No count target or geographic quota is used.
All 453 R271 proposals are reproduced exactly and preserved; the additional
color/interior checks exclude 198. The accepted subset still occupies 15 of
16 fixed full-frame grid cells. This is a trusted-subset proposal for review,
not complete bead recovery or calibrated proof of accuracy.

No black candidate passes all gates in this photograph. The implemented black
rule requires a neutral reflection and a predominantly dark, neutral surround;
it saves only a small reflection interior. It passes a known synthetic black-bead
test, shown [here](review/r272/synthetic-black-reflection.png). The inventory does
not invent a black classification to fill a category.

## What is saved for each accepted bead

- Stable source-image-scoped ID `B-x-y`, derived from the automatic location anchor.
  It survives changes in accepted membership. `inventory_number` is sequential
  row-major inventory order, **never a modeled string index**.
- Brightest native pixel, ICC-corrected relative luminance on 0–1, original RGB/HSV,
  and sRGB RGB/HSV. Hue is in degrees; S and V are 0–1. Ties use y then x.
- The connected bright patch (at least 85% of peak luminance), its exact pixel
  count, runs and unweighted native-pixel centroid.
- Color, image-derived palette evidence, location/region confidence measurements,
  parameter values and explicit acceptance reasons.
- Exact connected interior mask as inclusive `[y, x_start, x_end]` runs, pixel
  count, bounding box and area centroid, plus both raw and smoothed closed contours.

**Brightest has a defined scope:** the point maximizes luminance in the confidently
owned interior and also matches the absolute brightest pixel of the original 9×9
location neighborhood. An incompatible local brightest pixel excludes the
candidate; the algorithm does not silently replace it with a dimmer sample.
The point is not claimed to be the brightest pixel anywhere on the entire physical
bead, whose full boundary is deliberately not reconstructed.

Integer `(x,y)` denotes a native pixel center in the EXIF-oriented photograph.
Centroids average those coordinates; no interpolation enters any measurement.
The display adds half a pixel only to align this convention with the browser's
image raster. All color-managed image pixels were checked against the source ICC
conversion. R270's source profile and luminance definition are retained.

## Interior and color rules

R271's location/background/illumination/stability gates are unchanged. No reviewed
coordinate is used as input. Strong chromatic samples near automatic proposals
supply two circular hue clusters; the observed prototypes are approximately
0.68° and 37.76°. Semantic red/yellow names require proximity to their ordinary
hue references and a clear separation margin. Candidate color needs sufficient
saturated local support, low hue dispersion, and a clear prototype match. These
are not the historical hand-selected HSV boxes. Unsupported colors are deferred.
Neutral reflections require independent dark-body evidence to qualify as black.

For each qualifying location, start at the local native brightest pixel. Colored
pixels must remain within 10° of the local body hue and above both 0.08 luminance
and 40% of peak. Neutral specular pixels can join a strongly classified colored
patch only within its bright 9×9 core. Black reflection pixels must stay neutral
and above 55% of peak, with the same absolute floor. Each proposed pixel must
have a straight native seed-to-pixel path that never rises in luminance and never
crosses a failed brightness, color or background test. Stop at the first failure.
There is no watershed, spline, inferred center, ownership partition or neighbor model.

Take the seed's four-connected component, apply one exact native-pixel inward
retreat, and keep the seed-connected interior. Reject a proposal if the peak is
lost, the mask has holes, the support reaches the 20-pixel analysis radius, the
pre-retreat component exceeds 870 pixels, or too little reliable area survives.
Minimum interior sizes are 20 colored pixels and 9 black-reflection pixels; the
bright patch needs at least 5 pixels and must stay within 4 pixels of the stable
location. No holes or excluded pixels are filled to enlarge the mask.

Repeat using an 8° hue tolerance and a luminance floor five percentage points
higher. At least 60% of the interior must remain and its centroid may move at most
1.5 pixels. A substantial competing mean7 maximum inside the region rejects it;
any overlap between otherwise accepted proposals rejects both. **Largest interior**
means the full connected component surviving these declared confidence rules,
not the full bead or the largest possible region under relaxed thresholds.

Display outlines use two cyclic 1:2:1 vertex averages, with no splines. Maximum
vertex displacement is 0.4375 native pixels. Smoothing changes neither masks,
areas, centroids nor size ordering. The outlines are conservative interior supports,
not estimates of the physical bead boundary.

The three R00956 yellow locations retain accepted interiors. R01284's central
pale location remains a good R271 location but is **excluded from R272** because
its interior disappears under the stricter hue test. Its shadowed neighbor remains
excluded by R271. Location confidence is not treated as automatic region confidence.

## Which requirements exclude otherwise promising candidates?

This audit follows the user's steering; it does not relax thresholds or add beads.
All 40,483 location candidates and all 453 proposed interior records survive.
Failure totals overlap and should not be summed as unique candidates.

| Requirement | Candidates failing it | Only this inexpensive gate fails | Also pass remaining detailed checks |
|---|---:|---:|---:|
| Background clearance | 36,519 | 510 | 1 |
| Mean luminance ≥ 0.25 | 4,052 | 252 | 23 |
| Broad/even illumination | 743 | 115 | 45 |
| Local contrast | 36,991 | 1 | 0 |

All 878 single-gate cases receive additional search, color, interior and ownership
checks, including close-location conflicts with the inventory and other diagnostic
candidates. The failed screening gate is omitted **only for this diagnostic**;
all candidates remain excluded. Thus “passes the remaining checks” is a measured
counterfactual, not a visual truth label or permission to accept the bead.

The background-only remaining case is red. Of the 23 brightness-only remaining
cases, 17 are red and 6 yellow; all 45 uneven-illumination-only cases are red.
This demonstrates the illumination rules' bias against some red patches and
provides concrete examples for review. Brightness is not an independent estimate
of lighting; reflectance and illumination remain confounded.

[Background example](review/r272/audit-background-nearby-1.png) ·
[Dim example](review/r272/audit-insufficient-light-1.png) ·
[Uneven-illumination example](review/r272/audit-uneven-light-1.png).
[Exact counts for every recorded requirement](review/r272/requirement-failures.json)
include the new region failures. Unknown color stops subsequent region measurement;
“sole recorded region failure” does not imply that unmeasured tests passed. Image
edge candidates similarly lack full neighborhood measurements.

## Viewer and validation

Open the HTML directly; Chromium was tested without a server. The only controls
are ID jump, smallest/largest, one-based Nth smallest/largest, previous/next in the
current ordering, zoom/pan, fit-photo, and overlay visibility. Clicking a native
region selects it and automatically centers/zooms. Details show ID, color, native
brightest point, luminance, RGB/HSV, both centroids and both pixel counts.
Ascending and descending size order both use **exact mask counts, then ascending
ID for ties**. Inventory numbering is independent of size order.

Examples: [smallest, 20 pixels](review/r272/smallest.png),
[median, 49 pixels](review/r272/median.png),
[largest, 143 pixels](review/r272/largest.png).

12 Python tests cover color names/unknown colors, reflection-only black interiors,
ownership, connectedness, measurements, local brightest pixels, stable IDs,
translation and display-only smoothing. Native-data validation recomputes all
accepted masks, checks 13,855 interior pixels and 4,098 bright-patch pixels, and
verifies 510 closed simple contours and exact RGB/HSV/centroid/peak measurements.
32 Chromium checks cover the complete viewer, size ties, valid/invalid navigation,
clicking, selection centering, zoom/pan, overlays, direct-file loading and layout.
Across 112 preserved stress scenes, 11 accepted regions have **zero background
pixels, zero pixels belonging to another body, and zero duplicate known bodies**.
Most synthetic cases are intentionally withheld; these tests do not certify
whole-photo precision. The separate black fixture is nonempty and reflection-only.

R270/R271, historical detection and historical viewers remain unchanged. No geometry
or string indexing was resumed. Stop after commit/push. Next only when requested:
review the interior examples and single-gate exclusions before changing any criterion.
Keep current model/reasoning; no `/new` is needed for that review.
