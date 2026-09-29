"""R135 assisted boundary brackets plus supported interiors; G withheld."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-matplotlib')
import argparse,json
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from matplotlib.path import Path as MPath
from local_surface_fit import ROOT,IDS,polygons
from refine_surface_constraints import constraints,cast,metrics
from check_local_surface_fit import render as ortho_render
from check_local_perspective import render as perspective_render
from check_placement import sha


def arc_samples(arcs,point,radius,halfwidth=3,step=3,regions=None):
    """Pairs outside a diagnostic uncertainty band; no ownership at the arc."""
    samples=[]
    for arc in arcs:
        pts=np.array(arc['points'],float);hint=np.array(arc['interior_hint'],float)
        for a,b in zip(pts[:-1],pts[1:]):
            v=b-a;length=np.linalg.norm(v)
            if length==0:continue
            normal=np.array([-v[1],v[0]])/length
            if np.dot(normal,hint-(a+b)/2)<0:normal=-normal
            for t in (np.arange(max(1,int(np.ceil(length/step))))+.5)/max(1,int(np.ceil(length/step))):
                center=a+t*v
                # Both samples must be clear of P; arc coordinates remain unowned.
                for offset in [halfwidth+1,halfwidth+3]:
                    pair=np.array([center+offset*normal,center-offset*normal])
                    if np.any(np.linalg.norm(pair-np.array(point),axis=1)<=radius):continue
                    if regions is not None:
                        contained=MPath(regions[arc['body']]).contains_points(pair)
                        if not (contained[0] and not contained[1]):continue
                    samples.append(dict(arc=arc['id'],body=arc['body'],center=center.tolist(),
                        inside=pair[0].tolist(),outside=pair[1].tolist(),offset=float(offset)))
    return samples


def support(cfg,arcs,halfwidth=3,spacing=1,ignore_radius=6):
    xy,shape,masks=polygons(cfg,spacing)
    _,data=constraints(xy,shape,masks,cfg['held_out'],[1364,278],ignore_radius,3,spacing)
    selected=[a for a in arcs if a['body']!=cfg['held_out']]
    pairs=arc_samples(selected,[1364,278],ignore_radius,halfwidth,regions=cfg['observations'])
    allxy=[];core_ranges={};pair_ranges={};cursor=0
    for k,d in data.items():
        pts=xy[d['core'].ravel()];allxy.extend(pts);core_ranges[k]=(cursor,cursor+len(pts));cursor+=len(pts)
    for k in sorted({p['body'] for p in pairs}):
        chosen=[p for p in pairs if p['body']==k]
        pts=np.array([[p['inside'],p['outside']] for p in chosen]).reshape(-1,2)
        allxy.extend(pts);pair_ranges[k]=(cursor,cursor+len(pts));cursor+=len(pts)
    return np.array(allxy),core_ranges,pair_ranges,pairs


def losses(labels,mapping,core_ranges,pair_ranges,weight=1):
    cores=[float(np.mean(labels[a:b]!=mapping[k])) for k,(a,b) in core_ranges.items() if b>a]
    perbody={}
    for k,(a,b) in pair_ranges.items():
        own=(labels[a:b]==mapping[k]).reshape(-1,2)
        perbody[k]=float(np.mean(np.column_stack((~own[:,0],own[:,1]))))
    core=float(np.mean(cores));boundary=float(np.mean(list(perbody.values()))) if perbody else 0.
    return dict(total=core+weight*boundary,core_miss=core,bracket_miss=boundary,bracket_by_body=perbody)


def optimize(cfg,arcs,starts,camera,halfwidth,weight=1,maxfev=350):
    reference=np.array(starts[0]['parameters']);free=np.array([0,1,2,3,5,6])
    width=np.array([10,10,2,12,0,15,25]);bounds=list(zip((reference-width)[free],(reference+width)[free]))
    stages=[];best=None
    for restart,f in enumerate(starts):
        p=np.array(f['parameters']);p[free]=np.clip(p[free],reference[free]-width[free],reference[free]+width[free])
        for spacing in [2,1]:
            xy,cores,pairs,_=support(cfg,arcs,halfwidth,spacing)
            def unpack(v):
                q=p.copy();q[free]=v;return q
            def objective(v):return losses(cast(unpack(v),xy,f,camera),f['mapping'],cores,pairs,weight)['total']
            initial=objective(p[free])
            fit=minimize(objective,p[free],method='Powell',bounds=bounds,
                options=dict(maxfev=maxfev,maxiter=20,xtol=.005,ftol=.0001))
            accepted=fit.fun<=initial
            if accepted:p=unpack(fit.x)
            stages.append(dict(restart=restart,spacing=spacing,nfev=int(fit.nfev),success=bool(fit.success),
                message=str(fit.message),initial_loss=float(initial),final_loss=float(fit.fun),accepted=bool(accepted)))
        value=objective(p[free])
        if best is None or value<best[0]:best=(value,p.copy())
    return best[1],stages


def synthetic_arcs(cfg):
    """Supply diagnostic arcs from known contours; truth not an initializer."""
    arcs=[]
    for name,body,angles in [('L','C',(140,220)),('S','C',(40,120)),('R','B',(-30,70))]:
        pts=np.array(cfg['observations'][body]);hint=pts.mean(axis=0)
        theta=np.degrees(np.arctan2(pts[:,1]-hint[1],pts[:,0]-hint[0]))
        keep=(theta>=angles[0])&(theta<=angles[1])
        # Save consecutive segments individually: never connect across omitted contour.
        for i in range(len(pts)-1):
            if keep[i] and keep[i+1]:
                arcs.append(dict(id=name,body=body,points=pts[i:i+2].tolist(),interior_hint=hint.tolist()))
    return arcs


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--resume',action='store_true')
    ap.add_argument('--synthetic-only',action='store_true');args=ap.parse_args()
    out=ROOT/'photo2/output/r135';out.mkdir(parents=True,exist_ok=True)
    config=json.loads((ROOT/'photo2/local-fit-r126.json').read_text())
    annotation=json.loads((ROOT/'photo2/boundary-arcs-r135.json').read_text())
    old=json.loads((ROOT/'photo2/review/r132/report.json').read_text())
    # R132's frozen truth pose supplies the independent POV example only.
    truth=old['synthetic_truth'];actual,truth_provenance=ortho_render(truth['parameters'],truth['hand'],config['crop'],out,'synthetic-truth')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    scfg=dict(config,image=None,observations={})
    for k,index in truth['mapping'].items():
        fig,ax=plt.subplots();segments=ax.contour((actual==index).astype(float),levels=[.5]).allsegs[0]
        contour=max(segments,key=len);plt.close(fig)
        scfg['observations'][k]=(contour[::2]+np.array(config['crop'][:2])).tolist()
    sources=['beads-photo-2.jpg','beads.pov','photo2/local-fit-r126.json','photo2/boundary-arcs-r135.json',
        'photo2/fit_boundary_arcs.py','photo2/refine_surface_constraints.py','photo2/local_surface_fit.py',
        'photo2/check_local_perspective.py','photo2/check_local_surface_fit.py','photo2/review/r132/report.json']
    hashes={n:sha(ROOT/n) for n in sources};cases=[]
    if args.resume and (out/'report.json').exists():
        prev=json.loads((out/'report.json').read_text());assert prev['source_sha256']==hashes,'Changed source cannot resume'
        cases=prev['cases']
    datasets=[('synthetic',scfg,synthetic_arcs(scfg))]
    if not args.synthetic_only:datasets.append(('photo',config,annotation['arcs']))
    for dataset,cfg,arcs in datasets:
      for chart in ['H1','H2']:
        starts=[c for method in ['masked_regions','cores'] for c in old['cases']
            if c['dataset']==dataset and c['hypothesis']==chart and c['method']==method and c['ignore_radius_px']==6 and c['erosion_px']==3]
        camera=starts[0]['camera']
        for halfwidth in ([3] if dataset=='synthetic' else [3,5]):
            stem=f'{dataset}-{chart}-band{halfwidth}'
            if any(c['stem']==stem for c in cases):print('Resumed '+stem,flush=True);continue
            p,stages=optimize(cfg,arcs,starts,camera,halfwidth)
            hand=starts[0]['hand'];mapping=starts[0]['mapping'];f=dict(hand=hand,mapping=mapping)
            if dataset=='synthetic':labels,provenance=ortho_render(p,hand,cfg['crop'],out,stem)
            else:labels,provenance=perspective_render(p,hand,cfg['crop'],camera['focal_px'],np.array(camera['principal_xy']),out,stem)
            xy,shape,_=polygons(cfg);pred=cast(p,xy,f,camera).reshape(shape);diff=int((pred!=labels).sum())
            assert diff/labels.size<.001,(stem,diff)
            # Training brackets use Python at subpixel coordinates. Final full-grid
            # ownership and reported region metrics are independently POV checked.
            q,core,pairs,samples=support(cfg,arcs,halfwidth)
            support_score=losses(cast(p,q,f,camera),mapping,core,pairs)
            candidate_pairs=arc_samples(arcs,[1364,278],6,halfwidth)
            truth_training=None
            if dataset=='synthetic':
                truth_training=losses(cast(np.array(truth['parameters']),q,dict(hand=truth['hand']),camera),truth['mapping'],core,pairs)
                assert truth_training['total']==0,truth_training
            evalcfg=dict(cfg,active_mapping=mapping)
            entry=dict(stem=stem,dataset=dataset,hypothesis=chart,hand=hand,mapping=mapping,camera=camera,
                parameters=p.tolist(),start_parameters=[s['parameters'] for s in starts],halfwidth_px=halfwidth,
                bracket_weight=1.,optimizer=stages,training=support_score,
                metrics=metrics(labels,evalcfg,[1364,278]),ray_pov_mismatches=diff,
                arcs=arcs,samples=samples,region_rejected_pairs=len(candidate_pairs)-len(samples),
                synthetic_truth_training=truth_training,render_provenance=provenance)
            cases.append(entry)
            report=dict(request_id='R135',cases=cases,source_sha256=hashes,synthetic_truth=truth,
                synthetic_provenance=truth_provenance,synthetic_config=scfg,
                limits='Assistant arcs/polygons, fixed shape and tentative maps; no automatic detector, global optimum, camera elevation, accepted chart or recovered indices.',
                evaluation_support=dict(erosion_px=3,ignore_radius_px=6,held_out='G'))
            (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
            print(json.dumps({k:entry[k] for k in ['stem','training','metrics','ray_pov_mismatches']}),flush=True)

if __name__=='__main__':main()
