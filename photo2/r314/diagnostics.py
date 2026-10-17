"""Post-selection fixed-core attribution, isolated surfaces and optical components."""
from copy import copy,deepcopy
import time
import numpy as np
from scipy.spatial import cKDTree
from photo2.r297.common import ROOT,read,save,photo,pixels,digest
from photo2.r306.evidence import load
from photo2.r297.geometry import reference
from photo2.r299.forward import shade,light_params,highlight
from photo2.r307.fast import grid
from photo2.bead_detection.brightness_r270 import linearize
from photo2.r295.geometry import AXES
from .run import OUT,EV,engine,make,evaluated
from .geometry import paper
from .bright import components,freeze_epoch
from .correspondence import evaluate_fixed as evaluate

EARLY=['C-1497-0271','C-1477-0290','R282-1459-0316','R282-1536-0239','R282-1537-0308','C-1559-0252']

def isolated(s,j,xy):
    iso=copy(s);iso.n=1;iso.centers=s.centers[j:j+1];iso.pc=s.pc[j:j+1];iso.tree=cKDTree(iso.pc);iso.g={k:v[j:j+1] for k,v in s.g.items()};iso.indices=s.indices[j:j+1]
    return iso.trace(xy)

def geometric():
    began=time.monotonic();data,_,_=load();eng=engine();m=eng.m;doc=eng.doc;models=[read(p) for p in sorted((OUT/'models').glob('*.json.gz'))];base=next(r for r in models if r['name']=='R306-2405');basecores={c['id']:c for split in ['development','comparison','buffer'] for c in base[split]['cores']};output=[];ref=reference()
    for row in models:
        s=make(row['parameters'],data);raster=np.load(OUT/'models'/f'{row["name"]}.npz');oo=raster['owner'];uu=raster['unknown'];regions=[]
        for c in doc['regions']:
            ix=np.flatnonzero(m['core'].ravel()==c['label']);xy=m['xy'][ix];owner=oo[ix];valid=~uu[ix];ids,n=np.unique(owner[(owner>=0)&valid],return_counts=True);j=int(ids[n.argmax()]) if len(n) else None;k=basecores[c['id']]['index'];oldj=np.flatnonzero(s.indices==k) if k is not None else []
            a=float(ref.project([c['point']])['arc'][0]);arc=((a-data['arc0'])*data['direction']+ref.length/2)%ref.length-ref.length/2
            r=dict(id=c['id'],point=c['point'],arc=arc,split=c['split'],index=int(s.indices[j]) if j is not None else None,modal=float(n.max()/len(ix)) if len(n) else 0.,fixed_R306_index=k,fixed_R306_fraction=float(np.mean((owner==oldj[0])&valid)) if len(oldj) else 0.,changed_owner=j is not None and int(s.indices[j])!=k,alternatives=[dict(index=int(s.indices[k]),visible_fraction=float(v/len(ix))) for k,v in sorted(zip(ids,n),key=lambda z:-z[1])[:6]])
            if c['id'] in EARLY:
                candidates=s.tree.query_ball_point(c['point'],s.query_radius+12);iso=[]
                for jj in candidates:
                    tr=isolated(s,jj,xy);f=float(np.mean((tr['owner']>=0)&~tr['unknown']));full=float(np.mean((owner==jj)&valid));iso.append(dict(index=int(s.indices[jj]),isolated_fraction=f,full_visible_fraction=full,occluded_fraction=max(0,f-full),unknown=int(tr['unknown'].sum())))
                r['isolated']=sorted(iso,key=lambda z:-z['isolated_fraction'])[:8]
            regions.append(r)
        # Complete physical target visibility ledger, no target body dropped for lack of data.
        ix=np.flatnonzero((s.indices>=-100)&(s.indices<=99));xy=grid(s,1.,ix);tr=s.trace(xy);seen=np.bincount(tr['owner'][tr['owner']>=0],minlength=s.n);target=[]
        for j in ix:target.append(dict(index=int(s.indices[j]),visible_pixels=int(seen[j]),isolated_pixels=int(tr['isolated_counts'][j]),measured_core_ids=[r['id'] for r in regions if r['index']==int(s.indices[j])],center=s.centers[j].tolist(),projected=s.pc[j].tolist()))
        np.savez_compressed(OUT/'target-rasters'/f'{row["name"]}.npz',xy=xy,owner=tr['owner'],unknown=tr['unknown']) if (OUT/'target-rasters').exists() else None
        support=paper(s);turn=s.n/s.p['winding'] if s.closed else s.p['turn'];groups=np.floor(s.indices/turn).astype(int);z=np.tile([0.,0.,1.],(s.n,1));clear=s.centers[:,2]-s.support(z,s.g[AXES[0]])-support['plane_z'];low=[float(clear[groups==g].min()) for g in np.unique(groups) if np.sum(groups==g)>=5];support['per_turn_lowest_clearance']=dict(median=float(np.median(low)),p95=float(np.percentile(low,95)),maximum=max(low))
        output.append(dict(name=row['name'],regions=regions,target=target,full_target_camera_rays=len(xy),full_target_unknown=int(tr['unknown'].sum()),context_bodies=s.n-200,changed_core_owners=sum(r['changed_owner'] for r in regions),supporting_plane=support));print('DIAG',row['name'],'full target rays',len(xy),flush=True)
    save(OUT/'geometry-diagnostics.json.gz',dict(models=output,seconds=time.monotonic()-began,policy='Independent frozen photo cores. Isolated/full surfaces separate placement/shape from occlusion, with conditional competing owners. Target ledger includes every -100..99, hidden and unmeasured. No physical center or index chain recovered.'))
    # Actual interventions distinguish bore fill from external profile and rigid orientation.
    controls=[]
    for name in ['R306-2405','R313-focused-1','R313-focused-3']:
        row=next(r for r in models if r['name']==name);p=deepcopy(row['parameters']);p.update(exterior=True,edge=(1-p.get('hole',.14))/2*p.get('rounding',.8),face=p.get('rounding',.8))
        for bore in [.08,.25]:
            q=dict(p,bore=bore);r,s,tr=evaluated(q,data,eng,True,1.);r.update(parent=name,intervention='same_external_envelope_simple_bore',bore=bore);controls.append(r)
    bestrows=[r for r in models if r['name'].startswith('R314')];best=min(bestrows,key=lambda r:r['development']['search_merit']);parent=next(r for r in models if r['name']==best['parent'])
    for label,keys in [('revert_profile',['exterior','edge','face','bore','hole','rounding','axial']),('revert_orientation',['tilt','trajectory_mix']),('revert_placement_camera',['phase','s0','minor','scale','elevation','roll','perspective','local_spacing','local_phase'])]:
        p=deepcopy(best['parameters'])
        for k in keys:
            if k in parent['parameters']:p[k]=deepcopy(parent['parameters'][k])
            else:p.pop(k,None)
        r,s,tr=evaluated(p,data,eng,True,1.);r.update(parent=best['name'],intervention=label);controls.append(r)
    save(OUT/'structural-controls.json.gz',dict(cases=controls,policy='Fixed selected-model group reversions and unchanged external-envelope bore controls. Contact-invalid variants cannot identify a photographic causal preference. Not new optimization.'))

def optical():
    began=time.monotonic();data,_,_=load();m=dict(np.load(EV/'maps.npz'));_,rgb,meta=photo();lum=linearize(rgb.astype(float)/255.)@np.array([.2126,.7152,.0722]);records=read(ROOT/'photo2/r289/results/phase2-observations.json.gz')['records'];local=[];x0,y0=m['origin'];h,w=m['shape']
    for r in records:
        peak=r['absolute_local_maximum'];x,y=np.rint(peak).astype(int)
        if not (x0<=x<x0+w and y0<=y<y0+h and m['roi'][y-y0,x-x0]):continue
        xx0=max(0,x-16);yy0=max(0,y-16);xx1=min(lum.shape[1],x+17);yy1=min(lum.shape[0],y+17);yy,xx=np.mgrid[yy0:yy1,xx0:xx1];xy=np.c_[xx.ravel(),yy.ravel()];bg=r['brightness']['annulus_background_Y'];v=np.maximum(lum[yy,xx].ravel()-bg,0);contrast=max(lum[y,x]-bg,1e-12);variations=[]
        for f in [.4,.5,.6]:
            cs=components(xy,v,fraction=f*contrast/max(v.max(),1e-12),floor=1e-9)
            for c in cs:c['contains_original_peak']=bool(any(np.array_equal(p,peak) for p in c['pixels']));c['window_censored']=bool(any(p[0] in [xx0,xx1-1] or p[1] in [yy0,yy1-1] for p in c['pixels']))
            variations.append(dict(relative_to_original_peak_fraction=f,components=cs))
        local.append(dict(id=r['observation_id'],peak=peak,centroid=r['measured_point'],original=r,threshold_variants=variations,reliable_correspondence=False,reliably_localized=r['threshold_sensitivity_px']<=1.5,specular_status='ambiguous',uncertainty=dict(threshold_sensitivity_px=r['threshold_sensitivity_px'],interpretation='Numerical sensitivity, not calibrated precision')))
    # All owner/lobe correspondences remain unverified. Empty eligible cohort is explicit, not a zero error.
    epoch=freeze_epoch(local,{},'no-geometric-readiness');save(OUT/'bright-epoch.json.gz',epoch);save(OUT/'bright-readiness.json',evaluate(epoch,[],geometry_passed=False))
    names=['R306-2405','R313-focused-3'];summary=read(OUT/'summary.json');new=[r for r in summary['rows'] if r['name'].startswith('R314') and r['split']=='development'];names.append(min(new,key=lambda r:max(r['vector']['worst']/3,r['vector']['seam']/10,r['vector']['external']/3))['name']);outputs=[]
    for name in names:
        row=read(OUT/'models'/f'{name}.json.gz');s=make(row['parameters'],data);owners=np.flatnonzero((s.indices>=-100)&(s.indices<=99));inv=s.p.get('light_inverse',0);light=light_params([s.p['light_az'],s.p['light_el'],s.p['roughness']]+([1/inv] if inv else []),'finite' if inv else 'directional',s.centers.mean(0));variants=[]
        for step in [1.,.5]:
            # Half-pixel diagnostic restricted to physical -20..20, declared independently of error.
            use=owners if step==1 else np.flatnonzero((s.indices>=-20)&(s.indices<=20));xy=grid(s,step,use);tr=s.camera(xy);sh=shade(s,tr,light);pred=[]
            for j in use:
                ix=np.flatnonzero(tr['owner']==j)
                for f in [.4,.5,.6]:
                    cs=components(xy[ix],sh['intensity'][ix],step,f)
                    for c in cs:
                        z=int(ix[np.argmin(np.linalg.norm(xy[ix]-c['peak'],axis=1))]);surface_local=(tr['points'][z]-s.centers[j])@np.array([s.g[k][j] for k in AXES]).T/s.radius;c.update(index=int(s.indices[j]),peak_local_radius=surface_local.tolist())
                    old=highlight(xy[ix],sh['intensity'][ix],step) if f==.5 else None
                    from .local_lobes import maxima
                    pred.append(dict(index=int(s.indices[j]),threshold=f,components=cs,legacy_combined_centroid=old['centroid'] if old else None,all_local_maxima=maxima(xy[ix],sh['intensity'][ix],step) if f==.5 else []))
            variants.append(dict(step=step,physical_indices=s.indices[use].tolist(),rays=len(xy),unknown_camera=int(tr['unknown'].sum()),unknown_shadow=sh['unknown_shadow_pairs'],predictions=pred))
        from .correspondence import track
        native=[dict(c,lobe=c['component']) for p in variants[0]['predictions'] if p['threshold']==.5 and -20<=p['index']<=20 for c in p['components']];half=[c for p in variants[1]['predictions'] if p['threshold']==.5 for c in p['components']];tracking=track(native,half);nb={(r['index'],r['lobe']):r for r in native}
        for r in tracking['predictions']:
            b=nb[r['index'],r['lobe']];r['peak_shift_px']=float(np.linalg.norm(np.array(r['peak'])-b['peak']));r['centroid_shift_px']=float(np.linalg.norm(np.array(r['centroid'])-b['centroid']))
        correspondences=[]
        for o in local:
            pts=pixels({'runs':o['original']['bright_patch_runs']});tr=s.trace(pts);ix=tr['owner'];ids,n=np.unique(ix[(ix>=0)&~tr['unknown']],return_counts=True)
            correspondences.append(dict(id=o['id'],alternatives=[dict(index=int(s.indices[j]),patch_coverage=float(c/len(pts)),in_target=bool(-100<=s.indices[j]<=99)) for j,c in sorted(zip(ids,n),key=lambda z:-z[1]) if c/len(pts)>=.1],missing_surface_fraction=float(np.mean(ix<0)),physical_correspondence_verified=False,rule='Visible surface overlap with unchanged observed patch, not optical residual minimization. Color and physical adjacency remain unresolved.'))
        outputs.append(dict(name=name,variants=variants,correspondences=correspondences,resolution_tracking=tracking));print('OPTICS',name,flush=True)
    save(OUT/'connected-optics.json.gz',dict(models=outputs,observations=len(local),seconds=time.monotonic()-began,lighting_fitted=False,primary_maximum_established=False,policy='Measurement diagnostic only. Three fixed geometries, common inherited illumination, individual lobes and ties. Native all200 and predetermined halfpixel -20..20. No geometry benefit from reassignment and no optical fit.'))

if __name__=='__main__':
    import sys
    if sys.argv[1]=='geometry':(OUT/'target-rasters').mkdir(exist_ok=True);geometric()
    else:optical()
