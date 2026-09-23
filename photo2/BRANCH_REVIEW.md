# Markdown branch review — 2026-09-23

Enumerated all local branches and remote-tracking branches after the requested pulls.
Read each distinct Markdown blob once; identical copies on multiple branches share
an entry below. This inventories branch tips, not every historical commit.

## Complete Markdown review outside the excluded repositories

`bead_map` and `hsv_tools` have no tracked Markdown files on any available branch.
`arxiv-shelf` is included because it is a workspace project. No project edits were
made there. These repositories have no additional untracked Markdown inputs.

| Repository | File | Git blob | Branches |
|---|---|---|---|
| arxiv-shelf | MAC_API_TEST.md | `16cd1d1b68a0c75e7f1b39c686240899dfdcb901` | master, origin/HEAD, origin/master |
| arxiv-shelf | README.md | `6bd08a364913b5ff63e0506ff760b995a62c3cba` | master, origin/HEAD, origin/master |
| arxiv-shelf | TODO.md | `874dcb8d4cd78c42eacedd79965bff59d1d17069` | master, origin/HEAD, origin/master |
| beads | image-to-pattern/color_config.md | `0e30e38d0a9b2257f8c2706598d2c8ecc426a54b` | image-to-pattern, image-to-pattern-2, origin/image-to-pattern, origin/image-to-pattern-2, photo-2-reconstruction |
| beads | image-to-pattern/gui-testing.md | `3d166fb3e492d99f9c19ca040da57d6d33acd5b7` | image-to-pattern, image-to-pattern-2, origin/image-to-pattern, origin/image-to-pattern-2, photo-2-reconstruction |
| beads | image-to-pattern/plan.md | `e62a62ec45024d2a4222557330b2085e472b5a05` | image-to-pattern, origin/image-to-pattern |
| beads | image-to-pattern/setup.md | `9c97b869f3c58ed53bbad927b366ac44cc79e9e4` | image-to-pattern, image-to-pattern-2, origin/image-to-pattern, origin/image-to-pattern-2, photo-2-reconstruction |
| beads | image-to-pattern/plan.md | `8a852ab01a9ef20f6d882db06a578c6290f58e52` | image-to-pattern-2, origin/image-to-pattern-2, photo-2-reconstruction |
| beads | pattern.md | `d34ce815ac26add841cc30b31a259c41ba7ce72b` | origin/pattern |
| fft-image-explorer | README.md | `7c0a84dd1b9f715e00117b29f90d72042c7a1845` | main, origin/HEAD, origin/main, radial-sum |
| fft-image-explorer | notes.md | `2f22f0a766298d49dd7cc14f15a22e85632b02ca` | main, origin/HEAD, origin/main, radial-sum |
| fft-image-explorer | CHANGES_SINCE_LAST_COMMIT.md | `79941e7b1312fe52b7c386c817851eb9c95e15f6` | radial-sum |
| fft-image-explorer | COMMIT_AFTER_CURRENT_HEAD.md | `2e1a021b8394dfe7f8dad982c64024ba8562b3fc` | radial-sum |

## Vortex lab: workflow only

Read the current `AGENTS.md`, `docs/workflow/SESSION_PROTOCOL.md`, workflow/rendering
sections of `docs/workflow/TRACK_RULES.md`, `docs/WORKFLOW_OVERHEAD_PLAN.md`,
`docs/PROCESS_REVIEW_AND_MODEL_ROUTING.md`, and `docs/history/R092_ARCHIVE_INDEX.md`.
Read workflow sections of archived agent instructions and handoffs, the current
ownership table, and request entries concerning logging, continuation, publication,
machine switching, Python 3.12 and preserving agent context. Inspected lifecycle
record examples. Scientific research/evidence and historical numerical tasks were
excluded from the review; their restrictions and stale task assignments were not
transferred to beads. `povray` and `navier-stokes-physical-approximation` Markdown
were excluded. No subagents were used.

## Findings that affect this branch

- Beads v1 records failed palette clustering, background/shadow contamination,
  sparse sampling and unreliable inferred ordering; its early description of
  photo 2 as a purple bead palette was wrong. The magenta is paper.
- V2 calls for per-stage evidence and known-pattern validation. Photo 4 is the
  documented known-pattern photo (case 4); photo 2 has no established answer.
- HSV rectangle annotations are a useful existing path to labeled color evidence.
- FFT notes favor smooth windows, local directional information, explicit confidence,
  tangent/normal coordinates and uniform arc-length sampling.
- The local-only `radial-sum` branch preserves reverted tracer changes and the
  following commit description. They are historical experiments, not proven fixes.
- The latest lab workflow supersedes old document-size goals: useful progress and
  sufficient rationale/evidence matter. Match model/task complexity, avoid repeated
  contract/review cycles, and use complete capabilities as step boundaries.
- Keep one coherent handoff, append-only requests/results, reproducible artifacts,
  scoped user-authorized publication and clear machine-transfer state.
