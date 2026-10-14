# Existing boundary generation — diagnosis before replacement

The current system begins with photographic cues, not physical bead centers.
R284A combines preserved image-only seeds with local maxima of three- and
five-pixel mean luminance and maxima of colored-region thickness. Nearby cues
may consolidate when a same-color route lacks a sufficiently dark saddle. This
can suppress redundant measurements, but it cannot prove that two features
belong to the same bead.

Pixels are classified using ICC-managed linear luminance and HSV appearance.
The algorithm learns two pigment hues and a background hue from the photograph.
Colored support must have sufficient saturation and brightness, be closer to its
own pigment than the competing hue, and avoid the paper mask. A bounded exception
admits bright, weakly saturated highlight pixels next to pigment. These rules
identify plausible photographed material; they do not directly locate a bead's
physical edge. Neighboring beads of the same color can satisfy exactly the same
rules, while a shadowed portion of one bead can fail them.

R282's selected colored rule finds the connected component near a seed within
a fixed search radius, opens it with a small disk, erodes it, and retains the
connected remainder. R284A Method A adds an opening radius derived from maximum
interior thickness, capped at four pixels, then restores one pixel inside the
original mask. Opening removes protrusions too thin to contain its disk. A broad
tail can contain that disk and survive; dilation can restore part of its rim.
Neither operation explicitly tests the brightness saddle along a branch. A
surviving tail shifts the measured area centroid even if its boundary looks smooth.

Method B instead assigns pixels through competing shortest paths, with costs
based on brightness and local gradients. A winning-margin requirement leaves
ambiguous pixels unassigned. Competition prevents shared pixels, but multiple
seeds on one body can still produce several false bead supports. Its smooth or
flat boundaries may reflect seed competition and search limits rather than an
actual photographic transition. Method C's straight paths stop at material
barriers and renewed brightness rises. Shading, texture and off-center highlights
can therefore cut artificial notches or crescent-shaped remnants from valid
material.

Connectedness, area, solidity and thickness gates catch some small, fragmented or
obviously wandering regions. They do not establish distinct-body ownership, and
symmetrically marking overlapping masks uncertain does not repair their shapes.
The useful foundation is independent photographic evidence with exact native
masks and explicit uncertainty. The inadequate assumptions are that material
connectivity implies ownership, local morphology identifies intensity boundaries,
and every competing cue deserves a separate body. Historical black masks also
include dark collars. R284B replaces that interpretation with measurements of
specular reflections alone, keeping any subpixel contour separate from native
intensity support and leaving physical correspondence to Phase 2.
