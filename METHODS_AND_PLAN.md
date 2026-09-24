# Bead reconstruction: plan, methods, and current capability

Updated 2026-09-24. This explains what is available now and what still needs
work. The immediate inputs are **beads1.jpg–beads7.jpg**, the generated images.
Photographs come afterward. Pattern identification must use the images without
consulting the pattern definitions in the POV-Ray file.

The main problem is currently **identifying every visible bead reliably**.
We have approximate bracelet/background separation and many bead candidates.
We do not yet have a verified complete bead inventory or a recovered full
pattern for any of the seven generated images.

## Direct answers

| Question | Generated images: beads1.jpg–beads7.jpg | Existing work for beads-photo-2.jpg |
| --- | --- | --- |
| Can we separate the background from the necklace? | Approximately, yes. A binary foreground mask isolates the broad bracelet region and its central opening. Shadows, pale beads and tiny edge fragments are not reliably separated. | An HSV color-based outline workflow and saved boundary curves exist. Their pixel-level accuracy is not established. |
| Do we have an outer-edge spline? | No saved outer spline in the current seven-image pipeline. It uses a pixel mask. | Yes: 907 sampled points, with 152 control points in the saved file. |
| Do we have an inner-edge spline? | No saved inner spline in the current seven-image pipeline. | Yes: 847 sampled points, with 142 control points. |
| Do we have a centerline? | No saved centerline spline in the current seven-image pipeline. Neighbor inference estimates an elliptical orientation from the candidate positions. | Yes: 303 saved points; a copy is tracked in this repository. |
| Can we identify individual beads? | Partially. Brightness peaks and watershed segmentation produce candidate regions, with missed beads, fragments and incorrect boundaries still present. | Earlier work has provisional labels and local fits, not a verified complete inventory. |
| Can we identify the complete repeating pattern? | Not yet, for any of the seven images. | Not yet. |

A **mask** labels pixels as foreground or background. A **boundary curve** follows
the bracelet's outline. A **centerline** runs along the middle of the rope.
An **individual-bead map** separates neighboring beads within that rope. These
are different products; having the first three does not supply the fourth.

## Background separation: the method we actually use

For the generated images, [blind_generated.py](photo2/blind_generated.py) starts
with their light background:

1. Select pixels where at least one RGB channel is below 190 on the 0–255 scale.
   This selects strongly colored or dark pixels and rejects much of the white floor.
2. Apply morphological closing with a four-pixel radius. This joins small gaps
   to make a more continuous bracelet region.
3. Keep the largest connected foreground component.
4. Fill enclosed background holes smaller than 300 pixels, while preserving
   the large central opening and background connected to the image border.

The result is a useful **approximate search region**. It is not an exact
silhouette: dark floor shadows can be included, pale bead edges can be missed,
and small disconnected visible beads can be discarded. Closing can also bridge
real gaps between beads. We need to check those errors before treating this as
complete background removal. These thresholds are for the 800×600 generated
JPEGs, not a universal rule for photographs.

For photo 2, the existing `fft-image-explorer` workflow uses color selection in
HSV space—hue, saturation and brightness—to distinguish the magenta paper and
bracelet. This is a separate method; the light-background rule above is not
suitable for that photograph. The current extractor has a paper-color box and
an alternative union of red/yellow/black selections. The saved spline file
records `image_only_hsv`, but does not record which of those current predicate
options was used. Its exact historical threshold choice should not be invented.

## The splines we already have

All three photo-2 curves are in the existing sibling-repository file
[beads-photo-2_splines.json](../fft-image-explorer/beads-photo-2_splines.json).
They are closed sampled curves in original image coordinates, with x increasing
rightward and y downward. The file records Catmull–Rom boundary interpolation.
Counts in the table include the repeated closing point.

The available [find_splines.py](../fft-image-explorer/find_splines.py) traces
foreground/background transitions to obtain the outer and inner boundary
controls, then interpolates the boundary curves. Its centerline builder
resamples the boundaries, finds the nearest point on the outer polyline for
each inner sample, and takes the midpoint. This is an approximate middle path;
it need not be the exact physical axis, particularly around tight bends.

Only the photo-2 centerline was copied into this repository:
[photo2/centerline.json](photo2/centerline.json). The outer and inner curves
remain in the sibling repository. [reconstruct.py](photo2/reconstruct.py) fits
a smoothed periodic cubic spline to the copied centerline and evaluates it at
uniform distances along the curve. That supports image sampling and the
provisional photo-2 forward model.

I verified on 2026-09-24 that:

- The source spline file matches the hash recorded in the copied centerline.
- Its photograph matches this repository's photo 2 byte for byte.
- All three saved curves contain finite coordinates and close on themselves.
- The copied centerline differs by at most 0.0000500000001 pixel per coordinate,
  consistent with its recorded rounding.

These checks establish that the files exist and correspond to the same image.
They do not establish an exact boundary fit. The saved file reports no
inner/outer intersection; I did not independently rerun that geometric test.

**The current generated-image bead detector does not use these photo splines.**
They belong to a different image. Producing and reviewing comparable curves for
the generated images is still a task, not a capability already demonstrated on
all seven.

## Individual beads: the method used and its limitations

Inside each generated image's foreground mask, the current detector does this:

1. Smooth the brightness channel and find local brightness peaks. Peaks must
   be at least five pixels apart and brighter than their broader neighborhood.
   These often correspond to bead highlights.
2. Use each peak as a seed for **watershed segmentation**. Imagine regions
   growing from the seeds until they meet: brightness valleys and image edges
   help determine where they stop. A compactness term limits excessive spreading.
3. Assign each resulting region an anonymous observation ID, mask, bounding box,
   descriptive centroid and tentative color. Color sampling avoids many white
   highlights and uses palette boxes chosen by viewing the JPEGs.
4. Flag small regions and peaks close to the estimated silhouette for extra
   review. Uncertain colors remain unknown where the rule cannot assign one.

A highlight is not necessarily a bead's center, and one peak does not guarantee
one bead. A bead may have no detectable highlight or several local maxima.
The watershed may split one bead, merge neighbors, or put their shared boundary
in the wrong place. A region centroid is also not generally the physical center
of a partly hidden bead. Color labels and unflagged regions still need review.

The first watershed version used image gradients alone; it often isolated the
highlight instead of the bead. The current version combines negative smoothed
brightness with the color gradient and compactness. This improves the visible
maps but has not solved the inventory problem.

| Image | Candidate regions | Candidates flagged for extra review |
| --- | ---: | ---: |
| beads1.jpg | 352 | 28 |
| beads2.jpg | 392 | 60 |
| beads3.jpg | 435 | 217 |
| beads4.jpg | 410 | 68 |
| beads5.jpg | 403 | 83 |
| beads6.jpg | 354 | 70 |
| beads7.jpg | 417 | 90 |

These are **not verified bead counts**. The counts change when peak spacing or
contrast thresholds change. The [observation gallery](photo2/output/blind-generated-r059-final/index.html)
shows all seven images with hoverable candidate records and optional ID labels.
It is a local generated artifact; [BLIND_GENERATED.md](photo2/BLIND_GENERATED.md)
contains commands to recreate it, detailed results and checks.

## Overall plan and the evidence needed at each stage

1. **Establish the image region and geometry.** For the generated images, review
   background masks and distinguish bracelet, central opening and cast shadow.
   Extract outer/inner contours and a centerline where useful, keeping the actual
   pixel boundaries alongside smooth curves. Smooth curves provide direction and
   width; they must not erase visible edge beads or dictate bead locations.
2. **Complete the visible-bead inventory.** Start with beads1.jpg, inspect the
   whole bracelet, correct missed beads, split merged regions and remove duplicate
   fragments. Record every visible bead's region and color, with explicit unknowns
   for unreadable slivers. Keep direct observations separate from model predictions.
   Extend to the other six images. This is the immediate priority.
3. **Assign relative bead indices.** After the observations are reliable, compare
   ways of tracing the supplied neighbor directions ±1, ±6 and ±7. Select the
   method on those observations. Retain both helicities until evidence resolves
   them; check reciprocal edges, loops and duplicate indices. Disconnected groups
   keep unknown offsets. The existing nearest-neighbor sector method is a failed
   baseline on these seven images, not the accepted final algorithm.
4. **Infer the repeat and the remaining information.** Test indexed color
   observations for repeating sequences while keeping missing positions in place.
   Repeated occurrences may supply evidence for a color hidden at another
   occurrence. Unsupported positions remain unknown; inferred colors must be
   labeled as inferred. Check candidate repeats against observations not used to
   select them, retain alternatives, and do not look up the POV-Ray patterns.
   Successful toy sequence tests alone do not establish image recovery.
5. **Transfer the demonstrated method to photographs.** Only after success on
   the generated images, reuse the existing photo-2 curves and adapt background,
   boundary and color handling to the photograph. Do not assume synthetic-image
   accuracy carries over automatically.
6. **Fit and validate the appearance.** Use Python for geometry/analysis and
   POV-Ray for camera, lighting and bead appearance. Compare reconstructed images
   and separate crops with the input. A similar-looking render is not by itself
   proof that bead order or the repeat is correct.

The current index attempt already illustrates why the order matters: all four
variants on every generated image produce contradictory or duplicate indices.
Trying to extract a full pattern from those assignments would turn detection
errors into a fabricated sequence. Small compatible local fragments are retained,
but none establishes the whole pattern.

The next bounded work item remains a reviewed visible-bead inventory for
**beads1.jpg**, with explicit unresolved regions. Its stopping point is that map
and its checks, before another repeat search. No additional pattern information
from you is needed to do this work.
