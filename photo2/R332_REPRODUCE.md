# Reproduce R332

Use existing Python3.12 `.venv` with NumPy/SciPy/Pillow/Playwright. Historical
inputs are read-only. Scientific commands require a fresh output directory.
No new detector installation, renderer or pattern model is needed.

```sh
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export MPLCONFIGDIR=/tmp/r332-mpl
.venv/bin/python -m photo2.r332.audit --output /tmp/r332-audit
.venv/bin/python -m photo2.r332.recover --output /tmp/r332-recovery --passes 4 --budget 180
.venv/bin/python -m photo2.r332.finalize --run /tmp/r332-recovery --output /tmp/r332-final
.venv/bin/python -m photo2.r332.reference --run /tmp/r332-final
.venv/bin/python -m photo2.r332.viewer --run /tmp/r332-final --output /tmp/r332-review
```

The 180-second limit is checked after each complete pass. Delivered inference
used71.5s after imports, and stopped at a zero-addition fourth pass. It reuses the
R266 selected12/selected6 and R275 caches; it does not rerun their detector or
search for a new winding. Compare parsed scientific JSON excluding timing fields;
gzip headers may differ. No random sampler is used except the deterministic
every-eighth-observation retrospective coordinate check.

Principal delivered artifacts:

- `r332/audit/audit.json`: baseline, R331 panel omissions, all38 original unindexed
  records and six coordinate-neighbor pairs absent from the original working graph.
- `r332/audit/input-seal.json`: frozen source hashes.
- `r332/development/native-location-v4/`: selected completion run,2603 cached
  candidates, full proposal ledger and four iteration records.
- `r332/results/graph.json.gz`: complete additive graph and observations;167
  accepted assignment records with native pixels, anchor IDs and predictions;
  provisional/unassociated candidates and pure predictions in separate lists.
- `r332/results/summary.json`: exact count accounting.
- `r332/results/omissions.json.gz`: remaining22 original unindexed records,
  unresolved links, provisional groups, candidate aliases and pure predictions.
- `r332/results/provenance.json`: source run/hash and final integrity-screen cost.
- `r332/results/extended-reference.json`: post-freeze full-inventory R161 check,
  36/40 associations and74/86 links,zero wrong; the original frozen check stays separate.
- `r332/review/`: offline viewer, complete static comparisons, per-tile label CSVs,
  exact native crops, regional counts and browser screenshots/receipt.
- `r332/development/initial/`, `appearance-v2/`, `expanded-cache-v3/`, `pre-native-location-final/`: preserved rejected/intermediate
  inference epochs; source snapshots explain their changes. Do not combine counts
  from different epochs or use the first color classifier as the final result.

Independently coded scientific verification reads the delivered final data:

```sh
.venv/bin/python -m photo2.r332.verify --output /tmp/r332-verification.json
```

It independently reconstructs baseline coordinates, occupancy modulo H, every
edge equation, connectedness, original-pixel material support, all final native
corridors, every new target-excluded regression, literal crop equality and fixed
R161 regression. It never calls the completion fitting implementation. Historical
preservation is checked against `4b6c9a2`. This is numerical/provenance validation,
not a newly blinded independent photographic annotation dataset.

Viewer checks use the previously authorized local Chromium launcher:

```sh
/home/rharris/.local/bin/beads-chromium-review photo2.r332.browser_check
```

This exercises the actual offline JavaScript, pan/zoom, stable-ID recentering,
three directions, observation-status switches, native pixel/prediction overlays,
desktop/narrow layouts and all11 static comparisons. Repository-relative report
and original-image links assume the delivered directory depth; a `/tmp` review
requires matching layout or another checkout for browser testing. Scientific
verification of fresh outputs does not depend on viewer link paths.
