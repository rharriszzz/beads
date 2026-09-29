# Patch size and one extra neighbor step — R152–R155

**Use the existing 27-body patch first.** As a practical target, roughly 20–30
substantial visible bodies containing several overlapping six-neighbor stars is
reasonable. This is a proposed starting size, not an experimentally established
minimum or a guarantee. Width, position accuracy and viewing geometry matter
alongside bead count. Do not collect more labels before testing the saved patch.

**Angle-derived longitudinal target — R153–R155:** the nominal geometry accumulates
one extra direction-6 step over **18.6183 model units along the centerline**,
or **6.4615 row spacings / 4.41 bead diameters**. The same span contains seven
direction-6 steps and six direction-7 steps. The existing chart spans about ten
nominal rows under either index interpretation and exceeds this size scale.
A larger equally clear patch could improve accuracy; test the current one first.
This count/spacing criterion does not guarantee helicity identification.

The [corrected maker chart](LABEL_SERIES.md) already contains six complete recorded
stars, centered on 5, 8, 11, 14, 17 and 20. A star is its central bead plus the
six neighbors in ±d1, ±d2 and ±d3. Overlapping stars reuse bodies. The patch spans
several stations along the necklace and supplies all three direction families.

![Existing numbered patch and consistent neighbor chart](review/r144/corrected/labeled-chart.png)

## Calculate the one-step difference using the earlier angles

Use the requested outward points, nominal q=6.5 and the earlier 3D chord angles:
abs(alpha6)=47.717990° and abs(alpha7)=43.306972°. Their gap is 4.411018°,
equivalent to ±2.205509° around the mean. Both have transverse chord length
T=2.924875724 model units in this nominal geometry.

```text
Centerline advance per direction-6 step: a6 = T / tan(alpha6) = 2.659753844
Centerline advance per direction-7 step: a7 = T / tan(alpha7) = 3.103046151
Step counts over common centerline span L: n6=L/a6, n7=L/a7
For one extra step: L*(1/a6 - 1/a7)=1
L = a6*a7/(a7-a6) = 18.618276905
n6 = 7, n7 = 6
```

Three equivalent calculations are angle-derived neighbor density, unrolled-arc
density and index closure. The unrolled-reference angles 47.995985°/43.585944°
with transverse arc 2.953539696 give the same result. The index calculation
independently agrees: seven +6 steps and six +7 steps both reach relative index
+42. Thus the two paths meet at the same bead, and their counts including a shared
start are 8 versus 7. The step-count difference is one. There are 13 unique bodies
in the combined paths if every intermediate body is present.

Source row advance is H=2.881399997; therefore L/H=42/6.5=6.461538.
Source bead diameter is 4.221831498; L/diameter=4.41. L is centerline arc distance,
not a projected pixel distance. Reversing helicity swaps which minor-circle side
has the seven-step path; direction 6 remains the denser index-step family.

These paths wind around the minor circle. Their intermediate outward points
cannot all be assumed exposed in a single photograph; preserve hidden positions
and edge exclusions. This comparison does not claim a straight visible chain
contains all the required bodies.

The full saved chart's two candidate index spans are 67 and 65, respectively
about 10.31 and 10 nominal row spacings. Its longitudinal extent already exceeds
the 6.46-row scale under either interpretation. Outward-point support, exposure
and camera geometry still require assessment; no new fit is accepted.

## What the earlier seven-body test does and does not show

[R149](MAKER_POINT_FIT.md) supplied arbitrary points known to lie on visible
bodies. Both opposite-helicity/family candidates could explain those positive
ownership points; even the known synthetic case permitted the wrong candidate.
Those points were **not measured minor-outward wall midpoints**. This does not
establish that seven accurately located outward anchors would be insufficient.

A seven-body star may suffice under favorable viewing geometry, accurate outward
locations and constrained centerline/camera. There is no measured threshold for
that stricter observation model yet. Multiple stars supply repetitions, leverage
across the tube and a portion that can be withheld from fitting.

## Why count alone cannot guarantee the answer

- A neighbor graph can be reflected while preserving adjacency. It does not by
  itself supply geometric chirality, even with many vertices.
- A long narrow chain supplies little evidence across the minor circle. Retain
  all three neighbor families and appreciable transverse coverage; length alone
  is not a substitute.
- The visible point selected on a body can move substantially without violating
  ownership. Increasing their count does not make them outward measurements.
- Camera/section geometry, occlusion and systematic boundary errors can imitate
  a direction change. More observations do not automatically remove those errors.
- A longer patch requires its changing centerline tangent. Do not extend the
  seven-body straight-tube approximation unchanged over the entire saved patch.

For the [nominal local outward geometry](DIRECTION_ANGLES.md), direction 1 is
85.54° from forward centerline as a 3D chord, about 4.46° from perpendicular.
Opposite winding changes the side of that small tilt. The unrolled-reference
version is about 4.29°. This explains the need for accurate relative direction
measurement; these numbers are not a guaranteed tilt in the photograph.

## A practical decision rule

Three ways to assess sufficiency are repeated neighbor consistency, supported
outward-position/direction measurements, and competing geometry fits with a
withheld portion. Graph consistency is already established. Use supported outward
measurements with the third check to judge whether the patch identifies helicity.

Fit both helicities and both remaining 6/7 assignments under plausible camera
and curved-centerline geometry. Preserve anchor-location uncertainty and check
exposure of each outward point separately. Hold out a complete supported station
or neighboring group, rather than only one selected point. Call helicity clear
when one family of poses accounts for those locations within their uncertainty,
the alternative cannot, and the prediction persists on the withheld portion.
Optimization failure alone does not establish rejection.

If both remain feasible, report the uncertainty before deciding whether better
anchors, broader transverse coverage, more length or stronger camera/centerline
evidence would help. No fitted patch-size sweep, success probability or guaranteed
minimum was measured in this explanatory step.

**Stopping point:** practical size/decision criterion recorded; existing 27-body
patch is the next test, with no new fit or label collection. **Next task:** assess
supported outward locations in this saved patch and compare competing projected
poses, preserving edge exclusions and withheld evidence. Neither helicity is yet
identified. Recommend gpt-6.1-sol / High; same session, no /new needed.
