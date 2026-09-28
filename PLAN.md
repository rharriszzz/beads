# Photo-2 reconstruction plan

Start: origin/master 020303ec16c81cb62802b6ae718adda9bbc2fdfa, the default branch.
Working branch: photo-2-reconstruction-v2. Python 3.12 and POV-Ray.

R106 documentation detour completed: [initial question and construction facts](INITIAL_QUESTION.md)
and [reusable methods collection](METHODS.md). The catalog proposes five background
methods under varying illumination, with failures and validation plans. No new
classifier or contour was implemented. All supplied images place the bracelet
centrally with substantial margins; use that generic prior for background seeds,
not fixed bead coordinates or a prescribed border width. Enclosed paper/gaps need
support beyond exterior connectivity. The anchor/bridge experiment below remains
the next bounded numerical task; this detour did not run it.

One aspect at a time; offer 3–6 implementation methods at each phase and use
short illustrated feedback rounds. A phase boundary is a reviewable result,
not automatic authorization to select all later methods.

R103 generality constraint: final inference should use little image-specific
color or bead-location knowledge. Current fixed routes, paper reference centers
and historical HSV boxes are diagnostic fixtures only. The eventual pipeline
must estimate background statistics and necklace location from the supplied
image; color cues should use local differences or image-derived models, not
hard-coded red beads/magenta paper. Validate on changed palettes/backgrounds and
translated/rotated placements, keeping manually reviewed cases separate from
the algorithm's inputs. These generalization tests have not yet run.

| Aspect | Intended result | Status |
| --- | --- | --- |
| Paper versus necklace | Paper includes cast shadow and visible gaps; uncertain border retained | R104 hue trend survives ±8 px; hue maxima and reference-scaled texture crossings remain unreliable as edge rules |
| Lighting and paper appearance | Independently parameterized paper pigment; lighting constrained by shadows and specular reflections | Deferred; research primary sources when this phase starts |
| Planar centerline and camera | Spline matching physical arrangement, with global plane/camera view | Deferred; old spline is reference, not ground truth |
| Bead locations and exposed shapes | Occlusion-aware 3D candidates with missing/hidden observations | Deferred; offer methods before fitting |
| Colors and POV-Ray materials | Pigment/finish/normal/interior separated from lighting effects | Deferred |
| Helicity and spacings | Band-pass FFT peaks for directions 1/6/7; direction-1 angle relative to local centerline | R098 maker method saved; deferred with synthetic sign/convention validation |
| Repeating pattern | Competing sequences of length 200–400 with explicit uncertainty | Deferred; no photo-2 sequence established |

The phases can require revisiting shared parameters; lighting and material are
coupled. Background color is a configurable scene property, never a fixed rule
that determines foreground membership. Preserve legacy beads.pov while methods
are reviewed; add a configurable photo-2 mode once supported scene inputs exist.

For the later directional FFT phase, use [the R098 method and display plan](photo2/PRIOR_WORK.md#r098--makers-directional-fft-method):
retain a bead-spacing frequency band, label peak pairs, and show their relationship
to a tangent-aligned image patch. Compare the direction-1 relative angle for known
opposite helicities before assigning the photograph's hand. This preserves the
maker's proposed angular rule without treating the background-energy probe as
an implemented direction estimator.

R099 completed the bounded transition comparison: 48/24/12/6-pixel windows,
DC-only/finite exclusions, raw/detrended power fractions, spatial texture and
paper references. [Findings and limitations](photo2/BACKGROUND_TRANSITIONS.md).
Small windows narrow the texture response but have not established an edge rule.

R100–R102 adds [hue measurements and confirmed HSV-map provenance](photo2/HUE_TRANSITIONS.md).
Overlap does not eliminate useful hue transitions; white-balanced presets must
not be applied to the original JPEG without a new calibration.

R104 completes the [parallel-route/reference sensitivity comparison](photo2/PARALLEL_PATHS.md).
Largest hue changes can mark internal bead colors/highlights; changing paper
reference moves texture crossings by up to 32 pixels. No contour points selected.

R105 supplies the next strategy: move farther along the necklace in either
direction until boundary evidence is reliable; bridge ambiguous stretches with
a smooth large-scale envelope, keeping bead-scale scallops separate.

Next bounded task: expand one ambiguous neighborhood along the necklace, show
candidate reliable boundary anchors on either side and compare a short smooth
bridge with the raw image. Compare local cubic interpolation, a robust smoothing
spline, and coupled inner/outer envelopes as implementation options. Start with
the simplest local bridge if evidence supports its endpoints. Show anchor evidence
separately from inferred spans and sensitivity to anchor choice; leave unsupported
spans unresolved. Stop for review before whole-necklace contour adoption,
centerline/scene fitting or bead assignments. Diagnostic crops remain validation
fixtures, not runtime priors. The earlier proposed whole-image search is deferred
to follow the maker's more specific guidance.
