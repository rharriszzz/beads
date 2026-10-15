# Checkpoint 4 — development, failed versions and pre-confirmation correction

First E/W proposals: N07 E/W515, N11 E/W694, N06 E/W576, P2 E/W495,
P5 E/W664, C05 E/W527. E stays sensitive under nested perturbations: N11 minIoU
.437 and P5 .524. W minIoU .968/.952/.986/.947/.979/.944 on those six anchors.
N11 nominal upper extension remains unchanged; no claim of resolving ownership.

H local chromaticity alternative gives empty N07/N11: the diffuse color model
excludes the selected peak pixel, so the strict cue-connected component is empty.
It gives N06 573/P2 495/P5 660/C05 523, but cannot be a reliable replacement.
Do not silently borrow a component or relax color to repair the reviewed answers.
H is preserved as a failed diagnostic, excluded from five-way selection.

A mathematical narrow-continuation check exposed W v1's corridor failure: four
lateral paths were dark around a genuine bright neck, so the4-of5 rule split both
shallow shading and narrow bright material. Actual path ratios show the central
route at .746/.891, while off-axis paths are .015–.455. This is the B-like failure
we explicitly intended to test. Preserve methods_v1.py and development-v1.json.gz.

Revision BEFORE confirmation: require the central route itself to be dark, as well
as4/5 paths and consistent valley position, before making a corridor cannot-link.
This preserves narrow direct continuity while still allowing a meaningful dark
central seam to override a brighter detour. Dark interface positive-merge logic
is unchanged. It remains possible for a real seam to have a bright central bridge;
that ambiguity must be reported, not decided through a shape prior. Re-run complete
development/controls; freeze only after recording this failure and correction.

Final development after central-route correction: all six anchor areas unchanged;
W retains shallow/narrow mathematical continuity while separating deep valley.
21 cues yield7new/8M/4J/1both/1abstain. N11 upper extension remains unresolved and
is not called a successful boundary correction. E's correlated-instability and H's
empty-red failures remain. Source/selection/parameters frozen in freeze.json before
confirmation; next evaluate all15 new regions without any further inference change.
