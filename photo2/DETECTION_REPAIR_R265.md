# R265 — straight native growth and local retreat repair

[Additional first-black/gray step and final default](FIRST_DARK_R265.md). The
measurements below preserve the preceding v1 comparison.

**Growth/retreat repairs and automated comparisons are delivered; reliable
one-coordinate-per-visible-bead coverage is not established.** Old code/results
remain preserved. [Native comparisons and exact data](review/r265/README.md).

## Confirmed defects and corrections

Four methods were considered: independent histories, valley barriers, local retreat
and learned HSV seed rejection. The user's **“only go in straight paths”** correction
determines the final implementation; the intermediate graph-path approach was discarded.

- **Growth coupling:** remove the region-wide brightness floor. Every proposed pixel
  has a complete straight seed-to-pixel history, sampled by integer Bresenham steps
  on the native eight-neighbor raster. Check brightness and color along that fixed
  segment; a stop blocks its target. No curved alternative, image interpolation,
  blur, angular smoothing, watershed or ownership partition is used. With strict
  brightest-first growth the old global ceiling was often redundant; removing it
  alone is not evidence of improved coordinates.
- **Valley bypass:** an explicit regression grid confirms that a descending path
  can wind around a dark trench. Fixed straight paths prevent that detour. A
  separately tested local fence rejects pixels with opposing neighbors at least6 DN
  brighter; diagonal steps cannot cut dark/fenced corners.
- **Bright-leaf retreat:** the old leaf threshold was `v + margin`, guaranteeing
  rejection even for bright leaves. New retreat uses native3×3 darkness evidence,
  capped at81 DN, and `floor + max(2, .30*(peak-floor))`. Keep the seed-connected
  component and record disconnections. No descendant-minimum propagation or filling
  of holes remains. This is compact support, not a physical outline.
- **Background seeds:** learn circular H/S/V from generic margins; reject before
  growth only when all seed-neighborhood samples confidently match the learned
  model. Preserve uncertain seeds. This gate passes synthetic tests but rejects
  **zero** of this photograph's already-prominent seeds; no photographic benefit
  from this gate is claimed.
- **Numerical hue boundary:** full-photo auditing caught355°→5° slipping below the
  exact10° stop through floating-point subtraction. A1e-12° numerical guard fixes
  the boundary; four signed/wraparound regression cases cover it.

Keep the870 distinct-pixel limit before retreat; an eligible871st rejects the
proposal. Hue remains10°, prominence35, rise allowance0. No hue sweep or count
optimization. [Complete mechanics](bead_detection/README.md#r265-mechanics-and-limitations).

## Automated results

58 Python tests pass, including240 randomized grids. Four corrected-growth audits
verify492,360 acceptances and988,800 directed stops, native values, full straight
histories, monotonicity/color, adjacency, connectivity, centroids and coordinates.
The old ablation reproduces archived R264 masks/coordinates/statuses exactly.
44 Chromium checks pass, including straight-history and blocker replay.

| Full-photo variant | Retained supports | Enclosed hole pixels | IoU >.5 pairs | Paper-window pixels |
|---|---:|---:|---:|---:|
| Old | 1552 | 26744 | 210 | 1 |
| Straight growth only | 1556 | 250 | 3 | 0 |
| Straight + valley fence | 1556 | 169 | 1 | 0 |
| Local retreat only | 1552 | 17316 | 274 | 15 |
| Background precheck only | 1552 | 26744 | 210 | 1 |
| Straight + local retreat | 1556 | 445 | 11 | 7 |
| Joint correction | 1556 | 249 | 9 | 7 |

Joint holes comprise245 growth-stopped pixels and4 retreat removals; none are
unvisited/unexplained by the trace. This does not verify physical gaps. All final
supports are connected. Size-limit rejections fall5→0. Counts and overlaps are
not bead identities. Local retreat alone increases overlap and paper contamination;
it must not be credited as a complete detector repair.

Across24 compact synthetic bodies, both old and corrected detection miss0 bodies,
with0 background/neighbor contamination, but retain6 duplicate extras from multiple
peaks. Hole pixels fall59→0. Separate oversized stress scenes miss17/24 bodies old
and10/24 corrected; the cap and seed selection still limit coverage. Known synthetic
footprints, colors, noise, shadows, reflections and multiple peaks are evaluation
truth only, never detector priors.

126 fixed photographic seeds cover the named cases and automatic failure crops.
Among1551 common retained IDs,1406 coordinates move: median2.24px, p90 6.32px,
maximum17px. Five IDs are added; P115006 is lost to the post-growth paper check.
These are sensitivity measurements, not physical-center errors.

## Remaining photographic failures

All12 R264 likely duplicate pairs persist despite sharply reduced overlap. R01284
still duplicates the central yellow; R00956 remains on the yellow's left rim.
M1–M5 remain more than10px from a coordinate. M6/P013502 is restored3px from its
review landmark. Proximity does not prove identity or comprehensive recall.
R01307 still misses the upper pale and lower yellow landmarks.

**Paper contamination regresses in the saved window:1→7 pixels.** The largest
coordinate shifts include suspicious bead/paper edges. The conservative HSV gate
leaves these seeds uncertain; this is not a solved background problem. Straight
raster prefixes can also under-cover uneven/noisy bodies. No whole-photo accuracy,
verified count, recovered centers, geometry, indexing or pattern is claimed.

## Reproduction and stopping point

```sh
.venv/bin/python -m photo2.bead_detection.experiment_r265 --seconds 1800
.venv/bin/python -m photo2.bead_detection.experiment_r265 --seconds 1800 --resume
.venv/bin/python -m photo2.bead_detection.server
```

This v1 viewer uses `--work photo2/output/r265/joint`; historical versioned runs and
R264 hue links remain available. It shows sampled straight paths and exact blockers.
Sites skill used locally only; no deployment.

The30-minute supervisor window completed all final comparisons in16m57s, including
development reruns, without resetting the deadline. Browser checks followed inside
the same window. A50-ms forced deadline confirms termination/checkpoint behavior.
Initial JSON serialization failure, a source-change stop and the numerical-hue
failure remain documented; final matching stages pass. Source fingerprints prevent
stale-stage reuse. [Hashes, parameters, logs and complete traces](review/r265/README.md).

Next bounded task: review residual paper-like seeds, missed seed evidence and
multiple-peak identities against this fixed repair before choosing the next
algorithm phase. Stop after commit/push. Recommendation: retain the current model
and reasoning choice; no `/new` for review, use `/new` before a substantial new phase.
