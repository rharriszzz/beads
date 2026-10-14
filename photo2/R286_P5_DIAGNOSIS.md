# P5 root cause — measured before replacement algorithms

The failure is **missing photographic markers followed by a bright detour**, not
an erroneous merger decision between three existing watershed regions. Original S
was replayed exactly:1817 native pixels; its final marker group is just `[5]`.
All three visible yellow beads were already in that single basin before merging.
See [the diagnostic photograph](review/r286/P5-root-cause.png), native fields in
r286/results/P5-fields.npz and full measured paths in P5-diagnosis.json.

The source cue is the unchanged image-only observation at (1642,2980); its local
97px window refines the cue from(48,48) to(48,47). The diffuse pigment reference is
0.5441 linear Y, background0.008624, noise floor0.001603, and growth floor0.115714.
The sigma0.65 field preserves the neighboring bright maxima. S constructs maxima
on the whole log-intensity image, then intersects those individual maximum pixels
with its material/intensity eligibility mask.

Two important maxima at window(13,59) and(37,71) are lost in that intersection.
Their native Y values are0.7644 and0.7488, smoothed0.7465 and0.7346: they are not
weak or erased by smoothing. Their hues are55.472° and55.161°, compared with the
learned yellow prototype27°. S requires hue distance<28°. Their distances28.472°
and28.161° therefore exclude precisely those peak pixels. Their saturations0.445
and0.521 also fail the neutral-highlight continuation condition(<0.40). Neither
peak is classified as paper. Yet89.7% and96.6% of their radius3 neighborhoods pass
the yellow pigment gate. One native pixel away, both peaks have eligible material.
Thus a slight hue change at a highlight eliminates an entire competitor marker,
while nearly all of its surrounding photographic material remains growable.

There really are dark valleys. Along straight routes from the target cue to the
nearby eligible pixels of those lost maxima, minima are0.00760 and0.09491, both
below the growth floor. However, the saved maximum-minimum four-neighbor paths
bend around those valleys. Their lowest values are0.15173 and0.15470, above the
0.11571 floor. Those routes connect all three interiors in the allowed domain.
Without competitor markers, watershed assigns the connected material to marker5.
No pairwise saddle is ever evaluated between the target and these two neighbors.
The diagnostic shows both exact routes and the raw pixels they traverse.

S does retain the upper-right bead's marker2. Its boundary with target5 has a
saddle0.12642, reference ratio0.2231, and all boundary pairs below the old separation
limit. S correctly retains that separation. This explains its apparently
inconsistent behavior within the same photograph: one neighbor receives a marker
and a valid saddle test, while two others lose their markers through a pointwise
hue gate and never receive that test.

Search domain changes amplify the result:32px radius yields1114 pixels and48px
radius1817, IoU0.6131. The97px target support does not touch the outer window.
Clipping is therefore not the cause of the missing internal separation. The low
background estimate contributes a permissive floor, but simply raising it risks
recreating P2's red truncation. Neither clipping nor background alone explains
why one neighboring yellow is separated and two are not.

Demonstrated causes are marker deletion at tinted maxima and surviving connecting
routes. A general transitive-merge weakness exists in S's code, but **is not the
P5 cause**, since its target group contains only one marker. Internal texture may
also create spurious markers in other cases; that remains a hypothesis to test,
not an excuse to suppress all maxima near hue transitions.

Next experiments: preserve intensity cues when surrounding photographic pigment
supports them; test that change alone with old saddle rules as a causal ablation.
Compare spatially persistent dark barriers, watershed with protected separation,
and direct-path valley stopping. Do not hardcode these locations, widen hue just
enough to include55°, or sacrifice P2's dim red material to force a P5 success.
