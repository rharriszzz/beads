# Direct practice with beads.pov — R017

This exercise runs the original legacy scene with an invented color sequence.
It replaces the proposed inverse benchmark for this step, at the user's request.
The plan was committed first as `0fbd48f`, then implementation continued.

## Reproduce

```sh
.venv/bin/python photo2/practice_legacy.py
```

`practice-pattern.json` is the authored input: 40 colors, 20 groups, palette
indices 0=Red, 1=Green, 2=Blue. The generated wrapper declares `CustomColorPattern`
and `CustomPatternGroups`, then includes the actual root `beads.pov`. The small
optional hook replaces only color sequence and group count before the original
size/closure calculations. The original case-1 materials, camera, lighting,
shape, placement and hole orientation do all the rendering.

Outputs under ignored `photo2/output/legacy-practice/`: `phase-0.png`,
`phase-half.png` (2400x1800), two detail crops, generated wrapper, renderer logs
and `report.json`. The report contains exact commands, source/artifact SHA-256,
pattern input, Python/Pillow versions and parameters read back from POV-Ray.
POV-Ray 3.7.0.10.unofficial identifies itself in the hashed logs. Rendering uses
two threads and antialias threshold 0.1. Existing missing-assumed-gamma and version
placement warnings remain; no gamma/material modernization was mixed into practice.

## What the source and renders teach

- The sequence contains 800 beads and closes after 123 turns, giving
  `exact_beads_per_row=800/123=6.504065041`. Relative to nominal 6.5 this is a
  total closure correction of -27.6923 degrees over the entire necklace. It is
  distributed by the existing formula, not a free independent twist field.
- A 40-bead repeat advances `40*123/800=6.15` turns around the rope: the next
  occurrence begins 54 degrees farther around its cross-section. Thus a repeat
  does not have to appear as an identical patch from the camera. Different
  occurrences can expose different sequence positions. This is a geometric
  opportunity, not yet a measurement of full visibility or recovered colors.
- The two clock values are 0 and 0.0625. Both select case 1; `rclock` is 0 and
  0.499995. The latter changes both row phase (nearly 180 degrees) and position
  around the central circle (nearly 30 degrees). It is not a camera change or
  an isolated row-phase experiment.
- Both full renders and both right-side crops were inspected. Green/blue regions
  and red runs recur with different apparent arrangements around the ring;
  the side crops show bead-on-bead overlaps and partly hidden colored bodies.
  Same-colored neighbors and highlights make some boundaries less distinct.
  Hole axes remain tangent to the central circle, as specified by the source;
  no additional tilt is introduced. Visible hole rims are not measured here.
- The legacy scene places bead bodies, without explicit thread or crochet
  stitches. Learning its appearance is useful; it does not independently certify
  every construction detail. The user's construction guidance remains binding.

## Checks and limits

The default case-1 render before/after adding the hook is pixel-identical at
640x480, clock 0, no antialiasing. Actual commands were:

```sh
# Before editing beads.pov (source is preserved at commit 0fbd48f):
povray +Ibeads.pov +Ophoto2/output/legacy-practice/default-before.png +W640 +H480 +K0 +FN8 -D -A +WT2
# After adding the optional hook:
povray +Ibeads.pov +Ophoto2/output/legacy-practice/default-after.png +W640 +H480 +K0 +FN8 -D -A +WT2
```

To reproduce the earlier source after this change, save
`git show 0fbd48f:beads.pov` to an ignored output `.pov` file and render with `+L.`.
Compare decoded RGB pixels, since PNG timestamps change file hashes.
The renderer reports the expected case, pattern length, bead count and turn count
for both custom views. All 13 existing tests and practice script compilation pass.
All final report source/artifact hashes were checked against disk. Initial crops
contained too much blank center; the crop was moved onto the rope and both
practice images regenerated. No inverse fitting or segmentation test was run.

Final local image hashes:

- phase-0.png: `71e3dcaccd11960837dd5a1174ebfba7df404962eead745614d8469e3c103b48`
- phase-half.png: `e3b8820f11361a5f67f96f6a55b333852c212f2ca3fa30a29d2eed8cb9341068`

Next bounded task: use these same legacy renders and known sequence to identify
selected bead indices/repeat slots and measure which occurrences are visible.
Keep any instrumentation separate from the beauty render. Stop at an illustrated
visibility/sequence check, before automated recovery or photo refitting.
