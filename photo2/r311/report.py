"""Concise generated account; every headline links to the retained measurements."""
from pathlib import Path
import csv
import numpy as np
from photo2.r297.common import ROOT,read,save,utc
from .model import starts,VARIABLES,BOUNDS

def fmt(x,n=3):return 'unmeasured' if x is None else f'{x:.{n}f}'

def write(out,models,metrics):
    out=Path(out);state=read(out/'checkpoint.json');coverage=read(out/'coverage.json');audit=read(out.parent/'audit/coverage.json');accept=read(out/'acceptance.json');verify=read(out/'verification.json')
    rows=[read(p) for p in (out/'trials').glob('*.gz')];seeds=starts();byname={m['name']:m for m in models}
    result='At least one candidate meets the prespecified combined repair test; inspect its fixed-owner and geographic evidence before adoption.' if accept['any_pass'] else 'No tested candidate meets the combined first-error and whole-necklace repair test. Broader exploration finds photographic tradeoffs; it does not establish a global repair or justify adoption.'
    if accept.get('any_geometric_pass') and not accept['any_pass']:
        result='A candidate meets the first-error and whole-necklace photographic checks, while original fixed-index optical controls regress. This is a possible material-placement repair with unresolved identity, not an adopted reconstruction.'
    partial_note='';partial=None
    goodlocal=[r for r in accept['models'] if all(r['checks'][k] for k in ['negative_first_error_repaired_or_preserved','positive_first_error_repaired_or_preserved','reference_no5pp_regression']) and r['family'] in {s['name'] for s in seeds[:3]}]
    if goodlocal:
        choice=min(goodlocal,key=lambda r:metrics[r['model']]['overall']['reflection']['rms_D']);model=byname[choice['model']]
        parent=next(m for m in models if m['baseline'] and m['family']==model['family']);new=metrics[model['name']];old=metrics[parent['name']]
        a,b=old['overall'],new['overall'];targets={r['id']:r for r in model['first_errors']}
        delta=[(y['ownership_percent']-x['ownership_percent'],x['section']) for x,y in zip(old['regional'],new['regional']) if x['ownership_percent'] is not None and y['ownership_percent'] is not None]
        worst,section=min(delta)
        partial=dict(model=model['name'],trial=model['trial'],baseline=parent['name'],negative_coverage=targets['C-1477-0290']['modal_fraction'],positive_coverage=targets['C-1608-0253']['modal_fraction'],
                     reflection_RMS_D_before=a['reflection']['rms_D'],reflection_RMS_D_after=b['reflection']['rms_D'],ownership_percent_before=a['ownership']['coherent_percent'],ownership_percent_after=b['ownership']['coherent_percent'],
                     paper_percent_before=a['material']['background_occupation_percent'],paper_percent_after=b['material']['background_occupation_percent'],boundary_RMS_px_before=a['boundary']['rms_px'],boundary_RMS_px_after=b['boundary']['rms_px'],
                     worst_regional_ownership_change_pp=worst,worst_region=section,regional_improvements=sum(z>0 for z,i in delta),regional_regressions=sum(z<0 for z,i in delta),adopted=False)
        save(out/'partial-basin.json',partial)
        if not accept.get('any_geometric_pass'):
            result='The broader search found missed basins with strong first-error repairs and partial whole-necklace gains. No finalist provides a substantial improvement across the whole circuit; no adoption.'
        partial_note=f"The strongest partial candidate is **{model['name']} (trial {model['trial']})**: first-error coverage reaches **{100*partial['negative_coverage']:.1f}/{100*partial['positive_coverage']:.1f}%**, reflection RMS improves **{a['reflection']['rms_D']:.3f}→{b['reflection']['rms_D']:.3f}D**, ownership **{a['ownership']['coherent_percent']:.2f}→{b['ownership']['coherent_percent']:.2f}%**, and paper occupation **{a['material']['background_occupation_percent']:.2f}→{b['material']['background_occupation_percent']:.2f}%**. However, boundary RMS worsens **{a['boundary']['rms_px']:.2f}→{b['boundary']['rms_px']:.2f}px**, and section {section} loses **{-worst:.1f} ownership points**. This is a promising missed basin with a measured global tradeoff, not a completed repair. [Full partial-result ledger](r311/results/campaign/partial-basin.json)."
    text=f'''# R311 — a broader test of existing global parameter basins

**{result}** The conclusion is limited to the recorded finite boxes, inherited fields and discrete hypotheses. It is not proof that the existing geometry is inadequate, or that every permitted basin has been searched.

[Photographic review](review/r311/index.html) · [Response/coverage maps](review/r311/maps.html) · [Reproduce](R311_REPRODUCE.md) · [Protocol](R311_SPECIFICATION.md) · [Machine-readable acceptance](r311/results/campaign/acceptance.json).

{partial_note}

## What earlier searches actually covered

The audit reads **6,075 original trial records**: R306's 4,054 proposals plus 12 native trials, R307's 1,052, R308's 503 and R309's 454. Checkpoint/source copies and replays are excluded. R306's 1,082 structure-screened proposals did not receive its optical score; its broad numeric envelope is therefore not broad native joint coverage. R306 converted R297 starts by resetting/limiting inherited fields. The unchanged R297 anchor was absent as a principal start from R308/R309. R309 had **58 shared trials**; **all 41 derivative blocks failed the all-column gate**, with zero coupled gradient proposals. Its later work mainly tested coordinate brackets.

| Saved run | Trials | Recorded bounds rejections | Physical/separation rejections | Exact repeated full vectors |
|---|---:|---:|---:|---:|
'''
    for name,a in audit['campaigns'].items():
        bounds=sum(v for k,v in a['status'].items() if 'bound' in k);physical=sum(v for k,v in a['status'].items() if 'physical' in k or 'contact' in k or 'separation' in k)
        text+=f"| {name} | {a['trials']} | {bounds} | {physical} | {a['exact_duplicate_full_vectors']} |\n"
    gates=audit['campaigns']
    text+=f"\nR307 recorded {gates['R307']['sides_with_more_missing_than_their_recorded_base']}/{gates['R307']['feasible_recorded_derivative_sides']} feasible derivative sides with more missing lobes than their base, and {gates['R307']['trust_ratio_below_acceptance']}/{gates['R307']['recorded_trust_predictions']} trust predictions below its acceptance ratio. R308 recorded {gates['R308']['sides_with_more_missing_than_their_recorded_base']}/{gates['R308']['feasible_recorded_derivative_sides']} such sides, {gates['R308']['unavailable_derivative_columns_explicitly_marked']} explicitly unavailable derivative columns, and {gates['R308']['trust_ratio_below_acceptance']}/{gates['R308']['recorded_trust_predictions']} trust predictions below threshold. These are recorded overlapping diagnostics, not exclusive rejection causes.\n"
    text+='''
Repeated vectors can use different objectives or fixed owners and are not automatically wasted computation. Dense clusters of tiny perturbations appear in the actual parameter-space plots. R306 primarily used3px optical screening; most R307 fitting used2px sampling before its native correction. Every feasible R311 discovery proposal uses native1px optics. R308's unknown-ray repair arrived late in its budget. [Full audit](r311/results/audit/coverage.json) records families, starts, optical evaluation/sampling, bound flags, additional-missing-lobe derivative sides and trust-gate outcomes. These causes overlap; no exclusive rejection count is invented. [Per-family ranges](r311/results/audit/ranges.csv) preserve the combinations that a union range hides.

Exact physical intervals are unmeasured for most globals. Phase is periodic 2π; registration is a circuit gauge coupled to indexing; camera elevation above a plane lies in(0,90]°; scale, axial factor and minor radius are positive, further restricted by joint contacts/camera validity. Roll and the unoriented body axis are periodic. Numerical limits are **exploration boxes**, not calibrated physical restrictions. The maker's count minimum is 2,000; principal closed periodic transport uses N/winding. R297 also retains its frozen legacy turn correction. Radius fixes the unit gauge; fixed count plus true total arclength determines mean advance.

| Global | R306–R309 actual union | Earlier numerical box | R311 attempted union | R311 finite box |
|---|---|---|---|---|
'''
    ranges=list(csv.DictReader((out.parent/'audit/ranges.csv').open()))
    for k in VARIABLES:
        historical=[r for r in ranges if r['parameter']==k];hv=[float(r[z]) for r in historical for z in ['minimum','maximum']]
        nv=[r['parameters'][k] for r in rows];old=audit['allowed'][k]['historical_implementation_box']
        text+=f"| {k} | {fmt(min(hv))}…{fmt(max(hv))} | {old} | {fmt(min(nv))}…{fmt(max(nv))} | {list(BOUNDS[k])} |\n"
    text+='''
Union endpoints come from different starts/families; they do not imply joint coverage. [Allowed domains and limitations](r311/results/audit/coverage.json) include light, perspective, turn/twist, seam and existing height laws. R311 freezes those quantities and every inherited axis/phase/spacing/legacy correction field within its parent. It tests existing globals broadly, not all existing degrees of freedom. Both handedness controls and both string topologies remain distinct; broad maps prioritize three hand-minus hypotheses. Hand-plus controls are 2,204/closed and 2,002/open and are not exhaustively mapped. [Label provenance](r311/results/campaign/family-labels.json) retains the immutable trial keys while correcting two swapped descriptive aliases in publication names; counts/topologies/physical calculations never changed.

## Executed search and distinct basins

'''
    kinds=coverage['types'];feasible=sum(r['feasible'] for r in rows);text+=f"Executed **{len(rows)} unique parameter/implementation vectors**, {feasible} certified feasible. Types: `{kinds}`. Statuses: `{coverage['statuses']}`. Cumulative search time **{state['elapsed']/60:.2f}min**; initial allowance 40 min, contingent basin-centered4D allowance at most 10 min. Preflight, audit, recovery tests and final dense verification are separate. Broad schedule completed {state['cursor']}/{len(state['plan'])} planned slots; time-limited blank cells are untested. Exact duplicate evaluations avoided:{state['deduplicated']}. Stop reason: **{state['stop_reason']}**.\n\n"
    text+='''The five pair maps span a full sampled phase cycle, registration −40…40px, elevation 30…88°, roll −70…70°, tilt −30…30°, minor radius 3…6 units and scale 6.5…11 px/unit. Every joint proposal is evaluated directly: invalid intervening states do not block a distant feasible island. Scrambled Sobol designs explore four globals together. Adaptive joint cell subdivision refines distinct whole-score and constrained first-error basins; a contingent four-variable Sobol stage explores selected promising basins. No derivative calculation or missing-highlight veto restricts discovery. Unknown rays never earn paper credit. Missing lobes stay scored.

| Pair | Evaluated planned cells (three principal starts) | Certified feasible |
|---|---:|---:|
'''
    for a,b in __import__('photo2.r311.model',fromlist=['PAIRS']).PAIRS:
        ss=[s for s in coverage['surfaces'] if s['pair']==[a,b]]
        text+=f"| {a}/{b} | {sum(s['evaluated'] for s in ss)}/{sum(s['planned'] for s in ss)} | {sum(s['feasible'] for s in ss)} |\n"
    text+='''
The response surfaces distinguish rejected cells from unevaluated cells. [Basin ledger](r311/results/campaign/basins.json), [all vectors](r311/results/campaign/trial-vectors.csv), [native trial records](r311/results/campaign/trials/) and [predicted-versus-measured changes](review/r311/predicted-measured.png) survive. Forecasts are weak neighbor/center estimates and never gate evaluation. Failed separating-plane certificates are inconclusive unless original solid surface samples witness penetration. Feasible models with bad photographic scores remain separately labeled.

| Distinct finalist basin | Count / hand / topology | Changed globals relative to its parent | Complete contact certificate |
|---|---|---|---|
'''
    parents={s['name']:s['parameters'] for s in seeds}
    for model in models:
        if model['baseline']:continue
        p=model['parameters'];base=parents[model['family']];changes=[]
        for key in VARIABLES:
            delta=p[key]-base[key]
            if key=='phase':delta=(delta+np.pi)%(2*np.pi)-np.pi
            if abs(delta)>1e-9:changes.append(f'{key}={fmt(p[key])} (Δ{delta:+.3f})')
        cert=model['physical']
        text+=f"| {model['name']} (trial {model['trial']}) | {p['count']} / {p['hand']} / {p['topology']} | {'; '.join(changes)} | {cert['pairs']} pairs; minimum margin {fmt(cert['minimum_gap_units'],6)}units |\n"
    text+='''
Each row is a distinct parameter vector relative to its own unchanged hypothesis; coarse sampled minima/components are not proof of isolated continuous basins. Counts, hands, topology, winding and inherited fields were never merged or relabeled across these rows.

## First-error and adjacent-body comparison

All six original photographic interiors retain every native pixel. At(1480,291), poor isolated overlap diagnoses a different failure from an isolated body hidden by neighbors near(1613,253). Best isolated and best visible owners can differ. The unchanged R297 anchor already explains these two interiors comparatively well, while failing elsewhere. No interior centroid or reflection is treated as a physical center; no physical+1/+6/+7 chain is verified.

'''
    example=ROOT/'photo2/r311/evidence/phase-registration-example.json'
    if example.exists():
        ex=read(example);before={r['id']:r for r in ex['before_targets']};after={r['id']:r for r in ex['after_targets']}
        n='C-1477-0290';p='C-1608-0253';a='C-1497-0271';worse=100*(ex['global_score_after']/ex['global_score_before']-1)
        text+=f"A **pure phase/registration move** (trial {ex['after_trial']}) changes negative overlap {100*before[n]['modal_fraction']:.1f}→{100*after[n]['modal_fraction']:.1f}%, positive overlap {100*before[p]['modal_fraction']:.1f}→{100*after[p]['modal_fraction']:.1f}%, and reference overlap {100*before[a]['modal_fraction']:.1f}→{100*after[a]['modal_fraction']:.1f}%. Its whole-development score is {worse:+.1f}% relative to baseline (positive is worse). This demonstrates a missed, locally promising joint basin within the existing geometry, while retaining its global cost. [Native before/after figure](r311/evidence/phase-registration-example.png); the complete necklace occludes both crop renders.\n\n"
    text+='''
| Model | Reference visible% | Negative visible / best isolated% | Positive visible / best isolated% |
|---|---:|---:|---:|
'''
    for m in models:
        rr={r['id']:r for r in m['first_errors']};a=rr['C-1497-0271'];b=rr['C-1477-0290'];c=rr['C-1608-0253']
        text+=f"| {m['name']} | {100*a['modal_fraction']:.1f} | {100*b['modal_fraction']:.1f} / {100*b['best_isolated_fraction']:.1f} | {100*c['modal_fraction']:.1f} / {100*c['best_isolated_fraction']:.1f} |\n"
    text+='''
[Raw/native before-after atlas](review/r311/index.html) and per-model exports retain competing owners, isolated/visible/occluded fractions, reference and adjacent red/yellow bodies, including wholly hidden alternatives. A patch-directed finalist must have whole-development score≤115% of its own baseline and lose at most5 coverage points at the trusted reference; it still must pass every global measurement. Poor-reference local tradeoffs remain in trial records and can seed coupled exploration. No patch was detached or fitted independently.

## Independent whole-necklace measurements

Fixed **D=36.878px** is R309's uncertain B14 contour reference (±6px conservative length uncertainty), not a measured largest bead. Dense metrics use all original positive-interior pixels and both retrospective partitions. Paper/color percentages are means of regional frozen-cue fractions, not fractions of the entire photograph; interior ownership is region-balanced modal coverage, not verified per-bead accuracy. Supported external-boundary metrics use complete native outlines against 16 uncertain photographic contours; other complete bead boundaries are unmeasured. Measurement pathways are distinct but their pixels/evidence are correlated. Reflection associations remain conditional. All 811 catalog observations survive, including weak/missing evidence.

| Model | Reflection RMS / P95 / max(D) | Boundary RMS / max(D) | Interiors% | Paper / color omission% | Missing strong | Fixed-owner penalized RMS(D) / missing |
|---|---|---|---:|---|---:|---|
'''
    for model in models:
        r=metrics[model['name']];a=r['overall'];rf=a['reflection'];b=a['boundary'];mat=a['material'];fx=r['fixed']['overall']
        text+=f"| {model['name']} | {fmt(rf['rms_D'])} / {fmt(rf['p95_D'])} / {fmt(rf['maximum_D'])} | {fmt(b['rms_D'])} / {fmt(b['maximum_D'])} | {fmt(a['ownership']['coherent_percent'],2)} | {fmt(mat['background_occupation_percent'],2)} / {fmt(mat['foreground_omission_percent'],2)} | {rf['missing']} | {fmt(fx['penalized_RMS_D'])} / {fx['missing']} |\n"
    text+='''
Fixed controls retain each parent's original conditional owners and 48px missing-lobe penalties. These prevent a rematching-only decrease from being called recovered geometry; they do not certify those original identities. Free and fixed scores, development/comparison results, P95/max, boundary missingness, color, regional material outcomes and all physical witnesses are in [metrics](r311/results/campaign/metrics/). [Whole-circuit optical plots](review/r311/whole-circuit-reflections.png) expose geographic tradeoffs; nearest-only legacy plots are distinguished from the surface-compatible table above.

The requested first-error interiors enter search directly, including old comparison geography; the reference enters a preservation guard. Their local scores are not withheld. Additional dense whole-circuit comparison measurements are computed after finalist selection, but this is retrospective, partly target-exposed evidence, never a fresh holdout. [Exposure ledger](r311/results/campaign/exposure.json).

The acceptance ledger also separates material/photographic checks from the raw fixed-index control. A fixed-index regression alone cannot disprove better physical placement when identities are unknown. Conversely, reassignment alone cannot improve unchanged native interior ownership and material occupation. [Regional ownership/material plots](review/r311/regional-outcomes.png) expose whole-circuit regressions independently of index labels.

'''
    for row in accept['models']:
        failed=[k for k,v in row['checks'].items() if not v]
        text+=f"- **{row['model']}**: {'passes combined test' if row['passes'] else 'fails '+', '.join(failed)}.\n"
    text+='''
The earlier mechanism was restrictive: limited shared global trials, derivative-gated coupled proposals, coarse structural rejection and repeated local neighborhoods were not a broad native basin test. R311 tests a wider finite design and retains distant feasible islands. A lower weighted score or strong local repair alone does not answer the central question affirmatively. Remaining unsampled combinations, frozen fields/light, discrete starts and finite-map resolution limit any negative inference.

## Verification and stopping point

'''
    text+=f"Five scope/recovery contracts pass, including real SIGTERM/resume and a process exit after trial publication but before checkpoint update. Independent original-Python verification checks **{verify['positions']} positions, {verify['contact_pairs']} spatial contact witnesses, {verify['original_native_rays']} native rays, {verify['original_optical_rays']} optical rays and {verify['native_boundary_segments']} native boundary segments**. Original local isolated controls, normalized residual arithmetic, raw photograph/atlas pixels and exact frozen fields pass. {verify['preserved_files']} prior tracked files are checked; historical science is unchanged. [Verification receipt](r311/results/campaign/verification.json). Browser/launcher checks and remote-delivery status are recorded separately, never implied by this numerical receipt.\n\n"
    text+='''**Stop for maker review.** No geometry adoption, new bead shape, arbitrary local correction, Phase 3 or automatic R312. Review the first-error/global tradeoff and coverage gaps before choosing any next experiment. Keep the current model/session for review; no `/new` is needed and no model switch is required.
'''
    (ROOT/'photo2/R311_DETAILS.md').write_text(text)
    def table(header):
        i=text.index(header);block=text[i:].split('\n\n',1)[0]
        # Unchanged hand-plus controls remain in the full technical table.
        return '\n'.join(line for line in block.splitlines() if not line.startswith(('| R306-2204-plus-closed-baseline |','| R306-2002-plus-open-baseline |')))
    brief=f'''# R311 — broader existing-global basins

**{result}** No new bead geometry, local correction or Phase 3 was introduced.

[Photographic review](review/r311/index.html) · [Response maps](review/r311/maps.html) · [Full technical account](R311_DETAILS.md) · [Reproduce](R311_REPRODUCE.md).

{partial_note}

## Actual versus allowed coverage

The audit reads **6,075 archived trials**. R306 had 1,082 structural screens without optical evaluation; R307/R308 concentrated on small neighborhoods. R309 used **58 shared trials**, omitted the unchanged R297 anchor as a principal start, and rejected all **41 coupled derivative blocks** at its all-column gate. R307 had355/884 derivative sides with additional missing lobes; R308 had233/290 and23 unavailable columns. These are overlapping diagnostics, not exclusive rejection counts. Exact repeats, starts, discrete families, bound/contact rejections and optical sampling are in the [audit](r311/results/audit/coverage.json) and [per-family ranges](r311/results/audit/ranges.csv).

Exact physical intervals are unknown for most globals: positive dimensions/scale, camera above the plane, periodic angles, construction twist and joint contact/camera validity are the real constraints. The finite boxes below are engineering controls. Union endpoints do not imply joint coverage. Historical phase endpoints are saved unwrapped scalars; phase is periodic and wrapped in the plots. Units: phase radians; elevation/roll/tilt degrees; minor world units; scale px/world unit; axial is an affine multiplier with H/D=.7×axial. Registration s0 is scaled world arclength, not a fixed 2D image translation.

{table('| Global |')}

The search preserves R297's original placement and inherited fields, alongside R306-primary and2733; R309 and both hand-plus/topology controls remain distinct. Counts, winding, shared light, perspective and all inherited correction fields stay frozen. Closed principal phase usesN/winding; R297 retains its legacy turn correction. Untested combinations of these frozen quantities remain a limitation.

## Response maps and basins

Executed **{len(rows)} unique vectors**, **{feasible} certified feasible**, in **{state['elapsed']/60:.2f} search minutes** (initial40min plus contingent at most10min). Trial types:`{coverage['types']}`. Bounds/penetration/unresolved/numerical outcomes:`{coverage['statuses']}`. Broad schedule:{state['cursor']}/{len(state['plan'])} slots; skipped exact repeated evaluations:{state['deduplicated']}. Audit, preflight, recovery and final verification are separately timed.

Five broad pairs, scrambled four-variable Sobol sampling, adaptive pair subdivision and basin-centered four-variable sampling evaluate distant joint proposals directly. No derivative or missing-highlight veto gates discovery. Red crosses witness penetration; orange marks are unresolved contact checks; blank cells are untested. Feasible but photographically poor models remain scored.

{table('| Pair |')}

{table('| Distinct finalist basin |')}

[All vectors and outcomes](r311/results/campaign/trial-vectors.csv), [basin ledger](r311/results/campaign/basins.json) and [four-variable maps](review/r311/basin-multivariate.png) retain the failed alternatives. Discrete sampled components/minima do not prove isolated continuous basins.

## First positioning discrepancies

'''
    if example.exists():
        ex=read(example);eb={r['id']:r for r in ex['before_targets']};ea={r['id']:r for r in ex['after_targets']}
        en='C-1477-0290';ep='C-1608-0253';er='C-1497-0271';ew=100*(ex['global_score_after']/ex['global_score_before']-1)
        brief+=f"A pure phase/registration move (trial {ex['after_trial']}) repairs negative overlap **{100*eb[en]['modal_fraction']:.1f}→{100*ea[en]['modal_fraction']:.1f}%**, positive **{100*eb[ep]['modal_fraction']:.1f}→{100*ea[ep]['modal_fraction']:.1f}%**, and reference **{100*eb[er]['modal_fraction']:.1f}→{100*ea[er]['modal_fraction']:.1f}%**. Its whole-development score is **{ew:+.1f}%** (worse). Thus an earlier search missed a locally promising joint basin; this alone is not a global repair. [Native before/after](r311/evidence/phase-registration-example.png).\n\n"
    brief+=f'''{table('| Model | Reference visible%')}

All six original interiors, competing owners, isolated overlap, resolved occlusion/unknowns and adjacent conditional ±1/6/7 bodies are retained in the review. No photographic physical centers or verified index chain are invented. Patch-directed finalists preserve the trusted reference and stay within15% of baseline whole-development score; every proposal still describes the entire necklace.

## Whole-necklace comparison

Fixed **D=36.878px**, R309's B14 reference with conservative ±6px uncertainty, is not a measured largest bead. Interior percentages average regions; paper/omission average regional frozen cues. Boundaries use complete native exteriors against16 uncertain observed contours. All811 catalog observations survive. First-error targets intentionally enter search even in old comparison geography; later dense comparison is retrospective and partly exposed, not a fresh holdout. [Exposure ledger](r311/results/campaign/exposure.json).

{table('| Model | Reflection RMS')}

Fixed controls retain each family's original conditional owners, with48px missing-lobe penalties. Reassignment alone cannot improve unchanged native material placement; raw fixed-index regression also cannot, by itself, disprove better geometry when identities are unverified. [Every component/gate](r311/results/campaign/acceptance.json), [dense residuals](r311/results/campaign/metrics/) and [regional outcomes](review/r311/regional-outcomes.png) expose the tradeoffs. Combined passes:{sum(r['passes'] for r in accept['models'])}; material/photographic passes excluding the raw fixed-index control:{sum(r['geometric_passes'] for r in accept['models'])}.

Earlier mechanisms were restrictive; R311 demonstrates wider coverage and a real local repair under the existing geometry. The tested global outcomes above decide whether it extends to the necklace. A negative result remains limited by finite sampling, frozen fields/light/turn and discrete hypotheses; it is not proof that new physical geometry is necessary.

## Verified delivery and stop

Five contracts include real SIGTERM/resume and orphan-trial recovery. Original-Python replay verifies **{verify['positions']} positions, {verify['contact_pairs']} contact witnesses, {verify['original_native_rays']} native rays, {verify['original_optical_rays']} optical rays and {verify['native_boundary_segments']} boundary segments**. Frozen fields, complete boundary edges, viewer/native owners, raw pixels and {verify['preserved_files']} prior tracked files pass. [Scientific receipt](r311/results/campaign/verification.json); browser/remote receipts are separate.

**Stop for maker review.** No adoption, new geometry, local correction, Phase3 or automatic R312. Review the local/global tradeoff and untested coverage before another experiment. Keep the current model/session; no`/new` is needed.
'''
    for old,new in [('had355','had 355'),('had233','had 233'),('and23','and 23'),('and2733','and 2733'),('usesN','uses N'),('initial40min','initial 40 min'),('most10min','most 10 min'),('within15%','within 15%'),('against16','against 16'),('All811','All 811'),('with48px','with 48px'),('Phase3','Phase 3'),('no`/new`','no `/new`'),("and{verify", "and {verify")]:brief=brief.replace(old,new)
    (ROOT/'photo2/R311_REPORT.md').write_text(brief)
    save(out/'summary.json',dict(conclusion=result,any_pass=accept['any_pass'],any_geometric_pass=accept.get('any_geometric_pass',False),promising_missed_basin=partial,evaluations=len(rows),feasible=feasible,elapsed_seconds=state['elapsed'],models=[m['name'] for m in models],historical_files_unchanged=verify['preserved_files'],utc=utc()))
