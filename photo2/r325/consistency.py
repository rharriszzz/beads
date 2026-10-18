"""Simultaneous sparse integer-coordinate audit with free circuit holonomy.

Local proposed edges carry physical-guide wrap numbers. We first solve their
weighted L1 incidence equations simultaneously, rather than keeping a greedy
spanning history. Nonzero-residual edges abstain. Integral solutions are checked;
no fractional coordinates are silently rounded into acceptance. A separate
symbolic traversal determines whether accepted evidence actually fixes holonomy.
"""
from collections import defaultdict
import numpy as np
from scipy import sparse
from scipy.optimize import linprog,milp,Bounds,LinearConstraint


def synchronize(edges,obs,stations,period):
    if not edges:return [],[],{},[],dict(identified=False,reason='no edges')
    ids=sorted({e[k] for e in edges for k in ('source','target')});ix={o:i for i,o in enumerate(ids)};n=len(ids);m=len(edges)
    rows=[];cols=[];values=[];wrap=[]
    for k,e in enumerate(edges):
        w=int(np.rint((stations[e['source']]-stations[e['target']])/period));wrap.append(w)
        rows.extend([k,k,k]);cols.extend([ix[e['source']],ix[e['target']],n]);values.extend([-1.,1.,float(w)])
        e['circuit_wrap']=w
    A=sparse.coo_matrix((values,(rows,cols)),shape=(m,n+1)).tocsr();I=sparse.eye(m,format='csr')
    lhs=sparse.vstack([sparse.hstack([A,-I]),sparse.hstack([-A,-I])],format='csr')
    weights=np.array([e['supporting_windows']*e['consensus'] for e in edges]);c=np.r_[np.zeros(n+1),weights]
    bounds=[(-5000,5000)]*(n+1)+[(0,None)]*m;bounds[0]=(0,0)
    solutions=[];receipts=[]
    for dim in range(2):
        d=np.array([e['delta_ab'][dim] for e in edges]);b=np.r_[d,-d]
        sol=linprog(c,A_ub=lhs,b_ub=b,bounds=bounds,method='highs',options={'time_limit':20.})
        if not sol.success:raise RuntimeError('Global coordinate LP did not converge: '+sol.message)
        x=sol.x[:n+1];fraction=float(np.max(abs(x-np.rint(x))))
        if fraction>1e-6:
            lo=np.array([a for a,b in bounds]);hi=np.array([b if b is not None else np.inf for a,b in bounds])
            sol=milp(c,integrality=np.r_[np.ones(n+1),np.zeros(m)],bounds=Bounds(lo,hi),constraints=LinearConstraint(lhs,-np.inf,b),options={'time_limit':20.})
            if not sol.success:raise RuntimeError('Integer coordinate audit did not converge: '+sol.message)
            x=sol.x[:n+1]
        assert np.max(abs(x-np.rint(x)))<1e-6
        solutions.append(np.rint(x).astype(int));receipts.append(dict(objective=float(sol.fun),continuous_fractionality=fraction,message=sol.message))
    x=np.array(solutions).T;res=A@x-np.array([e['delta_ab'] for e in edges]);accepted=[];conflicts=[]
    for e,r in zip(edges,res):
        e['synchronization_residual_ab']=list(map(int,r))
        if np.any(r):
            e['status']='unresolved global integer conflict';e['reasons'].append('nonzero residual in simultaneous weighted L1 coordinate synchronization');conflicts.append(e)
        else:accepted.append(e)
    # Symbolic x_i = a_i + k_i H, independent of the optimizer's arbitrary gauge.
    adj=defaultdict(list)
    for e in accepted:
        s,t=e['source'],e['target'];d=np.array(e['delta_ab']);w=e['circuit_wrap'];adj[s].append((t,d,-w));adj[t].append((s,-d,w))
    coord={};coeff={};components=[];cycles=[]
    for root in sorted(adj):
        if root in coord:continue
        ci=len(components);coord[root]=(ci,np.zeros(2,int));coeff[root]=0;todo=[root];group=[]
        while todo:
            a=todo.pop();group.append(a)
            for b,d,k in adj[a]:
                bb=coord[a][1]+d;kk=coeff[a]+k
                if b in coord:
                    residual=bb-coord[b][1];wind=kk-coeff[b]
                    if wind or np.any(residual):cycles.append(dict(component=ci,constant_ab=residual.tolist(),holonomy_coefficient=int(wind)))
                else:coord[b]=(ci,bb);coeff[b]=kk;todo.append(b)
        components.append(dict(id=ci,origin=root,nodes=sorted(group)))
    hs=[]
    for row in cycles:
        k=row['holonomy_coefficient'];r=np.array(row['constant_ab'])
        if k:
            h=-r/k
            if np.max(abs(h-np.rint(h)))<1e-9:hs.append(tuple(map(int,h)))
        else:assert not np.any(r),'Accepted contractible cycle contradiction'
    values=sorted(set(hs));identified=len(values)==1;H=np.array(values[0]) if identified else None
    for o,(ci,v) in list(coord.items()):
        if identified:coord[o]=(ci,v+coeff[o]*H)
    closure=dict(identified=identified,holonomy_ab=H.tolist() if identified else None,cycles=cycles,
        possible_holonomies=[list(h) for h in values],optimizer_holonomy_ab=x[-1].tolist(),
        symbolic_winding_coefficients=coeff,lp_receipts=receipts,
        count_candidates=({'A':abs(int(H@[7,6])),'B':abs(int(H@[6,7]))} if identified else None),
        policy='x_target-x_source+wrap*H=delta. H is free, never forced zero. Without a winding cycle it is unidentifiable; optimizer gauge is not a measured closure.',
        uncertainty='L1 optimum can be nonunique; residual selection is conditional, not photographic certification.')
    return accepted,conflicts,coord,components,closure
