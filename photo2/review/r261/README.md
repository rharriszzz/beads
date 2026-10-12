# R261 curated pixel detector evidence

[Report](../../PIXEL_DETECTION_R261.md) · [Viewer](../../bead_detection/README.md).
Final generation: `5e12fe3816473053`. Photograph: 2540×3182 native oriented pixels.

- `regions.json.gz`: complete maxima catalog, retained and rejected grown regions,
  bright patches, exact masks, centroids, supported coordinates, display contours,
  dark-enclosure evidence, parameters and provenance.
- `growth-traces.tar`: 7,543 individually gzip-compressed per-region traces under
  `traces/Pxxxxxx.json.gz`. Includes all grown candidates, even rejected ones.
  The tar contains only those generated relative paths. Unexpanded noise maxima
  have plateau runs and `below-prominence` reasons in the full JSON, not fictitious
  acceptance records. Original RGB supplies values for unvisited pixels.
- `labels.npz`: retained-region native labels and **all** raw-maximum catchments.
  Positive integers map to P IDs padded to six digits. Retained background is zero.
- `coordinates.csv`: all grown candidates, including status, supported coordinate,
  exact area centroid, area and evidence kind. `rank-size.csv` ranks retained areas.
- `summary.json`, `size-distribution.png`: counts and histogram with numeric bins.
- `R01307`, `R00956`, `R01284` native comparison PNGs and compressed per-pixel CSVs:
  same raw crops, old/new contours, raw RGB/HSV and exact label membership.
  `r260-comparisons.json` lists every new support intersecting each crop, its exact
  coordinates, overlap with the old mask and centroid displacement (not error).
- `synthetic-*.png`, `synthetic-*.json.gz`, `synthetic-validation.json`: the six
  requested tests, their source-equivalent trace values, masks and result counts.
- `valley-proof.png/json`: single-catchment native-pixel detour stress test.
- `full-validation.json`: complete photo audit and stopping-reason counts.
- `isolation.json`: standalone code + original photo reproduce full JSON, labels,
  catchments and every trace byte-for-byte, with no historical data available.
- `browser-checks.json`, `browser-whole.png`, `browser-replay.png`: real Chromium.
- `manifest.json`: SHA-256 and byte size for every data/evidence artifact.

The photograph's original JPEG remains at the repository root, untouched; display
PNG is generated without an ICC profile so decoded RGB stays numerically faithful.
The source hash is `eb7c9edb62f5580ef56632872da48da92556d62b758295137068cc2404dc8fbb`.
The standalone detector hash is
`c26910200ab044abc2168c2e9a0f224cb0decbaf9c5a81e1d3a32bb71037c05d`.

Trace arrays have named schemas in every file. Accepted-array index is growth order;
predecessor is an earlier accepted-array index (`-1` for the root). Each entry
contains native x/y, raw Value DN, H degrees, S, V and a retained-after-retreat flag.
`retreat_floor_dn` records each path-tree floor. A false retained flag means
`retreat`; true means retained support, not a verified bead. Stops are directed
predecessor→destination events with the same values, a reason, and the acceptance
count when the stop occurred. Multiple stopped paths may target the same pixel.
The viewer permits inspection of **every** event, without downsampling the replay.

Use the reproduction sequence in the viewer README; the synthetic tests precede
full detection. `curate_r261 archive` saves this curated package after validation.
The temporary output directory and runtime environments remain ignored. Prior
R259/R260 artifacts and all user review history are preserved.

For direct archive inspection in a new temporary directory:

```bash
mkdir -p /tmp/beads-r261-traces
tar -xf photo2/review/r261/growth-traces.tar -C /tmp/beads-r261-traces
gzip -dc /tmp/beads-r261-traces/traces/P128275.json.gz
```

Questions requiring user bead marking: **none**. The illustrated comparisons expose
remaining duplicate and false-positive uncertainty; they are not new maker facts.
Next review concerns reliable locations and duplicate highlights, not larger masks.
