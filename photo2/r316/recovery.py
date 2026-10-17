"""Explicit Pareto recovery, preserving a failed scalar diagnostic selection.

No new shared dimensions: resolve the two separate occlusion regressions with
coherent +/-13-address fields. All existing trial arrays remain unchanged.
"""
import itertools,time
from copy import deepcopy
from photo2.r297.common import read,save
from photo2.r306.evidence import load
from photo2.r314.run import engine
from .experiment import OUT,evaluate
from .followup import export


def main():
    began=time.monotonic();data=load()[0];e=engine();rows=[read(p) for p in sorted((OUT/'followup-trials').glob('*.gz'))]
    def cs(r):return {z['id']:z for z in r['early']}
    feasible=[r for r in rows if r['feasible'] and cs(r)['C-1477-0290']['best_visible']>=.8 and cs(r)['R282-1459-0316']['best_isolated']>=.8]
    seed=max(feasible,key=lambda r:cs(r)['R282-1536-0239']['best_visible']);positive=export('positive-recovery',seed,data,e);new=[]
    for phase,orientation,station in itertools.product([-.16,0,.16],[-10.,0,10.],[-.008,0,.008]):
        q=deepcopy(seed['parameters']);q['compact_phase'][0]+=phase;q['compact_tilt'][0]+=orientation;q['compact_spacing'][0]+=station
        try:r,s,tr=evaluate(q,data,e)
        except ValueError as ex:r=dict(parameters=q,feasible=False,classification='exploratory-bound',reason=str(ex))
        r.update(id=len(new),epoch='negative-neighbor-recovery',intervention=dict(phase_at_minus13=phase,orientation_at_minus13=orientation,station_at_minus13=station))
        if 'physical' in r:r['physical'].pop('witnesses',None)
        save(OUT/'recovery-trials'/f'{r["id"]:03d}.json.gz',r);new.append(r);print(r['id'],r['classification'],flush=True)
    # Keep named simultaneous constraints explicit; failure cannot be compensated by coverage.
    admissible=[r for r in new if r['feasible'] and cs(r)['C-1477-0290']['best_visible']>=.8 and cs(r)['R282-1536-0239']['best_visible']>=.75 and r['development']['vector']['paper']<=.5 and r['comparison']['vector']['paper']<=positive['comparison']['vector']['paper']+1e-10 and r['brackets']['p95']<=positive['brackets']['p95']]
    best=max(admissible,key=lambda r:cs(r)['R282-1459-0316']['best_visible']) if admissible else seed
    result=export('joint-recovery',best,data,e)
    save(OUT/'recovery.json',dict(seconds=time.monotonic()-began,source_followup_trial=seed['id'],trials=len(new),feasible=sum(r['feasible'] for r in new),admissible=[r['id'] for r in admissible],best=dict(epoch=best['epoch'],id=best['id']),constraints='first negative visible >=80%; positive +8 visible >=75%; development paper <=0.5%; comparison paper and all-bracket p95 no worse than positive-recovery; maximize next-negative visible coverage only inside these constraints',readiness=result['readiness'],adopted=False))
if __name__=='__main__':main()
