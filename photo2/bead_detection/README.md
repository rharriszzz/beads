# Native-pixel bead supports — R263

R264 adds **Compare six hue settings** at `/hue-comparison`: nine identical-photo
crops, supported-coordinate crosses, hover HSV and run-specific growth replay.
The provisional recommendation is the saved8° run at `/?hue=8`;10°/12° alternatives
remain useful. The historical detector default stays10°. Restart an older server.
[Photographic findings, duplicates/misses and leaf retreat](../HUE_COMPARISON_R264.md).


R263 uses independent native-pixel growth without watershed ownership.
Its goal is a reliable supported coordinate per visible bead. These results remain
candidate supports, with duplicate highlights and misses unresolved.

```bash
.venv/bin/python -m photo2.bead_detection.server
```

Open **http://localhost:8767**. Restart an older server first, or add `--port 8768`.
The first launch generates missing data in `photo2/output/detection-r263-bounded/` from the
original photograph. It does not read historical bead labels, curves or models.
The familiar `photo2.bead_debugger.server` launcher also opens this viewer.

Drag to pan; scroll to zoom. Cyan contours are smoothed for display only. Their
exact integer pixel runs determine area, area centroid and supported coordinate.
The bright-patch centroid is a separate measurement. No coordinate is called the
physical bead center. Pixel centers use integer x right / y down after EXIF orientation;
at high zoom the photograph uses nearest-neighbor display.

Click a region or enter its `P` ID (numeric input is accepted). **Largest, Smallest,
Median** and previous/next browse retained area. The median button selects the
middle ranked region, choosing the lower area for an even-sized inventory. Click
histogram bars to filter. Region IDs belong to this run, not the R260 `R` namespace
or a resolved bead index. Rejected grown supports can be selected by ID too.

**Growth replay:** Reset begins before the seed. `+1 pixel` accepts exactly one
recorded native pixel; Play advances at one pixel per 60 ms. The slider can inspect
any acceptance. Cyan fill shows pre-retreat growth; the contour remains the final
support. Pixel details identify acceptance order, predecessor, raw brightness,
HSV, and whether retreat later removed the pixel. **Final** hides the replay fill.
**Stop → / ← Stop**, or an exact stop event number, visits every stopped edge,
restores its exact acceptance time, and marks the destination pixel orange and
its predecessor edge white. Brightness is max(R,G,B) in 0–255; H is degrees, S/V
are 0–1. Traces are loaded on selection; Download full growth trace exports them.

All candidate maxima, coordinates, size ranks and histogram are downloadable.
153,166 below-prominence maxima have preserved plateau pixels and rejection
reasons but no expansion trace because no growth was attempted. All1,595 grown
candidates, including rejected ones, have complete traces.1,552 retained supports
remain identity-ambiguous;695 overlap another support. These are not confirmed
distinct bead counts. Full compressed copies are committed in
[../review/r263](../review/r263/README.md).

The default uses prominence35, minimum peak0, zero brightness-rise allowance and
a10° circular hue limit relative to the first reliable chromatic pixel on each
path. Hue stopping applies at or above10°, with S≥0.35,V≥0.20,S×V≥0.08.
Equal brightness is accepted; heap ties are deterministic. Rejected destinations
stay locked against other paths. Different maxima grow independently and can
overlap; overlap never establishes one shared bead identity.

Growth accepts at most870 distinct native pixels **before retreat**. If it needs
an871st eligible pixel, the candidate is flagged/rejected and all pending edges
receive `maximum-region-pixels` stop records. Five such candidates remain
inspectable by ID; smaller final masks are not automatically valid beads.
The original photograph, cyan contours, IDs, centroids, pan/zoom, selection,
histogram and pixel/stop replay remain the viewer's working tools.

Reproduce in Python 3.12 with the existing [requirements](requirements.txt):

```bash
.venv/bin/python -m unittest photo2.bead_detection.test_bounded photo2.bead_detection.test_tuning photo2.bead_detection.test_no_watershed -v
.venv/bin/python -m photo2.bead_detection.bounded_detect
.venv/bin/python -m photo2.bead_detection.validate_bounded --isolation
PLAYWRIGHT_BROWSERS_PATH=/tmp/beads-debugger-browsers .venv/bin/python -m photo2.bead_detection.browser_pixels --work photo2/output/detection-r263-bounded --output photo2/review/r263/bounded
.venv/bin/python -m photo2.bead_detection.curate_bounded
```

Every parameter is configurable through `bounded_detect --help`, including
one-level integer brightness thresholds, `--minimum-peak-dn`, `--hue-stop-deg`,
`--retreat-fraction` and `--retreat-dn`. `--max-region-pixels` can be lowered but
cannot exceed870. Save experiments to different `--output` directories and open
them with `server --work PATH`. The viewer preserves the selected run's parameters
and chooses the matching archived generator if regeneration is needed. Unknown
versions raise an error. Historical `pixel_detect` (R261), `monotone_detect` (R262)
and `tunable_detect` (uncapped search) remain frozen for reproduction.
Changing display contours never changes masks.
Playwright/Chromium is optional and needed only for browser tests.

**Preserved R260:** `python -m photo2.bead_detection.server_r260 --port 8768`
(with `.venv/bin/python`) uses the unchanged historical radial detector and copied
viewer assets. `detect.py`, R259/R260 results, strict comparisons and reviews remain
preserved. The old `browser_smoke` tests explicitly target this archived viewer.
The geometry debugger remains at `photo2.bead_debugger.server --legacy`.

[Current algorithm, parameter search and limitations](../PARAMETER_SEARCH_R263.md).
[Watershed removal and pair diagnosis](../NO_WATERSHED_R262.md).
[Historical R261](../PIXEL_DETECTION_R261.md).

## R265 straight-path detector

Default viewer data now comes from `photo2/output/r265/joint`, generated by
`repaired_detect.py`. Every proposed pixel is evaluated along a straight segment
from its image-derived seed, sampled with integer Bresenham steps. No curved
alternative route, image interpolation, watershed or ownership partition is used.
Full straight histories and exact blocking pixels are saved in traces. Local
retreat preserves bright leaves and the seed-connected support. The hard870-pixel
pre-retreat cap remains. See [the repair report](../DETECTION_REPAIR_R265.md) and
[automated comparisons](../review/r265/README.md).

```sh
.venv/bin/python -m photo2.bead_detection.experiment_r265 --seconds 1800
.venv/bin/python -m photo2.bead_detection.server
# Historical detector/viewer remains reproducible:
.venv/bin/python -m photo2.bead_detection.server --work photo2/output/detection-r263-bounded
```

For a separate harness destination use `--work PATH --output PATH`. Resume with
`--resume` preserves the original absolute deadline, skips only matching completed
stages, and reruns stages invalidated by changed detector/harness/test sources.

## R265 mechanics and limitations

Four approaches were considered: independent path histories, local valley barriers,
local darkness retreat, and conservative learned HSV background seed rejection.
The user's subsequent **“only go in straight paths”** instruction determines the
final growth implementation. An intermediate graph-path approach was discarded.

- **Shared growth state:** the old region-wide minimum and destination locks could
  couple different paths. The corrected detector validates a complete straight
  seed-to-target segment, with its own running brightness floor and first reliable
  chromatic anchor. With zero rise allowance, strict descent remains mandatory.
  Removing a shared variable alone is not evidence of photographic improvement:
  the original brightest-first strict queue often made that ceiling redundant.
- **Valley circumvention:** a descending path can wind around a dark trench without
  ever taking an uphill step. A regression grid demonstrates this in the old
  detector. Now only the fixed straight segment is eligible. Integer Bresenham
  sampling visits original eight-neighbor pixels; no image interpolation, blur,
  angular smoothing, watershed or ownership map is used. Dark/uphill/hue/saturation
  stops anywhere on that segment block its target. An additional native local
  saddle fence stops pixels with opposing neighbors at least6 DN brighter, and
  diagonal steps cannot cut a dark/fenced corner. This fence has its own ablation.
- **Bright-leaf retreat:** old terminal leaves used their own brightness as the
  retreat floor and therefore failed `v > v + margin`. This is a confirmed bug.
  New retreat uses the native3×3 minimum at each accepted pixel, capped by the dark
  reference81 DN, then threshold `floor + max(2, .30*(peak-floor))`. Peak pixels
  survive; other pixels must exceed their local threshold. Keep only the seed's
  eight-connected component, recording any disconnection separately. There is no
  predecessor-tree propagation, dependence on leaf count or hole filling. This
  defines compact support, not a physical bead outline or inferred center.
- **Background before growth:** circular H, S and V are learned from generic image
  margins (3.5% border). Reject only if every pixel in a seed's3×3 neighborhood
  agrees with the narrow learned95% intervals. Broad/heterogeneous models and
  neutral/uncertain hue are left unresolved, as are unseen deep-shadow values.
  The older post-growth paper-compatible check remains separately observable.

All870 distinct accepted pixels are counted before retreat; an eligible871st
rejects the proposal. Minimum support and prominence are separate. Hue stays10°,
prominence35, rise allowance0; there is no new hue sweep or count optimization.
All maxima remain cataloged, including unexpanded background/noise seeds.

The queue processes native distance shells, then brighter pixels within a shell,
so straight prefixes are decided before more distant targets. Different straight
segments can rasterize different prefixes; a target whose required prefix was
blocked is conservatively rejected. This can under-cover a noisy bead. Complete
`straight_path_indices` accompany adjacent acceptance predecessors, so replay does
not confuse a shared predecessor tree with a straight path. Stops include the
actual blocking pixel along the requested segment. No curved alternative can
repair a stopped segment.


## First neutral-black follow-up

The final default is `photo2/output/r265-first-dark/joint`. Neutral gray samples
stop at V≤min(81 DN, half the seed peak), independently of the old36-DN contrast
condition. A dim gray reflection may still seed growth. Gray means S≤.25 or
channel spread≤12 DN; this is evidence, not a material label. Complete gray-path
fractions and blockers are saved. See [the follow-up](../FIRST_DARK_R265.md).
