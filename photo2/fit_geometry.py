#!/usr/bin/env python3
"""Compare local orthographic helices on fixed, provisional photo annotations.

This fits unordered center sets, not bead order. No sequence is inferred.
"""
from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

import numpy as np
import scipy
from PIL import Image, ImageDraw
from scipy.optimize import differential_evolution, linear_sum_assignment
from scipy.spatial.distance import cdist

from reconstruct import ClosedPath, HERE, ROOT, digest, sample_rgb

# Finite search domain is part of the experiment, not physical prior knowledge.
GLOBAL_BOUNDS = [(18., 32.), (5., 9.), (22., 55.)]  # pitch, beads/turn, radius
LOCAL_BOUNDS = [(0., 1.), (-np.pi, np.pi), (-20., 20.)]  # axial fraction, phase, n offset


def centers(global_values, local_values, hand, front_only=True, twist=0.):
    pitch, count, radius = global_values
    axial, phase, offset = local_values
    index = np.arange(-16, 112)
    x = (index + axial) * pitch / count
    theta = hand * 2 * np.pi * index / count + phase + twist * (x - 80) / 160
    keep = (x >= -32) & (x <= 192)
    if front_only:
        keep &= np.cos(theta) >= 0
    return np.column_stack([x[keep], offset + radius * np.sin(theta[keep])]), index[keep]


def match(observed, predicted):
    """One-to-one set assignment; never interpret this as chain reconstruction."""
    if len(predicted) < len(observed):
        return np.full(len(observed), 1e6), np.full(len(observed), -1)
    costs = cdist(observed, predicted, metric='sqeuclidean')
    rows, cols = linear_sum_assignment(costs)
    return costs[rows, cols], cols


def fit_shared(patches, hand, seed, maxiter):
    observed = [np.array([[b['x_px'], b['n_px']] for b in p['beads']]) for p in patches]
    def objective(v):
        errors = [match(obs, centers(v[:3], v[3+3*i:6+3*i], hand)[0])[0]
                  for i, obs in enumerate(observed)]
        return float(np.mean(np.concatenate(errors)))
    result = differential_evolution(objective, GLOBAL_BOUNDS + LOCAL_BOUNDS * len(patches),
                                    seed=seed, maxiter=maxiter, popsize=10, tol=1e-7,
                                    polish=False, workers=1)
    return {'seed':seed, 'parameters':result.x.tolist(), 'mse':float(result.fun),
            'converged':bool(result.success), 'message':str(result.message), 'evaluations':result.nfev}


def fit_local(observed, global_values, hand, seed, maxiter=180):
    def objective(v):
        return float(np.mean(match(observed, centers(global_values, v, hand)[0])[0]))
    result = differential_evolution(objective, LOCAL_BOUNDS, seed=seed, maxiter=maxiter,
                                    popsize=12, tol=1e-7, polish=False)
    return result.x, float(result.fun), bool(result.success)


def summarize(errors):
    e = np.sqrt(errors)
    return {'count':len(e), 'rmse_px':float(np.sqrt(np.mean(errors))),
            'median_px':float(np.median(e)), 'p90_px':float(np.quantile(e, .9))}


def photo_xy(path, patch, points):
    xy, _, normal = path.evaluate(patch['start_s_px'] + points[:, 0])
    return xy + points[:, 1, None] * normal


def draw_patch(rgb, path, patch, output, fits):
    s = patch['start_s_px'] + np.arange(161)
    xy, _, normal = path.evaluate(s)
    offsets = np.arange(-65, 66)
    strip = np.uint8(np.clip(sample_rgb(rgb, xy[None] + offsets[:, None, None]*normal[None]), 0, 255))
    # Two copies: unobscured source and annotations, followed by both fitted signs.
    canvas = Image.new('RGB', (700, 580*4), 'white')
    for panel, title in enumerate(['source', 'labels (ID; colors in JSON)', 'hand -1', 'hand +1']):
        origin = 580*panel
        canvas.paste(Image.fromarray(strip).resize((644,524), Image.Resampling.BICUBIC),(40,30+origin))
        d=ImageDraw.Draw(canvas)
        for x in range(0,161,20): d.text((40+4*x,8+origin),str(x),fill='black')
        for n in range(-60,61,20): d.text((3,30+4*(n+65)+origin),str(n),fill='black')
        d.text((40,560+origin),f"{patch['id']}: s={patch['start_s_px']}+x; {title}",fill='black')
        if panel:
            for bead in patch['beads']:
                x,y=40+4*bead['x_px'],30+4*(bead['n_px']+65)+origin
                d.ellipse((x-4,y-4,x+4,y+4),outline='cyan',width=2)
                if panel==1: d.text((x+5,y),bead['id'].split('_')[-1],fill='white',stroke_width=1,stroke_fill='black')
        if panel>=2:
            fit=fits[str(-1 if panel==2 else 1)]
            pred=np.array(fit['predicted_centers'])
            obs=np.array([[b['x_px'],b['n_px']] for b in patch['beads']])
            for a,b in zip(obs,pred):
                ax,ay=40+4*a[0],30+4*(a[1]+65)+origin
                bx,by=40+4*b[0],30+4*(b[1]+65)+origin
                d.line((ax,ay,bx,by),fill='white',width=2)
                d.line((bx-5,by,bx+5,by),fill='lime',width=2)
                d.line((bx,by-5,bx,by+5),fill='lime',width=2)
    canvas.save(output/f"{patch['id']}-comparison.png")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--labels',type=Path,default=HERE/'geometry-labels.json')
    parser.add_argument('--output',type=Path,default=HERE/'output/geometry-fit')
    parser.add_argument('--maxiter',type=int,default=600)
    parser.add_argument('--seeds',type=int,nargs='+',default=[17,43])
    args=parser.parse_args()
    data=json.loads(args.labels.read_text())
    assert data['image_sha256']==digest(ROOT/data['image'])
    assert data['centerline_sha256']==digest(HERE/'centerline.json')
    path=ClosedPath(json.loads((HERE/'centerline.json').read_text())['points'])
    output=args.output;output.mkdir(parents=True,exist_ok=True)
    patches=data['patches']; train=[p for p in patches if p['split']=='train']
    report={'status':'conditional center-set comparison; no accepted hand, count, repeat, or tilt',
            'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},
            'hashes':{str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p):digest(p)
                      for p in [args.labels.resolve(),HERE/'fit_geometry.py',HERE/'reconstruct.py',HERE/'centerline.json',ROOT/data['image']]},
            'bounds':{'global':GLOBAL_BOUNDS,'local':LOCAL_BOUNDS},'seeds':args.seeds,'maxiter':args.maxiter,
            'protocol':'Shared pitch/count/radius from train patches. Validation patches calibrate axial offset/phase/normal offset using x<80 only; x>=80 scores extrapolation. This is partial patch holdout, not zero-calibration whole-patch prediction. Labels fixed for both hands; colors not fitted.',
            'metric':'Euclidean distance in unwrapped source-pixel coordinates, one-to-one assignment. Also report original-photo distances. Extra model beads are unpenalized because annotation completeness is unknown.',
            'hands':{}}
    report['identifiability'] = {
        'local_twist': 'Held at zero in fits: pitch, beads/turn and linear twist have an exact gauge freedom; see GEOMETRY.md and test_fit_geometry.py.',
        'hole_axis_tilt': 'Not fitted: no hole-axis landmarks, and tilt does not enter the center equations.',
        'bead_dimensions': 'Not fitted: centers alone do not measure bead outlines or dimensions.',
        'visibility': 'cos(theta)>=0 is an assumption, not a measured front/back label; removing it admits exact hand reflection.',
        'camera': 'Orthographic approximation only. These labels do not compare camera models.',
        'annotation_count': sum(len(p['beads']) for p in patches),
        'annotation_uncertainty_px': data['center_uncertainty_px'],
    }
    for hand in [-1,1]:
        attempts=[]
        for seed in args.seeds:
            attempt=fit_shared(train,hand,seed,args.maxiter);attempts.append(attempt)
            print(f"hand={hand} seed={seed} train RMSE={np.sqrt(attempt['mse']):.3f} params={attempt['parameters'][:3]}",flush=True)
        best=min(attempts,key=lambda a:a['mse']);v=np.array(best['parameters'])
        fits={};test_errors=[];test_photo_errors=[];train_index=0
        for patch in patches:
            obs=np.array([[b['x_px'],b['n_px']] for b in patch['beads']]);cal=obs[:,0]<80
            if patch['split']=='train':
                local=v[3+3*train_index:6+3*train_index];train_index+=1
                test=np.zeros(len(obs),dtype=bool);local_converged=best['converged']
            else:
                locals_=[fit_local(obs[cal],v[:3],hand,seed) for seed in args.seeds]
                local,_,local_converged=min(locals_,key=lambda r:r[1]);test=~cal
            pred,indices=centers(v[:3],local,hand)
            # Keep validation assignment independent of withheld labels: match
            # calibration first, then withheld labels to unused model beads.
            if patch['split']=='validation':
                errors=np.zeros(len(obs));assigned=np.empty(len(obs),dtype=int)
                errors[cal],assigned[cal]=match(obs[cal],pred)
                available=np.setdiff1d(np.arange(len(pred)),assigned[cal])
                errors[test],cols=match(obs[test],pred[available]);assigned[test]=available[cols]
            else: errors,assigned=match(obs,pred)
            matched=pred[assigned]
            photo_errors=np.sum((photo_xy(path,patch,obs)-photo_xy(path,patch,matched))**2,axis=1)
            test_errors.extend(errors[test]);test_photo_errors.extend(photo_errors[test])
            fits[patch['id']]={'local_parameters':local.tolist(),'local_converged':local_converged,
                'all_centers':summarize(errors),'withheld':summarize(errors[test]) if test.any() else None,
                'photo_withheld':summarize(photo_errors[test]) if test.any() else None,
                'predicted_centers':matched.tolist(),'temporary_model_indices':indices[assigned].tolist(),
                'index_warning':'Local assignment only; not original bead indices or recovered order.'}
        report['hands'][str(hand)]={'attempts':attempts,'selected_seed':best['seed'],
            'global_parameters':v[:3].tolist(),'train_rmse_px':float(np.sqrt(best['mse'])),
            'validation':summarize(np.array(test_errors)),
            'validation_photo':summarize(np.array(test_photo_errors)), 'patches':fits}
    rgb=np.array(Image.open(ROOT/data['image']).convert('RGB'))
    for patch in patches:
        draw_patch(rgb,path,patch,output,{h:r['patches'][patch['id']] for h,r in report['hands'].items()})
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({h:{k:r[k] for k in ['global_parameters','train_rmse_px','validation','validation_photo']} for h,r in report['hands'].items()},indent=2))


if __name__=='__main__':main()
