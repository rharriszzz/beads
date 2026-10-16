"""Evaluation only: independent material supports, geometry and ranked intervals."""
import copy,csv,json,time
import numpy as np
from scipy.spatial import cKDTree
from scipy.ndimage import binary_erosion
from PIL import Image
from photo2.r297.common import save
from photo2.r302.experiment import clean
from .model import *
from .forward import raster,records,physical,segments

def isolated(scene,k):
    single=copy.copy(scene);j=np.searchsorted(scene.indices,k);single.n=1
    single.centers=scene.centers[j:j+1];single.pc=scene.pc[j:j+1];single.indices=np.array([k]);single.g={key:v[j:j+1] for key,v in scene.g.items()};single.tree=cKDTree(single.pc)
    return single

def support_points(r):
    return np.array([(x,y) for y,a,b in r['measured_support']['runs'] for x in range(a,b+1)])

def main():
    start=time.monotonic();source=read(ROOT/'photo2/r283/results/phase1.json.gz')['records'];models=[];red=[];ranked=[]
    special={'C-1130-0364':0,'C-1116-0328':-1,'E9-1088-0322':-8,'C-1497-0271':103}
    for name in FAMILIES:
        scene=Extended(name);doc=read(BASE/f'results/{name}.json.gz');corr=read(BASE/f'results/{name}-correspondences.json');mat=read(BASE/f'results/{name}-material.json.gz');rr=corr['records'];core=[b for b in doc['positions'] if b['displayed']];by={b['index']:b for b in core};r=dict(np.load(BASE/f'results/{name}-raster.npz'));x0,y0,x1,y1=doc['bounds']
        # Native-address lossless PNG for offline first-hit picking; RG=uint16+32768.
        enc=r['address'].astype(np.int32)+32768;rgb=np.zeros((*enc.shape,3),np.uint8);rgb[:,:,0]=enc%256;rgb[:,:,1]=enc//256;Image.fromarray(rgb).save(REVIEW/f'{name}-owners.png')
        supports=[]
        for obs in source:
            if obs['color'] not in ['red','yellow'] or not (obs.get('measured_support') or {}).get('runs'):continue
            pts=support_points(obs);center=pts.mean(0);pr=scene.ref.project([center]);arc=float(pr['arc'][0]-scene.photo_origin);arc=arc+scene.ref.length if arc < -1000 else arc
            if not core[0]['photo_arc']<=arc<=core[-1]['photo_arc']:continue
            xx,yy=pts.T;valid=(xx>=x0)&(xx<=x1)&(yy>=y0)&(yy<=y1);owner=np.full(len(pts),-32768);owner[valid]=r['address'][yy[valid]-y0,xx[valid]-x0]
            counts={int(k):int(n) for k,n in zip(*np.unique(owner,return_counts=True))};largest=max((k for k in counts if k!=-32768),key=lambda k:counts[k],default=None)
            matched=next((q['index'] for q in rr if q['observation']==obs['record_id']),None)
            idx=(matched if matched is not None else special[obs['record_id']]) if obs['record_id'] in special else int(round(np.interp(arc,scene.photo_arc,scene.indices)))
            row=dict(id=obs['record_id'],point=center.tolist(),index=idx,color=obs['color'],pixels=len(pts),outside_union=float(np.mean(owner==-32768)),owner_counts=counts,largest_owner=largest,status=obs['status'],scope='Historical automatic colored interior; incomplete and uncertain, not a verified whole-bead contour or identity.')
            supports.append(row)
            if obs['record_id'] not in special:continue
            b=by[idx];single=isolated(scene,idx);unobscured=single.camera(pts)['owner']>=0;assigned=owner==idx;other=(owner!=-32768)&~assigned
            bounds=np.array(b['boundary_segments']);edges=np.concatenate([np.array([[x,y] for x in np.arange(a,c+.01) for y in [bb]]) if bb==d else np.array([[a,y] for y in np.arange(bb,d+.01)]) for a,bb,c,d in bounds]) if len(bounds) else np.empty((0,2))
            distances=cKDTree(edges).query(pts)[0] if len(edges) else np.full(len(pts),np.nan)
            lo=pts.min(0)-35;hi=pts.max(0)+35;yy2,xx2=np.mgrid[lo[1]:hi[1]+1,lo[0]:hi[0]+1];xy=np.c_[xx2.ravel(),yy2.ravel()];sil=single.camera(xy)['owner'].reshape(xx2.shape)>=0
            paired=[q for q in rr if q['observation']==obs['record_id'] or q['index']==idx]
            detail=dict(**row,model=name,assigned_fraction=float(assigned.mean()),other_fraction=float(other.mean()),outside_fraction=float(np.mean(owner==-32768)),unobstructed_assigned_fraction=float(unobscured.mean()),occluded_assigned_fraction=float(np.mean(unobscured&other)),unknown_camera_fraction=float(np.mean(r['unknown'][pts[:,1]-y0,pts[:,0]-x0])),shape_or_pose_miss_fraction=float(np.mean(~unobscured)),uncovered_assigned_pixels=int((~assigned).sum()),outside_boundary_distance_median_px=float(np.median(distances[~assigned])) if (~assigned).any() else 0.,outside_boundary_distance_max_px=float(np.max(distances[~assigned])) if (~assigned).any() else 0.,reflection_records=paired,photographic_runs=obs['measured_support']['runs'],unobstructed_segments=segments(sil,*lo),visible_segments=b['boundary_segments'],interpretation='Unobstructed miss diagnoses shape/pose/projection or uncertain support/identity; occluded fraction diagnoses modeled neighbor masking. Neither isolates a fitted parameter.')
            red.append(detail)
        save(BASE/f'results/{name}-colored-supports.json.gz',clean(supports))
        # Curvature, advance, phase and station continuity on every address.
        chord=np.linalg.norm(np.diff(scene.line,axis=0),axis=1);advance=np.diff(scene.arc);turn=np.arccos(np.clip(np.sum(unit(scene.spline(scene.arc[:-1],1))*unit(scene.spline(scene.arc[1:],1)),axis=1),-1,1))
        geometry=dict(indices=scene.indices.tolist(),curvature=scene.curvature.tolist(),world_arc=scene.arc.tolist(),chord=chord.tolist(),advance=advance.tolist(),tangent_turn_radians=turn.tolist(),phase_step=np.diff(scene.phase).tolist(),photo_arc_step=np.diff(scene.photo_arc).tolist(),reference_seam=scene.reference_seam,maximum_chord_deficit=float(np.max(advance-chord)),minimum_photo_arc_step=float(np.diff(scene.photo_arc).min()),maximum_phase_step_error=float(np.max(abs(np.diff(scene.phase)-scene.hand*2*np.pi/scene.p['turn']))))
        save(BASE/f'results/{name}-geometry.json',clean(geometry))
        used={q['index'] for q in rr if q['index'] is not None};groups=corr['groups']
        for g in groups:
            lo,hi=g['first'],g['last'];bs=[b for b in core if lo<=b['index']<=hi];qs=[q for q in rr if q['index'] is not None and lo<=q['index']<=hi];strong=[q for q in qs if q['strong']];support=[q for q in supports if lo<=q['index']<=hi];pairs=[q for q in doc['physical']['penetration_checks'] if any(lo<=k<=hi for k in q['pair'])]
            g['demonstrated_penetrating_pairs']=sum(q['demonstrated_penetration'] for q in pairs);g['uncertified_pairs']=len(pairs);g['maximum_curvature']=max(b['curvature'] for b in bs);g['insufficient_evidence']=len(strong)<3;g['assignment_sensitive']=sum(not q['stable_across_gap_penalties'] for q in qs)
            g['examples']={
              'unmatched_observed':[dict(id=q['observation'],index=int(round(np.interp(q['photo_arc'],scene.photo_arc,scene.indices)))) for q in rr if q['index'] is None and lo<=np.interp(q['photo_arc'],scene.photo_arc,scene.indices)<=hi],
              'unassigned_predicted':[b['index'] for b in bs if b['reflection'] and b['index'] not in used],
              'no_predicted_reflection':[b['index'] for b in bs if not b['reflection'] and b['visible_area_px2']],
              'occluded':[b['index'] for b in bs if not b['visible_area_px2']],
              'ambiguous':[q['index'] for q in qs if q['status']=='ambiguous'],
              'physical_failure':[b['index'] for b in bs if b['uncertified_pairs']]}
            x=np.array([q['index'] for q in strong]);y=np.array([q['tangent_px'] for q in strong]);g['signed_tangent_slope_px_per_50']=float(np.polyfit(x,y,1)[0]*50) if len(x)>=3 and np.ptp(x)>10 else None
            g['observed_support_omission']=float(np.average([q['outside_union'] for q in support],weights=[q['pixels'] for q in support])) if support else None
            g['largest_ordered_pair_index_gap']=max(np.diff(sorted(q['index'] for q in qs)),default=0)
            g['strong_error_change_from_previous']=g['rms']-groups[groups.index(g)-1]['rms'] if groups.index(g)>0 and g['rms'] is not None and groups[groups.index(g)-1]['rms'] is not None else None
            numfile=BASE/f'results/{name}-numerical.json'
            numeric=[q for q in read(numfile)['checks'] if lo<=q['index']<=hi] if numfile.exists() else []
            g['sampling_centroid_change_max_px']=max((q['centroid_change_px'] for q in numeric if q['centroid_change_px'] is not None),default=None)
            g['sampling_presence_changes']=sum(q['native_present']!=q['half_pixel_present'] for q in numeric)
            components=dict(curvature=g['maximum_curvature']/.04,abrupt_error_change=abs(g['strong_error_change_from_previous'] or 0)/scene.scale,signed_local_drift=abs(g['signed_tangent_slope_px_per_50'] or 0)/scene.scale,numerical=(g['sampling_centroid_change_max_px'] or 0)/2,unassigned_fraction=g['unmatched_predictions']/max(1,len(bs)),reflection=(g['rms'] or 0)/scene.scale,material=(g['colored_omission'] or 0)/.2,paper=(g['paper_occupation'] or 0)/.1,physical=g['demonstrated_penetrating_pairs']/max(1,len(bs)/10),ambiguity=g['ambiguous']/max(1,len(qs)),insufficient_evidence=1 if g['insufficient_evidence'] else 0)
            ranked.append(dict(model=name,first=lo,last=hi,score=float(sum(components.values())),components=components,summary=g))
        corr['unmatched_outside_model_geography']=[q for q in rr if q['index'] is None and not core[0]['photo_arc']<=q['photo_arc']<=core[-1]['photo_arc']]
        save(BASE/f'results/{name}-correspondences.json',clean(corr))
        with (BASE/f'results/{name}-errors.csv').open('w') as f:
            fields=['observation','index','error_px','tangent_px','normal_px','strong','status','stable_across_gap_penalties','observed','predicted'];w=csv.DictWriter(f,fields,extrasaction='ignore',lineterminator='\n');w.writeheader();w.writerows(rr)
        with (BASE/f'results/{name}-groups.csv').open('w') as f:
            fields=[k for k in groups[0] if k not in ['examples','all_quality']];w=csv.DictWriter(f,fields,extrasaction='ignore',lineterminator='\n');w.writeheader();w.writerows(groups)
        viewer={k:v for k,v in doc.items() if k not in ['positions','physical']};viewer['positions']=core;
        numpath=BASE/f'results/{name}-numerical.json'
        if numpath.exists():
            checks={b['index']:b for b in read(numpath)['checks']}
            for b in core:b['sampling_check']=checks[b['index']]
        viewer['physical']={k:v for k,v in doc['physical'].items() if k!='witnesses'};viewer['correspondences']=corr;viewer['material']=mat;viewer['supports']=supports;models.append(viewer)
    ranked.sort(key=lambda r:r['score'],reverse=True);save(BASE/'results/problem-intervals.json',clean(dict(policy='Screening priority, not accuracy: summed normalized RMS/radius, adjacent-group RMS change/radius, signed slope per50/radius, curvature/.04, halfpixel change/2px, unassigned-lobe fraction, colored omission/.2, paper/.1, penetration per10 addresses, ambiguity fraction and sparse-evidence flag. Raw values retained; correlated components are not probabilities.',intervals=ranked)))
    save(BASE/'results/starting-red-diagnosis.json',clean(red))
    # Single prespecified diagnostic: spread same quintic transition from4 to24.
    # Same parameters and origin; do not substitute into delivered geometry.
    ctl=Extended('primary',splice=(4.,24.));primary=Extended('primary');select=(ctl.indices>=-20)&(ctl.indices<=110);rad=ctl.query_radius+3;lo=np.floor(np.minimum(ctl.pc[select].min(0),primary.pc[select].min(0))-rad).astype(int);hi=np.ceil(np.maximum(ctl.pc[select].max(0),primary.pc[select].max(0))+rad).astype(int);ras=raster(ctl,[*lo,*hi]);bs={b['index']:b for b in records(ctl,ras)};cert=physical(ctl)
    rows=[]
    for q in models[0]['correspondences']['records']:
        k=q['index']
        if k is None or not -20<=k<=100:continue
        h=bs[k]['reflection'];rows.append(dict(observation=q['observation'],index=k,strong=q['strong'],primary_error=q['error_px'],control_error=float(np.linalg.norm(np.array(h['centroid'])-q['observed'])) if h else None,primary_curvature=float(primary.curvature[np.searchsorted(primary.indices,k)]),control_curvature=float(ctl.curvature[np.searchsorted(ctl.indices,k)]),center_change_px=float(np.linalg.norm(ctl.pc[np.searchsorted(ctl.indices,k)]-primary.pc[np.searchsorted(primary.indices,k)]))))
    save(BASE/'results/transition-control.json',clean(dict(rule='Evaluation-only quintic4→24 instead of4→12 radius units; no fitting or correspondence rematching. No control adopted.',records=rows,early_penetration_checks=[q for q in cert['penetration_checks'] if any(0<=k<=100 for k in q['pair'])],early_primary_penetration_checks=[q for q in models[0]['physical']['penetration_checks'] if any(0<=k<=100 for k in q['pair'])])))
    data=dict(models=models,observations=read(BASE/'evidence/observations.json')['observations'],reference=Reference().points[::5].tolist(),range=[FIRST,LAST],anchor=[1499.36,271.20],red=red,problems=ranked,questions=['Which independent bead dimensions/orientation measurements could constrain starting material mismatch?','Is the photographed trace the physical axis near the splice and bends?','Which neighboring reflections can be assigned independently to test phase and pitch without rematching?'])
    (REVIEW/'data.js').write_text('const DATA='+json.dumps(clean(data),separators=(',',':'))+';\n');save(BASE/'results/diagnosis-cost.json',dict(seconds=time.monotonic()-start))
if __name__=='__main__':main()
