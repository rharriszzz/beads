"""Separate evaluation: exact native supports, conditional assignment hypotheses."""
import argparse,datetime
import numpy as np
from scipy.spatial import cKDTree
from .common import *
from .geometry import Chain,extend,AXES
from .fit import Objective

def observations(scene,data,splits=None):
    rows=[r for r in data['rows'] if splits is None or r['split'] in splits];out=[]
    for r in rows:
        xy=pixels(r['pixels']);q=scene.trace(xy);ids,count=np.unique(q['owner'],return_counts=True)
        alt=sorted([dict(index=int(scene.indices[k]),fraction=float(v/len(xy))) for k,v in zip(ids,count) if k>=0],key=lambda a:-a['fraction'])
        k=alt[0]['index'] if alt else None;fraction=alt[0]['fraction'] if alt else 0.;rival=alt[1]['fraction'] if len(alt)>1 else 0.
        out.append(dict(id=r['id'],kind=r['kind'],split=r['split'],historical_split=r['historical_split'],color=r['color'],point=r['point'],along_px=r['along_px'],
            index=k if fraction>=.3 else None,containment=fraction,rival=rival,compatible=fraction>=.8 and fraction-rival>=.2,
            requested_compatible=fraction>=.8 and fraction-rival>=.2 and k is not None and -20<=k<=200,
            alternatives=alt,unmatched_fraction=float(np.mean(q['owner']<0)),unresolved_pixels=int(q['unknown'].sum()),identity_verified=False))
    return out

def summary(rows):
    return dict(n=len(rows),mean_containment=float(np.mean([r['containment'] for r in rows])) if rows else None,
        compatible=sum(r['compatible'] for r in rows),requested_compatible=sum(r['requested_compatible'] for r in rows),unmatched=sum(r['index'] is None for r in rows))

def hypotheses(scene,data,obs,center,width=85):
    rows=[r for r in obs if r['kind']=='region' and abs(r['along_px']-center)<width]
    by={r['id']:r for r in data['rows']};beam=[(0.,[])];photo_xy=[]
    # Bounded discrete ownership search. Shared owner is allowed unless native
    # colors or measured dark separator favor distinct owners. ±1/6/7 retained
    # explicitly even when no pixel intersects that alternative (poor unary score).
    for r in rows:
        fractions={a['index']:a['fraction'] for a in r['alternatives']};best=r['index'];keys=set(fractions)
        if best is not None:keys.update(best+d for d in (-7,-6,-1,0,1,6,7))
        options=[(None,.28)]+[(k,fractions.get(k,0.)) for k in sorted(keys) if -20<=k<=200]
        nextbeam=[]
        for score,assignment in beam:
            for k,value in options:
                penalty=0.
                for previous,j in zip(rows,assignment):
                    distance=np.linalg.norm(np.array(r['point'])-previous['point'])
                    if distance>60 or k is None or j is None:continue
                    if k==j:
                        if r['color']!=previous['color']:penalty+=.6
                        elif distance>20:penalty+=.15
                    # Reversed projected ordering is a conditional context penalty,
                    # not a declaration that image-nearest must be index-adjacent.
                    if k!=j:
                        predicted=scene.pc[k-int(scene.indices[0])]-scene.pc[j-int(scene.indices[0])]
                        measured=np.array(r['point'])-previous['point']
                        if predicted@measured<0:penalty+=.15
                nextbeam.append((score+value-penalty,assignment+[k]))
        beam=sorted(nextbeam,key=lambda a:-a[0])[:16]
    return dict(center_station=center,observations=[r['id'] for r in rows],hypotheses=[dict(score=float(s),indices=a) for s,a in beam[:6]],
        limits='Conditional bounded beam, automatic regions may be wrong. Null is unmatched. ±1/6/7 alternatives included without forcing image-neighbor adjacency; appearance does not certify identity.')

def evaluate(p,data,splits=None):
    scene=Chain(p,data['r294']);obs=observations(scene,data,splits);splits=splits or ['train','validation','reserved','buffer']
    return dict(parameters=extend(p),observations=obs,summary={s:{k:summary([r for r in obs if r['split']==s and r['kind']==k]) for k in ('patch','region')} for s in splits},
        diagnostics={s:Objective(split=s).assess(p,physical=False) for s in splits if s!='buffer'},contact=scene.certify(iterations=160),
        anchor_containment=float(np.mean(scene.trace(pixels(data['r294']['anchor']['measured_support']))['owner']==45)),
        correspondence_hypotheses=[hypotheses(scene,data,obs,c) for c in (130,250,710)])

def development():
    assert not (OUT/'development-validation.json').exists(),'Development evaluation already exposed; use separate named iteration.'
    data=read(EVIDENCE/'inputs.json.gz');models={'R294':read(ROOT/'photo2/r294/results/revised.json')['selected']['parameters']}
    local=read(OUT/'local.json');models.update({'local-'+str(i):r['parameters'] for i,r in enumerate(local['candidates'])})
    results={k:evaluate(p,data,['train','validation']) for k,p in models.items()}
    save(OUT/'development-validation.json',dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),models=results,model_selection='Training winner fixed before development validation; candidates all retained. Reserved outcomes not queried.'))
    for k,v in results.items():print(k,v['summary']['validation'],flush=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['development']);a=p.parse_args();development()
if __name__=='__main__':main()
