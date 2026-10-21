# Why a repeat divisible by 13 can still be decoded

**Divisibility by 13 can make photographic coverage harder, but it does not make
the pattern mathematically undecodable.** In this project the retained observations
cover every position of the proposed 208-bead repeat, so the possible coverage
obstacle did not prevent the current conditional recovery.

## The real reason to worry: repeats can stay on the hidden side

In the ideal 6.5-beads-per-turn construction, 13 beads make two turns around the
tube. A repeat of 13, 26, 104 or 208 beads therefore returns to the same circumferential
alignment. In an ideal rigid, untwisted straight tube seen from one direction,
some pattern positions could remain on the back in every repetition. More copies
of that same view would supply no new information about those positions.

A repeat not divisible by 13 can shift its successive copies through different
circumferential phases, potentially bringing otherwise hidden positions into view.
This can help coverage. It is not a guarantee of decoding: shadows, repeated
colors, wrong row associations and insufficient views can still make it difficult.

That is a visibility/identification issue, not a rule forbidding multiples of 13.
The physical tube can also bend, twist and expose different surfaces. The phase
argument is an ideal construction model, not a measured camera/pose calibration.

## The ordering equations remain usable

For the current A convention, the lattice-to-string map is:

```text
k = 7a + 6b
```

The two primitive neighbor families advance the string index by 7 and 6. Their
difference advances it by 1. Thus the combined lattice relationships connect
consecutive string positions; a factor 13 in the repeat length creates no missing
class of indices. Algebraically, `gcd(6,7,L)=1` for every positive candidate length L.
This does not say that any single photographed direction or isolated patch sees
all positions. It says that the index map itself has no such arithmetic obstruction.

For 208 there is a particularly clear fundamental domain:

```text
u = (6,-7)     changes k by 0      same-index seam identification
v = (16,16)   changes k by 208    proposed pattern repeat
|det(u,v)| = |6*16 - (-7)*16| = 208
```

There are 208 distinct lattice classes in this domain, not just 13. In the
graph-paper coordinates `x=a-b, y=a+b`, v is `(0,32)`: the pattern repeats after
32 alternating 6/7 rows. The repeat lines up neatly with the strip; no positions
are lost because it lines up. More generally, L=13m permits v=(m,m), and the
same determinant is 13m=L. [General strip and seam equations](../GRAPH_PAPER_6_5_BEADS.md)

## Same phase does not mean same color

A 208-bead block contains 16 positions in each of the 13 classes `k mod 13`.
Those 16 positions can have different colors along the tube. Identifying angular
phase alone throws away this longitudinal information. Recovering the lattice
and string addresses lets us retain it.

The data make the distinction concrete:

| Proposed description | Best agreement with 1040 retained colors |
|---|---:|
| Color depends only on 13-bead phase: a length 13 word | 451/1040 = 43.37% |
| Length 104 word | 954/1040 = 91.73% |
| Length 208 word | 1040/1040 = 100% |

Assigning just one color to each angular phase does not fit these observations.
The 104 candidate also has the favorable alignment but still disagrees with 86
observations. Longer color structure along the lattice is needed under the saved
mapping. This does not exclude every possible visibility-related misassociation
under another mapping. [Complete period scan and method](PATTERN_LENGTH_MATCH.md)

## Why the possible obstacle did not defeat this reconstruction

The actual retained dataset collectively covers all 208 residues, and therefore
all 13 phase classes. These measurements are spread around the necklace; they
are not restricted to repeated views of a single straight, fixed-facing segment.
The graph supplies proposed neighbor order, and separate occurrences supply
color redundancy. We can group observations by their actual proposed string
addresses rather than relying on the motif rotating into view on each repeat.

This establishes that phase locking did not leave a wholly unobserved pattern
position in the saved mapping. It does not establish exactly which physical bend
or twist exposed each bead, nor that every physical bead has been inspected.
Seven positions still lack the historical three-region corroboration rule and
remain provisionally black. The original chart, physical count and exact global
topology remain independently unverified. [Current evidence assessment](../r347/answers/ASSESSMENT.md)

Historically, R331 treated the restriction against multiples of 13 as firm and therefore
could not accept the leading 208 candidate. R337 records the clarification to
“I hope it isn't” and removes the hard filter. The later result supports removing
that prohibition; it does not show that aligned repeats can never cause ambiguity.
[Historical analysis](../R331_REPORT.md), [clarification and lattice domain](../R337_REPORT.md)

The useful rule for another object is: **check whether reliable observations cover
the pattern positions and distinguish competing orderings. Use phase alignment
to anticipate gaps, rather than excluding a repeat length in advance.**
