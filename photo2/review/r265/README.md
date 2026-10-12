# R265 evidence

[Repair report](../../DETECTION_REPAIR_R265.md) ·
[checkpoint and complete stage history](checkpoint.json) ·
[parameters, versions and source hashes](manifest.json) ·
[full numerical ablations](full-metrics.json) ·
[coordinate and photographic-landmark evaluation](photo-evaluation.json).

Native images use nearest-neighbor enlargement, identical source crops, cyan
retained pixels and white supported coordinates. No detection smoothing is used.

- Named failures: [R00956](R00956.png), [R01284](R01284.png), [R01307](R01307.png).
- Existing R264 cases: [red pair](pair.png), [top transition](top-transition.png),
  [inner transition](inner-transition.png), [paper risk](paper-risk.png),
  [R264 largest shift](largest-shift.png), [yellow shift](yellow-shift.png).
- Automatically chosen largest final movements:
  [first](auto-shift-1.png), [second](auto-shift-2.png), [third](auto-shift-3.png).
  Three `auto-holes-P*.png` figures use the largest hole totals in the old results;
  exact IDs, boxes and ranking scores are in [targeted.json](targeted.json).
- Synthetic [metrics](synthetic.json), [known footprint arrays](synthetic-truth.npz),
  and `scene-*.png` illustrate two known bodies, including multiple peaks and dark
  reflections. Scenes00–11 deliberately stress the hard size cap;12–23 use compact
  bodies. None of those labels enters the detector.
- [Old replay](baseline-replay.json) checks masks, coordinates, statuses and
  size-limit flags against the archived R26410° output exactly.
- [Deadline test](deadline-test.json) records a forced50-ms termination.
- `units.log` records58 passing tests, including240 randomized small grids.

Each variant directory holds its summary and coordinate CSV. `joint/regions.json.gz`
and `joint/traces.tar` preserve the complete corrected maxima, masks and native
histories. Historical old full data/traces remain under `../r264/10`. Intermediate
full ablations and source-change prototypes are ignored in `photo2/output/r265`;
all can be reproduced with the command in the report. Logs and checkpoint history
retain failed/development stages; only the final matching source fingerprint is
the delivered comparison. The initial JSON serialization failure was repaired.
A later source-change checkpoint correctly halted a run after stronger audit
checks were added; resume reran invalidated stages under the same deadline.

Photo evaluation is limited to saved R264 evidence and explicit geometric proxies.
Coordinate displacement is not physical-center error. A nearby point does not
prove a formerly missed bead was found. Pair retention and overlap do not establish
bead identity. No expected-count target is used.

Original detector/harness/test snapshots are `detector-source.py`,
`harness-source.py`, and `tests-source.py`; these match the archived manifest.
The current harness imports frozen `straight_detect_r265.py` to reproduce v1.
The final follow-up is [first-dark evidence](../r265-first-dark/README.md).
