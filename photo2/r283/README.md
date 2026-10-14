# R283 reproduction and artifact map

Read [report](../R283_REPORT.md), [requirements](../R283_CHECKLIST.md), and
[28-panel photographic review](../review/r283/index.html). R282 code and evidence
remain unchanged. Python3.12 uses the existing `.venv`; native image operations
use NumPy/SciPy/scikit-image/Pillow. POV-Ray provides independent appearance and
identity rasters. No network or new package installation is needed.

From the repository root:

```bash
R283_OUTPUT=/tmp/beads-r283-replay OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r283.run
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r283.audit --replay /tmp/beads-r283-replay
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r283.tests
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r282.tests
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r283.review
/home/rharris/.local/bin/beads-chromium-review photo2.r283.browser_check
```

Use a **fresh** replay directory: `run` refuses to replace a completed Phase1.
The review command deliberately reads saved final results and writes curated PNGs.
Individual algorithm modules are development entry points and may overwrite their
target files; use `R283_OUTPUT` for further experiments. The final pipeline runner
performs ownership → coverage/freeze → development and fresh synthetic tests →
local fit/prediction/evaluation → second-region confirmation → global regression
and Phase3. It never reads historical manually assigned neighbors or fitted poses.

`results/phase1.json.gz` has all1092 stable records and unchanged native Attempt C
supports. `ownership.json` stores symmetric pair evidence and alternatives;
`coverage.json` stores signed support relationships, single-assignment longitudinal
bins, 24 flanking pairs and all eight reinterpreted gap regions. B supports are
retained for every yellow observation where available. The R282 A/B/C viewer is
linked from the new review. All reliability numbers are engineering weights.

`method-freeze.json` binds photo-only rules and original detector source before
fresh confirmation. Seed283501 became development after its five duplicate black
failures were inspected. Seed283601 is the independent 16-scene confirmation.
Both sets contain literal annuli, randomized appearances and certified packing;
`synthetic/` and `confirmation/` retain POV source, original rasters, truth,
certificates, detector outputs, and pair alternatives. Truth is evaluated only
after inference serialization. `*-results.json` contains full per-scene hits,
missed bodies, purity, duplicates, color, centroid and adjacency accounting.

`local/` is development, `local-confirmation/` is a separately selected region
at least250px away. Each has four frozen anchors, four independently measured
withheld supports, all cold/refined alternatives, a prediction freeze, native owner
arrays, evaluations, camera/phase/neighbor controls, actual photo crops and
independent POV renders. Local indices range−64…64 and have no global closure
meaning. An extended−80…80 bank verifies the crop has no finite-end ownership
artifact. Local `managed-rgb.npy` is the original ICC-managed crop, not a render.

`integrated/` reruns the preserved global Phase2 family from frozen R283 evidence:
ten count/hand fits, four full inventories, native visibility and measured colors,
then Phase3. Local improvements are not promoted into an unvalidated global model.
`uncapped/` retains exports and pattern alternatives before the explicit0.35
identity-weight ceiling. The strict Phase3 subset consequently has no usable
identity evidence; arbitrary leading all-unknown periods are abstentions.

`first-pass/` preserves the initial ownership/synthetic failure and the failed
short-bank local fit; `second-pass/` preserves the longer-bank fit that sacrificed
an anchor. `third-pass/` also retains the final bank-margin test predecessor: the81-bead bank still ended inside crop corners. Their source snapshots remain alongside outputs. No failed scientific
run has been replaced. The final fit penalizes the worst anchor and compares
exact first-hit assignments with physical-center proxy assignments.

Audit compares all original tracked photo2/source-geometry/source-photo files
against the pre-R283 commit, native crops against decoded source pixels, final JSON
numerical content, exact array contents and decoded replay rasters. Source/freeze
metadata differences caused by later output-path support are explicitly excluded;
all numerical parameters, support masks, predictions and evaluations must match.
POV PNG container hashes are verified within each run; decoded pixels are compared across runs because POV embeds render timestamps. Browser screenshots are environment-dependent and separately checked.

The photograph uses EXIF-transposed native pixel centers, x right/y down. Signed
normal is `(-tangent_y,tangent_x)` along the saved image-derived curve; its sign is
only a side convention. Conservative interiors are never full silhouettes.
