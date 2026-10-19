# Reproduce R335

Start from R334 delivery `4e40da6a2b222ae1a755f0dc4d403e6d9ad7ec7f` on
`photo-2-strategy-v3`, using the existing `.venv`. No detector, classifier training,
period search, physical rendering, new dependency or scientific network input.

A bounded fresh replay records process time/RSS and checks exact scientific JSON,
viewer data/templates and native crops (excluding measured `seconds` only):

```sh
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r335.replay --output /tmp/r335-exact-new
```

Manual stages, with fresh output directories that must not exist:

```sh
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r335.application --output /tmp/r335-replay-new/results
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r335.review --run /tmp/r335-replay-new --output /tmp/r335-replay-new/review
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r335.verify --run /tmp/r335-replay-new --output /tmp/r335-replay-new/verification.json
```

The first stage reads R334's frozen global classifier evidence and current
authoritative overlay. It applies the eight newly accepted maker decisions plus
concordant red/black intensity results, retaining every inventory admission status
and all geometry. Its compact-reflection audit uses no hue or expected motif color.
The existing (16,16) diagnostic and 208 consensus are refreshed once; no repeat
length is searched or adopted. The second stage generates the current numbered
review, full keys and literal crops. All historical source paths remain fixed.

Compare JSON parsed from gzip/plain files, excluding only `seconds`. Native PNGs
must match pixel-for-pixel. Review links assume the same repository depth; fresh
`/tmp` pages need that layout for report/history links. Scientific checks do not
depend on those links. Selected outputs live under `photo2/r335/results/` and
`photo2/r335/review/`; `verification.json` is independent of application/view code.

The actual desktop/narrow/offline review test uses the approved Chromium launcher:

```sh
/home/rharris/.local/bin/beads-chromium-review photo2.r335.browser_check
```

It checks the current default, ten primary cases, complete keys, current black
blockers, matched examples, optional pixel masks, links/traces, zoom/pan,
next/previous, lower-priority records, native links and offline loading. The
review does not ask the maker to recheck the sixteen accepted maker targets.

`development/` retains selection/native-body contact sheets and the preliminary
compact audit. Those are diagnostic evidence, not additional accepted beads.
The initial independent verifier's raw-coordinate assertion was corrected to the
existing modulo-H equation, preserving the R334 winding convention and graph.
`input-seal.json` covers the 657 historical inputs; `manifest.json` covers scoped
R335 outputs and updated handoff files; `delivery.json` records remote confirmation.

The delivered scientific stages completed once under `/tmp/r335-replay-01`.
A final caption change initially differed only in escaped viewer text; after
normalizing the caption, `replay --compare-only` verified all already completed
fresh outputs without repeating the scientific stages. The selected performance
receipt records this explicitly.
