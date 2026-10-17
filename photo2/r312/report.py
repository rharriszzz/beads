"""Readable static R312 scientific and reproduction handoff."""
from pathlib import Path
import html
from photo2.r297.common import ROOT,read,save,sha,utc

def fmt(value):return '—' if value is None else f'{value:.3f}'

def write(root):
    root=Path(root);stages={i:read(root/f'stage{i}/diagnostics.json') for i in [1,2]}
    performance=read(root/'performance-comparison.json');verification=read(root/'verification.json')
    best={i:min([m for m in stages[i]['models'] if not m.get('tradeoff_only',False)],key=lambda m:m['metrics']['objective_px']) for i in stages}
    lines=['# R312 — physical-chain minimax and performance','',
        'R312 completes the authorized two-stage experiment. Measured computational speed improves substantially; photographic minimax gains are partial and do not establish a substantial overall reconstruction improvement. It preserves all historical science and source photographs. The output is a set of conditional geometry fits, not recovered bead identities or an adopted reconstruction. **Stop for scientific review; no Phase 3 or pattern inference.**','',
        '## Objective and physical scope','',
        'Stage 1 uses exactly the **200 consecutive physical addresses −100…99**. Hidden and partially occluded beads remain in the geometry. Every necklace body participates in camera/shadow occlusion and spatial contact checks, including neighbors at offsets +1, +6 and +7. Photographic safeguards use a frozen neighborhood around the original 200 centers. Stage 2 evaluates the full necklace.','',
        'The immutable Stage 1 photographic cohort contains 27 strong localized observations associated with this interval by the unchanged R306 reference. Stage 2 contains all 269 strong observations. All 811 catalog observations survive, including 542 weak/uncertain observations. A photographic reference point or reflection is not a measured physical bead center. The physical identity of every association remains unverified.','',
        'An initial native one-to-one bottleneck assignment establishes each hypothesis’s conditional owners. Owners remain frozen during each optimization epoch. The initial Stage 2 campaign retains Stage 1 owners; R311 distant basins share their parent’s map. A subsequent full-chain initialization control, explained below, starts a separately frozen before/after epoch. The primary loss is the **maximum Euclidean reflection displacement in image pixels**, plus 10000px per missing lobe. This penalty exceeds the image diagonal. Ambiguous strong observations remain in the maximum. Reassignment-only changes are never counted as geometry improvements. Exact measured max/RMS/P95 and missing counts are reported separately; a low measured maximum with missing lobes is never a successful minimax result.','',
        'Initially unambiguous associations (assigned nearest owner and a ≥3px gap to the next alternative) and initially ambiguous associations have separate statistics. These are numerical association diagnostics, not verified physical identities. Free rematching is retained only as a labeled secondary control, together with the number of reassigned observations. Weak observations have nearest-only descriptive diagnostics and never enter the primary loss.','',
        '## Native results','',
        '| Stage / basin | Before max / RMS / P95 (px) | After max / RMS / P95 (px) | Missing | Primary loss (px) | Dense safeguards |',
        '|---|---|---|---:|---:|---|']
    for i in [1,2]:
        for m in stages[i]['models']:
            b=m['before'];a=m['metrics']
            role=' [tradeoff only]' if m.get('tradeoff_only') else ''
            lines.append(f'| {i}: {m["name"]}{role} | {fmt(b["maximum_px"])} / {fmt(b["rms_px"])} / {fmt(b["p95_px"])} | {fmt(a["maximum_px"])} / {fmt(a["rms_px"])} / {fmt(a["p95_px"])} | {a["missing"]} | {fmt(a["objective_px"])} | {"pass" if m["dense_passes_safeguards"] else "regression; inspect"} |')
    for i in [1,2]:
        b=best[i];base=b['before']['maximum_px'];after=b['metrics']['maximum_px']
        gain=100*(base-after)/base if base else 0
        lines += ['',f'Stage {i}’s best native primary maximum is **{after:.3f}px**, versus {base:.3f}px for its own frozen-map baseline ({gain:.1f}% reduction). Its RMS is {b["metrics"]["rms_px"]:.3f}px and P95 is {b["metrics"]["p95_px"]:.3f}px, with {b["metrics"]["missing"]} missing observations. All retained models and their full parameters/contact witnesses remain in `r312/results/campaign/stage{i}/exports/`.']
        u=b['initially_unambiguous_metrics']
        lines += [f'For the initially unambiguous subset, the exact maximum / RMS / P95 is {fmt(u["maximum_px"])} / {fmt(u["rms_px"])} / {fmt(u["p95_px"])}px, with {u["missing"]} missing. Ambiguous observations remain in the conservative primary maximum above; neither subset establishes physical identity.']
        model=read(root/f'stage{i}/exports/{b["name"]}.json.gz')
        prefix='baseline-fullchain-' if i==2 else 'baseline-'
        common=read(root/f'stage{i}/exports/{prefix}R306-2405.json.gz')['result']['safeguards'];after_guard=model['result']['safeguards']
        lines += [f'Against the common R306 calibration in the same photographic region, dense ownership changes {common["ownership_percent"]:.3f}→{after_guard["ownership_percent"]:.3f}%, paper occupation {common["background_percent"]:.3f}→{after_guard["background_percent"]:.3f}%, colored omission {common["omission_percent"]:.3f}→{after_guard["omission_percent"]:.3f}%, and exterior boundary RMS {common["boundary_rms_px"]:.3f}→{after_guard["boundary_rms_px"]:.3f}px. Its minimum separating-plane margin is {model["physical"]["minimum_gap_units"]:.9f} source units; this is numerical nonpenetration for a conditional model, not a measured physical clearance or mechanical equilibrium.']
    initial=read(root/'stage2/selection.json');initial_best=min(initial['models'],key=lambda r:r['objective_px'])
    initial_summary=read(root/'stage2/summary.json')
    lines += ['',f'The separately preserved initial Stage 2 campaign ran {initial_summary["evaluations"]} evaluations in {initial_summary["elapsed"]/60:.2f} minutes; its best inherited-map objective was {initial_best["objective_px"]:.6f}px. The subsequent full-chain controls and contingent refinement are separately checkpointed under `stage2/local/`; their trials are included in the combined performance ledger.']
    lines += ['',
        'The initial full-necklace campaign exposed a scope problem: the immutable photographic cohort selected by the R306 reference can extend outside addresses −100…99 under another count hypothesis. Reserving its Stage 1 owners can then force a poor full-chain assignment. The complete initial 1800-second campaign and maps remain sealed. A separate control recomputes full-necklace assignments at **identical starting geometry**, saves every changed owner and labels all resulting score changes as correspondence-only. For example, unchanged R306-2733 changes 65.257→22.242px and N2860 hand− changes 97.973→15.438px, with no geometry improvement. The R306-2405 baseline changes no owners. The contingent local epoch freezes the new full-chain maps, retains all 269 observations, and compares each fitted result with its own refreshed-map baseline. Final Stage 2 tables use this epoch; every exported model also retains its original-map score as a control. These alternatives are conditional, not recovered bead identities. The main campaign’s inherited maps restricted useful exploration of denser families; its failure cannot rule those families out.','',
        'The search guards permit at most 2 percentage points loss of mean positive-interior support coverage, 1 point additional paper occupation, 2 points colored omission, 1px boundary RMS regression and no extra missing supported contour. Stage 1 compares each hypothesis with its own calibration. **Stage 2 requires both that comparison and preservation against the common R306-2405 baseline.** Lower-error models failing the common safeguards remain diagnostic tradeoffs. These are operational tolerances; they do not establish that every region improves. Dense measurements can also fail the sampled search guards. A reflection improvement alone does not establish a substantial overall photographic reconstruction improvement.','',
        'A post-seal audit found that my Stage 1 boundary guard included native hole edges, whereas the photographic contours annotate outer boundaries. Complete fitting records and original boundary scores remain preserved. Dense exterior-only diagnostics reuse the same saved native rays, with no fitting repeated and no change to any reflection result. Stage 2 uses exterior-only boundary guards. Native holes remain visible in overlays. This limits conclusions based on Stage 1 safeguard selection.','',
        '## Where large errors appear','',
        'For every retained basin, static plots show Euclidean error and signed tangential/transverse components against frozen conditional physical address. Separate positive/negative outward plots show individual errors and the cumulative maximum from address 0. First observed crossings of 5/10/15/20px are saved; gaps between observations are unknown, not verified error-free beads. Bead 0 has no independently verified reflection correspondence.','',
        'The twenty largest measured mismatches include observation IDs, native photographic locations, predicted points, displacement vectors, magnitude and conditional owner. Missing lobes are listed separately. Before/after photographic overlays include complete native visible boundaries for the rendered target bodies; all other bodies still occlude them. Orange annotations mark ambiguous alternatives or a frozen owner different from the nearest alternative. The top-20 crop atlas uses dashed white vectors for the baseline.','']
    for i in [1,2]:
        m=read(root/f'stage{i}/exports/{best[i]["name"]}.json.gz')
        prefix='baseline-fullchain-' if m.get('correspondence_epoch')=='full-chain' else 'baseline-'
        baseline=read(root/f'stage{i}/exports/{prefix}{m["family"]}.json.gz')
        lines += [f'### Stage {i} best basin: first observed ≥10px errors','']
        for label,doc in [('Before',baseline),('After',m)]:
            for r in doc['first_large']:
                if r['threshold_px']!=10:continue
                first=r['first'];direction='negative' if r['direction']<0 else 'positive'
                lines.append(f'- {label}, toward {direction} addresses: '+(f'{first["id"]}, conditional index {first["index"]}, {first["error_px"]:.3f}px at {first["observed"]}.' if first else 'no observed crossing in the retained cohort.'))
        changes=[]
        for before,after in zip(m['before_regional'],m['regional']):
            a=after['reflection']['maximum_px'];b=before['reflection']['maximum_px']
            if a is not None and b is not None:changes.append((a-b,after['section']))
        if changes:
            gains=sorted(changes)[:3];losses=sorted(changes,reverse=True)[:3]
            lines += ['', 'Largest regional maximum-error changes (after minus before; negative improves): '+', '.join(f'section {sec}: {delta:+.3f}px' for delta,sec in gains+[x for x in losses if x not in gains])+'. These fixed photographic sections are diagnostic, not independent tests.']
        lines += ['',f'![Stage {i} before/after](r312/results/campaign/stage{i}/plots/{m["name"]}-overlay.png)',
                  f'![Stage {i} signed errors](r312/results/campaign/stage{i}/plots/{m["name"]}-errors.png)',
                  f'![Stage {i} outward errors](r312/results/campaign/stage{i}/plots/{m["name"]}-outward.png)',
                  f'![Stage {i} largest twenty](r312/results/campaign/stage{i}/plots/{m["name"]}-top20.png)',
                  f'![Stage {i} regional changes](r312/results/campaign/stage{i}/plots/{m["name"]}-regional.png)','']
    lines += ['## Search breadth and limitations','',
        'The existing periodic planar axis, true arclength transport, affine annulus and shared optical law are retained. The optical law is a positional approximation, not a calibrated radiometric model. Phase/registration, elevation/roll/tilt, scale/perspective, minor radius/axial thickness, winding/turn, gap, height laws, shared light direction/roughness/distance and the existing smooth axis/phase/spacing fields are varied in coupled blocks. Mean axial advance/pitch follows true length, count, scale and gap; the inactive legacy `pitch` field is not advertised as a fitted degree of freedom. No new bead-shape law or per-bead correction is introduced.','',
        'Scrambled Sobol proposals interleave full-box and moderate/wide coupled blocks across hypotheses; multistart perturbations and differential evolution refine multiple feasible basins. Both hands and both topologies are represented, with count hypotheses spanning 2000…3200. Discrete combinations and joint boxes are sampled, not exhaustively enumerated. The maker’s minimum count 2000 and near-6.5 winding/closure-twist constraint remain distinct from numerical exploration boxes and inherited field-rate bounds. An uncertified separating-plane search is inconclusive, not a demonstrated penetration.','']
    for i in [1,2]:
        p=stages[i]['performance'];coverage=read(root/f'stage{i}/coverage.json')
        lines += [f'- Stage {i}: {p["evaluations"]} unique evaluations in {p["elapsed"]/60:.2f} wall minutes / {p["cpu_seconds"]/60:.2f} CPU minutes; {p["strict_running_best_improvements"]} strict running-best safeguarded improvements; statuses `{p["statuses"]}`; kinds `{p["kinds"]}`. Peak RSS {p["peak_rss_mib"]:.1f}MiB. Attempted counts `{coverage["counts"]}`. Native improvement per CPU-second: {p["useful_native_gain_px_per_cpu_second"]:.6f}px/s.']
    lines += ['',
        'Full parameter ranges and projection plots show actual attempts and certified outcomes separately. Range endpoints from different candidates do not imply joint coverage. Failed searches remain in atomic trial files. Fixed conditional owners prevent reassignment-only gains but can penalize a legitimately relabeled distant basin; physical identities remain unknown. Finite time, discrete starts, existing shape laws and numerical bounds limit negative inference. The R297 legacy placement implementation remains historical and is not a fresh R312 fitting family. Immutable family keys retain two old plus-hand aliases; displayed counts/hands/topologies come from actual parameters. The result does not establish that the photographed necklace cannot be reconstructed with the existing geometry.','',
        'Stage 1 seals its checkpoint and saves distinct native basins and complete static diagnostics before Stage 2. The later exterior-only control overlaps Stage 2 initialization, as recorded in the milestone receipt. Stage 2 changes the same continuous parameters again; it does not freeze Stage 1 values. Its initial starts include Stage 1 basins and the original hypotheses. The contingent 600-second multistart Nelder-Mead epoch refines shared illumination, coupled geometry/camera and existing harmonic fields from three full-chain controls. The preflight’s 2px lattice lost small lobes and shifted some individual errors substantially, so native 1px fitting is used for the executed Stage 2; the 2px measurements remain explicit approximation diagnostics.','',
        'All available strong photographic observations enter fitting. Dense final measurements and historical comparisons are retrospective diagnostics, not fresh validation or statistically independent holdouts. Correlated pixels are not independent observations. Only 16 uncertain photographic contours exist; their boundary uncertainty remains approximately ±3px, and unannotated bodies have no measured complete photographic outlines.','',
        '## Performance before fitting','',
        'The initial paused benchmark completed normally and was reused. Its optical timing suite uses the same 2px lattice for both implementations; the later minimax timing suite and executed fitting use native 1px sampling. Original-Python accuracy audits separately use 1px sampling. Statistical Python stack sampling identifies native work by its Python call site; it can be delayed by the GIL. Exclusive wall timers measure geometry, contact, camera rays, surface normals, shadow occlusion, reflection assembly, outlines, correspondence and safeguards. Numerical threads are fixed to one. Warm timings use medians of two repetitions; these are measurements on this machine, not precise population estimates.','',
        '| Same-lattice benchmark | Before (s) | Optimized (s) | Speedup |',
        '|---|---:|---:|---:|']
    for r in performance['original_baseline']:lines.append(f'| {r["region"]} bodies, {"finite" if r["finite_light"] else "directional"} light | {r["before_seconds"]:.4f} | {r["after_seconds"]:.4f} | {r["speedup"]:.2f}× |')
    lines += ['','| Full-necklace finite-light subsystem | Before (s) | After (s) | Speedup |','|---|---:|---:|---:|']
    components=next(r['components'] for r in performance['original_baseline'] if r['region']=='whole' and r['finite_light'])
    for name,r in components.items():lines.append(f'| {name} | {r["before_seconds"]:.5f} | {r["after_seconds"]:.5f} | {r["speedup"]:.2f}× |')
    lines += ['',
        'Contact checks avoid refining pairs after a valid positive analytic separating plane is found. Finite-light queries conservatively enclose projected bounding spheres on the light-centered unit sphere before the unchanged native marcher. Directional shadow trees are reused. Bounded caches reuse geometry, contact results and native camera first hits when only illumination changes. Stage 2 renders complete boxes for frozen target owners, while retaining all occluders. Exact centroid thresholds, annulus shape, marching tolerance, unknown-ray treatment and light law remain unchanged.','',
        'Initial timing identified contact refinement and finite-light all-pairs shadow queries as worthwhile targets. Geometry construction was a few milliseconds and did not justify a new compiled placement kernel. After acceleration, camera rays and shadow rays dominate. Analytical reflection positions were considered but not substituted for complete annular visible lobes: holes, changing ownership and shadows require native evaluation. The old complete photographic objective, which excludes contact checks, measured 1.754s before and 1.784s afterward in its single pair; no speedup is claimed for that test.','',
        '| Complete native minimax evaluation | Cold (s) | Camera reused (s) | Speedup |',
        '|---|---:|---:|---:|']
    for r in performance['minimax_cache']:lines.append(f'| Stage {r["stage"]}, {"finite" if r["finite_light"] else "directional"} light | {r["cold_native_seconds"]:.4f} | {r["cached_native_seconds"]:.4f} | {r["speedup"]:.2f}× |')
    if 'stage2_optimizations' in performance:
        x=performance['stage2_optimizations'];lines += ['',f'Stage 2 adds measured exact improvements against the archived Stage 1 objective: alternative-distance bookkeeping {x["matching"]["speedup"]:.2f}× faster ({x["matching"]["stage1_original"]["median_seconds"]:.4f}→{x["matching"]["vectorized"]["median_seconds"]:.4f}s), repeated unchanged-contact evaluation {x["unchanged_contact_reuse"]["speedup"]:.2f}× faster, and a three-evaluation native illumination batch {x["native_illumination_batch"]["speedup"]:.2f}× faster. Primary errors/owners are exact and alternative-distance roundoff is {x["matching"]["maximum_alternative_distance_roundoff_px"]:.3g}px. Illumination proposals are batched so the measured camera reuse is actually used by the search.']
        for stage in [1,2]:
            pp=stages[stage]['performance'];lines += [f'- Stage {stage}: {pp["camera_reused_evaluations"]} camera-reused evaluations, {pp["contact_reused_evaluations"]} recorded contact-reused evaluations, {pp["camera_rays_avoided_by_reuse"]} camera rays avoided by reuse.']
    lines += ['',
        'Caching helps illumination proposals with unchanged geometry; arbitrary geometry changes still pay for new first hits. Exact cold-versus-cached predictions agree. Initial original-Python audits reported zero centroid differences. The minimax preflight also exactly agrees with the previous native predictor. Computational agreement is not photographic accuracy: a 10px photographic mismatch remains a 10px mismatch even when both renderers agree numerically.','',
        'The preflight’s 2px approximation changes some errors by up to 10.68px and changes lobe presence; it is not treated as a reliable substitute for native minimax. Baseline/optimized subsystem timings, stack samples, approximation measurements, memory and per-trial wall/CPU times are retained in the performance comparison and both stage ledgers. The ledger retains the chronology of both correspondence epochs; its running-best reduction must be interpreted alongside the same-map before/after model tables, and is not automatically a pure geometry gain. Increased throughput permits the recorded thousands of direct broad proposals and native refinements; it does not prove that the same basins would have been unreachable with a slower implementation and more time.','',
        '![Performance comparison](r312/results/campaign/performance-comparison.png)','',
        '## Independent verification and delivery','',
        f'The fresh-process verifier passes {verification["unique_trial_vectors"]} unique trial records and {len(verification["models"])} exported model/baseline combinations: {verification["positions"]} positions, {verification["independent_contact_witnesses"]} independently recomputed analytic contact witnesses, {verification["original_python_camera_and_guard_rays"]} original-Python camera/guard rays, {verification["original_compiled_optical_rays"]} original compiled optical rays for every fitted lobe, and {verification["original_python_top20_optical_rays"]} original-Python optical rays for the actual top twenty errors. Primary centroids agree within 1e-9px; all reported distances, RMS/P95/max, fixed maps, complete 200-address cohorts and source archives pass. Arclength refinement and right-handed orthonormal frames are checked.','',
        f'Preservation audit checks {verification["historical_files_checked"]} pre-existing tracked files. Historical scientific data and source photographs are byte-identical; handoffs/logs contain only additive text. Exact fitting-source bundles preserve both stages. The scientific push and independent remote-tip receipt are recorded separately in `r312/results/delivery.json`.','',
        'Static review: [R312 index](r312/results/campaign/index.html). Numerical receipt: [verification](r312/results/campaign/verification.json). Full protocol: [specification](R312_SPECIFICATION.md). Reproduction: [commands](R312_REPRODUCE.md).','',
        '**Stop for maker review of the minimax/material/regional tradeoffs.** No model adoption, Phase 3, color-pattern inference or automatic R313. Keep this session for review; no `/new` or model switch is needed.']
    controls=read(root/'numerical-resolution-controls.json.gz')
    lines += ['','## Resolution sensitivity','']
    for c in controls:lines.append(f'- Stage {c["stage"]}: identical parameters/maps at 0.5px sampling shift centroids by at most {c["maximum_centroid_shift_px"]:.3f}px; {len(c["lobe_presence_changes"])} lobe-presence changes. Native max {fmt(c["native_metrics"]["maximum_px"])}px; half-pixel max {fmt(c["half_pixel_metrics"]["maximum_px"])}px. This is computational sampling sensitivity, not a new fit or physical ground truth.')
    lines += ['', 'Export alternative lists, weak nearest-only diagnostics and secondary rematching use their rendered target-owner pool, and can omit unrendered competitors. Primary maps remain frozen and all strong observations enter the maximum regardless of this ambiguity flag. The separate all-body optical-pool control checks the full-necklace best and baseline without changing parameters, maps or selection.']
    pool=root/'full-necklace-optical-pool-control.json.gz'
    if pool.exists():
        for c in read(pool)['models']:lines.append(f'- {c["name"]}: {c["body_count"]} bodies, {c["predicted_lobes"]} native lobes, {c["rays"]} rays; maximum target-only versus all-body centroid difference {c["maximum_target_pool_centroid_difference_px"]:.3g}px. Full-pool free rematching gives max {fmt(c["full_pool_free_rematch_control"]["metrics"]["maximum_px"])}px with {c["full_pool_free_rematch_control"]["reassigned"]} owner changes; that is a correspondence control, not a fitting gain.')
    report='\n'.join(lines)+'\n'
    (root/'R312_REPORT.md').write_text(report.replace('r312/results/campaign/',''))
    delivered=root.resolve()==(ROOT/'photo2/r312/results/campaign').resolve()
    if delivered:(ROOT/'photo2/R312_REPORT.md').write_text(report)
    reproduce='''# R312 reproduction

Work on `photo-2-strategy-v3` in `rharriszzz/beads`. Existing `.venv` supplies
Python 3.12, NumPy, SciPy, Pillow and matplotlib. Numerical threads are fixed to
one by the entry point. Use a **new output directory** for new experiments.

```sh
python3 photo2/phase2_minimax.py --output /tmp/r312-new --profile-only
python3 photo2/phase2_minimax.py --output /tmp/r312-new --stage 1 --seconds 1800
python3 photo2/phase2_minimax.py --output /tmp/r312-new --stage 1 --seconds 1800 --resume
```

The delivered experiment reuses the completed initial profiling files. The
additional exact/caching preflight is `python -m photo2.r312.preflight` under
`.venv`, with the same thread environment. It is not fitting. Stage 1 source is
archived exactly, including the initial entry point. The later `--native-only`
entry option configures Stage 2's existing native search phase in response to
the preflight, without changing Stage 1 search calculations.

Save Stage 1 static diagnostics before starting Stage 2:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MPLCONFIGDIR=/tmp/beads-r312-mpl .venv/bin/python -c 'from pathlib import Path; from photo2.r312.delivery import stage_diagnostics; stage_diagnostics(Path("/tmp/r312-new"),1)'
python3 photo2/phase2_minimax.py --output /tmp/r312-new --stage 2 --native-only --seconds 1800
python3 photo2/phase2_minimax.py --output /tmp/r312-new --stage 2 --native-only --seconds 1800 --resume
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MPLCONFIGDIR=/tmp/beads-r312-mpl .venv/bin/python -m photo2.r312.local_refine --output /tmp/r312-new --seconds 600
python3 photo2/phase2_minimax.py --output /tmp/r312-new --finalize
```

Source bundles are written automatically for new runs. Exact Stage 1 source in
the delivered run was archived before the Stage 2 performance update.
Source/evidence/environment mismatches reject a resume. SIGTERM
or SIGINT finishes the current trial and atomically checkpoints. A complete
orphan trial is recovered without rerendering. A directory lock rejects another
writer. A sealed stage cannot resume. Budgets are cumulative wall allowances;
hardware/load and time limits mean exact proposal counts are not promised.
Seeds, complete parameters, proposal-plan hashes and all executed vectors are
saved. Initial Stage 2 retains Stage 1 fixed maps; the contingent full-chain epoch
saves correspondence-only controls and freezes new full-chain maps before fitting.
All fitted continuous parameters can change. Local refinement also supports
`--resume`. Finalization runs verification in a fresh process automatically;
`python3 photo2/phase2_minimax.py --verify` reruns only that audit if needed.

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MPLCONFIGDIR=/tmp/beads-r312-mpl .venv/bin/python -m unittest photo2.r312.tests -v
```

Open `photo2/r312/results/campaign/index.html` or individual static PNGs directly.
No browser application or interactive viewer is needed. Each stage contains
top-20 JSON/CSV/PNG, missing observations, outward thresholds, signed error plots,
native before/after overlays, regional outcomes and a performance ledger.
Historical experiments/source photographs and `beads.pov` are preserved.
'''
    (root/'R312_REPRODUCE.md').write_text(reproduce)
    if delivered:(ROOT/'photo2/R312_REPRODUCE.md').write_text(reproduce)
    parts=['<!doctype html><html><meta charset="utf-8"><title>R312 scientific review</title><style>body{font:16px system-ui;max-width:1200px;margin:2em auto;padding:1em;background:#f8f6f1;color:#24313b}img{max-width:100%;height:auto}a{color:#006f99}article{margin:3em 0}table{border-collapse:collapse}td,th{padding:.5em;border:1px solid #aaa}</style><body><h1>R312 — native minimax scientific review</h1><p>All bead identities remain conditional. No model adoption. Stop for maker review; no Phase 3.</p><p><a href="../../../R312_REPORT.md">Scientific report</a> · <a href="verification.json">Independent numerical verification</a> · <a href="performance-comparison.json">Performance measurements</a></p>']
    for i in [1,2]:
        parts.append(f'<h2>Stage {i}</h2><p>{"200 consecutive physical beads −100…99; full-chain occlusion/contact" if i==1 else "Complete necklace; all 269 strong observations"}. Native 1px maxima; frozen one-to-one owners; all ambiguous strong observations retained.</p>')
        parts.append(f'<p><a href="stage{i}/performance-ledger.csv">Evaluation ledger CSV</a> · <a href="stage{i}/coverage.json">Actual search coverage</a></p><img src="stage{i}/plots/progress.png"><img src="stage{i}/plots/coverage.png">')
        for m in stages[i]['models']:
            name=m['name'];a=m['metrics'];parts.append(f'<article><h3>{html.escape(name)}</h3><p>Max {a["maximum_px"]:.3f}px · RMS {a["rms_px"]:.3f}px · P95 {a["p95_px"]:.3f}px · Missing {a["missing"]} · Dense safeguards: {m["dense_passes_safeguards"]}</p>')
            parts.append(f'<p><a href="stage{i}/plots/{name}-reflections.csv">All displacements CSV</a> · <a href="stage{i}/plots/{name}-top20.json">Top twenty JSON</a> · <a href="stage{i}/plots/{name}-missing.json">Missing</a> · <a href="stage{i}/plots/{name}-first-large.json">First large errors</a> · <a href="stage{i}/exports/{name}.json.gz">Complete model/evidence</a></p>')
            for suffix in ['overlay','errors','outward','top20','regional']+(['physical200'] if i==1 else []):parts.append(f'<img loading="lazy" src="stage{i}/plots/{name}-{suffix}.png" alt="{html.escape(name)} {suffix}">')
            parts.append('</article>')
    parts.append('<h2>Performance</h2><img src="performance-comparison.png"></body></html>');(root/'index.html').write_text('\n'.join(parts).replace('../../../R312_REPORT.md','R312_REPORT.md'))
    save(root/'publication.json',dict(utc=utc(),report_sha256=sha(root/'R312_REPORT.md'),reproduce_sha256=sha(root/'R312_REPRODUCE.md'),index_sha256=sha(root/'index.html'),static_review=True))
    validate_static(root)

def validate_static(root):
    from html.parser import HTMLParser
    from urllib.parse import urlsplit,unquote
    from PIL import Image
    class Links(HTMLParser):
        def __init__(self):super().__init__();self.links=[]
        def handle_starttag(self,tag,attrs):
            for k,v in attrs:
                if k in ['href','src'] and v:self.links.append(v)
    parser=Links();parser.feed((root/'index.html').read_text());checked=[]
    for link in parser.links:
        url=urlsplit(link);assert not url.scheme and not url.netloc,link
        target=(root/unquote(url.path)).resolve();assert target.is_file(),target
        checked.append(link)
    images=[]
    for path in sorted(root.rglob('*.png')):
        with Image.open(path) as im:
            width,height=im.size;im.verify()
        images.append(dict(path=str(path.relative_to(root)),width=width,height=height,sha256=sha(path)))
    save(root/'static-review-check.json',dict(passed=True,utc=utc(),links_checked=checked,images=images,no_network_or_javascript_required=True,source_photo_sha256=sha(ROOT/'beads-photo-2.jpg')))
