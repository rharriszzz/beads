# Checkpoint2 — candidate design before implementations/results

P5's two lost maxima are only0.47/0.16 degrees outside a single-pixel hue gate,
although their neighborhoods strongly support yellow. Do not widen that gate just
to fit P5. M is a causal control: retain an intensity maximum if >=half its radius3
neighborhood is eligible pigment and an eligible pixel is within3px, then project
its marker to the nearest supported pixel. Preserve original maximum and offset.
Use unchanged S saddle logic with those completed markers. M is not counted as an
independent boundary method; it isolates the demonstrated marker-loss mechanism.

A — persistent dark-ridge barriers: test bilateral bright shoulders at4/7px over
8 directions in log intensity, require a valley at both scales and a connected
ridge of >=5pixels. Direct seed-to-pixel paths may not cross those barriers;
connectivity cannot take a bright detour. Risk: internal shading can resemble a
persistent seam; direct visibility can truncate legitimate bent material.

B — protected watershed: context-supported markers as M; use the distribution of
native interface intensities (>=60% dark pairs), not only its brightest saddle.
A coherent dark interface becomes a cannot-link constraint. Weak basin mergers
cannot erase a previously supported separation through transitive graph routes.
Multiple maxima alone do not imply bodies. Risk: false markers/deep internal
texture can partition one physical bead; evidence remains uncalibrated.

C — direct-path intensity topology: every seed-to-pixel route retains its running
minimum; a renewed rise after a sufficiently deep, nonlocal valley is barred.
Depth/rise are relative to diffuse pigment, never specular peak. This tests the
old dark-stopping intention independently of watershed markers or ridge extent.
Risk: native ray anisotropy and internal deep shading can carve false wedges.

All reuse S's diffuse/material measurement domain to isolate separation mechanisms.
No new compactness/area optimization, thickness pruning or silhouette inference.
Compare65/97px domains and exposure scaling;870px ceiling is a rejection guard.
P1–P5 and P2/P5 tradeoff are development. Freeze methods after inspecting development
and documenting failed variants; only then open newly selected confirmation images.
