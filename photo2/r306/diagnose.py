"""Automatic residual triage, common-evidence comparisons and causal controls."""
from copy import deepcopy
from pathlib import Path
import time
import numpy as np
from scipy.spatial import cKDTree
from photo2.r297.common import ROOT,read,save,pixels
from photo2.r297.geometry import reference
from photo2.r305.diagnose import isolated
from .geometry import Chain
from .objective import predict,match,contours,contour_samples

def summary(model):
    row=dict(name=model['name'],count=model['parameters']['count'],hand=model['parameters']['hand'],topology=model['parameters']['topology'],
        certified=model['physical']['certified'],minimum_separating_margin=model['physical']['independent_minimum_gap'],
        contacts=model['physical']['pairs'],reflection=model['correspondences']['summary_strong'],assignment_sensitive=model['correspondences']['assignment_sensitivity'],
        phase=model['closure'],axis_departure_median=float(np.median(abs(np.array(model['reference_departure_px'])))),
        axis_departure_max=float(np.max(abs(np.array(model['reference_departure_px'])))),
        visible_bodies=sum(b['visible_area_px2']>0 for b in model['positions']),all_bodies=len(model['positions']))
    for split in ['development','comparison']:
        z=model['evaluation'][split];row[split]={k:z[k] for k in ['loss','bead_extent_mae','bead_axial_mae','bead_face_mae','envelope_width_mae','envelope_edge_mae','envelope_common_mae']}
        row[split].update({k:z['photographic'][k] for k in ['paper_occupied','colored_missing','region_containment','color_conflict','separator_error_px']})
        row[split]['visible_boundary_mae']=float(np.mean([r['boundary_mae'] for r in z['contours']]))
        row[split]['reflection']={k:v for k,v in z['reflection'].items() if k!='records'}
    row['native_supports']={split:{kind:dict(n=len(rows),mean=float(np.mean([r['fraction'] for r in rows])) if rows else None,
        compatible=sum(r['compatible'] for r in rows)) for kind in ['region','patch']
        for rows in [[r for r in model['supports'] if r['kind']==kind and (split=='all' or r['split']==split)]]}
        for split in ['all','train','validation','reserved','buffer']}
    return row

def red_checks(scene,model):
    old=[r for r in read(ROOT/'photo2/r305/results/starting-red-diagnosis.json') if r['model']=='primary'];out=[]
    corr={r['id']:r for r in model['correspondences']['records']}
    for r in old:
        xy=pixels({'runs':r['photographic_runs']});tr=scene.trace(xy);o=tr['owner'];c=corr.get(r['id']);idx=c['index'] if c else None
        values,count=np.unique(o[o>=0],return_counts=True);modal=int(scene.indices[values[count.argmax()]]) if len(values) else None
        if idx is None:idx=modal
        one=isolated(scene,idx).trace(xy) if idx is not None else None
        hit=(one['owner']>=0) if one else np.zeros(len(xy),bool);assigned=(o==np.searchsorted(scene.indices,idx)) if idx is not None else np.zeros(len(xy),bool)
        out.append(dict(model=model['name'],id=r['id'],historical_R305_index=r['index'],index=idx,modal_index=modal,
            pixels=len(xy),photographic_runs=r['photographic_runs'],point=r['point'],assigned_fraction=float(assigned.mean()),
            other_fraction=float(((o>=0)&~assigned).mean()),outside_fraction=float((o<0).mean()),
            occluded_assigned_fraction=float((hit&~assigned&(o>=0)).mean()),shape_or_pose_miss_fraction=float((~hit).mean()),
            unknown_camera_fraction=float(tr['unknown'].mean()),unobstructed_segments=[],
            interpretation='Original R305 photographic pixels; current conditional correspondence/modal fallback. Unobstructed misses do not identify shape, pose, projection or owner separately.'))
    return out

def diagnose(out,models,data,m,obs):
    out=Path(out);primary=models[0];scene=Chain(primary['parameters'],data);comparison=[summary(r) for r in models]
    save(out/'comparison.json',comparison)
    from .residual_audit import build as residual_audit
    residual_audit(out,models,data)
    # Common supports distinguish actual material progress from changed assignments.
    native_changes=[]
    pmap={r['id']:r for r in primary['supports']}
    for model in models[1:]:
        for row in model['supports']:
            p=pmap[row['id']]
            native_changes.append(dict(reference=model['name'],id=row['id'],kind=row['kind'],split=row['split'],point=row['point'],
                before=row['fraction'],after=p['fraction'],delta=p['fraction']-row['fraction'],before_index=row['index'],after_index=p['index']))
    save(out/'common-support-deltas.json.gz',native_changes)
    regions=[]
    for model in models:
        for i,r in enumerate(model['regions']):
            previous=model['regions'][(i-1)%32];following=model['regions'][(i+1)%32]
            informative=r['n']>=3 or r['support_count']>=4;tags=[]
            if r['rms'] is not None and r['rms']>12:tags.append('reflection displacement')
            if (r['colored_omission'] or 0)>.3:tags.append('unexplained colored material')
            if (r['paper_occupation'] or 0)>.12:tags.append('background occupation')
            if r['rms'] is not None and previous['rms'] is not None and r['rms']-previous['rms']>4:tags.append('regional jump')
            if r['rms'] is not None and following['rms'] is not None and r['rms']-following['rms']>4:tags.append('subsequent recovery')
            if r['ambiguous']>r['n']/2:tags.append('correspondence ambiguity')
            if not informative:tags.append('sparse photographic constraint')
            score=((r['rms'] or 0)/12+2*(1-(r['support_containment'] or 0))+2*(r['colored_omission'] or 0)+2*(r['paper_occupation'] or 0))*(1 if informative else .4)
            regions.append(dict(model=model['name'],section=i,priority=score,informative=informative,tags=tags,metrics=r,
                inference='Descriptive residual categories. Phase slip remains possible; no physical identity sequence or unique cause established.'))
    regions.sort(key=lambda r:-r['priority']);save(out/'diagnosis.json',regions)
    # The maker's old problem intervals are geographic cohorts, never fixed identities.
    old=read(ROOT/'photo2/r305/results/primary.json.gz');oldpos={b['index']:b for b in old['positions']};oldcorr=read(ROOT/'photo2/r305/results/primary-correspondences.json')['records']
    cohorts=[]
    for lo,hi in [(-1,0),(30,79),(103,103),(230,329),(760,859),(910,959)]:
        ids={r['observation'] for r in oldcorr if r['index'] is not None and lo<=r['index']<=hi}
        cases=[r for r in primary['correspondences']['records'] if r['id'] in ids]
        center=np.mean([oldpos[k]['axis_xy'] for k in range(lo,hi+1)],axis=0)
        cohorts.append(dict(historical_R305_interval=[lo,hi],original_observation_ids=sorted(ids),center=center.tolist(),
            current_indices=[r['index'] for r in cases],records=cases,meaning='Same original observations; current conditional indices may differ.'))
    save(out/'R305-problem-cohorts.json',cohorts)
    red=[]
    for model in models:
        from photo2.r299.forward import Surface
        s=(Surface if model.get('historical') else Chain)(model['parameters'],data);red+=red_checks(s,model)
    save(out/'starting-red-diagnosis.json',red)
    # Two-sided interventions at the worst informative TRAINING regions. Exact
    # native reflections with frozen owners separate geometry from reassignment.
    controls_file=out/'controlled-diagnosis.json.gz'
    if not controls_file.exists():
        selected=[r['section'] for r in regions if r['model']=='primary' and r['metrics']['n']>=3 and r['section']%4!=3][:3]
        evidence=[r for r in obs if r['strong'] and r['section'] in selected]
        fixed={r['id']:r['index'] for r in primary['correspondences']['records'] if r['strong']}
        basepred=[dict(index=b['index'],point=b['reflection']['centroid']) for b in primary['positions'] if b['reflection']]
        base=match(evidence,basepred,fixed=fixed);controls=[]
        for key,step in [('phase',.05),('axial',.025),('roll',2.),('light_az',3.),('axis_nodes',1.),('local_spacing',.001)]:
            for sign in [-1,1]:
                p=deepcopy(primary['parameters']);t=time.monotonic()
                if key in ['axis_nodes','local_spacing']:
                    center=np.array(evidence[0]['point'])
                    if key=='axis_nodes':k=int(round(reference().project([center])['arc'][0]/reference().length*32))%32
                    else:k=int(round((scene.indices[scene.tree.query(center)[1]]/scene.n+.5)%1*32))%32
                    for off,w in [(-1,.35),(0,1.),(1,.35)]:p[key][(k+off)%32]+=sign*step*w
                else:p[key]+=sign*step
                try:
                    s=Chain(p,data);cert=s.certify(iterations=100,witnesses=True);row=dict(parameter=key,delta=sign*step,parameters=p,certified=cert['certified'])
                    if cert['certified']:
                        pred,meta=predict(s,1.,evidence);locked=match(evidence,pred,fixed=fixed);free=match(evidence,pred)
                        row.update(fixed_owner=locked,free_assignment=free,numerics=meta,delta_fixed_loss=locked['loss']-base['loss'])
                    else:row.update(contact=cert,penetration=s.penetration(cert))
                except ValueError as error:row=dict(parameter=key,delta=sign*step,certified=False,reason=str(error))
                row['seconds']=time.monotonic()-t;controls.append(row);print('diagnostic control',key,sign,row.get('delta_fixed_loss'),flush=True)
                save(controls_file,dict(regions=selected,baseline=base,controls=controls,
                    interpretation='Evaluation-only interventions after model freeze. Partial directional improvements do not uniquely identify the cause or justify adoption. Geometry, light and alternative ownership remain coupled.'))
    # Report identity sensitivity between viable families by nearest geographic
    # prediction, never by treating equal integer numbers as equal bodies.
    identities=[]
    for model in models[1:]:
        other={r['id']:r for r in model['correspondences']['records']}
        for r in primary['correspondences']['records']:
            q=other[r['id']]
            identities.append(dict(id=r['id'],alternative=model['name'],primary_index=r['index'],alternative_index=q['index'],
                prediction_shift_px=float(np.linalg.norm(np.array(r['predicted'])-q['predicted'])) if r['predicted'] and q['predicted'] else None,
                primary_status=r['status'],alternative_status=q['status']))
    save(out/'identity-sensitivity.json.gz',identities)
    # Same-count initialization control: freeze its mathematical index mapping
    # and measure final residuals before allowing any reassignment benefit.
    fixed_file=out/'fixed-initial-assignment-control.json.gz'
    if not fixed_file.exists():
        st=read(out/'checkpoint.json');p=primary['parameters']
        candidates=[(i,r) for i,r in enumerate(st['starts']) if all(r['parameters'][key]==p[key] for key in ['count','hand','topology'])]
        if candidates:
            i,r=candidates[0];s=Chain(r['parameters'],data);strong=[q for q in obs if q['strong']]
            pred,meta=predict(s,1.,strong);initial=match(strong,pred);fixed={r['id']:r['index'] for r in initial['records']}
            finalpred=[dict(index=b['index'],point=b['reflection']['centroid']) for b in primary['positions'] if b['reflection']]
            save(fixed_file,dict(initial_id=i,initial_parameters=r['parameters'],initial=initial,
                final_fixed=match(strong,finalpred,fixed=fixed),final_free=match(strong,finalpred),numerics=meta,
                interpretation='Same count/hand/topology and global index gauge, but no verified physical identities. Fixed-initial mapping exposes improvements lost when rematching is disallowed. Union material coverage and envelope metrics do not use reflection assignments.'))
        else:save(fixed_file,dict(available=False,reason='No initial hypothesis shares the final count/hand/topology. Equal numbers across counts are not a valid fixed-identity control.'))

if __name__=='__main__':
    from .evidence import load
    out=ROOT/'photo2/r306/results/campaign';data,m,obs=load();manifest=read(out/'export-manifest.json')
    models=[read(out/'exports'/f'{name}.json.gz') for name in manifest['models']];models.sort(key=lambda r:r['name']!='primary');diagnose(out,models,data,m,obs)
