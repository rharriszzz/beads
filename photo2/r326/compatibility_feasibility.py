"""Post-freeze feasibility audit of the original accepted link union.
Tests necessary whole-hypothesis coexistence constraints over ALL R325 candidates.
Infeasibility proves no witness under those necessary constraints. Feasibility alone
would require a further translation-cycle audit; no photo correctness is implied.
"""
import json,time
from pathlib import Path
import numpy as np
from scipy import sparse
from scipy.optimize import milp,Bounds,LinearConstraint
from photo2.r323.tracker import save
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'photo2/r326/results'
def main():
    start=time.perf_counter();g=json.load(open(ROOT/'photo2/r325/results/graph.json'));ws=g['windows'];off=np.cumsum([0]+[len(w['hypotheses']) for w in ws]);n=int(off[-1]);cuts=[];lo=[];hi=[]
    for i,w in enumerate(ws):cuts.append(list(range(int(off[i]),int(off[i+1]))));lo.append(-np.inf);hi.append(1)
    sets=[set(w['observation_ids']) for w in ws]
    for i,w in enumerate(ws):
        for j in range(i+1,len(ws)):
            if len(sets[i]&sets[j])<2:continue
            for a,h in enumerate(w['hypotheses']):
                aa=h['assignments']
                for b,k in enumerate(ws[j]['hypotheses']):
                    bb=k['assignments'];common=aa.keys()&bb.keys()
                    if len(common)<2:continue
                    ds={(aa[o]['ab'][0]-bb[o]['ab'][0],aa[o]['ab'][1]-bb[o]['ab'][1]) for o in common}
                    if len(ds)>1:cuts.append([int(off[i])+a,int(off[j])+b]);lo.append(-np.inf);hi.append(1)
    firstedge=len(cuts);missing=[]
    for e in g['graph']['edges']:
        support=[]
        for i,w in enumerate(ws):
            for a,h in enumerate(w['hypotheses']):
                aa=h['assignments'];s,t=e['source'],e['target']
                if s in aa and t in aa and (np.array(aa[t]['ab'])-aa[s]['ab']).tolist()==e['delta_ab']:support.append(int(off[i])+a)
        if not support:missing.append(e)
        cuts.append(support);lo.append(1);hi.append(np.inf)
    rr=[];cc=[]
    for r,cut in enumerate(cuts):rr.extend([r]*len(cut));cc.extend(cut)
    A=sparse.coo_matrix((np.ones(len(rr)),(rr,cc)),shape=(len(cuts),n)).tocsc();runs=[]
    for multiplicity in [1,2]:
        lower=np.array(lo);lower[firstedge:]=multiplicity;t=time.perf_counter();r=milp(np.zeros(n),integrality=np.ones(n),bounds=Bounds(np.zeros(n),np.ones(n)),constraints=LinearConstraint(A,lower,hi),options={'time_limit':10.})
        runs.append(dict(required_supporting_windows=multiplicity,status=int(r.status),message=r.message,feasible_incumbent=r.x is not None,proved_infeasible=r.status==2,seconds=time.perf_counter()-t,selected_states=[dict(window=i,hypothesis=a) for i,w in enumerate(ws) for a in range(len(w['hypotheses'])) if r.x is not None and r.x[int(off[i])+a]>.5]))
    report=dict(candidates=n,constraints=len(cuts),accepted_links=len(g['graph']['edges']),missing_single_link_candidates=missing,runs=runs,seconds=time.perf_counter()-start,policy='No candidate pruning or score cutoff. Whole-window abstention allowed. Pairwise translation compatibility is necessary for full coexistence; infeasibility here suffices to disprove a whole-hypothesis witness for the complete1826-link union on the R325 bank. This is a representation result, not proof any photographed connection is wrong.')
    save(OUT/'r325-union-feasibility.json',report);print([{k:v for k,v in r.items() if k!='selected_states'} for r in runs])
if __name__=='__main__':main()
