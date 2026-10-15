# The sine angle in `beads.pov`

The original radius formula appears to mix degrees and radians. With the supplied
parameters it produces a bead radius of **2.110916** rather than the likely intended
**1.784537**, or **18.2893% larger**. This document records the source behavior and
its consequences. It does not change `beads.pov`, the Python geometry, or any saved
experiment, and it does not establish the dimensions of the photographed necklace.

## What the source actually evaluates

At [line 154 of the checked source](https://github.com/rharriszzz/beads/blob/c7dea2c6c76663532ddb2a5b51d2ce5c13fe64d9/beads.pov#L148-L157):

```pov
#declare chain_minor = 4;
#declare bead_radius = chain_minor * 0.96 * sin(180 / beads_per_row);
```

All eight pattern cases set `beads_per_row = 6.5`. POV-Ray's `sin()` takes its
argument in **radians**; it does not interpret `180` as half a turn. This is stated
in the official [Float Expressions documentation](https://www.povray.org/documentation/view/3.60/228/).
The likely intended declaration is:

```pov
// Proposed interpretation only; the original source remains unchanged.
#declare bead_radius = chain_minor * 0.96 * sin(pi / beads_per_row);
```

Equivalently, the sine argument could be `radians(180 / beads_per_row)`.
For 6.5, the intended half-angle is 27.6923077 degrees, or 0.483321947 radians.
The original expression instead evaluates the sine of 27.6923077 **radians**.
After removing four full turns, that is 2.559566464 radians, about 146.652356 degrees.
Its sine happens to be positive and moderately sized:

```text
sin(180 / 6.5) = 0.549717642948272
sin(pi  / 6.5) = 0.464723172043769

legacy radius   = 4 * 0.96 * 0.549717642948272 = 2.110915748921366
intended radius = 4 * 0.96 * 0.464723172043769 = 1.784536980648071

legacy / intended                    = 1.182892689707538
100 * (legacy / intended - 1)         = 18.2892689707538%
100 * (1 - intended / legacy)         = 15.4614777231194%
```

Thus 18.3% means the excess relative to the intended radius. Changing from the
legacy radius to the intended one would reduce the legacy radius by 15.46%.
The radius is not larger by the degrees-to-radians factor 180/pi: the mistaken
argument is passed through a periodic sine function.

## The likely geometric intention

For neighboring centers on a circle of radius `chain_minor`, separated by an angle
`2*pi/q`, their chord distance is:

```text
center chord = 2 * chain_minor * sin(pi / q)
```

If bead diameter is 96% of that chord, then bead radius is
`0.96 * chain_minor * sin(pi/q)`, exactly the proposed interpretation. With
`chain_minor=4` and `q=6.5`, the chord is 3.717785376 and the intended diameter is
3.569073961. The factor 0.96 plausibly provides a small nominal clearance.

This is a geometric inference about the author's intention, not a recorded author
confirmation. The actual construction is a helix of rounded, hole-bearing beads,
not a single ring of spheres. The value 6.5 is a nominal beads-per-turn value; the source
rounds the number of rows and uses `exact_beads_per_row` for placement. Axial
advance, bead orientation, curvature and neighboring turns also affect contact.
The chord argument alone does not prove physically valid packing.

## Why the original images still rendered and looked reasonable

The original formula is legal numerical input and gives a positive radius for the
supplied parameters. A ray tracer renders the resulting surfaces; it does not
check whether the formula expresses the author's intent or whether neighboring
beads form a physically possible necklace. Rendering success and a plausible
appearance therefore do not certify the dimensions or the absence of intersections.

Several source relationships preserve much of the visual organization:

1. **The individual beads retain their shape proportions.** In the `bead` macro
   (lines 169–205), `bead_actual_radius` scales the annular dimensions, hole and
   axial half-height. At fixed material, roundedness, height ratio and relative
   size, a larger radius makes the same bead shape larger. For example, hole
   radius remains 0.14 times actual bead radius.
2. **The major necklace radius grows with bead size.** Lines 155–157 define
   `bead_maximum_height = 0.65 * 2 * bead_radius` and
   `chain_major = bead_maximum_height * 1.05 * nrows / (2*pi)`.
   At a fixed bead count, both this major radius and its centerline circumference
   grow by 18.2893%. The nominal row advance
   `2*pi*chain_major/nrows = 0.65*2*bead_radius*1.05` grows by the same factor.
   Large beads are therefore placed around a larger major loop rather than simply
   being enlarged at completely fixed centers. The 0.65/1.05 factors specify row
   advance; they are not a general proof of bead clearance.
3. **The angular sequence is unchanged.** Lines 149–151 derive bead count, rounded
   row count and exact beads-per-row independently of radius. Lines 305–311 use
   `360*(bead_index/nbeads + rclock*0.1666)` and
   `360*(bead_index/exact_beads_per_row + rclock)` for major and minor placement.
   Those angles correctly feed degree-based `vaxis_rotate` and `rotate` operations;
   their unit conventions differ from `sin()`. See the official
   [vector-function documentation](https://www.povray.org/documentation/view/3.6.1/229/)
   and [rotation documentation](https://wiki.povray.org/content/Reference:Transformations).
   The order, color-pattern assignment and number of minor turns remain intact.
4. **This is not a uniform scaling of the whole scene.** `chain_minor` stays 4, so
   beads become larger relative to the tube-center circle. The nominal transverse
   envelope `2*(chain_minor+bead_radius)` grows only about 5.64%. Minor-angle
   center-to-center chord spacing is unchanged at fixed angular separation,
   while major-loop/axial advance changes. Consequently, relative packing,
   occlusion and visible extents change. The vertical translation
   `chain_minor + 2*bead_radius` also changes. Camera and light coordinates remain
   fixed, so framing, perspective and illumination need not be identical.

For a concrete source example, the default `clock=0` selects pattern 1:
`nbeads=28*24=672`, `nrows=floor(0.5+672/6.5)=103`, and
`exact_beads_per_row=672/103=6.524271845`.

| Quantity, source units | Original / `legacy` | Likely intended |
|---|---:|---:|
| Bead radius |2.110916|1.784537|
| Bead diameter, relative size 1 |4.221831|3.569074|
| Tube-center radius `chain_minor` |4.000000|4.000000|
| Nominal transverse envelope diameter |12.221831|11.569074|
| Row advance `0.65*2*radius*1.05` |2.881400|2.435893|
| Major radius for 103 rows |47.234672|39.931494|
| Vertical translation `4+2*radius` |8.221831|7.569074|

The transverse envelope is a geometric scale description, not an exact discrete,
occluded photographic silhouette. A recognizable loop, regular angular winding,
familiar bead shapes and the same colors can survive these dimension changes.
This explains plausibility; no new render comparison is claimed here.

## Python conventions and experiment provenance

[`photo 2/bead_placement.py`](https://github.com/rharriszzz/beads/blob/c7dea2c6c76663532ddb2a5b51d2ce5c13fe64d9/photo2/bead_placement.py)
provides explicit alternatives in `Rope`:

```python
radius_convention: str = 'legacy'
# In bead_radius:
angle = 180 if self.radius_convention == 'legacy' else np.pi
return self.chain_minor * .96 * np.sin(angle / self.beads_per_row)
```

`legacy` is still the default, preserving literal source behavior and old results.
`intended` must be requested explicitly. Both conventions propagate their radius
into `chain_major`; surface sampling uses the selected radius. `nrows`,
`exact_beads_per_row`, and the angular formulas in `coordinates()` do not change
merely because the radius convention changes. Some later experiments separately
vary pitch, camera, axis shape or orientation; the convention alone does not
describe all their geometry.

The option was introduced in
[R278 commit d7c8407](https://github.com/rharriszzz/beads/commit/d7c8407f5774ff38fcb723d53f70a42c399b3f35),
while retaining the default. Source-checked examples, rather than a claim that
every numbered experiment performed geometry fitting:

| Experiments | Radius convention and source evidence |
|---|---|
| [R253 global fitting](https://github.com/rharriszzz/beads/blob/c7dea2c6c76663532ddb2a5b51d2ce5c13fe64d9/photo2/GLOBAL_GEOMETRY_R253.md) | Legacy 2.11091575. `global_fit_r253.py` imports `tangent_circles.RADIUS`, defined by default `Rope(2698).bead_radius`. |
| [R258 bead-driven geometry](https://github.com/rharriszzz/beads/blob/c7dea2c6c76663532ddb2a5b51d2ce5c13fe64d9/photo2/BEAD_DRIVEN_R258.md) and [R276 reconstruction](https://github.com/rharriszzz/beads/blob/c7dea2c6c76663532ddb2a5b51d2ce5c13fe64d9/photo2/RECONSTRUCTION_R276.md) | Legacy source-radius family through the debugger/surface helpers. R258 explicitly preserves `sin(180/6.5)`; later packing/metric controls are separate geometry adjustments. |
| [R278 construction comparison](https://github.com/rharriszzz/beads/blob/c7dea2c6c76663532ddb2a5b51d2ce5c13fe64d9/photo2/RECONSTRUCTION_R278.md) | Explicit comparison of both conventions; new intended-radius candidates plus preserved legacy controls. `construction_r278.radius()` defaults to `intended`; model records retain the convention. |
| R279, R280–R283, R289's synthetic landmark-transfer scenes, and R294 | Intended 1.78453698. [`r279/geometry.py`](https://github.com/rharriszzz/beads/blob/c7dea2c6c76663532ddb2a5b51d2ce5c13fe64d9/photo2/r279/geometry.py) explicitly constructs `Rope(2600, radius_convention='intended')`; the cited later geometry modules reuse its radius. R294 uses real-photo evidence only. |

Historical links are pinned to the verified R294 repository snapshot so they also
work from `master`, which does not contain the experimental `photo 2` tree. No
experimental implementation needs to be merged into `master` to read this document.

## Independent verification without rendering or changing files

From either branch's repository root, run this standard-library calculation. It
reads the original source, checks the supplied constants, and writes no files:

```bash
python3 - <<'PY'
from math import floor, isclose, pi, radians, sin
from pathlib import Path
import re

source = Path('beads.pov').read_text()
assert '#declare chain_minor = 4;' in source
assert 'sin(180 / beads_per_row)' in source
row_values = re.findall(r'#declare beads_per_row\s*=\s*([0-9.]+)', source)
assert len(row_values) == 8 and all(float(q) == 6.5 for q in row_values)

a, q = 4.0, 6.5
legacy = a * .96 * sin(180 / q)
intended = a * .96 * sin(pi / q)
assert isclose(intended, a * .96 * sin(radians(180 / q)), abs_tol=1e-14)
rows = floor(.5 + 672 / q)
for name, radius in [('legacy', legacy), ('intended', intended)]:
    pitch = .65 * 2 * radius * 1.05
    major = pitch * rows / (2 * pi)
    print(f'{name}: radius={radius:.12f}, row_advance={pitch:.12f}, '
          f'chain_major={major:.12f}')
print(f'legacy excess over intended: {100 * (legacy / intended - 1):.9f}%')
print(f'intended reduction from legacy: {100 * (1 - intended / legacy):.9f}%')
PY
```

Expected radii are 2.110915748921 and 1.784536980648; excess 18.289268971%,
reduction 15.461477723%. A calculator in radian mode gives an independent cross-check.
On `photo-2-strategy-v3`, the existing environment can additionally compare
`Rope(672).bead_radius` and
`Rope(672, radius_convention='intended').bead_radius` with those values.
The Python helper is not required for the standalone calculation on `master`.

## Source correction versus photographic dimensions

The language rule and the original numeric result are directly verifiable. The
chord formula strongly supports an apparent programming error, but identifying
that error does not measure the real beads or prove that the smaller dimensions,
unchanged pitch, source shape or a particular camera best match the photograph.

R278's recorded packing audit illustrates the distinction: the intended radius
removed its sampled immediate-neighbor penetration failure, but other neighbor
penetrations remained until additional construction changes were tested. R294
also retains clear photographic mismatches despite using intended-radius models
with nonintersection certificates. Neither pleasant rendering nor a contact
certificate establishes real photographic correspondence.

Future physical fitting should state the radius convention, spacing assumptions,
units and camera separately, preserve alternatives, and compare them with the
unchanged photograph and independent observations. This documentation does not
retroactively correct legacy experiments or settle the photographed necklace's
dimensions.
