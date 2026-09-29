"""R132: compare uncertain-outline penalties with positive surface cores.

Assisted local diagnostic: reuses supplied regions and tentative correspondence
charts. Unknown pixels carry no ownership constraint. No image detector or new
geometry parameters are introduced; G remains withheld.
"""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-matplotlib')
import argparse,json
from pathlib import Path
import numpy as np
from scipy.ndimage import distance_transform_edt
from scipy.optimize import minimize
from local_surface_fit import ROOT,IDS,polygons,trace as ortho_trace
from check_local_perspective import trace as perspective_trace,render as perspective_render
from check_local_surface_fit import render as ortho_render
from check_placement import sha


def constraints(xy,shape,masks,held_out,point,radius,erosion,spacing=1):
    unknown=(np.linalg.norm(xy-np.asarray(point),axis=1)<=radius).reshape(shape)
    data={}
    for k,mask in masks.items():
        if k==held_out:continue
        # Unknown pixels must not create an artificial boundary, even inside
        # the distance transform. Values assigned inside unknown are irrelevant.
        inside=distance_transform_edt(mask|unknown)*spacing
        outside=distance_transform_edt((~mask)|unknown)*spacing
        core=mask & (~unknown) & (inside>erosion)
        data[k]=dict(core=core,inside=np.maximum(inside-erosion,0)*(~unknown),
                     outside=np.maximum(outside-erosion,0)*(~unknown),
                     normalization=max(1,int((mask&~unknown).sum())))
    return unknown,data


def score(labels,mapping,data,method):
    result=[]
    for k,d in data.items():
        pred=labels==mapping[k]
        if method=='cores':
            result.append(float((d['core']&~pred).sum()/max(1,d['core'].sum())))
        elif method=='masked_regions':
            result.append(float(((~pred)*d['inside']+pred*d['outside']).sum()/d['normalization']))
        else:raise ValueError(method)
    return float(np.mean(result))


def cast(p,xy,fit,camera):
    if camera['kind']=='orthographic':return ortho_trace(p,xy,fit['hand'])[0]
    return perspective_trace(p,xy,fit['hand'],camera['focal_px'],np.array(camera['principal_xy']))[0]


def optimize(cfg,fit,camera,method,point,radius,erosion,maxfev=400):
    original=np.array(fit['parameters']);free=np.array([0,1,2,3,5,6])
    widths=np.array([10,10,2,12,0,15,25])
    bounds=list(zip((original-widths)[free],(original+widths)[free]))
    summaries=[];best=None
    # The same two local starts for both methods; no held-out score ranks starts.
    for restart,dx in enumerate([0.,-3.]):
        p=original.copy();p[0]+=dx
        for spacing in [2,1]:
            xy,shape,masks=polygons(cfg,spacing)
            _,data=constraints(xy,shape,masks,cfg['held_out'],point,radius,erosion,spacing)
            def unpack(v):
                out=p.copy();out[free]=v;return out
            active=np.logical_or.reduce([d['core'] for d in data.values()]).ravel() if method=='cores' else np.ones(len(xy),bool)
            def objective(v):
                labels=np.full(len(xy),-999,int)
                labels[active]=cast(unpack(v),xy[active],fit,camera)
                return score(labels.reshape(shape),fit['mapping'],data,method)
            start_value=objective(p[free])
            result=minimize(objective,p[free],method='Powell',bounds=bounds,
                options={'maxfev':maxfev,'maxiter':20,'xtol':.005,'ftol':.0001})
            # Keep a seed if bounded line-search steps end with a worse value.
            accepted=result.fun<=start_value
            if accepted:p=unpack(result.x)
            summaries.append(dict(restart=restart,spacing=spacing,evaluations=int(result.nfev),
                success=bool(result.success),message=str(result.message),accepted=bool(accepted),
                start_loss=float(start_value),end_loss=float(result.fun)))
        value=score(cast(p,xy,fit,camera).reshape(shape),fit['mapping'],data,method)
        if best is None or value<best[0]:best=(value,p.copy())
    return best[1],best[0],summaries


def metrics(labels,cfg,point,radius=6,erosion=3):
    xy,shape,masks=polygons(cfg)
    unknown,cores=constraints(xy,shape,masks,None,point,radius,erosion)
    result={}
    for k,mask in masks.items():
        pred=labels==cfg['active_mapping'][k]
        a=pred&~unknown;b=mask&~unknown
        core=cores[k]['core']
        result[k]=dict(core_coverage=float((pred&core).sum()/max(1,core.sum())),
            iou=float((a&b).sum()/max(1,(a|b).sum())),
            area_ratio=float(a.sum()/max(1,b.sum())),predicted_area=int(a.sum()),
            observed_area=int(b.sum()),core_pixels=int(core.sum()))
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'photo2/output/r132')
    parser.add_argument('--resume',action='store_true',help='Resume completed cases after validating unchanged dependencies')
    args=parser.parse_args();out=args.output;out.mkdir(parents=True,exist_ok=True)
    cached={}
    if args.resume and (out/'report.json').exists():
        previous=json.loads((out/'report.json').read_text())
        for name,digest in previous['source_sha256'].items():
            if name!='photo2/refine_surface_constraints.py':assert sha(ROOT/name)==digest,name
        for case in previous['cases']:
            case.setdefault('fit_code_sha256',previous['source_sha256']['photo2/refine_surface_constraints.py'])
            cached[case['stem']]=case
    photo_cfg=json.loads((ROOT/'photo2/local-fit-r126.json').read_text())
    prior=json.loads((ROOT/'photo2/review/r126/perspective-report.json').read_text())
    photo_fits=[f for f in prior['results'] if f['focal_ratio']==1.]
    photo_camera=dict(kind='perspective',focal_px=prior['nominal_focal_px'],principal_xy=prior['principal_xy'])
    # Reproduce a known synthetic source from the original POV macro. Truth is
    # used to supply diagnostic regions and for evaluation, never to initialize.
    true_p=[1348,289,8,-4,55,10,5]
    actual,synthetic_provenance=ortho_render(true_p,1,photo_cfg['crop'],out/'synthetic','truth')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    synthetic_cfg=dict(photo_cfg,image=None,observations={})
    for k,index in photo_cfg['hypotheses']['H1'].items():
        fig,ax=plt.subplots();segments=ax.contour((actual==index).astype(float),levels=[.5]).allsegs[0]
        poly=max(segments,key=len);plt.close(fig)
        synthetic_cfg['observations'][k]=(poly[::2]+np.array(photo_cfg['crop'][:2])).tolist()
    (out/'synthetic-config.json').write_text(json.dumps(synthetic_cfg,indent=2)+'\n')
    old_synthetic=json.loads((ROOT/'photo2/review/r126/synthetic-fits.json').read_text())
    synthetic_fits=[min([f for f in old_synthetic if f['hypothesis']==name],key=lambda f:f['region_loss']) for name in ['H1','H2']]
    cases=[]
    # Freeze a single evaluation support regardless of fit erosion/radius.
    for dataset,cfg,fits,camera in [('synthetic',synthetic_cfg,synthetic_fits,dict(kind='orthographic')),
                                   ('photo',photo_cfg,photo_fits,photo_camera)]:
      variants=[('masked_regions',6,3),('cores',6,3)]
      if dataset=='photo':variants += [('cores',10,3),('cores',6,5)]
      for f in fits:
        point=[1364,278];mapping=f['mapping'];metric_cfg=dict(cfg,active_mapping=mapping)
        xy,shape,_=polygons(cfg)
        old_labels=cast(np.array(f['parameters']),xy,f,camera).reshape(shape)
        baseline=metrics(old_labels,metric_cfg,point)
        for method,radius,erosion in variants:
            stem=f'{dataset}-{f["hypothesis"]}-{method}-r{radius}-e{erosion}'
            if stem in cached:
                cases.append(cached[stem]);print('Resumed '+stem,flush=True);continue
            p,loss,optim=optimize(cfg,f,camera,method,point,radius,erosion)
            if camera['kind']=='orthographic':
                independent,provenance=ortho_render(p,f['hand'],cfg['crop'],out,stem)
            else:
                independent,provenance=perspective_render(p,f['hand'],cfg['crop'],camera['focal_px'],
                                                       np.array(camera['principal_xy']),out,stem)
            python=cast(p,xy,f,camera).reshape(shape)
            difference=int((python!=independent).sum())
            assert difference/independent.size<.001,(stem,difference)
            _,data=constraints(xy,shape,polygons(cfg)[2],cfg['held_out'],point,radius,erosion)
            entry=dict(fit_code_sha256=sha(Path(__file__)),dataset=dataset,hypothesis=f['hypothesis'],hand=f['hand'],mapping=mapping,camera=camera,
                method=method,ignore_point_xy=point,ignore_radius_px=radius,erosion_px=erosion,
                parameters=p.tolist(),start_parameters=f['parameters'],python_training_loss=loss,
                pov_training_loss=score(independent,mapping,data,method),baseline_metrics=baseline,
                metrics=metrics(independent,metric_cfg,point),optimizer=optim,ray_pov_mismatches=difference,
                render_provenance=provenance,stem=stem)
            cases.append(entry)
            print(json.dumps(dict(case=stem,loss=entry['pov_training_loss'],C=entry['metrics']['C'],
                F=entry['metrics']['F'],G=entry['metrics']['G'])),flush=True)
            report=dict(request_id='R132',cases=cases,synthetic_provenance=synthetic_provenance,
                synthetic_truth=dict(parameters=true_p,hand=1,mapping=photo_cfg['hypotheses']['H1']),
                evaluation_support=dict(erosion_px=3,ignore_radius_px=6,held_out='G'),
                assistance='R126 assistant polygons and tentative charts, warm-started from frozen fits. No automatic detector or new maker coordinates. Circle radii and erosions are diagnostic choices; P is never assigned an owner.',
                source_sha256={name:sha(ROOT/name) for name in ['beads.pov','beads-photo-2.jpg','photo2/local-fit-r126.json',
                   'photo2/local-surface-review-r130.json','photo2/refine_surface_constraints.py','photo2/local_surface_fit.py',
                   'photo2/check_local_perspective.py','photo2/check_local_surface_fit.py','photo2/review/r126/perspective-report.json',
                   'photo2/review/r126/synthetic-fits.json']})
            (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
