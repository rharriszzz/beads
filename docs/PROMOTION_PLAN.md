# Curated promotion to master

Prepared 1 November 2026 before implementation. Integration branch:
`curate-research-pages`, based on master `5d1258cd99301ec803b193ee3b78d9d5ff745d7b`.
Research source throughout: `photo-2-strategy-v3` at
`628351437842b2ecd05f8a1765d17449fbea61f9` (21 October 2026).
No research merge, history rewrite, historical experiment rerun, or R349.

## Preflight and preservation

Remote fetch confirmed the expected research tip is the newest completed work.
Master has its own sine-note commit; the note's blob is already identical on
research. Master's original POV source differs and will remain byte-exact.
The research checkout contains unrelated untracked R340 work. A separate small
worktree protects it. About 884 GiB was available; Git, Python, Node, POV-Ray and
an existing Playwright/Chromium installation are available. GitHub repository
access reports admin/push permission. The old master worktree registration points
to a missing `/tmp` directory; leave that registration alone.

## Selection

Every source below is pinned to the research commit above unless marked master.
Sizes are approximate new tracked content, with a target under 20 MiB. Exact
copied-file hashes and extracted-data provenance will be recorded in
`docs/photo2/provenance.json`. The website has a separate explicit file allowlist.

| Class / original source path | Value and action | Destination | Dependencies / size | Evidence and qualification |
|---|---|---|---|---|
| Essential: `beads-photo-2.jpg` (already on master) | Use the original photograph without duplication | Existing root path | 1.3 MB already present | Compare master/research blobs; photograph is appearance evidence, not a complete bead census |
| Essential: `photo2/r344/graph-paper.png`, `graph-paper.pdf`, `graph-paper-numbered.pdf` | Copy authentic strict/provisional presentation and usable print downloads | `docs/photo2/assets/` | ~4.4 MB | SHA-256 equality; captions retain historical R344 199/2/7 and nine unknowns |
| Essential: `photo2/r345/output/render.png` | Copy complete numerical reconstruction | `docs/photo2/assets/` | ~6.8 MB | Exact bytes and saved verification; 2704=13×208 and geometry remain conditional construction choices |
| Essential: `photo2/r346/output/{comparison.jpg,shadow-fields.png,shadow-profiles.png,crop-inner-bend.jpg}` | Copy whole-loop comparison, metrology and enlarged detail | `docs/photo2/assets/` | ~1.4 MB | Hashes, captions, native dimensions; relative paper loss, retrospective geographic checks, not unique lamp calibration |
| Essential: `photo2/r347/review/q0{1,2,3}-native.png` and `questions.json` | Copy only three literal crops; extract their IDs/coordinates for captions | Assets and provenance | ~0.14 MB | Compare saved crop pixels to original; Q1 withheld, Q2/Q3 photo-based yellow; no repeat questions |
| Explanation: `photo2/retrospective/visibility/{01-hidden-patterns,04-complementary-views,05-full-pattern,06-observation-coverage}.png` | Copy four verified figures | Assets | ~1.9 MB | Hashes and existing `verification.json`; first two are synthetic constructed examples, latter two show candidate/saved evidence |
| Reusable: `photo2/r344/graph_paper.py` | Extract pure sequence geometry, remove only historical I/O entry point; add explicit public-input checks and standalone CLI | `beadwork/graph_paper.py`, tests, `docs/graph-paper.md` | Python standard library; <40 KB | Independent enumeration, 1/6/7 equations, seam, 7 sides, stepped cuts, negative indices and arbitrary lengths; no inference code |
| Reproduction: `photo2/r344/{pattern208.json,graph-paper-layout.json}`, `photo2/r347/answers/assessment.json` | Extract compact two-epoch candidate data; reuse maintained layout to build a small SVG viewer | `docs/photo2/data/`, site assets | Standard library; ~0.5 MB | Compare every promoted color/status to pinned sources; retain historical/current views and copy identity |
| Reproduction: `photo2/r34{4,5,6}/...verification.json`, `photo2/r348/validation.json`, visibility receipt | Copy selected small validation receipts with source attribution | `docs/photo2/evidence/` | <150 KB | Existing receipts are historical validation, not new physical evidence; pin full replay scripts/configs instead of copying coupled trees |
| Science/methods: `photo2/{RETROSPECTIVE,FUTURE_PROJECT_METHODS,R344_REPORT,GRAPH_PAPER_6_5_BEADS,R345_REPORT,R346_REPORT,R347_PATTERN_CONFIRMATION,PATTERN_VISIBILITY_ILLUSTRATED}.md`, `photo2/r348/SENSITIVITY.md` | Adapt into concise topical documentation and question-led public narrative | README; `docs/photo2/{overview,pattern,geometry-and-rendering,methods-and-lessons,reproducibility,research-history}.md` | Text <100 KB | Review every numerical claim against source; distinguish observed labels, conditional inference and synthetic construction |
| Historical only: `photo2/r345/{render.py,verify.py,config.json,output/}`, `photo2/r346/{deliver.py,shadows.py,verify.py,config.json,output/}`, R323–R343 and all other archives | Link to fixed source commit; keep coupled infrastructure, failed epochs, large diagnostics and ledgers on research | Pinned history/reproduction links | No archive copies | Do not regenerate inputs, annotations, labels, cameras, geometry or light |
| Existing master: every file, especially `beads.pov`, `BEADS_POV_SINE_ANGLE.md`, `beads.html` | Preserve; replace only the redirect landing `index.html`, retaining its history and links | Original paths | No new copies | Blob comparison against master; historic demo assets included explicitly in Pages publication |

## Delivery and checks

Use buildless HTML/CSS/JS with local assets, light styling, readable narrative,
and an SVG viewer generated from the extracted Python layout. No browser inverse
pipeline or runtime research dependency. Root index becomes the project site;
the historical demonstration stays at `beads.html`. GitHub Actions builds an
explicit allowlist into `dist/beads`, tests it and deploys that directory only.

Bounded validation: unit tests independent of the layout formula, extraction
parity with the pinned research code, copied-byte provenance, original crop
checks, local link/anchor/image checks, publication inventory/size tests, existing
master preservation, representative original POV renders, and desktop/mobile
browser checks of navigation, unknowns, epoch controls, selection and zoom.
Historical scientific tests remain unchanged and are linked, not rerun.

Review the complete staged diff, commit the integration branch, then integrate
into master without importing research ancestry or rewriting history. Push and
verify remote commit and GitHub Pages deployment. Once the URL is live, make a
separate scoped update to `rharriszzz/rharriszzz.github.io`, preserving its format
and running its existing tests. GitHub plugin tools lack Pages configuration;
use authenticated GitHub REST/CLI where available for that supported setting.

## Scientific publication contract

Implementation refinements: the final site preserves all 34 preexisting files
other than the old landing redirect byte-for-byte. The old simulated-bracelet
page links an absent, never-tracked `beads.mp4`; only its **published copy** routes
that link to a clear `legacy-movie.html` notice. Original source HTML is exact.
The final selected images/receipts total 14,717,685 bytes; the entire publication
is about 16.6 MiB, including inline SVG/data and the original gallery assets.
The independent graph-paper extraction matches all 192 historical dictionaries
and the exact current saved layout. Historical scientific tests remain unchanged.

Current R347: 201/0/7 and 1040/1040 retained-label agreement; all 208 residues
observed. Historical R344: 199/2/7 and 1038/1041. Do not collapse epochs. Q1 is
withheld, never independent yellow confirmation. Q2/Q3 are same-photo maker
judgments, not physical/chart verification. Seven sparse black positions remain
tentative. A/208 uniqueness requires the accepted lattice/H, specified counting
conventions, complete repeats and period bound. R348 is saved-graph deletion
sensitivity, not an image-inference rerun or a modified adopted graph. Physical
count, exact topology, camera/shape and authentic chart remain unverified.
