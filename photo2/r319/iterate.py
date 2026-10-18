"""Relinearize at accepted states; avoid repeated shrinking of a stale Jacobian."""
import numpy as np
from .experiment import Run
from .common import *
from .refine import minimax,metric
from .contact_fit import fit

def main():
    run=Run();run.rows=[read(p) for p in sorted((OUT/'trials').glob('*.gz'))];run.baseline=read(OUT/'baseline.json.gz');run.deadline=__import__('datetime').datetime(2026,10,18,2,55,30,tzinfo=__import__('datetime').timezone.utc).timestamp()
    chosen=read(OUT/'small-selection.json')['chosen'];vs=read(OUT/'geometry-constrained-minimax.json.gz')['variables'];history=[]
    # Better-conditioned useful directions: fixed support centers; no remote
    # spline nodes whose main effect is the same global station displacement.
    keys=['phase','s0','tilt','axial','radius','minor','elevation','roll','scale','light_az','light_el','roughness','turn','radial_cant']
    vs=[v for v in vs if (isinstance(v['key'],str) and v['key'] in keys) or (isinstance(v['key'],list) and (v['key'][0]=='translation' or v['key'][0].startswith('compact_') and v['key'][0]!='compact_centers'))]
    parent=read(OUT/'best-full.json.gz')
    for iteration in range(4):
        base=run.trial(parent['parameters'],f'iterate{iteration}-parent');cols=[];gcols=[];used=[];records=[]
        for v in vs:
            a=run.trial(change(base['parameters'],v['key'],-v['scale']),f'iterate{iteration}-negative',dict(key=v['key'],factor=-1))
            b=run.trial(change(base['parameters'],v['key'],v['scale']),f'iterate{iteration}-positive',dict(key=v['key'],factor=1))
            rec=dict(variable=v,negative=a['id'],positive=b['id'])
            if run.usable(a) and run.usable(b):
                J=(positions(b)-positions(a))/2;rec['central']=J.tolist();rec['second_difference']=np.linalg.norm(positions(b)+positions(a)-2*positions(base),axis=1).tolist()
                if np.linalg.norm(J)>.15:cols.append(J);gcols.append((metric(b)-metric(a))/2);used.append(v)
            records.append(rec)
        save(OUT/f'iterate{iteration}-jacobian.json.gz',dict(parent=base['id'],records=records))
        J=np.stack(cols,axis=2);G=np.stack(gcols,axis=1)
        minimax(run,base,used,J,G,f'iterate{iteration}-minimax')
        fit(run,base,used,J,G,f'iterate{iteration}-contact')
        good=[r for r in run.rows if run.usable(r) and r.get('acceptance',{}).get('passed')];best=min(good,key=lambda r:r['emax_px']);history.append(dict(iteration=iteration,parent=base['id'],selected=best['id'],before=base['emax_px'],after=best['emax_px']))
        save(OUT/'best-full.json.gz',best);save(OUT/'accepted-history.json',history)
        if best['emax_px']>=parent['emax_px']-.005:break
        parent=best
    guarded=[r for r in good if r['emax_px']<=run.baseline['emax_px']+.05];small=min(guarded,key=lambda r:max(r['rows'][i]['error_px'] for i in chosen['cohort']));save(OUT/'best-small.json.gz',small)
    save(OUT/'iterate-summary.json',dict(utc=utc(),trials=len(run.rows),best_full=best['id'],best_small=small['id'],history=history));print('ITERATE COMPLETE',len(run.rows),best['emax_px'],flush=True)
if __name__=='__main__':main()
