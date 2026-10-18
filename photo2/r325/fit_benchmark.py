import json,time,cProfile,pstats
from pathlib import Path
import numpy as np
from photo2.r323 import tracker as reference
from photo2.r325.batched_fit import fit_hypotheses
OUT=Path(__file__).parent/'results'
def signature(h):
    a=h['assignments'];first=a[sorted(a)[0]]['ab'];return tuple((o,*(np.array(a[o]['ab'])-first)) for o in sorted(a))
def main():
    g=json.load(open('photo2/r324/results/graph.json'));obs={o['id']:o for o in g['observations']};wins=g['windows'][65:94];results=[];ledger=[];prof=cProfile.Profile()
    for label,func in [('reference',reference.fit_hypotheses),('batched',fit_hypotheses)]:
        rng=np.random.default_rng(324);allh=[];beg=time.perf_counter();prof.enable() if label=='reference' else None
        for w in wins:
            ids=w['observation_ids'];xy=(np.array([obs[o]['xy'] for o in ids])-w['center'])@np.array(w['frame']);sig=np.array([8 if obs[o]['color']=='black' else 5 for o in ids]);wt=np.array([1 if obs[o]['band_clearance_px']>=18 else .55 for o in ids]);wh=[]
            for B in w.get('competing_bases_local',[]):
                h,n,m=func(xy,sig,wt,np.array(B),ids,rng);wh.append(h);ledger.append(dict(mode=label,window=w['id'],seeds=n,distinct=m))
            allh.append(wh)
        if label=='reference':prof.disable();prof.dump_stats(str(OUT/'candidate-profile.pstats'));pstats.Stats(prof,stream=open(OUT/'candidate-profile.txt','w')).strip_dirs().sort_stats('cumtime').print_stats(25)
        results.append(dict(mode=label,seconds=time.perf_counter()-beg,hypotheses=allh))
    checks=0;maxerr=0.;mismatch=[]
    for wi,(aa,bb) in enumerate(zip(results[0]['hypotheses'],results[1]['hypotheses'])):
        for bi,(a,b) in enumerate(zip(aa,bb)):
            da={signature(h):h for h in a};db={signature(h):h for h in b}
            if da.keys()!=db.keys():mismatch.append(dict(window=wins[wi]['id'],basis=bi,only_reference=len(da.keys()-db.keys()),only_batch=len(db.keys()-da.keys())))
            for s in da.keys()&db.keys():
                for oid in da[s]['assignments']:
                    err=np.max(abs(np.array(da[s]['assignments'][oid]['predicted_xy'])-db[s]['assignments'][oid]['predicted_xy']));maxerr=max(maxerr,float(err));checks+=1
    report=dict(times=[{k:v for k,v in r.items() if k!='hypotheses'} for r in results],profiled_reference=True,assignments_compared=checks,maximum_prediction_delta_px=maxerr,topology_mismatches=mismatch,ledger=ledger)
    reference.save(OUT/'fit-benchmark.json',report);print({k:v for k,v in report.items() if k!='ledger'})
if __name__=='__main__':main()
