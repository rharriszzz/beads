"""Bounded, manually assisted 27-body comparison. Never an automatic detector.

Maker marks are arbitrary visible-surface points, not centers/outward anchors.
The entire 22/23/24/25 group is withheld from pose fitting and candidate ranking.
"""
import argparse,json,time
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares,minimize
from scipy.ndimage import distance_transform_edt
from curved_surface_fit import geometry,project,point_residual,anchors,ROW,NOMINAL_FOCAL
from check_placement import ROOT,sha
from check_curved_patch import render

HELD={22,23,24,25}
NUMBERS=np.arange(1,28)


def load():
    annotations=json.loads((ROOT/'photo2/manual-labels-r146.json').read_text())
    xy=np.array([[a['x'],a['y']] for a in sorted(annotations['annotations'],key=lambda a:a['number'])])
    chart=json.loads((ROOT/'photo2/review/r144/corrected-report.json').read_text())['conditional_charts'][0]
    mappings={}
    for name,weight in [('A',{'d1':1,'d2':7,'d3':6}),('B',{'d1':-1,'d2':6,'d3':7})]:
        candidate=next(c for c in chart['relative_index_candidates'] if c['weights']==weight)
        mappings[name]=np.array([candidate['offsets'][str(i)]-candidate['offsets']['20'] for i in NUMBERS])
    return xy,mappings


def setup(xy,indices,numbers):
    """Every location-derived bound/seed uses the training subset only."""
    use=np.array([i not in HELD for i in numbers])
    xy=xy[use];indices=indices[use]
    differences=[]
    for i in range(len(indices)):
        for j in range(i+1,len(indices)):
            if indices[j]-indices[i]==13:
                differences.append((xy[j]-xy[i])/(13*ROW/6.5))
    if not differences:raise ValueError('Training chart needs a 13-step pair')
    advance=np.median(differences,axis=0)
    scale=np.linalg.norm(advance);angle=np.degrees(np.arctan2(advance[1],advance[0]))
    origin=xy[indices==0][0] if np.any(indices==0) else xy.mean(axis=0)
    lo=np.array([origin[0]-70,origin[1]-70,scale*.65,angle-180,5,-179.9,-540,-.045,6.45])
    hi=np.array([origin[0]+70,origin[1]+70,scale*2.8,angle+180,89.5,179.9,540,.045,6.55])
    return xy,indices,origin,scale,angle,lo,hi


def proposals(xy,indices,hand,numbers,focal=None,q_fixed=None):
    train,target,origin,scale,angle,lo,hi=setup(xy,indices,numbers)
    if q_fixed is not None:
        lo[8]=q_fixed-1e-10;hi[8]=q_fixed+1e-10
    fits=[]
    for el in [30,70]:
      for az in [-145,-25,25,145]:
       for phase in [-90,90]:
        for k in [-.015,.015]:
            p=np.array([*origin,scale*1.15,angle,el,az,phase,k,6.5 if q_fixed is None else q_fixed])
            fit=least_squares(lambda v:(project(v,geometry(v,target,hand)[4],focal)-train).ravel(),
                p,bounds=(lo,hi),max_nfev=120,ftol=1e-5,xtol=1e-5,gtol=1e-5)
            guide,owner,u=point_residual(fit.x,train,target,hand,focal)
            fits.append(dict(parameters=fit.x.tolist(),proposal_mse=float(np.mean(fit.fun**2)),
                ownership=int(np.sum(owner==target)),guide=float(np.mean(guide**2)),unfinished=u,
                converged=bool(fit.success)))
    return sorted(fits,key=lambda a:(-a['ownership'],a['guide'],a['proposal_mse'])),(train,target,lo,hi)


def fit_case(xy,indices,hand,numbers,focal=None,maxfev=550,q_fixed=None):
    starts,(train,target,lo,hi)=proposals(xy,indices,hand,numbers,focal,q_fixed)
    diverse=[];signatures=[]
    for start in starts:
        v=np.array(start['parameters']);c,t,n,line,outer=geometry(v,target,hand)
        signature=project(v,np.concatenate((c,c+t,outer)),focal)
        if any(np.sqrt(np.mean((signature-s)**2))<.25 for s in signatures):continue
        diverse.append(start);signatures.append(signature)
        if len(diverse)==3:break
    retained=[]
    for rank,start in enumerate(diverse):
        p=np.array(start['parameters']); best=[float(start['guide']),p.copy()]
        count=0
        def loss(v):
            nonlocal count
            count+=1
            residual,_,_=point_residual(v,train,target,hand,focal)
            value=float(np.mean(residual**2))
            if value<best[0]:best[:]=[value,v.copy()]
            return value
        # Small bounded pose refinement; retain best visited candidate even when
        # a discontinuous line search finishes at a worse point or hits its cap.
        widths=np.array([18,18,2.5,20,20,30,35,.02,.04])
        bounds=list(zip(np.maximum(lo,p-widths),np.minimum(hi,p+widths)))
        if best[0]>0:
            opt=minimize(loss,p,method='Powell',bounds=bounds,
                         options={'maxfev':maxfev,'maxiter':40,'xtol':.001,'ftol':1e-5})
            success=bool(opt.success);message=str(opt.message)
        else:success=True;message='Proposal already meets every training point; no refinement.'
        p=best[1]
        residual,owner,u=point_residual(p,xy,indices,hand,focal)
        use=np.array([i not in HELD for i in numbers])
        axy,exposed,aowner,gap,au=anchors(p,indices,hand,focal)
        observations=[]
        for j,n in enumerate(numbers):
            observations.append(dict(number=int(n),relative_index=int(indices[j]),
                role='training' if use[j] else 'held-out',point=xy[j].tolist(),
                point_owner=int(owner[j]),point_pass=bool(owner[j]==indices[j]),
                outward_xy=axy[j].tolist(),outward_exposed=bool(exposed[j]),
                outward_owner=int(aowner[j]),front_minus_anchor_depth=float(gap[j]) if np.isfinite(gap[j]) else None))
        retained.append(dict(start_rank=rank,parameters=p.tolist(),guide_loss=best[0],
            training_pass=int(np.sum(owner[use]==indices[use])),training_total=int(use.sum()),
            heldout_pass=int(np.sum(owner[~use]==indices[~use])),heldout_total=int((~use).sum()),
            point_ray_unfinished=u,anchor_ray_unfinished=au,outward_exposed=int(exposed.sum()),
            observations=observations,evaluations=count,optimizer_success=success,
            optimizer_message=message,seed=start))
    # Held-out scores and predicted anchors never enter selection.
    return dict(hand=hand,focal=focal,q_fixed=q_fixed,retained=retained,proposal_count=len(starts),
                capped_proposals=sum(not v['converged'] for v in starts),
                training_bounds=[lo.tolist(),hi.tolist()])


def synthetic(mappings,out):
    """One known curved POV example; missing/hidden bodies stay missing."""
    p=[1345,285,8,-8,60,15,10,.018,6.5];hand=1
    crop=[1170,200,1510,385]
    labels,provenance=render(p,hand,crop,out,'synthetic-truth')
    numbers=[];points=[];missing=[]
    for number,index in zip(NUMBERS,mappings['A']):
        mask=labels==index
        dt=distance_transform_edt(mask)
        if dt.max()<3:
            missing.append(int(number));continue
        y,x=np.unravel_index(np.argmax(dt),dt.shape)
        numbers.append(int(number));points.append([int(x+crop[0]),int(y+crop[1])])
    return np.array(points),np.array(numbers),dict(parameters=p,hand=hand,family='A',
        crop=crop,missing_numbers=missing,points=points,numbers=numbers,**provenance)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--maxfev',type=int,default=550)
    args=parser.parse_args()
    out=ROOT/'photo2/output/r156';out.mkdir(parents=True,exist_ok=True)
    review=ROOT/'photo2/review/r156';review.mkdir(parents=True,exist_ok=True)
    xy,mappings=load();sx,sn,truth=synthetic(mappings,out)
    report=dict(heldout_numbers=sorted(HELD),parameter_order=['tx','ty','pixels_per_unit','roll_deg',
        'elevation_deg','azimuth_deg','phase_deg','signed_curvature_per_unit','beads_per_row_q'],
        annotation_sha256=sha(ROOT/'photo2/manual-labels-r146.json'),
        image_sha256=sha(ROOT/'beads-photo-2.jpg'),source_sha256=sha(ROOT/'beads.pov'),
        kernel_sha256=sha(ROOT/'photo2/curved_surface_fit.py'),fitter_sha256=sha(Path(__file__)),
        checker_sha256=sha(ROOT/'photo2/check_curved_patch.py'),mappings={k:v.tolist() for k,v in mappings.items()},
        observation_ids={str(a['number']):a['id'] for a in
            json.loads((ROOT/'photo2/manual-labels-r146.json').read_text())['annotations']},
        maxfev=args.maxfev,synthetic_truth=truth,cases=[])
    for dataset,points,numbers,focals,q_fixed in [('synthetic',sx,sn,[None],None),
            ('photo',xy,NUMBERS,[None,NOMINAL_FOCAL],None),('photo',xy,NUMBERS,[None],6.5)]:
      for focal in focals:
       for family,allindices in mappings.items():
        for hand in [1,-1]:
            start=time.monotonic()
            indices=allindices[numbers-1]
            result=fit_case(points,indices,hand,numbers,focal,args.maxfev,q_fixed)
            result.update(dataset=dataset,family=family,seconds=time.monotonic()-start)
            report['cases'].append(result)
            (review/'report.json').write_text(json.dumps(report,indent=2)+'\n')
            print(json.dumps(dict(dataset=dataset,family=family,hand=hand,focal=focal,q_fixed=q_fixed,
                seconds=result['seconds'],scores=[(v['training_pass'],v['heldout_pass'],v['outward_exposed']) for v in result['retained']])),flush=True)


if __name__=='__main__':main()
