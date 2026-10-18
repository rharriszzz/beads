# Reproduce and inspect R322

From repository root, use the existing `.venv`:

```sh
MPLCONFIGDIR=/tmp/r322-mpl OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r322.verify
```

This audits saved evidence, all original support pixels, algebra and held-out
edge arithmetic; it also performs an exact detector replay into a new `/tmp`
directory. It writes only the R322 verification receipt in the repository.
No old graph, fitting model or physical renderer enters the detector.

For a fresh image-only run **outside the frozen delivery**:

```sh
MPLCONFIGDIR=/tmp/r322-mpl OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r322.tracker --output /tmp/r322-fresh
MPLCONFIGDIR=/tmp/r322-mpl .venv/bin/python -m photo2.r322.review --output /tmp/r322-fresh
```

The input files are the original `beads-photo-2.jpg` and
`photo2/review/r275/inventory.json`. Only its native bright supports, colors and
appearance locations are reused. The old station groups, full outlines, black
collars and physical identities are not inputs. The fixed geographical rectangle
comes from the requested R161 region. No new package installation is needed.

Open `photo2/r322/results/index.html` directly from disk. The clean view contains
only cyan/green diagonal fragments and small labels. The indexed view is explicitly
conditional; failed associations are not repaired. `heldout-validation.png` and
`failure-and-recovery.png` show post-freeze maker evidence separately.

The evaluator and diagnostic scripts intentionally read the held-out R161 graph:

```sh
MPLCONFIGDIR=/tmp/r322-mpl OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r322.evaluate
MPLCONFIGDIR=/tmp/r322-mpl .venv/bin/python -m photo2.r322.diagnose
/home/rharris/.local/bin/beads-chromium-review photo2.r322.browser_check
```

They do not modify the frozen graph or detector. Re-running them updates their
R322 timestamps/receipts. Do not overwrite the delivery with a newly tuned detector
and continue calling the R161 comparison held out.

`freeze.json` retains the original prevalidation freeze time and an explicit later
pixel-serialization correction time. `development/frozen-v1` preserves the exact
initial detector, graph, exported pixels, freeze and validation result. Inclusive
R275 run endpoints repaired33 exported pixel counts; coordinates, all observations,
colors, track topology, decisions and scores are identical. The verifier asserts
this equality. `support-decoder-correction.json` lists every changed pixel count.
The other development directories retain the fresh-mask failure and the
prevalidation appearance-catalog/supplemental runs. They are not independent
held-out successes. Two bandwidth controls are embedded in the final graph.

The algorithm is a failed conservative expansion candidate, not a production
inventory replacement. It finds24/25 interior maker beads and38/45 interior links,
but makes three interior graph errors. Pattern and frozen-model comparisons are
therefore deliberately absent. No automatic R323.
