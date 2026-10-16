"""Frozen photographic catalog, global ordered correspondences and drift diagnostics."""
import csv,json,time
import numpy as np
from scipy.spatial import cKDTree
from PIL import Image,ImageOps
from photo2.r297.common import save,sha,utc
from photo2.r302.experiment import clean
from .model import *

def observations(primary):
    ref=Reference();old=read(ROOT/'photo2/r299/evidence/measurements.json.gz');screen=read(ROOT/'photo2/r299/evidence/visual-screen.json')['ambiguous']
    rows=[];raw=[];origin=primary['registration']['reference_arc_origin'];core=[b for b in primary['positions'] if b['displayed']];lo=core[0]['photo_arc'];hi=core[-1]['photo_arc']
    for r in old['observations']:
        xy=r.get('centroid') or r['historical_peak'];pr=ref.project([xy]);arc=float(pr['arc'][0]-origin);arc=arc+ref.length if arc < -1000 else arc
        if not lo<=arc<=hi or pr['distance'][0]>85:continue
        strong=bool(r['eligible'] and r['id'] not in screen)
        quality='strong localized' if strong else 'possible merged / broad' if r.get('area_px2',0)>90 else 'weak / uncertain' if r.get('historical_specular_candidate') else 'diffuse / optical type uncertain'
        rows.append(dict(id=r['id'],point=xy,peak=r.get('peak',r['historical_peak']),arc=arc,color=r['color'],quality=quality,strong=strong,uncertainty_px=r.get('uncertainty_px'),source=r['source'],aliases=[],duplicate=False));raw.append(r)
    for r in old['historical_r257']:
        xy=r['xy'];pr=ref.project([xy]);arc=float(pr['arc'][0]-origin);arc=arc+ref.length if arc < -1000 else arc
        if not lo<=arc<=hi or pr['distance'][0]>85:continue
        distances=np.linalg.norm(np.array([q['point'] for q in rows])-xy,axis=1);near=int(np.argmin(distances)) if len(distances) else -1
        duplicate=bool(near>=0 and distances[near]<4)
        if duplicate:rows[near]['aliases'].append(dict(id=r['id'],point=xy,distance_px=float(distances[near]),source='R257'))
        else:rows.append(dict(id=r['id'],point=xy,peak=xy,arc=arc,color='black',quality='weak / uncertain (R257 only)',strong=False,uncertainty_px=r.get('uncertainty_px'),source='photo2/review/r257/observations.json',aliases=[],duplicate=False))
        raw.append(dict(R257_original=r))
    rows.sort(key=lambda r:r['arc']);save(BASE/'evidence/observations-original.json.gz',raw)
    save(BASE/'evidence/observations.json',dict(observations=rows,policy='All R299/R276 catalog entries in the primary geographic interval; R257 originals retained, within4px cross-references not counted twice. No old physical owner IDs transferred. Original coordinates unchanged. No new detection: existing coverage sufficient for inspection, incomplete for counting.',sources={p:sha(ROOT/p) for p in ['beads-photo-2.jpg','photo2/r299/evidence/measurements.json.gz','photo2/review/r257/observations.json','photo2/review/r276/observations.json','photo2/r303/results/fit-freeze.json','photo2/r282/results/centerline.json']}))
    return rows

def align(obs,pred,penalty):
    """Single ordered sequence edit path. Gaps explicit, never panel-local matching."""
    n,m=len(obs),len(pred);cost=np.full((n+1,m+1),np.inf);op=np.zeros((n+1,m+1),np.int8);cost[0,0]=0
    cost[:,0]=np.arange(n+1)*penalty**2;cost[0,:]=np.arange(m+1)*penalty**2;op[1:,0]=1;op[0,1:]=2
    for i in range(1,n+1):
        for j in range(1,m+1):
            dist=float(np.linalg.norm(np.array(obs[i-1]['point'])-pred[j-1]['reflection']['centroid']))
            match=dist**2 if dist<=70 else np.inf
            vals=[cost[i-1,j-1]+match,cost[i-1,j]+penalty**2,cost[i,j-1]+penalty**2];k=int(np.argmin(vals));cost[i,j]=vals[k];op[i,j]=k
    i,j=n,m;mapping={};path=[]
    while i or j:
        k=op[i,j]
        if k==0:mapping[obs[i-1]['id']]=pred[j-1]['index'];path.append(dict(observation=obs[i-1]['id'],index=pred[j-1]['index'],operation='pair'));i-=1;j-=1
        elif k==1:path.append(dict(observation=obs[i-1]['id'],index=None,operation='unmatched_observation'));i-=1
        else:path.append(dict(observation=None,index=pred[j-1]['index'],operation='unmatched_prediction'));j-=1
    return mapping,list(reversed(path))

def correspondences(model,obs):
    # Keep every saved S1 identity conditional on R303; impose it on every path.
    native=read(ROOT/f"photo2/r303/results/native-{model['source']['name']}.json.gz")['result']
    anchors={r['id']:r['index'] for r in native['train']['records']+native['withheld']['records'] if r.get('index') is not None}
    pred=[b for b in model['positions'] if b['displayed'] and b['reflection']];by={b['index']:b for b in pred};oid={r['id']:r for r in obs}
    pinned=sorted([(oid[k]['arc'],k,v) for k,v in anchors.items() if k in oid and v in by])
    # Photographic order can reverse neighboring addresses across the helix.
    # Keep all historical S1 pairs, including this reversal for hand-minus.
    paths={};maps={}
    for penalty in [12,24,48]:
        mapping={k:v for _,k,v in pinned};path=[];limits=[(-np.inf,None,FIRST-1),(pinned[0][0],None,min(v for _,_,v in pinned)),(pinned[-1][0],None,max(v for _,_,v in pinned)),(np.inf,None,LAST+1)]
        for segment,(a,b) in enumerate(zip(limits,limits[1:])):
            if segment==1:
                path.extend(dict(observation=k,index=v,operation='R303_anchor') for _,k,v in pinned)
                path.extend(dict(observation=r['id'],index=None,operation='unmatched_S1_observation') for r in obs if a[0]<=r['arc']<=b[0] and r['id'] not in anchors)
                path.extend(dict(observation=None,index=r['index'],operation='unmatched_S1_prediction') for r in pred if a[2]<=r['index']<=b[2] and r['index'] not in anchors.values())
                continue
            oo=[r for r in obs if a[0]<r['arc']<b[0]];pp=[r for r in pred if a[2]<r['index']<b[2]]
            mm,pa=align(oo,pp,penalty);mapping.update(mm);path+=pa
            if b[1]:path.append(dict(observation=b[1],index=b[2],operation='R303_anchor'))
        maps[penalty]=mapping;paths[str(penalty)]=path
    records=[];base=maps[24];ref=Reference()
    for o in obs:
        k=base.get(o['id']);p=by.get(k);dist=[(float(np.linalg.norm(np.array(o['point'])-b['reflection']['centroid'])),b) for b in pred]
        dist.sort(key=lambda z:z[0]);alternatives=[dict(index=b['index'],point=b['reflection']['centroid'],distance_px=d) for d,b in dist[:4]]
        status='unmatched';error=tangent=normal=None;res=None
        stable=all(maps[q].get(o['id'])==k for q in maps)
        if p:
            res=np.array(p['reflection']['centroid'])-o['point'];error=float(np.linalg.norm(res));proj=ref.project([o['point']]);arc=proj['arc'][0];a=np.array([np.interp(arc-1,ref.arc,ref.points[:,j]) for j in range(2)]);b=np.array([np.interp(arc+1,ref.arc,ref.points[:,j]) for j in range(2)]);t=unit(b-a);tangent=float(res@t);normal=float(res@[-t[1],t[0]])
            competitor=min((d for d,b in dist if b['index']!=k),default=1e6)
            confident=o['strong'] and stable and error<=8 and competitor-error>=8
            status='confident conditional' if confident else 'ambiguous'
        records.append(dict(observation=o['id'],observed=o['point'],quality=o['quality'],strong=o['strong'],uncertainty_px=o['uncertainty_px'],index=k,index_separation=k,photo_arc=o['arc'],predicted=p['reflection']['centroid'] if p else None,error_px=error,tangent_px=tangent,normal_px=normal,residual=res.tolist() if res is not None else None,status=status,R303_anchor=o['id'] in anchors,stable_across_gap_penalties=stable,penalty_owners={str(q):maps[q].get(o['id']) for q in maps},alternatives=alternatives))
    # No-gap ordinal control: freeze sequence rank at last S1 anchor, then never
    # skip an observation or predicted reflection. Incomplete catalog => NOT truth.
    last=pinned[-1];oo=[r for r in obs if r['arc']>last[0]];pp=[r for r in pred if r['index']>last[2]];ordinal=[]
    for o,p in zip(oo,pp):
        delta=np.array(p['reflection']['centroid'])-o['point'];ordinal.append(dict(observation=o['id'],index=p['index'],photo_arc=o['arc'],error_px=float(np.linalg.norm(delta)),aligned_index=base.get(o['id']),index_discrepancy=None if o['id'] not in base else base[o['id']]-p['index']))
    return dict(records=records,paths=paths,ordinal_control=ordinal,policy='Global order-preserving sequence alignment outside S1, all saved S1 pairs pinned (including local projected-order reversals); unanchored S1 observations remain unmatched; one-to-one pairs and explicit gaps. Cost squared centroid distance; each skipped observation/prediction costs24^2 px^2, with12/48 sensitivity. No geometry correction. All weak observations remain; only strong rows enter main trends. Nearest alternatives are diagnostic only, never substitute for the global path. Confident conditional means strong, <=8px, >=8px advantage over all competitors, same owner across all penalties; NOT verified bead identity. Ordinal control uses no skips after S1 and is confounded by catalog incompleteness.')

def summary(rr):
    ok=[r for r in rr if r['error_px'] is not None];d=[r['error_px'] for r in ok]
    return dict(n=len(ok),rms=float(np.sqrt(np.mean(np.square(d)))) if d else None,median=float(np.median(d)) if d else None,tangent_mean=float(np.mean([r['tangent_px'] for r in ok])) if ok else None,normal_mean=float(np.mean([r['normal_px'] for r in ok])) if ok else None)

def material(scene,model):
    cues=np.load(ROOT/'photo2/r296/evidence/cues.npz');xy=cues['xy'];pr=scene.ref.project(xy);arc=pr['arc']-scene.photo_origin;arc=np.where(arc < -1000,arc+scene.ref.length,arc)
    core=[b for b in model['positions'] if b['displayed']];lo,hi=core[0]['photo_arc'],core[-1]['photo_arc'];keep=(arc>=lo)&(arc<=hi)&(pr['distance']<85)
    xy=xy[keep];tr=scene.camera(xy);records=[]
    for q,a,col,pap,own in zip(xy,arc[keep],cues['color'][keep],cues['paper'][keep],tr['owner']):
        idx=float(np.interp(a,scene.photo_arc,scene.indices));records.append(dict(point=q.tolist(),index=idx,paper=bool(pap),colored=bool(col>0),predicted_material=bool(own>=0)))
    profiles=[]
    for r in read(ROOT/'photo2/r298/evidence/measurements.json')['envelope']:
        a=r['arc']-scene.photo_origin;a=a+scene.ref.length if a < -1000 else a
        if not lo<=a<=hi:continue
        c=np.array(r['point']);n=np.array(r['normal']);t=np.array(r['tangent']);bounds=[]
        for lane in [-12,-6,0,6,12]:
            u=np.arange(-110,111,.5);xy=c+lane*t+u[:,None]*n;own=scene.camera(xy)['owner'];hit=u[own>=0];bounds.append([float(hit.min()),float(hit.max())] if len(hit) else [None,None])
        valid=[b for b in bounds if b[0] is not None];p=np.median(valid,axis=0) if valid else None
        profiles.append(dict(id=r['id'],point=r['point'],normal=r['normal'],index=float(np.interp(a,scene.photo_arc,scene.indices)),observed=r['bounds'],predicted=p.tolist() if p is not None else None,edge_mae=float(np.mean(abs(p-r['bounds']))) if p is not None else None,midline_displacement=float(np.mean(p)-np.mean(r['bounds'])) if p is not None else None,eligible=r['eligible'],uncertainty_px=r['uncertainty_px']))
    return dict(cues=records,envelope_profiles=profiles,meaning='Frozen image-only paper/color samples and uncertain R298 photographic envelope proxies. Actual native first-hit union used; neither masks nor profile midpoints are certified bead ownership or exact rope centerline.')

def main():
    start=time.monotonic();primary=read(BASE/'results/primary.json.gz');obs=observations(primary);models=[]
    for name in FAMILIES:
        m=read(BASE/f'results/{name}.json.gz');scene=Extended(name);corr=correspondences(m,obs);mat=material(scene,m);rows=[];rr=corr['records'];core=[b for b in m['positions'] if b['displayed']]
        for lo in range(FIRST,LAST+1,50):
            hi=min(lo+49,LAST);beads=[b for b in core if lo<=b['index']<=hi];aa=[b['photo_arc'] for b in beads];r=[r for r in rr if (lo<=r['index']<=hi if r['index'] is not None else aa[0]<=r['photo_arc']<=aa[-1])];strong=[q for q in r if q['strong']];cues=[q for q in mat['cues'] if lo<=q['index']<hi+1];paper=[q for q in cues if q['paper']];color=[q for q in cues if q['colored']];env=[q for q in mat['envelope_profiles'] if lo<=q['index']<hi+1 and q['eligible'] and q['edge_mae'] is not None];used={q['index'] for q in rr if q['index'] is not None}
            rows.append(dict(first=lo,last=hi,modeled=len(beads),visible=sum(b['visible_area_px2']>0 for b in beads),observations=len(r),strong_observations=len(strong),confident=sum(q['status']=='confident conditional' for q in r),ambiguous=sum(q['status']=='ambiguous' for q in r),unmatched_observations=sum(q['index'] is None for q in r),unmatched_predictions=sum(b['reflection'] is not None and b['index'] not in used for b in beads),occluded=sum(b['visible_area_px2']==0 for b in beads),physical_failure=sum(bool(b['uncertified_pairs']) for b in beads),no_predicted_reflection=sum(b['reflection'] is None and b['visible_area_px2']>0 for b in beads),**summary(strong),all_quality=summary(r),paper_samples=len(paper),paper_occupation=float(np.mean([q['predicted_material'] for q in paper])) if paper else None,colored_samples=len(color),colored_omission=float(np.mean([not q['predicted_material'] for q in color])) if color else None,envelope_profiles=len(env),envelope_mae=float(np.mean([q['edge_mae'] for q in env])) if env else None,axis_reference_departure_max=float(max(abs(b['axis_departure_px']) for b in beads))))
        rolling=[]
        for k in range(FIRST,LAST+1,5):
            lo=np.interp(k-25,scene.indices,scene.photo_arc);hi=np.interp(k+25,scene.indices,scene.photo_arc);r=[q for q in rr if q['strong'] and q['index'] is not None and k-25<=q['index']<=k+25]
            rolling.append(dict(index=k,photo_arc=float(np.interp(k,scene.indices,scene.photo_arc)),**summary(r),missing=sum(q['index'] is None for q in r)))
        strong=[q for q in rr if q['strong'] and q['error_px'] is not None];trends={}
        for field in ['error_px','tangent_px','normal_px']:
            for axis in ['index','photo_arc']:
                x=np.array([q[axis] for q in strong]);y=np.array([q[field] for q in strong]);trends[field+'-per-'+axis]=float(np.polyfit(x,y,1)[0]) if len(x)>1 else None
        corr.update(groups=rows,rolling=rolling,trends=trends,summary_strong=summary(strong));save(BASE/f'results/{name}-correspondences.json',clean(corr));save(BASE/f'results/{name}-material.json.gz',clean(mat))
        with (BASE/f'results/{name}-groups.csv').open('w') as f:
            fields=[k for k in rows[0] if k!='all_quality'];w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n',extrasaction='ignore');w.writeheader();w.writerows(rows)
        # Boundary vectors remain in complete machine-readable prediction records.
        viewer={k:v for k,v in m.items() if k not in ['physical','positions']};viewer['physical']={k:v for k,v in m['physical'].items() if k!='witnesses'};viewer['positions']=[{k:v for k,v in b.items() if True} for b in core];
        numerical_path=BASE/f'results/{name}-numerical.json'
        if numerical_path.exists():
            sampling={b['index']:b for b in read(numerical_path)['checks']}
            for b in viewer['positions']:
                b['sampling_check']=sampling.get(b['index'])
                b['visibility']='visible' if b['visible_area_px2'] else 'fully_occluded_at_native_resolution' if b['isolated_area_within_raster_px2'] else 'no_native_projected_samples'
        viewer['correspondences']=corr;viewer['material']=dict(envelope_profiles=mat['envelope_profiles']);models.append(viewer)
        print(name,corr['summary_strong'],trends,flush=True)
    ref=Reference();data=dict(models=models,observations=obs,reference=ref.points[::5].tolist(),range=[FIRST,LAST],anchor=[1499.36,271.20],note='Conditional forward hypotheses. See complete extended physical checks for each family. Global gaps and competing owners remain visible; small rematched errors cannot prove stable physical indexing.')
    (REVIEW/'data.js').write_text('const DATA='+json.dumps(clean(data),separators=(',',':'))+';\n')
    # Exact native decoded pixels; no recoloring, resizing or ICC transformation.
    image=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');image.save(REVIEW/'photo.png')
    save(BASE/'results/analysis-cost.json',dict(seconds=time.monotonic()-start,utc=utc()))

if __name__=='__main__':main()
