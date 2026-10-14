# R284B reproduction and evidence map

Read [the full report](../R284B_REPORT.md), [complete request](../R284B_SPECIFICATION.md),
[permanent measurement contract](../PHASE1_MEASUREMENTS.md), and
[review page](../review/r284b/index.html). This package does not replace production.

From repository root, using existing `.venv/bin/python` (Python3.12):

```sh
.venv/bin/python -m photo2.r284b.diagnose
.venv/bin/python -m photo2.r284b.synthetic
.venv/bin/python -m photo2.r284b.run
.venv/bin/python -m photo2.r284b.review
.venv/bin/python -m photo2.r284b.validate_photo
.venv/bin/python -m photo2.r284b.package
.venv/bin/python -m unittest photo2.r284b.tests photo2.r284.tests photo2.r283.tests photo2.r282.tests
.venv/bin/python -m photo2.r284b.audit
/home/rharris/.local/bin/beads-chromium-review photo2.r2840.browser_check
```

Expected:59 tests;15 exact replay files;9916 previous Git blobs unchanged;
10 native crops pixel-exact;36 browser images/16 tables/10 case sections.
The audit writes its independent replay under `/tmp/beads-r284b-replay` and
verifies source/input hashes. `run --output /tmp/another-directory` produces an
independent bounded comparison. `r2840` is only the numeric browser-launcher adapter.

`methods.py` has no review coordinates or physical model inputs. `run.py` freezes
cases/cues and preserves the shared Phase1 schema. `diagnose.py`, `review.py`,
`validate_photo.py` and `package.py` are evaluation/rendering only; their reviewed
locations and captions never flow into inference. `synthetic.py` is a two-feature
analytic intensity field, not a physical-body rendering or bead-accuracy benchmark.

Each case JSON contains source cue/provenance,49×49 native linear Y, exact run-length
supports, peaks, native centroids, independent subpixel contours, shape/brightness
metrics, perturbations, signed-side/station evidence and pair conflicts. A/R283
black outputs are explicitly historical collar baselines. R1–R4 support kind is
`specular-reflection region`. Rejected oversized proposals remain inspectable;
all other alternatives are experimental/unresolved, with unrated reliability.
No Phase1 record gains physical identity or a black-body silhouette.

`results/pass01` retains the first restricted-domain pass and its exact two
algorithm/runner source snapshots. To reproduce its numerical science, copy
`methods.py.txt` and `run.py.txt` to `methods.py`/`run.py` in a temporary importable
package with an empty `__init__.py`; invoke that package's `run --output` while
keeping this checkout importable. Its old pair-list order used unsorted sets;
compare pairs by IDs/method/kind, not list byte order. The final runner sorts them
and passes exact byte replay. The old freeze refers to the source set at that
checkpoint; do not overwrite it with the final source hash set.

`results/selection-control` retains the mistaken peak-field selector's two affected
cases. The final selector uses `illumination.peak`; no easy replacement was chosen
for the unreliable same-color case. All failed mathematical and photo alternatives
remain visible. Checkpoints00–06 preserve reasoning and next steps across sessions.

Stop after delivery for user method selection. No automatic global adoption,
Phase2/3 optimization, new labeling request, model change or `/new`.
