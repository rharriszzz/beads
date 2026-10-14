# Permanent photographic measurement contract — effective R284B

This contract supersedes earlier black-support descriptions in historical R282,
R283 and R284A specifications. Historical experiments remain unchanged evidence.

**Phase 1 red/yellow:** measure a compact, photographically supported visible
interior and a representative image location. A full physical silhouette is not
required. Keep seed, peak, native-mask centroid and any subpixel contour distinct.

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

Implementation and tests: isolated R284B modules and their schema tests implement
this contract. Production inventory adoption requires explicit method selection.
