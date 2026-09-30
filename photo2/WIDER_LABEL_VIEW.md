# Continue labelling in a wider raw view — R164

The larger raw image is **1000×700 pixels**, covering original x900–1900,
y0–700. It contains the entire previous 360×390 view, with room in both directions
along the necklace. All 40 beads and 30 series are preserved.

Stop the running labeler with Ctrl+C, then use this command from the repository
root to continue editing the **same original-coordinate save**:

```sh
.venv/bin/python photo2/label_beads.py --crop 900 0 1900 700 --port 0
```

No labels need importing, moving or renumbering. The app loads the existing
photo2/output/labeler/annotations.json. For the whole original photograph instead,
replace --crop 900 0 1900 700 with --full-image. Zoom and pan as before.

A portable pair is also provided: [larger raw PNG](review/r164/wider-photo.png)
and [matching JSON](review/r164/wider-labels.json). This JSON uses coordinates in
the cropped PNG: subtract 900 from original x, leave y unchanged. Stable IDs,
numbers, label offsets and every ordered series are unchanged. The inverse
translation and source hashes are in the [manifest](review/r164/manifest.json).
Do not mix this translated JSON with the original JPEG.

An editable copy has been prepared in the ignored output/labeler-wider folder.
To continue using the portable pair instead of the original-coordinate workflow:

```sh
.venv/bin/python photo2/label_beads.py --image photo2/review/r164/wider-photo.png --annotations photo2/output/labeler-wider/annotations.json --port 0
```

Consider full original view, a larger original-coordinate app crop, or a portable
PNG/translated-JSON export; provide the latter two. Original-coordinate editing
is preferred for ongoing analysis. Original live data and the immutable revision-296
snapshot are preserved. The export is a lossless crop of EXIF-oriented source pixels;
it contains no generated, retouched or drawn bead appearance.

```sh
.venv/bin/python photo2/export_label_context.py
```

The exporter verifies pixel identity, exact recovery of all original positions,
IDs/numbers/series/offsets, and loading both workflows with the real LabelStore.
It starts no server/browser and does not write the original live save. No launcher
changes or manual retry test are required.
