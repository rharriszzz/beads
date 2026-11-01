# Reusable graph paper for 6.5-bead crochet

[Project](../README.md) · [Module](../beadwork/graph_paper.py) · [Independent tests](../tests/test_graph_paper.py)

This standard-library tool lays out a **supplied sequence**. It needs no photograph,
scientific archive, classifier, or renderer. It does not infer colors or physical
bead identities. The circumference is specifically 6.5 beads per turn; arbitrary
repeat lengths do not mean arbitrary circumference.

## Coordinates

Use integer lattice coordinates `(a,b)` with `k=7a+6b`. Define `x=a-b`, `y=a+b`,
so `2k=x+13y`. Valid sites have matching x/y parity. Mathematical y increases
**upward**; screen renderers invert y.

| Direction | Display step | Index step |
|---|---|---:|
| Right | `(2,0)` | +1 |
| Up-left | `(-1,1)` | +6 |
| Up-right | `(1,1)` | +7 |

One horizontal bead pitch is two x units. The canonical strip `-1<=x<12` has
six centers on even rows and seven on odd rows. Two rows contain thirteen beads.
For any integer k, including negative values, its unique representative is:

```python
x = x0 + ((2*k-x0) % 13)
y = (2*k-x) // 13
```

The zero-index lateral seam is `(Δa,Δb)=(6,-7)`, or **`(Δx,Δy)=(13,-1)`**.
A rightward same-k copy goes one row down. Side extensions follow actual
horizontal +1 steps, normalizing through as many seams as necessary.

Every default row has exactly **7 left + 6/7 basic + 7 right = 20/21 symbols**.
On row y=1, basic k=6..12 is surrounded by k=-1..5 and k=13..19. The two extreme
copies require *two* seams. Pasting a whole neighboring strip misses the seventh
continuation on seven-bead rows.

## Use with any sequence

From the repository root, with Python 3.10+:

```python
from beadwork.graph_paper import pattern_layout

paper = pattern_layout('BRYBRYBRYBRYBRYB?',
                       'BRYBRYBRYBRYBRYBY', start=5, x0=-1)
chosen = [p for p in paper['points'] if p['in_chosen_interval']]
assert sorted(p['k'] for p in chosen) == list(range(5, 22))
assert len(chosen) == 17
```

`R`, `Y`, `B`, `?` strings (whitespace ignored), or lists of full lowercase color
names, are accepted. Unknown strict colors remain `?`; an optional provisional
sequence is stored separately. The two sequences must have equal length. The
first supplied position belongs at `start`, with position `(k-start) mod L`.

The CLI emits JSON without writing files itself:

```sh
python3 -m beadwork.graph_paper 'BRYBRYBRYBRYBRYB?' \
  --provisional BRYBRYBRYBRYBRYBY --start 5 > /tmp/pattern-layout.json
```

`layout(length,start=0,x0=-1,extension_rows=8,minimum_rows=40,side_beads=7)`
returns geometry alone. `representative`, `boundary` and `strip_sides` are
also public. Integer arguments reject fractional values and booleans. Length
must be positive; context and side counts must be nonnegative. `side_beads=0`
is a basic-strip diagnostic; standard output uses seven.

Every point retains unwrapped k, pattern position, a/b, x/y, canonical x/y,
seam multiplier, row slot, side, repeat-copy number, selected membership and
both color interpretations. Two meanings of copy must stay distinct:

- A lateral copy has the **same k** and canonical identity.
- A repeat copy has k changed by a multiple of L and the same pattern position.

Neither is an additional photographic observation. Count the chosen repeat
using `in_chosen_interval`, never all displayed points.

## Partial rows, boundaries and drawing

Two solid staggered side outlines separate the basic strip from side copies.
Each side follows `first_x-1` or `last_x+1` between `y-.5` and `y+.5`, joining
successive rows horizontally. They are distinct from the START and END cuts
before `start` and `start+length`.

For a cut before T, find its representative `(x,y)`. If T begins a row, the cut
is horizontal at `y-.5`. Otherwise it steps at `x-1`, from `y+.5` on the left to
`y-.5` on the right. This encloses partial rows correctly. For S=5/L=17, the
cuts step at x=9 and x=4 and include exactly k=5..21. A rectangle would be wrong.

Any repeat translation has `(Δx,Δy)=(2L-13t,t)` for integer t. A purely vertical
translation exists only when 13 divides L; an aligned 208 repeat occupies 32
rows. The conditional photographic H maps to `(13,415)=13*(0,32)+(13,-1)`.
That algebra is not a physical count measurement.

Use equal ellipse dimensions for all colors: the historical display uses x/y
scales 24/32 and radii 18/14. These leave room for stepped cuts and side outlines.
`scripts/build_site.py` demonstrates an SVG presentation with mathematical y up,
thin non-scaling boundaries, unknown labels and separate tentative marks.

## Provenance and maintenance

Extracted from [R344 graph_paper.py](https://github.com/rharriszzz/beads/blob/628351437842b2ecd05f8a1765d17449fbea61f9/photo2/r344/graph_paper.py).
The geometry and output fields are retained; historical `common`/file I/O is
removed, explicit input checks and a CLI added, and code reformatted. No original
research file or test was edited. A bounded extraction check compares complete
output dictionaries with the original API across its 192 documented cases.
The maintained tests independently enumerate lattice sites and verify directions,
negative indices, double seams, copies, all seven extensions, membership and
ellipse clearance at partial-row cuts.

The original [general specification](https://github.com/rharriszzz/beads/blob/628351437842b2ecd05f8a1765d17449fbea61f9/photo2/GRAPH_PAPER_6_5_BEADS.md)
and [historical verifier](https://github.com/rharriszzz/beads/blob/628351437842b2ecd05f8a1765d17449fbea61f9/photo2/r344/verify_graph_paper.py)
remain the detailed research references. Their statistical checks are deliberately
not dependencies of this small reusable tool.
