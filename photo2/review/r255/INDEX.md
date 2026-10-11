# R255 visual evidence index

[Read the sequential audit report](../../AUDIT_R255.md). All global labels are model-conditional.

## Read in order

| Stage | Whole photograph or main view | Enlargements / data |
|---|---|---|
| 0. Source | [Original native JPEG](../../../beads-photo-2.jpg) | Coordinates: x right, y down; 2540 × 3182 |
| 1. Splines | [Seed, edges, tangents and sections](01-splines-whole.png); [registered primary-model centerline](01-registered-centerline-whole.png) | Historical edges are unvalidated; R190 remains unadopted |
| 2. Trusted beads | [310 observations and withheld cases](02-trusted-whole.png) | Red/yellow rings accepted; cyan diamonds ambiguous; magenta crosses rejected |
| 3. Origin | [Whole-photo locator](03-origin-whole.png); [raw/marked detail](03-origin.png) | C252-A948, red, maker 20 = C; k=0 |
| 4. Triples | [Whole photograph](04-triple-whole.png); [direction schematic](04-direction-schematic.png) | [27-node maker graph with A/B alternatives](04-maker-triples.png); global triples are algebraic addresses |
| 5. Indices | [Primary N2696 h+1](05-index-whole.png) | ? ambiguous assignment; ! failed ownership |
| 6. Patterns | [P382 diagnostic](06-pattern-N2674_h+1_f0-P382.png); [primary model P337](06-pattern-N2696_h+1_f0-P337.png) | Both REJECTED; gray ? unknown, purple ! conflict; no black inference |

## Raw/marked crop matrix

Each link opens the original pixels beside the corresponding annotated crop. Dense index/triple labels use numbered keys with a readable gutter.

| Region | Splines + R190 comparison | Trusted observations | Canonical triples | bead_index |
|---|---|---|---|---|
| origin | [PNG](01-splines-origin.png) | [PNG](02-trusted-origin.png) | [PNG](04-triple-origin.png) | [PNG](05-index-origin.png) |
| right | [PNG](01-splines-right.png) | [PNG](02-trusted-right.png) | [PNG](04-triple-right.png) | [PNG](05-index-right.png) |
| bend | [PNG](01-splines-bend.png) | [PNG](02-trusted-bend.png) | [PNG](04-triple-bend.png) | [PNG](05-index-bend.png) |
| left | [PNG](01-splines-left.png) | [PNG](02-trusted-left.png) | [PNG](04-triple-left.png) | [PNG](05-index-left.png) |
| bottom | [PNG](01-splines-bottom.png) | [PNG](02-trusted-bottom.png) | [PNG](04-triple-bottom.png) | [PNG](05-index-bottom.png) |

## Concrete pattern conflicts

| Hypothesis | Shared residue | Red: raw + marked | Yellow: raw + marked |
|---|---:|---|---|
| N2674_h+1_f0 | 7 | [PNG](06-conflict-N2674_h+1_f0-r7-red.png) | [PNG](06-conflict-N2674_h+1_f0-r7-yellow.png) |
| N2674_h+1_f0 | 14 | [PNG](06-conflict-N2674_h+1_f0-r14-red.png) | [PNG](06-conflict-N2674_h+1_f0-r14-yellow.png) |
| N2674_h+1_f0 | 117 | [PNG](06-conflict-N2674_h+1_f0-r117-red.png) | [PNG](06-conflict-N2674_h+1_f0-r117-yellow.png) |
| N2696_h+1_f0 | 0 | [PNG](06-conflict-N2696_h+1_f0-r0-red.png) | [PNG](06-conflict-N2696_h+1_f0-r0-yellow.png) |
| N2696_h+1_f0 | 6 | [PNG](06-conflict-N2696_h+1_f0-r6-red.png) | [PNG](06-conflict-N2696_h+1_f0-r6-yellow.png) |
| N2696_h+1_f0 | 11 | [PNG](06-conflict-N2696_h+1_f0-r11-red.png) | [PNG](06-conflict-N2696_h+1_f0-r11-yellow.png) |

## Tables, provenance and review

- [Complete 930-row observation/color/coordinate/triple/index/model ledger](observation-index-triples.csv)
- [Saved competing assignments, triples, exact ownership and patch support](assignment-alternatives.csv)
- [All 27 maker nodes, UUIDs, local A/B triples and signed indices](maker-local-triples.csv)
- [All 719 residues, observed IDs and index memberships](pattern-residues.csv)
- [Readable complete template-to-observation tables](PATTERN_RESIDUES.md)
- [Twelve photographed witnesses: IDs, coordinates, k, residue and ownership](conflict-witnesses.csv)
- [29 unresolved cases and two rejected colored proposals with reasons](withheld-candidates.csv)
- [Five spline-normal sections: endpoints, width and centering diagnostic](cross-sections.csv)
- [8,193 active seed samples and native tangents](spline-samples.csv)
- [8,193 primary-model translated samples](registered-centerline.csv)
- [Exact archived original edge/centerline source, hash-verified](historical-splines.json)
- [Selections, crop boxes, dimensions and summary counts](summary.json)
- [Checks and source/artifact SHA-256 hashes](verification.json)
- [Three small illustrated questions for later review](QUESTIONS.md)

## Source evidence and reproduction

- [R252 consolidation](../r252/INDEX.md): observation provenance, aliases, maker facts and withheld cases.
- [R253 geometry](../r253/INDEX.md): earlier hypotheses, maker chart, uncertainty and source geometry.
- [R254 pattern/geometry](../r254/INDEX.md): saved model nominations, assignments, ownership and rejected periods.
- [Primary exact maker ownership](../r254/N2696_h+1_f0-maker-ownership.png); [opposite-hand native indices](../r254/N2681_h-1_f0-indexed-photo.png).
- [Audit generator](../../audit_r255.py); run `.venv/bin/python photo2/audit_r255.py` from the repository root. Replay with `--output photo2/output/r255-replay`. No fit or search is run.
