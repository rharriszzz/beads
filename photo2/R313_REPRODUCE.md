# R313 reproduction and sealed experiments

Use repository `rharriszzz/beads`, branch `photo-2-strategy-v3`, the existing `.venv`,
and a C++17 compiler. Open [static review](r313/continuation/index.html) directly;
no server is needed. The numerical winner is experimental, not adopted.

Run the completed contracts and independent saved-model reproduction:

```sh
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/beads-r313-mpl .venv/bin/python -m unittest photo2.r313.tests photo2.r313.continuation_tests -v
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/beads-r313-mpl .venv/bin/python -m photo2.r313.continuation_verify
```

Verification rebuilds model positions/frames from saved parameters, recomputes all
three photographic split metrics, independently checks every contact support
witness and samples the original Python marcher against native owner/unknown rays.
It checks the fixed maps and all 426 earlier trial hashes. All 12 exports include
complete-necklace geometry and exactly the −100…99 target cohort. Ray verification
is stratified sampling, not exhaustive replay of every camera pixel.

The original interrupted 426-trial epoch is in `r313/results/trials`, its checkpoints
and `r313/evidence/fitting-source`; failed controls are preserved in
`r313/evidence/preflight-v1`. Do not rerun preparation or optimization over these
artifacts. The initial entry point remains `phase2_surface_fit.py`; its old
`--verify` command is superseded for this delivery by `continuation_verify` above.

Continuation sequence and saved outputs:

1. `continuation_setup`: hash original trials and recover three incumbents.
2. `sanity`, `sanity_v2`: deliberate corruption controls, including failed controls.
3. `diagnose_geometry`, `historical_contact_audit`: shared-shape/orientation probes
   and actual-solid contact classification. No illumination fitting.
4. `score_epoch2`: additional worst-core/exterior-envelope score, unchanged evidence.
5. `focused_search`: sealed four-start 420-second diagnostic, 808 saved proposals.
6. `finalize_continuation`, `physical_diagnosis`, `secondary_diagnostics`: frozen
   candidate exports, supporting-plane/first-error tests and independent reflections.
7. `continuation_review`: static raw/evidence/boundary/first-40/worst-20 images.
8. `continuation_verify`: independent reproduction and preservation audit.

These modules use the delivered directory. **Do not rerun mutation-producing steps
in the scientific checkout.** Use a separate disposable clone to regenerate static
outputs or conduct a separately authorized experiment. The search refuses an
existing sealed selection. Fixed seeds do not make wall-limited proposal counts
hardware-independent; exact saved-vector/model replay is the reproducibility test.

`continuation/search-plan.json` records exact fitting sources/bounds; its source
archive is `continuation/fitting-source/source.tar.gz`. `epoch2-freeze.json` records
the changed objective epoch. The photographic map SHA256 is
`aba2fc08f2dafa113caba376ccc27e24aea294af62b2f6b1943cb64b276a6600`.
Original and continuation scores are different objectives, not directly comparable.
Comparison arcs [−310,−230] and [230,310], plus 25px buffers, were excluded from
fitting; historical exposure prevents calling them fresh holdouts. Photographic
core records can overlap and are not independently verified physical identities.
