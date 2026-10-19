"""Small deterministic held-section perturbations and abstaining latent errors.

This model proposes observation-level diagnostics. Every index edit is separately
checked against frozen incident graph links; no such edit changes the graph.
Appearance is cached R330 distant-section RGB evidence, not new measured centers.
"""
import argparse,time
from pathlib import Path
import numpy as np
from .analyze import save,fit
from photo2.r330.pattern import dataset,COLORS,viterbi
from photo2.r329.common import ROOT,read,canonical

OFFSETS=np.array([-7,-6,-1,1,6,7])

def latent(k,c,q,theta):
    """Fixed competing no-error/color/index states, no insert/delete operations.

    Priors .80/.12/.08 are explicit sensitivity assumptions, not calibrated.
    Ambiguous winning states abstain; type-level flags survive that abstention.
    """
    n=len(k);p=len(theta);scores=[.8*theta[k%p,c]*q[np.arange(n),c]];states=[('unchanged',0)]
    for offset in OFFSETS:
        scores.append((.08/6)*theta[(k+offset)%p,c]*q[np.arange(n),c]);states.append(('index',int(offset)))
    for delta in [1,2]:
        t=(c+delta)%3;scores.append(.06*theta[k%p,t]*q[np.arange(n),t]);states.append(('color',delta))
    score=np.array(scores).T;order=np.argsort(-score,axis=1);winner=order[:,0]
    post=score/score.sum(1)[:,None];out=[]
    for j,which in enumerate(winner):
        ratio=score[j,which]/max(score[j,0],1e-15);runner=score[j,order[j,1]]
        confident=which!=0 and ratio>=2 and score[j,which]>=1.5*runner and post[j,which]>=.5
        type_mass={kind:float(sum(post[j,t] for t,s in enumerate(states) if s[0]==kind)) for kind in ['unchanged','index','color']}
        kind,value=states[which]
        out.append(dict(kind=kind if confident else 'abstain',offset=value if kind=='index' and confident else 0,
            color=int((c[j]+value)%3) if kind=='color' and confident else int(c[j]),
            posterior=float(post[j,which]),type_mass=type_mass,
            type_flag=max(type_mass,key=type_mass.get) if max(type_mass.values())>=.5 else 'uncertain',
            alternative_offsets=[int(states[t][1]) for t in range(1,7) if score[j,t]>=score[j,which]/1.5]))
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);args=ap.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=False);start=time.perf_counter()
    g,states,ids,obs,station,b0,c0,w0=dataset();co=canonical(states['working']);names=sorted(co);ii=np.array([ids.index(o) for o in names]);ab=np.array([co[o] for o in names]);c,w,b,st=c0[ii],w0[ii],b0[ii],station[ii]
    audit={r['id']:r for r in read(ROOT/'photo2/r330/refinement/refinement.json.gz')['color_audit']}
    q=np.array([audit[o]['mean_votes'] for o in names]);q=np.maximum(q,.03);q/=q.sum(1)[:,None]
    degree={o:0 for o in names}
    for e in g['graph']['edges']:
        for o in [e['source'],e['target']]:degree[o]=degree.get(o,0)+1
    results=[];actual=[];rng=np.random.default_rng(33102)
    for family,wt,p,parent in [('A',[7,6],208,104),('B',[6,7],207,None)]:
        k=ab@wt
        for block in range(12):
            tr=b!=block;te=np.flatnonzero(b==block);theta,_=fit(k,c,w,p,tr,parent)
            pp=latent(k[te],c[te],q[te],theta)
            for j,r in zip(te,pp):
                if r['kind']!='abstain':actual.append(dict(r,id=names[j],family=family,period=p,index=int(k[j]),
                    original_color=COLORS[c[j]],proposed_color=COLORS[r['color']],
                    graph_links_broken=degree[names[j]] if r['kind']=='index' else 0,
                    adoptable=False,excluded_section=block))
            if block not in [0,3,6,9]:continue
            ordered=te[np.argsort(st[te])];single=np.sort(rng.choice(len(te),min(6,len(te)),replace=False));mid=len(ordered)//2
            burst_ids=ordered[max(0,mid-6):mid+6];burst=np.flatnonzero(np.isin(te,burst_ids))
            experiments=[('clean',[],0),('color_single',single,0),('color_burst',burst,0),('unobserved',burst,0)]
            experiments += [('index_single',single,d) for d in [-7,-6,-1,1,6,7]]
            experiments += [('index_burst',burst,d) for d in [1,6,7]]
            for kind,affected,shift in experiments:
                affected=np.array(affected,int);kk=k[te].copy();cc=c[te].copy();ww=w[te].copy()
                if 'index' in kind:kk[affected]+=shift
                if kind.startswith('color'):cc[affected]=(cc[affected]+1)%3
                if kind=='unobserved':ww[affected]=0.
                visible=np.flatnonzero(ww>0);clean=np.setdiff1d(visible,affected)
                for method,qq in [('motif_latent',np.ones_like(q[te])/3),('appearance_latent',q[te])]:
                    inference=latent(kk,cc,qq,theta)
                    if kind=='unobserved':
                        for j in affected:inference[j]=dict(kind='abstain',offset=0,color=int(cc[j]),type_flag='uncertain')
                    original=latent(k[te],c[te],qq,theta)
                    index_exact=sum(inference[j]['kind']=='index' and inference[j]['offset']==-shift for j in affected) if shift else 0
                    color_exact=sum(inference[j]['kind']=='color' and inference[j]['color']==int(c[te[j]]) for j in affected) if kind.startswith('color') else 0
                    false_index=sum(inference[j]['kind']=='index' for j in clean)
                    false_color=sum(inference[j]['kind']=='color' for j in clean)
                    # Original labels/indices are evaluator reference, not known truth.
                    baseline_edits=sum(original[j]['kind']!='abstain' for j in clean)
                    results.append(dict(family=family,period=p,section=block,kind=kind,shift=shift,method=method,
                        affected=len(affected),unaffected=len(clean),exact_index_recovered=index_exact,color_recovered=color_exact,
                        flagged_index=sum(inference[j]['type_flag']=='index' for j in affected),
                        false_index=false_index,false_color=false_color,clean_baseline_edits=baseline_edits,
                        affected_ids=[names[te[j]] for j in affected]))
                # Original regional decoder, trained outside the complete target section.
                offsets,receipt=viterbi(kk,cc,ww,st[te],theta,np.ones(len(te),bool),6.)
                results.append(dict(family=family,period=p,section=block,kind=kind,shift=shift,method='viterbi6',
                    affected=len(affected),unaffected=len(clean),exact_index_recovered=int(sum(offsets[affected]==-shift)) if shift else 0,
                    color_recovered=0,flagged_index=int(sum(offsets[affected]!=0)),
                    false_index=int(sum(offsets[clean]!=0)),false_color=0,
                    color_burst_as_index=int(sum(offsets[affected]!=0)) if kind.startswith('color') else 0,
                    affected_ids=[names[te[j]] for j in affected]))
    # Duplicate injection: metadata identity catches exact copies without deleting
    # an observation. Close but distinct supports remain unresolved (R330 pair).
    duplicated=[names[j] for j in range(0,len(names),100)];inventory=names+duplicated
    duplicate_checks=dict(injected=len(duplicated),detected=len(inventory)-len(set(inventory)),
        physical_merges=0,limitation='Only exact duplicate IDs tested. Distinct-ID misassociation cannot be certified from index or proximity alone.')
    save(out/'errors.json.gz',dict(results=results,real_proposals=actual,duplicates=duplicate_checks,
        priors=dict(unchanged=.8,color=.12,index=.08),seconds=time.perf_counter()-start,
        policy='Held-section exploratory real-data perturbations. Photo and cached appearance remain fixed. Recovery is relative to uncertain original labels/indices. Index proposals breaking frozen links are diagnostic only; no graph edits or missing-bead operations.'))
    print('error records',len(results),'real proposals',len(actual),round(time.perf_counter()-start,3),flush=True)

if __name__=='__main__':main()
