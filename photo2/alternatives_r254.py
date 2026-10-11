"""Bounded alternative-domain proofs; no unsupported assignment is promoted."""
import argparse,json
import numpy as np
from scipy.optimize import milp,Bounds,LinearConstraint
from scipy.sparse import lil_matrix
from pattern_r254 import OUT,OLD,diagnostic,propagate
import global_fit_r253 as g


def solve(rows,domains,P,seconds=5):
    # Exact discrete formulation: choose one option per observation; each index
    # at most once; one red/yellow color per residue. Unknown residues stay free.
    options=[(i,k) for i,dd in enumerate(domains) for k in dd];nv=len(options)+P;indices=sorted({k for _,k in options});ix={k:j for j,k in enumerate(indices)}
    A=lil_matrix((len(rows)+len(indices)+len(options),nv),dtype=float);lo=np.full(A.shape[0],-np.inf);hi=np.ones(A.shape[0]);lo[:len(rows)]=1
    for j,(i,k) in enumerate(options):
        A[i,j]=1;A[len(rows)+ix[k],j]=1
        a=len(rows)+len(indices)+j;A[a,j]=1
        if rows[i]['color']=='red':A[a,len(options)+k%P]=1
        else:A[a,len(options)+k%P]=-1;hi[a]=0
    objective=np.r_[[float(k!=rows[i]['k']) for i,k in options],np.zeros(P)]
    res=milp(objective,integrality=np.ones(nv),bounds=Bounds(0,1),constraints=LinearConstraint(A.tocsr(),lo,hi),options={'time_limit':seconds,'mip_rel_gap':0.})
    out=dict(status=int(res.status),message=res.message,minimum_changes=float(res.fun) if res.fun is not None else None,dual_bound=float(res.mip_dual_bound) if getattr(res,'mip_dual_bound',None) is not None else None)
    if res.x is not None:
        kk=[None]*len(rows)
        for j,(i,k) in enumerate(options):
            if res.x[j]>.5:kk[i]=int(k)
        if None in kk or len(set(kk))!=len(kk) or not diagnostic([dict(r,k=k) for r,k in zip(rows,kk)],P)['exact']:raise RuntimeError('Invalid integer solution')
        out['indices']=kk
    return out


def run(out=OUT):
    models=json.loads((OLD/'models.json').read_text());selected=json.loads((OLD/'selected.json').read_text());summaries=[];proofs=[]
    for m in models:
        mid=m['model_id'];rows=json.loads((OLD/f'{mid}-assignments.json').read_text());periods=[P for P in range(1,400) if m['n']%P==0 and P%13]
        # Cost envelopes are deliberately optimistic necessary-condition tests:
        # cost is R253's support+center guide, not a calibrated likelihood.
        for delta in [.15,.5,1.0]:
            domains=[]
            for r in rows:
                baseline=next(a['exact_audit_cost'] for a in r['alternatives'] if a['k']==r['k'])
                domains.append([a['k'] for a in r['alternatives'] if a['exact_audit_cost']<=baseline+delta+1e-12])
            for P in periods:
                result=propagate(rows,domains,P);record=dict(model_id=mid,P=P,delta_cost=delta,status=result['status'],witness=result['witness'],domain_sizes=[len(d) for d in domains])
                if result['status']=='unresolved':record['solver']=solve(rows,result['domains'],P);record['status']='infeasible' if record['solver']['status']==2 else 'optimistic_feasible' if 'indices' in record['solver'] else 'bounded_unsolved'
                proofs.append(record)
        if mid not in selected:continue
        model=g.Model(m['n'],m['h'],m['p']);geom=model.geometry(np.arange(m['n']));groups,_=g.patch_points(rows);po,_,pu=g.rays(model,np.concatenate(groups),geom);cursor=0;records=[]
        for r,points in zip(rows,groups):
            oo=po[cursor:cursor+len(points)];uu=pu[cursor:cursor+len(points)];cursor+=len(points);alts=[]
            baseline=next(a['exact_audit_cost'] for a in r['alternatives'] if a['k']==r['k'])
            for a in r['alternatives']:
                support=float(np.mean((oo==a['generator_index'])&(uu==0)))
                alts.append(dict(**a,cost_change=a['exact_audit_cost']-baseline,patch_support=support,owns_representative=a['generator_index']==r['first_owner'] and r['unfinished']==0))
            records.append(dict(observation_id=r['observation_id'],color=r['color'],k=r['k'],alternatives=alts))
        g.save(out/f'{mid}-alternative-support.json',records)
        summaries.append(dict(model_id=mid,admissible_periods=periods,observations_no_representative_owner=sum(not any(a['owns_representative'] for a in r['alternatives']) for r in records),observations_no_95percent_patch=sum(not any(a['patch_support']>=.95 for a in r['alternatives']) for r in records)))
        print(mid,'alternative audit complete',flush=True)
    g.save(out/'alternative-proofs.json',proofs);g.save(out/'alternative-summary.json',summaries)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=__import__('pathlib').Path,default=OUT);a=ap.parse_args();run(a.output)
