"""Whole-hypothesis compatibility, including nonlocal overlaps and free holonomy.
The cyclic score is a proposal objective. This separate sparse binary optimization
retains a compatible subset of its chosen WHOLE hypotheses; omitted windows abstain.
No individual conflicting assignments are trimmed to manufacture a coherent state.
"""
from collections import defaultdict
import time
import numpy as np
from scipy import sparse
from scipy.optimize import milp, Bounds, LinearConstraint


def relations(windows, choices, stations, period):
    active=[i for i,h in enumerate(choices) if h is not None]
    conflicts=[];links=[]
    for ai,i in enumerate(active):
        h=windows[i]['hypotheses'][choices[i]]['assignments']
        for j in active[ai+1:]:
            k=windows[j]['hypotheses'][choices[j]]['assignments'];common=sorted(h.keys()&k.keys())
            if not common:continue
            # Lift window geography across an arbitrary circular cut. All shared
            # observations in a local overlap must imply the same translation.
            ds={tuple(np.array(h[o]['ab'])-k[o]['ab']) for o in common}
            if len(ds)>1:conflicts.append(dict(windows=[i,j],shared=common,translations=[list(d) for d in sorted(ds)]))
            else:
                wrap=int(np.rint((windows[i]['arc_px']-windows[j]['arc_px'])/period))
                links.append((i,j,np.array(next(iter(ds))),wrap))
    return active,conflicts,links


def cycle_audit(active,links):
    adj=defaultdict(list)
    for i,j,d,w in links:
        if i in active and j in active:adj[i].append((j,d,w));adj[j].append((i,-d,-w))
    coord={};coeff={};paths={};cycles=[];bad=[];holonomies=[]
    for root in sorted(active):
        if root in coord:continue
        coord[root]=np.zeros(2,int);coeff[root]=0;paths[root]=[root];todo=[root]
        while todo:
            i=todo.pop()
            for j,d,w in adj[i]:
                v=coord[i]+d;q=coeff[i]-w
                if j not in coord:coord[j]=v;coeff[j]=q;paths[j]=paths[i]+[j];todo.append(j)
                else:
                    r=v-coord[j];wind=q-coeff[j]
                    if not wind and not np.any(r):continue
                    left,right=paths[i],paths[j]; prefix=0
                    while prefix<min(len(left),len(right)) and left[prefix]==right[prefix]:prefix+=1
                    witness=sorted(set(left[max(0,prefix-1):]+right[max(0,prefix-1):]));row=dict(windows=witness,residual_ab=r.tolist(),winding=wind)
                    cycles.append(row)
                    if not wind:bad.append(witness)
                    elif np.any(r%wind):bad.append(witness)
                    else:holonomies.append((tuple((-r//wind).tolist()),witness))
    if holonomies:
        first=holonomies[0]
        for h,p in holonomies[1:]:
            if h!=first[0]:bad.append(sorted(set(p+first[1])))
    return bad,dict(cycles=cycles,possible_holonomies=[list(h) for h in sorted({h for h,p in holonomies})],compatible=not bad)


def compatible_subset(windows,solution,stations,period):
    start=time.perf_counter();choices=solution['choices'];active,conflicts,links=relations(windows,choices,stations,period)
    n=len(windows);weights=np.array([1+max(w['hypotheses'][h].get('photo_score',w['hypotheses'][h]['score']),0)*.05 if h is not None else 0 for w,h in zip(windows,choices)])
    cuts=[c['windows'] for c in conflicts];history=[]
    for iteration in range(12):
        if cuts:
            rr=[];cc=[]
            for r,cut in enumerate(cuts):rr.extend([r]*len(cut));cc.extend(cut)
            A=sparse.coo_matrix((np.ones(len(rr)),(rr,cc)),shape=(len(cuts),n)).tocsc()
            con=LinearConstraint(A,-np.inf,np.array([len(c)-1 for c in cuts]))
        else:con=None
        result=milp(-weights,integrality=np.ones(n),bounds=Bounds(np.zeros(n),[int(i in active) for i in range(n)]),constraints=con,options={'time_limit':3.,'mip_rel_gap':0.})
        if result.x is None:raise RuntimeError('No feasible whole-hypothesis subset: '+result.message)
        keep={i for i,x in enumerate(result.x) if x>.5};bad,audit=cycle_audit(keep,links)
        history.append(dict(cuts=len(cuts),kept=len(keep),objective=float(-result.fun),optimal=bool(result.success),message=result.message,new_cycle_conflicts=len(bad)))
        if not bad:break
        cuts.extend(bad)
    else:raise RuntimeError('Whole-hypothesis cycle cut limit reached')
    selected=[[h] if i in keep else [] for i,h in enumerate(choices)]
    return selected,dict(selected_windows=sorted(keep),abstained_windows=sorted(set(active)-keep),pair_conflicts=conflicts,cycle_audit=audit,optimization=history,seconds=time.perf_counter()-start,
        policy='One complete cyclic state configuration, then simultaneous maximum-weight compatible whole-hypothesis subset; omitted windows abstain. Pair and cycle constraints include all shared observations, not only nearby window indices. Optimality only if MILP receipt says optimal; no claim of exact joint photo objective.')


def reconsider(windows,solution,stations,period,time_limit=3.):
    """Sparse joint reconsideration of ALL candidates, using cyclic regret unaries.
    This is an explicitly approximate decomposition of the original objective:
    regret(h)=best complete cyclic score - best score with h fixed. Summing these
    regrets is a surrogate, not the original cyclic objective. Pairwise conflicts
    and translation cycles are HARD; whole-window abstention costs20 score units.
    """
    start=time.perf_counter();offsets=np.cumsum([0]+[len(w['hypotheses']) for w in windows]);n=int(offsets[-1]);cuts=[];uppers=[];pair_count=0
    for i,w in enumerate(windows):cuts.append(list(range(int(offsets[i]),int(offsets[i+1]))));uppers.append(1)
    sets=[set(w['observation_ids']) for w in windows]
    for i,w in enumerate(windows):
        for j in range(i+1,len(windows)):
            if len(sets[i]&sets[j])<2:continue
            for a,h in enumerate(w['hypotheses']):
                aa=h['assignments']
                for b,k in enumerate(windows[j]['hypotheses']):
                    bb=k['assignments'];common=aa.keys()&bb.keys()
                    if len(common)<2:continue
                    first=None;bad=False
                    for o in common:
                        d=(aa[o]['ab'][0]-bb[o]['ab'][0],aa[o]['ab'][1]-bb[o]['ab'][1])
                        if first is None:first=d
                        elif d!=first:bad=True;break
                    if bad:cuts.append([int(offsets[i])+a,int(offsets[j])+b]);uppers.append(1);pair_count+=1
    weights=np.array([20.-gap for gaps in solution['max_marginal_gaps'] for gap in gaps]);build=time.perf_counter()-start;history=[]
    for iteration in range(24):
        rr=[];cc=[]
        for r,cut in enumerate(cuts):rr.extend([r]*len(cut));cc.extend(cut)
        A=sparse.coo_matrix((np.ones(len(rr)),(rr,cc)),shape=(len(cuts),n)).tocsc()
        result=milp(-weights,integrality=np.ones(n),bounds=Bounds(np.zeros(n),np.ones(n)),constraints=LinearConstraint(A,-np.inf,uppers),options={'time_limit':time_limit,'mip_rel_gap':.001})
        if result.x is None:
            selected,audit=compatible_subset(windows,solution,stations,period)
            return selected,dict(**audit,fallback=True,total_seconds=time.perf_counter()-start,reason='no feasible MILP incumbent within bounded solve',pair_constraints=pair_count,optimal=False)
        choices=[]
        for i,w in enumerate(windows):
            picks=np.flatnonzero(result.x[offsets[i]:offsets[i+1]]>.5);choices.append(int(picks[0]) if len(picks) else None)
        active,conflicts,links=relations(windows,choices,stations,period);assert not conflicts
        bad,audit=cycle_audit(set(active),links)
        history.append(dict(objective=float(-result.fun),mip_gap=float(result.mip_gap),optimal=bool(result.success),message=result.message,new_cycle_conflicts=len(bad)))
        if not bad:break
        for cut in bad:cuts.append([int(offsets[i])+choices[i] for i in cut]);uppers.append(len(cut)-1)
    else:
        chosen=dict(solution,choices=choices);selected,audit=compatible_subset(windows,chosen,stations,period)
        return selected,dict(**audit,fallback=True,total_seconds=time.perf_counter()-start,reason='cycle-cut budget',pair_constraints=pair_count,optimal=False)
    selected=[[h] if h is not None else [] for h in choices]
    return selected,dict(selected_windows=active,abstained_windows=[i for i,h in enumerate(choices) if h is None],pair_conflicts=[],cycle_audit=audit,optimization=history,seconds=time.perf_counter()-start,factor_build_seconds=build,pair_constraints=pair_count,
        changed_from_cyclic=[dict(window=i,cyclic=a,compatible=b) for i,(a,b) in enumerate(zip(solution['choices'],choices)) if a!=b],
        policy='All retained candidates compete jointly under hard all-overlap compatibility and cycle cuts; cyclic max-marginal regret is a surrogate unary, with20-unit whole-window abstention. No claim of exact optimization of the original cyclic+photo objective.')
