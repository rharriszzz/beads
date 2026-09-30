# Interactive bead labeler — R138–R148

From the repository root:

```sh
.venv/bin/python photo2/label_beads.py
```

On WSL, the launcher opens the Windows browser using `wslview` when available,
then PowerShell if needed. If launching fails, it quietly prints the URL to open
manually. On a Linux machine without a browser, it also gives the manual URL.
Keep the terminal running; Ctrl+C stops the server.

The default port is 8765. If it is occupied, the program asks the OS for a free
port and prints the actual URL. An explicit `--port 4000` is honored and gives a
clear error if busy; `--port 0` explicitly requests a free port. `--no-browser`
skips automatic opening. No browser installation is required for WSL launching.

The default view is the original photograph's EXIF-oriented wider raw crop x1180–1540, y130–520,
360×390 pixels. No existing B/C/G annotations are loaded. Installed Pillow is
the only third-party runtime dependency.

R164: [expand to x900–1900, y0–700 with the saved 40-bead labels](WIDER_LABEL_VIEW.md).
The app loads the existing annotation file; a larger raw PNG and matching
portable JSON are also available there. No re-labelling or launcher change.

Source SHA-256: `eb7c9edb62f5580ef56632872da48da92556d62b758295137068cc2404dc8fbb`;
oriented source size 2540×3182. Integrity checking confirmed the served crop
matches the original pixel-for-pixel and creates no annotation file until saving.

## Number beads

1. Click the location you want on an unmarked bead. A ring marks the pending point.
2. Enter its unique integer number, then click **Add bead** or press Enter. The
   suggested next unused number can be changed before adding the bead.
3. Repeat for the other visible beads. Duplicate numbers are rejected.

Click an existing dot or number to select it. Enter a replacement number and
**Apply number**. Outside an active series, drag a dot to move its location;
drag its text to move only the label. Numbers are your chosen bead names, separate
from stable internal IDs and any later inferred full-string bead_index.

## Record direction series

Choose a direction, then **Start series**. Click near the starting numbered bead,
then near each following numbered bead in your intended order. **End series**
finishes the series after at least two beads. The sidebar shows the numbered
sequence; arrows show click order on the photo. Repeat to create more series.

| Name | Maker's description |
| --- | --- |
| d1 | Plus or minus 1 direction |
| d2 | Up to down while proceeding clockwise around the bracelet, according to the major torus diameter |
| d3 | Down to up while proceeding clockwise; equivalently up to down while proceeding counterclockwise |

The [verbatim specification and clarification](LABELER_QUESTIONS.md) establish
these descriptions. No d2/d3 assignment to 6/7 or numerical sign is inferred.
Each series records its first bead and every subsequent click, including revisits
other than consecutive duplicates. Links express the maker's selected direction;
they do not assert verified nearest neighbors or known intervening step counts.
Skipping unmarked beads does not compress or recover string indices.

During a series, clicks snap to the nearest visible stored location within 18
screen pixels; clicking a number also selects its bead. Clicking empty space adds
nothing. Series clicks do not move locations. Sidebar bead buttons can also add
the chosen bead to the active series. **Undo last series click** removes its last
entry. **Cancel series** removes an unfinished series; completed series have
**Remove series**. Global Undo/Redo also cover these operations and numbering.
A saved active series resumes after reload. End or cancel it to place/move beads.

Renumbering or moving a bead preserves its series references. To delete a bead
used by a series, first remove those series. This prevents a deletion from silently
joining its predecessor and successor. Undo can restore removed beads or series.

## Navigation and saving

Scroll or use +/- to zoom. Hold Space and drag, middle/right drag, or drag empty
space to pan. **Fit image** restores the full crop. **Show annotations** reveals
the raw photo without overlays. **Save**/Ctrl+S flushes pending changes; changes
also save automatically. **Download JSON** exports a portable copy of saved or
unsaved numbered locations and series. A pending point must be confirmed with
Add bead before it is included. Escape/Cancel discards a pending point.

Default file: `photo2/output/labeler/annotations.json` (ignored user data).
Successful saves atomically replace the file and preserve its previous version
as `annotations.previous.json`. Revision checks reject stale saves from other
tabs/processes. Browser storage also retains unsent same-revision drafts when
available. After a save conflict, download that window's JSON before reloading.

Schema 2 stores source SHA-256, oriented dimensions, coordinate convention, view
crop, revision, direction definitions, `annotations` and `series`. Each bead has
`id`, `number`, original oriented `x/y` and image-pixel `label_dx/dy`. Each series
has `id`, `direction`, `status` (`active` or `complete`) and ordered `bead_ids`.
Pan/zoom do not change source coordinates. Points outside a later crop remain
saved. Files for a different source or unsupported schema are rejected without
being overwritten; choose another `--annotations` path if needed. The unpublished
free-text foundation used schema 1; no annotation file existed when schema 2 was
implemented, and existing schema 1 files are not silently converted.

Other views and photographs:

```sh
.venv/bin/python photo2/label_beads.py --full-image
.venv/bin/python photo2/label_beads.py --image /path/to/raw-photo.png --annotations /path/to/labels.json
.venv/bin/python photo2/label_beads.py --crop 1180 130 1540 520 --port 8766 --no-browser
```

Another photograph defaults to its whole oriented extent. This is a manual evidence
collection tool. The viewing crop is explicit; it supplies no automatic bead
locations, colors, closure, total bead count, repeat or resolved string indices.

R167 adds a separate [automatic proposal generator](AUTO_LABELS.md). Its
schema2 output opens in this app with `--full-image --annotations` pointing to
the separate generated file. Automatic numbers/links remain provisional.
Saving an edited automatic file preserves its origin and uncertainty; it does
not declare every untouched proposal maker-confirmed. Original manual saves
retain their existing behavior. The generator refuses the maker live path and
refuses to overwrite reviewed output.

## Verification and stopping point

R143–R147: the maker ran the labeler, saved 27 locations and 19 direction series,
and corrected two series in the app. [The resulting graph analysis](LABEL_SERIES.md)
provides manual workflow evidence and a seven-body seed for projection fitting.
The automated graphical-browser limitation below remains unchanged.

Thirteen Python tests pass, covering raw crop/EXIF geometry, original-coordinate
save/reload, ordered series and renumbering, invalid/dangling references and
duplicate-number rejection, source/backup protection, stale revisions and real
HTTP image/save/reload/conflict. Five launch tests cover actual temporary occupied-
port fallback, explicit port/zero behavior, non-port bind errors, mocked Windows
launching, absent launchers and timeout/failure fallback from wslview to PowerShell.
No real browser is opened by the tests. Six JavaScript model tests cover coordinates,
number validation, click snapping, series transitions and identity/history.
One scripted application test uses the real UI handlers with a minimal DOM/canvas
adapter to place beads, reject a duplicate, click/end a d3 series, renumber, undo
and save. Syntax checks pass. The HTTP test needs local sockets enabled outside
the sandbox. No graphical browser is installed here, so real-browser layout and
pointer interaction remain unverified; the scripted adapter is not a browser.

```sh
.venv/bin/python -m unittest discover -s photo2 -p test_label_beads.py -v
node photo2/labeler/test_model.mjs
node photo2/labeler/test_app.mjs
node --check photo2/labeler/app.mjs
```

The graph review is complete and the R148 launcher fix is delivered. Stop an
existing server with Ctrl+C, then rerun the normal command to load the fix. Next
analysis task: compare the two relative-index families on the seven-body patch.
Recommend gpt-6.1-sol / High; stay in this session, no /new required.
