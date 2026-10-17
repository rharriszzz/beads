"""Preserve interrupted epoch and export its actually saved incumbents, no search."""
from pathlib import Path
from photo2.r297.common import ROOT,read,save,sha,utc
from photo2.r306.evidence import load
from photo2.r313.objective import Objective
from photo2.r313.run import export
import numpy as np

def run():
 out=ROOT/'photo2/r313/results';ev=out.parent/'evidence';dest=out.parent/'continuation';dest.mkdir(exist_ok=True)
 saved={str(p.relative_to(ROOT)):sha(p) for p in sorted((out/'trials').glob('*.json.gz'))}
 assert len(saved)==426
 save(dest/'start.json',dict(utc=utc(),session_start_utc='2026-10-17T20:17:01Z',experiment_cutoff_utc='2026-10-17T20:41:01Z',hard_deadline_utc='2026-10-17T20:47:01Z',preserved_trials=saved,evidence_sha256=sha(ev/'maps.npz')))
 trials=[read(ROOT/p) for p in saved];best=[];data,_,_=load();engine=Objective(dict(np.load(ev/'maps.npz')),read(ev/'freeze.json'))
 for name in sorted({r['start'] for r in trials}):
  r=min([r for r in trials if r['start']==name and r['feasible']],key=lambda r:r['score']);best.append(r)
  a,s,tr=engine.evaluate(r['parameters'],data,r['implementation'],True);a['source_trial']=r['id'];a['parent']=name
  export(out,'R313-initial-'+name,a,s,tr)
  print(name,r['id'],r['score'],a['comparison']['score'],flush=True)
 save(dest/'initial-incumbents.json',dict(best=best,interrupted=True,original_evaluations=len(trials),new_proposals=0))
if __name__=='__main__':run()
