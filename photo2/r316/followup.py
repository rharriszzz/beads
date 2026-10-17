"""Sealed causal follow-up to trial 179: repair positive occlusion, preserve negatives."""
import time,itertools
from copy import deepcopy
import numpy as np
from photo2.r297.common import ROOT,read,save
from photo2.r306.evidence import load
from photo2.r314.run import engine
from photo2.r315.model import refined_trace
from photo2.r315.measurement import measure_readiness
from photo2.r315.diagnose import brackets
from photo2.r307.fast import grid
from .experiment import evaluate,OUT,vector


def export(name,row,data,e):
    r,s,tr=evaluate(row['parameters'],data,e);r.update(name=name,source_trial=row['id'],source_epoch=row.get('epoch','initial'),cohort=list(range(-100,100)),positions=dict(indices=s.indices.tolist(),centers=s.centers.tolist(),frames={k:v.tolist() for k,v in s.g.items()},projected=s.pc.tolist()))
    r['readiness']={k:measure_readiness(e,tr,r[k],i) for i,k in enumerate(['development','comparison','buffer'])};ix=np.flatnonzero((s.indices>=-100)&(s.indices<=99));xy=grid(s,1.,ix);full=refined_trace(s,xy);assert len(ix)==200
    r['target']=dict(bodies=200,full_bodies=s.n,rays=len(xy),unknown=int(full['unknown'].sum()),visible_counts=[dict(index=int(s.indices[j]),pixels=int(np.sum(full['owner']==j))) for j in ix]);save(OUT/f'{name}-model.json.gz',r);np.savez_compressed(OUT/f'{name}-raster.npz',owner=tr['owner'],unknown=tr['unknown']);np.savez_compressed(OUT/f'{name}-target.npz',xy=xy,owner=full['owner'],unknown=full['unknown']);save(OUT/f'{name}-brackets.json.gz',brackets(e,tr));return r


def main():
    start=time.monotonic();data=load()[0];e=engine();seed=read(OUT/'trials/0179.json.gz');rows=[]
    for phase,orientation,station,minor in list(itertools.product([-.16,0,.16],[-10.,0,10.],[-.008,0,.008],[0.]))+list(itertools.product([-.16,0,.16],[-10.,0,10.],[0.],[-.2,.2])):
        q=deepcopy(seed['parameters']);q['compact_phase'][2]+=phase;q['compact_spacing'][2]+=station;q['compact_tilt']=[0,0,orientation];q['minor']+=minor
        try:r,s,tr=evaluate(q,data,e)
        except ValueError as ex:r=dict(parameters=q,feasible=False,classification='exploratory-bound',reason=str(ex))
        r.update(id=len(rows),epoch='positive-occlusion-followup',intervention=dict(phase_at13=phase,orientation_at13=orientation,station_at13=station,minor=minor))
        if 'physical' in r:r['physical'].pop('witnesses',None)
        rows.append(r);save(OUT/'followup-trials'/f'{r["id"]:03d}.json.gz',r);print(r['id'],r['classification'],flush=True)
    feasible=[r for r in rows if r['feasible']]
    def rank(r):
        cs={z['id']:z for z in r['early']};v=r['development']['vector'];w=r['comparison']['vector'];neg=['C-1477-0290','R282-1459-0316'];viol=[max(0,.8-cs[k]['best_isolated'])/.2 for k in neg];viol += [max(0,.8-z['best_visible'])/.2 for z in r['early']]+[v['paper']/.5,w['paper']/.5,v['seam']/10,w['seam']/10,r['brackets']['p95']/3,v['worst']/3,w['worst']/3]
        return tuple(sorted(viol,reverse=True))
    best=min(feasible,key=rank);a=export('negative-repair',seed,data,e);b=export('positive-followup',best,data,e)
    save(OUT/'followup.json',dict(seconds=time.monotonic()-start,trials=len(rows),feasible=len(feasible),source_initial_trial=179,best=best['id'],rank_policy='Lexicographic separate absolute violations including both negative isolated cores, six visible cores, development/comparison paper, seam, finite brackets, worst cores. No coverage compensation or adoption.',selected=[dict(name='negative-repair',trial=179,readiness=a['readiness']),dict(name='positive-followup',trial=best['id'],readiness=b['readiness'])],adopted=False))
if __name__=='__main__':main()
