# Interactive count, helicity, zoom and pan — R181–R182

**R183:** [Width guides and +7% comparison](WIDTH_GUIDES.md) add the centerline,
current maximum-radius edges and an adjustable width reference. Restart a
running Python server and reload the page to enable the new controls.

Run the Python viewer from the repository:

```bash
.venv/bin/python photo2/tangent_viewer.py
```

It prints a local URL and attempts to open the browser using the existing
WSL-aware launcher. If needed, paste the printed URL into your browser.
Default port is 8766; an occupied default automatically falls back to a free
port. An explicit port can be selected with `--port 4001` or `--port 0`.
Ctrl+C stops the Python server. No new packages or external service are needed.

The viewer uses the whole original photograph. It starts at helicity −1,
2,698 beads, with a **2,000–3,600 count slider**. A previous saved choice takes
precedence on restart unless `--count` / `--hand` is supplied.

- Move the slider, use its arrow keys for one-bead changes, or type a count
  and press Enter. Buttons return directly to 2,698 or 2,833.
- Scroll the mouse wheel to zoom around the pointer. Drag with the left mouse
  button to pan. Zoom buttons, 100%, Fit photo and Starting patch are available.
- Count and helicity changes preserve the current zoom and pan. The Starting
  patch button returns to the diagnostic three-colored-bead registration area.
- Switch helicity between −1 and +1. Each uses its saved original local fit;
  the spline, camera and physical dimensions are common. Phase/station stay
  fixed within each helicity while the count changes.
- Uncheck Show cyan circles for an unobstructed raw-photo comparison.
- White dashed marks the centerline; amber dashed marks its±maximum-radius
  model edges. Green is an adjustable comparison starting at107% width.
  Guide width changes80–130% without moving cyan circles. Edges/Centerline
  checkboxes toggle these references; Model width/+7% buttons restore presets.
- Slider range lets you adjust its endpoints. Supported whole counts are
  100–10,000; the initial range spans below, between and above both trial counts.
- Save choice writes the current count, helicity, view and width-guide settings to
  `photo2/output/tangent-viewer/choice.json`. Restart restores that choice.
  Each save retains the previous version in `choice.previous.json`.
- Download full PNG exports the entire source photograph with the current
  selected cyan circles and guides, independent of the zoomed viewport. Download parameters exports
  a portable JSON usable with the existing static-overlay program.

For a different initial range or save file:

```bash
.venv/bin/python photo2/tangent_viewer.py --min-count 2300 --max-count 3200 --count 2698 --hand -1 --save photo2/output/tangent-viewer/another-choice.json
```

To make a static overlay from the saved choice:

```bash
.venv/bin/python photo2/tangent_circles.py --stage overlay --parameters photo2/output/tangent-viewer/choice.json --output photo2/output/tangent-selected
```

## Geometry and responsiveness

Three interface methods were considered: a native desktop window, this local
browser viewer, and a notebook widget. The browser viewer matches the existing
labeller and supplies zoom/pan without installing a desktop toolkit or widget
package. It reuses the existing [tangent-circle geometry](TANGENT_CIRCLES.md)
and [per-helicity original registrations](HELICITY_COUNT_COMPARISON.md).

Each count recomputes placement and exposure against **all** model beads.
Only an exposed minor-outward point receives a circle; hidden/grazing/unfinished
rays are excluded as before. The browser receives each exact projected ellipse
as a center and two axes, then draws a smooth 48-segment loop at the same
source coordinates as the photograph. Changing count also changes projected
bead size to fit the fixed image spline, as in the original comparisons.

Dragging the count slider coalesces requests; only the latest choice may update
the display. Previous circles dim while calculation is pending. Save/export
controls remain disabled until the displayed frame matches the requested
count and helicity. Recent results are cached. Zoom/pan redraw locally without
asking Python to recalculate geometry.

The maker's [R180 drift review](drift-review-r180.json) reports center-to-boundary
drift after 130–156 bead steps at 2,698 and 65–91 at the increased count, with
similar behavior for both helicities. “Minus 3833” is provisionally interpreted
as the supplied minus 2,833 image; the original statement is preserved. These
unsigned approximate observations do not determine a correct count. This viewer
lets the maker inspect all three count possibilities directly rather than
assigning a count from an assumed boundary displacement. No new question is
required before using the controls.

## Verification and stopping point

Four Python checks cover agreement with all four frozen original/+5% variants,
exact projected-circle reconstruction, save/reload/backup behavior with protection
of unrelated documents, and invalid selections. Four JavaScript checks cover
pointer-centered zoom, pan/resize alignment, whole/patch framing and rejection
of stale slider replies. Python and JavaScript syntax checks pass. Fresh lower,
middle and upper range calculations are [recorded with source hashes](review/r182/validation.json). These are backend
and viewport checks; a browser/launcher/server interaction test was not run.

```bash
.venv/bin/python -m unittest discover -s photo2 -p test_tangent_viewer.py
node photo2/tangent_viewer/viewport.test.mjs
```

The app saves only explicit viewer choices, preserving manual annotations and
all old comparisons. Model count and helicity remain hypotheses; a selected
count is not verified closure or automatic reconstruction. Saved choices include
source-photo/model/UI hashes and the exact parameters.

Stopping point: deliver the requested adjustable viewer. Next bounded task:
read the maker's saved preferred count and assess remaining drift on an adjacent
unfitted patch. Recommend **gpt-6.1-sol / High**, same session; no `/new` needed.
