"""Frozen denominators, frozen owners, bounded shared light and geometry trials."""
import argparse,time
from copy import deepcopy
import numpy as np
from .common import *
from .forward import *
from photo2.r297.common import pixels
from photo2.r298.calibrate import measurements,prediction,metrics
from photo2.r298.refine import dimension_loss
from photo2.r298.geometry import contact
from photo2.r298.photometry import PhotoScore


def observations():
    doc=read(BASE/'evidence/measurements.json.gz');screen=read(BASE/'evidence/visual-screen.json')['ambiguous'];rows=[deepcopy(r) for r in doc['observations'] if r['selected']]
    for r in rows:r['trusted']=r['id'] not in screen;r['weight']=1. if r['trusted'] else .25
    return rows


def ownership(scene,rows):
    out=[]
    for r in rows:
        xy=pixels({'runs':r['positive_interior']});tr=scene.trace(xy);ids,counts=np.unique(tr['owner'][tr['owner']>=0],return_counts=True);order=np.argsort(-counts,kind='stable');alts=[dict(owner=int(ids[i]),index=int(scene.indices[ids[i]]),fraction=float(counts[i]/len(xy))) for i in order]
        out.append(dict(id=r['id'],owner=alts[0]['owner'] if alts else -1,index=alts[0]['index'] if alts else None,alternatives=alts,unknown=int(tr['unknown'].sum()),basis='Largest fixed positive-interior first-hit fraction before lighting; no highlight-position matching',ambiguous=not alts or alts[0]['fraction']<.8 or len(alts)>1 and alts[1]['fraction']>.15))
    return out


def evaluate(scene,data,light,rows,assign,step=2.,order=3,detail=False):
    sh=shade(scene,data,light,order=order);pred={}
    for k in sorted(set(a['owner'] for a in assign)-{-1}):
        mask=data['owner']==k;pred[k]=highlight(data['xy'][mask],sh['intensity'][mask],step)
    records=[]
    for r,a in zip(rows,assign):
        k=a['owner'];h=pred.get(k);record=dict(id=r['id'],color=r['color'],split=r['split'],trusted=r['trusted'],observed_peak=r['peak'],observed_centroid=r['centroid'],observed_area=r['area_px2'],ownership=a,exists=h is not None,missing_reason=None if h else ('No assigned visible surface' if k<0 else 'No physically visible lobe above 1e-4'),predicted=h)
        diameter=None
        if k>=0:
            # Conditional projected physical face diameter, not a highlight-derived scale.
            eps=scene.radius;center=scene.centers[k];normal=scene.g[AXES[1]][k];binormal=scene.g[AXES[2]][k]
            circle=center+eps*(np.cos(np.arange(64)*np.pi/32)[:,None]*normal+np.sin(np.arange(64)*np.pi/32)[:,None]*binormal);p=scene.project(circle);diameter=float(max(np.ptp(p,axis=0)))
            record.update(orientation_deg=float(np.degrees(np.arctan2(scene.g[AXES[0]][k]@scene.down,scene.g[AXES[0]][k]@scene.right))%180),phase_deg=float(np.degrees(scene.phase[k])%360),station_fraction=float((scene.station_px[k]/scene.length)%1))
        record['apparent_diameter_px']=diameter
        for kind in ['peak','centroid']:
            delta=np.array(h[kind])-r[kind] if h else None;err=float(np.linalg.norm(delta)) if h else None
            record[kind+'_residual']=delta.tolist() if h else None;record[kind+'_error_px']=err;record[kind+'_normalized_error']=err/diameter if h and diameter else None
        record['extent_area_error_px2']=h['area_px2']-r['area_px2'] if h else None
        record['sigma_major_error_px']=h['sigma_major']-r['shape']['sigma_major'] if h else None
        record['sigma_minor_error_px']=h['sigma_minor']-r['shape']['sigma_minor'] if h else None
        record['orientation_error_deg']=float(abs((h['orientation_deg']-r['shape']['orientation_deg']+90)%180-90)) if h else None
        if not detail and h:record['predicted']={q:v for q,v in h.items() if q not in ['region','intensity']}
        records.append(record)
    return records,{k:v for k,v in sh.items() if k!='intensity'}


def score(records,rows):
    # Missing =30 only for bounded optimization, never reported as a measurement.
    rr=[(r,w) for r,w in zip(records,rows) if r['split']=='development'];weights=np.array([w['weight'] for r,w in rr]);loss=np.array([sum(min(30.,r[k+'_error_px'] if r['exists'] else 30.)**2 for k in ['peak','centroid'])/2 for r,w in rr]);return float(np.sum(loss*weights)/weights.sum())


def summary(records):
    out={}
    for group in ['all','trusted','yellow','red','black','development','comparison','trusted-comparison']:
        rr=[r for r in records if group=='all' or group=='trusted' and r['trusted'] or group in ['yellow','red','black'] and r['color']==group or group in ['development','comparison'] and r['split']==group or group=='trusted-comparison' and r['trusted'] and r['split']=='comparison']
        m=dict(n=len(rr),predicted=sum(r['exists'] for r in rr),missing=sum(not r['exists'] for r in rr),ambiguous_ownership=sum(r['ownership']['ambiguous'] for r in rr))
        for kind in ['peak','centroid']:
            a=np.sort([r[kind+'_error_px'] if r['exists'] else np.inf for r in rr]);finite=a[np.isfinite(a)]
            quant=lambda q:float(a[min(len(a)-1,int(np.ceil(q*len(a)))-1)]) if len(a) and np.isfinite(a[min(len(a)-1,int(np.ceil(q*len(a)))-1)]) else None
            m[kind]=dict(median=quant(.5),p90=quant(.9),quantile_null_means_infinite=True,finite_rms=float(np.sqrt(np.mean(finite**2))) if len(finite) else None,finite_median=float(np.median(finite)) if len(finite) else None,within={str(t):int(np.sum(a<=t)) for t in [2,3,5]},percent_within={str(t):float(100*np.sum(a<=t)/len(a)) if len(a) else None for t in [2,3,5]})
        out[group]=m
    return out


def geometry_assess(p,inputs,m):
    s,poly,bd,en=prediction(p,inputs,m);cert=contact(s);photo={split:PhotoScore(inputs,split).assess(s) for split in ['development','comparison']}
    return dict(physical=cert,metrics={split:metrics((bd,en),m,split) for split in ['development','comparison']},photographic=photo,dimension_loss=dimension_loss(bd,en,m))


def light_fit(scene,data,rows,assign,kind,start=None,budget=24,history_path=None,deadline=np.inf):
    center=scene.centers.mean(0);hist=[];best=[np.inf,None,None]
    def trial(v):
        if len(hist)>=budget or time.monotonic()>deadline:return
        v=np.array(v,float);v[0]=(v[0]+180)%360-180;v[1]=np.clip(v[1],15,89);v[2]=np.clip(v[2],3,18)
        if kind=='finite':v[3]=np.clip(v[3],300,6000)
        if kind=='extended':v[3]=np.clip(v[3],0,50)
        light=light_params(v,kind,center);rr,diagnostic=evaluate(scene,data,light,rows,assign);loss=score(rr,rows);hist.append(dict(v=v.tolist(),light=light,loss=loss,shadow=diagnostic))
        if loss<best[0]:best[:]=[loss,v,light]
        if history_path:save(history_path,hist)
    if start is None:
        for az in [-135.,-45.,45.,135.]:trial([az,60.,8.])
    else:
        if kind=='finite':
            for distance in [400.,1200.,4000.]:trial(list(start[:3])+[distance])
        elif kind=='extended':
            for width in [10.,25.,45.]:trial(list(start[:3])+[width])
        else:trial(start)
    steps=[24.,12.,3.]+([600.] if kind=='finite' else [12.] if kind=='extended' else [])
    for factor in [1.,.5,.25]:
        for j,delta in enumerate(steps):
            origin=best[1].copy()
            for sign in [-1,1]:
                v=origin.copy();v[j]+=sign*delta*factor;trial(v)
    return dict(light=best[2],v=best[1].tolist(),loss=best[0],history=hist)


def fixed():
    rows=observations();inputs,_=load_evidence();m=measurements();manifest=[];start=time.monotonic();deadline=start+1800
    ids=[0,49,8,29,76]
    # Freeze all five correspondence sets before any light optimization.
    for ident in ids:
        p=read(ROOT/f'photo2/r298/results/model-{ident}.json.gz')['parameters'];s=Surface(p,inputs);a=ownership(s,rows);save(BASE/f'evidence/ownership-{ident}.json',dict(parameters=p,assignments=a,utc=utc()))
    save(BASE/'evidence/fit-freeze.json',dict(utc=utc(),files={str(p.relative_to(ROOT)):sha(p) for p in (BASE/'evidence').glob('*') if p.is_file()},targets=dict(median_px=3,p90_px=5),denominator=len(rows),no_fitting_yet=True))
    for ident in ids:
        p=read(BASE/f'evidence/ownership-{ident}.json')['parameters'];s=Surface(p,inputs);assign=read(BASE/f'evidence/ownership-{ident}.json')['assignments'];data=grids(s,[a['owner'] for a in assign],2.);geo=geometry_assess(p,inputs,m);directional=None
        for kind,budget in [('directional',22),('finite',19),('extended',19)]:
            name=f'fixed-{ident}-{kind}';print('FIT',name,'surface pixels',len(data['xy']),flush=True)
            result=light_fit(s,data,rows,assign,kind,start=directional,budget=budget,history_path=BASE/f'results/{name}-history.json',deadline=deadline)
            if kind=='directional':directional=result['v']
            rr,diag=evaluate(s,data,result['light'],rows,assign);doc=dict(name=name,baseline=ident,parameters=p,geometry=geo,fit=result,records=rr,summary=summary(rr),shadow=diag,step=2,elapsed=time.monotonic()-start)
            save(BASE/f'results/{name}.json.gz',doc);manifest.append(name);save(BASE/'results/fixed-manifest.json',dict(models=manifest,elapsed=time.monotonic()-start,deadline_seconds=1800));print(name,doc['summary']['trusted']['centroid'],flush=True)
    save(BASE/'results/fixed-complete.json',dict(utc=utc(),models=manifest,elapsed=time.monotonic()-start))


def candidate_gate(geo,base):
    a=geo['metrics']['comparison'];b=base['metrics']['comparison'];x=geo['photographic']['comparison'];y=base['photographic']['comparison']
    return dict(physical=geo['physical']['certified'],width=a['width_mae']<=b['width_mae']+1,axial=a['bead_axial_mae']<=b['bead_axial_mae']+1,separator=x['separator_error_px']<=y['separator_error_px']+1,paper=x['paper_occupied']<=y['paper_occupied']+.02,region=x['region_containment']>=y['region_containment']-.02)


def joint():
    rows=observations();inputs,_=load_evidence();m=measurements();base=read(BASE/'results/fixed-49-directional.json.gz');assign=read(BASE/'evidence/ownership-49.json')['assignments'];history=[];winners=[];start=time.monotonic();remaining=1800-read(BASE/'results/fixed-complete.json')['elapsed'];deadline=start+max(0,remaining)
    groups=dict(camera_axis=[('elevation',3.),('roll',4.),('perspective',.00025),('axis_factor',.35)],shape_helix=[('axial',.05),('scale',.25),('minor',.2),('phase',.15)])
    groups['joint']=groups['camera_axis']+groups['shape_helix']
    def trial(p,label,light_start):
        geo=geometry_assess(p,inputs,m);gates=candidate_gate(geo,base['geometry']);row=dict(id=len(history),label=label,parameters=p,geometry=geo,gates=gates,fit=None,objective=None)
        if geo['physical']['certified'] and time.monotonic()<deadline:
            s=Surface(p,inputs);data=grids(s,[a['owner'] for a in assign],2);fit=light_fit(s,data,rows,assign,'directional',start=light_start,budget=7,deadline=deadline);rr,diag=evaluate(s,data,fit['light'],rows,assign);ph=geo['photographic']['development'];penalty=9*geo['dimension_loss']+50*ph['paper_occupied']+25*(1-ph['region_containment'])+ph['separator_error_px']**2
            row.update(fit=fit,records=rr,summary=summary(rr),shadow=diag,objective=fit['loss']+penalty)
        history.append(row);save(BASE/'results/joint-history.json.gz',history);print('JOINT',row['id'],label,geo['physical']['state'],row['objective'],flush=True);return row
    baseline=trial(deepcopy(base['parameters']),'joint-control',base['fit']['v'])
    for group,params in groups.items():
        best=baseline
        for key,delta in params:
            origin=deepcopy(best['parameters'])
            for sign in [-1,1]:
                if time.monotonic()>deadline:break
                p=deepcopy(origin)
                if key=='axis_factor':p['axis_nodes']=(np.array(origin['axis_nodes'])*(1+sign*delta)).tolist()
                else:p[key]=p.get(key,0.)+sign*delta
                p['perspective']=max(0.,p['perspective']);p['elevation']=min(89.,max(48.,p['elevation']))
                row=trial(p,f'{group} {key} {sign:+}',best['fit']['v'])
                if row['objective'] is not None and row['objective']<best['objective']:best=row
        winners.append(dict(group=group,trial=best['id']))
    assert len(history)<=96
    eligible=[r for r in history if r['fit'] and all(r['gates'].values())];chosen=min(eligible,key=lambda r:r['objective']) if eligible else baseline
    save(BASE/'results/selection.json',dict(utc=utc(),trials=len(history),elapsed=time.monotonic()-start,controls=winners,chosen=chosen['id'],native_exports=sorted(set([0,chosen['id']]+[r['trial'] for r in winners])),strict_success_not_yet_evaluated=True,decision='No further optimization. Native evaluation follows. No adoption from training scores.'))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['fixed','joint']);a=p.parse_args();globals()[a.stage]()
