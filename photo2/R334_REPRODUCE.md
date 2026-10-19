# Reproduce R334

Use the existing Python3.12 `.venv`, NumPy/SciPy/Pillow/Matplotlib and Playwright.
No installation, detector bank, network scientific input or physical renderer.
Historical R330–R333 files are read-only inputs. The first pigment decision is
intensity-only black testing; RGB red/yellow inference is executed only after
not-black, and unknown first decisions abstain.

A fresh replay of the four main scientific stages, including measured process time/RSS and parsed
comparison with delivery(excluding time fields only):

```sh
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r334.replay --output /tmp/r334-replay-new
```

The output must be new. The measured delivered replay takes about104s and peaks
at2.71GiB, including native evidence arrays and comparison parsing. The receipt
and complete fresh outputs/stdout/stderr remain in the requested directory.

Manual stages, each writing a new directory:

```sh
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export MPLCONFIGDIR=/tmp/r334-mpl
export R334_RUN_ROOT=/tmp/r334-manual-new
.venv/bin/python -m photo2.r334.corrections --output "$R334_RUN_ROOT/corrections"
.venv/bin/python -m photo2.r334.classify --output "$R334_RUN_ROOT/classification"
.venv/bin/python -m photo2.r334.export --output "$R334_RUN_ROOT/overlay"
.venv/bin/python -m photo2.r334.analyze --output "$R334_RUN_ROOT/analysis"
.venv/bin/python -m photo2.r334.controls --output "$R334_RUN_ROOT/controls"
.venv/bin/python -m photo2.r334.review --output "$R334_RUN_ROOT/review"
```

`R334_RUN_ROOT` redirects only new-round dependencies; old photos/maps/keys stay
fixed. Compare JSON excluding `seconds`/`sampling_seconds`; gzip headers may vary.
All seeds are explicit in reused R333 search/control code and R334 analysis334.
The in-memory R333 algorithm adapters write only the specified R334 directories.

Native photographs in the review are literal crops. Enlarged annotated images
are separate files. Offline image/report links assume repository depth; fresh
`/tmp` scientific outputs do not require those links. Use a matching checkout
layout to inspect a fresh page. All1600 classifier support IDs and exact used/
excluded pixels are retained, including abstentions and unassociated groups.

Independent checks, without calling classifier/fitting/tracing implementations:

```sh
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r334.verify --output /tmp/r334-independent-check.json
```

`--run /tmp/r334-manual-new` checks a fresh full output including literal crops.
Supplemental controls can be checked separately with
`OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r334.verify_controls`.
The main verifier recalculates maker-reference keys, native annular intensities,
hue-free lighting masks, first-stage decisions/order, graph equations/occupancy,
moved native corridors, all1624 primary fits, path equations, rejected stripe
collisions, R161 regression and historical preservation. It is not a new blind
photographic accuracy assessment.

Run the actual offline desktop/narrow viewer checks with the approved launcher:

```sh
/home/rharris/.local/bin/beads-chromium-review photo2.r334.browser_check
```

The initial actual-R333 DOM/expanded-key inspection is preserved separately in
`r334/inspect_review.py` and `development/R333-dom-inspection.json`, with screenshots
of the exact two named comparison panels. The final browser test checks R334's
layer order, all1600 IDs, separate yellow/black bodies, no fabricated yellow lattice
site, pixel switches, real zoom/pan/recenter, maps/conventions and offline assets.

Key artifacts:

- `corrections/ledger.json`, `overlay/maker-corrections.csv`: exact photograph /
  panel / local-number / stable-ID / original-coordinate mapping; eight unique
  corrections, eleven panel references and duplicate-mention accounting.
- `overlay/graph.json.gz`: authoritative maker overlay,1064 observations,
 1041 unchanged lattice coordinates and2285 unchanged equations. Original raw
  evidence remains in R332 and is linked in each reviewed observation.
- `classification/audit.json.gz`:1600 complete support records, all three radii,
  excluded reflection / annular / later body pixels, scalar intensity tests,
  lighting-reference IDs, red/yellow-only cross-fit votes and abstentions.
- `overlay/ranked-suspects.*`, `complete-classification.csv`: provisional rankings,
  independent evidence columns and the full scan. No extra accepted corrections.
- `analysis/analysis.json.gz`, `analysis/periods.csv`: four matched layers, all
 200–399+104 fits,40 saved-map scans,18 exact-divisor checks,176 cached G fits,
 16 rejected whole-stripe transforms and additional family conventions.
- `analysis/{raw,color,relocated,provisional}/`: complete flexible/regular traces,
  continuation rules, measured counterparts and spatial tests. All automatic
  layers remain diagnostic, with original/maker layers separately preserved.
- `controls/`: twelve geographic control tables, fixed2/5/8/11 cohort, exposed
  maker/reference controls and automatic-training feedback on unchanged targets.
- `review/`: exact R333 before panels, corrected overlays/matched lattice panels,
 22 literal crops,14 detailed pixel/distribution panels, all stable-ID keys,
  linked canvases, screenshots and browser receipt.
- `input-seal.json`, `verification.json`, `performance.json`, `manifest.json`,
  `delivery.json`:346 historical hashes, independent checks, fresh replay,
  scoped delivery hashes and independently verified remote scientific commit.

Earlier RGB-body, grayscale-only, pre-follow-up and export-failure epochs remain
under development with source snapshots. Their outputs are superseded, not
extra accepted detections/corrections. The black-first/all-channel selected
classifier and maker overlay are the delivered scientific layers.
