"""R258 bead-driven periodic geometry. No historical observations in fitting.

The initial curve is data, never an objective term. All losses use positive
photo patches, exact first-hit annular footprints, and physical invariants.
"""
from __future__ import annotations
import argparse, copy, hashlib, json, time
from pathlib import Path
from types import SimpleNamespace
import numpy as np
from scipy.interpolate import CubicSpline
from scipy.ndimage import distance_transform_edt, map_coordinates
from scipy.optimize import linear_sum_assignment
from .generate import ROOT, save, sha
from .models import load as old_load, RADIUS, rays
from camera_r254 import Camera
from bead_placement import Rope
from tangent_circles import ROW

OUT=ROOT/'photo2/review/r258'
VERSION='r258-positive-surfaces-v2'

class BeadCurve:
    """Absolute periodic 3D knots; planar specialization (z=0) for this photo.

    Parameter t is material position. Speed is regularized in source units, not
    to a saved curve. Periodic phase corrections preserve integer winding.
    """
    def __init__(self,config):
        self.config=config;self.source=SimpleNamespace(nbeads=config['n'],nrows=config['turns'],helicity=config['h'])
        self.view=Camera(**config['camera']);self.view.focal=config.get('focal',0)
        knots=np.asarray(config['knots'])
        if np.max(np.abs(knots[:,2]))>1e-8:raise ValueError('This fitted specialization requires a centerline in the table plane z=0')
        self.curve=CubicSpline(np.linspace(0,1,len(knots)+1),np.vstack([knots,knots[0]]),bc_type='periodic')
        self.unscaled_length=ROW*config['turns']*self.view.scale
    def geometry(self,indices):
        if self.config.get('frozen_legacy'):
            return old_load(self.config['frozen_legacy'])[1].geometry(indices)
        ii=np.atleast_1d(indices);t=(ii/self.source.nbeads)%1;line=self.curve(t);v=self.curve(t,1);v/=np.linalg.norm(v,axis=1)[:,None]
        # z=0 specializes the otherwise 3D spline to the maker's table plane.
        normal=np.c_[-v[:,1],v[:,0],np.zeros(len(t))]
        if self.config.get('fixed_legacy_curve'):
            g=old_load(self.config['fixed_legacy_curve'])[1].geometry(indices)
            line,v,normal=g['line'],g['tangent'],g['normal']
        angle=self.config['phase']+self.source.helicity*2*np.pi*self.source.nrows*t
        a=2*np.pi*t
        angle+=np.array([np.sin(a),np.cos(a),np.sin(2*a),np.cos(2*a)]).T@np.array(self.config.get('phase_harmonics',[0]*4))
        for b in self.config.get('local',[]):
            u=((t-b['t']+.5)%1-.5)/b['width'];w=np.where(abs(u)<1,(1-u*u)**3,0)
            angle+=w*(b.get('phase',0)+b.get('winding',0)*u)
        radial=np.sin(angle)[:,None]*normal;radial[:,2]=np.cos(angle)
        return dict(indices=ii.astype(int),line=line,tangent=v,normal=normal,radial=radial,centers=line+4*radial,outward=line+(4+RADIUS)*radial,fraction=t)


def initialize(n=2696,h=1,knots=192):
    """Only warm-start geometry/camera; never load old labels/adjacency/stars.

    Old fitted fields enter only the initial sampled geometry/phase. Index zero retains its
    *review address* only. It is not an observation or fitting constraint.
    """
    c,m=old_load('N2696_h+1_f0')
    # Sample underlying unregistered material curve, not old bead centers.
    f=np.arange(knots)/knots
    xy=np.c_[np.interp(f,m.arc_fraction,m.plane[:,0]),np.interp(f,m.arc_fraction,m.plane[:,1])]
    origin=round(c['origin']*n/c['n']);turns=Rope(n).nrows
    phase=(c['p'][0]+c['h']*2*np.pi*m.turns*c['origin']/c['n']-h*2*np.pi*turns*origin/n)%(2*np.pi)
    # Rotate material chart only to match the old review address near k=0.
    from global_fit_r253 import correction
    ds,_=correction(np.array([c['origin']/c['n']]),c['p'])
    offset=c['p'][1]/c['n']+float(ds[0])
    ff=(f+offset)%1
    xy=m.geometry(f*c['n'])['line'][:,:2]
    return dict(schema=1,id=f'R258_N{n}_h{h:+d}',n=n,h=h,turns=turns,origin=origin,phase=float(c['p'][0] if n==2696 and h==1 else phase),phase_harmonics=c['p'][10:14] if n==2696 and h==1 else [0]*4,
                knots=np.c_[xy,np.zeros(knots)].tolist(),local=[],focal=0,freeze_B_curve=True,
                camera=dict(elevation=m.view.elevation,roll=m.view.roll,tx=m.view.tx,ty=m.view.ty,scale=m.view.scale),
                initialization='R254 underlying curve/camera and approximate phase only; no observations, adjacency, color order or correction penalties',
                independence='Warm-start conditional local refit; unobserved spans remain initialized, not photographically recovered')


def section_basis(config,t,width=.025):
    u=((np.arange(len(config['knots']))/len(config['knots'])-t+.5)%1-.5)/width
    w=np.where(abs(u)<1,(1-u*u)**3,0)
    # Smooth compact supports; no displacement regularization or target at zero.
    return np.c_[w,w*u,w*u*u]


def apply(config,t,p,variant):
    c=copy.deepcopy(config);c.pop('frozen_legacy',None);c.pop('fixed_legacy_curve',None);v=c['camera'];b=section_basis(c,t)
    # Units of coefficients are projected pixels. Converted to world plane.
    basis=Camera(**v).basis();inv=np.linalg.inv(np.array([basis[0][:2],basis[1][:2]]))/v['scale']
    if variant in ['C','D']:
        delta=(b@np.asarray(p[:6]).reshape(3,2))@inv.T
        q=np.asarray(c['knots']);q[:,:2]+=delta;c['knots']=q.tolist()
    if variant in ['B','D']:
        phase,winding=p[6:8];c['local'].append(dict(t=t,width=.025,phase=float(phase),winding=float(winding)))
    if variant=='D':
        v['elevation']+=p[8];v['roll']+=p[9];v['tx']+=p[10];v['ty']+=p[11]
        # Smooth longitudinal motion of material along the actual curve.
        curve=BeadCurve(c);u=np.arange(len(c['knots']))/len(c['knots']);q=np.asarray(c['knots'])
        tangent=curve.curve(u,1);tangent/=np.linalg.norm(tangent,axis=1)[:,None]
        q+=b[:,0,None]*p[12]/v['scale']*tangent;c['knots']=q.tolist()
        # Camera scale is estimated in D, never constrained to old curve length.
        v['scale']*=float(np.exp(p[13] if len(p)>13 else 0.))
    c['variant']=variant
    if variant=='A' and c.get('n')==2696 and c.get('h')==1:c['frozen_legacy']='N2696_h+1_f0'
    if variant=='B' and c.get('n')==2696 and c.get('h')==1 and c.get('freeze_B_curve',False):c['fixed_legacy_curve']='N2696_h+1_f0'
    return c


def physical(model):
    n=model.source.nbeads;t=np.arange(n)/n
    d=model.curve(t,1);dd=model.curve(t,2);speed=np.linalg.norm(d,axis=1)
    curvature=np.linalg.norm(np.cross(d,dd),axis=1)/np.maximum(speed,1e-10)**3
    spacing=speed/n;nominal=ROW*model.source.nrows/n
    # Soft physical tolerance bands, absolute curvature and source spacing.
    spacing_cost=float(np.mean((np.maximum(abs(spacing/nominal-1)-.08,0)/.08)**2))
    curvature_cost=float(np.mean((np.maximum(curvature-.12,0)/.08)**2))
    g=model.geometry(np.arange(n));angle=np.unwrap(np.arctan2(np.sum(g['radial']*g['normal'],axis=1),g['radial'][:,2]))
    step=np.diff(np.r_[angle,angle[0]+model.source.helicity*2*np.pi*model.source.nrows]);expected=model.source.helicity*2*np.pi*model.source.nrows/n
    winding_cost=float(np.mean((np.maximum(abs(step/expected-1)-.03,0)/.03)**2))
    # Adjacent center separations: packing collision surrogate, not intersection proof.
    sep=np.linalg.norm(np.roll(g['centers'],-1,axis=0)-g['centers'],axis=1)
    packing_cost=float(np.mean((np.maximum(3.25-sep,0)/.3)**2))
    return dict(cost=spacing_cost+curvature_cost+winding_cost+packing_cost,spacing_cost=spacing_cost,curvature_cost=curvature_cost,winding_cost=winding_cost,packing_cost=packing_cost,
                spacing_ratio_min=float(min(spacing/nominal)),spacing_ratio_max=float(max(spacing/nominal)),curvature_max=float(max(curvature)),neighbor_distance_min=float(min(sep)),
                winding_step_min=float(min(abs(step))),winding_step_max=float(max(abs(step))),closure_position=float(np.linalg.norm(model.curve(0)-model.curve(1))),closure_tangent=float(np.linalg.norm(model.curve(0,1)-model.curve(1,1))))


def evidence(inventory,box,section):
    """Whole ambiguity groups are split together. No saved modeled owners read."""
    rows=[r for r in inventory['observations'] if box[0]+12<r['x']<box[2]-12 and box[1]+12<r['y']<box[3]-12 and r['kind']=='colored-interior' and r['evidence_class']!='rejected' and r['patch_area']>=12]
    # Credible separate bodies need an interior class or ALL within-component
    # relevant pair tests credible. Others kept as uncertain positive patches.
    result=[]
    for r in rows:
        separate=r['evidence_class']=='interior'
        key=r['component'] # conservative leakage block: touching same-color groups
        split='holdout-body' if int(hashlib.sha256(key.encode()).hexdigest()[:8],16)%4==0 else 'train'
        result.append(dict(id=r['id'],component=key,xy=[r['x'],r['y']],color=r['color'],patch=r['patch'],weight=1. if separate else .3,distinct=separate,split=split,identity=None,reason=r['reason']))
    if section=='origin':
        # R258 maker color is authoritative; association of these photo-only
        # shadow patches with that body remains an explicitly conditional mask.
        c,m=old_load('N2696_h+1_f0');p=m.view.project(m.geometry([c['origin']+2])['centers'])[0]
        rr=[r for r in inventory['observations'] if r['kind']=='colored-interior' and r['patch_area']>=3 and np.linalg.norm(np.array([r['x'],r['y']])-p)<24 and r['y']>p[1] and r['evidence_class']!='interior']
        reviewed=json.loads((OUT/'bead2-reviewed-support.json').read_text())
        # Maker Q2 excludes A. Only the seven B pixels are established. The
        # old rejected union is preserved in the question artifact, not fitted.
        ids={r['id'] for r in rr};result=[r for r in result if r['id'] not in ids]
        result.append(dict(id='R258-bead2-reviewed-B',component='R258-bead2',xy=np.mean(reviewed['patch'],axis=0).tolist(),color='yellow (maker R258)',patch=reviewed['patch'],weight=2.,distinct=True,split='train',identity=2,
                           source_ids=[reviewed['source_id']],reason=reviewed['evidence']))
    # Reliable R257 photo-only reflection patches; ignore their saved owners.
    rd=json.loads((ROOT/'photo2/review/r257/observations.json').read_text())['observations']
    for r in rd:
        x,y=r['xy']
        if r['reliable_candidate'] and box[0]+12<x<box[2]-12 and box[1]+12<y<box[3]-12:
            split='holdout-body' if int(hashlib.sha256(r['id'].encode()).hexdigest()[:8],16)%4==0 else 'train'
            result.append(dict(id=r['id'],component=r['id'],xy=r['xy'],color='black?',patch=r['patch'],weight=.6,distinct=True,split=split,identity=None,reason='Positive reflection on dark surround only; no dark-gap mask or light-position objective'))
    return result


class SurfaceLoss:
    def __init__(self,box,observations,step=3):
        self.box=box;self.rows=observations;self.step=step
        y,x=np.mgrid[box[1]:box[3]:step,box[0]:box[2]:step];self.xy=np.c_[x.ravel(),y.ravel()];self.shape=x.shape
    def raster(self,model):
        own,_,un=rays(model,self.xy,model.geometry(np.arange(model.source.nbeads)))
        own[un>0]=-1
        return own.reshape(self.shape)
    def evaluate(self,model,split='train',details=False):
        raster=self.raster(model);rows=[r for r in self.rows if split=='all' or r['split']==split]
        if not rows:return (0.,[]) if details else 0.
        known={(model.config['origin']+r['identity'])%model.source.nbeads for r in rows if r['identity'] is not None}
        owners=np.array(sorted(set(raster[raster>=0])|known),int);dist={int(i):(distance_transform_edt(raster!=i)*self.step if np.any(raster==i) else np.full(self.shape,30.)) for i in owners}
        costs=np.full((len(rows),len(owners)+len(rows)),36.)
        for j,r in enumerate(rows):
            pp=np.asarray(r['patch']);coords=np.array([(pp[:,1]-self.box[1])/self.step,(pp[:,0]-self.box[0])/self.step])
            for col,i in enumerate(owners):
                if r['identity'] is not None and i!=(model.config['origin']+r['identity'])%model.source.nbeads:continue
                d=map_coordinates(dist[int(i)],coords,order=1,mode='constant',cval=30.)
                costs[j,col]=np.mean(np.minimum(d,12)**2)
        # Only distinct candidate bodies consume unique slots; ambiguous patches
        # may share owners. Opposite classes cannot silently become one body.
        assigned={j:int(np.where(owners==(model.config['origin']+r['identity'])%model.source.nbeads)[0][0]) for j,r in enumerate(rows) if r['identity'] is not None}
        distinct=[j for j,r in enumerate(rows) if r['distinct'] and j not in assigned]
        if distinct:
            matrix=costs[distinct].copy()
            for col in assigned.values():matrix[:,col]=1e6
            a,b=linear_sum_assignment(matrix);assigned.update({distinct[j]:int(k) for j,k in zip(a,b)})
        for j,r in enumerate(rows):
            if j not in assigned:assigned[j]=int(costs[j].argmin())
        records=[];value=0.;total=0.
        color_owners={}
        for j,r in enumerate(rows):
            col=assigned[j];owner=int(owners[col]) if col<len(owners) else -1;cost=costs[j,col]
            value+=r['weight']*min(cost,36);total+=r['weight']
            if owner>=0:color_owners.setdefault(owner,set()).add(r['color'].split(' ')[0])
            records.append(dict(id=r['id'],owner=owner,k=(owner-model.config['origin'])%model.source.nbeads if owner>=0 else None,cost=float(cost),split=r['split'],distinct=r['distinct']))
        conflicts=sum(len(cs)>1 for cs in color_owners.values());value=value/max(total,1)+2*conflicts/max(len(rows),1)
        return (float(value),records) if details else float(value)


def fit(config,t,loss,variant,budget=180,active_override=None):
    active={'A':[],'B':[6,7],'C':list(range(6)),'D':list(range(14))}[variant]
    if active_override is not None:active=list(active_override)
    steps=np.array([3,3,8,8,12,12,.14,.12,1.,.15,2,2,3.,.003])
    # No displacement, tangent, curvature, registration, or spacing bounds
    # relative to the initial curve. Only B's explicitly limited diagnostic
    # phase freedom and the camera-above-paper domain are bounded.
    lower=np.full(14,-np.inf);upper=np.full(14,np.inf)
    if variant=='B':lower[6:8]=[-1.4,-1.2];upper[6:8]=[1.4,1.2]
    lower[8]=1.-config['camera']['elevation'];upper[8]=89.9-config['camera']['elevation']
    p=np.zeros(14);evaluations=0;trace=[]
    def score(q):
        nonlocal evaluations
        m=BeadCurve(apply(config,t,q,variant));v=loss.evaluate(m)+.8*physical(m)['cost'];evaluations+=1;return v
    best=score(p)
    while active and evaluations+2*len(active)<=budget:
        improved=False
        for j in active:
            candidates=[]
            for sign in [-1,1]:
                q=p.copy();q[j]=np.clip(q[j]+sign*steps[j],lower[j],upper[j]);candidates.append((score(q),q))
            v,q=min(candidates,key=lambda z:z[0])
            if v<best-1e-6:best,p=v,q;improved=True
        trace.append(dict(evaluations=evaluations,cost=best,steps=steps[active].tolist()))
        if not improved:
            steps*=.5
            if max(steps[active]/np.array([3,3,8,8,12,12,.14,.12,1.,.15,2,2,3.,.003])[active])<.12:break
    c=apply(config,t,p,variant)
    return c,dict(variant=variant,parameters=p.tolist(),evaluations=evaluations,objective=best,trace=trace,budget=budget,active=active,boundary_hits=[j for j in active if p[j]<=lower[j]+.001 or p[j]>=upper[j]-.001])


def audit(config,loss):
    m=BeadCurve(config);matches=[]
    for split in ['train','holdout-body']:
        matches+=loss.evaluate(m,split,True)[1]
    match_map={r['id']:r for r in matches};matches=[match_map[r['id']] for r in loss.rows]
    g=m.geometry(np.arange(config['n']));raster=loss.raster(m);records=[]
    for r,a in zip(loss.rows,matches):
        pp=np.asarray(r['patch']);own,_,un=rays(m,pp,g);owner=a['owner'];good=(own==owner)&(un==0)&(owner>=0)
        footprint=loss.xy[raster.ravel()==owner] if owner>=0 else np.empty((0,2))
        from scipy.spatial import cKDTree
        residual=cKDTree(footprint).query(pp)[0] if len(footprint) else np.full(len(pp),30.)
        records.append(dict(**a,color=r['color'],identity=r['identity'],positive_pixels=len(pp),owned_fraction=float(good.mean()),unowned_fraction=float((own<0).mean()),wrong_owner_fraction=float(((own>=0)&~good).mean()),
                            residual_mean=float(residual.mean()),residual_rms=float(np.sqrt(np.mean(residual**2))),residual_median=float(np.median(residual)),residual_p90=float(np.percentile(residual,90)),residual_worst=float(max(residual)),
                            footprint_area_px2=len(footprint)*loss.step**2,positive_area_not_owned=int((~good).sum()),
                            unsupported_predicted_area_upper_bound_px2=max(0,len(footprint)*loss.step**2-int(good.sum())),boundary_iou=None,
                            boundary_iou_reason='Positive interiors are not verified full body masks',support_reason=r['reason']))
    metrics={}
    for split in ['train','holdout-body','all']:
        rr=[r for r in records if split=='all' or r['split']==split]
        if rr:metrics[split]=dict(count=len(rr),distinct_candidates=sum(r['distinct'] for r in rr),explained_distinct_candidates=sum(r['distinct'] and r['owned_fraction']>=.8 for r in rr),
                                  ownership_mean=float(np.mean([r['owned_fraction'] for r in rr])),wrong_owner_mean=float(np.mean([r['wrong_owner_fraction'] for r in rr])),
                                  mean_residual=float(np.mean([r['residual_mean'] for r in rr])),rms_residual=float(np.sqrt(np.mean([r['residual_rms']**2 for r in rr]))),worst_residual=float(max(r['residual_worst'] for r in rr)))
    return dict(metrics=metrics,physical=physical(m),observations=records)


def run(budget=180):
    OUT.mkdir(parents=True,exist_ok=True);inventory=json.loads((ROOT/'photo2/output/debugger/generated/observations.json').read_text());base=initialize()
    # ROIs use old geometry only to locate sections, never as photo evidence.
    sections=[('origin',2),('straight-black',370),('bend',1695),('opposite',1100)]
    bm=BeadCurve(base);results=[];models=[]
    for name,k in sections:
        gi=(base['origin']+k)%base['n'];t=gi/base['n'];pc=bm.view.project(bm.geometry([gi])['centers'])[0]
        box=[int(pc[0]-110),int(pc[1]-100),int(pc[0]+110),int(pc[1]+100)];rows=evidence(inventory,box,name);loss=SurfaceLoss(box,rows)
        save(OUT/f'{name}-evidence.json',dict(box=box,observations=rows,split_rule='SHA256 component/id mod4 ==0 holds entire ambiguity group; no per-pixel split'))
        for variant in ['A','B','C','D']:
            start=time.monotonic()
            c,fitlog=fit(base,t,loss,variant,budget);c['id']=f'R258_{name}_{variant}';c['section']=name;c['box']=box
            measured=audit(c,loss);row=dict(id=c['id'],section=name,**fitlog,**measured,seconds=time.monotonic()-start)
            oldmodel=old_load('N2696_h+1_f0')[1];oldline=oldmodel.view.project(oldmodel.geometry(np.arange(base['n']))['line']);new=BeadCurve(c);newline=new.view.project(new.geometry(np.arange(base['n']))['line']);delta=np.linalg.norm(newline-oldline,axis=1)
            row['curve_displacement_px']=dict(mean=float(delta.mean()),rms=float(np.sqrt(np.mean(delta**2))),maximum=float(delta.max()),at_section=float(delta[gi]))
            # Spatial holdout: identical evidence in each other region, no refit.
            row['spatial_holdout']={}
            for other,kk in sections:
                if other==name:continue
                j=(base['origin']+kk)%base['n'];p=bm.view.project(bm.geometry([j])['centers'])[0];bb=[int(p[0]-110),int(p[1]-100),int(p[0]+110),int(p[1]+100)]
                ll=SurfaceLoss(bb,evidence(inventory,bb,other));row['spatial_holdout'][other]=ll.evaluate(new,'all')
            save(OUT/(c['id']+'.json'),c);results.append(row);models.append(c['id']);save(OUT/'results.json',results);save(OUT/'model-index.json',models)
            print(c['id'],row['metrics'], 'sec',round(row['seconds']),flush=True)
    save(OUT/'initial.json',base)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--budget',type=int,default=180);a=ap.parse_args();run(a.budget)
