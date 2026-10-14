# R278 evidence and reproduction

[Main report](../../RECONSTRUCTION_R278.md)

`phase1-inventory.json.gz` is the frozen independent inventory; `phase1-positions.csv` separates measured position types and unknown physical centers. `phase1-decisions.json.gz` and `phase1-features.json.gz` retain every attempted proposal and feature, including rejections. The original 295 R275 uncertain records remain in the inventory. `phase1-review-cases.json` indexes additions, unresolved peak groups, small supports, short intervals and band edges. Cyan marks preserved locations; green marks additions; the orange square is the review target, not a detection.

`failed-wide-control/` preserves the failed 425-addition control and illustrative paper failures. `enclosure-only-control/` preserves the 117-addition intermediate. `obsolete-prefreeze-fits/` contains interrupted/obsolete preliminary fits against earlier inventories; NEVER include these in final model comparisons. Routine full failed atlases can be regenerated; only representative failure images are curated.

`packing-screen.json`, `contact-screen.json`, `tilt-screen.json` retain failed packing alternatives. `comparison.json`/CSV contain all 14 fits, color/sector breakdowns and budgets. `MODEL.json` includes full spline/camera/phase parameters, frozen inventory hash and fit trace. `MODEL-separation.json` stores a separating-plane normal/gap for every possible collision pair. `MODEL-contact.json` is the denser sampled audit for exported models.

`MODEL-correspondence.json.gz` contains every generated bead and every independent observation, alternatives, statuses, raw-pixel colors and unknown rays. `MODEL-visible-support.json.gz` contains 2px first-hit support samples keyed by model index. `MODEL-beads.csv` is suitable for later indexing review; indices remain conditional. `MODEL-discrepancies.json` links worst native crops, black matches and geometry-assisted candidates. `MODEL-light.json` contains all 20 shared-light trials and every individual error. POV scenes preserve the literal source macro with the intended radius; uncertain colors are gray.

No external packages are required beyond the existing Python 3.12 environment. From repository root:

```bash
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.reproduce_r278 --stage phase1
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.reproduce_r278 --stage screens
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.reproduce_r278 --stage fit
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.reproduce_r278 --stage audit
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.reproduce_r278 --stage export
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.reproduce_r278 --stage light
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.validate_r278 synthetic
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.validate_r278 native
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.validate_r278 preservation
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m unittest photo2.test_reconstruct_r278 photo2.test_reconstruct_r276 photo2.bead_debugger.test_surface
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.report_r278
povray +Iphoto2/review/r278/intended_N2696_h+1_p1.300_f0_tilt-8.pov +Ophoto2/review/r278/intended_N2696_h+1_p1.300_f0_tilt-8-pov.png +W762 +H955 +FN -D +A0.2 +WT2
```

The fit stage reuses saved models only when the Phase 1 hash agrees. To rerun optimization from scratch, first archive its model JSON files separately. For a cheap deterministic replay, rerun export for a named saved model with `python -m photo2.reconstruct_r278 export --name MODEL`. Phase 1 can also reproduce the selected output from the preserved failed control with `python -m photo2.bead_detection.phase1_r278 --select-saved`.

## Photographic atlas

- [phase1-atlas-01.jpg](phase1-atlas-01.jpg)
- [phase1-atlas-02.jpg](phase1-atlas-02.jpg)
- [phase1-atlas-03.jpg](phase1-atlas-03.jpg)
- [phase1-atlas-04.jpg](phase1-atlas-04.jpg)
- [phase1-atlas-05.jpg](phase1-atlas-05.jpg)
- [phase1-atlas-06.jpg](phase1-atlas-06.jpg)
- [phase1-atlas-07.jpg](phase1-atlas-07.jpg)
- [phase1-atlas-08.jpg](phase1-atlas-08.jpg)
- [phase1-atlas-09.jpg](phase1-atlas-09.jpg)
- [phase1-atlas-10.jpg](phase1-atlas-10.jpg)
- [phase1-atlas-11.jpg](phase1-atlas-11.jpg)
- [phase1-atlas-12.jpg](phase1-atlas-12.jpg)
- [phase1-atlas-13.jpg](phase1-atlas-13.jpg)
- [phase1-atlas-14.jpg](phase1-atlas-14.jpg)
- [phase1-atlas-15.jpg](phase1-atlas-15.jpg)
- [phase1-atlas-16.jpg](phase1-atlas-16.jpg)
- [phase1-atlas-17.jpg](phase1-atlas-17.jpg)
- [phase1-atlas-18.jpg](phase1-atlas-18.jpg)
- [phase1-atlas-19.jpg](phase1-atlas-19.jpg)
- [phase1-atlas-20.jpg](phase1-atlas-20.jpg)
- [phase1-atlas-21.jpg](phase1-atlas-21.jpg)
- [phase1-atlas-22.jpg](phase1-atlas-22.jpg)
- [phase1-atlas-23.jpg](phase1-atlas-23.jpg)
- [phase1-atlas-24.jpg](phase1-atlas-24.jpg)
- [phase1-atlas-25.jpg](phase1-atlas-25.jpg)
- [phase1-atlas-26.jpg](phase1-atlas-26.jpg)
- [phase1-atlas-27.jpg](phase1-atlas-27.jpg)
- [phase1-atlas-28.jpg](phase1-atlas-28.jpg)

## Candidate overlays and ledgers

- [intended_N2080_h-1_p1.400_f0: overlay](intended_N2080_h-1_p1.400_f0-overlay.jpg) · [per-bead CSV](intended_N2080_h-1_p1.400_f0-beads.csv) · [accounting](intended_N2080_h-1_p1.400_f0-accounting.json) · [discrepancies](intended_N2080_h-1_p1.400_f0-discrepancies.json)
- [intended_N2080_h+1_p1.400_f0: overlay](intended_N2080_h+1_p1.400_f0-overlay.jpg) · [per-bead CSV](intended_N2080_h+1_p1.400_f0-beads.csv) · [accounting](intended_N2080_h+1_p1.400_f0-accounting.json) · [discrepancies](intended_N2080_h+1_p1.400_f0-discrepancies.json)
- [intended_N2696_h+1_p1.300_f0_tilt-8: overlay](intended_N2696_h+1_p1.300_f0_tilt-8-overlay.jpg) · [per-bead CSV](intended_N2696_h+1_p1.300_f0_tilt-8-beads.csv) · [accounting](intended_N2696_h+1_p1.300_f0_tilt-8-accounting.json) · [discrepancies](intended_N2696_h+1_p1.300_f0_tilt-8-discrepancies.json)
- [intended_N2696_h-1_p1.300_f0_tilt-8: overlay](intended_N2696_h-1_p1.300_f0_tilt-8-overlay.jpg) · [per-bead CSV](intended_N2696_h-1_p1.300_f0_tilt-8-beads.csv) · [accounting](intended_N2696_h-1_p1.300_f0_tilt-8-accounting.json) · [discrepancies](intended_N2696_h-1_p1.300_f0_tilt-8-discrepancies.json)
