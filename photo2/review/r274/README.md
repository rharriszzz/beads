# R274 evidence and reproduction

[Report](../../HUE_INTERIORS_R274.md) · [viewer](../../hue_inventory_r274/index.html).

- `inventory.json/js/csv`: trusted locations and accepted interiors, distinct statuses.
- `selection.json`, `summary.json`: one selected rule and all8controls.
- `*-candidates.jsonl.gz`: every automatic R272 proposal, full native masks and directional stops.
- `*-locations.json`: trusted points, including uncertain interiors, for every rule.
- `paired-interiors.csv`, `paired-summary.json`: exact old/new changes and exclusions.
- `contact-ranking.json`, `contact-cases.json`: post-detection review selection; not detector inputs.
- `review-paths.jsonl.gz`, `review-stops.json`, `path-*.png`: exact hue/brightness evidence.
- `synthetic-inputs.npz`, `synthetic-truth.npz`:35new reproducible input/truth fixtures.
- `synthetic-evaluation.json`, `synthetic-records.jsonl.gz`:199scene end-to-end comparisons.
- `component-evaluation.json`: fixed automatic-location tests, clearly distinct from recall.
- `validation.json`, `viewer-node-checks.json`, `python-tests.json`: completed checks.
- `preserved-hashes.json`:162R273evidence/report/source/viewer files checked unchanged.

The original ICC-corrected photograph is reused from `../r272/photo-srgb.png`.
All R272 maxima and R273 alternative/reflection records remain at their old paths.
Opening the HTML directly loads the photograph without a server.

```sh
export MPLCONFIGDIR=/tmp/beads-r274-mpl
.venv/bin/python -m photo2.bead_detection.experiment_r274
.venv/bin/python -m photo2.bead_detection.deliver_r274 highlight-palette
.venv/bin/python -m photo2.bead_detection.review_r274
.venv/bin/python -m photo2.bead_detection.evidence_r274
.venv/bin/python -m photo2.bead_detection.evaluate_r274
.venv/bin/python -m photo2.bead_detection.component_r274
.venv/bin/python -m photo2.bead_detection.validate_r274
.venv/bin/python -m unittest photo2.bead_detection.test_r274 photo2.bead_detection.test_r273 photo2.bead_detection.test_coverage_r272 photo2.bead_detection.test_inventory_r272
node photo2/hue_inventory_r274/test_viewer.cjs
```

Runtime: `hue_r274.detect(native_rgb, icc_srgb)`; neither review crops, prior saved IDs,
expected counts nor truth labels are inputs. Paired experiments can reuse the exact,
verified automatically generated R272/R273 records to avoid repeated candidate work.
