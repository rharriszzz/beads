# R315 reproduction

Open `photo2/r315/results/index.html`. The central24-row table links the exact
photographic crops and ray arrays. Read the report before interpreting conditional
indices or removed-occluder counterfactuals as physical candidates.

Use repository Python3.12. All R314 inputs and sources are unchanged. Inputs and
R315 sources are hashed in `r315/results/provenance.json`; original HEAD, deadline
and photograph hash are in `results/start.json`. All trial parameters, failures,
contact classifications and selected full-chain positions are retained.

## Validate the committed artifact

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  .venv/bin/python -m unittest photo2.r315.tests photo2.r314.tests photo2.r314.tests_extra
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  .venv/bin/python -m photo2.r315.verify
/home/rharris/.local/bin/beads-chromium-review photo2.r315.browser_check
```

Verification rewrites only its receipt. After later scientific revisions, use this
commit in an isolated checkout because historical-preservation checks intentionally
reject changes to pre-R315 evidence. The trusted browser wrapper is machine-specific;
elsewhere use Playwright Chromium and run `photo2.r315.browser_check` directly.
No network is needed by the static review.

## Recompute in a separate disposable checkout

Preserve the delivered `photo2/r315/results` first; these commands overwrite R315
outputs and are not restart/resume interfaces. Never remove historical R314 results.
Copy `start.json` into the disposable destination, adjusting its parent HEAD only
if verifying against a different checkout. Set `MPLCONFIGDIR=/tmp/r315-mpl`,
`OPENBLAS_NUM_THREADS=1` and `OMP_NUM_THREADS=1` for each command.

```bash
.venv/bin/python -m photo2.r315.diagnose
.venv/bin/python -m photo2.r315.sensitivity
.venv/bin/python -m photo2.r315.experiment
.venv/bin/python -m photo2.r315.narrow
.venv/bin/python -m photo2.r315.followup
.venv/bin/python -m photo2.r315.review
.venv/bin/python -m photo2.r315.audit
.venv/bin/python -m photo2.r315.verify
```

`experiment` has a240s internal proposal allowance after fixed controls; `narrow`
has a110s truncation guard. Saved sequences contain239 and141 settings. Machine
speed can change truncation; exact delivered settings are replayable from each
trial without any fitting. No command changes illumination or optical assignment.
The specification/report and handoff text are curated, not overwritten by a generator.

`model.Chain` adds post-construction image translation and compact phase/station
fields; zero settings are exactly the R314 model. `refined_trace` uses the same
native kernel, continues only unfinished rays, and retains a valid upper bound on
unfinished hit depth. `verify.root_owner` separately isolates roots of the original
implicit solid along each formerly uncertain R306 ray. It does not call that marcher.
`measurement.measure_readiness` separates unknown independent-evidence pixels from
unrelated unknown ROI pixels and separates missing brackets from finite distances.

The source-unit radius is a gauge, not calibrated millimeters. Bounds and engineering
thresholds are not measured strain or statistical confidence intervals. This is a
controlled negative/partial result, not a recovered necklace or verified index chain.
