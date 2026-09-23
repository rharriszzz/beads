# Reconstruction experiments

Append results; preserve failed attempts and limitations.

## 2026-09-23 — Initial forward model and diagnostic baseline

Started at `402663e` on new branch `photo-2-reconstruction`. All eight sibling
repository pulls reported already up to date. Existing `beads-render.png` and
`image-to-pattern/pattern_from_photo/` were present before work and preserved.

The saved FFT-explorer centerline visually follows the full nonconvex necklace
shape. A periodic cubic fit has arc length 9,235.5869 source pixels. The first
POV render exposed a horizontal reflection caused by `look_at` rotating the
camera basis. Explicit `direction -z`, `right x` and `up y` correct it. A
color-mask overlap check now records ordinary and reflected comparisons.

The first prototype ran on system Python 3.10.12. After the user's Python 3.12
instruction, created beads' own environment, installed NumPy/SciPy/Pillow, and
reran the baseline with CPython 3.12.14. No other environment was changed.

Five focused numerical tests pass: closed-path spacing/frame continuity;
handedness reflection and height; photo-specific paper/shadow rejection;
synthetic 271-bead repeat recovery with 55% hidden and 6% randomized labels;
preservation of unknown residues. A test initially exposed palette-ID-dependent
tie breaking in held-out scoring; fractional tie credit fixes it and makes
the candidate ordering invariant to color renumbering. These tests validate
parts of the machinery, not synthetic-image round trips or the real pattern.

Legacy regression: rendered original HEAD and modified `beads.pov`, both at
320x240 and clock 0.32 with two threads. PNG pixel arrays match exactly, maximum
channel difference zero. Evidence: `output/legacy-check.json` and render logs.

Baseline photo preview: 800x1002, 2,698 model beads, 415 turns, effective pitch
22.2544 pixels, all positions finite. Rough color-mask IoU is 0.4731 versus
0.1044 for a horizontally reflected render. This checks broad registration;
it is not a bead segmentation accuracy score. Visually the lattice remains
too regular and square, with mismatched highlights, local bead orientation,
color boundaries and shadow softness. Paper color/texture are initial proxies.

For negative sign: 1,047 retained color observations; top-ranked period 202,
held-out accuracy 0.4497, majority baseline 0.4315. For positive sign: 1,018
retained observations; top-ranked period 311, accuracy 0.4555, baseline 0.4064,
held-out coverage 0.9614. The hypotheses have different sampled positions;
their accuracies are not a controlled handedness comparison. **Both helicity
and repeat remain unresolved.** A visually fitting observation render is not
evidence for the inferred period. No scientific acceptance gate is passed.

Next: label bead centers/colors in several separated sections of the unwrapped
rope, then fit pitch, circumference count, phase, local twist and hole-axis tilt
against those observations before ranking repeat lengths again.
