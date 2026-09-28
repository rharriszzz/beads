# Lessons carried into the new branch

Source: [photo-2-reconstruction at 2c4c116](https://github.com/rharriszzz/beads/tree/2c4c116bf7f7b9e8c773358a97740dcd77879a8a).
Old experiments and request history stay there; this branch does not import their
numerical pipeline or adopt their masks. R092 returns priority to photo 2 and
supersedes the earlier generated-JPEG-first task order.

## Quick shape model

Visible bead shape is a projected 3D surface after neighbor occlusion. It need
not be an oval: caps, crescents, notches and fully hidden beads occur. Highlights,
visible centroids and physical centers differ. Helicity determines minor-circle
progression; local in-plane section direction and the global camera/plane view
determine the shape family. R086 confirms the necklace lies flat on paper/table:
no independent out-of-plane centerline bends or local section tilts.

Before geometry or helicity work, read the prior branch's
[SHAPE_REASONING.md](https://github.com/rharriszzz/beads/blob/2c4c116bf7f7b9e8c773358a97740dcd77879a8a/photo2/SHAPE_REASONING.md)
quick model and applicable task row; follow detailed recipes only as needed.

## Methods and failures worth retaining

- [R091 methods overview](https://github.com/rharriszzz/beads/blob/2c4c116bf7f7b9e8c773358a97740dcd77879a8a/METHODS_AND_PLAN.md):
  approximate HSV photo mask, boundary-derived midpoint centerline, periodic
  spline, and separately reviewed generated-image bead inventories. None proves
  the photo's full order or repeating pattern.
- [R067 edge failure](https://github.com/rharriszzz/beads/blob/2c4c116bf7f7b9e8c773358a97740dcd77879a8a/photo2/IMAGE_EDGES.md):
  local color-transition evidence often extended a candidate into shadow/blur.
  R093 now adds maker feedback: implausible indents and bumps. More smoothing
  alone cannot establish the true edge; compare raw views and uncertainty.
- [Older photo questions](https://github.com/rharriszzz/beads/blob/2c4c116bf7f7b9e8c773358a97740dcd77879a8a/photo2/QUESTIONS_FOR_MAKER.md)
  remain unanswered. R093 rejects contour quality in general, without supplying
  exact edge coordinates or selecting a replacement. Do not treat it as labels
  for those historical transects, or repeat that entire question round.
- [R089 saved answers](https://github.com/rharriszzz/beads/blob/2c4c116bf7f7b9e8c773358a97740dcd77879a8a/photo2/BEADS6_SV_QUESTIONS.md):
  original A/B endpoints lie on different beads; H's specular spot is not a
  boundary; both K endpoints lie on boundaries and fail as interior references.
  Those labels are specific to beads6, not photo 2 or perturbed endpoints.
  Conventional HSV V falls with darkening. R069 ignores slivers and beads1 211.

## Reusable FFT ideas

**R110 update:** the maker reports Gaussian-window FFT works well for shadowed
background and for bead directions. [Inspected source/metric details](FFT_EXPLORER_NOTES.md)
identify the scanner's `hp_removed` as low-pass retained power fraction and the
explorer's opposite-pair grouping/reconstruction. Reproduce that raw-window
baseline before substituting detrended texture or spatial filters. Directional
analysis explicitly seeks three noncentral opposite pairs for 1/6/7.

Read local fft-image-explorer main at
`2caf0707c2b63a0d7540e2cac447d2f1b883d8c1`: README and Gaussian-window code in
map_from_fft.py. It uses spatial Gaussian weighting and local FFT metrics.
The new probe independently implements a weighted-plane residual and records its
own parameters. No external code dependency, spline import or pattern lookup.
Other permitted repositories/branches can be consulted when a specific phase
needs them; R110 compared the two FFT source files on main/radial-sum read-only.

Historical generated-JPEG inventories remain there, with unresolved extents,
palette/border uncertainty, missing indices and no verified complete inventory.
Their counts are not transferred into a photo-2 inventory on this branch.

## R098 — Maker's directional FFT method

For directions, the maker removed **both low and high frequencies** and inspected
peaks at expected bead spacings for directions **1, 6 and 7**. This is a band-pass
direction measurement, distinct from the background test's remaining-power score.
The maker reports that the angular difference between the direction-1 FFT feature
and the bracelet's local centerline is sufficient to identify helicity. Preserve
that as the proposed inference rule to implement and calibrate; the current
background probe has not identified those peaks or tested the rule.

The maker finds a Gaussian-window FFT centered on the centerline hard to interpret.
For the eventual direction review, present raw context, a centerline-tangent-aligned
patch, the visible band-pass mask, labeled peak pairs, and corresponding directions
overlaid on the photograph. An optional inverse transform of selected peaks can
show which image structure each peak family represents. Keep the original patch
and coordinate transform available so alignment does not hide a sign convention.

Define image-axis orientation, tangent/normal axes, and the mapping between a
frequency vector and its associated spatial structure before assigning hand.
Account for opposite FFT peak pairs and line angles modulo 180 degrees. Calibrate
the direction-1 association and signed relative angle on known opposite-helicity
POV-Ray examples at several in-plane section directions under a fixed camera.
Do not silently identify a frequency-vector angle with a real-space bead-connection
angle, or assume that 1/6/7 labels imply raw FFT-radius ratios of 1:6:7.
Keep the major centerline planar and local viewing direction distinct from winding.

Window width, frequency-band limits and the maker's peak-label convention remain
unspecified numerically. R109 now specifies a window width comparable to the
necklace width, centered along the centerline; Gaussian sigma/FWHM convention
still needs to be stated explicitly in an implementation. The maker also proposes
HSV paths along the centerline, with dark seam and bright specular clues and a
black-bead limitation. [Six methods and the proposed local comparison](../METHODS.md#bead-analysis-given-approximate-boundaries-and-a-centerline)
record these together. Resolve remaining spectral choices with illustrated
alternatives when this phase starts; no directional estimator has been run.
