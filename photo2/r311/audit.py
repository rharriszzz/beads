"""Actual archived search vectors, not counts of finite-difference evaluations."""
from pathlib import Path
from collections import Counter,defaultdict
import csv,json,time
import numpy as np
from scipy.spatial import cKDTree
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from photo2.r297.common import ROOT,read,save,sha,digest
from .model import BOUNDS,PAIRS

PARAMS=['phase','s0','turn','elevation','roll','tilt','minor','scale','axial','perspective','light_az','light_el','roughness','minor_y','tilt_y','tilt_y2','light_inverse','gap_steps','seam_fraction','count','winding']
PARAMS += ['radius','yaw','pitch','local_metric','local_turn','local_phase_bias','phase_transport']
UNITS=dict(phase='rad',s0='world arclength times scale; nominal px',turn='beads/turn',elevation='deg',roll='deg',tilt='deg',minor='world units',scale='px/world unit',axial='affine multiplier; H/D=.7*axial',perspective='1/world unit',light_az='deg',light_el='deg',roughness='historical lobe parameter',minor_y='fraction/image height',tilt_y='deg/image height',tilt_y2='deg/image height squared',light_inverse='1/world unit',gap_steps='addresses',seam_fraction='circuit fraction',count='bodies',winding='turns',radius='world-unit gauge',yaw='deg; world-rotation gauge',pitch='historical source-pitch multiplier')
HISTORICAL_BOX=dict(scale=[7,10.5],axial=[.45,1.12],minor=[3.5,5.4],elevation=[40,88],roll=[-70,70],perspective=[0,.001],s0=[-40,40],tilt=[-12,12],gap_steps=[.5,8],seam_fraction=[-.85,-.15],light_az=[-180,180],light_el=[25,88],roughness=[7,18],minor_y=[-.04,.04],tilt_y=[-3,3],tilt_y2=[-3,3],light_inverse=[0,.003],phase=[-np.pi,np.pi],count=[1800,3200])
DOMAINS=dict(phase='One full 2pi cycle; periodic gauge.',s0='Registration along one whole physical circuit, modulo length with coupled relabeling; ±40px is an exploration box, not a physical limit.',elevation='0<elevation<=90deg for a camera above the plane; grazing deprojection is singular. No calibrated photograph-derived interval.',roll='Periodic 360deg camera rotation; symmetries do not certify physical indexing.',tilt='Annular body axis is unoriented, so tilt is periodic 180deg; no measured crochet-compatible interval.',minor='Positive centerline radial offset; contact and camera bounds restrict each joint configuration. No measured independent min/max.',scale='Positive pixel/world scale; radius fixes the unit gauge. No calibrated independent interval.',axial='Positive affine axial factor of existing bead; contact and photo restrict joint values, no measured exact min/max.',turn='Near6.5 with abs(N*(1/turn-1/6.5))<=1; principal closed transport uses N/winding; R297 also has a frozen compact legacy turn correction.',count='Maker minimum2000; prior R306 box1800..3200 is historical, not adopted.',winding='Integer; near N/6.5 under the closure-twist allowance.',perspective='Nonnegative inverse camera distance, plus explicit nonsingular projection and camera-clearance bounds.',light_az='360deg periodic shared light azimuth.',light_el='Physical source direction above plane (0..90deg); historic fit box25..88.',roughness='Positive historical optical lobe parameter; no independent calibrated physical interval.',minor_y='Existing fractional image-height radius law; positive radius everywhere and contacts, not a measured ±4% law.',tilt_y='Existing image-height orientation law; prior ±3deg exploration control, not mechanical truth.',tilt_y2='Existing quadratic image-height law; prior ±3deg exploration control.',light_inverse='Nonnegative inverse shared light distance; finite-source visibility remains required.',gap_steps='Open-end construction, nonnegative; finite prior interval is a search control.',seam_fraction='Periodic index-storage/cut coordinate; open cut is physical, closed storage is a gauge.')
DOMAINS.update(radius='Positive radius fixes the world-unit gauge; frozen at1.784536980648071 in these hypotheses.',yaw='Periodic pure world-rotation gauge; fixed at0. Camera roll is distinct and active.',pitch='Modern mean advance is set by fixed count and true total arclength; saved pitch is unused. Original R297 compact local-metric law still uses its frozen pitch multiplier.',local_metric='Inherited R297 compact station-correction blend; inactive/zero in modern families. No independently measured physical interval.',local_turn='Inherited R297 compact phase-rate blend; inactive/zero in modern families.',local_phase_bias='Inherited R297 compact phase bias, radians; inactive/zero in modern families.',phase_transport='Inherited R297 compact correction transport blend; inactive/zero in modern families.')

def files():
    rows=[]
    for label,folder,pattern in [
      ('R306-initial','r306/results/campaign-initial','candidates/*.gz'),
      ('R306-cold','r306/results/independent','candidates/*.gz'),
      ('R306-main','r306/results/campaign','candidates/*.gz'),
      ('R306-native','r306/results/campaign/native-refinement','candidate-*.gz'),
      ('R307','r307/results/campaign','trials/*.gz'),
      ('R308','r308/results/campaign','trials/*.gz'),
      ('R309','r309/results/campaign','trials/*.gz')]:
        for f in sorted((ROOT/'photo2'/folder).glob(pattern)):
            r=read(f);p=r.get('parameters')
            if p is None:continue
            feasible=r.get('feasible',r.get('status') in ['eligible','structure-screened'])
            status=r.get('status', 'feasible' if feasible else r.get('rejection') or r.get('reason') or 'unknown')
            tag=r.get('tag',r.get('stage','native'))
            result=r.get('result',r.get('train',{}))
            missing=result.get('missing',result.get('unmatched'))
            if missing is None and isinstance(result.get('reflection'),dict):missing=result['reflection'].get('missing')
            rows.append(dict(campaign=label,id=r.get('id'),file=str(f.relative_to(ROOT)),sha256=sha(f),parameters=p,
                             feasible=bool(feasible),status=status,tag=tag,origin=r.get('origin'),operation=r.get('operation'),
                             missing=missing,optically_evaluated=bool(label=='R306-native' or 'predictions' in r or 'residual' in r or 'scores' in result or 'reflection' in result),
                             numerical_step=r.get('step',r.get('native_step',3 if label.startswith('R306') and label!='R306-native' else 1))))
    return rows

def unitvector(p):
    return [((p.get(k,0)+np.pi)%(2*np.pi)-np.pi if k=='phase' else p.get(k,0))/(hi-lo) for k,(lo,hi) in BOUNDS.items()]

def run(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);began=time.monotonic();rows=files()
    save(out/'vectors.json.gz',rows)
    summary={};ranges=[]
    for campaign in dict.fromkeys(r['campaign'] for r in rows):
        rr=[r for r in rows if r['campaign']==campaign];families=defaultdict(list)
        for r in rr:
            p=r['parameters'];families[f"N{p['count']}:hand{p['hand']}:{p['topology']}"] .append(r)
        group=[]
        for fam,fr in families.items():
            for k in PARAMS:
                v=np.array([r['parameters'].get(k,0) for r in fr],float)
                ranges.append(dict(campaign=campaign,family=fam,parameter=k,units=UNITS.get(k,'inherited multiplier'),minimum=float(v.min()),maximum=float(v.max()),unique=len(set(np.round(v,10))),evaluations=len(v)))
            group.append(dict(family=fam,trials=len(fr),feasible=sum(r['feasible'] for r in fr)))
        vectors=np.array([unitvector(r['parameters']) for r in rr]);nearest=cKDTree(vectors).query(vectors,k=2)[0][:,1] if len(vectors)>1 else np.array([np.inf])
        full=[digest(r['parameters']) for r in rr];global_keys=[digest({k:r['parameters'].get(k,0) for k in BOUNDS}) for r in rr]
        fields={}
        for k in ['axis_nodes','local_phase','local_spacing','bend','strain','phase_knots','local_bend','local_metric','local_turn','local_phase_bias','phase_transport']:
            vals=[r['parameters'].get(k) for r in rr]
            fields[k]=dict(unique=len({digest(v) for v in vals}),note='Across all families/parents; variation does not imply broad joint global coverage.')
        summary[campaign]=dict(trials=len(rr),status=dict(Counter(r['status'] for r in rr)),tags=dict(Counter(r['tag'].split(':')[0] for r in rr)),
             families=group,starts=[{k:r[k] for k in ['id','origin','tag','file']} for r in rr if r['tag'].startswith(('initial','start'))],
             exact_duplicate_full_vectors=len(full)-len(set(full)),exact_duplicate_global_vectors=len(global_keys)-len(set(global_keys)),
             near_another_global_vector_within_one_percent_box=int((nearest<.01).sum()),
             near_another_global_vector_within_point_one_percent_box=int((nearest<.001).sum()),
             proximity_warning='Nearest-neighbor density, symmetric and ignoring correction fields/discrete families; not number of wasted evaluations. Exact full-vector repeats may use different fixed owners/objectives.',
             optically_evaluated=sum(r['optically_evaluated'] for r in rr),
             optical_sampling_steps=dict(Counter(str(r['numerical_step']) for r in rr if r['optically_evaluated'])),
             scored_with_missing_highlights=sum((r['missing'] or 0)>0 for r in rr),missingness_not_rejection=True,fields=fields)
    with (out/'ranges.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(ranges[0]),lineterminator="\n");w.writeheader();w.writerows(ranges)
    controls=read(ROOT/'photo2/r309/results/campaign/checkpoint.json')
    summary['R309']['shared_trials']=len(controls['shared'])
    summary['R309']['derivative_blocks']=sum(len(b['controls']) for b in controls['branches'].values())
    summary['R309']['all_columns_gate_failures']=sum(not all(c['reliable']) for b in controls['branches'].values() for c in b['controls'])
    summary['R309']['guided_proposals']=sum('step' in c for b in controls['branches'].values() for c in b['controls'])
    summary['R309']['principal_R297_original_start']=False
    summary['R309']['missing_highlight_gate']='No hard missing-lobe basin veto in R309; missingness penalized. All41 derivative blocks failed the all-column numerical gate.'
    # Reconstruct recorded numerical gates without inventing exclusive causes.
    # A proposal may fail several guards simultaneously.
    for campaign,threshold in [('R307',.05),('R308',.03)]:
        folder=ROOT/f'photo2/{campaign.lower()}/results/campaign'
        raw={r.get('id'):r for p in sorted((folder/'trials').glob('*.gz')) for r in [read(p)]}
        trust=[r['trust'] for r in raw.values() if 'trust' in r] if campaign=='R307' else [read(p) for p in (folder/'predictions').glob('*.json')]
        summary[campaign]['recorded_trust_predictions']=len(trust)
        summary[campaign]['trust_ratio_below_acceptance']=sum(t.get('ratio') is not None and t['ratio']<=threshold for t in trust)
        sensitivities=list(folder.glob('sensitivity-*.json.gz')) if campaign=='R307' else list((folder/'sensitivities').glob('*.gz'))
        missing_sides=0;sides=0;unavailable=0
        for path in sensitivities:
            rec=read(path);base=raw.get(rec.get('base'));unavailable+=sum('unavailable' in z for z in rec.get('methods',[]))
            if not base or not base.get('feasible'):continue
            baseline_missing=base['result']['unmatched']
            for ident in rec.get('trials',[]):
                z=raw.get(ident)
                if z and z.get('feasible'):
                    sides+=1;missing_sides+=z['result']['unmatched']>baseline_missing
        summary[campaign].update(feasible_recorded_derivative_sides=sides,sides_with_more_missing_than_their_recorded_base=missing_sides,
                                 unavailable_derivative_columns_explicitly_marked=unavailable,
                                 derivative_gate_note='R307/R308 do not use R309 all-column instability gate. Trust ratios and additional missing-lobe guards can reject adoption; these are overlapping diagnostics, not exclusive rejection reasons.')
        if campaign=='R307':
            accepted={r['id'] for r in read(folder/'checkpoint.json')['accepted']}
            attempts=[r for r in raw.values() if r.get('tag')=='native-acceptance']
            summary[campaign]['native_acceptance_attempts']=len(attempts)
            summary[campaign]['native_acceptance_not_adopted']=sum(r['id'] not in accepted for r in attempts)
    # Bound violations reconstructed by field; a single proposal may violate
    # several bounds, so counts need not sum to the bounds-rejected total.
    for campaign in summary:
        invalid=[r for r in rows if r['campaign']==campaign and ('bound' in r['status'])]
        flags=Counter()
        for row in invalid:
            p=row['parameters']
            for key,(lo,hi) in HISTORICAL_BOX.items():
                if key!='phase' and key in p and not lo<=p[key]<=hi:flags[key]+=1
            turn=p['count']/p['winding'] if p['topology']=='closed' else p['turn']
            if abs(p['count']*(1/turn-1/6.5))>1.000001:flags['closure_twist']+=1
            for key,limit in [('axis_nodes',30),('local_phase',.45),('local_spacing',.02)]:
                if key in p and max(abs(np.asarray(p[key])))>limit:flags[key]+=1
        summary[campaign]['reconstructed_bound_violations']=dict(flags)
        summary[campaign]['bound_flag_policy']='Overlapping flags from final published bounds. Archived pretransition implementations can differ; recorded status above is authoritative.'
    allowed={k:dict(units=UNITS.get(k,'inherited multiplier'),physical_domain=DOMAINS.get(k,'Unknown exact physical range.'),historical_implementation_box=HISTORICAL_BOX.get(k),r311_exploration_box=list(BOUNDS[k]) if k in BOUNDS else None) for k in PARAMS}
    save(out/'coverage.json',dict(campaigns=summary,allowed=allowed,seconds=time.monotonic()-began,
          omissions='R309 starts omit original R297, R306 hand-plus closed, and all cold broad camera/shape starts. R308 includes four R306 discrete families but no original R297 principal. R306 contains converted R297 starts and broad count-grid starts, not unchanged R297 anchor placement.',
          counting='Trial files only, not checkpoint copies, archived source copies, qualification/replay duplicates. R306 includes428 initial+684 cold+2942 main=4054 proposals and12 separately labeled native trials.',
          limits='Finite ranges and occupied cells do not establish uniform coverage; projections can hide sparse high-dimensional combinations. Contact failures remain inconclusive unless a solid witness exists.'))
    for n,(a,b) in enumerate(PAIRS):
        fig,axes=plt.subplots(1,4,figsize=(16,4),layout='constrained')
        for ax,roundname in zip(axes,['R306','R307','R308','R309']):
            rr=[r for r in rows if r['campaign'].startswith(roundname)]
            x=[(r['parameters'].get(a,0)+np.pi)%(2*np.pi)-np.pi if a=='phase' else r['parameters'].get(a,0) for r in rr];y=[r['parameters'].get(b,0) for r in rr]
            ax.scatter(x,y,s=5,c=['#176d9c' if r['optically_evaluated'] else '#cf9327' if r['feasible'] else '#bb4e40' for r in rr],alpha=.35,rasterized=True)
            from matplotlib.patches import Rectangle
            if a in HISTORICAL_BOX and b in HISTORICAL_BOX:
                aa,bb=HISTORICAL_BOX[a],HISTORICAL_BOX[b]
                ax.add_patch(Rectangle((aa[0],bb[0]),aa[1]-aa[0],bb[1]-bb[0],fill=False,linestyle='--',edgecolor='#333333',linewidth=1))
            ax.set(xlim=BOUNDS[a],ylim=BOUNDS[b],xlabel=a,ylabel=b,title=f'{roundname}: {len(rr)} vectors')
            ax.grid(alpha=.2)
        fig.suptitle('Historical proposals: blue optical score (includes coarse sampling); amber structural-only; red rejected. Dashed: old box; axes: R311 box.')
        fig.savefig(out/f'coverage-{a}-{b}.png',dpi=160);plt.close(fig)
    # Per-parameter envelopes show full engineering box alongside actual proposals.
    fig,axes=plt.subplots(2,4,figsize=(15,7),layout='constrained')
    for ax,(k,box) in zip(axes.ravel(),BOUNDS.items()):
        for y,campaign in enumerate(['R306','R307','R308','R309']):
            v=[r['parameters'].get(k,0) for r in rows if r['campaign'].startswith(campaign)]
            ax.scatter(v,np.full(len(v),y),s=3,alpha=.25)
        ax.set(xlim=box,yticks=range(4),yticklabels=['R306','R307','R308','R309'],xlabel=k)
    fig.suptitle('Many perturbations do not imply broad coverage. Finite exploration ranges, not measured physical limits.')
    fig.savefig(out/'parameter-ranges.png',dpi=160);plt.close(fig)
    print('coverage audit',len(rows),'archived trials',flush=True)
    return summary
if __name__=='__main__':run(ROOT/'photo2/r311/results/audit')
