# Run the R296 whole-necklace optimizer

From the repository root on `photo-2-strategy-v3`. `python3` is only the bootstrap:
`photo2/phase2_autofit.py` re-executes with the repository `.venv/bin/python`.
No virtual-environment activation, AI model, network service or renderer is used.
The frozen photograph/observations are specific to this necklace.

## Commands

Fast deterministic smoke (search and checkpoint, skip expensive native exports):

```bash
python3 photo2/phase2_autofit.py --preset smoke --output photo2/output/r296-smoke --no-review
```

Short search, including an offline native visual review:

```bash
python3 photo2/phase2_autofit.py --preset medium --seconds 300 --max-evaluations 160 --output photo2/output/r296-short
```

Unattended four-hour budget (may stop earlier on convergence or validation stagnation):

```bash
python3 photo2/phase2_autofit.py --preset long --hours 4 --max-evaluations 20000 --patience 1000 --seed 296 --output photo2/output/r296-long > /tmp/r296-long.log 2>&1
```

Resume after a budget stop, SIGINT/SIGTERM or interruption:

```bash
python3 photo2/phase2_autofit.py --resume --preset long --hours 8 --max-evaluations 40000 --output photo2/output/r296-long > /tmp/r296-resume.log 2>&1
```

Budgets are **cumulative** across resumes: the last command permits up to eight
hours total search, not eight additional hours. Seed, population, count bounds,
patience and minimum-improvement tolerance are fixed when a run starts. Omit them
on resume. `--hours` and `--seconds` are alternatives. The default presets are
smoke 120 seconds/8 proposals, medium 1800 seconds/600 proposals, long four hours/
100000 proposals; the first reached limit wins. Explicit flags override presets.

Open or regenerate a development review without further optimization:

```bash
python3 photo2/phase2_autofit.py --review-only --output photo2/output/r296-long --serve
```

Visit `http://127.0.0.1:8296/review/`. Stop the local server with Ctrl-C. The review
also opens directly as `photo2/output/r296-long/review/index.html`. Use `--port`
if another local server occupies 8296. Downloads are relative to the run directory.

When finished with a run, freeze its selected models and evaluate reserved cases:

```bash
python3 photo2/phase2_autofit.py --review-only --seal --output photo2/output/r296-long
```

**Sealing prevents further optimization of that run.** Until sealing, every budget
stop produces a resumable development review and leaves reserved outcomes unread.
Once reserved outcomes have been examined, the same cases in subsequent runs are
retrospective checks, not fresh independent confirmation. Do not select a new seed
or model from repeated reserved comparisons. The software cannot erase a person's
knowledge of prior results. A fresh experiment needs newly designated evidence.

## Search controls and stopping

`--count-min` / `--count-max` constrain integer counts at creation. Default bounds
come from photographed curve length under the two R295 camera/spacing families,
expanded to 75–120% of their estimates; they do not use the generator's bead count.
`--population` (default 8, minimum 4) retains both hands and seam families when
feasible, plus distinct count/phase/shape basins. `--min-delta` (default .0005)
defines meaningful score improvement. `--patience` defaults to 256 proposals.
Validation stagnation and reduced-step convergence are checked only after at least
128 refinement proposals beyond the 32 global starts. These are finite-search
stopping rules, not proofs that the best physical reconstruction was found.

The wall-clock limit is checked between candidate transactions. A trial in progress
finishes; startup, checkpoint I/O and especially final native evaluation/plots add
overhead. It is not a hard operating-system deadline. SIGINT/SIGTERM request a safe
stop at a transaction boundary. A hard kill may repeat the unfinished proposal,
but completed candidate records are recovered before advancing the RNG. Final
native export can be rerun with `--review-only`; it never changes fitted parameters.

Only documented model families are searched: one planar image-derived axis with
smooth shared displacement/spacing/phase fields, a common camera, common annular
bead dimensions and tube radius, integer count, both hands, closed integer winding
or a limited open seam. The program cannot invent new bead shapes, nonplanar axes,
new photographic detectors or a new physical-ownership theory. It stops and records
a diagnostic when this family cannot produce a feasible start.

## Files

- `checkpoint.json`: RNG, next/pending transaction, population IDs, source/evidence
  fingerprints, cumulative budgets, step sizes and progress history.
- `candidates/NNNNNN.json.gz`: every proposal, parameters, stage/parent, bounds or
  physical rejection, sampled scores, assignments/rivals and selection reason.
- `final-freeze.json`: written before reserved evaluation, only on sealing.
- `exports/`: full signed-index positions, native first-hit visibility, independent
  contact witnesses, native support evaluations, uncertainty across retained
  families and explicit R295 correspondence changes. No inferred pattern colors.
- `summary.json` and `review/`: failure locations, metrics, progress plot, whole
  original-photo overlays, raw/model crops and downloadable scientific records.

The same signed index across different count/hand families need not identify the
same physical bead. Exported alternative spread is not a confidence interval.
Geometry-only predictions and unsupported/occluded sites remain explicit.
Source/evidence changes deliberately invalidate resume rather than mixing methods.
Use a new destination after a code change; preserve the old run for comparison.

## Verification

```bash
.venv/bin/python -m unittest photo2.r296.tests
.venv/bin/python -m photo2.r296.profile
/home/rharris/.local/bin/beads-chromium-review photo2.r296.browser_check
git diff --check
```

The browser contract targets the curated pilot at `photo2/r296/results/pilot`.
Tests use existing real-photo evidence and mathematical geometry contracts; no
synthetic photographs or synthetic ground truth. Historical scientific inputs and
feedback are hash-checked against `r296/evidence/preservation.json.gz` at delivery.

The CLI holds an OS advisory lock while searching or exporting. A second writer
using the same directory is refused; different output directories are independent.
The lock is released automatically after process termination. Serving the completed
review does not hold the writer lock. The supplied launcher/locking contract targets
the repository's Linux/WSL Python environment.

Additional delivered-pilot checks:

```bash
.venv/bin/python photo2/r296/checkpoints/verify_pilot.py
.venv/bin/python photo2/r296/checkpoints/native_baseline.py
```

The first compares the final192-proposal run against both independent recovery
histories, then rechecks all exported positions, contact witnesses, selected native
rays/supports and original-photo pixels. The second compares native support metrics
to the fixed stage-A baseline, whose parameters were frozen before reserved access;
it never chooses or changes a model. Archived pre-lock runs retain their original
source checkpoints and are not resumable with the current source fingerprint.

Native observation exports use the modal first-hit owner of each unchanged support.
The search's discrete beam may instead choose null or another owner because of
neighbor evidence; its complete alternatives are retained under each candidate's
`train.ownership` / `validation.ownership`. Neither is a certified physical identity.
Search, resume and standalone review verify original source hashes and bind both
observation and photographic-cue content to the checkpoint.
