# R273 — why so few red regions, and remedies to test

**The low red count is largely a region-construction/filtering failure, not a lack
of detected red locations.** Of363R272 red proposals,79survive the new broad-interior
rules;284are excluded. Yellow retains189/299. The R273 request prioritizes a trusted
subset, but these figures do not justify treating every exclusion as unavoidable.

[Exact audit](review/r273/red-failure-audit.json) · [R273 delivery](INTERIORS_R273.md).
The counts below describe the preserved **pre-remedy** result. The user subsequently
authorized implementing remedies in this step; the delivered choice is recorded next.

## Implemented in this step

Tested each remedy separately, then together, using the same image-derived proposals.

| Uniform rule | Black | Red | Yellow |
|---|---:|---:|---:|
| Before remedies, solidity≥0.88 | 201 | 79 | 189 |
| **Delivered: solidity≥0.84** | **201** | **116** | **207** |
| Textured uncertain-background continuation only | 201 | 81 | 189 |
| Both remedies | 201 | 120 | 207 |

The selected shape remedy admits40additional red candidates and excludes3previously
accepted red regions after renewed overlap checks: **net+37**. It admits19yellow
candidates and excludes1: net+18. It never adds pixels, weakens the size ceiling or
suppresses ownership conflicts. All colors use the same0.84threshold.

[Addition near the top](review/r273/red-remedy-addition-1.png) ·
[middle](review/r273/red-remedy-addition-3.png) ·
[lower photograph](review/r273/red-remedy-addition-6.png) ·
[all gains and losses](review/r273/red-remedies-comparison.json).

Every one of the5173red background-triggered stops in the pre-remedy failure audit
was **uncertain paper context**, not confident paper. The optional implemented
background remedy permits only textured (native5×5V range≥32DN), seed-color-consistent
pixels within3pixels of definite chromatic support; confident paper stays blocked.
It adds very few detections, and its [rescued photographic example](review/r273/background-remedy-addition-1.png)
remains ambiguous. Therefore it is **not selected**; its code, results and tests remain
available. No bead-specific override was used.

All three controls introduce zero false locations, duplicate extras, background pixels
or neighboring-body pixels in the164preserved synthetic scenes. This does not verify
the photographic additions independently. The viewer and inventory select only the
shape remedy. Substantial red losses remain; the other proposals below are deferred.

## Pre-remedy failure accounting

| Failure | Red | Yellow |
|---|---:|---:|
| Shape/solidity, including combined failures | 261 | 87 |
| **Shape is the only failed requirement** | **114** | **44** |
| Open context or pre-cleanup size>870 | 159 | 63 |
| Reaches context, below size ceiling | 93 | 38 |
| Reaches context and exceeds ceiling | 53 | 16 |
| Exceeds ceiling without reaching context | 13 | 9 |
| Final ownership overlap | 3 | 3 |

The first two rows overlap; do not sum them. Of159red open/size failures,139also
fail shape,19fail only open/size, and1also fails size/seed/shape criteria.
The existing0.88solidity requirement measures area divided by convex-hull area.
It is a convenient shape proxy, not photographic evidence that a bead is absent.

## What the photographs show

- [Shape-only example1](review/r273/red-excluded-shape-only-1.png): a435-pixel broad
  interior is rejected at solidity0.875, just below0.88. Visual inspection suggests
  this is a plausible location/region unfairly excluded by the cutoff; that is a
  review judgment, not independently labeled ground truth.
- [Shape-only example2](review/r273/red-excluded-shape-only-2.png): solidity0.800;
  a large notch near the reflection and long extensions show defects in growth
  and background/valley stopping. Simply accepting this unchanged is questionable.
- [Open and irregular](review/r273/red-excluded-open-and-shape-1.png): one ray reaches
  the context boundary, while the retained mask also has a deep notch. A scalar
  global cutoff cannot distinguish the safe directions from the defective ones.
- [Open-only example](review/r273/red-excluded-open-only-1.png): a536-pixel cleaned
  region passes the shape criterion, but its original support contains5open rays.
  Earlier leakage remains disqualifying even after cleanup removes the leaking tail.

These examples were chosen by geographic quartiles within failure classes, after
running the uniform detector. They are not detector inputs or hand-assigned IDs.

## Proposed remedies — test separately before combining

| Remedy | Bounded experiment | Evidence of success / principal risk |
|---|---|---|
| **1. Replace the rigid shape cutoff** | Compare0.88/0.84/0.80solidity with unchanged masks and full renewed ownership checks; then compare against a boundary-evidence score. | Of114shape-only red failures,46already reach0.84and67reach0.80. Those are upper bounds, not guaranteed new beads. Recover convincing interiors without accepting long tails or neighbor crossings. |
| **2. Repair local growth defects before rejecting the bead** | Remove thin protrusions and unstable sectors using native support width and neighboring-direction agreement; compare opening radii2/3/4or support-restricted reconstruction. Preserve broad safe directions; never fill outside photographic eligibility. | Test the notch/tail examples and measure retained area, boundary clearance and ownership. Avoid shrinking the entire bead or merely hiding a leaking raw support. |
| **3. Distinguish uncertain background from confident paper** | Keep confident paper blocked. At uncertain-paper-context stops, require additional local color continuity and texture/edge evidence before permitting continuation. Save the exact stop class. | Red has5173background-triggered ray stops among failed proposals versus52for yellow. These are repeated rays, not5173unique pixels or beads, and do not by themselves prove false rejection. Test interior notches and paper/shadow negative controls. |
| **4. Improve dark-valley localization** | Compare native and3×3/5×5luminance profiles; normalize recovery to local dark material and noise, and use hue/chroma edges as corroboration. End at the near side of a supported trough. | Reduce premature within-bead stops and outward tails simultaneously. Test multiple highlights and touching same-color beads; do not require a circular outline or known bead geometry. |
| **5. Separate leakage from the size ceiling** | Audit open directions independently from the870-pixel safety rule. For cap-only failures, inspect whether growth crosses a real boundary before considering any separately authorized ceiling revision. | Only13red proposals are cap-only; raising the ceiling cannot address the main losses and could admit merged beads. Keep the current ceiling unchanged in this delivery. |

**Next proposed test:** repair directional growth and replace the remaining scalar
shape proxy with boundary evidence, using the completed shape/background controls
as baselines. Then compare support-restricted cleanup
on the remaining notch/tail cases. Apply each tested rule uniformly to all colors;
use color-stratified results to expose bias, not hard-coded red bead exceptions.
Keep the current and all excluded masks for paired comparison, and require the
synthetic neighboring-bead tests and geographically distributed photographs to agree.
