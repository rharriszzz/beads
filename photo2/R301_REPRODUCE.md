# R301 reproduction and graphical review

Run from the repository; the standalone search selects `.venv` automatically:

```sh
python3 photo2/local_inverse.py --output photo2/output/r301-new --section S1 --hand -1 --seed 3011 --budget 1536
```

Repeat the same command to resume. Changing the source, frozen evidence, section,
seed, method, hand or starting vector is rejected. A single writer lock prevents
concurrent processes sharing a destination. SIGTERM/SIGINT commits the last
completed evaluation; a hard kill replays uncommitted work from the last atomic
16-proposal checkpoint. Increasing the budget is permitted. The delivered run
directories are historical results: use a new output for new work.

The command above is a cold global start. Exact reproduction of the delivered
baseline-seeded independent runs uses the corresponding checkpoint `config.start`
with `photo2.r301.search.run` in a new directory. The experiment driver records the
complete schedules and initialization, including both hands and seeds. It must not
be used to silently tune delivered results after their native evaluation.

```sh
.venv/bin/python -m unittest photo2.r301.tests
.venv/bin/python -m photo2.r301.verify
photo2/review/r301/launch.sh
```

The launcher binds localhost, selects another port if 8301 is busy, and opens the
Windows default browser through PowerShell when available under WSL2. Use
`--no-browser --port 0` for an automatic local port without browser dispatch.
`photo2/review/r301/index.html` also works offline. No assets require the internet.

`r301/evidence/frozen.json.gz` contains the complete prior observation ledger,
automatic region-selection candidates, selected regions, train/withheld splits,
native coordinates and photographic hashes. The separate withheld-separator file
is never used by the optimizer. Historical science and feedback preservation is
recorded in `evidence/preservation.json.gz` and checked by `verify`.

Each search checkpoint contains all proposals, rejected hypotheses, parameters,
component timings, objective values, population, RNG state, source/evidence hashes
and environment versions. `independent-manifest`, `refined-manifest`, `ablations`
and `joint-manifest` identify the deterministic selected alternatives.
`fit-freeze.json` seals selection before native held-out evaluation.

Native results include all surface outlines and local addresses, predicted and
observed reflections, explicit unmatched observations, alternative ownership costs,
signed errors, color groups, face-diameter normalization, physical witnesses and
guard-extension diagnostics. They do not establish physical string identities,
necklace closure or a total count.

The two `checkpoints` subdirectories retain the initial and interim synthetic
experiments and evidence selections while the maker clarified the minimum count.
Those synthetic tests use native implicit ray tracing to generate known targets
and an independently sampled surface representation for coarse inversion. They
share the same mathematical shape, so they are not an independent-renderer proof.
No real-photo search ran under the superseded 6,000 minimum.

The current step ends with the measured R301 results, explanation and graphical
comparison. The maker stated that there is a new plan and requested complete
closure of this step with the reasons recorded. No subsequent plan or R302 is
started by this delivery.
