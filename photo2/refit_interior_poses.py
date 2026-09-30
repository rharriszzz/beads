"""R160 bounded multistart fit to maker-confirmed positive interiors.

No boundary/outside loss. Black color certainty does not imply known extent.
The whole 22/23/24/25 group stays evaluator-only. Manual assistance is explicit.
"""
import argparse,json,time
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares,minimize
from curved_surface_fit import point_residual,anchors
from fit_curved_patch import load,setup,HELD,NUMBERS
from score_interior_poses import photo_samples,synthetic_samples,score
from check_placement import ROOT,sha


def training_data(xy,numbers,samples,coarse=False):
    """Filter held-out locations before deriving any fitting data."""
    use=np.array([int(n) not in HELD for n in numbers])
    groups=[dict(kind='marks',xy=xy[use],numbers=np.asarray(numbers)[use],weight=.5)]
    for n,s in samples.items():
        if n in HELD:raise ValueError('Held-out bead supplied as an interior')
        core=s['core'];route=s['route']
        if coarse:
            keep=(core[:,0].astype(int)%3==0)&(core[:,1].astype(int)%3==0)
            core=core[keep] if keep.any() else core[:1]
            route=route[::4]
        for kind,points in [('core',core),('route',route)]:
            groups.append(dict(kind=kind,xy=points,numbers=np.full(len(points),n),weight=.25/len(samples)))
    return groups


def residual(p,groups,mapping,hand,focal):
    values=[]
    for group in groups:
        target=np.asarray(mapping)[group['numbers']-1]
        guide,_,_=point_residual(p,group['xy'],target,hand,focal)
        values.extend(guide*np.sqrt(group['weight']/len(guide)))
    return np.array(values)


def evaluate(p,xy,numbers,samples,mapping,hand,focal):
    indices=np.asarray(mapping)[numbers-1]
    _,owner,unfinished=point_residual(p,xy,indices,hand,focal)
    use=np.array([int(n) not in HELD for n in numbers])
    interiors=score(p,hand,focal,mapping,samples)
    return dict(training_marks_pass=int(np.sum(owner[use]==indices[use])),training_marks_total=int(use.sum()),
        heldout_marks_pass=int(np.sum(owner[~use]==indices[~use])),heldout_marks_total=int((~use).sum()),
        mark_ray_unfinished=unfinished,mark_failures=[dict(number=int(n),expected=int(i),owner=int(o),
            role='training' if n not in HELD else 'held-out') for n,i,o in zip(numbers,indices,owner) if i!=o],
        interiors=interiors)


def fit(p,xy,numbers,samples,mapping,hand,focal,q_fixed,maxfev):
    coarse=training_data(xy,numbers,samples,True);full=training_data(xy,numbers,samples,False)
    _,_,_,_,_,lo,hi=setup(xy,np.asarray(mapping)[numbers-1],numbers)
    if q_fixed is not None:lo[8]=q_fixed-1e-10;hi[8]=q_fixed+1e-10
    p=np.clip(np.array(p,float),lo+1e-12,hi-1e-12)
    best=[float(np.sum(residual(p,full,mapping,hand,focal)**2)),p.copy()]
    before=evaluate(p,xy,numbers,samples,mapping,hand,focal)
    stages=[]
    if best[0]>0:
        coarse_fit=least_squares(lambda v:residual(v,coarse,mapping,hand,focal),p,
            bounds=(lo,hi),max_nfev=90,ftol=1e-5,xtol=1e-5,gtol=1e-5)
        p=coarse_fit.x
        value=float(np.sum(residual(p,full,mapping,hand,focal)**2))
        if value<best[0]:best[:]=[value,p.copy()]
        stages.append(dict(method='coarse least squares',reported_evaluations=int(coarse_fit.nfev),
            success=bool(coarse_fit.success),message=str(coarse_fit.message),full_guide_loss=value))
        # Refine all confirmed pixels after the cheap sparse proposal. Keep best
        # visited full-data pose; a line search endpoint may be worse.
        p=best[1].copy();count=0
        def loss(v):
            nonlocal count
            count+=1
            value=float(np.sum(residual(v,full,mapping,hand,focal)**2))
            if value<best[0]:best[:]=[value,v.copy()]
            return value
        widths=np.array([25,25,3,30,35,45,50,.025,.05])
        bounds=list(zip(np.maximum(lo,p-widths),np.minimum(hi,p+widths)))
        if best[0]>0:
            result=minimize(loss,p,method='Powell',bounds=bounds,
                options={'maxfev':maxfev,'maxiter':50,'xtol':.0005,'ftol':1e-6})
            stages.append(dict(method='full positive-sample Powell',evaluations=count,
                success=bool(result.success),message=str(result.message),best_full_guide_loss=best[0]))
    p=best[1]
    after=evaluate(p,xy,numbers,samples,mapping,hand,focal)
    anchor_xy,exposed,owner,gap,unfinished=anchors(p,np.asarray(mapping)[numbers-1],hand,focal)
    return dict(parameters=p.tolist(),before=before,after=after,guide_loss=best[0],stages=stages,
        outward_predictions=[dict(number=int(n),xy=a.tolist(),exposed=bool(e),owner=int(o),
            front_minus_anchor_depth=float(g) if np.isfinite(g) else None) for n,a,e,o,g in zip(numbers,anchor_xy,exposed,owner,gap)],
        anchor_ray_unfinished=unfinished)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--maxfev',type=int,default=700)
    args=parser.parse_args()
    out=ROOT/'photo2/review/r160';out.mkdir(parents=True,exist_ok=True)
    old_path=ROOT/'photo2/review/r156/report.json';old=json.loads(old_path.read_text())
    loop_path=ROOT/'photo2/review/r157/report.json';loops=json.loads(loop_path.read_text())
    photo=photo_samples(loops);synth,truth=synthetic_samples(old,ROOT/'photo2/output/r160')
    xy,mapping=load()
    report=dict(old_fits_sha256=sha(old_path),loops_sha256=sha(loop_path),
        confirmation_sha256=sha(ROOT/'photo2/interior-confirmed-r160.json'),
        fitter_sha256=sha(Path(__file__)),kernel_sha256=sha(ROOT/'photo2/curved_surface_fit.py'),
        heldout_numbers=sorted(HELD),maxfev=args.maxfev,synthetic=truth,
        objective='Half equal-weight training-mark loss plus half equal-weight five-body interior loss; per body core/route equal; no outside loss',
        observation_ids=old['observation_ids'],mappings=old['mappings'],cases=[])
    for case_index,c in enumerate(old['cases']):
        # Both winding signs are kept. Every old retained pose gets equal caps;
        # no held-out score or maker color selects a start.
        if c['dataset']=='synthetic':
            points=np.array(old['synthetic_truth']['points']);numbers=np.array(old['synthetic_truth']['numbers']);samples=synth
        else:points=xy;numbers=NUMBERS;samples=photo
        for rank,start in enumerate(c['retained']):
            began=time.monotonic()
            result=fit(start['parameters'],points,numbers,samples,old['mappings'][c['family']],
                c['hand'],c['focal'],c['q_fixed'],args.maxfev)
            result.update(case_index=case_index,start_rank=rank,dataset=c['dataset'],family=c['family'],
                hand=c['hand'],focal=c['focal'],q_fixed=c['q_fixed'],seconds=time.monotonic()-began)
            report['cases'].append(result)
            (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
            print(json.dumps(dict(case=case_index,rank=rank,dataset=c['dataset'],family=c['family'],
                hand=c['hand'],seconds=result['seconds'],guide=result['guide_loss'],
                marks=[result['after']['training_marks_pass'],result['after']['heldout_marks_pass']],
                core=result['after']['interiors']['mean_core_fraction'],route=result['after']['interiors']['mean_route_fraction'])),flush=True)


if __name__=='__main__':main()
