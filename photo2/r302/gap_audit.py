"""Post-seal predicted gap sensitivity on the four untouched image routes.

This does not read valley locations or select a model. Rows are dependent
diagnostics, not extra training information or physical neighbor identities.
"""
import time
import numpy as np
from .core import *

def predicted_gaps(scene,section):
    values=[]
    for r in section['diagnostic_separators']:
        xy=np.array(r['xy']);owner=scene.trace(xy)['owner'];paper=owner<0
        padded=np.r_[False,paper,False];starts=np.flatnonzero(np.diff(padded.astype(int))==1);ends=np.flatnonzero(np.diff(padded.astype(int))==-1)
        step=float(np.linalg.norm(xy[1]-xy[0]));values.extend([float(paper.sum()*step),float(max(ends-starts,default=0)*step),float(np.sum(owner[:-1]!=owner[1:]))])
    # Directional support margins are NOT exact minimum surface distances.
    ids=np.searchsorted(scene.indices,[-6,0,6])
    for lag in [1,6,7]:
        a=ids;b=a+lag;v=scene.centers[b]-scene.centers[a];distance=np.linalg.norm(v,axis=1);n=v/distance[:,None]
        margin=distance-scene.support(n,scene.g[AXES[0]][a])-scene.support(n,scene.g[AXES[0]][b])
        values.extend(margin.tolist())
    return np.array(values)

def main():
    seal=read(BASE/'results/fit-freeze.json');started=time.monotonic();s=read(BASE/'evidence/section.json.gz');d=read(BASE/'results/diagnosis.json.gz');rows=[]
    for r in d['sensitivity']:
        hand=r['start']['hand'];v=r['start']['parameters'];base=predicted_gaps(Scene(v,s,hand),s);columns=[]
        for j,name in enumerate(NAMES):
            pair=[x for x in r['perturbations'] if x['parameter']==name]
            a,b=[predicted_gaps(Scene(x['parameters'],s,hand),s) for x in pair]
            columns.append((b-a)/(pair[1]['parameters'][j]-pair[0]['parameters'][j])*STEPS[j])
        rows.append(dict(start=r['start']['name'],base=base.tolist(),jacobian=np.array(columns).T.tolist()))
    save(BASE/'results/gap-sensitivity.json',dict(utc=utc(),seconds=time.monotonic()-started,rows=rows,labels=[f'{r["id"]}:{key}' for r in s['diagnostic_separators'] for key in ['total_background_px','maximum_background_run_px','owner_transitions']]+[f'lag{lag}:address{k}:directional-support-margin' for lag in [1,6,7] for k in [-6,0,6]],meaning='First12 rows: predictions on held routes, no observed valley locations used. Last9: directional 3D support margins, not exact gap measurements. Prediction-only diagnostics, NOT included in rank or optimization. Some perturbations uncertified; consult diagnosis for their status. No refit.',fit_seal_sha256=sha(BASE/'results/fit-freeze.json')))

if __name__=='__main__':main()
