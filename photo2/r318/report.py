"""Compact raw-photograph vectors, exact error tables and scientific report."""
import csv,html
from collections import Counter
from pathlib import Path
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from photo2.r297.common import ROOT,read,save,utc
from .detect import OUT
from .optics import Chain
from photo2.r306.evidence import load

def main():
    raw=np.array(Image.open(ROOT/'beads-photo-2.jpg'));doc=read(OUT/'observations.json.gz');summaries=[]
    for folder in [OUT,OUT/'epoch2']:
        if not (folder/'best.json.gz').exists():continue
        epoch=read(folder/'epoch.json');before=read(folder/'baseline.json.gz');best=read(folder/'best.json.gz');obs=epoch['observations'];D=epoch['diameter']['photo_median_px'];Dc=epoch['diameter']['fixed_conservative_reference_px']
        scene=Chain(best['parameters'],load()[0]);angles=np.linspace(0,np.pi,181);directions=np.cos(angles)[:,None]*scene.right+np.sin(angles)[:,None]*scene.down
        byid={o['id']:o for o in obs};rows=[]
        for r in best['rows']:
            o=byid[r['id']];q=dict(r);q.pop('predicted_lobe',None);q.update(error_photo_diameter=r['error_px']/D,error_baseline_model_diameter=r['error_px']/o['baseline_model_diameter_px'],error_conservative_diameter=r['error_px']/Dc,
                    localization_confidence='threshold-stable; provisional specular classification',localization_uncertainty_px=o['uncertainty_px'],photo_apparent_diameter_px=o['photo_apparent_diameter_px'],baseline_model_diameter_px=o['baseline_model_diameter_px'],
                    component_area_px=o['component']['area'],saturated_rgb_pixels=o['saturated_rgb_pixels'],observed_peak_ties=o['component']['ties'],geometry_alternatives=o['geometry_alternatives'])
            j=int(np.flatnonzero(scene.indices==r['index'])[0]);diam=float(2*scene.scale*scene.support(directions,np.tile(scene.g['surface_tangent'][j],(len(directions),1))).max())
            q.update(final_model_diameter_px=diam,error_final_model_diameter=r['error_px']/diam)
            rows.append(q)
        save(folder/'bead-ledger.json',rows)
        with (folder/'bead-ledger.csv').open('w',newline='') as f:
            fields=['id','index','observed_x','observed_y','predicted_x','predicted_y','error_px','error_photo_diameter','error_baseline_model_diameter','localization_uncertainty_px','correspondence_confidence','localization_confidence','color'];w=csv.DictWriter(f,fields,lineterminator='\n');w.writeheader()
            for r in rows:w.writerow({k:r[k] for k in fields if k in r}|dict(observed_x=r['observed'][0],observed_y=r['observed'][1],predicted_x=r['predicted'][0],predicted_y=r['predicted'][1]))
        xy=np.array([o['point'] for o in obs]);lo=np.floor(xy.min(0)-30).astype(int);hi=np.ceil(xy.max(0)+30).astype(int);crop=raw[lo[1]:hi[1],lo[0]:hi[0]]
        Image.fromarray(crop).save(folder/'raw-patch.png')
        fig,ax=plt.subplots(1,2,figsize=(14,6),layout='constrained')
        for a,r,title in zip(ax,[before,best],['Before','After']):
            a.imshow(crop,extent=[lo[0]-.5,hi[0]-.5,hi[1]-.5,lo[1]-.5],interpolation='nearest');worst=max(r['rows'],key=lambda z:z['error_px'])['id']
            for z in r['rows']:
                x,y=z['observed'];u,v=z['predicted'];color='#ff5c44' if z['id']==worst else '#00ffff'
                a.plot(x,y,'o',ms=3,mfc='white',mec='black',mew=.5);a.annotate('',xy=(u,v),xytext=(x,y),arrowprops=dict(arrowstyle='->',color=color,lw=1.4));a.text(x+2,y-3,str(z['index']),fontsize=7,color='white',bbox=dict(facecolor='black',alpha=.5,pad=.3,edgecolor='none'))
            a.set_title(f"{title}: Emax {r['emax_px']:.2f}px, {r['emax_px']/D:.3f} D_photo");a.set_axis_off()
        fig.suptitle(f"{epoch['id']} — white: observed; arrow tip: predicted; red: worst. Conditional indices.")
        fig.savefig(folder/'vectors.png',dpi=150);plt.close(fig)
        indexes=np.array([r['index'] for r in rows]);errors=np.array([r['error_px'] for r in rows]);b={r['id']:r['error_px'] for r in before['rows']};berr=np.array([b[r['id']] for r in rows]);order=np.argsort(indexes)
        center=float(np.median(indexes));outward=np.argsort(abs(indexes-center),kind='stable')
        fig,ax=plt.subplots(1,2,figsize=(12,3.5),layout='constrained')
        ax[0].plot(indexes[order],berr[order],'o--',label='Before');ax[0].plot(indexes[order],errors[order],'o-',label='After');ax[0].set_xlabel('Conditional bead index');ax[0].set_ylabel('Reflection displacement (px)');ax[0].legend()
        ax[1].step(abs(indexes-center)[outward],np.maximum.accumulate(errors[outward]),where='post');ax[1].scatter(abs(indexes-center)[outward],np.maximum.accumulate(errors[outward]),s=12);ax[1].set_xlabel(f'Address distance from patch median {center:g}');ax[1].set_ylabel('Cumulative maximum (px)')
        for a in ax:a.axhline(.5*D,color='red',ls=':',label='0.5 D_photo');a.axhline(.2*Dc,color='green',ls=':',label='0.2 conservative D');a.grid(alpha=.2)
        ax[0].legend(fontsize=8)
        fig.savefig(folder/'errors.png',dpi=150);plt.close(fig)
        worst=max(rows,key=lambda z:z['error_px']);half=read(folder/'half-pixel.json') if (folder/'half-pixel.json').exists() else None
        summary=dict(epoch=epoch['id'],directory=str(folder.relative_to(OUT)) or '.',observations=len(rows),before_emax=before['emax_px'],after_emax=best['emax_px'],before_rms=before['rms_px'],after_rms=best['rms_px'],median=best['median_px'],missing=best['missing'],worst=worst,
                     photo_D=D,conservative_D=Dc,model_D=epoch['diameter']['baseline_model_median_px'],worst_photo_fraction=best['emax_px']/D,max_individual_baseline_model_fraction=max(r['error_baseline_model_diameter'] for r in rows),
                     final_model_median_D=float(np.median([r['final_model_diameter_px'] for r in rows])),max_final_model_fraction=max(r['error_final_model_diameter'] for r in rows),
                     provisional_correspondences=len(rows),low_initial_confidence=sum(o['correspondence_confidence']=='provisional-low' for o in obs),
                     localization_max_uncertainty=max(o['uncertainty_px'] for o in obs),half_pixel=half,parameters=best['parameters'],trial=best.get('trial'),
                     localization_uncertainty_above_2px=sum(o['uncertainty_px']>2 for o in obs),tied_observed_peaks=sum(len(o['component']['ties'])>1 for o in obs),
                     excellent=bool(best['emax_px']+max(o['uncertainty_px'] for o in obs)<.2*Dc),expanded=False)
        summaries.append(summary)
        inventory=[]
        for idx in range(*[epoch['scope'][0],epoch['scope'][1]+1]):
            selected=[r['id'] for r in rows if r['index']==idx]
            inventory.append(dict(index=idx,observations=selected,status='included provisional correspondence' if selected else 'no selected reliable interior reflection assigned; visibility/photographic identity unverified, not zero error'))
        save(folder/'interval-inventory.json',inventory)
    excluded=[dict(id=o['id'],point=o['point'],in_initial_patch=o['in_initial_patch'],reasons=o['exclusion_reasons'],color=o['color']) for o in doc['observations'] if not o['selected_photo_candidate']]
    save(OUT/'excluded-observations.json.gz',excluded)
    chosen=min(summaries,key=lambda r:r['after_emax']);save(OUT/'summary.json',dict(utc=utc(),epochs=summaries,displayed_best_conditional_epoch=chosen['epoch'],stage2_started=False,stage3_started=False,success=False,exclusions=len(excluded),in_patch_exclusions=sum(r['in_initial_patch'] for r in excluded)))
    control=read(OUT/'epoch2/assignment-control.json') if (OUT/'epoch2/assignment-control.json').exists() else None
    table='\n'.join(f"| {s['epoch']} | {s['observations']} | {s['before_emax']:.3f} | {s['after_emax']:.3f} | {s['after_rms']:.3f} | {s['median']:.3f} | {s['worst_photo_fraction']:.3f} | {s['missing']} |" for s in summaries)
    w=chosen['worst'];epoch=read(OUT/('epoch2/' if chosen['directory']=='epoch2' else '')/'epoch.json');counts=Counter(o['color'] for o in epoch['observations']);trials=sum(len(list(p.glob('*.gz'))) for p in [OUT/'trials',OUT/'epoch2/trials'])
    folder=OUT/('epoch2' if chosen['directory']=='epoch2' else '')
    diagnosis=read(folder/'worst-diagnosis.json') if (folder/'worst-diagnosis.json').exists() else None
    dd=diagnosis['rows'][0] if diagnosis else None
    controls=[]
    for f in [OUT,OUT/'epoch2']:
        for name in ['finite','extended']:
            path=f/(name+'-light-controls.json.gz')
            if path.exists():
                c=read(path);controls.append(f"| {'epoch2' if f.name=='epoch2' else 'epoch1'} | {name} | {len(c['rows'])} | {c['base_emax']:.3f} | {c['best']['emax_px']:.3f} |")
    control_table='\n'.join(controls)
    half_table='\n'.join(f"| {s['epoch']} | {s['half_pixel']['emax_px']:.3f} | {s['half_pixel']['maximum_native_shift_px']:.3f} | {s['half_pixel']['missing']} |" for s in summaries if s['half_pixel'])
    text=f'''# R318 — conditional reflection minimax, Stage 1 only

**Stage 1 does not achieve excellent agreement. No expansion or reconstruction adoption.**
The primary objective throughout is the exact maximum Euclidean observed–predicted
reflection displacement. All 22 observations remain in each fitting epoch; all
2405 rigid bodies remain in camera visibility, common-light shadows and contact.
No silhouette/coverage score replaces or contributes to the fitting objective.

[Compact review](r318/results/index.html) · [Full summary](r318/results/summary.json) ·
[Verification](r318/results/verification.json) · [Protocol](R318_SPECIFICATION.md)

## Direct answers

1. **Stage 1 contains 22 interior photographed reflection candidates**, with automatic
   pigment cues {dict(counts)}. They occupy a compact photo-selected patch across
   a longer physical-address interval containing hidden and unmeasured bodies.
   Bead identities are explicitly provisional, one-to-one within each epoch.
2. **Localization:** intensity-weighted centroid of the brightest connected
   half-maximum component. Observed intensities are linearized minimum RGB,
   an achromatic reflection proxy; predicted intensities are the shared physical
   specular model. Both use the same connected-component rule, threshold and
   weighted-centroid calculation. Components never average across disconnected
   lobes. Peak and unweighted centroid alternatives, 40/50/60% threshold controls,
   saturated pixels, tied peaks and competing lobes are retained. This chooses
   a stable connected bright region rather than an arbitrary saturated pixel;
   it is not a claim of calibrated radiometry or proof every bright patch is
   pure front-surface reflection. The method is fixed before fitting.
3. **Emax before and after:** see both fixed-map epochs below. Their differing
   starting values are correspondence-only effects, not geometric progress.
4. **Worst displacement in diameter units:** best conditional epoch has
   {chosen['after_emax']:.3f}px = {chosen['worst_photo_fraction']:.3f} of the fixed
   photographic diameter estimate ({chosen['photo_D']:.3f}px). Maximum error
   divided by each bead's fixed baseline model diameter is
   {chosen['max_individual_baseline_model_fraction']:.3f}; the baseline modeled
   median diameter is {chosen['model_D']:.3f}px. The conservative photo-scale
   reference is {chosen['conservative_D']:.3f}px. Diameter normalization is frozen
   and cannot improve just by making fitted beads larger.
   The fitted model median diameter is {chosen['final_model_median_D']:.3f}px;
   the largest individual error/fitted-model-diameter ratio is
   {chosen['max_final_model_fraction']:.3f}. Both fixed and fitted scales are exposed.
5. **Worst bead:** {w['id']}, conditional index {w['index']}, observed
   {w['observed']}, predicted {w['predicted']}, error {w['error_px']:.3f}px.
   Its photographic localization uncertainty estimate is
   {w['localization_uncertainty_px']:.3f}px. The vector and competing geometric
   assignments are retained. Its error is not removed or silently reassigned.
   In the camera-isolation diagnostic its error is
   {dd['isolated_camera_error_px'] if dd else float('nan'):.3f}px, and the current
   full scene assigns the observed point to body
   {dd['full_scene_owner_at_observed'] if dd else 'unavailable'}. Thus the
   remaining mismatch cannot be explained simply by hiding the principal
   predicted reflection; body placement/correspondence remains consequential.
6. **Limitation:** residual geometry/common-illumination/correspondence coupling
   remains unresolved. The magnitude exceeds the photo-only localization
   stability scale; that does not uniquely identify the physical cause.
   Different provisional maps give different optima. A single shared surface
   specular BRDF omits glass refraction, color-dependent diffuse contamination,
   and complex illumination. No unique causal attribution is established.
7. **Expansion justified? No.** Merely crossing below half a diameter is not
   excellent alignment. The predeclared excellent-agreement target was <=0.2
   diameter, with localization and sampling controls. It is not met.
8. **100 and several hundred beads:** not fitted. Stage 1's original observations
   and the full necklace remain preserved; time passing did not trigger expansion.
9. **Specific obstruction:** a common light and coherent rigid geometry still
   leave competing worst reflections displaced by a substantial fraction of a
   bead width. The fixed-map objectives cannot independently shift those points.
   The retained correspondence alternative changes the objective with identical
   geometry, demonstrating that assignment uncertainty is also material.

## Exact conditional objectives

| Frozen epoch | Beads | Before Emax px | After Emax px | After RMS px | Median px | After Emax / photo D | Missing |
|---|---:|---:|---:|---:|---:|---:|---:|
{table}

All 22 correspondences in each epoch remain provisional; this is a usable
conditional fit, not an empty reliable cohort. Missing predicted lobes would
make the exact maximum infinite; search penalties never become reported success.
The displayed conditional winner is {chosen['epoch']}; it is not a verified
physical indexing solution. Total serialized evaluations: {trials}.
The chosen epoch has {chosen['tied_observed_peaks']} observed components with
tied maximum pixels and {chosen['localization_uncertainty_above_2px']} with
localization uncertainty estimates above 2px. These remain in the maximum;
uncertainties are conservative localization indicators, not calibrated confidence
intervals. There is no ground-truth accuracy ranking of centroid versus peak.

Half-pixel controls are separate numerical diagnostics, not refits or changed
measurements. The chosen epoch has half-pixel Emax
{chosen['half_pixel']['emax_px'] if chosen['half_pixel'] else float('nan'):.3f}px,
with maximum native-to-half-pixel predicted-centroid shift
{chosen['half_pixel']['maximum_native_shift_px'] if chosen['half_pixel'] else float('nan'):.3f}px.
Every per-bead shift, including the larger lobe switch in epoch 1, is retained
in its half-pixel file. Principal lobes are never selectively changed to improve
a score.

| Epoch | Half-pixel Emax px | Largest centroid shift px | Missing |
|---|---:|---:|---:|
{half_table}

## Automatic evidence and correspondence controls

The native original photograph is the only source of observed intensities.
An automatic pigment/dark-material mask, closing and small-hole filling define
the rope silhouette. Candidates require >=11px inward distance from that
silhouette, not distance from the image boundary. A compact set of 22 stable
interior components is chosen within inherited −100…99 geographical context
before any optical predictions. The image-only choice is not the patch with
the lowest modeled residual. All {len(doc['observations'])} detected candidate
observations are retained; {len(excluded)} are outside the selected cohort,
including {sum(r['in_initial_patch'] for r in excluded)} in the patch with stated
photo-only exclusion reasons. These counts concern detected observations, not
a claimed inventory of every physical photographed bead. The address inventory
explicitly marks unmeasured/hidden slots rather than giving them zero error.

Epoch 1 assigns observed bright supports by visible model-body overlap and freezes
the map. Epoch 2 instead maximizes one-to-one overlap of full automatic
photographic luminance basins with visible body footprints. Its map is selected
without predicted reflection distances. Both retain all 22 observations and the
same localization rule. The unchanged-original-geometry control changes
Emax {control['before_emax'] if control else float('nan'):.3f}→{control['after_emax'] if control else float('nan'):.3f}px
through {len(control['changes']) if control else 0} correspondence changes alone;
**none of that difference is geometric fitting progress**. The transferred
geometry control is separately saved. Alternative assignments remain visible.

## Diameter, optics and limits

The automatic photographic diameter estimate is an equivalent-area diameter of
luminance watershed basins inside the rope mask. Its quartiles and all individual
areas are saved; these are uncertain visible supports, not manually annotated
complete contours. The modeled diameter uses analytic projected solid support
over 181 directions. Reported pixel Emax remains primary; uncertain normalization
cannot turn an unconvincing fit into success.

One shared light source and one shared half-vector specular BRDF
predict the visible front-surface intensity. The complete necklace casts camera
occlusions and light shadows. One identical rigid legacy glass shape is retained
per setting; shared thickness, pose, camera, phase and small smooth station/phase/
orientation fields are coupled. There are no independent bead translations,
independent lights or relocated predicted points. Additional compact radial
orientation probes in the followup use this same reflection objective; this
is not a separate radial-tilt campaign. Numerical
parameter and smoothness bounds are exploration bounds, not crochet mechanics.
R312 exact camera reuse accelerates light-only controls; native ray grids and
the original full-chain support checks are retained. No new speedup claim.

Directional, finite-point and extended-directional illumination are explicitly
compared at fixed geometry and frozen correspondence. Zero inverse distance is
included in each finite-source grid; extended-source controls use one shared
square angular source and the inherited quadrature. No per-bead light is fitted.

| Epoch | Shared light hypothesis | Controls | Parent Emax px | Best control Emax px |
|---|---|---:|---:|---:|
{control_table}

These bounded tests do not rule out other lighting or glass optics. The final
parameters identify the selected light exactly; no rejected illumination control
is silently substituted in the displacement ledger.

## Verification and delivery

Independent verification reconstructs observed components directly from native
RGB pixels, checks the frozen cohort/map hashes, recomputes each Euclidean error
and maximum, checks every full-chain separating-plane witness with an independent
support formula, and compares sampled original Python camera/shadow rays.
Half-pixel principal-component controls, all failures, source snapshots and raw
photo crops are retained. These checks establish numerical reproducibility,
not correct physical identity or photographic truth.

Start 2026-10-18 01:38:55 UTC; scientific cutoff 02:02:55 UTC; hard deadline
02:08:55 UTC. See the delivery receipt for actual cutoff and verified commit.
**Stop for scientific review. No automatic R319, color-pattern inference or
beads.pov edits. Keep the current session/model; no /new is needed.**
'''
    (ROOT/'photo2/R318_REPORT.md').write_text(text)
    body=['<!doctype html><html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>R318 reflection minimax</title><style>body{font:16px system-ui;max-width:1200px;margin:2em auto;padding:0 1em}img{max-width:100%}table{border-collapse:collapse}td,th{border:1px solid #bbb;padding:.4em}</style><h1>R318 — Stage 1 reflection minimax</h1><p>22 provisional correspondences per epoch. Exact maximum is primary. No expansion or adoption.</p><p><a href="../../R318_REPORT.md">Report</a> · <a href="summary.json">Full summary</a> · <a href="verification.json">Verification</a> · <a href="excluded-observations.json.gz">All excluded observations</a></p>']
    for s in summaries:
        prefix='' if s['directory']=='.' else s['directory']+'/'
        body.append(f'<h2>{html.escape(s["epoch"])}</h2><p>Emax {s["before_emax"]:.3f} → {s["after_emax"]:.3f}px; RMS {s["after_rms"]:.3f}px; missing {s["missing"]}; identities provisional 22/22.</p><p><a href="{prefix}bead-ledger.csv">Per-bead CSV</a> · <a href="{prefix}bead-ledger.json">Confidence and alternatives</a> · <a href="{prefix}raw-patch.png">Unmodified native photo crop</a></p><img src="{prefix}vectors.png" alt="Original photograph and displacement vectors"><img src="{prefix}errors.png" alt="Per-bead error and outward cumulative maximum">')
    body.append('</html>');(OUT/'index.html').write_text('\n'.join(body))
    print('REPORT',chosen['epoch'],chosen['after_emax'],flush=True)

if __name__=='__main__':main()
