# Permanent photographic measurement contract — R285 clarification

This contract supersedes earlier black-support descriptions in historical R282,
R283 and R284A specifications. Historical experiments remain unchanged evidence.

**Phase 1 red/yellow:** follow photographed brightness and color, measuring a
supported visible interior and representative image location. Stop at meaningful
local dark separations, seams, occlusions or background. Distinguish ordinary
shading/texture/weak reflections from a saddle with evidence of material on both
sides. Absolute darkness alone is insufficient. Narrow bright continuations may
be valid; wide or smooth supports may be wrong. Compactness is a descriptive aim,
not a rule that deletes photographed material. Geometric regularization assists
image evidence and must not replace it. A search radius is computational, never
an accepted photographic edge; flag clipping and test larger domains.

R285 user decisions: T thickness pruning is NOT approved or preferred. Method J
is the primary colored-support candidate; its less compact shape is not a defect
by itself. Review truncation/leakage/ownership regressions before adoption. A full
physical silhouette is not required. Keep seed, peak, native-mask centroid and
any subpixel contour distinct.

**Phase 1 black:** detect and measure the specular reflection itself. The support
kind is `specular-reflection region`. Save native intensity support, peak,
representative location, shape/intensity information and a separate optional subpixel
contour. Do not dilate into dark body material, attach a dark collar, reconstruct
black-body outlines, or report the reflection centroid as a physical bead center.
Multiple reflections remain separate observations when photographically separable;
primary/secondary describes feature evidence, not resolved same-bead ownership.

**Phase 2:** fit physical geometry and common lighting to independent observations.
Determine correspondence, expected reflection location, physical centers and body
visibility conditionally. Physical identity reliability stays zero/null in pure
Phase 1 records. No fitted model or correspondence chart certifies Phase 1 input.

**Phase 3:** infer repeating color patterns from the uncertain Phase 2 inventory.
Neither later phase may manufacture, recolor, move or replace independent Phase 1
observations. Later interpretation must link original records with its own provenance.

Every Phase 1 observation remains important, including unresolved measurements.
Keep importance, photographic reliability, color reliability, visibility, physical
identity reliability, discovery phase and subsequent interpretation separate.
Smoothness alone cannot increase reliability. Scores are uncalibrated engineering
weights unless independently calibrated. Unknown identity/visibility stays unknown.

Centerline accounting uses measured support geometry, signed sides and stations.
A compact colored interior can understate full-body crossing. A black reflection
usually cannot determine whether its full black bead crosses the centerline:
record `body_centerline_crossing = null`, not a manufactured body outline. Both
sides are eligible; one close feature is not complete coverage; impose no bead quota.

Implementation and tests: isolated R284B/R285 modules and their schema tests
exercise this contract; experimental failures remain documented. Production inventory adoption requires explicit method selection.

R285 black review: smoother R2/R4 contours are acceptable candidates, with R1
as reference. Select an experimental default by localization/intensity/stability
and retain alternatives under feature ambiguity; no dark-body expansion.

R285 subsequent review priority: edge/shadow areas may be disregarded to obtain
consistently good results on clearly visible material. Preserve their unresolved
evidence and provenance; do not use that exclusion to hide clear-interior failures.
See R285_REPORT.md for the J/S comparison and the explicit yellow confirmation
failure. No new method is adopted into the production inventory by this round.
