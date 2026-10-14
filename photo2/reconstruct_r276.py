"""R276 integrated reconstruction. Additive experiment; all R275 inputs read-only.

Run: .venv/bin/python -m photo2.reconstruct_r276 --stage all
Physical generator indices are conditional addresses, never photographic identities.
"""
from __future__ import annotations
import argparse, copy, gzip, hashlib, json, time
from pathlib import Path
from types import SimpleNamespace
import numpy as np
from scipy.interpolate import CubicSpline
from scipy.integrate import cumulative_trapezoid
from scipy.optimize import linear_sum_assignment, minimize
from scipy.spatial import cKDTree
from PIL import Image, ImageDraw
from .bead_debugger.refit import BeadCurve
from .bead_debugger.surface import Scene, RADIUS, unit, moments, shade, highlight
from .bead_debugger.generate import ROOT, save, sha
from .bead_detection.brightness_r270 import color_managed_photo, linearize
from camera_r254 import Camera
from bead_placement import Rope

OUT=ROOT/'photo2/review/r276'
CACHE=ROOT/'photo2/output/r276'
VERSION='r276-integrated-1'
# Normal bending (4), longitudinal strain (4), twist (4), material origin,
# global phase, camera translation/elevation/roll/log-scale, shared light (3).
NAMES=['bend_s1_px','bend_c1_px','bend_s2_px','bend_c2_px',
       'strain_s1','strain_c1','strain_s2','strain_c2',
       'twist_s1_rad','twist_c1_rad','twist_s2_rad','twist_c2_rad',
       'material_shift_beads','phase_rad','camera_dx_px','camera_dy_px',
       'camera_elevation_delta_deg','camera_roll_delta_deg','camera_log_scale',
       'light_azimuth_deg','light_elevation_deg','roughness_deg']
LIMIT=np.array([8]*4+[.005]*4+[.06]*4+[1,.6,8,8,2,.4,.006,360,89,18.])
STEPS=np.array([2]*4+[.001]*4+[.018]*4+[.2,.14,2,2,.5,.1,.0015,15,8,2.])
DEFAULT=np.r_[np.zeros(19),-164.,75.,6.]


def basis(t):
    a=2*np.pi*np.asarray(t)
    return np.stack([np.sin(a),np.cos(a),np.sin(2*a),np.cos(2*a)],axis=-1)


def integral_strain(f,a):
    """Integral epsilon ds / L from 0 to f; f is physical reference arclength/L."""
    x=2*np.pi*np.asarray(f)
    return ((1-np.cos(x))*a[0]+np.sin(x)*a[1]+(1-np.cos(2*x))*a[2]/2+np.sin(2*x)*a[3]/2)/(2*np.pi)


class Model(BeadCurve):
    def __init__(self,base,p):
        self.base=base;self.p=np.asarray(p,float);c=copy.deepcopy(base)
        self.source=SimpleNamespace(nbeads=c['n'],nrows=c['turns'],helicity=c['h'])
        self.config=c;self.q=np.linspace(0,1,8193)
        bcurve=CubicSpline(np.linspace(0,1,len(c['knots'])+1),np.vstack([c['knots'],c['knots'][0]]),bc_type='periodic')
        speed=np.linalg.norm(bcurve(self.q,1),axis=1)
        arc=np.r_[0,cumulative_trapezoid(speed,self.q)];self.length=arc[-1];self.reference_arc=arc/self.length
        u=np.arange(len(c['knots']))/len(c['knots']);v=bcurve(u,1);v=unit(v);normal=np.c_[-v[:,1],v[:,0],np.zeros(len(u))]
        displacement=basis(np.interp(u,self.q,self.reference_arc))@p[:4]/c['camera']['scale']
        knots=np.asarray(c['knots'])+displacement[:,None]*normal
        curve=CubicSpline(np.r_[u,1.],np.vstack([knots,knots[0]]),bc_type='periodic')
        length=np.trapezoid(np.linalg.norm(curve(self.q,1),axis=1),self.q)
        # Fix length independently of redistribution. Scaling about curve mean
        # is an explicit small global component of bending, recorded below.
        center=np.mean(knots,axis=0);knots=center+(knots-center)*self.length/length
        self.length_scale=float(self.length/length)
        self.curve=CubicSpline(np.r_[u,1.],np.vstack([knots,knots[0]]),bc_type='periodic')
        arc=np.r_[0,cumulative_trapezoid(np.linalg.norm(self.curve(self.q,1),axis=1),self.q)]
        self.deformed_arc=arc/arc[-1]
        cv=copy.deepcopy(c['camera']);cv['tx']+=p[14];cv['ty']+=p[15];cv['elevation']+=p[16];cv['roll']+=p[17];cv['scale']*=np.exp(p[18])
        self.view=Camera(**cv);self.view.focal=c.get('focal',0);self.unscaled_length=self.length*self.view.scale

    def geometry(self,indices):
        ii=np.atleast_1d(indices).astype(float);t=ii/self.source.nbeads
        # Material shift is a single periodic origin, not local strain or twist.
        chart=(t+self.p[12]/self.source.nbeads)%1
        f=chart if self.config.get("uniform_material",False) else np.interp(chart,self.q,self.reference_arc)
        f=(f+integral_strain(f,self.p[4:8]))%1
        u=np.interp(f,self.deformed_arc,self.q)
        line=self.curve(u);tangent=unit(self.curve(u,1));normal=np.c_[-tangent[:,1],tangent[:,0],np.zeros(len(u))]
        angle=self.config['phase']+self.p[13]+self.source.helicity*2*np.pi*self.source.nrows*t
        angle+=basis(t)@(np.array(self.config.get('phase_harmonics',[0]*4))+self.p[8:12])
        for b in self.config.get('local',[]):
            x=((t-b['t']+.5)%1-.5)/b['width'];w=np.where(abs(x)<1,(1-x*x)**3,0)
            angle+=w*(b.get('phase',0)+b.get('winding',0)*x)
        radial=np.sin(angle)[:,None]*normal;radial[:,2]=np.cos(angle)
        return dict(indices=ii.astype(int),line=line,tangent=tangent,normal=normal,radial=radial,centers=line+self.config.get('rope_radius',4)*radial,outward=line+(self.config.get('rope_radius',4)+RADIUS)*radial,fraction=t)


def scene(base,p):
    s=Scene.__new__(Scene);s.config=base;s.model=Model(base,p);s.g=s.model.geometry(np.arange(base['n']))
    s.mid='R276';s.version=VERSION;s.centers=s.g['centers'];s.pc=s.model.view.project(s.centers);s.shadow_trees={};s.plane_z=-(base.get('rope_radius',4)+RADIUS)
    return s


def light(p):
    a,e=np.radians(p[19:21]);return dict(direction=[float(np.cos(e)*np.cos(a)),float(np.cos(e)*np.sin(a)),float(np.sin(e))],roughness_deg=float(p[21]),width_deg=0,height_deg=0,source_model='one shared directional distant source')


def pixels(runs):return np.array([[x,y] for y,x0,x1 in runs for x in range(x0,x1+1)],int).reshape(-1,2)


def stats(values):
    a=np.asarray(values,float)
    if not len(a):return dict(n=0,mean=None,rms=None,maximum=None,median=None,p90=None,p95=None)
    return dict(n=len(a),mean=float(a.mean()),rms=float(np.sqrt(np.mean(a*a))),maximum=float(a.max()),median=float(np.median(a)),p90=float(np.percentile(a,90)),p95=float(np.percentile(a,95)))


def observation_data(write=True):
    inv=json.loads((ROOT/'photo2/review/r275/inventory.json').read_text());beads={b['id']:b for b in inv['beads']}
    rgb,icc=color_managed_photo();lin=linearize(rgb/255.);lum=lin@np.array([.2126,.7152,.0722]);rows=[]
    for loc in inv['locations']:
        b=beads.get(loc['id']);point=loc['point'];xy=[point['x'],point['y']];region=pixels(b['region']['runs']) if b else np.empty((0,2),int)
        patch=pixels(loc['bright_patch']['runs']);pp=lum[patch[:,1],patch[:,0]] if len(patch) else np.array([])
        vals=lum[region[:,1],region[:,0]] if len(region) else np.array([])
        floor=float(np.percentile(vals,30)) if len(vals) else 0
        weights=np.maximum(pp-floor,1e-8);shape=moments(patch,weights)
        contrast=(point['luminance']-floor)/max(point['luminance'],1e-8)
        # This gate is fixed from photo evidence, never model residual/ownership.
        strong=bool(b and len(region)>=(12 if loc['color']=='black' else 60))
        saturation=(rgb[region[:,1],region[:,0]].max(1).astype(float)-rgb[region[:,1],region[:,0]].min(1))/np.maximum(rgb[region[:,1],region[:,0]].max(1),1) if len(region) else np.array([0.])
        desaturation=float(np.median(saturation)-point['hsv_srgb']['s'])
        neutral=point['hsv_srgb']['s']<=.35
        yellow_excess=loc['color']=='yellow' and point['hsv_srgb']['s']<=.65 and desaturation>=.2
        spec=bool(strong and 3<=len(patch)<=100 and (neutral or yellow_excess) and point['luminance']>=.25 and contrast>=.2)
        sector=int((np.arctan2(xy[1]-1590.5,xy[0]-1269.5)%(2*np.pi))/(2*np.pi)*16)
        split='holdout' if sector in (1,5,9,13) else 'train'
        # Narrow geographic buffers exclude near-sector-boundary training, not test.
        angle=(np.arctan2(xy[1]-1590.5,xy[0]-1269.5)%(2*np.pi))/(2*np.pi)*16
        boundary=min(abs(angle-k) for k in (1,2,5,6,9,10,13,14))
        if split=='train' and boundary<.12:split='buffer'
        rows.append(dict(id=loc['id'],color=loc['color'],xy=xy,brightest=point,bright_patch=loc['bright_patch'],bright_shape=shape,
                         interior_centroid=b['region']['centroid'] if b else None,region_runs=b['region']['runs'] if b else [],
                         outline=b['outline']['raw'] if b else [],area=len(region),patch_area=len(patch),contrast=contrast,
                         strong=strong,specular_candidate=spec,peak_desaturation=desaturation,specular_evidence='neutral peak or yellow peak desaturated >=.2 relative to its interior; not proof of mirror reflection',sector=sector,split=split,uncertainty_px=2. if spec else 4.,
                         normalized_brightness=float(max(point['luminance']-floor,0)),
                         warning='Brightness patch, not verified mirror highlight; interior is not silhouette',
                         centerline_near=loc.get('centerline_near'),observed_full_boundary=None))
    if write:
        save(OUT/'observations.json',dict(source_sha256=sha(ROOT/'photo2/review/r275/inventory.json'),icc=icc,observations=rows,
             uncertain_source='photo2/review/r275/inventory.json:uncertain',uncertain_count=len(inv['uncertain']),
             selection='strong: >=60 colored /12 black interior px; specular: 3..100 bright px, peak saturation<=.35 OR yellow saturation<=.65 and >=.2 interior-relative desaturation; Y>=.25, contrast>=.2; no modeled selection',
             split='16 fixed image-angle sectors; 1,5,9,13 held out; .12-sector adjacent training buffer; all choices frozen before fitting'))
    return rows,rgb


def grid_points(s,step,rows=None):
    mask=np.zeros((int(np.ceil(3182/step)),int(np.ceil(2540/step))),bool)
    centers=s.pc if rows is None else np.array([r['xy'] for r in rows])
    radius=25 if rows is None else 45
    for x,y in centers:
        a=np.floor((np.array([x,y])-radius)/step).astype(int);b=np.ceil((np.array([x,y])+radius)/step).astype(int)+1
        mask[max(0,a[1]):min(mask.shape[0],b[1]),max(0,a[0]):min(mask.shape[1],b[0])]=True
    y,x=np.where(mask);return np.c_[x,y]*step


def bright_prediction(xy,intensity,step=1):
    # R275 uses a connected 85%-of-peak brightness patch. Compare same relative
    # threshold; intrinsic specular versus diffuse contamination remains uncertain.
    if not len(intensity) or intensity.max()<1e-4:return None
    peak=float(intensity.max());mask=intensity>=.85*peak
    # Preserve disconnected competing lobes diagnostically, select component
    # containing the global peak on the regular sampled image grid.
    from scipy.ndimage import label
    selected=xy[mask];lo=selected.min(0);ij=np.rint((selected-lo)/step).astype(int)
    raster=np.zeros((ij[:,1].max()+1,ij[:,0].max()+1),bool);raster[ij[:,1],ij[:,0]]=True
    labels,_=label(raster,np.ones((3,3),int));at=np.rint((xy[intensity.argmax()]-lo)/step).astype(int)
    keep=labels[ij[:,1],ij[:,0]]==labels[at[1],at[0]]
    result=moments(selected[keep],intensity[mask][keep]);result.update(peak_xy=xy[intensity.argmax()].tolist(),peak_intensity=peak,
         area_px2=int(keep.sum())*step**2,threshold_relative=.85,competing_high_pixels=int((~keep).sum()),
         region=np.c_[selected[keep],intensity[mask][keep]].round(5).tolist())
    return result


class Evaluation:
    """First-hit visible surfaces, one-sided interior distance, independent identities.

    Assignment uses positive support only. Light positions never choose owners.
    Dummy assignments remain in all score denominators. All scene beads occlude.
    """
    def __init__(self,base,rows,step=4,fit=True):
        self.base=base;self.rows=[r for r in rows if r['strong'] and r['split']=='train'] if fit else rows
        self.step=step;self.fit=fit
        self.samples=[pixels(r['region_runs']) for r in self.rows]
        if fit:self.samples=[p[np.linspace(0,len(p)-1,min(len(p),24)).astype(int)] for p in self.samples]
        self.xy=grid_points(scene(base,DEFAULT),step,self.rows if fit else None)
        self.cached=None

    def surfaces(self,p):
        key=tuple(p[:19])
        if self.cached is not None and self.cached[0]==key:return self.cached[1:]
        s=scene(self.base,p);d=s.camera(self.xy);good=d['owner']>=0;owners=np.unique(d['owner'][good]);foot={int(k):np.flatnonzero(d['owner']==k) for k in owners}
        trees={k:cKDTree(d['xy'][ix]) for k,ix in foot.items()}
        distances,near=cKDTree(s.pc[owners]).query(np.array([r['xy'] for r in self.rows]),k=min(8,len(owners)))
        candidates=owners[near];cols={int(k):j for j,k in enumerate(owners)}
        matrix=np.full((len(self.rows),len(owners)+len(self.rows)),144.);matrix[:,:len(owners)]=1e5
        allcost=[]
        for j,(row,pts,ks) in enumerate(zip(self.rows,self.samples,candidates)):
            if not len(pts):pts=np.array([row['xy']])
            costs={}
            for k in ks:
                dd=trees[int(k)].query(pts)[0]
                # Remove only raster quantization radius; no centering attraction.
                dd=np.maximum(dd-self.step/np.sqrt(2),0)
                cost=float(np.mean(np.minimum(dd,30)**2));costs[int(k)]=cost;matrix[j,cols[int(k)]]=cost
            allcost.append(costs)
        # Split independently: heldout data cannot affect training assignment.
        assignments=np.full(len(self.rows),-1,int)
        for split in ('train','holdout','buffer'):
            take=[j for j,r in enumerate(self.rows) if r['split']==split]
            if take:
                a,b=linear_sum_assignment(matrix[take]);assignments[np.array(take)[a]]=np.where(b<len(owners),owners[np.minimum(b,len(owners)-1)],-1)
        self.cached=(key,s,d,foot,trees,assignments,allcost)
        return self.cached[1:]

    def evaluate(self,p,details=False):
        s,d,foot,trees,assignments,costs=self.surfaces(p)
        sh=shade(s,d,light(p),shadows=True);pred={};mixed={}
        for k in set(assignments)-{-1}:
            ix=foot[k];h=bright_prediction(d['xy'][ix],sh['specular'][ix],self.step);pred[int(k)]=h
            if self.base.get('yellow_diffuse_ratio',0):mixed[int(k)]=bright_prediction(d['xy'][ix],sh['specular'][ix]+self.base['yellow_diffuse_ratio']*sh['diffuse'][ix],self.step)
        records=[];support=[];reflection=[];black_reflection=[]
        for j,(r,k,pts) in enumerate(zip(self.rows,assignments,self.samples)):
            k=int(k);h=mixed.get(k,pred.get(k)) if r['color']=='yellow' else pred.get(k);cost=costs[j].get(k,144.);support.append(min(cost,144.))
            err=float(np.linalg.norm(np.array(h['centroid'])-r['bright_shape']['centroid'])) if h and r['bright_shape'] else 30.
            if r['color']=='yellow' and r['specular_candidate']:reflection.append(min(err**2,900.))
            if r['color']=='black' and r['specular_candidate']:black_reflection.append(min(err**2,900.))
            if details:
                ds=(np.maximum(trees[k].query(pts)[0]-self.step/np.sqrt(2),0) if k>=0 else np.full(len(pts),30.)) if len(pts) else np.empty(0)
                alternatives=sorted(costs[j].items(),key=lambda z:z[1])[:3]
                records.append(dict(id=r['id'],color=r['color'],split=r['split'],strong=r['strong'],specular_candidate=r['specular_candidate'],owner=k,
                    conditional_identity=True,alternatives=[dict(owner=int(a),support_mse=float(b)) for a,b in alternatives],
                    observed_peak=r['xy'],observed_bright_centroid=r['bright_shape']['centroid'] if r['bright_shape'] else None,
                    observed_interior_centroid=r['interior_centroid'],observed_shape=r['bright_shape'],predicted=h,predicted_pure_specular=pred.get(k),yellow_diffuse_ratio=self.base.get('yellow_diffuse_ratio',0) if r['color']=='yellow' else 0,
                    projected_physical_center=s.pc[k].tolist() if k>=0 else None,
                    projected_visible_centroid=d['xy'][foot[k]].mean(0).tolist() if k>=0 else None,
                    highlight_error=err,missing_highlight=h is None,missing_highlight_sentinel_px=30,
                    peak_error=float(np.linalg.norm(np.array(h['peak_xy'])-r['xy'])) if h else 30.,
                    support=stats(ds),positive_pixels=r['area'],uncertainty_px=r['uncertainty_px'],
                    observed_brightness=r['normalized_brightness'],predicted_brightness=h['peak_intensity'] if h else 0.,
                    supported_boundary_distance=None,full_silhouette_iou=None,
                    boundary_reason='No verified physical outline in R275; positive interior containment reported instead'))
        # Only yellow calibrates light; transfer colors do not change it.
        data=float(np.mean(support)/16 + (np.mean(reflection)/36 if reflection else 0)+self.base.get('black_reflection_weight',0)*(np.mean(black_reflection)/36 if black_reflection else 0))
        reg=regularization(s.model,p)
        if not details:return data+reg['cost']
        return dict(objective=data+reg['cost'],data_objective=data,regularization=reg,records=records,
                    camera_unfinished=int((d['unknown']>0).sum()),shadow_unfinished=int(sh['unfinished_shadow_pairs']),
                    step=self.step,metrics=summarize(records),physical=physical(s.model)),(s,d,sh)


def regularization(model,p):
    # Independent priors, not interchangeable per-bead corrections.
    bending=float(np.sum((p[:4]/6)**2)*.08)
    strain=float(np.sum((p[4:8]/.005)**2)*.10)
    twist=float(np.sum((p[8:12]/.06)**2)*.10)
    camera=float(np.sum((p[14:19]/LIMIT[14:19])**2)*.08)
    # Center-distance surrogate catches collapse; exact penetration audit follows.
    g=model.geometry(np.arange(model.source.nbeads));sep=np.concatenate([np.linalg.norm(g['centers']-np.roll(g['centers'],i,axis=0),axis=1) for i in (1,6,7)])
    packing=float(np.mean(np.maximum(3.0-sep,0)**2)*2)
    return dict(cost=bending+strain+twist+camera+packing,bending=bending,strain=strain,twist=twist,camera=camera,packing=packing)


def physical(m):
    q=m.q;f=m.reference_arc;eps=basis(f)@m.p[4:8];speed=np.linalg.norm(m.curve(q,1),axis=1)
    length=np.trapezoid(speed,q);g=m.geometry(np.arange(m.source.nbeads));curv=np.linalg.norm(np.cross(m.curve(q,1),m.curve(q,2)),axis=1)/speed**3
    t=np.linspace(0,1,8193);angle=basis(t)@(np.array(m.config.get('phase_harmonics',[0]*4))+m.p[8:12])
    out=dict(length_units=float(length),reference_length_units=float(m.length),length_error_units=float(length-m.length),length_normalization=m.length_scale,
         strain_integral_units=float(np.trapezoid(eps,f*m.length)),strain_min=float(eps.min()),strain_max=float(eps.max()),material_jacobian_min=float((1+eps).min()),
         closure_position_units=float(np.linalg.norm(m.curve(0)-m.curve(1))),closure_tangent_units=float(np.linalg.norm(m.curve(0,1)-m.curve(1,1))),
         helical_turns=m.source.helicity*m.source.nrows,beads_per_turn=m.source.nbeads/m.source.nrows,phase_closure_error_rad=float(angle[-1]-angle[0]),
         curvature_max_inverse_units=float(curv.max()),hole_axis='local centerline tangent',strain_measure='increment relative to inherited material placement; integrated against physical reference arclength',
         neighbor_families={str(i):stats(np.linalg.norm(g['centers']-np.roll(g['centers'],i,axis=0),axis=1)) for i in (1,6,7)})
    # Actual material-speed irregularity is separate from the incremental strain.
    t=np.arange(m.source.nbeads)/m.source.nbeads;dt=1e-6
    sp=np.linalg.norm(m.geometry((t+dt)*m.source.nbeads)['line']-m.geometry((t-dt)*m.source.nbeads)['line'],axis=1)/(2*dt)
    out['total_material_speed_relative_to_uniform']=dict(min=float(sp.min()/length),max=float(sp.max()/length))
    return out


def summarize(records):
    out={}
    for split in ('train','holdout','buffer','all'):
        for color in ('yellow','red','black','all'):
            rr=[r for r in records if (split=='all' or r['split']==split) and (color=='all' or r['color']==color)]
            spec=[r for r in rr if r['specular_candidate']]
            out[split+'/'+color]=dict(count=len(rr),unmatched=sum(r['owner']<0 for r in rr),specular_candidates=len(spec),
                highlight=stats([r['highlight_error'] for r in spec]),peak=stats([r['peak_error'] for r in spec]),missing_specular=sum(r['missing_highlight'] for r in spec),
                support=stats([r['support']['rms'] for r in rr if r['support']['rms'] is not None]),missing_interior_count=sum(r['positive_pixels']==0 for r in rr),support_untrimmed_max=max((r['support']['maximum'] for r in rr if r['support']['maximum'] is not None),default=None))
    return out


def pattern_fit(ev,p,active,budget=121):
    p=np.array(p,float);best=ev.evaluate(p);steps=STEPS.copy();trace=[];count=1
    while count+2*len(active)<=budget:
        improved=False
        for j in active:
            choices=[]
            for sign in (-1,1):
                q=p.copy();q[j]=np.clip(q[j]+sign*steps[j],-LIMIT[j],LIMIT[j])
                if j==20:q[j]=np.clip(q[j],15,89)
                if j==21:q[j]=np.clip(q[j],2,18)
                val=ev.evaluate(q);count+=1;choices.append((val,q))
            val,q=min(choices,key=lambda z:z[0])
            if val<best-1e-7:best,p=val,q;improved=True
        trace.append(dict(evaluations=count,objective=best,parameters=p.tolist()))
        print('fit',count,round(best,5),flush=True)
        if not improved:steps*=.5
        if max(steps[active]/STEPS[active])<.125:break
    return p,dict(budget=budget,evaluations=count,objective=best,trace=trace,active=[NAMES[j] for j in active])


def fit_light(ev,p,budget=65):
    if any(r['split']!='train' for r in ev.rows):raise ValueError('Lighting fit accepts training observations only')
    if not any(r['color']=='yellow' and r['specular_candidate'] for r in ev.rows):raise ValueError('No yellow specular calibration candidates; do not fit an unidentifiable light')
    # Same four deterministic starts for every count/hand/camera screen.
    trials=[]
    for az in (-150,-60,30,120):
        q=np.array(p);q[19:22]=[az,65,6]
        # Powell is robust to half-peak raster/visibility changes.
        def fun(x):
            pp=q.copy();pp[19:22]=x;return ev.evaluate(pp)
        res=minimize(fun,q[19:22],method='Powell',bounds=[(-360,360),(15,89),(2,18)],options={'maxfev':budget,'xtol':.5,'ftol':.002})
        q[19:22]=res.x;trials.append(dict(parameters=q.tolist(),objective=float(fun(res.x)),nfev=res.nfev,success=bool(res.success)))
    best=min(trials,key=lambda r:r['objective']);return np.array(best['parameters']),trials


def save_model(name,base,p,fitlog):
    doc=dict(id=name,version=VERSION,base=base,parameters=dict(zip(NAMES,map(float,p))),p=list(map(float,p)),light=light(p),fit=fitlog)
    save(OUT/(name+'.json'),doc)


def initial_base(n=2696,h=1):
    c=json.loads((ROOT/'photo2/review/r258/R258_global_low_modes.json').read_text())
    c['n']=n;c['h']=h;c['turns']=Rope(n).nrows
    c.pop('frozen_legacy',None);c.pop('fixed_legacy_curve',None)
    c['id']='R276-base';return c


def preservation():
    # Track every preexisting photo2 artifact/code through R275 plus source photo/POV.
    import subprocess
    paths=subprocess.check_output(['git','ls-files','photo2','beads.pov','beads-photo-2.jpg'],cwd=ROOT,text=True).splitlines()
    return {p:sha(ROOT/p) for p in paths if 'r276' not in p.lower() and 'R276' not in p}


def run_fit():
    OUT.mkdir(parents=True,exist_ok=True);CACHE.mkdir(parents=True,exist_ok=True)
    if not (OUT/'preserved-hashes.json').exists():save(OUT/'preserved-hashes.json',preservation())
    rows,rgb=observation_data();base=initial_base();ev=Evaluation(base,rows)
    save(OUT/'protocol.json',dict(version=VERSION,parameter_names=NAMES,bounds_absolute=LIMIT.tolist(),steps=STEPS.tolist(),
         methods=['frozen surface + shared light','positive-interior geometry','bounded joint geometry + light','empirical normalized local-frame control'],
         physical='fixed total curve length; periodic normal bending; arclength-zero-integral strain; independent periodic twist; no individual translations',
         observed_boundaries='R275 masks positive only: no symmetric silhouette loss',
         limitations=['warm-started historical geometry','conditional one-to-one ownership','orthographic primary camera','no recovered sequence or physical count']))
    save_model('initial',base,DEFAULT,dict(status='inherited R258 geometry, R257-like direction only'))
    start=time.monotonic();p,trials=fit_light(ev,DEFAULT)
    save_model('light_only',base,p,dict(trials=trials,seconds=time.monotonic()-start))
    # Geometry-only diagnostic: same light, no highlight objective is achieved
    # by disabling specular flags only in this independent objective copy.
    no_spec=copy.deepcopy(rows)
    for r in no_spec:r['specular_candidate']=False
    geo=Evaluation(base,no_spec);pg,log=pattern_fit(geo,p,list(range(19)),budget=153)
    save_model('interior_geometry',base,pg,log)
    # Joint starts from the best training objective, not heldout feedback.
    seed=min((p,pg),key=ev.evaluate)
    pj,log=pattern_fit(ev,seed,list(range(22)),budget=177)
    save_model('joint',base,pj,log)
    # Correct coarse-grid instability with a finer 2px training pass; no new freedom.
    fine=Evaluation(base,rows,step=2)
    pf,flog=pattern_fit(fine,pj,[0,1,2,3,12,13,14,15,19,20,21],budget=89)
    save_model('joint_refined',base,pf,flog)
    print('FIT COMPLETE',time.monotonic()-start,flush=True)


def run_alternatives():
    rows,_=observation_data(False);results=[]
    # Equal flexibility/budget and eight phase starts; no old fitted correspondences.
    for n,h,focal in [(n,h,0) for n in (2674,2681,2696,2700) for h in (-1,1)]+[(2696,1,9598.)]:
        base=initial_base(n,h);base['focal']=focal
        # Camera sensitivity keeps projected paper centerline fixed on initialization.
        if focal:
            old=Model(base,DEFAULT);cam=old.view;cam.focal=0;pts=cam.project(np.array(base['knots']));cam.focal=focal
            r,d,e=cam.basis();P=(pts-[cam.tx,cam.ty])/cam.scale
            A=np.broadcast_to(np.array([r[:2],d[:2]]),(len(P),2,2)).copy();A+=P[:,:,None]*cam.scale*e[None,None,:2]/focal
            knots=np.array(base['knots']);knots[:,:2]=np.linalg.solve(A,P[...,None])[...,0];base['knots']=knots.tolist()
        # Reset inherited twist for every member, including primary in this screen.
        base['phase_harmonics']=[0]*4;base['local']=[]
        ev=Evaluation(base,rows);starts=[]
        for phase in np.linspace(-np.pi,np.pi,8,endpoint=False):
            b=copy.deepcopy(base);b['phase']=float(phase);ee=Evaluation(b,rows);starts.append((ee.evaluate(DEFAULT),b))
        score,base=min(starts,key=lambda z:z[0]);ev=Evaluation(base,rows)
        p,trials=fit_light(ev,DEFAULT,budget=35)
        p,log=pattern_fit(ev,p,[0,1,12,13,14,15,19,20],budget=49)
        name=f'alternative_N{n}_h{h:+d}_f{int(focal)}';save_model(name,base,p,dict(**log,light_starts=trials,phase_scores=[v for v,b in starts],scope='equal-budget local screen; not converged count selection'))
        results.append(dict(id=name,objective=log['objective']));save(OUT/'alternative-summary.json',results);print(name,flush=True)


def run_audit(names=None,step=2):
    rows,rgb=observation_data(False)
    if names is None:names=['initial','light_only','interior_geometry','joint','joint_refined']
    for name in names:
        doc=json.loads((OUT/(name+'.json')).read_text());ev=Evaluation(doc['base'],rows,step=step,fit=False)
        result,(s,d,sh)=ev.evaluate(np.array(doc['p']),True)
        # Native ownership is traced at EVERY original positive pixel, not sampled.
        counts=np.array([r['area'] for r in rows]);pts=np.concatenate([pixels(r['region_runs']) for r in rows]);hit=s.camera(pts);offset=np.r_[0,np.cumsum(counts)]
        colors={};conflicts=[]
        for j,(r,rec) in enumerate(zip(rows,result['records'])):
            own=hit['owner'][offset[j]:offset[j+1]];k=rec['owner']
            rec['native_owned_fraction']=(float(np.mean(own==k)) if k>=0 else 0.) if len(own) else None
            rec['native_unowned_fraction']=float(np.mean(own<0)) if len(own) else None
            rec['native_wrong_owner_fraction']=float(np.mean((own>=0)&(own!=k))) if len(own) else None
            if k>=0:colors.setdefault(k,[]).append((r['id'],r['color'],r['split']))
            if rec['predicted'] and r['bright_shape']:
                a=rec['predicted'];b=r['bright_shape'];rec['shape_sigma_error']=float(np.hypot(a['sigma_major']-b['sigma_major'],a['sigma_minor']-b['sigma_minor']))
                rec['shape_orientation_error_deg']=float(abs((a['orientation_deg']-b['orientation_deg']+90)%180-90))
                rec['shape_orientation_reliable']=bool(b['sigma_major']>1.4*max(b['sigma_minor'],.1))
        for k,rr in colors.items():
            if len(set(r[1] for r in rr))>1:conflicts.append(dict(owner=k,observations=rr))
        result['cross_split_color_conflicts']=conflicts
        for key,v in result['metrics'].items():
            split,col=key.split('/');rr=[r for r in result['records'] if (split=='all' or r['split']==split) and (col=='all' or r['color']==col)]
            v['native_owned_fraction_mean']=float(np.mean([r['native_owned_fraction'] for r in rr if r['native_owned_fraction'] is not None])) if any(r['native_owned_fraction'] is not None for r in rr) else None
        # Fit ONE material gain per color to training specular candidates, no offset.
        gains={}
        for col in ('yellow','red','black'):
            rr=[r for r in result['records'] if r['color']==col and r['specular_candidate'] and r['split']=='train']
            x=np.array([r['predicted_brightness'] for r in rr]);y=np.array([r['observed_brightness'] for r in rr]);gain=float(x@y/max(x@x,1e-12));gains[col]=gain
            for r in result['records']:
                if r['color']==col:r['relative_brightness_error']=(gain*r['predicted_brightness']-r['observed_brightness'])/max(float(np.mean(y)) if len(y) else 0,1e-8)
        result['material_gains']=gains;result['light']=doc['light'];result['parameter_source']=name+'.json';result['physical']=physical(s.model)
        result['native_camera_unfinished']=int((hit['unknown']>0).sum())
        with gzip.open(OUT/(name+'-audit.json.gz'),'wt') as f:json.dump(result,f,allow_nan=False)
        summary={k:v for k,v in result.items() if k!='records'};save(OUT/(name+'-summary.json'),summary)
        # Full-photo prediction retains unknown colors. Assigned observations color
        # only their conditional owner; never infer a repeating sequence.
        render=np.full((3182,2540,3),225,np.uint8);over=Image.fromarray(rgb.copy());od=ImageDraw.Draw(over)
        color={'yellow':np.array([225,172,35]),'red':np.array([170,40,55]),'black':np.array([25,25,30]),'unknown':np.array([110,125,140])}
        for k in np.unique(d['owner'][d['owner']>=0]):
            ix=np.flatnonzero(d['owner']==k);classes={z[1] for z in colors.get(int(k),[])};col=next(iter(classes)) if len(classes)==1 else 'unknown'
            intensity=.3+.5*sh['diffuse'][ix];pix=np.clip(color[col][None]*intensity[:,None]+sh['specular'][ix,None]*210,0,255).astype(np.uint8)
            for (x,y),v in zip(d['xy'][ix].astype(int),pix):render[y:y+step,x:x+step]=v
        for rec in result['records']:
            if rec['specular_candidate']:
                x,y=rec['observed_bright_centroid'];od.ellipse((x-3,y-3,x+3,y+3),outline='cyan',width=2)
                if rec['predicted']:
                    a,b=rec['predicted']['centroid'];od.line((x,y,a,b),fill='magenta',width=1);od.line((a-3,b,a+3,b),fill='magenta',width=2);od.line((a,b-3,a,b+3),fill='magenta',width=2)
        Image.fromarray(render).resize((1270,1591)).save(OUT/(name+'-prediction.png'));over.resize((1270,1591)).save(OUT/(name+'-highlights.png'))
        # Exact ray-derived sampled surfaces/normals/specular fields reproducible and saved.
        np.savez_compressed(OUT/(name+'-surfaces.npz'),xy=d['xy'].astype(np.int16),owner=d['owner'].astype(np.int16),normal=d['normal'].astype(np.float32),specular=sh['specular'].astype(np.float32),diffuse=sh['diffuse'].astype(np.float32))
        worst_crops(name,rows,result['records'],rgb,d,step)
        print('AUDIT',name,'yellow',result['metrics']['holdout/yellow'],'black',result['metrics']['holdout/black'],flush=True)


def worst_crops(name,rows,records,rgb,data,step):
    selected=sorted([r for r in records if r['specular_candidate']],key=lambda r:-r['highlight_error'])[:9]
    canvas=Image.new('RGB',(900,3*260),'#202020');draw=ImageDraw.Draw(canvas);index=[]
    for j,r in enumerate(selected):
        x,y=map(int,r['observed_peak']);box=(max(0,x-28),max(0,y-28),min(2540,x+29),min(3182,y+29));raw=Image.fromarray(rgb).crop(box).resize((228,228),Image.Resampling.NEAREST)
        marked=raw.copy();dd=ImageDraw.Draw(marked);scale=228/(box[2]-box[0]);project=lambda p:((p[0]-box[0])*scale,(p[1]-box[1])*scale)
        # Positive interior contour cyan; visible footprint samples white; peak magenta.
        row=next(o for o in rows if o['id']==r['id']);outline=[project(p) for p in row['outline']]
        if outline:dd.line(outline,fill='cyan',width=1)
        foot=data['xy'][data['owner']==r['owner']] if r['owner']>=0 else []
        for p in foot:
            a,b=project(p)
            if 0<=a<228 and 0<=b<228:dd.point((a,b),fill='white')
        a,b=project(r['observed_bright_centroid']);dd.ellipse((a-5,b-5,a+5,b+5),outline='lime',width=2)
        if r['predicted']:
            a,b=project(r['predicted']['centroid']);dd.line((a-6,b,a+6,b),fill='magenta',width=2);dd.line((a,b-6,a,b+6),fill='magenta',width=2)
        # Three cases per sheet would be tiny; individual raw/marked paired crops.
        pair=Image.new('RGB',(456,258),'#202020');pair.paste(raw,(0,30));pair.paste(marked,(228,30));pd=ImageDraw.Draw(pair);pd.text((4,3),r['id']+' '+r['split']+' err %.2fpx'%r['highlight_error'],fill='white')
        pair.save(OUT/f'{name}-worst-{j+1:02d}.png');index.append(dict(rank=j+1,id=r['id'],box=box,error=r['highlight_error']))
    save(OUT/(name+'-worst.json'),index)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--stage',choices=['fit','alternatives','audit','all'],default='all');ap.add_argument('--names',nargs='*');ap.add_argument('--step',type=int,default=2);args=ap.parse_args()
    if args.stage in ('fit','all'):run_fit()
    if args.stage in ('alternatives','all'):run_alternatives()
    if args.stage in ('audit','all'):run_audit(args.names,args.step)

if __name__=='__main__':main()
