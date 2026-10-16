"""Deterministic resumable Sobol + differential-evolution search and control.

Each committed step stores full RNG and population. No model calls or supervisor
are needed. A killed uncommitted evaluation is replayed; evidence/source mismatch
and concurrent writers fail closed. Final validation is separate from selection.
"""
import argparse, os, signal, time
from pathlib import Path
import numpy as np
from scipy.stats import qmc
from photo2.r297.common import read,save,sha,run_lock,utc,environment
from .evidence import BASE
from .model import BOUNDS,NAMES,DEFAULT
from .objective import evaluate

def fingerprints():
    return {str(p):sha(p) for p in sorted((BASE).glob('*.py')) if p.name in ['model.py','objective.py','search.py']}|{'evidence':sha(BASE/'evidence/frozen.json.gz')}

def run(output,section,hand,seed,budget=2048,method='de',resolution=0,start=None,seconds=None,secondary_weight=1):
    output=Path(output);finger=fingerprints();stop=[False]
    def halt(*_):stop[0]=True
    old=signal.signal(signal.SIGTERM,halt);oldint=signal.signal(signal.SIGINT,halt)
    try:
      with run_lock(output):
        cp=output/'checkpoint.json.gz';rng=np.random.default_rng(seed);dim=len(BOUNDS);lo,hi=BOUNDS.T;span=hi-lo;popsize=48
        sobol=qmc.Sobol(dim,scramble=True,seed=seed).random_base2(12)
        config=dict(section=section['id'],hand=hand,seed=seed,method=method,resolution=resolution,secondary_weight=secondary_weight,start=start)
        if cp.exists():
            state=read(cp)
            if state['fingerprints']!=finger or state['config']!=config:raise ValueError('Source, evidence or configuration mismatch')
            rng.bit_generator.state=state['rng'];history=state['history'];pop=np.array(state['population']);scores=np.array(state['scores']);elapsed=state['elapsed'];best=np.array(state['best']);bestloss=state['bestloss']
        else:
            history=[];pop=sobol[:popsize].copy();scores=np.full(popsize,1e12);elapsed=0.;best=np.clip(((DEFAULT if start is None else np.array(start))-lo)/span,0,1);bestloss=1e12
            if start is not None:
                if resolution:pop=np.clip(best+rng.normal(0,.08,(popsize,dim)),0,1)
                pop[0]=best
        began=time.monotonic()
        for i in range(len(history),budget):
            if stop[0] or (seconds is not None and time.monotonic()-began>=seconds):break
            if i==0 and (method=='coordinate' or start is not None):u=best.copy();target=0
            elif method=='coordinate':
                u=best.copy();j=((i-1)//2)%dim;sign=1 if i%2 else -1;u[j]=np.clip(u[j]+sign*.025*(.75**(i//(2*dim))),0,1);target=0
            elif i<popsize:u=pop[i].copy();target=i
            elif method=='sobol':u=sobol[i%len(sobol)];target=i%popsize
            else:
                target=i%popsize;a,b,c=rng.choice([j for j in range(popsize) if j!=target],3,replace=False)
                mutant=pop[a]+rng.uniform(.45,.95)*(pop[b]-pop[c]);cross=rng.random(dim)<.8;cross[rng.integers(dim)]=True
                u=np.where(cross,mutant,pop[target]);u=np.where((u<0)|(u>1),rng.random(dim),u)
                # Global injection prevents a population becoming one local basin.
                if i%29==0:u=sobol[(i+seed)%len(sobol)].copy()
            v=lo+span*u;t0=time.perf_counter();result=evaluate(v,section,hand,resolution,secondary_weight=secondary_weight);duration=time.perf_counter()-t0
            history.append(dict(i=i,parameters=v.tolist(),**result,seconds=duration))
            if result['loss']<scores[target]:pop[target]=u;scores[target]=result['loss']
            if result['loss']<bestloss:bestloss=result['loss'];best=u.copy()
            # Atomic checkpoint contains proposal, score and *next* generator state.
            elapsed_now=elapsed+time.monotonic()-began
            state=dict(config=config,fingerprints=finger,history=history,population=pop.tolist(),scores=scores.tolist(),best=best.tolist(),bestloss=bestloss,rng=rng.bit_generator.state,elapsed=elapsed_now,environment=environment())
            if (i+1)%16==0 or i+1==budget:save(cp,state)
            if (i+1)%256==0:print(section['id'],hand,seed,method,resolution,i+1,round(bestloss,3),flush=True)
        save(cp,state)
        return state
    finally:signal.signal(signal.SIGTERM,old);signal.signal(signal.SIGINT,oldint)

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--section',default='S1');p.add_argument('--hand',type=int,choices=[-1,1],default=-1);p.add_argument('--seed',type=int,default=301);p.add_argument('--budget',type=int,default=2048);p.add_argument('--method',choices=['de','sobol','coordinate'],default='de');p.add_argument('--resolution',type=int,default=0);p.add_argument('--seconds',type=float);a=p.parse_args()
    sections=read(BASE/'evidence/frozen.json.gz')['sections'];section=next(s for s in sections if s['id']==a.section)
    run(a.output,section,a.hand,a.seed,a.budget,a.method,a.resolution,seconds=a.seconds)

if __name__=='__main__':main()
