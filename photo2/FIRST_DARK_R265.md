# R265 follow-up — stop at the first neutral dark pixel

User steering: stop on black without seeking a subsequent bright region; black in
the photograph need not have HSV value zero, and black-bead shading progresses
through gray. This is one additional bounded step after the
[straight-growth/retreat comparison](DETECTION_REPAIR_R265.md).

Three evidence types are kept distinct: neutral gray progression, absolute darkness,
and contrast relative to the seed. The additional stop uses **V in DN ≤min(81, .5×seed peak) plus neutral
appearance**: S≤.25 or channel spread S×V×255≤12 DN. Hue is unreliable near gray and
is not used to define black. These operational tolerances allow nonzero, imperfect
grays; they do not identify physical material. Complete straight paths now report
the fraction of neutral samples, and stopped paths report the blocker's neutrality
and preceding gray fraction.

Previously, a neutral30-DN pixel could be accepted from a60-DN seed because
the reflection-drop condition required36 DN of contrast. That exception is removed
for neutral black pixels. Nonzero dim gray reflections remain eligible seeds. Dark
chromatic samples retain the existing relative-dark stop; they are not silently
called black. No pixel beyond the first blocked point on a straight path is used
to justify accepting that target. Tests explicitly include nonzero neutral dark pixels at half the seed peak,
several irrelevant hue angles, a later bright patch, and a dark red counterexample.

A preliminary absolute81-DN gate incorrectly removed a visible60-DN gray reflection
P050477. The curated raw crop exposed the regression, so the final black cutoff is
capped at half the seed peak. The rejected draft is preserved for comparison.

The four meaningful seeds at or below81 DN have visible chroma: their RGB samples
are(80,51,56), (60,47,54), (60,41,45), (77,47,55). This prevents treating all four as
verified black just because they are dim. Native before/after crops are saved.

## Residual failure diagnosis

The paper-edge seeds P127165/P127225/P126974 have a clipped red channel255,
saturation around.53 and hue about329°–339°. The learned paper center is about312°,
S=.509,V=.843; their3×3 neighborhoods fail both its hue and value intervals even
though saturation agrees. Thus the conservative HSV gate preserves them. A global
wider hue rule would also admit/reject real colored material ambiguously. The
paper-window regression is therefore **not repaired by stopping on gray-black**.
These are image-derived diagnostics; the saved paper window/IDs are evaluation
references, never runtime priors.

The persistent missed landmarks still have nearby maxima below prominence35;
stopping or retreat cannot invent those missing seed proposals. Duplicate peaks
also persist. No whole-photo one-coordinate-per-bead success is claimed.

## Reproduce

```sh
MPLCONFIGDIR=/tmp/beads-r265-mpl .venv/bin/python -m photo2.bead_detection.first_dark_r265 --seconds 300
.venv/bin/python -m photo2.bead_detection.server
```

The delivered run also used `--deadline-from photo2/review/r265/checkpoint.json`,
so it shared the original absolute30-minute deadline. The default viewer now uses
`photo2/output/r265-first-dark/joint`. Its historical v1 counterpart remains
available with `--work photo2/output/r265/joint`, backed by the preserved
`straight_detect_r265.py`. Full data, native crops, traces, parameters, audits and
logs are under [review/r265-first-dark](review/r265-first-dark/README.md).

Stop after this additional delivery. Next task: review residual paper-edge seeds,
missed seed evidence and same-body peak association before another algorithm phase.
Keep the current model/reasoning choice; no `/new` for review, use `/new` before a
substantial new phase.

## Final measured outcome

64 Python tests pass. The full-photo audit checks107269 acceptances and226364 stops against the first-neutral-black invariant. Final retained supports:1556; changed masks:0; moved coordinates:0; lost/added IDs:0/0. These are support changes, not bead accuracy. The reviewed paper window remains7 pixels. Complete numerical results and the rejected absolute-threshold draft are preserved in the evidence folder.

The final44 Chromium checks pass, and both v1/v2 viewer preparations reuse their
saved data without regeneration. The additional rule removes8 pre-retreat dark
acceptances while preserving every final mask/coordinate, including P050477. This
is a stopping-semantics correction, not a new photographic accuracy improvement.
