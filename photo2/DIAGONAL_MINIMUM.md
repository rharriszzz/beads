# Diagonal steps, conditional guarantees and visibility — R162–R163, R165

**There is no universal minimum based only on how many visible beads are labelled.**
The earlier geometric one-extra-bead scale is seven direction-6 steps versus six
direction-7 steps, from the [outward-angle calculation](PATCH_SUFFICIENCY.md).
Arbitrary interior points, uncertain camera geometry and hidden bodies can leave
both families feasible. Both did fit the old 27-body photo patch and its confirmed
interiors. The new 40-body geometry has not yet been tested.

**R166: inference stays photo-only.** The original necklace is not needed for
the planned analysis. Do not ask for hidden-body labels or physical inspection
to make a conditional mathematical test observable. Use substantial visible
central bodies, including black, and test both candidates against photo evidence.

There is, however, an **exact conditional test** using bead identity at the ends
of two forward diagonal paths from the same bead. It requires **seven steps in
one diagonal and six in the other**, not seven in both. The earlier seven-in-both
recommendation was a conservative coverage target before checking this identity
criterion. These counts are links: seven steps contain eight bead positions.

Consider three ways to establish a stopping rule: accumulated angle/spacing
difference, exact path endpoint identity, or a calibrated competing-pose size
sweep. The first gives a scale; the third gives empirical evidence with stated
uncertainty. The second supplies the conditional algebraic guarantee below.

## The exact endpoint test

In the adopted construction, one forward diagonal advances bead_index by 6 and
the other by 7. For two paths to reach the same index, their step counts satisfy
6*m=7*n. Since 6 and 7 are coprime, the smallest positive solution is **m=7,n=6**,
meeting at relative index **42**. There are 13 links in the combined paths.

| Paths from a shared start | A endpoint index difference | B endpoint index difference |
| --- | ---: | ---: |
| 6 steps in d2 versus 7 in d3 | 6×7−7×6 = 0 | 6×6−7×7 = −13 |
| 7 steps in d2 versus 6 in d3 | 7×7−6×6 = +13 | 7×6−6×7 = 0 |

Thus, for the first test, **same end bead selects A; different end beads select B**.
The second test reverses that conclusion. Global index reversal changes the
nonzero sign but does not change zero versus nonzero. A complete test contains
13 distinct beads if the paths meet, or 14 if they do not; the paths always share
their start. Thirteen is the minimum for this particular two-forward-diagonal
closure test, not an absolute minimum for every conceivable helicity method.

The guarantee depends on all of these facts:

- Each recorded link is exactly one consecutive neighbor step in its named
  direction; a skipped or misidentified bead invalidates the count.
- Both paths share a known bead and follow the same forward major-circle sense.
- Endpoint identities are known, including whether two marks name the same body.
- The necklace contains more than 13 beads, so a difference of 13 cannot be a
  full-necklace wrap. The maker's 40 distinct-body inventory supplies this lower
  bound if those identities are correct; exact total N is not required.

Under these assumptions this decides the remaining signed 6/7 family; translating
it to a helicity name retains the established direction/view convention. It is
not a guarantee that the entire required path is exposed in one photograph.
Other tests involving d1 or geometric measurements may use fewer bodies.

The current save has maximum runs of five steps in each diagonal. Its 47 local
triangle cycles span the entire graph cycle space, and both relative-index maps
are injective. Consequently neither family has a closure or identity conflict
in the supplied graph. Do not extend the local integer chart blindly through a
minor-circle wrap: such a valid nonlocal cycle can violate the planar chart while
closing exactly for one weighted index family. Preserve and test that witness
instead of deleting its links as mistakes.

## Modulo 13 for an approximate visibility phase

**42 mod 13 = 3.** At nominal q=6.5, thirteen thread indices make two turns
around the minor circle. Therefore the relative phase can be estimated from r=k mod13:

```text
minor_phase(k) ≈ starting_phase + h * 720° * r/13  (mod 360°)
r=3: relative phase ≈ h * 166.153846°
```

Here k is a supported relative index, not a maker number, and h is the winding
sign. Direction +6 moves about −27.692308° around the minor circle for h=+1;
+7 moves about +27.692308°. Reverse winding reverses those signs. This makes
mod13 useful for selecting likely central/exposed positions once the starting
phase and local view are known.

The starting phase, camera and local centerline tangent still determine which
side faces the camera. Neighbor occlusion additionally matters. A bead body
may be partly visible while its minor-outward point is hidden. If the start's
outward point faces the camera, an endpoint about 166° around the tube is likely
on the far side. Do not require those hidden intermediate beads to be labelled.

For q≠6.5, use h*360°*k/q rather than reducing k modulo 13 exactly. Within the
existing q6.45–6.55 sensitivity bounds, the exact phase at k42 differs from the
nominal value by about +18.03°/−17.76°, material near a visibility edge. This is
an approximate geometry phase, **not a 13-bead color repeat or a restriction on N**.

**Stopping point:** nominal scale and exact conditional identity test are distinct.
**Next task:** test the expanded saved patch before requesting more labels;
use residue phase to help preserve hidden/edge exclusions, not to force visibility.
Recommend gpt-6.1-sol / High; same session, no /new needed.
