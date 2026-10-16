"""Native predictions and diagnoses after optimizer stop; no fitting or rematching."""
import csv,json,time
import numpy as np
from PIL import Image
from .experiment import *
from photo2.r298.geometry import outlines,bead_extents,envelope


def runs(xy):
    xy=np.asarray(xy,int);out=[]
    for y in np.unique(xy[:,1]) if len(xy) else []:
        xx=np.unique(xy[xy[:,1]==y,0]);cuts=np.r_[0,np.flatnonzero(np.diff(xx)>1)+1,len(xx)]
        out.extend([[int(y),int(xx[a]),int(xx[b-1])] for a,b in zip(cuts[:-1],cuts[1:])])
    return out


def native_geometry(scene,geo,m):
    ij=np.concatenate([r['samples_xy'] for r in m['envelope']]);tr=scene.trace(ij);o=tr['owner'].reshape(len(m['envelope']),9,191);bounds=[]
    for r in o:
        vals=[]
        for line in r:
            hits=np.flatnonzero(line>=0);vals.append((hits[[0,-1]]-95).tolist() if len(hits) else [0.,0.])
        bounds.append(np.median(vals,axis=0))
    bd=bead_extents(scene,m['beads']);out=deepcopy(geo);out['polygon_metrics']=out['metrics'];out['metrics']={sp:metrics((bd,np.array(bounds)),m,sp) for sp in ['development','comparison']};out['native_profile_unknown']=int(tr['unknown'].sum());out['envelope']=np.array(bounds).tolist();out['bead_extents']=bd.tolist();out['physical']=contact(scene,exact=True)
    return out


def diagnose(scene,data,rows,assign,light,records):
    observed=np.array([r['peak'] for r in rows]);tr=scene.camera(observed);shade_at=shade(scene,tr,light,order=5);l=np.array(light['direction']);out=[]
    for i,(r,a,record) in enumerate(zip(rows,assign,records)):
        k=a['owner'];mask=data['owner']==k;points=data['xy'][mask];dist=float(np.linalg.norm(points-observed[i],axis=1).min()) if len(points) else None;actual=int(tr['owner'][i]);normal=tr['normal'][i];viewer=tr['viewer'][i];implied=2*np.dot(normal,viewer)*normal-viewer if actual>=0 else None
        direction=unit(np.array(light['position'])-tr['points'][i]) if light['kind']=='finite' else l
        angle=float(np.degrees(np.arccos(np.clip(np.dot(implied,direction),-1,1)))) if implied is not None else None
        out.append(dict(id=r['id'],surface_distance_lower_bound_px=dist,first_hit_at_observed_peak=int(scene.indices[actual]) if actual>=0 else None,first_hit_agrees_with_frozen_owner=actual==k and k>=0,unknown_observed_ray=bool(tr['unknown'][i]),implied_light_direction=implied.tolist() if implied is not None else None,implied_light_mismatch_deg=angle,predicted_specular_at_observed_peak=float(shade_at['intensity'][i]),meaning='Implied light is conditional on current first hit and mirror assumption; not an independently measured lamp. Distance uses native samples and has ~0.71px grid tolerance.'))
    return out


def main():
    start=time.monotonic();rows=observations();inputs,_=load_evidence();m=measurements();fixed=read(BASE/'results/fixed-complete.json')['models'];selection=read(BASE/'results/selection.json');hist=read(BASE/'results/joint-history.json.gz');models=[];public=[];convergence=[]
    for name in fixed:models.append(read(BASE/f'results/{name}.json.gz'))
    for ident in selection['native_exports']:
        r=hist[ident];models.append(dict(name=f'joint-{ident}',baseline=49,parameters=r['parameters'],fit=r['fit'],geometry=r['geometry']))
    for source in models:
        name=source['name'];p=source['parameters'];s=Surface(p,inputs);assign=read(BASE/f"evidence/ownership-{source['baseline']}.json")['assignments'];allowners=sorted(set(a['owner'] for a in assign)|set(b['owner'] for a in assign for b in a['alternatives']));data=grids(s,allowners,1.);light=source['fit']['light'];order=5
        rr,diag=evaluate(s,data,light,rows,assign,1.,order,True);sh=shade(s,data,light,order=order);altpred={k:highlight(data['xy'][data['owner']==k],sh['intensity'][data['owner']==k],1.) for k in allowners if k>=0};footprints={str(k):runs(data['xy'][data['owner']==k]) for k in allowners if k>=0}
        for r,a in zip(rr,assign):
            r['alternatives']=[dict(**b,predicted=altpred.get(b['owner'])) for b in a['alternatives']];r['optimistic_alternative_peak_error_px']=min((float(np.linalg.norm(np.array(b['predicted']['peak'])-r['observed_peak'])) for b in r['alternatives'] if b['predicted']),default=None)
        diagnostics=diagnose(s,data,rows,assign,light,rr);geo=native_geometry(s,source['geometry'],m)
        result=dict(name=name,baseline=source['baseline'],parameters=p,light=light,records=rr,summary=summary(rr),shadow=diag,geometry=geo,diagnosis=diagnostics,positions=s.pc.tolist(),world_centers=s.centers.tolist(),indices=s.indices.tolist(),polygons=outlines(s).tolist(),visible_surfaces=footprints,normal_convention='Inverse transpose of exact R279 annulus under R298 axial/radial scaling; current camera eye and roll.',step=1.,angular_order=order,source_sha256=sha(BASE/f'results/{name}.json.gz') if name in fixed else sha(BASE/'results/joint-history.json.gz'))
        # Grid/quadrature control: predetermined every eighth observation, never
        # choose easy cases by residual. Peaks can jump between competing maxima.
        sample=list(range(0,len(rows),8));a=[assign[i] for i in sample];r=[rows[i] for i in sample];half=grids(s,[v['owner'] for v in a],.5);hr,_=evaluate(s,half,light,r,a,.5,9,False)
        for i,q in zip(sample,hr):
            z=rr[i];convergence.append(dict(model=name,id=z['id'],native_exists=z['exists'],half_exists=q['exists'],peak_change=float(np.linalg.norm(np.array(q['predicted']['peak'])-z['predicted']['peak'])) if q['exists'] and z['exists'] else None,centroid_change=float(np.linalg.norm(np.array(q['predicted']['centroid'])-z['predicted']['centroid'])) if q['exists'] and z['exists'] else None))
        save(BASE/f'results/native-{name}.json.gz',result)
        header=['id','color','split','trusted','exists','modeled_index','ownership_ambiguous','observed_peak_x','observed_peak_y','predicted_peak_x','predicted_peak_y','peak_dx','peak_dy','peak_error_px','peak_normalized_error','observed_centroid_x','observed_centroid_y','predicted_centroid_x','predicted_centroid_y','centroid_dx','centroid_dy','centroid_error_px','centroid_normalized_error','apparent_diameter_px','extent_area_error_px2','sigma_major_error_px','sigma_minor_error_px','orientation_error_deg','competing_indices']
        with (BASE/f'results/residuals-{name}.csv').open('w') as f:
            w=csv.DictWriter(f,fieldnames=header,lineterminator='\n');w.writeheader()
            for z in rr:
                row={key:z.get(key) for key in header if key in z};row.update(modeled_index=z['ownership']['index'],ownership_ambiguous=z['ownership']['ambiguous'],competing_indices=';'.join(str(a['index']) for a in z['ownership']['alternatives']))
                for kind in ['peak','centroid']:
                    for j,axis in enumerate(['x','y']):row[f'observed_{kind}_{axis}']=z[f'observed_{kind}'][j];row[f'predicted_{kind}_{axis}']=z['predicted'][kind][j] if z['exists'] else None;row[f'{kind}_d{axis}']=z[f'{kind}_residual'][j] if z['exists'] else None
                w.writerow(row)
        with (BASE/f'results/positions-{name}.csv').open('w') as f:
            w=csv.writer(f,lineterminator='\n');w.writerow(['conditional_index','x','y','z','image_x','image_y']);w.writerows([[int(k),*xyz,*uv] for k,xyz,uv in zip(s.indices,s.centers,s.pc)])
        small={k:v for k,v in result.items() if k not in ['world_centers','polygons','positions','indices']};small['geometry']=deepcopy(geo);small['geometry']['physical']={k:v for k,v in geo['physical'].items() if k not in ['witnesses','index_pairs','fallback']};small['geometry']['photographic']={sp:{k:v for k,v in o.items() if k not in ['assignments','separators']} for sp,o in geo['photographic'].items()};public.append(small)
        print('NATIVE',name,result['summary']['trusted'],flush=True)
    save(BASE/'results/convergence.json',convergence)
    summary_models=[dict(name=r['name'],summary=r['summary'],geometry=r['geometry'],light=r['light']) for r in public]
    save(BASE/'results/native-summary.json',summary_models)
    bundle=dict(observations=rows,models=public,selection=selection,default=f"joint-{selection['chosen']}",targets=dict(median=3,p90=5),historical=read(BASE/'evidence/historical.json'))
    (REVIEW/'data.js').write_text('const DATA='+json.dumps(bundle,separators=(',',':'),allow_nan=False)+';\n')
    save(BASE/'results/export-manifest.json',dict(models=[r['name'] for r in models],elapsed=time.monotonic()-start,files={str(p.relative_to(ROOT)):sha(p) for p in (BASE/'results').glob('native-*.json.gz')}))
if __name__=='__main__':main()
