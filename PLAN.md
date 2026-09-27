# Photo-2 reconstruction plan

Start: origin/master 020303ec16c81cb62802b6ae718adda9bbc2fdfa, the default branch.
Working branch: photo-2-reconstruction-v2. Python 3.12 and POV-Ray.

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
| Paper versus necklace | Paper includes cast shadow and visible gaps; uncertain border retained | R099 texture comparison plus R100–R102 T1/T2 hue clues and confirmed overlapping HSV-map history; exact edges unresolved |
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

Next bounded task: incorporate [visual feedback](photo2/TRANSITION_QUESTIONS.md),
then compare hue and texture on a few nearby parallel routes with paper controls.
Preserve the T3 dark-bead failure and test whether reported crossing spreads
remain stable. Stop for illustrated review before connecting any crossings into
a full contour or fitting centerline/scene parameters. If answers are absent,
proceed with controls and provisional labels; do not invent maker edge locations.
