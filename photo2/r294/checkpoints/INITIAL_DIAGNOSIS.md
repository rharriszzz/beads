# Initial diagnosis, before revised fit or held-out evaluation

The selected initial hand− model has scale8.3 px/unit, pitch1.26 times source,
elevation60°, phase.53rad and axial origin2.25px. The hand+ candidate scores.843
against.845 for hand−: essentially tied under this uncalibrated objective.

Full training measurements:92 bright patches,79 compatible under80% containment
and20-point rival margin, mean single-surface containment.9117.29 high historical
colored interiors,11 compatible, mean one-to-one containment.7391. Anchor full
containment is recorded in initial-diagnosis.json. Predicted material on the
existing image-derived paper proxy is1.41% on training sample points.

The native top-arc overlay shows broad alignment but individual centers are not
measured interior centroids. E5-1633-0278 and E5-1607-0290 (yellow, about114–136px
along the image axis), R282-1537-0308 and the later red C-1932-0452 are substantial
split/unsupported interior failures. The mismatches are not confined to weak edges.
They may reflect phase/hand/spacing aliases, source geometry mismatch, erroneous
historical support ownership, or a slow mismatch in the image-derived axis. A
brightness patch lying inside a modeled bead does not select a unique neighbor.

Revise with five shared slow log-rate and normal-axis knots at indices
−30/30/90/150/210, bounded to±.12 log rate and±8px deprojected normal displacement.
Penalize training predicted material on the existing border-learned paper proxy.
Retain both hands, common camera, fixed source radius and6.5-index minor progression.
Keep all initial candidates and all observation coordinates/supports unchanged.
There is no individual bead displacement, inferred color pattern, Phase1 update,
holdout-driven change or independent out-of-plane axis bending.

The first evaluate invocation had an unmatched closing parenthesis; corrected
before any diagnosis data were written. This technical error did not change fit
results or inference. Initial optimization log and every coarse/refined candidate
are retained. Held-out observation outcomes have not been evaluated at this point.
