# R338 reproduction

Use the existing `.venv`, branch `photo-2-strategy-v3`, starting delivery `4ddb0c34`. The experiment reads original RGB, R332–R337 cached evidence and the immutable R336 active graph. No detector training, physical rendering or winding search is required.

The selected additive graph is `photo2/r338/results/graph.json.gz`; original graph files are preserved. Native visual decisions are explicit inputs to the replay: the frozen inspection plan and documented source judgments are not independently rediscovered truth.

From the checkout root:

```bash
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r338.replay --output /tmp/beads-r338-fresh
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.r338.verify --root photo2/r338
/home/rharris/.local/bin/beads-chromium-review photo2.r338.browser_check
```

Choose a fresh output path. The replay runs `audit`, `inspect`, `conflicts`, `measure`, `revise`, `analyze`, `review`, then independent `verify`. It sets `R338_RUN_ROOT` for generated inputs and preserves the selected body-freeze UTC with `R338_FREEZE_UTC`. Runtime fields are ignored for exact JSON comparison; PNG/HTML/JS/CSS artifacts are compared byte for byte. Gzip containers are compared by decoded JSON because their headers have creation timestamps. The receipt lists every compared file and stage time; child peak RSS measures the largest child, not summed memory.

To run stages individually, use the module's `--output` argument (`verify` uses `--root`) and set `R338_RUN_ROOT` to the same fresh output root. `inspect` reads the static `photo2/r338/inspection-plan.json`:17 exact source cues plus two additional eligible native panels actually inspected. `revise` encodes the documented manual native judgments and exact earlier maker decision. Replaying those decisions is not independent re-certification of the photograph. The paper-outline screen and native components only generate priorities; they do not admit beads. The final statistical analysis reads a body-freeze fingerprint and runs only fixed208 models, not a new period/winding search.

Selected outputs:

- `audit/audit.json.gz`, `summary.json`, `association-exceptions.json`, `input-seal.json`: all3,993 source cues, frozen source pixels, geometry and exclusions.
- `inspection/*`, `conflicts/*`: native views, local keys,121 conflict contributors and26 nonmodal targets; none automatically relabeled.
- `measurement/pigment.json.gz`:166 fixed-support, three-radius broad/compact pigment checks and exact source pixels.
- `results/graph.json.gz`, `body-freeze.json`, `link-audit.json`, `summary.json`: additive association layer and explicit abstentions.
- `analysis/analysis.json.gz`: eight cohorts, strict entries, geographic/whole-occurrence scores and newly indexed known-body check.
- `review/index.html`, `ledger.html`, `panels.json`, `native-crops.json`: offline questions, actual links and185 literal source crops.
- `verification.json`, `review/browser-verification.json`, `performance.json`: independent computation, actual browser and fresh replay receipts.

The original photograph is EXIF-transposed once, as in R332–R337. Native crop boxes use that2540×3182 orientation. No rotation, resizing, hue correction or fitted rendering enters the saved native PNG evidence. Display enlargement is separate.

The delivered fresh replay completed in51.979s with1,825.16MiB peak child RSS. Its first failed presentation comparison and the runtime-export fix are recorded under `development/`; no scientific conclusion changed.

`legacy-cache-verification.json` seals the four R266/R275 catalogs reused through `Completion.pool` against the exact starting delivery commit. The independent verifier also checks those hashes; the recent-round seal covers1,099 other files.
