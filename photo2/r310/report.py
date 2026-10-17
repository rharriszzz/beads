"""Machine-readable findings and concise scientific report from unchanged results."""
import csv
import numpy as np
from photo2.r297.common import ROOT,read,save
from .analysis import OUT,D,MODELS,ANCHOR,stats

def main():
    datasets=[read(OUT/f'{name}-partA.json.gz') for name in MODELS];controls=read(OUT/'partA-controls.json.gz');curve=read(OUT/'curvature.json.gz');table=[];individual=[];firsts=[];recoveries=[]
    for d in datasets:
        for sign,f in d['findings'].items():
            r=f['first_demonstrated_material_inconsistency'];near=[x for x in d['supports'] if 0<float(sign)*x['distance_px'] and abs(x['distance_px'])>abs(r['distance_px']) and x['core_coherence']>=.9];recovery=min(near,key=lambda x:abs(x['distance_px'])) if near else None
            optical=[x for x in d['reflections'] if x['strong'] and x['error_px'] is not None and 0<float(sign)*x['distance_px'] and abs(x['distance_px'])>abs(r['distance_px']) and x['error_px']/D<.1];optical=min(optical,key=lambda x:abs(x['distance_px'])) if optical else None
            recoveries.append(dict(model=d['model'],direction=int(sign),first_high_coverage_after_mismatch={k:recovery[k] for k in ['id','distance_px','index','coherence','core_coherence']} if recovery else None,first_small_strong_reflection_after_mismatch=optical,policy='Apparent material/optical recovery, never proof of restored physical indexing.'))
            st=r['core_outside_owner'];table.append(f"| {d['model']} | {'−' if sign=='-1' else '+'} | {r['id']} | ({r['point'][0]:.1f},{r['point'][1]:.1f}) | {r['distance_px']:+.1f} / {r['distance_D']:+.3f} | {r['index']} / {r['index_from_reference']:+d} | {100*r['coherence']:.1f}% | {st['rms_D']:.3f} / {st['p95_D']:.3f} / {st['maximum_D']:.3f} |")
            firsts.append(dict(model=d['model'],direction=int(sign),observation=r['id'],point=r['point'],index=r['index'],relative_index=r['index_from_reference'],photographic_distance_px=r['distance_px'],photographic_distance_D=r['distance_D'],core_distances=st,physical_position_failure=None))
        for r in sorted([x for x in d['supports'] if abs(x['distance_px'])<180],key=lambda x:x['distance_px']):
            q=r['reflection_record'];individual.append(dict(model=d['model'],id=r['id'],photo_x=r['point'][0],photo_y=r['point'][1],photo_distance_D=r['distance_D'],index=r['index'],relative_index=r['index_from_reference'],coherent_percent=r['coherence']*100,core_percent=r['core_coherence']*100,core_rms_D=r['core_outside_owner']['rms_D'],core_P95_D=r['core_outside_owner']['p95_D'],core_max_D=r['core_outside_owner']['maximum_D'],reflection_D=q['error_px']/D if q and q['error_px'] is not None else None,reflection_strong=q['strong'] if q else None))
    save(OUT/'recoveries.json',recoveries)
    nv=read(OUT/'neighbor-vectors.json.gz')['rows'];save(OUT/'neighbor-summary.json',[dict(model=name,visible_centroid_vector_discrepancy=stats([r['visible_proxy_error_px'] for r in nv if r['model']==name]),uncertain_correspondences=sum(r['model']==name for r in nv),physical_center_vector_error=None,policy='Dependent image-centroid pair proxies, not measured physical-center vectors; full individual records in neighbor-vectors.json.gz') for name in MODELS])
    with (OUT/'individual-discrepancies.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(individual[0]),lineterminator='\n');w.writeheader();w.writerows(individual)
    prefixes=[]
    for d in datasets:
        for p in d['prefixes']:
            prefixes.append(dict(model=d['model'],direction=p['direction'],beads_outward=p['length'],strong_reflections=p['reflections']['n'],missing=p['reflections']['missing'],uncertain_owners=p['uncertain_reflection_owners'],rms_D=p['reflections']['rms_D'],p95_D=p['reflections']['p95_D'],maximum_D=p['reflections']['maximum_D'],support_regions=p['supports'],mean_coherence=p['mean_coherence'],unsupported_bodies=p['unsupported_bodies']))
    with (OUT/'prefixes.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(prefixes[0]),lineterminator='\n');w.writeheader();w.writerows(prefixes)
    # Weak/unmatched observations remain in raw records; geographic prefix counts supplement owner-conditioned counts.
    geographic=[]
    for d in datasets:
        for sign in [-1,1]:
            for length in [40,80,160,320,640,1280]:
                q=[r for r in d['reflections'] if 0<=sign*r['distance_px']<=length];strong=[r for r in q if r['strong']];geographic.append(dict(model=d['model'],direction=sign,photo_length_px=length,all_catalog=stats([r['error_px'] for r in q]),strong=stats([r['error_px'] for r in strong]),uncertain_correspondences=len(q),unmatched_ids=[r.get('observation',r.get('id')) for r in q if r['index'] is None]))
    save(OUT/'geographic-prefixes.json',geographic)
    expected=[]
    for d in datasets:
        a=d['anchor'];expected.append(dict(model=d['model'],index=a['index'],coverage=a['coherence'],alternatives=a['alternatives'],observed_interior_centroid=a['point'],observed_reflection=a['observed_reflection'],modeled_center=a['modeled_center']))
    summary=dict(schema=310,diagnostic_only=True,fit_evaluations=0,D_px=D,D_uncertainty_px=6,reference=expected,first_material_inconsistencies=firsts,first_verified_physical_positioning_failures=None,leading_hypotheses=['Incorrect global phase/advance/camera produces incorrect body poses and relative depths, sometimes through occlusion.','Incorrect body orientation/shape or incomplete/merged photographic supports; unknown physical identities confound separation.'],curvature=curve['summary'],implementation_verification=curve['verification'],smallest_next_experiment='Image-only joint assessment of reference C-1497-0271, C-1477-0290 and R282-1459-0316: establish separate visible rims and over/under relations using existing pixels and conservative boundary bands; test unchanged families with fixed owner alternatives. A reliable hole/rim orientation or verified crochet-neighbor link would distinguish phase/pose from shape ambiguity. If unresolved in this photograph, leave the physical sequence unknown; do not infer a curvature correction from the present correlation.',links=dict(report='../../R310_REPORT.md',viewer='../../review/r310/index.html',partA='partA.json.gz',controls='partA-controls.json.gz',curvature='curvature.json.gz',neighbors='neighbor-vectors.json.gz',prefixes='prefixes.csv',geographic_prefixes='geographic-prefixes.json',individual='individual-discrepancies.csv',recoveries='recoveries.json',verification='verification.json'))
    save(OUT/'summary.json',summary)
    r306,r309=datasets[:2];anchor_table='\n'.join(f"| {d['model']} | {d['anchor']['index']} | {100*d['anchor']['coherence']:.1f}% | {100*d['anchor']['core_coherence']:.1f}% | ({d['anchor']['modeled_center'][0]:.2f},{d['anchor']['modeled_center'][1]:.2f}) |" for d in datasets)
    curvature_table='\n'.join(f"| {r['model']} | {r['minimum_radius_over_width']:.2f} | {r['minimum_pure_bend_tangent_factor']:.3f} | {r['spearman_curvature_vs_ownership_error']:+.3f} |" for r in curve['summary'])
    text=f'''# R310 — the first inconsistency is near the reference, before a verified sequence exists

**Part A: no unique first physical bead-positioning failure can be established.** The reference photograph is known, but no verified chain of physical +1/+6/+7 identities or bead-center coordinates extends from it. The saved models already disagree with nearby positive interiors. R306's negative-direction failure is visible just **19.8px (0.536D)** from the reference: C-1477-0290 is split among several modeled bodies. R309 explains that interior better but fails on different nearby bodies. No geometry was changed, and no fitting or parameter search was performed.

[Interactive viewer](review/r310/index.html) · [JSON summary](r310/results/summary.json) · [Individual discrepancies](r310/results/individual-discrepancies.csv) · [Reproduce](R310_REPRODUCE.md).

## 1. What reference correspondence is established?

The maker's reference is the photographed red crossing **C-1497-0271**. Its393 saved positive-interior pixels have centroid **(1499.3613,271.2036)**. The separate catalog reflection is **(1496.9262,271.0149)**, marked **weak/ambiguous**, with 3px uncertainty. R294's independent H-1497-0270 bright-patch representative is (1496.95,271.15), threshold sensitivity 0.30px. These are three photographic measurements, not physical bead centers. R294 explicitly reported no human-accepted complete region in this starting window; the current maker reference does not retrospectively certify an exact contour or crochet sequence.

| Unchanged complete model | Conditional owner | Interior coverage | 2px-eroded core coverage | Projected physical center |
|---|---:|---:|---:|---|
{anchor_table}

The dominant **0 / 2 / 0** assignments are well supported as model-to-photo overlaps, but remain conditional physical identities. R306 alternatives −3/−1 and R309 3/−2 remain in the ledger. A selected index0 in another historical model is not automatically this red bead. R297 is included because its starting evidence is substantially better; R294's bounded221-body local model is historical evidence, not substituted for a complete necklace.

## 2. Where does the first failure occur in each direction?

Prefixes 0…±10/20/40/80/160/320 are inspected from each model's own conditional reference, retaining hidden and unsupported bodies. The ordered atlas follows the **same photographic locations** across models. Geographic ordering also prevents rematched indices from changing what counts as the first observed discrepancy.

A **suspected disagreement** has less than 80% of an observed positive region owned by one visible body. A conservative **major material inconsistency** requires: fewer than 65% of a2px-eroded core on any one owner; at least 20% of that core farther than **0.15D=5.53px** from the modal owner's complete visible surface; and at least 40 core pixels. This tests supported material placement, not physical center displacement. All regions retain possible same-color-merger uncertainty. Unknown rays are excluded, not background. Distances below include zero for supported core pixels already on the body; correlated pixels are not independent observations.

| Model | Direction | First major material inconsistency | Photo position | Reference arc px / D | Index / relative index | Whole interior ownership | Core distance RMS / P95 / max, all /D |
|---|---|---|---|---|---|---:|---|
{chr(10).join(table)}

Earlier positive-direction fragmentation begins at **R282-1536-0239,+37.3px**, and the next lower red **R282-1537-0308,+40.8px**. Do not interpret the stricter R306+172.9px threshold as successful positioning of every preceding bead. Negative R306's first large discrepancy is corroborated by the next measured red at −42.3px. Positive R309's+108.6px discrepancy is followed by failures near +136/+154px. R309's negative−133px case is isolated under this stringent rule; nearby partial failures do not justify calling it a sustained verified sequence error.

**Threshold uncertainty is material:** changing the distance threshold 0.10→0.20D moves R306's negative first event from −19.8 to −42.3px, and its positive event from +40.8 to +172.9px. R309's positive event remains +108.6px; its negative event ranges from −42.3px to no qualifying event within 230px. Erosion 0/1/2/3px controls are saved. These are diagnostic engineering thresholds, not calibrated confidence intervals.

The last preceding **verified physical correspondence is unknown** in every direction. The last high-coverage candidate is the reference for R306− and both R309 directions; R306+ has E5-1607-0290 at+113.5px with 100% eroded-core coverage, and R297− has C-1477-0290 with 97.9%. High coverage does not prove identity. Later material/optical recoveries are explicitly marked and saved; they do not establish recovered indexing.

All displacements use **D=36.878px**, the fixed R309 B14 reference, ±6px conservative dimensional uncertainty, not a proven largest photographed bead. Full records retain pixels, RMS/D, P95/D, maximum/D, counts, missing observations, weak reflections and competing owners. Physical center displacement is **unmeasured**, not zero. Prefix reflection cohorts are conditional-owner selections; separate geographic cohorts retain unmatched observations.

## 3. What is the strongest evidence for the cause?

**Relabeling alone fails.** The maximal-overlap one-to-one assignment on the unchanged ±210px neighborhood equals the per-region modal assignments in all three models. No alternative owner improves the dominant visible coverage, even though several isolated projections may overlap. This is a diagnostic association control, not a geometry fit.

At R306 C-1477-0290, the best visible owner −7 covers only 31.7%; even the best isolated candidate −9 covers 46.5%. The adjacent lower red has at most 50.6% isolated coverage. Neighbor masking alone cannot explain this pair: incorrect body pose/shape/projection or an invalid single-bead support interpretation is required. Its large reflection error is not used as proof of center displacement.

At R309 C-1608-0253, candidate 30's **isolated surface covers100%**, but only 29.7% survives neighboring occlusion. Modal visible owner 35 covers 35.7%, with owners 30/29 sharing most remaining material. A change of label cannot make bead 30 visible. This is strong evidence of a **relative-pose/depth/phase/occlusion problem** if the independent red support is one body. Nearby red/yellow fragmentation corroborates the visible-body failure. It does not uniquely distinguish global phase from camera or bead orientation.

The leading hypotheses are (a) an incorrect global phase/advance/camera combination yielding wrong body poses and depths, and (b) incorrect bead orientation/shape or incomplete single-body evidence. A trustworthy rim/hole axis and over/under relation across the reference and its two negative-side red neighbors would distinguish them. Reflection position alone would not. No light-only explanation can repair the measured material splits.

## 4. Why do 2405 and 2733 disagree?

They are different full physical hypotheses, not a simple relabeling: both have hand−, but R306 is open and R309 closed; cameras are 60.41°/53.32° elevation and 31.18°/24.29° roll; scale 8.718/8.423, axial parameter 0.845/0.873, and global phase/registration also differ. R309's actual closed turn count gives 2733/420=6.50714 beads per turn; its saved `turn` scalar is not used for closed phase transport. True total geometric arclength and count jointly determine mean advance.

At the reference, subtracting origins 0/2 aligns conditional labels. By C-1608-0253 the modal relative indices are +27/+33, a whole-turn-sized difference; at C-1559-0252 they are +14/+20. This is **conditional periodic aliasing plus different spacing/projection**, not demonstrated extra physical beads between those observations. The model-to-model axis displacement has RMS/P95/maximum 0.129/0.260/0.294D across 2049 common photographic stations, and maximum tangent difference 1.21°. These are model differences, not photographic error; the original photographic axis is itself an uncertain reference. These displacements do not identify which axis is correct or isolate the coupled camera/phase effects. Observed interior-centroid vectors and predicted visible-centroid/physical-center vectors are shown side by side; there are **zero independently verified physical-center +1/+6/+7 vectors** in the reused evidence. There are 34 existing near-anchor separator-pair records per model in the neighbor ledger. They support distinct material to varying degrees, not integer crochet identity. The reference-to-C-1477 interior-centroid vector is 0.748D long; its discrepancy against the modeled visible-centroid vector is 0.211D (R306),0.151D (R309),0.206D (R297). These are visible-centroid proxy discrepancies, not physical center errors.

## 5. Does curvature contribute?

Part A was completed and recorded before the curvature analysis. The existing R306/R309 implementation **does transport the helix through bends correctly**. For axis arclength s, radial offset rho and phase phi,

`dC/ds = (1 − rho*kappa*sin(phi))*T + rho*phi_s*circum + rho_s*radial`.

The first term compresses inner-bend longitudinal spacing and expands the outside; the second preserves continuous helical phase. The third includes R309's existing height-dependent minor radius. Finite differences of every saved body agree within **1.7e−6** in derivative norm. Frames remain orthonormal and right-handed to 1e−15, and saved centers reproduce exactly. Nine analytic circle cases independently verify inside/outside behavior as turning radius decreases. No frame flip, phase reset, or missing pure-bending factor was found. +1/+6/+7 directions and separations, transformed annular orientations, full-scene occlusion and historical contact certificates already include bending. The body axis is the transported centerline tangent with the saved circumferential tilt, plus R309’s existing height-dependent tilt; it is not forced to equal the helical center-trajectory tangent. That is a physical orientation assumption, not a numerical frame-transport defect. Prescribed phase/spacing fields do **not** solve mechanical crochet relaxation.

| Model | Tightest axis radius / rope width | Minimum inner tangent factor | Curvature vs ownership-error Spearman |
|---|---:|---:|---:|
{curvature_table}

R306's first negative mismatch has turning radius **8.67 rope widths**, near the 56th curvature percentile; R309's negative event has **11.24 widths**, near 42nd percentile. R309's positive event is tighter (**3.90 widths**,88th percentile), but this association does not generalize consistently: errors occur at mild bends, and tighter regions can have better ownership. Camera foreshortening and inside/outside phase confound a simple curvature plot. These diagnostics do not justify a curvature-dependent correction yet.

## 6. Smallest justified next experiment

Perform a **fixed-model, image-only three-body correspondence and rim/occlusion assessment** of C-1497-0271, C-1477-0290 and R282-1459-0316, using their existing native pixels and conservative uncertainty bands. Establish which boundaries separate individual bodies and, if possible, one reliable crochet-neighbor or hole-axis relation. Then compare the already saved families with those owners fixed. If the image cannot resolve it, keep the physical sequence unknown. A curvature coefficient or longer search is not supported by the present first-failure evidence.

A possible future globally consistent law is `delta_phi(s)=a*rho*kappa(s)` or `tilt(s)=tilt0+b*rho*kappa(s)`, with periodic smoothing and physically bounded derivatives. These are **descriptions only**, neither implemented nor optimized in R310.

## Verification and scope

The standalone CPU workflow reuses saved native rasters and whole models, computes all prefixes and alternatives automatically, then runs original-Python ray and isolated-body checks, saved-center/parameter replay, native boundary replay, arithmetic checks and raw-photo atlas checks. An initial shallow-copy/bound-method defect in the R297 isolated diagnostic was caught, documented and repaired before Part B; historical outputs were untouched. Independent original-Python replay passed 55,457 full-scene rays, the near-anchor isolated controls, all 7,475 saved centers/parameters and 105,730 native boundary segments across 1,923 inspected addresses. All 28 atlas raw panels are exact crops. Chromium passed 30 model/location checks, model switching, index steps, recentering, raw-layer invariance, all images/links, narrow and offline review. Preservation receipts accompany the final delivery. No fitted parameters, Phase1 observations, prior reports, beads.pov, Phase3 or color patterns were changed. **Stop for maker and independent AI review.**
'''
    (ROOT/'photo2/R310_REPORT.md').write_text(text)
if __name__=='__main__':main()
