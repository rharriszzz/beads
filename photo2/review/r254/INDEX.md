# R254 evidence and visual audit

[Scientific conclusions and limits](../../PATTERN_GEOMETRY_R254.md).
**No exact admissible template survived.** P divides N under the maker's latest
clarification. Every image distinguishes a diagnostic hypothesis from observed
color or a recovered result. The original310 observations remain unchanged.

## Review each stage

| Stage | Open this evidence | What to check |
|---|---|---|
| A: modulo arithmetic | [Conflicts vs every P](A-period-conflicts.png), [divisibility](A2-divisibility.png) | Nondivisors are excluded; conflicts count minimum contradictory assignments, not order-dependent pairs. |
| B: residue constraints | [Rejected strips](B-rejected-residue-strips.png), [exact source IDs](residue-constraints.csv) | Gray `?` is unknown; purple `!` is contradictory. Red/yellow alone do not make the full strip consistent. |
| B: visibility | [P-residue vs k-mod13 coverage](B2-residue-visibility.png), [coverage ledger](residue-coverage.csv) | Blank cells represent missing observations, not black beads. |
| C: geometry and pattern | [Separate costs](C-geometry-pattern.png), [bounded deformation](C2-geometric-corrections.png) | Better geometric cost does not imply correct global indices or a consistent template. |
| D: maker identity | [Raw vs exact ownership](N2670_h+1_f0-maker-ownership.png) | Point7 fails in this model; green marks pass and magenta marks fail. Cyan contours are calculated first-visible surfaces. |
| D: distributed identity | [Four raw/marked stars](D2-distributed-stars.png) | These reserved R253 index hypotheses remain conditional. Inspect actual photographic ownership. |
| E: concrete contradiction | [P382 raw pairs and alternatives](N2674_h+1_f0-conflict-crops.png), [P267 pairs](N2670_h+1_f0-conflict-crops.png) | Does each source point lie in the stated colored body? Can a displayed alternative actually own its interior? Crosses are model centers, not measured photo centers. |
| F: independent colors | [Heldout outcome map](F-heldout-map.png), [all scores](refined-heldout.json) | Unknown/conflicted residues abstain. All displayed training templates are already inconsistent. |
| G: inferred colors | [Prediction status](G-prediction-status.png), [all model colors](template-prediction-status.csv) | No viable template means no justified predicted colors; hidden model beads are included and explicitly unobserved. |
| H: exact control | [Known sequence](H-known-pattern-control.png), [source/observation/prediction ledger](known-pattern-control.json) | The synthetic source contains black, but the inferred unobserved positions remain `?`. |

## Native photograph overlays

All overlays are2540×3182, the original photo resolution. Colored rings mark
observed red/yellow interiors; cyan crosses mark calculated centers; labels are
model-conditional k; `!` marks failed exact representative ownership. Lines connect
an interior to its assigned calculated center, never a claim that they coincide.

- [N2674,h+1: strongest new all310 color diagnostic](N2674_h+1_f0-indexed-photo.png)
- [N2696,h+1: training geometry nominee](N2696_h+1_f0-indexed-photo.png)
- [N2681,h−1: training geometry nominee](N2681_h-1_f0-indexed-photo.png)
- [N2670,h+1: original count neighborhood](N2670_h+1_f0-indexed-photo.png)
- [N2679,h−1: original count neighborhood](N2679_h-1_f0-indexed-photo.png)

Corresponding `MODEL-maker-ownership.png` files give raw/marked maker-chart crops.
[Display-selection ledger](display-selection.json) records training-only nominees
separately from the post-hoc color diagnostic.

## Exact and machine-readable records

- [Protocol and active instruction changes](protocol.json).
- [All46 fixed mappings ×399 periods ×three subsets](fixed-periods.csv),
  [all exact-period lists](fixed-summary.json),
  [six models' complete per-period residue constraints, gzip JSON](selected-residue-constraints.json.gz).
- [Original strict ownership domains](strict-domains.json),
  [702 original bounded-domain exclusions](alternative-proofs.json),
  [selected support summary](alternative-summary.json).
  `MODEL-alternative-support.json` contains per-option exact patch support,
  representative ownership and cost change.
- [114 refined-model comparison](comparison.csv), [42 camera fits](camera-results.json),
  [72 count/turn extensions](extended-results.json), [arithmetic count pruning](count-pruning.json).
- [All399-period refined counts](camera-pattern-summary.json),
  [all399-period extension counts](extended-pattern-summary.json),
  [2640 bounded-domain exclusions and two-body witnesses](refined-alternative-proofs.json).
- [Every changed/unchanged photographic index](index-changes.csv),
  [same-index geometric displacement/deformation](geometry-changes.csv),
  [stretch/winding profiles](geometry-profiles.csv).
- Every `MODEL-camera.json` has parameters, initialization, reserved stars and
  full chart ownership; `MODEL-assignments.json` has all310 original IDs/colors,
  k, generator index, exact patch support and nearby alternatives. New-count
  `*-initial-model.json` / `*-initial-assignments.json` preserve their R253-based
  initialization, not an additional accepted reconstruction.
- [Original-mapping heldout diagnostics](heldout-diagnostics.json),
  [refined heldout diagnostics](refined-heldout.json),
  [specific conflict witnesses](conflict-examples.json).
- [155 unchanged source hashes](source-integrity.json),
  [tests](tests.txt), [replay and artifact manifest](verification.json).

## Reproduction

Use Python3.12 in the existing `.venv`, at repository root. Run sequentially:

```sh
PYTHONPATH=photo2 .venv/bin/python -m unittest photo2/test_pattern_r254.py photo2/test_global_fit_r253.py
.venv/bin/python photo2/pattern_r254.py
.venv/bin/python photo2/alternatives_r254.py
.venv/bin/python photo2/camera_r254.py
.venv/bin/python photo2/extend_r254.py
.venv/bin/python photo2/evidence_r254.py
.venv/bin/python photo2/review_visuals_r254.py
.venv/bin/python photo2/geometry_changes_r254.py
.venv/bin/python photo2/verify_r254.py
```

Every command accepts `--output PATH`; use a fresh ignored `photo2/output/r254-replay`
for a complete independent rebuild. Later stages depend on preceding outputs.
Camera/extension commands reuse matching protocol-version2 cached results;
verification independently refits three cases and replays all discrete witnesses.
No new image detector, appearance renderer, dependency download or remote service
is required. These are mathematical/projection plots and photograph annotations,
not newly rendered scene appearance.
