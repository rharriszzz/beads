# Working bead-size reminder

The user accepts the existing estimated bead rectangle as sufficient for a
provisional size reference: **30 × 29 native pixels = 870 pixels of bounding-box
area**. This is the largest estimated rectangle in the four-section R235 review,
not a verified maximum over every bead in the photograph.

Source: D4-B15 in [R235 references](review/r235/references.json), estimated extent
`[30,29]`, original reference representative `(1754,1626)`. In the
[raw D4 crop](review/r235/D4-raw.png), its visible yellow face appears broadly
rounded rather than strongly elongated along a diagonal. No orientation angle
has been measured. A rotated face may enlarge an axis-aligned bounding box; the
870-pixel rectangle is not a measured bead mask.

The user subsequently clarified that the purpose is a **hard do-not-exceed limit**
for the number of pixels in a region. Adopt **870 distinct native pixels** as the
working maximum. This is an operational ceiling accepted by the user, not a claim
that870 is the photograph's measured largest bead area. Regions of6,155 or17,095
pixels exceed it. When implementing the guard, stop and flag overgrowth rather
than silently truncate an oversized candidate and certify its coordinate.
The minimum is independent and may use more arbitrary, tunable criteria; no new
minimum has been selected. This note records the decision; the guard is not yet
implemented in the paused detector work. Do not use the reference as a complete
bead mask or a bead-position prior.
Do not use the historical1,501-pixel R259 maximum as a verified bead: it is
R01284, a documented detector failure. R260's1,053-pixel maximum is the same ID.

The user accepted this approximation after being shown a top-of-necklace crop
with native coordinate axes. No new manual bead marking or further measurement
is required for this provisional reference. Broader detector work remains paused.
