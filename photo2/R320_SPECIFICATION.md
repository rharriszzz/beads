# R320 — derived closed staircase and measured optimization cost

Authorized 2026-10-18 04:10:01 UTC, scientific cutoff 04:34:01, total deadline
04:40:01. At least six minutes are reserved for verification, documentation and
commit/push. No reconstruction adoption, color inference or automatic R321.
Original photo, beads.pov and all historical outputs are immutable.

The principal physical inputs are integer count N, outer radius r in historical
units, and axial a with full thickness H=1.4ra. The closed winding is
floor(N/6.5+0.5), T=N/W. The empirical .96 factor is not an input. Initial minor
radius is r/sin(pi/T). The body axis is the normal to the local radial/helical
staircase surface, calculated from the actual center trajectory, including the
curvature of the planar photographic centerline. Its straight-axis tilt is
-hand atan(P/(2 pi R)), where P=L/W. The bore is not a thread trajectory.

The photographic centerline is deprojected through the fixed R319-best camera
(scale 8.658283442409605 px/unit, elevation/roll retained, negligible perspective
set to zero). Fixing scale makes radius a genuine photographic-size variable;
otherwise uniform scaling r,L,R and inverse camera scale would be a gauge.
The new centerline starts with zero inherited corrections. The user's subsequent
steering authorizes a two-harmonic periodic normal correction, maximum absolute
3.3468px = 0.10 of the fixed 33.468px photo diameter. Four coefficients, not 32
independent spline nodes. Local phase and local spacing fields remain exactly
zero. Global phase and station registration may move in the bounded pilot;
station remains within +/-3.3468px. Camera/light remain fixed during this pilot.

At each input, first test R0. If its sufficient convex-support separation test
fails, test R/R0=1.02,1.04,1.08,1.12,1.16 in order; bisect the first failed/passed
bracket eight times and add 0.00002 R0 clearance. This is a declared deterministic
construction, not a proof of a globally minimum contact solution. It does not
prove monotonic feasibility or exclude feasible configurations below R0 or
between failed samples. All bodies and all spatially relevant pairs participate.
Uncertified envelopes are not collisions. The coarse grid separately invokes
actual hollow-solid subdivision and retains its penetration witnesses/unresolved
outcomes. No free minor radius, tilt, turn, cant, seam or gap is optimized.

The primary near-rise screen is 0.90 <= L/(WH) <= 1.15, an explicit conservative
exploration tolerance, not measured crochet mechanics. Wider-ratio certified
models are retained as labeled diagnostic controls, never silently called
near-one-thickness packing. Seam convention is ceil(-N/2), with bead0 at the
original reference station and the same phase convention across count families.
No duplicate guard bodies replace the closing pair.

The coarse physical grid is count [2000,2200,2404,2405,2406,2600,2800,3000,3200],
radius [1.35,1.65,1.95,2.25], axial [.65,.85,1.05,1.25], both hands. All 288 inputs
are serialized. Additional 2401/2402 controls straddle an actual winding boundary.
Per count/hand, one-to-one observed-support overlap initializes a frozen map for
the same R318 photo-only 22 observations. Missing predictions mean infinite max,
never removal of an observation. Count comparisons remain correspondence-conditional.
Photographic material, paper, chromatic separators, per-core ownership and
supported exterior brackets are separate diagnostics, not hidden objective weights.

Benchmarks measure full-scene construction/contact plus native grids for 100
consecutive addresses0..99, 200 addresses-100..99 and all N bodies. All bodies
remain occluders and shadow casters. Fixed automatic photo cohorts contain fewer
observations than target bodies. Three physically different models are measured
in fresh processes, with a geometry-invalidating radius/centerline perturbation,
and two exact-geometry cached light changes per geometry. Geometry, acceleration,
normals and evidence tracing are explicitly combined where the implementation
cannot honestly separate them. Warm light-only performance is not charged to
geometry-changing optimization. Runtime scenarios are planning assumptions only.
