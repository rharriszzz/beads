"""Robust positional assignment with explicit missing costs and secondary checks."""
import time
import numpy as np
from scipy.optimize import linear_sum_assignment
from photo2.r301.model import Local, predict
from photo2.r298.geometry import envelope, bead_extents

def rho(d2):
    # Smooth bounded influence, approximately squared below 12px.
    return 576*d2/(576+d2)

def assignment(pred,rows,section,blocked=(),detail=False):
    center=np.array(section['center']);t=np.array(section['tangent']);n=np.array([-t[1],t[0]])
    pp=[p for p in pred if abs((np.array(p['point'])-center)@t)<section.get('halfspan',52)+16 and abs((np.array(p['point'])-center)@n)<80 and p['owner'] not in blocked]
    m=len(rows);q=len(pp);weights=np.array([r['weight'] for r in rows]);xy=np.array([r['point'] for r in rows]).reshape(-1,2)
    d2=np.sum((xy[:,None]-np.array([p['point'] for p in pp]).reshape(-1,2)[None])**2,axis=-1)
    cost=weights[:,None]*rho(d2);miss=weights*400
    for i,r in enumerate(rows):
        if r.get('known_owner') is not None:
            cost[i,[j for j,p in enumerate(pp) if p['owner']!=r['known_owner']]]=1e8
    # Every predicted bead pays 4px^2 if unused; missed predictions remain explicit.
    # A second component can share a bead, but costs 64 and must be <=12px from
    # its first component. Thus multiple observed components are not forced beads.
    matrix=np.c_[cost-4,cost+64,np.full((m,m),1e9)]
    if m:matrix[np.arange(m),2*q+np.arange(m)]=miss
    for _ in range(m+1):
        rr,cc=linear_sum_assignment(matrix)
        violations=[]
        for j in range(q):
            ix=rr[(cc==j)|(cc==j+q)]
            if len(ix)==2 and np.linalg.norm(xy[ix[0]]-xy[ix[1]])>12:violations.append(j+q)
        if not violations:break
        matrix[:,violations]=1e9
    total=float(matrix[rr,cc].sum()+4*q);out=[];owners=[]
    for i,j in zip(rr,cc):
        match=j<2*q;k=j%q if match else None;p=pp[k] if match else None
        if match:owners.append(p['owner'])
        order=np.argsort(cost[i],kind='stable')[:3] if q else []
        alternatives=[dict(owner=pp[a]['owner'],index=pp[a]['index'],point=pp[a]['point'],cost=float(cost[i,a]),distance=float(np.sqrt(d2[i,a]))) for a in order]
        out.append(dict(id=rows[i]['id'],color=rows[i]['color'],split=rows[i]['split'],weight=rows[i]['weight'],observed=rows[i]['point'],owner=p['owner'] if match else None,index=p['index'] if match else None,predicted=p['point'] if match else None,residual=(np.array(p['point'])-xy[i]).tolist() if match else None,error=float(np.sqrt(d2[i,k])) if match else None,cost=float(cost[i,k]+(64 if j>=q else 0)) if match else float(miss[i]),shared_component=bool(match and j>=q),alternatives=alternatives))
    return dict(loss=total/max(weights.sum(),1),records=out,used=owners,unmatched=sum(r['owner'] is None for r in out),missed_predictions=q-len(set(owners)),prediction_count=q)

def secondary(scene,s,resolution):
    cues=s.get('cues',{});xy=np.array(cues.get('xy',[])).reshape(-1,2)
    # Low-resolution body proxy only during exploration. Accurate candidates use
    # the unchanged implicit first-hit kernel, including holes and all guards.
    if len(xy):
        keep=~np.array(cues.get('withheld',[False]*len(xy)),bool);xy=xy[keep]
        if resolution:
            tr=scene.trace(xy);owner=tr['owner']
        else:
            delta=xy[:,None]-scene.pc[None];a=np.sum(delta**2,axis=2);owner=np.argmin(a,axis=1);owner[np.min(a,axis=1)>(scene.scale*.82)**2]=-1
        paper=np.array(cues['paper'],bool)[keep];color=np.array(cues['color'])[keep];colored=color>0
        paper_error=float(np.mean(owner[paper]>=0)) if paper.any() else 0
        material_error=float(np.mean(owner[colored]<0)) if colored.any() else 0
    else:paper_error=material_error=0
    poly=scene.polygons();profiles=s.get('profiles',[]);dimensions=s.get('bead_dimensions',[])
    en=envelope(scene,profiles,poly) if profiles else np.empty((0,2))
    width=float(np.mean(abs(en-np.array([r['bounds'] for r in profiles])))) if profiles else 0
    bd=bead_extents(scene,dimensions,poly) if dimensions else np.empty((0,2))
    dim=float(np.mean(abs(bd-np.array([r['extent_px'] for r in dimensions])))) if dimensions else 0
    sep=[]
    if resolution:
        for r in s.get('separators',[]):
            own=scene.trace(r['xy'])['owner'];changes=np.flatnonzero(own[:-1]!=own[1:])+.5
            sep.append(float(min(abs(changes-r['valley_sample']))*r['representative_distance']/96) if len(changes) else 24.)
    serr=float(np.mean(sep)) if sep else 0
    return dict(loss=30*paper_error+12*material_error+.12*min(dim,20)**2+.12*min(width,20)**2+.15*min(serr,20)**2,paper=paper_error,material_missing=material_error,dimension_mae=dim,edge_mae=width,separator_mae=serr,profiles=len(profiles),dimensions=len(dimensions),separators=len(sep))

def evaluate(v,s,hand,resolution=0,detail=False,secondary_weight=1):
    timing={};start=time.perf_counter();scene=Local(v,s,hand);timing['geometry']=time.perf_counter()-start
    if 'halfspan' in s:
        station=(scene.project(scene.line)-np.array(s['center']))@np.array(s['tangent'])
        local_positions=int(np.sum(abs(station)<=s['halfspan']))
    else:local_positions=25
    start=time.perf_counter();cert=scene.certify(iterations=25 if resolution==0 else 90,witnesses=detail);timing['contact']=time.perf_counter()-start
    if not cert['certified']:
        return dict(loss=1000+100*max(0,-cert['minimum_gap_units']),feasible=False,reason='No separating-plane certificate (not proof of collision)',contact=cert,timing=timing)
    start=time.perf_counter();pred,diag=predict(scene,s,resolution);timing['specular']=time.perf_counter()-start
    start=time.perf_counter();train=assignment(pred,[r for r in s['observations'] if r['split']=='train'],s);timing['assignment']=time.perf_counter()-start
    start=time.perf_counter();sec=secondary(scene,s,resolution);timing['secondary']=time.perf_counter()-start
    out=dict(loss=train['loss']+secondary_weight*sec['loss'],feasible=True,local_positions=local_positions,reflection_loss=train['loss'],secondary=sec,contact=cert,timing=timing,train_unmatched=train['unmatched'])
    if detail:
        # Training owners locked out of withheld assignment; hidden predictions
        # cannot be reclaimed by a withheld feature to inflate apparent success.
        held=assignment(pred,[r for r in s['observations'] if r['split']=='withheld'],s,blocked=train['used'])
        out.update(train=train,withheld=held,predictions=pred,diagnostic=diag,polygons=scene.polygons().tolist(),indices=scene.indices.tolist(),centers=scene.centers.tolist(),projected_centers=scene.pc.tolist(),parameters=dict(scene.p),hand=hand)
    return out
