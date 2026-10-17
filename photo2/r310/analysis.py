"""Unchanged native models: exhaustive support ownership, outward prefixes, controls."""
from pathlib import Path
import copy,time
from types import MethodType
from photo2.r307.fast import Chain as Fast
import numpy as np
from scipy.ndimage import binary_erosion,distance_transform_edt
from scipy.spatial import cKDTree
from scipy.optimize import linear_sum_assignment
from photo2.r297.common import ROOT,read,save,sha,utc
from photo2.r297.geometry import reference
from photo2.r306.evidence import load
from photo2.r309.geometry import Chain
from photo2.r307.delivery import model_scene as historical_scene
from photo2.r305.diagnose import isolated

BASE=ROOT/'photo2/r310';OUT=BASE/'results';D=36.878
MODELS={'R306-2405':('photo2/r306/results/campaign/exports','primary'), 'R309-2733':('photo2/r309/results/campaign/exports','primary'),'R297-2337':('photo2/r307/results/campaign/exports','R297')}
ANCHOR='C-1497-0271'

def stats(v,total=None):
    values=[x for x in v if x is not None and np.isfinite(x)];a=np.array(values);n=len(a)
    return dict(n=n,missing=(len(v) if total is None else total)-n,rms_px=float(np.sqrt(np.mean(a*a))) if n else None,p95_px=float(np.percentile(a,95)) if n else None,maximum_px=float(a.max()) if n else None,**{k:float(f(a)/D) if n else None for k,f in [('rms_D',lambda x:np.sqrt(np.mean(x*x))),('p95_D',lambda x:np.percentile(x,95)),('maximum_D',np.max)]})

def wrap(a,length):return (np.asarray(a)+length/2)%length-length/2

def models():
    data,m,obs=load()
    for name,(folder,stem) in MODELS.items():
        path=ROOT/folder;doc=read(path/f'{stem}.json.gz');scene=historical_scene(doc,data) if name.startswith('R297') else Chain(doc['parameters'],data)
        yield name,doc,scene,np.load(path/f'{stem}-raster.npz')

def points(r):return np.array([(x,y) for y,a,b in r['pixels']['runs'] for x in range(a,b+1)],int)

def evidence():
    data,m,obs=load();ref=reference();old={r['record_id']:r for r in read(ROOT/'photo2/r283/results/phase1.json.gz')['records']};rows=[]
    for r in data['rows']:
        if r['kind']!='region' or r['reflection']:continue
        q=copy.deepcopy(r);q['distance_px']=float(wrap((ref.project([r['point']])['arc'][0]-data['arc0'])*data['direction'],ref.length));q['distance_D']=q['distance_px']/D;q['status']=old.get(r['id'],{}).get('status','unspecified');q['historical_ownership_alternatives']=old.get(r['id'],{}).get('ownership_alternatives',[]);q['physical_identity_verified']=False;rows.append(q)
    return data,m,obs,rows

def analyze():
    began=time.monotonic();data,m,obs,supports=evidence();ref=reference();out=[];view=[]
    save(BASE/'evidence/observations.json.gz',dict(D_px=D,reference=ANCHOR,supports=supports,reflections=obs,neighbors=data['edges'],maker_evidence='User identifies the red reference; source support is automatic high-class, not a maker-certified complete contour. R294 reports no human-accepted full region in its starting window.',no_verified_physical_neighbor_chain=True))
    for name,doc,scene,raster in models():
        address=raster['address'];unknown=raster['unknown'];bs={b['index']:b for b in doc['positions']};pc=np.array([b['projected_center'] for b in doc['positions']]);indices=np.array(list(bs));rows=[]
        # Saved exact native pixels; no geometry or correspondence re-fit.
        cor=doc.get('guided_correspondences',doc['correspondences'])['records'];rc={r.get('observation',r.get('id')):r for r in cor}
        for r in supports:
            pts=points(r);lo=pts.min(0)-3;hi=pts.max(0)+4;mask=np.zeros((hi[1]-lo[1],hi[0]-lo[0]),bool);mask[pts[:,1]-lo[1],pts[:,0]-lo[0]]=True
            coremask=binary_erosion(mask,iterations=2);yy,xx=np.where(coremask);core=np.c_[xx+lo[0],yy+lo[1]]
            if len(core)<20:core=pts;eroded=False
            else:eroded=True
            own=address[pts[:,1],pts[:,0]];valid=~unknown[pts[:,1],pts[:,0]];ks,ns=np.unique(own[valid&(own!=-32768)],return_counts=True);order=np.argsort(-ns);ks=ks[order];ns=ns[order];k=int(ks[0]) if len(ks) else None
            if k is None:k=int(indices[np.argmin(np.linalg.norm(pc-r['point'],axis=1))])
            alternatives=[]
            for kk,n in zip(ks[:5],ns[:5]):
                b=bs[int(kk)];alternatives.append(dict(index=int(kk),fraction=float(n/len(pts)),core_fraction=float(np.mean((address[core[:,1],core[:,0]]==kk)&~unknown[core[:,1],core[:,0]])),center=b['projected_center'],reflection=b['reflection']['centroid'] if b['reflection'] else None))
            owncore=address[core[:,1],core[:,0]];vc=~unknown[core[:,1],core[:,0]];fraction=float(np.mean(own==k));core_fraction=float(np.mean((owncore==k)&vc))
            # Distance of each positive core pixel to this full visible owner, not to its center.
            b=bs[k];center=np.array(b['projected_center']);radius=scene.query_radius+4;low=np.maximum([0,0],np.floor(center-radius)).astype(int);high=np.minimum([2540,3182],np.ceil(center+radius)).astype(int);y,x=np.where((address[low[1]:high[1],low[0]:high[0]]==k)&~unknown[low[1]:high[1],low[0]:high[0]])
            visible=np.c_[x+low[0],y+low[1]];dist=cKDTree(visible).query(core)[0] if len(visible) else np.full(len(core),np.nan);dist[~vc]=np.nan
            isolated_detail=[]
            if abs(r['distance_px'])<210:
                for alt in alternatives[:3]:
                    single=isolated(scene,alt['index']);single.trace=MethodType(Fast.trace,single);tr=single.trace(pts);hits=(tr['owner']>=0)&~tr['unknown'];hitsfull=own==alt['index'];isolated_detail.append(dict(index=alt['index'],isolated_fraction=float(hits.mean()),visible_fraction=float(hitsfull.mean()),hidden_by_neighbors_fraction=float(np.mean(hits&~hitsfull)),outside_isolated_fraction=float(np.mean(~hits&~tr['unknown'])),unknown_fraction=float(tr['unknown'].mean())))
            rr=rc.get(r['id']);observed=next((o for o in obs if o['id']==r['id']),None)
            row=dict(id=r['id'],point=r['point'],distance_px=r['distance_px'],distance_D=r['distance_D'],color=r['color'],status=r['status'],accepted=r['accepted'],pixels=len(pts),core_pixels=len(core),eroded=eroded,index=k,coherence=fraction,core_coherence=core_fraction,alternatives=alternatives,unknown=float((~valid).mean()),outside_union=float(np.mean((own==-32768)&valid)),core_outside_owner=stats(dist.tolist()),core_distances_px=[float(z) if np.isfinite(z) else None for z in dist],best_core_coherence=max([a['core_fraction'] for a in alternatives],default=0.),core_far_fraction=float(np.nanmean(dist>.15*D)),isolated=isolated_detail,observed_interior_centroid=r['point'],modeled_center=bs[k]['projected_center'],predicted_visible_centroid=visible.mean(0).tolist() if len(visible) else None,reflection_record=rr,observed_reflection=observed,physical_identity_verified=False,possible_merged_interior=True)
            row['suspected']=bool(fraction<.8)
            row['material_inconsistency']=bool(row['best_core_coherence']<.65 and row['core_far_fraction']>=.2 and len(core)>=40)
            row['strong_support_conflict']=bool(core_fraction<.65 and len(core)>=40)
            row['positioning_failure_proven']=False
            rows.append(row)
        anchor=next(r for r in rows if r['id']==ANCHOR);origin=anchor['index']
        for r in rows:r['index_from_reference']=int(wrap(r['index']-origin,scene.n))
        rr=[]
        for r in cor:
            q=copy.deepcopy(r);pt=q['observed'];q['distance_px']=float(wrap((ref.project([pt])['arc'][0]-data['arc0'])*data['direction'],ref.length));q['distance_D']=q['distance_px']/D;q['index_from_reference']=int(wrap(q['index']-origin,scene.n)) if q['index'] is not None else None;q['error_D']=q['error_px']/D if q['error_px'] is not None else None;rr.append(q)
        sequences=[];prefix=[];findings={}
        for sign in [-1,1]:
            ordered=sorted([r for r in rows if sign*r['distance_px']>1e-6],key=lambda r:abs(r['distance_px']))
            suspect=next((r for r in ordered if r['suspected']),None);first=next((r for r in ordered if r['material_inconsistency']),None)
            # Corroboration from another separate region within 80 photographic px; not physical neighbor proof.
            sustained=next((r for r in ordered if r['material_inconsistency'] and any(q['id']!=r['id'] and q['material_inconsistency'] and 0<sign*(q['distance_px']-r['distance_px'])<80 for q in ordered)),None)
            good=[r for r in [anchor]+ordered if (first is None or abs(r['distance_px'])<abs(first['distance_px'])) and r['core_coherence']>=.9]
            findings[str(sign)]=dict(first_suspected=suspect,first_demonstrated_material_inconsistency=first,first_corroborated_material_inconsistency=sustained,last_preceding_high_coverage=good[-1] if good else None,first_physical_positioning_failure=None,last_verified_physical_correspondence=None,policy='Order by original photographic geographic distance, never nearest reflection or old conditional label. No established physical identity chain.')
            for n in [10,20,40,80,160,320]:
                ks=[origin+sign*j for j in range(n+1)];ks=[int(indices[0]+(k-indices[0])%scene.n) for k in ks];chosen=[b for b in doc['positions'] if b['index'] in ks];reflections=[q for q in rr if q['index'] in ks and q['strong']];ss=[q for q in rows if q['index'] in ks]
                prefix.append(dict(direction=sign,length=n,indices=ks,projected_centers=[b['projected_center'] for b in chosen],reflections=stats([q['error_px'] for q in reflections]),uncertain_reflection_owners=len(reflections),supports=len(ss),mean_coherence=float(np.mean([q['coherence'] for q in ss])) if ss else None,material_inconsistencies=[q['id'] for q in ss if q['material_inconsistency']],unsupported_bodies=len(set(ks)-{q['index'] for q in ss}),hidden_bodies=sum(b['visible_area_px2']==0 for b in chosen)))
            for j in range(321):
                k=int(indices[0]+(origin+sign*j-indices[0])%scene.n);b=bs[k];sequences.append(dict(direction=sign,step=j,index=k,point=b['projected_center'],visible_area_px2=b['visible_area_px2'],supports=[q['id'] for q in rows if q['index']==k],physical_identity='unverified',neighbors={str(d):int(indices[0]+(k+d-indices[0])%scene.n) for d in [-7,-6,-1,1,6,7]}))
        # Reassignment-only one-to-one control, same fixed geometry; does not fit any prefix.
        near=sorted([r for r in rows if abs(r['distance_px'])<210],key=lambda r:r['distance_px']);owners=sorted({a['index'] for r in near for a in r['alternatives']});cost=np.ones((len(near),len(owners)+len(near)))
        for i,r in enumerate(near):
            for a in r['alternatives']:cost[i,owners.index(a['index'])]=1-a['fraction']
        ai,aj=linear_sum_assignment(cost);assignment=[dict(id=near[i]['id'],modal=near[i]['index'],assigned=owners[j] if j<len(owners) else None,coverage=float(1-cost[i,j]),modal_coverage=near[i]['coherence']) for i,j in zip(ai,aj)]
        result=dict(model=name,count=scene.n,anchor=anchor,findings=findings,supports=rows,reflections=rr,prefixes=prefix,sequences=sequences,reassignment_only=assignment,parameters=doc['parameters'],physical= {k:v for k,v in doc['physical'].items() if k not in ['witnesses','index_pairs']},parameter_sha256=sha(ROOT/MODELS[name][0]/f'{MODELS[name][1]}.json.gz'))
        save(OUT/f'{name}-partA.json.gz',result);out.append(dict(model=name,anchor=anchor,findings=findings,prefixes=prefix));view.append(dict(name=name,parameters=doc['parameters'],positions=doc['positions'],supports=rows,reflections=rr,anchor=origin,geometric_axis_xy=doc.get('geometric_axis_xy',[b['axis_xy'] for b in doc['positions']])))
        print(name,'anchor',origin,round(anchor['coherence'],3),flush=True)
        for sign,f in findings.items():print(sign,[(k, (v['id'],round(v['distance_px'],1),v['index'],round(v['core_coherence'],3),round(v['core_far_fraction'],3)) if isinstance(v,dict) and 'id' in v else v) for k,v in f.items() if k.startswith(('first','last_preceding'))],flush=True)
    save(OUT/'partA.json.gz',dict(models=out,completed_utc=utc(),seconds=time.monotonic()-began,physical_failure_not_identified=True,D_px=D,criterion='Suspected: <80% positive interior on any single owner. Demonstrated material mismatch: <65% two-pixel-eroded core owned coherently and >=20% core >0.15D from modal full visible body, >=40 core pixels. Corroborated: second qualifying distinct support within80px ahead. These are support-geometry inconsistencies, not verified bead-center displacements or proof that an automatic region is one bead. Thresholds have 0.1/0.2D and 60/70% controls in verification. No reliable physical center coordinates or physical +1/+6/+7 annotations exist.'))
    save(OUT/'viewer-data.json.gz',dict(models=view,reference=ref.points.tolist(),supports=supports,D=D,anchor=data['anchor']['measured_photo_location']))
if __name__=='__main__':analyze()
