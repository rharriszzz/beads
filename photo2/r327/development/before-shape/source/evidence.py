"""Cross-predicted native evidence; alternative fits are never contradictions.
All geometry is shared across colors. Sigma concerns reflection localization.
Predictions exclude the scored target, but candidate discovery used these supports:
this is cross-prediction, NOT independent validation.
"""
from collections import Counter
import numpy as np
from scipy.ndimage import gaussian_filter, map_coordinates
from photo2.r325.candidates import signature

STEPS=((1,0),(0,1),(1,-1))

def maps(rgb):
    linear=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4)
    r,g,b=linear.transpose(2,0,1)
    channels={'black':np.minimum(np.minimum(r,g),b),'red':np.maximum(r-np.maximum(g,b),0),'yellow':np.maximum(np.minimum(r,g)-b,0)}
    return {c:gaussian_filter(v,3) for c,v in channels.items()}

def sample(field,xy):
    xy=np.asarray(xy);return map_coordinates(field,[xy[...,1].ravel(),xy[...,0].ravel()],order=1,mode='nearest').reshape(xy.shape[:-1])

def predict(ab,xy,target,train,curved=False):
    # Target-centered coordinates and locality prevent remote affine distortion.
    u=ab-ab[target];scale=max(float(np.median(np.linalg.norm(u[train],axis=1))),1.)
    u=u/scale
    X=np.column_stack([np.ones(len(u)),u])
    if curved:X=np.column_stack([X,u[:,0]**2,u[:,0]*u[:,1],u[:,1]**2])
    if len(train)<(6 if curved else 4) or np.linalg.matrix_rank(X[train,:3])<3:return None
    wt=np.exp(-np.sum(u[train]**2,axis=1)/8)
    ridge=np.diag([0.,0.,0.]+([2.,2.,2.] if curved else []))
    coef=np.linalg.lstsq(X[train].T@(wt[:,None]*X[train])+ridge,X[train].T@(wt[:,None]*xy[train]),rcond=None)[0]
    return coef[0]

def evaluate(h,op,fields):
    ids=sorted(h['assignments']);ab=np.array([h['assignments'][o]['ab'] for o in ids]);xy=np.array([op[o]['xy'] for o in ids]);rows=[];utilities={}
    colored=np.array([op[o]['color']!='black' for o in ids])
    for i,o in enumerate(ids):
        train=np.flatnonzero(np.arange(len(ids))!=i);kind='all other supports'
        if not colored[i] and colored.sum()>=6:train=np.flatnonzero(colored);kind='colored supports only'
        predictions=[predict(ab,xy,i,train,c) for c in (False,True)];predictions=[p for p in predictions if p is not None]
        if not predictions:continue
        sigma=8. if not colored[i] else 5.;field=fields[op[o]['color']];observed=float(sample(field,xy[i]));ps=np.array(predictions);err=np.linalg.norm(ps-xy[i],axis=1)
        values=sample(field,ps);ratio=np.clip(values/max(observed,1e-6),0,1)
        # Absence is not contradiction: low response loses a positive reward.
        geom=float(np.mean(np.exp(-.5*(err/sigma)**2)));pixel=float(np.mean(ratio))
        utility=.75*geom+.25*pixel;utilities[o]=utility
        rows.append(dict(observation=o,anchor_ids=[ids[j] for j in train],anchor_kind=kind,predictions_xy=ps.tolist(),errors_px=err.tolist(),sigma_px=sigma,observed_native_response=observed,predicted_native_responses=values.tolist(),geometry_support=geom,pixel_support=pixel,utility=utility,evidence_class='cross-predicted photographic support' if geom>=.5 else 'prediction mismatch; not an established image contradiction'))
    lookup={tuple(a):o for a,o in zip(ab,ids)};runs=[]
    for d in STEPS:
        for cell,o in lookup.items():
            if (cell[0]-d[0],cell[1]-d[1]) in lookup:continue
            run=[];k=cell
            while k in lookup:run.append(lookup[k]);k=(k[0]+d[0],k[1]+d[1])
            if len(run)>=4:
                # Geometric mean requires mutually supported observations, rather
                # than rewarding connectivity alone. Cap length, not evidence.
                quality=float(np.exp(np.mean(np.log([max(utilities.get(s,0),1e-4) for s in run]))))
                runs.append(dict(step=list(d),observations=run,quality=quality,reward=min(len(run)-3,3)*quality))
    support=float(sum(utilities.values()));sequence=float(sum(r['reward'] for r in runs))
    return dict(support=support,sequence=sequence,rows=rows,runs=runs,score=support+.35*sequence)

def score_bank(windows,op,fields,cache):
    added=0
    for w in windows:
        for h in w['hypotheses']:
            k=signature(h)
            if k not in cache:cache[k]=evaluate(h,op,fields);added+=1
            ev=cache[k];h['r327_evidence']=ev
            # Preserve discovery score; discard R326 disagreement/message penalties.
            h.setdefault('photo_score',h['score']);h['score']=.35*h['photo_score']+ev['score']
    return added
