# Optional review after automatic detection

No bead identification was requested as a prerequisite. No answers to the following
prompts are assumed; the complete automatic run is already generated.

Recorded maker answer during implementation: “you are not required to find the
full extent of the black beads, it will fail. Instead stop growing the region
once the perimiter gets fully black.” Applied in final v2; black support ends at
the first dark perimeter. All full-black-body proposals from the earlier pass
are superseded.

For a subsequent review, start with the [raw/outline example](example-1.png) and
the viewer's Largest/Smallest buttons. One region ID and one finding at a time
would be useful:

- Does an automatic colored region contain two beads or substantial paper?
- Does a visible reflection lack a retained dark-perimeter region?
- Does an outline stop too early on a colored bead?

Use generation `40eaf236aa363f0c` with the ID. These are review prompts, not new
runtime priors or permission to start geometry/indexing work.
