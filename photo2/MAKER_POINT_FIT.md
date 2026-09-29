# Seven maker-point ownership comparison — R149

**Both 6/7 assignments have a pose satisfying all seven marked photo locations.**
The known-synthetic case also admits the wrong assignment at all seven points.
These locations establish useful ownership constraints, but do not yet identify
the 6/7 assignment, helicity or a unique surface pose. No fit is accepted for
propagation around the necklace.

The maker declines the manual launcher retry and asks to move on. R148's existing
automated results stand; this step resumes the planned local geometry comparison.

## Raw evidence and methods

Start with the [unaltered wider raw context](review/r149/wider-context.png),
then [the seven-body neighborhood and all retained candidate outlines](review/r149/candidate-range.png).
Original photo is `beads-photo-2.jpg`, SHA-256
`eb7c9edb62f5580ef56632872da48da92556d62b758295137068cc2404dc8fbb`,
EXIF-oriented 2540×3182; x increases rightward, y downward. Wider crop remains
[1180,130,1540,520]. Curated images crop/annotate original pixels; no image editing
or synthesized photographic evidence.

Use [corrected maker save](manual-labels-r146.json), revision 162, SHA-256
`94470dc222324dd6d2081cd43f94f187c01f18c13958761392af14ddd8bdf7de`,
and its [consistent graph](LABEL_SERIES.md). Maker identities B=22,C=20,G=23 are
confirmed. Selected locations are points on visible bodies, not measured centers,
outward anchors or highlight positions. Fit 16/17/19/20/21/22; G=23's location
is evaluator-only. Its graph relation is available, but its location does not
determine bounds, proposals, fitting losses or candidate selection.

Three methods were presented: point ownership, reviewed body outlines, and joint
torus/centerline placement. Point ownership was selected because it directly uses
the newly supplied evidence. Colors and assistant polygons do not enter its cost.
Every other image pixel remains unconstrained, including paper, shadow and P.

## Model and fitting

The [Python surface kernel](local_surface_fit.py) reproduces the source's rounded
annular bead in a local straight planar-centerline limit. Radius is
2.110915748921366 model units; axial pitch per index is 0.443292307273487.
The 676-bead calibration sets exactly 6.5 beads/turn; it does not estimate the
photo's N. All 67 latent indices −26 through 40 participate in first-hit occlusion.
Unmarked or hidden neighbors are not removed to make points fit.

Relative offsets use C's unknown full index K:

| Maker number | 16 | 17 | 19 | 20=C | 21 | 22=B | 23=G |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Family A offset | −7 | −6 | −1 | 0 | +1 | +6 | +7 |
| Family B offset | −6 | −7 | +1 | 0 | −1 | +7 | +6 |

Test both model helicities for each family. Six free pose parameters are image
translation, scale, roll, camera azimuth and section phase. The fixed 55-degree
elevation is an unobservable camera/phase **gauge**, not measured elevation.
Orthographic projection, straight-tube curvature and exact row pitch are local
assumptions. iPhone perspective remains unresolved; no actual camera distance,
elevation or calibrated intrinsics are inferred here.

Twelve loose outward-point least-squares proposals per case initialize poses;
this convenience does not make maker points outward-anchor measurements. Bounds
and scale proposals derive from the six training positions. Rank proposals by
actual visible ownership, retaining two starts. Exact first-hit ownership makes
a point's loss zero. Misses use distance to the correct visible region on a
3-pixel then 1-pixel grid. Powell has a 180-evaluation cap at each stage. Once
all six exact rays have expected ownership, stop at feasibility. This positive-only
cost does not constrain body size or boundary fit at unmarked pixels.

Holdout fields are excluded from final pose-selection keys. Both retained starts
are preserved. The [initial selection figure](review/r149/comparison.png) shows
the first training-selected B pose missing G; it must be read alongside the
[candidate-range figure](review/r149/candidate-range.png), where B's second start
passes G too. Neither start was fitted using G.

## Results and inverse check

Known synthetic truth is Family A, helicity +1. An independent POV-Ray ID render
supplies one substantial visible interior point per body. Truth pose stays in
the evaluator and is not used for initialization. The wrong B/−1 family passes
all six training rays and the withheld G ray. This is a concrete counterexample
to selecting the assignment from seven positive ownership points alone.

| Dataset | Family / model helicity | Selected training ownership | G ownership |
| --- | --- | --- | --- |
| Known synthetic | A / −1 | 1/6 | Miss |
| Known synthetic | A / +1 | 6/6 | Pass |
| Known synthetic | B / −1 | 6/6 | Pass, although family is wrong |
| Known synthetic | B / +1 | 0/6 | Miss |
| Photo | A / −1 | 1/6 | Miss |
| Photo | A / +1 | 6/6 | Pass |
| Photo | B / −1, first start | 6/6 | Miss |
| Photo | B / −1, second start | 6/6 | Pass |
| Photo | B / +1 | 0/6 | Miss |

Twenty of 32 optimizer stages hit their evaluation cap. Failed cases do not
prove infeasibility or establish a global optimum. Successful cases establish
existence of these local feasible poses, not unique recovered geometry.

Nine independent Python/POV pixel-ownership comparisons pass: eight selected
cases plus photo B's second start. Maximum disagreement is 5/19,257 pixels
(0.026%). Grid tracing leaves up to 88 grazing ray/body pairs unfinished;
all seven tested point rays converge in the selected cases. Renderer agreement
validates the implemented local surface, not its adequacy for the real photo.
Two new tests guard signed offsets/minor-circle symmetry and G exclusion from
bounds/proposals. No live annotation, source image or historical evidence is edited.

The symmetry explains part of the ambiguity. With discussion coordinates (u,v)
relative to C, kA=u+7v and kB=−u+6v, so kA+kB=13v. Reversing helicity between
these families changes minor-circle phase by 360×13v/6.5=720v degrees: the same
minor-circle position. Axial positions still differ, and camera/pose freedom plus
positive-only observations can accommodate both. This is a model identity,
not a claim that the two rendered surfaces must be identical.

## Reproduction and next evidence

```sh
.venv/bin/python photo2/fit_maker_points.py --maxfev 180
.venv/bin/python photo2/review_maker_points.py
.venv/bin/python -m unittest discover -s photo2 -p test_maker_points.py
```

Preserved [fit report](review/r149/report.json) contains source/code hashes,
parameters, seed results, convergence limits, exact ownership and render commands.
[Review report](review/r149/review-report.json) adds B's second-start renderer check
and hashes for its curated figures. Routine POV scenes/PNGs/logs remain ignored
under `photo2/output/r149`. This is assisted diagnosis using maker labels; no
automatic bead detector, color recovery, full-string indices, closure or repeat.

**Stopping point:** local point-ownership comparison complete; neither family
accepted. **Next task:** review C=20's visible extent in
[Q149.1](MAKER_POINT_QUESTIONS.md), then use supported surface boundaries to
constrain the competing poses. Preserve unclear shadowed stretches. Model
recommendation gpt-6.1-sol / High; same session, no /new required.
