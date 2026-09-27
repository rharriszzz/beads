# Photo-2 reconstruction plan

Start: origin/master 020303ec16c81cb62802b6ae718adda9bbc2fdfa, the default branch.
Working branch: photo-2-reconstruction-v2. Python 3.12 and POV-Ray.

One aspect at a time; offer 3–6 implementation methods at each phase and use
short illustrated feedback rounds. A phase boundary is a reviewable result,
not automatic authorization to select all later methods.

| Aspect | Intended result | Status |
| --- | --- | --- |
| Paper versus necklace | Paper includes cast shadow and visible gaps; uncertain border retained | Five options and initial local FFT probe ready for review |
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

Next bounded task, refined by R095: compare progressively smaller FFT windows
and spatial texture cues along a few short paper/shadow/necklace transitions.
Question 2 has a working direction; question 1's Gaussian definition remains
provisional. Show raw/annotated pairs, explain the sampling routes, and show
uncertainty. Stop for review before fitting a whole-image contour or spline.
R097 refinement: compare DC-only versus finite central-peak exclusion, absolute
retained power and retained fractions (with explicit denominators), using paper
controls. Show excluded frequencies; do not tune the metric only on successful
examples or equate an uncalibrated score with a background probability.
If feedback is absent, keep the radius interpretation provisional and restrict
work to independent controls and clearly labeled alternatives.
