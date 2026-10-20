# R339 reproduction

Start from `f6ed047543c647dd30d7efda97244861a202fbc2`, branch `photo-2-strategy-v3`. Use the existing `.venv` and original photograph/caches; no training, renderer, count or winding search.

```bash
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r339.replay --output /tmp/beads-r339-fresh
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r339.verify --root photo2/r339
/home/rharris/.local/bin/beads-chromium-review photo2.r339.browser_check
```

Choose a fresh replay path. Stages are maker → classify → compare → apply → analyze → review → independent verify. `R339_RUN_ROOT` redirects generated inputs. Exact decoded JSON comparison ignores only measured `seconds`; native PNG/HTML/JS/CSS artifacts compare byte for byte. Gzip timestamps are excluded from content fingerprints. `performance.json` records stage timing and peak child RSS.

The exact maker decisions and documented native ownership judgments in `apply.py` are manual inputs, not rediscovered independent truth. The simple rule has one selected 0.40-spacing aperture; 0.35 and 0.45 are fixed robustness checks. Maximum RGB channel supplies hue-independent brightness; the upper 20% tail is excluded, with ties retained. Nearby reference classes and all photographic decisions are frozen before fixed 208 analysis. No expected pattern color enters classification or its reference choices. The old three-radius/two-extent classifier is freshly recomputed for all 1,058 active records solely as a benchmark.

Selected outputs live under `photo2/r339/`: `maker/` exact decisions/seal; `classification/` all 1,058 original supports, 3,174 common apertures and old/new decisions; `comparison/` matched controls and literal suspect contexts; `results/` corrected overlay, freeze, protected colors and changes; `analysis/` fixed-cohort 208 block, all contributing IDs, unchanged-color target scores and post-freeze occurrence checks; `review/` offline native questions, full own-panel keys, current diagrams, optional body samples and source ledger. `verification.json` and the browser receipt are separate checks.

`development/` preserves the rejected weighted-luminance trial, its native failure examples and preliminary comparison. It is not the selected classifier. All R332–R338 scientific files remain unchanged. The geometry is the R338 1,040-site/2,287-link graph; only six recorded colors change in this overlay.
