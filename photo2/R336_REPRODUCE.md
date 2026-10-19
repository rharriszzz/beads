# Reproduce R336

Baseline R335 delivery `8c8ecab00f726c2010c2571e9ada953a60e878dc`, branch
`photo-2-strategy-v3`. Use the existing `.venv`; no dependency installation,
scientific network input, detector/physical campaign or broad pattern search.

A fresh replay in a new directory records time/RSS and exact comparisons:

```sh
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r336.replay --output /tmp/r336-replay-new
```

Manual stages below use selected paths; use an isolated checkout with new output
directories, or set `R336_RUN_ROOT=/tmp/r336-manual-new` and use matching
`--output` subdirectories. Historical source locations remain fixed.

```sh
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r336.evidence --output photo2/r336/evidence
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r336.revise --output photo2/r336/results
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r336.diagnose --output photo2/r336/analysis
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r336.review --output photo2/r336/review
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r336.verify
/home/rharris/.local/bin/beads-chromium-review photo2.r336.browser_check
```

The evidence investigation must complete before revision. Historical R332–R335
sources/results are read-only. To reproduce a delivered checkout, run in an
isolated checkout or use the fresh replay command supplied in `r336/replay.py`;
do not overwrite delivered scientific artifacts. JSON comparison ignores measured
`seconds` only; gzip headers may differ. Native PNGs must remain pixel-exact.

`evidence.py` independently samples the old dark-response coordinates and audits
all687 stored native records. Its corrected contract cannot admit/propagate a
separate body from intensity alone. `revise.py` resolves exact R335 local numbers,
sets independent role flags, preserves all evidence, and rechecks five native
corridors plus common local geometry and modulo-H equations. `diagnose.py` compares
fixed cohorts under the same two staircase rules and208 consensus; no template or
period selection is rerun. `review.py` shows two current visible row questions;
completed maker cases appear only in explicitly completed appendices.

`verify.py` independently re-reads native pixels and source keys, checks retained
and active identities/links, fixed-cohort diagnostics, every path equation, native
crops, R161 regression and910 historical hashes. The browser test opens the actual
R335 page and expands all ten original keys without editing historical artifacts,
then checks the current page, exact-pixel controls, repaired-link illustrations,
zoom/pan, navigation, narrow layout and offline loading.

Machine-readable entry points:

- `evidence/investigation.json.gz`: exact pixels, causal chain and global risk scan.
- `results/maker-decisions.json`: ten precise photo/feature/ID mappings, statuses,
  colors, role exclusions, two accepted1=P associations and alias distinctions.
- `results/retained-graph.json.gz`: all1,064 historical records/1,041 coordinates,
  role flags and2,290 retained links, including inactive evidence.
- `results/graph.json.gz`: selected1,057 active records/1,039 sites/2,284 links.
- `results/link-audit.json`: before/after obstruction, foreground, spacing,
  equations and matched local reflection brightness.
- `analysis/diagnostics.json.gz`: six consistent cohorts, fixed-rule paths,
  recurrence pairs, remaining marginal flags and all208 consensus entries.
- `review/evidence-pixels.json.gz`: every plotted pixel and original coordinate.
- `verification.json`, `input-seal.json`, `manifest.json`, `delivery.json`:
  independent checks, historical preservation, scoped hashes and remote receipt.

The recorded fresh run is `/tmp/r336-replay-01`. Its initial final comparison
incorrectly included an embedded measured `seconds` field in viewer-data byte
equality; comparison-only mode then passed parsed data excluding time and exact
HTML/JS templates/native PNGs. The scientific stages completed once.
