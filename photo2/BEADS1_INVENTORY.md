# beads1.jpg: reviewed visible inventory — R068

**R069 update:** the maker requests ignoring all slivers and 211. The
[active selection](INVENTORY_SELECTION.md) now contains 313 body observations;
37 fragments and ten small body candidates are excluded. The R068 measurements
below remain historical evidence, and its questions are answered operationally.

The first generated image now has a reviewed observation map: **323 visibly
supported bead bodies and 37 unresolved colored fragments**. This is progress
beyond the original 352 automatic candidates, but it is **not a verified total
of visible beads**. A fragment may be part of a bead already represented or a
separate mostly hidden bead. Same-color mask boundaries remain approximate.
No bead order or repeating pattern has been inferred.

[Interactive review](review/r068/review.html) ·
[whole-image numbered map](review/r068/overview.png) ·
[region map](review/r068/regions.png) ·
[questions with images](BEADS1_QUESTIONS.md) ·
[observation records](review/r068/inventory.json).

Cyan markers are reviewed bodies; orange markers are unresolved fragments.
IDs are stable observation references, not chain indices. The interactive page
lets you hide markers, show IDs and inspect each record by hovering. Eight
magnified crops retain whole-image context through the overview.

## What changed

| Observation class | Red | Green | Blue | Total |
| --- | ---: | ---: | ---: | ---: |
| Reviewed body observations | 136 | 134 | 53 | 323 |
| Fragments with unresolved bead identity | 14 | 15 | 8 | 37 |

From the 352 original brightness-peak markers:

- Retained 323 as visually supported body observations and eight as unresolved
  silhouette/fragment observations.
- Removed 18 markers on neutral boundary/background/shadow pixels and two edge
  glints without a separately supported body. Nearby colored pixels remain in
  the region/fragment audit; removing a marker does not erase that image evidence.
- Merged the duplicate marker 211 into the red body represented by 217.
- Added 18 manually noted caps/crescents/slivers, followed by 11 more visible
  slivers found by checking unassigned colored regions. All 29 additions remain
  fragments, without assuming an independent bead for each.

The edits, exact coordinates, review boxes, source hashes and reasons are saved
in [beads1-review-r068.json](beads1-review-r068.json). Removed IDs are not reused.
New fragment IDs are 353–381. Each fragment records nearby same-color body IDs
where available; those lists are possible review references, not assignments.

## Review and segmentation method

Only beads1.jpg and image-only detector/review code supplied image evidence.
The POV-Ray source, saved patterns, renderer truth and photo geometry were not
read for this inventory. The assistant inspected the full JPEG and all eight
overlapping raw, numbered and coordinate-grid crops. This is assistant visual
review, not maker confirmation or an independently labeled benchmark.

The existing R059 brightness detector is reproduced unchanged to preserve its
observation IDs. The saved edits remove/retain/add observations. Markers indicate
a visible point, often a highlight; they are not estimated physical bead centers.

The replacement **provisional region map** uses this image's visible red/green/
blue palette:

1. Keep pixels whose strongest RGB channel exceeds the second strongest by more
   than 25 levels and whose strongest channel is at least 35. Neutral floor and
   cast-shadow pixels are excluded. This is an image-specific color-support mask,
   not an exact silhouette, and is unsuitable unchanged for the other palettes.
2. Fill enclosed holes of at most 64 pixels to retain small white highlights;
   never fill a component connected to the image border. The large bracelet
   opening stays open. Give filled pixels the nearest retained pixel's color.
3. Assign red/green/blue support by the strongest channel. Snap each observation
   seed to matching color support within six pixels; actual maximum snap is two
   pixels. Unsupported or coincident seeds would be recorded explicitly.
4. Run a compact watershed separately within each color, using negative smoothed
   brightness (sigma 1px, compactness .002). Disallow assignments farther than 28px
   from a marker. Regions cannot cross into a different color class. Adjacent
   same-color bead boundaries are still provisional.
5. Audit all colored pixels left without a region. Initially 258 pixels included
   eleven components of at least six pixels. Raw magnified inspection identified
   visible colored slivers; they became fragment observations 371–381. The final
   residual is 41 pixels, all in components smaller than six pixels, retained in
   the mask accounting. They are not silently converted into beads.

The old broad foreground contained 103,467 pixels; the new color-support mask
contains 99,809. The 3,658 excluded pixels include neutral/weakly colored boundary
pixels and shadow; this difference is not a measured shadow-only area. All final
color-support pixels fall within the eight reviewed crops. Every one of the 360
observation regions is nonempty, connected and restricted to its recorded color.

These are coverage/consistency checks, **not proof that all visible beads were
identified**. They cannot distinguish an incorrectly merged same-color pair,
a partly hidden bead, or a fragment belonging to a bead already represented.
The explicit `complete_visible_bead_inventory_verified` field stays false.

## Illustrations of remaining uncertainty

The [sliver sheet](review/r068/slivers.png) shows eleven regions the original
highlight detector missed, including red371 between green bodies, red379/380
between blue and green bodies, and blue381 below a red body. Their colors are
visible, but their independent bead identities are unresolved. The
[duplicate comparison](review/r068/duplicate-211-217.png) preserves the raw crop,
old two-marker interpretation and new single-body interpretation for maker review.
The questions file asks about these concrete image ambiguities, not additional
construction-pattern information.

## Reproduce and checks

```sh
.venv/bin/python photo2/beads1_inventory.py \
  --output photo2/output/inventory-r068-final \
  --review-bundle photo2/review/r068
.venv/bin/python -m unittest discover -s photo2 -p test_beads1_inventory.py -v
.venv/bin/python -m unittest discover -s photo2 -p test_blind_generated.py -v
```

Five new controls pass: neutral-shadow rejection/highlight retention, keeping a
large opening, color-separated regions with an unseeded component left unknown,
explicit duplicate/unsupported seeds, and retention of tiny unassigned pixels.
Five existing detector/sequence controls also pass (ten tests total); compilation
passes. Those toy controls do not establish real-image completeness.

Two final runs reproduce all 14 review artifacts and both bulk maps byte for byte;
reports match except command paths. All five source hashes verify. The 360 retained
IDs are unique, all removed IDs are absent, every seed survives in its own region,
all regions are connected/palette-pure, and all chain indices remain unknown.
The original image, eight raw/ID/grid crops, twelve final review PNGs and HTML
links were inspected/checked. No new rendering, index/repeat search, other-image
inventory or full legacy regression was performed in this step.

Committed review report SHA256:
`b1a13a22b09f3d83e587d9a5400ec11c2ef1512f25b33a4378e622c358ece45a`.
Review annotation SHA256:
`780a41a1e8be2095f4436ba1af5b29eb7378d1e67cd5df6bc479d1ca55c27032`.
Twelve PNGs, the interactive HTML, inventory JSON and report are committed as
supporting review material. Bulk label/color-support NPY maps and scratch/duplicate
outputs remain ignored; the command recreates them.

## Next bounded task

Apply the image-only review workflow to **beads2.jpg**, adapting color support to
its own visible palette. Preserve these beads1 fragment uncertainties and any
maker answers. Stop after beads2's reviewable body/color/fragment map and checks;
continue through beads3–7 before another indexing/repeat attempt. No POV-Ray
pattern lookup or hidden-bead completion. Use gpt-6-astra / High; stay here,
no `/new` needed. The full seven-image recovery objective remains unfinished.
