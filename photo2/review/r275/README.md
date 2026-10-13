# R275 evidence and reproduction

[Report](../../CENTERLINE_INVENTORY_R275.md) · [minimal viewer](../../centerline_inventory_r275/index.html).

Open the viewer through the repository's static serving setup, or run `python3 -m http.server 8000` from the repository root and visit `/photo2/centerline_inventory_r275/`. The photograph is the preserved ICC-corrected `../r272/photo-srgb.png`. Cyan shows accepted measured supports and peaks; orange candidates are optional. The centerline checkbox filters selection, rendering and native-size ordering. Stable IDs, not atlas numbers, are used for ID jump.

Reproduce with Python 3.12 and the existing `.venv`:

```sh
MPLCONFIGDIR=/tmp/beads-r275-mpl .venv/bin/python -m photo2.bead_detection.run_r275
MPLCONFIGDIR=/tmp/beads-r275-mpl .venv/bin/python -m photo2.bead_detection.delivery_r275
MPLCONFIGDIR=/tmp/beads-r275-mpl .venv/bin/python -m photo2.bead_detection.evaluate_r275
MPLCONFIGDIR=/tmp/beads-r275-mpl .venv/bin/python -m unittest photo2.bead_detection.test_inventory_r272 photo2.bead_detection.test_coverage_r272 photo2.bead_detection.test_r273 photo2.bead_detection.test_r274 photo2.bead_detection.test_r275
MPLCONFIGDIR=/tmp/beads-r275-mpl .venv/bin/python -m photo2.bead_detection.validate_r275
node photo2/centerline_inventory_r275/test_viewer.cjs
```

The detector consumes pixels and parameters. Frozen upstream inventories are reproducible outputs of the preserved R272/R274 image-only stages, not reviewed truth. The unregistered R255 centerline only selects the work area. `run_r275 --from=STAGE` resumes from the current inventory; ordinary individual stage reruns use their saved pre-stage snapshot unless passed `--refresh`. Full replay is the safest reproduction command. Ignored working snapshots can be regenerated; final masks and compressed full decisions are tracked.

| Artifact | Meaning |
|---|---|
| `inventory.json`, `inventory.js` | Complete active inventory and archived suppressed/superseded measurements; JavaScript copy serves the viewer. |
| `centerline-audit.csv`, `target-locations.json` | Every accepted target, corrections, explicit removals and residual proposal groups. Atlas numbers are inspection labels, not string indices. |
| `band.json`, `baseline-band.json` | Frozen band definition, provenance/hash and prior membership. |
| `all-band-maxima.jsonl.gz` | All native raw and 5/7/9-average maxima, including those rejected later. |
| `*-decisions.jsonl.gz` | Exact per-control measurements, reasons, candidate competition and support records. |
| `*-controls.json`, `*-summary.json` | Controls, selected settings and accepted changes. |
| `color-corrections.json`, `dominance.json`, `final-ownership.json` | Explicit color/point correction, peak/contrast ratios and native photographic bridge traces. |
| `angular-locations.json`, `angular-increments.csv` | Every target's along-reference position, signed distance and circular increment; separate measured-support crossing and central-anchor subsets. |
| `stations.json`, `station-increments.csv`, `angular-sectors.csv` | Diagnostic single/double associations, all increments and geographic uniformity. |
| `unresolved-candidates.json`, `associated-rejections.json` | Residual groups versus aliases already associated with a supported or suppressed peak. Neither is a census of missed beads. |
| `comparisons.json` | Explanations and crop bounds for final original/before/after comparisons. |
| `final-artifacts.json` | Authoritative final atlas, residual photographs, comparisons and short-gap witnesses. Extra old `gap-*`, `group-*` and `unresolved-*` images are preserved exploratory outputs, not additional final failures. |
| `synthetic-evaluation.json`, `synthetic-decisions.jsonl.gz` | Known-identity end-to-end scoring and every tested synthetic proposal. |
| `validation.json`, `preserved-hashes.json`, `reproduction.json`, `source-hashes.json` | Exact measurement, preservation, replay and source-provenance checks. |
| `before-*.gz`, `synthetic-before-*.gz` | Rejected/earlier controls preserved for diagnosis, including the retreat/ownership regressions. |

Whole photo: [target band and accepted locations](whole-photo.png). Progress: [individual angular spacing](angular-spacing.png), [single/double progression](single-double-spacing.png). Raw sheets show the photograph independently of proposals. Each overlapping atlas tile pairs the raw photograph with numbered accepted points and separate U-numbered unresolved proposals.

## Full photographic atlas

[Tile 01](atlas-01.jpg) · [Tile 02](atlas-02.jpg) · [Tile 03](atlas-03.jpg) · [Tile 04](atlas-04.jpg) · [Tile 05](atlas-05.jpg) · [Tile 06](atlas-06.jpg) · [Tile 07](atlas-07.jpg) · [Tile 08](atlas-08.jpg) · [Tile 09](atlas-09.jpg) · [Tile 10](atlas-10.jpg) · [Tile 11](atlas-11.jpg) · [Tile 12](atlas-12.jpg) · [Tile 13](atlas-13.jpg) · [Tile 14](atlas-14.jpg) · [Tile 15](atlas-15.jpg) · [Tile 16](atlas-16.jpg) · [Tile 17](atlas-17.jpg) · [Tile 18](atlas-18.jpg) · [Tile 19](atlas-19.jpg) · [Tile 20](atlas-20.jpg) · [Tile 21](atlas-21.jpg) · [Tile 22](atlas-22.jpg) · [Tile 23](atlas-23.jpg) · [Tile 24](atlas-24.jpg) · [Tile 25](atlas-25.jpg) · [Tile 26](atlas-26.jpg) · [Tile 27](atlas-27.jpg) · [Tile 28](atlas-28.jpg) · [Tile 29](atlas-29.jpg) · [Tile 30](atlas-30.jpg) · [Tile 31](atlas-31.jpg) · [Tile 32](atlas-32.jpg) · [Tile 33](atlas-33.jpg) · [Tile 34](atlas-34.jpg) · [Tile 35](atlas-35.jpg) · [Tile 36](atlas-36.jpg) · [Tile 37](atlas-37.jpg) · [Tile 38](atlas-38.jpg) · [Tile 39](atlas-39.jpg) · [Tile 40](atlas-40.jpg) · [Tile 41](atlas-41.jpg) · [Tile 42](atlas-42.jpg) · [Tile 43](atlas-43.jpg) · [Tile 44](atlas-44.jpg) · [Tile 45](atlas-45.jpg) · [Tile 46](atlas-46.jpg) · [Tile 47](atlas-47.jpg) · [Tile 48](atlas-48.jpg) · [Tile 49](atlas-49.jpg) · [Tile 50](atlas-50.jpg) · [Tile 51](atlas-51.jpg) · [Tile 52](atlas-52.jpg) · [Tile 53](atlas-53.jpg) · [Tile 54](atlas-54.jpg) · [Tile 55](atlas-55.jpg) · [Tile 56](atlas-56.jpg) · [Tile 57](atlas-57.jpg) · [Tile 58](atlas-58.jpg) · [Tile 59](atlas-59.jpg) · [Tile 60](atlas-60.jpg) · [Tile 61](atlas-61.jpg) · [Tile 62](atlas-62.jpg) · [Tile 63](atlas-63.jpg) · [Tile 64](atlas-64.jpg) · [Tile 65](atlas-65.jpg) · [Tile 66](atlas-66.jpg) · [Tile 67](atlas-67.jpg) · [Tile 68](atlas-68.jpg) · [Tile 69](atlas-69.jpg) · [Tile 70](atlas-70.jpg) · [Tile 71](atlas-71.jpg) · [Tile 72](atlas-72.jpg) · [Tile 73](atlas-73.jpg) · [Tile 74](atlas-74.jpg) · [Tile 75](atlas-75.jpg) · [Tile 76](atlas-76.jpg) · [Tile 77](atlas-77.jpg)

[Raw sheet 1](raw-sheet-1.jpg) · [Raw sheet 2](raw-sheet-2.jpg) · [Raw sheet 3](raw-sheet-3.jpg) · [Raw sheet 4](raw-sheet-4.jpg) · [Raw sheet 5](raw-sheet-5.jpg) · [Raw sheet 6](raw-sheet-6.jpg) · [Raw sheet 7](raw-sheet-7.jpg)
