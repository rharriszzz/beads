# R297 standalone search and photographic debugger

From the repository root, the launcher selects `.venv` automatically:

```bash
python3 photo2/phase2_autofit.py --preset medium --output photo2/output/r297-my-run
```

The default is the R297 section-balanced objective with a soft prior-fit preservation
term. Search includes both hands, multiple counts, open and closed families, local
metric restoration, compact shared fields and alternative open cuts. It never
assigns a repeating color pattern. A positive full-chain nonintersection certificate
is required for selection. Unresolved certificates and demonstrated collisions are
reported separately.

Resume with cumulative limits; omit settings frozen at creation:

```bash
python3 photo2/phase2_autofit.py --resume --hours 1 --max-evaluations 3000 --output photo2/output/r297-my-run
```

SIGINT/SIGTERM saves at a transaction boundary; a hard kill recovers completed
candidate records without repeating them. A run-directory writer lock prevents
concurrent writers. Source, numerical environment and photographic input changes
invalidate resume. Use a new destination after implementation changes. Limits are
checked between trials; native final export adds overhead. Patience and convergence
can stop earlier than the budget. These stopping rules do not establish optimality.

Generate the native diagnostic review without further optimization:

```bash
python3 photo2/phase2_autofit.py --review-only --output photo2/output/r297-my-run --serve
```

Open `http://127.0.0.1:8297/review/debug.html`. The same `review/debug.html` works
as a local file. Click the photograph, choose any of 32 sections, filter failures,
or inspect nearby observations, contact margins and the proposed seam. Raw pixels
always remain unmarked in the first panel. Other panels compare R296, R297 and a
competing family; the R295 button shows the original local baseline. Measured cyan
supports can be toggled on the candidate crop. Numerical evidence separates original
measurement/provenance, model predictions and conditional comparisons.

`review/index.html` contains native full-photo overlays, parameter alternatives,
CSV positions and complete visibility/contact/correspondence exports.
`exports/regions.csv` compares all geographic sections. `failure-atlas.json.gz`
contains every evaluated observation and its failure mechanisms; per-model
`disagreements-*.json.gz` contains original photographic cues and predicted ownership
for paper, coherent-material cuts, conflicting colors and uncovered material.
`index-continuity.json`, `near-contacts.json`, and `circuit.json` report index jumps,
separating-plane margins and seam geometry. A small positive plane margin is a
lower bound on separation, not the exact closest-surface distance. Apparent index
jumps, color/paper proxies and occlusion competition require photographic inspection.

Seal only when stopping optimization of that run:

```bash
python3 photo2/phase2_autofit.py --review-only --seal --output photo2/output/r297-my-run
```

The frozen model list precedes retrospective reserved/buffer evaluation. Sealed runs
cannot resume. R296's reserved results have already been revealed: they are not new
holdouts in R297 or future uses. Validation is explicitly used for model selection.
No untouched independent photographic evidence is claimed. Repeated splitting of
this same photograph cannot establish external reconstruction accuracy.

For controlled experiments, `--objective legacy`, `no-patches`, `no-boundaries`
and `no-preservation` expose documented ablations. They are fixed at run creation.
Scores from different objectives must not be compared numerically as if identical.
The original R296 modules and original scientific artifacts remain unchanged.

Checks:

```bash
.venv/bin/python -m unittest photo2.r297.tests
.venv/bin/python -m photo2.r297.verify
/home/rharris/.local/bin/beads-chromium-review photo2.r297.browser_check
git diff --check
```

The curated delivered review is `photo2/r297/results/pilot/review/debug.html`.
Serve the repository with `.venv/bin/python -m http.server 8297 --bind 127.0.0.1`
and open `/photo2/r297/results/pilot/review/debug.html`, or open that file directly.

The delivered pilot uses `--max-evaluations 768 --seconds 1800 --patience 512
--seal`. It is immutable and cannot resume. For a subsequent longer study, use a
new output directory; identical seed/settings replay the initial search. Keep that
new run unsealed while resuming it. A different seed changes cold hypotheses and
exploration, and must be reported as a new development experiment.

The final source snapshot is in `r297/checkpoints/final-source`; medium and first
ablation sources are separately archived. The two discarded station-transfer
probes and unsafe phase-transport cases remain in `r297/results`. The preliminary
UI smoke review was regenerated after display-only repairs and is a development
artifact, not the delivered frozen pilot. For an exact earlier R296 reproduction,
use its scientific commit in a separate checkout; the current shared launcher now
selects R297. No original R296 scientific module or result was edited.
