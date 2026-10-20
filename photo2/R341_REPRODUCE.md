# R341 reproduction

Start at R340 delivery6484b9da on `photo-2-strategy-v3`. Current files are under `photo2/r341/`. Earlier stopped, untracked R340 development is preserved and unused.

From the repository root:

```
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r341/experiment.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r341/audit_panels.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r341/native_audit.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r341/audit_uncertain.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r341/excluded_controls.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r341/freeze.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r341/pattern.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r341/evaluate.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r341/review.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r341/verify.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python photo2/r341/replay.py
/home/rharris/.local/bin/beads-chromium-review photo2.r341.browser_check
```

`recognize.py` contains the complete3×3/73.5 measurement and the two predeclared simple search regions. `experiment.py` selects on52 development cases only, saves the selection, then evaluates64 other maker labels. No later tuning follows. Local affine geometry is estimated from unchanged native primitive links; only geometric positions enter.

`native_audit.py` contains explicit photographic ownership annotations after inspection of all16 black/red and seven yellow atlas pages and all19 expanded disagreement contexts. Its50 initial flags, six expanded-context ownership confirmations,44 remaining uncertainties and12 accepted changes are scientific inputs. Replaying these annotations is not an independent second human inspection. Every observation retains its native page/number, region pixels, actual3×3 RGB, raw/autonomous/audited output, ownership assessment and binary recorded-label agreement. Red/yellow pigment certification is explicitly separate from not-black.

`freeze.py` preserves all prior metadata and writes the reversible color overlay and evidence hashes before any R341 pattern analysis. `pattern.py` uses only fixedA/2704/208, identical cohorts/folds, and strict conflicts; `evaluate.py` keeps raw, autonomous eligibility, native audit and maker truth separate. Excluded maker colors remain reference-only and never reenter the active graph.

`R341_RUN_ROOT` redirects generated outputs. `replay.py` creates a fresh `/tmp` directory and runs the full pipeline including independent verification. It compares17 decoded scientific products, all58 reproducible atlas/detail/literal images and offline HTML. Only measured seconds/UTC and dependent `*_sha256` fields are excluded from comparison; the fresh verifier checks producer hashes independently. Delivery screenshots are separate browser receipts.

`verify.py` independently reconstructs local affine maps using normal equations, complete region masks and all candidate patch maxima; checks original RGB values, model choice, maker protections, unchanged graph geometry and each strict entry; and independently recomputes all eight matched held-out prediction metrics. It does not call the classifier or pattern consensus/prediction helper for those checks.

The offline review presents four questions and21 native panels, each with its own stable-ID key and target1. A comparison photograph's numbers belong to that comparison only. The complete inventory and audit atlas remain available without turning correct observations into maker questions.
