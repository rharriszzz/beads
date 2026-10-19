# Reproduce R337

Input commit `a6e16d54eb692f78a725de6fb56414d4f3e98843`, branch
`photo-2-strategy-v3`. Existing `.venv`; no dependency installation, detector,
classifier, model fit, renderer or network scientific input. Multiples of13 are
allowed. The maker hopes the shortest repeat is not a multiple; this has no
exclusion or score penalty.

Fresh complete replay, preserving delivered outputs:

```sh
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r337.replay --output /tmp/r337-replay-new
```

Manual stages, each analysis/search/review output must be a new directory:

```sh
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r337.analyze --output /tmp/r337-manual/results
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r337.bounded --output /tmp/r337-manual/bounded
R337_EXTRA_STATES=/tmp/r337-manual/bounded/states.json.gz OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r337.search --output /tmp/r337-manual/search-results
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r337.consequences --output /tmp/r337-manual/results --results /tmp/r337-manual/results --search /tmp/r337-manual/search-results
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r337.pattern --output /tmp/r337-manual/results
R337_EXTRA_STATES=/tmp/r337-manual/bounded/states.json.gz OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r337.review --output /tmp/r337-manual/review --results /tmp/r337-manual/results --search /tmp/r337-manual/search-results
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r337.verify --root /tmp/r337-manual
/home/rharris/.local/bin/beads-chromium-review photo2.r337.browser_check
```

The review's relative report/photo links assume its delivered repository location;
fresh replay verifies its science, templates and crops before browser-testing the
delivered offline page. JSON comparisons ignore measured `seconds` and
`peak_rss_mib` only. Gzip headers are not scientific values. PNG pixels and
HTML/JS/CSS/SVG must reproduce exactly.

- `analyze.py`: frozen 710 and complete1039 cohorts, direct spatial translations,
  signed cycles, all12 integer neighbor maps,1,969 small translation domains per
  cohort and learned measured staircase words. No broad fixed-index period scan.
- `bounded.py`: width32 recombination in two declared corridors; hard maker-link
  pruning and full downstream return replay, no color-guided growth.
- `search.py`:145 historical plus25 bounded paths, coherent extensions, all
  own-count exact lengths200–399, cyclic occurrence and geographic prediction.
  871 common original IDs ensure a matched comparison. All lengths allowed.
- `consequences.py`: constructed graph components/equations, full scalar identity
  collisions, map equivalence groups and conditional period-composition algebra.
- `pattern.py`: strict176/32 partial208 block, all conflicting IDs, proper-divisor
  witnesses and held-out predictions. No color correction or unknown filling.
- `verify.py`: independently coded artifact, prediction, arithmetic, exact native
  crop and historical preservation checks.

Machine-readable entry points are `results/analysis.json.gz`, `topology.json`,
`maker-review.json`, `*-translations.json`, `*-domains.json.gz`,
`*-staircases.json.gz`, `pattern208.json`/`.csv`, `consequences.json.gz`,
`bounded/states.json.gz`, `search-results/candidates.json.gz`, `replays.json.gz`,
`comparisons.json`, `scope.json`, and the independent verification/replay/browser
receipts. Every candidate records exact old links it would change and later-body
boundary contradictions. No proposed graph replaces R336.

Development epochs are retained and explicitly superseded: an initial import
syntax error; an incomplete NumPy-integer export; preliminary recent-review-only
protection; the original hard13 eligibility rule before the maker relaxed it;
and pre-normalization cyclic-occurrence groups. Their outputs never overwrite
historical rounds and are not selected final evidence. Successful stage and
fresh-replay timing is reported separately from those exploratory epochs.
