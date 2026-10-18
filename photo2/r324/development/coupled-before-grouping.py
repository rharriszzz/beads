"""Frozen topology/visibility ledger, then bounded graph-conditioned R321 fit.
The photograph tracker is never imported or modified by physical diagnosis.
"""
import json,time,hashlib,resource,copy,argparse
from pathlib import Path
from collections import Counter
import numpy as np
from scipy.spatial import cKDTree
from scipy.stats import spearmanr
from photo2.r297.common import ROOT,read,save,digest
from photo2.r306.evidence import load
from photo2.r319.local_model import Chain as R319
from photo2.r321.model import Chain as R321,corrected
from photo2.r321.packing import derive,curvature
from photo2.r314.geometry import contacts
from photo2.r315.model import refined_trace
from photo2.r307.fast import grid
from photo2.r318.optics import make_light
from photo2.r318.detect import principal
from photo2.r299.forward import shade
OUT=ROOT/'photo2/r324/results'

def frozen_models(data):
    old=read(ROOT/'photo2/r319/results/best-full.json.gz');p=old['parameters']
    yield 'R319-best',R319(p,data),read(ROOT/'photo2/r319/results/best-full-positions.json.gz')
    for name in ['geometry-best','photo-sized-rescue']:
        d=read(ROOT/f'photo2/r321/results/{name}-model.json.gz');yield 'R321-'+name,R321(d['parameters'],data),d['positions']

def support_ledger(s,obs,pixels):
    bounds=np.r_[0,np.cumsum([len(pixels[o['id']]) for o in obs])];xy=np.concatenate([pixels[o['id']] for o in obs]);tr=refined_trace(s,xy)
    fractions=np.zeros((len(obs),s.n));rows=[]
    for i,(o,a,b) in enumerate(zip(obs,bounds[:-1],bounds[1:])):
        own=tr['owner'][a:b];valid=~tr['unknown'][a:b];js,nn=np.unique(own[valid&(own>=0)],return_counts=True);fractions[i,js]=nn/(b-a)
        alternatives=sorted([dict(index=int(s.indices[j]),fraction=float(n/(b-a))) for j,n in zip(js,nn)],key=lambda r:-r['fraction'])
        rows.append(dict(id=o['id'],xy=o['xy'],color=o['color'],pixels=int(b-a),unknown=int((~valid).sum()),owners=alternatives,modal_index=alternatives[0]['index'] if alternatives else None,modal_fraction=alternatives[0]['fraction'] if alternatives else 0))
    return rows,fractions,len(xy)

def correspond(s,nodes,obs,frac):
    oi={o['id']:i for i,o in enumerate(obs)};ns=[n for n in nodes if n['component'] is not None];ii=np.array([oi[n['id']] for n in ns]);xy=np.array([n['xy'] for n in ns]);ab=np.array([n['relative_ab'] for n in ns]);origins=s.indices;closed=s.p['topology']=='closed';options=[]
    for name,weights in [('A',[7,6]),('B',[6,7]),('reverse_A',[-7,-6]),('reverse_B',[-6,-7])]:
        rel=ab@weights;idx=origins[:,None]+rel[None,:];valid=(idx>=s.indices[0])&(idx<=s.indices[-1]);jj=(idx-s.indices[0])%s.n
        d=np.linalg.norm(s.pc[jj]-xy[None,:,:],axis=2);f=frac[ii[None,:],jj]
        # Support ownership primary; capped center distance is a weak tie breaker.
        losses=1-f+.001*np.minimum(d,100)
        if not closed:losses[~valid]=10
        costs=losses.mean(1)
        for k in np.argsort(costs)[:4]:options.append(dict(interpretation=name,weights=weights,origin=int(origins[k]),loss=float(costs[k]),mean_support_fraction=float(f[k].mean()),center_distance_rms_px=float(np.sqrt(np.mean(d[k]**2))),mapping={n['id']:int(s.indices[j]) for n,j in zip(ns,jj[k])},relative_indices=rel.tolist()))
    options.sort(key=lambda r:r['loss']);return options

def optical(s,targets,photo_reflections,mapping,scope_label,certificate=None):
    t=time.perf_counter();tm={};cert=certificate or contacts(s,seconds=.5);tm['full_chain_contact']=time.perf_counter()-t
    if not cert['certified']:return dict(feasible=False,contact=cert,times=tm),None
    t=time.perf_counter();js=np.flatnonzero(np.isin(s.indices,targets));xy=grid(s,1.,js);tm['grid']=time.perf_counter()-t;t=time.perf_counter();tr=s.camera(xy);tm['camera']=time.perf_counter()-t;t=time.perf_counter();sh=shade(s,tr,make_light(s.p,s));tm['shadow_light']=time.perf_counter()-t;t=time.perf_counter();pred={}
    for j in js:
        hit=tr['owner']==j;h=principal(xy[hit],sh['intensity'][hit])
        if h:pred[int(s.indices[j])]=h
    rows=[]
    for o in photo_reflections:
        idx=mapping[o['observation']];h=pred.get(idx);point=h['point'] if h else None
        rows.append(dict(id=o['id'],observation=o['observation'],index=idx,observed=o['point'],predicted=point,error_px=float(np.linalg.norm(np.array(point)-o['point'])) if point is not None else None))
    ds=[r['error_px'] for r in rows if r['error_px'] is not None];missing=len(rows)-len(ds);tm['reflection_measurement']=time.perf_counter()-t
    result=dict(feasible=True,scope=scope_label,target_addresses=list(map(int,targets)),all_bodies=s.n,camera_rays=len(xy),unknown_camera=int(tr['unknown'].sum()),unknown_shadow_pairs=sh['unknown_shadow_pairs'],contact={k:v for k,v in cert.items() if k!='witnesses'},times=tm,total_seconds=sum(tm.values()),rows=rows,missing=missing,maximum_is_infinite=bool(missing),emax_px=max(ds) if ds and not missing else None,rms_finite_px=float(np.sqrt(np.mean(np.square(ds)))) if ds else None,predictions={str(k):v for k,v in pred.items()})
    return result,dict(xy=xy,owner=tr['owner'],intensity=sh['intensity'])

def main():
    began=time.perf_counter();data=load()[0];g=read(OUT/'graph.json');obs=g['observations'];nodes={n['id']:n for n in g['intersections']};pixels={r['id']:np.array(r['pixels_xy']) for r in read(OUT/'observation-pixels.json')};oi={o['id']:i for i,o in enumerate(obs)}
    # Local seed is selected photographically, before any model is constructed.
    seed=[n for n in nodes.values() if 1180<=n['xy'][0]<=1505 and 200<n['xy'][1]<390 and n['region_priority']=='interior' and n['component'] is not None]
    assert len({n['component'] for n in seed})==1
    auto=read(ROOT/'photo2/r318/results/observations.json.gz')['observations'];auto=[a for a in auto if a['eligible']];axy=np.array([a['point'] for a in auto]);atree=cKDTree(axy)
    refl=[]
    for n in nodes.values():
        dist,j=atree.query(n['xy'])
        if dist<=8 and n['component'] is not None:
            a=auto[j];refl.append(dict(id=a['id'],observation=n['id'],point=a['point'],color=a['color'],pixels=a['component']['pixels'],threshold_shift=a['method_threshold_shift_px']['point'],association_distance=float(dist)))
    counts=Counter(a['id'] for a in refl);refl=[a for a in refl if counts[a['id']]==1]
    save(OUT/'fit-evidence.json',dict(seed_observations=[n['id'] for n in seed],reflections=refl,policy='Seed x1180..1505,y200..390 interior photo graph. Reflection centroids use original R318 photo-only extraction; within8px unique association, no predicted highlight selection. Bright supports are never bead centers.'))
    models=[]
    for label,s,saved in frozen_models(data):
        t=time.perf_counter();assert np.allclose(s.pc,saved['projected'],atol=1e-8);assert np.allclose(s.centers,saved['centers'],atol=1e-8)
        rows,frac,rays=support_ledger(s,obs,pixels);supporttime=time.perf_counter()-t;t=time.perf_counter();seed_options=correspond(s,seed,obs,frac);seedbest=seed_options[0];components=[]
        for comp in g['graph']['components']:
            ns=[nodes[i] for i in comp['nodes']];opts=correspond(s,ns,obs,frac);best=opts[0];components.append(dict(component=comp['id'],observations=len(ns),options=opts,best=best))
        map_time=time.perf_counter()-t;rl={r['id']:r for r in rows};edge_rows=[]
        for e in g['graph']['edges']:
            a,b=rl[e['source']],rl[e['target']];cc=nodes[e['source']]['component'];hyp=components[cc]['best'];expected=int(np.dot(e['delta_ab'],hyp['weights']));actual=None
            if a['modal_index'] is not None and b['modal_index'] is not None:
                actual=b['modal_index']-a['modal_index']
                if s.p['topology']=='closed':actual=int((actual+s.n//2)%s.n-s.n//2)
            strong=min(a['modal_fraction'],b['modal_fraction'])>=.6
            edge_rows.append(dict(source=e['source'],target=e['target'],component=cc,family=e['family'],expected_delta=expected,modal_delta=actual,both_modal_fraction_over_60pct=strong,status='agrees' if strong and actual==expected else 'disagrees' if strong else 'unresolved surface correspondence'))
        # A seed-origin chart is extended without refitting origin; each diagnostic
        # remains a conditional test of this global gauge, not a new identity truth.
        compid=seed[0]['component'];component=[nodes[i] for i in g['graph']['components'][compid]['nodes']];weights=seedbest['weights'];origin=seedbest['origin'];mapping={n['id']:int(s.indices[(origin+np.dot(n['relative_ab'],weights)-s.indices[0])%s.n]) for n in component}
        diagnostic=[]
        for n in sorted(component,key=lambda n:n['xy'][0]):
            idx=mapping[n['id']];j=int(np.flatnonzero(s.indices==idx)[0]);r=rl[n['id']];modal=r['modal_index'];drift=None if modal is None else modal-idx
            if drift is not None and s.p['topology']=='closed':drift=int((drift+s.n//2)%s.n-s.n//2)
            diagnostic.append(dict(id=n['id'],xy=n['xy'],color=n['color'],index=idx,modal_index=modal,modal_fraction=r['modal_fraction'],assigned_support_fraction=float(frac[oi[n['id']],j]),projected_center=s.pc[j].tolist(),anchor_center_distance_px=float(np.linalg.norm(s.pc[j]-n['xy'])),index_discrepancy=drift,curvature=float(abs(curvature(s)[j]))))
        strong=[r for r in diagnostic if r['modal_fraction']>=.6];rho=spearmanr([r['curvature'] for r in strong],[abs(r['index_discrepancy']) for r in strong]) if len(strong)>3 else None
        refs=[r for r in refl if r['observation'] in seedbest['mapping']];targets=sorted(seedbest['mapping'].values());native,raster=optical(s,targets,refs,seedbest['mapping'],'frozen seed')
        if raster:np.savez_compressed(OUT/(label+'-raster.npz'),**raster)
        record=dict(label=label,parameters=s.p,positions=dict(indices=s.indices.tolist(),projected=s.pc.tolist()),topology=s.p['topology'],frozen_positions_exact=True,seed_options=seed_options,components=components,support=rows,edge_comparison=edge_rows,seed_origin_extension=diagnostic,curvature_index_error_spearman=float(rho.statistic) if rho is not None and np.isfinite(rho.statistic) else None,curvature_test_n=len(strong),native=native,timings=dict(support_rays=supporttime,discrete_correspondence=map_time),support_rays=rays,first_seed_origin_disagreement=next((r for r in diagnostic if r['id'] in seedbest['mapping'] and r['modal_fraction']>=.6 and r['index_discrepancy']!=0),None),policy='Modal surface owners are model predictions. Graph weights enforce topology algebraically; only independent first-hit ownership comparison tests that mapping. Center/bright-anchor distance is not center measurement error.')
        save(OUT/(label+'-frozen.json.gz'),record);models.append(dict(label=label,seed_options=seed_options[:4],edges=dict(Counter(r['status'] for r in edge_rows)),first_disagreement=record['first_seed_origin_disagreement'],native_summary={k:v for k,v in native.items() if k not in ['predictions','rows','target_addresses']},timings=record['timings'],curvature_index_error_spearman=record['curvature_index_error_spearman']))
        print('FROZEN',label,models[-1]['edges'],native.get('emax_px'),native.get('missing'),flush=True)
    save(OUT/'frozen-summary.json',dict(models=models,seconds=time.perf_counter()-began,peak_rss_mb=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,all_models_compared_before_refitting=True))
if __name__=='__main__':main()
