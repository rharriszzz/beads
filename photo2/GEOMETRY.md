# Fixed-observation geometry comparison — R014

The 103 provisional bead-center/color annotations in `geometry-labels.json`
support an **inconclusive** local geometry comparison. Neither hand nor the
circumference count is accepted. The scene settings remain the Step 1 baseline.

## Reproduce

```sh
.venv/bin/python photo2/fit_geometry.py
.venv/bin/python -m unittest discover -s photo2 -p 'test_*.py' -v
```

The first command writes `output/geometry-fit/report.json` and six four-panel
`*-comparison.png` files: source, labeled source, negative-hand fit, positive-hand
fit. Cyan circles are annotations; green crosses are assigned model centers;
white segments are residuals. It records hashes of the image, centerline,
annotations and implementation, library versions, seeds, bounds, all optimized
parameters, optimizer termination, assignments and errors. All generated files
are ignored. The default seeds are 17 and 43, maximum 600 differential-evolution
iterations, population multiplier 10, tolerance 1e-7, without polishing.

## Observations and holdout

Annotations were visually estimated from enlarged unwrapped photo crops before
fitting, without predicted positions. They are assistant annotations, **not
human-reviewed ground truth**. Coordinates use the existing spline's arc length
and signed normal displacement. Typical center uncertainty is estimated at four
source pixels, with worse uncertainty possible for dark, blurred or edge beads;
this is neither a calibrated standard deviation nor a hard error bound. Colors
are provisional visual labels and do not enter this geometric objective. All
original chain indices are null. The dataset does not claim completeness.

| Patch | Start arc (px) | Shape | Centers | Use |
| --- | ---: | --- | ---: | --- |
| straight_a | 200 | straight | 18 | training |
| bend_b | 3920 | bend | 16 | training |
| bend_c | 5450 | bend | 17 | training |
| bend_a | 1850 | bend | 17 | validation |
| straight_b | 4520 | straight | 18 | validation |
| straight_c | 7000 | straight | 17 | validation |

Each patch covers 160 arc pixels. Training uses 51 centers to fit shared pitch,
beads/turn and center-cylinder radius, plus three alignment parameters per patch.
On the other three patches, only the 25 centers with local x<80 calibrate axial
alignment, angular phase and normal offset; shared geometry stays frozen. The
remaining 27 centers with x>=80 are withheld for extrapolation. Assignments for
calibration are fixed before matching withheld centers to unused model sites.
Both hands use precisely the same labels, calibration split and search budget.
Selection between seeds uses training error only.

This is **partial patch holdout**, not prediction of wholly unseen patches with
no local alignment. Absolute phase cannot be carried between these separated
patches without a trusted intervening index/twist model. No such model is assumed.

## Model and conditional results

For local integer site k, hand h, axial fraction q, pitch p, beads/turn b,
phase phi, center-cylinder radius r and normal offset o:

```text
x_k = (k + q) p / b
angle_k = h 2 pi k / b + phi
n_k = o + r sin(angle_k)
visible candidate if cos(angle_k) >= 0
photo position = C(start + x_k) + n_k N(start + x_k)
```

The first fit minimizes mean squared distance in unwrapped coordinates, with
one-to-one assignment between annotations and predicted centers. This assignment
is a local registration device, not nearest-neighbor chain tracing or recovered
bead order. Extra model sites receive no penalty because the labels are
incomplete. This is a serious density bias: a denser candidate can match more
arbitrary points. Search bounds are p=18–32 px, b=5–9, r=22–55 px, q=0–1,
phi=-pi–pi, o=-20–20 px. These are exploratory domains, not measured priors.
The model does not enforce global closure or physical non-intersection.

| Hand | Pitch px | Beads/turn | Radius px | Training RMSE px | Withheld RMSE px | Original-photo withheld RMSE px |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| -1 | 18.5045 | 8.9691 | 33.0595 | 5.9696 | 6.2728 | 6.2698 |
| +1 | 22.0267 | 8.5342 | 48.2992 | 3.9479 | 6.4124 | 6.4141 |

The positive-hand seed 17 solution instead has p=22.0929, b=8.9030, r=32.0825,
training RMSE 5.0904. Negative-hand seed 43 gives 6.0152 px. All four optimizers
reported numerical convergence, which does not prove a global optimum. The
competing solutions, high count near the bound and large radius variation prevent
interpreting these parameters as measured necklace dimensions.

| Withheld patch | Hand -1 RMSE px | Hand +1 RMSE px |
| --- | ---: | ---: |
| bend_a | 6.3856 | 3.8838 |
| straight_b | 5.7287 | 5.3223 |
| straight_c | 6.7330 | 8.8585 |

The pooled difference is only 0.1396 px in unwrapped coordinates and reverses the
training preference. Patch preferences vary; the gap is much smaller than the
estimated annotation scale. This is not a statistical confidence test, and no
sign is selected. Original-photo residuals closely match unwrapped residuals
for these fits; that checks the metric transformation, not camera adequacy.

## What the data cannot identify

Allowing linear local twist adds `tau (x_k - 80) / 160` to the angle. Let d=p/b.
For any replacement b', define:

```text
p' = d b'
tau' = tau + (160/d) (h 2 pi/b - h 2 pi/b')
phi' = phi - (tau' - tau) (q d - 80)/160
```

Both x and angle are unchanged at every k. Consequently all projected centers
and the front-half visibility mask are identical. Pitch, count and unconstrained
linear twist cannot be fitted independently from these observations. The
numerical gauge test verifies this equality to 1e-10 px. Reported fits fix twist
to zero to choose one parameterization; they do not measure actual zero twist.
Physical thread connectivity or independently constrained twist would be needed
to interpret pitch and count separately.

Without a front/back visibility restriction, replacing h with -h and phi with
pi-phi preserves every projected center because sin(pi-angle)=sin(angle), while
reversing depth relative to the center cylinder. The front-half assumption breaks
that exact symmetry, but real bead occlusion is not represented by this cutoff.
A numerical test verifies the unrestricted ambiguity and a known synthetic
front-only lattice distinguishes hands when global geometry is fixed.

Hole-axis tilt does not appear in these center equations: every tilt has the
same objective. No reliable paired hole rims were annotated. Body elongation in
an unwrap cannot simply be called a measured hole axis. Bead dimensions, total
rope width and perspective adequacy likewise need outline/occlusion evidence;
r is the radius of the **center cylinder**, not the outer rope radius. None of
these missing quantities is filled with an invented estimate.

## Boundary and next experiment

This completes the bounded comparison at an evidenced ambiguity, not PLAN Step 2
as a whole. No scene defaults, POV-Ray materials or repeat candidates are updated.
Nine tests pass: the prior five plus one-to-one assignment, projected-hand
ambiguity, pitch/count/twist degeneracy, and a noisy known front-lattice hand
check. The latter is a center-level test, not a rendered-image recovery test.

Next: build a small POV-Ray synthetic patch benchmark with known bead IDs,
body dimensions, hole-axis tilt and true occlusion for both hands. Python should
score visible centers and body outlines and test density bias and missing labels.
Stop after a reproducible benchmark determines which geometry observations can
separate the known alternatives, or records why they cannot. Do this before
refitting real-photo geometry or resuming repeat inference.
