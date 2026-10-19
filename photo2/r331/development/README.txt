Preserved development epochs, not scientific inputs to final selection:

initial/analyze.py and initial/analysis.json.gz: first successful scan. Its
black-weight sensitivity overwrote the provisional .25 black-site weight, and
the robust diagnostic dropped the hierarchical parent after reweighting.
Corrected in results-final; main scans/nulls/G comparisons were unaffected.
results/ remains the original successful full run, byte-preserved.

initial/errors.py and initial/errors.json.gz, plus errors/: first latent-error
run, before adding a separately labeled frozen-graph bookkeeping control.
errors-v2/ is the final error study. Initial results remain unchanged.

First followup invocation failed before exporting any result: colored-only
per-color statistics attempted to average an empty black cohort. evaluate now
returns null for unavailable color statistics. The failed output directory
followup/ was left untouched; successful followup is written to followup-final/.
