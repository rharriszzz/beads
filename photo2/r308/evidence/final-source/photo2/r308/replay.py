"""Post-seal corrected structural scoring with unchanged cached native optics.

Only the background, separator and contour blocks changed in the repair. Reuse
all other original native residual blocks, then independently retrace these three
blocks. This is a same-candidate diagnostic, never another search or selection.
"""
import time
import numpy as np
from scipy.ndimage import binary_erosion,binary_dilation,distance_transform_edt
from photo2.r297.common import read,save
from photo2.r307.fast import Chain
from .objective import Objective

def structural(obj,scene,anchors=None):
    tr=scene.trace(obj.xy);own,unknown=tr['owner'],tr['unknown'];start=len(obj.supportxy);c=obj.cues
    o=own[start:start+len(c['xy'])];u=unknown[start:start+len(c['xy'])];start+=len(c['xy']);paper=[]
    for j in range(32):
        keep=obj.cue_sections==j;pp=keep&c['paper'];cc=keep&(c['color']>0)
        if not pp.any() and not cc.any():continue
        paper.append(float(np.mean((o[pp]>=0)|u[pp])) if pp.any() else 0.)
    sep=[]
    for r in obj.separators:
        o=own[start:start+97];u=unknown[start:start+97];start+=97
        changes=np.flatnonzero((o[:-1]!=o[1:])&~u[:-1]&~u[1:])+.5
        sep.append(float(min(abs(changes-r['valley_sample']))*r['representative_distance']/96) if len(changes) else 24.)
    contours=[]
    for ci,cnt in enumerate(obj.contours):
        o=own[start:start+len(cnt['xy'])];u=unknown[start:start+len(cnt['xy'])].reshape(cnt['shape']);start+=len(cnt['xy']);inside=cnt['inside']
        ids,counts=np.unique(o[inside.ravel()&(o>=0)],return_counts=True);k=ids[counts.argmax()] if len(ids) else -1
        if anchors is not None:k=anchors['contours'][ci]-int(scene.indices[0])
        mask=(o==k).reshape(cnt['shape']) if k>=0 else np.zeros(cnt['shape'],bool);edge=mask&~binary_erosion(mask)&~binary_dilation(u);oe=inside&~binary_erosion(inside);signed=cnt['signed']
        dist=distance_transform_edt(~edge)*cnt['step'] if edge.any() else np.full(mask.shape,40.);forward=float(np.mean(np.maximum(0,dist[oe]-3)));reverse=float(np.mean(np.maximum(0,abs(signed[edge])-3))) if edge.any() else 30.
        inner=signed< -3;outside=signed>3;miss=float(np.mean(~mask[inner])) if inner.any() else 0.;excess=float(np.sum(mask&outside)/max(1,inside.sum()));contours.append([forward/3,reverse/3,np.sqrt(miss)/.5,np.sqrt(excess)/.4])
    return dict(background=4*np.mean(np.array(paper)/.25**2),separator=1.5*np.mean((np.array(sep)/4)**2),visible_boundary=3*np.mean(np.square(contours)))

def replay(out,data,m,obs):
    target=out/'corrected-response-replay.json'
    if target.exists():return read(target)
    curves=read(out/'response-curves.json');pairs=read(out/'response-pairs.json');ids=sorted({r['trial'] for d in curves+pairs for r in d['rows'] if r['feasible']});obj=Objective(data,m,obs);records=[]
    for i in ids:
        trial=read(out/'trials'/f'{i:06d}.json.gz');s=Chain(trial['parameters'],data);b=structural(obj,s);loss=trial['result']['loss']+sum(b[k]-trial['result']['blocks'][k] for k in b)
        records.append(dict(trial=i,original_loss=trial['result']['loss'],corrected_loss=float(loss),changed_blocks=b))
    result=dict(records=records,policy='After seal, same native hypotheses: independently retrace repaired structural blocks; reuse original native optical/coherence/other blocks. No geometry or correspondence change, no new candidate search. Curves were free-assignment evaluations, so modal contour owners are identical.')
    save(target,result);return result

def all_candidates(out,data,m,obs):
    from photo2.r297.common import digest,sha,ROOT,utc
    from copy import deepcopy
    began=time.monotonic();path=out/'all-candidate-corrected-ranking.json'
    if path.exists():return read(path)
    obj=Objective(data,m,obs);records=[];cache={};current=sha(ROOT/'photo2/r308/objective.py')
    for file in sorted((out/'trials').glob('*.gz')):
        trial=read(file)
        if not trial['feasible']:continue
        if trial.get('objective_sha')==current:blocks={k:trial['result']['blocks'][k] for k in ['background','separator','visible_boundary']}
        else:
            key=digest(dict(p=trial['parameters'],contours=trial['anchors']['contours']))
            if key not in cache:cache[key]=structural(obj,Chain(trial['parameters'],data),trial['anchors'])
            blocks=cache[key]
        loss=trial['result']['loss']+sum(blocks[k]-trial['result']['blocks'][k] for k in blocks)-trial['result'].get('correction_penalty',0.)
        records.append(dict(trial=trial['id'],tag=trial['tag'],corrected_photographic_loss=float(loss),native_missing=trial['result']['unmatched'],initial_objective=trial.get('objective_sha','pre-repair'),parameters_digest=digest(trial['parameters'])))
        if len(records)%50==0:print('Corrected retained-candidate audit',len(records),flush=True)
    records.sort(key=lambda r:r['corrected_photographic_loss'])
    result=dict(utc=utc(),seconds=time.monotonic()-began,records=records,unique_retraced_structures=len(cache),policy='No new proposals: repair-score replay of every retained feasible native trial, fixed original trial owners. Unchanged optical/coherence blocks reused, changed structural blocks retraced. Correction penalty removed for uniform photographic ranking. No comparison evidence is consulted.')
    save(path,result);return result
