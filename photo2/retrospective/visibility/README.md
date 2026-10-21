# Illustrated pattern visibility explanation

Review documents:

- [Illustrated Markdown](../../PATTERN_VISIBILITY_ILLUSTRATED.md)
- [Illustrated PDF](../../PATTERN_VISIBILITY_ILLUSTRATED.pdf)
- [Previous prose draft, preserved](../../PATTERN_VISIBILITY_EXPLAINED.md)

These are educational examples and a presentation of saved R347 evidence.
There is no new inference, classifier, pattern selection, geometry fit or
lighting fit. Historical scientific inputs are read only. The bead shape macro
is reused verbatim from `beads.pov`; the illustrative helix and opaque core are
explicit constructed geometry, distinct from the R345/R346 necklace scene.

## Reproduction

From the repository root, with POV-Ray 3.7, this checkout's Python environment,
DejaVu Sans at `/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf`, and the existing
Playwright Chromium installation:

```bash
.venv/bin/python photo2/retrospective/visibility/render_figures.py
PLAYWRIGHT_BROWSERS_PATH=/home/rharris/.cache/beads-playwright .venv/bin/python photo2/retrospective/visibility/build_pdf.py
```

The first command writes the `.pov` sources, PNG images, gzip-compressed verbatim renderer logs and
[verification.json](verification.json). It verifies primitive periods, distinct
adversaries under rotation/reversal, unchanged source hashes, front/back color
differences, owner-ID visibility, illustrative bead nonintersection by enclosing
spheres, all 208 chart positions, alternating 6/7 row counts and saved coverage.
Owner-ID passes use no antialiasing and linear file gamma; illustrated figures
use antialiasing and the renderer's standard display transfer. No radiosity,
transmission or reflection carries hidden pigment into the front comparison.
Pixel equality is checked on the isolated `check-front-A.png` / `check-front-B.png`
images, without the differing panel labels of the composite illustration.

The second command validates Markdown links, the full table and illustrated toy
words, then exports a searchable, tagged US Letter PDF with embedded images,
bookmarks and linked references. Its [PDF receipt](pdf-export.json) records source
and image hashes, complete text extraction and page-bound checks. Browser launch
can require sandbox approval in Codex. HTML and page-preview files are temporary.

## Figure sources

- `01-hidden-patterns`: two primitive 26-bead words, identical fronts and different backs.
- `02-phase-shift`: end-on phase arithmetic, not a measurement of hidden pigment.
- `03-phase-shift-tubes`: four ray-traced windows of a 27-bead construction.
- `04-complementary-views`: 52-bead word, three source views and combined readings.
- `05-full-pattern`: current 208-color candidate, 32 alternating 6/7 rows and seven R347 uncertainty marks.
- `06-observation-coverage`: complete occurrence matrix overview for zooming.
- `07-coverage-000-103` and `07-coverage-104-207`: larger-label matrix panels used in print.
- `check-*`: independent flat owner/color passes for the illustrated scenes.

The 52-bead masks select clear front-facing phases, rather than all optically
visible surfaces. Their union establishes coverage with known indices, not an
automatic blind decoding algorithm. The phase-copy owner passes intentionally
record a small rear-facing glimpse in copy 1 and an edge surface in copy 2;
both remain excluded by the clear-reading rule.

Each coverage cell corresponds to a retained observation address: no missing
entry is filled from the candidate, and Q1 pigment is excluded. Unique indexed
sites make the 1040 occupied cells correspond to 1040 observations. The source
ID manifest is [the saved enumeration](../visibility-example-checks.json).
R347's geographic corroboration rule, distinct from occurrence coverage, is
used unchanged for the seven uncertainty marks. The two maker photo-based
yellow corrections have teal cell borders. The existing whole-necklace
comparison is reused from R346, without edits or a rerender.

## Preserved failed illustration

[development/rear-leak](development/rear-leak/README.md) preserves the initial
scene, generator and front/ownership images. It showed that a rear bead center
was insufficient to guarantee hidden surfaces. The delivered toy changes only
phases 3 and 10, instead of Draft 2's wider rear set, and swaps positions 3 and
16 instead of 4 and 17. All accompanying words and counts were updated together.
The previous Markdown and arithmetic manifest retain their original meanings.

The scientific evidence remains conditional on the saved lattice and indexing.
Physical count, exact topology, authentic original chart and detailed bead poses
have not been independently verified by these illustrations.
