# Reproduce the curated materials

[Overview](overview.md) · [Graph-paper API](../graph-paper.md) · [Source manifest](provenance.json)

All research references are pinned to
`628351437842b2ecd05f8a1765d17449fbea61f9`, branch `photo-2-strategy-v3`.
The default branch and Pages build never fetch or require that archive.

## Small maintained replay on master

Requires Python 3.10+ (standard library) and Node 20+ for JS syntax checking.
There is no npm install, server dependency, private data or runtime API call.

```sh
python3 -m unittest discover -s tests -v
node --check site/app.js
python3 -m beadwork.graph_paper 'BRYBRYBRYBRYBRYB?' --start 5 > /tmp/layout.json
python3 scripts/build_site.py
python3 scripts/build_site.py --check
python3 -m http.server 8000 --bind 127.0.0.1 --directory dist/beads
```

The builder generates only presentation SVG and HTML from the supplied candidate
dataset. It changes no historical image or scientific evidence. The viewer uses
the same maintained Python layout, with separate R344/R347 masks. Its default
shows current strict unknowns; provisional completion and historical epoch are
explicit choices. The [independent tests](../../tests/test_graph_paper.py) cover
all 192 historical length/origin/strip combinations plus direct integer
enumeration, primitive directions, double seams, copies, partial-row cuts and
ellipse clearance. The extraction parity receipt is
[promotion-checks.json](evidence/promotion-checks.json).

`provenance.json` records exact source paths, source commit, byte lengths and
SHA-256 hashes for every copied image/receipt and extraction input. Curated
`data/candidate.json` copies the named assessment entries, source IDs, geographic
blocks and counts. Strict strings mask the unchanged candidate wherever the
corresponding saved status is not supported. This is a presentation extraction,
not a new color assessment. `data/photo-questions.json` copies the first three
saved questions' coordinates/crop boxes; it contains no new answer request.

`scripts/publication.json` is the explicit file allowlist. `--check` fails on
unexpected files, changed copied bytes, missing local HTML links, stale generated
output, symlinks or the size budget. Historical demo assets are included. Large
master photographs unrelated to the site stay in Git but are not published.
The Pages workflow uploads **only `dist/beads`**, never the checkout.

The original gallery and simulated-bracelet HTML stay byte-exact in Git. The
movie `beads.mp4` was absent from master; its one dead link is routed in the
published copy to `legacy-movie.html`, explaining that absence. Existing stills
and source links work. Low-resolution original-example checks use system
POV-Ray 3.7 at eight midpoint clock values, without changing the scene source.

Optional browser QA requires Playwright and Chromium. With a local server on
port 8765, run `python3 scripts/browser_check.py`; use `--base-url` to check the
published URL. The script checks desktop/tablet/390px/320px layouts, both epochs,
unknown masks, selection, source lists, zoom, keyboard, images, gallery links and
JavaScript-disabled presentation. Screenshots are optional via `--screenshots`.

## Full historical replay is a separate optional checkout

The research tree has roughly 7.9 GB of uncompressed tracked content and many
coupled dependencies. Use a fresh detached worktree or checkout at the fixed
commit if you deliberately want to reproduce those experiments. Do not run the
commands below from master or point them at an active scientific checkout.
They are documented commands, **not commands executed for this promotion**.

| Result | Relevant source/configuration | Saved evidence and practical command |
|---|---|---|
| R344 graph-paper/statistics | `photo2/r344/graph_paper.py`, `verify_graph_paper.py`; `pattern208.json`, `graph.json.gz`, `evaluation.json` | [Full instructions](https://github.com/rharriszzz/beads/blob/628351437842b2ecd05f8a1765d17449fbea61f9/photo2/R344_REPRODUCE.md); `OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r344/replay.py`; NumPy/SciPy/Pillow/Matplotlib plus historical dependencies |
| R345 full necklace | `photo2/r345/render.py`, `verify.py`, `config.json`; R344 pattern/graph, R282 centerline and research `beads.pov` | [Full instructions](https://github.com/rharriszzz/beads/blob/628351437842b2ecd05f8a1765d17449fbea61f9/photo2/R345_REPRODUCE.md); `OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r345/replay.py`; Python NumPy/SciPy/Pillow and POV-Ray 3.7 |
| R346 whole-loop shadow | `photo2/r346/deliver.py`, `shadows.py`, `verify.py`, `config.json`; original R345 `shape.inc`/`beads.inc` and frozen measurements | [Full instructions](https://github.com/rharriszzz/beads/blob/628351437842b2ecd05f8a1765d17449fbea61f9/photo2/R346_REPRODUCE.md); `OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r346.deliver`, then `-m photo2.r346.verify`; add Matplotlib; full soft-shadow rendering is expensive |
| R347 maker overlay | `photo2/r347/assess_answers.py`, archived `answers/maker-2026-10-20.json`, frozen R344 inputs | [Assessment/instructions](https://github.com/rharriszzz/beads/blob/628351437842b2ecd05f8a1765d17449fbea61f9/photo2/r347/answers/ASSESSMENT.md); `python3 -m photo2.r347.assess_answers` |
| R348 saved-graph sensitivity | `photo2/r348/analyze.py`, `validate.py`, `input-seal.json`; R344 graph and R347 assessment | [Methods/limits](https://github.com/rharriszzz/beads/blob/628351437842b2ecd05f8a1765d17449fbea61f9/photo2/r348/SENSITIVITY.md); `python3 -m photo2.r348.analyze`, then `python3 -m photo2.r348.validate` |
| Visibility figures | `photo2/retrospective/visibility/render_figures.py`, generated `.pov` scenes, reused rounded macro | [Full instructions](https://github.com/rharriszzz/beads/blob/628351437842b2ecd05f8a1765d17449fbea61f9/photo2/retrospective/visibility/README.md); Python/Pillow and POV-Ray 3.7; PDF export additionally needs Playwright/Chromium and DejaVu fonts |

All listed source paths resolve beneath the
[fixed research tree](https://github.com/rharriszzz/beads/tree/628351437842b2ecd05f8a1765d17449fbea61f9).
Normal replays use saved parameters. Refitting switches such as R345 `--calibrate`
or R346 search commands are unnecessary for reproduction and are outside this
curation task. Do not substitute rejected `development/` epochs.

## What the existing receipts establish

Selected historical receipts remain exact copies in [evidence](evidence/):

- R344's independent statistics and graph-paper checks, including its 192 general
  cases, 77,408 ellipse-cut checks and 174,922 horizontal steps.
- R345's 2704 emitted transforms, closure/winding, 8112 separating certificates,
  macro bore/surface checks and 19-artifact fresh replay.
- R346's 162 sealed inputs, whole-loop/both-side coverage, independent rendered
  paper samples, sampling convergence and embedded-profile sensitivity.
- R348's independent weighted-graph/walk/support/period validation.
- The synthetic visibility examples' exact-front and surface-owner checks.

These receipts certify the original software calculations and saved scene/data
properties within their stated premises. This promotion does not rerun historical
scientific campaigns or turn those receipts into independent physical evidence.
Full large inputs, detailed certificates and original tests stay on research.
