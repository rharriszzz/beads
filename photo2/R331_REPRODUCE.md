# Reproduce R331

Start from branch `photo-2-strategy-v3`, baseline R330 commit `422a85e`, with
the delivered R331 source. Use existing `.venv/bin/python` (Python3.12), NumPy,
SciPy, Pillow, Matplotlib and Playwright. No new packages, detector, candidate
search, physical fit or rendering are required.

The scientific commands refuse to reuse an output directory. Write to fresh
paths; never overwrite the delivered historical evidence:

```sh
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export MPLCONFIGDIR=/tmp/r331-mpl
.venv/bin/python -m photo2.r331.analyze --output /tmp/r331-independent-analysis
.venv/bin/python -m photo2.r331.errors --output /tmp/r331-independent-errors
.venv/bin/python -m photo2.r331.followup --output /tmp/r331-independent-followup
```

Compare parsed JSON excluding `seconds`; gzip headers can differ. The first
command uses seed331 and19 trials per null family; the second uses seed33102.
The third is an explicitly post-scan diagnostic of fixed lengths305/306 and
cyclic-cut/black-exclusion sensitivity. It does not read newly searched maps.

Delivered final scientific artifacts:

- `r331/results-final/analysis.json.gz`: arithmetic/alias witnesses; all40 cached
  map rankings;419 leave-section-out fits; sensitivities;38 stronger nulls;
  all44 G alternatives on their own maps; partial motifs; six-site controls.
- `r331/results-final/periods.csv`: comparable period/count/prediction summary.
- `r331/results-final/input-seal.json`: frozen original/R330 source hashes.
- `r331/errors-v2/errors.json.gz`:416 perturbation records, model priors,
  real-data unverified flags and exact-duplicate bookkeeping control.
- `r331/followup-final/followup.json.gz`:305/306 observed partition equivalence,
  pair vectors, cyclic cuts, colored-only/equal-section controls, own-map G fits.
- `r331/development/`, `results/`, `errors/`: preserved initial epochs and
  documented failures; not inputs to final selection.

Read-only independently coded scientific verification writes a receipt only:

```sh
.venv/bin/python -m photo2.r331.verify --output /tmp/r331-independent-verification.json
```

The verifier checks the delivered final files; compare fresh reproductions with
those files separately. It rebuilds original coordinates and weighted fits without
calling the fitting implementation, checks counts/exclusion/alias witnesses,
own-map G prediction, frozen-neighbor controls, native crop pixels and historical
preservation. It does not certify photographic truth or a recovered design.

Offline review and ten-slide presentation are at `r331/review/index.html` and
`r331/review/presentation.html`; the PDF is `presentation.pdf`. To regenerate
presentation assets (writes only R331 presentation files) and check the browser:

```sh
.venv/bin/python -m photo2.r331.review
/home/rharris/.local/bin/beads-chromium-review photo2.r331.browser_check
```

`review --output NEW_DIRECTORY` can generate fresh photographic assets elsewhere;
report links assume the delivered repository-relative layout. The browser helper
uses the installed Chromium cache and produces desktop/narrow screenshots,
four problem-slide screenshots, a PDF, and a clipping/offline receipt. Use the
delivered layout or a separate checkout for a fully independent browser replay.

Every scientific comparison reuses R330's noisy observations. A computationally
held-out section is not new independent photographic truth. All corrections,
counts, windings and motif entries remain conditional hypotheses.
