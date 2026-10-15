"""Independent native support, visibility, common-light and indexing diagnostics."""
import argparse
from copy import deepcopy
from collections import Counter
import numpy as np
from scipy.optimize import linear_sum_assignment
from PIL import Image,ImageDraw,ImageFont
from photo2.r282.geometry import unit
from photo2.r282.phase1 import image_features
from .common import *
from .geometry import Chain
from .fit import Objective

def observations(scene,inputs,split=None):
    rows=[r for r in inputs['records'] if r['fit_eligible'] and (split is None or r['split']==split)]
    result=[]
    for r in rows:
        f=r['source'];xy=pixels(f['native_bright_patch']);d=scene.trace(xy);ids,co=np.unique(d['owner'],return_counts=True)
        hist=sorted([(int(scene.indices[k]),float(v/len(xy))) for k,v in zip(ids,co) if k>=0],key=lambda v:-v[1])
        k,frac=hist[0] if hist else (None,0.);rival=hist[1][1] if len(hist)>1 else 0.
        result.append(dict(observation_id=f['observation_id'],split=r['split'],along_px=r['along_px'],
            source_location=f['representative_bright_patch_location'],source_color_context=f['source_context_color'],
            reflection_like_patch=f['reflection_like_patch'],conditional_index=k if frac>=.3 else None,
            best_surface_index=k,containment=frac,runner_up_fraction=rival,margin=frac-rival,
            alternatives=[dict(index=a,fraction=b) for a,b in hist],
            unresolved_pixels=int(np.sum(d['unknown'])),outside_model_fraction=float(np.mean(d['owner']<0)),
            source_threshold_sensitivity_px=f['uncertainty']['patch_threshold_sensitivity_px'],
            compatible=bool(frac>=.8 and frac-rival>=.2),physical_identity_verified=False))
    return result

def legacy(scene,inputs,split=None):
    rows=[r for r in inputs['legacy_colored'] if r['fit_eligible'] and (split is None or r['split']==split)]
    matrix=np.zeros((len(rows),scene.n)); details=[]
    for i,r in enumerate(rows):
        xy=pixels(r['source']['measured_support']);d=scene.trace(xy);ids,co=np.unique(d['owner'],return_counts=True)
        for k,c in zip(ids,co):
            if k>=0:matrix[i,k]=c/len(xy)
    aa,bb=linear_sum_assignment(np.c_[1-matrix,np.full((len(rows),len(rows)),.7)])
    assignments=np.full(len(rows),-1);assignments[aa[bb<scene.n]]=bb[bb<scene.n]
    for i,(r,j) in enumerate(zip(rows,assignments)):
        frac=float(matrix[i,j]) if j>=0 else 0.;other=matrix[i].copy()
        if j>=0:other[j]=0
        rival=float(other.max());source=r['source']
        details.append(dict(record_id=source['record_id'],split=r['split'],along_px=r['along_px'],
            source_location=source['measured_photo_location'],source_color=source['color'],
            conditional_index=int(scene.indices[j]) if j>=0 else None,containment=frac,
            runner_up_fraction=rival,margin=frac-rival,compatible=bool(frac>=.8 and frac-rival>=.2),
            scope='Historical automatic high colored interior; not exact truth or human ownership label',
            alternatives=[dict(index=int(scene.indices[k]),fraction=float(matrix[i,k])) for k in np.flatnonzero(matrix[i]>0)]))
    return details

def light(scene,inputs,obs):
    # Use the existing reflection flag, never the patch as a physical center.
    by={r['source']['observation_id']:r['source'] for r in inputs['records']};evidence=[]
    for r in obs:
        f=by[r['observation_id']]
        if not f['reflection_like_patch']:continue
        q=scene.trace(np.array(r['source_location'])[None],normals=True);j=int(q['owner'][0])
        if j<0:continue
        n=q['normal'][0];v=unit(2*np.dot(n,scene.eye)*n-scene.eye)
        evidence.append(dict(observation_id=r['observation_id'],split=r['split'],
            context=f['source_context_color'],surface_index=int(scene.indices[j]),normal=n.tolist(),
            inferred_direction=v.tolist(),compatible_patch=r['compatible']))
    training=[r for r in evidence if r['split']=='train' and r['compatible_patch']]
    if len(training)<2:
        return dict(constrained=False,training_reflection_candidates=len(training),evidence=evidence,
                    limitation='Fewer than two usable reflection candidates; no shared-light direction inferred.')
    v=unit(np.median([r['inferred_direction'] for r in training],axis=0))
    for r in evidence:r['angle_deg']=float(np.degrees(np.arccos(np.clip(np.dot(v,r['inferred_direction']),-1,1))))
    summary={}
    for split in ('train','holdout'):
        for context in ('yellow','red','unknown'):
            rows=[r for r in evidence if r['split']==split and r['context']==context]
            summary[split+'_'+context]=dict(n=len(rows),median_angle_deg=float(np.median([r['angle_deg'] for r in rows])) if rows else None,
                within30deg=sum(r['angle_deg']<=30 for r in rows))
    return dict(constrained=True,direction=v.tolist(),training_reflection_candidates=len(training),summary=summary,evidence=evidence,
        limitation='One robust distant mirror direction, fitted to all compatible training reflection candidates because the frozen patch flags supply no yellow candidates. Descriptive diagnostic only; flags and normals are conditional. Unknown-context reflections are not certified black bodies. No BRDF or radiometric fit; no geometry is refitted to this result.')

def summary(rows):
    if not rows:return dict(n=0)
    return dict(n=len(rows),compatible=sum(r['compatible'] for r in rows),
        mean_containment=float(np.mean([r['containment'] for r in rows])),
        median_containment=float(np.median([r['containment'] for r in rows])),
        unmatched=sum(r['conditional_index'] is None for r in rows),
        assigned_guard_observations=sum(r['conditional_index'] is not None and not REQUESTED[0]<=r['conditional_index']<=REQUESTED[1] for r in rows),
        requested_compatible=sum(r['compatible'] and r['conditional_index'] is not None and REQUESTED[0]<=r['conditional_index']<=REQUESTED[1] for r in rows),
        requested_mean_containment=float(np.mean([r['containment'] if r['conditional_index'] is not None and REQUESTED[0]<=r['conditional_index']<=REQUESTED[1] else 0. for r in rows])))

def metrics(p,inputs,training_only=False,grid=False):
    s=Chain(p,inputs);obs=observations(s,inputs,'train' if training_only else None)
    old=legacy(s,inputs,'train' if training_only else None)
    result=dict(parameters=p,observations=obs,legacy=old,
        summary={split:dict(patches=summary([r for r in obs if r['split']==split]),
            legacy=summary([r for r in old if r['split']==split])) for split in (('train',) if training_only else ('train','holdout'))},
        blocks=[dict(start_px=a,end_px=a+120,patches=summary([r for r in obs if a<=r['along_px']<a+120]),
            legacy=summary([r for r in old if a<=r['along_px']<a+120])) for a in range(-60,751,120)],
        anchor_full_containment=float(np.mean(s.trace(pixels(inputs['anchor']['measured_support']))['owner']==np.flatnonzero(s.indices==0)[0])))
    if not training_only:
        result['light']=light(s,inputs,obs)
        result['contact']=s.certify()
    if grid:
        native,rgb,_=photo();xy,d=s.grid(native.shape[:2],step=1);o=d['owner'];valid=o>=0
        actual=np.full(len(o),-999,int);actual[valid]=s.indices[o[valid]]
        f=image_features(rgb);wanted=(actual>=REQUESTED[0])&(actual<=REQUESTED[1]);q=xy[wanted]
        result['predicted_paper_fraction']=float(f['paper'][q[:,1],q[:,0]].mean()) if len(q) else None
        counts=np.bincount(o[valid],minlength=s.n);cent=[]
        for k in range(s.n):
            pts=xy[o==k];cent.append(pts.mean(0).tolist() if len(pts) else None)
        result['visibility']=[dict(index=int(k),visible_pixels=int(counts[j]),isolated_pixels=int(d['isolated_counts'][j]),
            visible_fraction=float(counts[j]/max(1,d['isolated_counts'][j])),visible_centroid=cent[j]) for j,k in enumerate(s.indices)]
        np.savez_compressed(OUT/('initial' if training_only else 'current')/'visibility.npz',xy=xy,owner=actual,unknown=d['unknown'])
    return result

def diagnose():
    inputs=read(EVIDENCE/'inputs.json.gz');p=read(OUT/'initial.json')['selected']['parameters']
    r=metrics(p,inputs,True)
    # Only training/background points enter the initial diagnosis and revised objective.
    training=Objective(inputs,revised=True).assess(p,True)
    r['training_background']=training
    r['proposed_revision']='Add five shared log-spacing and in-plane axis-normal correction knots over indices -30..210, bounded to +/-12% log rate and +/-8px axis shift; penalize train predicted material on image-derived paper. Keep source radius, 6.5 progression, one camera, both hands and unchanged inputs. No per-bead displacement.'
    save(BASE/'checkpoints/initial-diagnosis.json',r)
    print(r['summary']);print('training paper',training['predicted_paper_fraction']);print('worst train interiors',[(v['record_id'],round(v['containment'],3),round(v['along_px'])) for v in sorted(r['legacy'],key=lambda v:v['containment'])[:8]])

def compare():
    inputs=read(EVIDENCE/'inputs.json.gz');models={};evaluations={}
    for stage in ('initial','revised'):
        m=read(OUT/(stage+'.json'));p=m['selected']['parameters'];models[stage]=p
        s=Chain(p,inputs);r=metrics(p,inputs,False,True)
        # Each model gets its own full exact visibility archive.
        (OUT/stage).mkdir(exist_ok=True);(OUT/'current/visibility.npz').replace(OUT/stage/'visibility.npz')
        save(OUT/(stage+'-evaluation.json'),r);evaluations[stage]=r
    a,b=evaluations.values();by={r['observation_id']:r for r in a['observations']};changes=[]
    for r in b['observations']:
        q=by[r['observation_id']];changes.append(dict(observation_id=r['observation_id'],split=r['split'],
            source_location=r['source_location'],along_px=r['along_px'],initial_index=q['conditional_index'],revised_index=r['conditional_index'],
            initial_containment=q['containment'],revised_containment=r['containment'],
            same_index=q['conditional_index']==r['conditional_index'],delta=r['containment']-q['containment']))
    save(OUT/'comparison.json',dict(models=models,summary={k:r['summary'] for k,r in evaluations.items()},
        changes=changes,index_stability=dict(Counter('same' if r['same_index'] else 'changed' for r in changes)),
        heldout_was_not_used_in_fit=True,limits='Descriptive compatibility on one historically studied photograph. No physical ownership or calibrated accuracy truth.'))
    export(inputs,evaluations)
    print({k:r['summary'] for k,r in evaluations.items()})

def export(inputs,evaluations):
    import csv
    for stage,r in evaluations.items():
        p=r['parameters'];s=Chain(p,inputs);alt=read(OUT/(stage+'.json'))['candidates'];alternatives=[]
        for hand in (-1,1):
            pool=[m for m in alt if m['parameters']['hand']==hand]
            alternatives.append(max(pool,key=lambda m:m['train']['score']))
        alternatives=sorted(alternatives,key=lambda m:m['train']['score'],reverse=True)
        # Sensitivity is conditional to fixed sequence labels, not a probability CI.
        poses=[s.pc]
        for key,delta in [('scale',.2),('pitch',.02),('elevation',5.),('phase',.1),('s0',1.5)]:
            for sign in (-1,1):
                q=deepcopy(p);q[key]+=sign*delta;poses.append(Chain(q,inputs).pc)
        same_hand_envelope=np.max(np.linalg.norm(np.array(poses)-s.pc,axis=2),axis=0)
        alternate_positions=[Chain(m['parameters'],inputs).pc for m in alternatives]
        alternate_certificates=[Chain(m['parameters'],inputs).certify() for m in alternatives]
        observations_by={}
        for o in r['observations']:
            if o['conditional_index'] is not None:observations_by.setdefault(o['conditional_index'],[]).append(o)
        visibility={v['index']:v for v in r['visibility']};ledger=[]
        for j,k in enumerate(s.indices):
            if not REQUESTED[0]<=k<=REQUESTED[1]:continue
            linked=observations_by.get(int(k),[])
            ledger.append(dict(index=int(k),discovery_phase='Phase2 prediction',physical_identity_verified=False,
                predicted_center_xyz=s.centers[j].tolist(),predicted_center_xy=s.pc[j].tolist(),
                predicted_axis_xy=s.project(s.line[j]).tolist(),nominal_radius_units=s.radius,
                nominal_radius_px=s.radius*s.scale,station_in_deprojected_axis_px=float(s.station_px[j]),
                visibility=visibility[int(k)],color=None,
                linked_independent_observations=linked,
                status='conditional surface-compatible observation' if any(o['compatible'] for o in linked) else 'prediction without compatible independent patch',
                uncertainty=dict(local_parameter_sensitivity_radius_px=float(same_hand_envelope[j]),
                    alternate_hand_center_xy=[v[j].tolist() for v in alternate_positions],
                    competing_models=[dict(hand=m['parameters']['hand'],predicted_center_xy=v[j].tolist(),
                        contact_certified=cert['certified'],training_score=m['train']['score']) for m,v,cert in zip(alternatives,alternate_positions,alternate_certificates)],
                    interpretation='Uncalibrated conditional sensitivity; alternatives can also change integer correspondence. Hidden/model-only sites retain indices.',
                    physical_identity_probability=None,physical_center_accuracy_px=None)))
        save(OUT/(stage+'-positions.json.gz'),dict(records=ledger,parameters=p,
            alternate_hands=[dict(parameters=m['parameters'],training_score=m['train']['score'],contact_certified=cert['certified']) for m,cert in zip(alternatives,alternate_certificates)],
            input_sha256=sha(EVIDENCE/'inputs.json.gz'),requested_indices=list(REQUESTED),
            camera='One global orthographic view of a planar table axis; no calibrated perspective intrinsics',
            scope='Conditional model indices only. Source context colors remain in linked observations; model bead color unknown.'))
        with (OUT/(stage+'-positions.csv')).open('w') as f:
            w=csv.writer(f,lineterminator='\n');w.writerow(['index','x','y','z_units','visible_fraction','visible_pixels','sensitivity_radius_px','linked_feature_ids','status'])
            for o in ledger:w.writerow([o['index'],*o['predicted_center_xy'],o['predicted_center_xyz'][2],o['visibility']['visible_fraction'],o['visibility']['visible_pixels'],o['uncertainty']['local_parameter_sensitivity_radius_px'],';'.join(v['observation_id'] for v in o['linked_independent_observations']),o['status']])
    with (OUT/'correspondence-comparison.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(read(OUT/'comparison.json')['changes'][0]),lineterminator='\n');w.writeheader();w.writerows(read(OUT/'comparison.json')['changes'])

def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['diagnose','compare']);a=p.parse_args()
    for name in ('initial','revised','current'):(OUT/name).mkdir(parents=True,exist_ok=True)
    {'diagnose':diagnose,'compare':compare}[a.stage]()
if __name__=='__main__':main()
