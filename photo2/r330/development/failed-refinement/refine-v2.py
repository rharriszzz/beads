"""Exploratory harmonic refinement, color audit, and real-data perturbations.

The initial outer test has already been opened. All new leave-section-out
predictions exclude their targets computationally but are not a fresh blind test.
"""
import argparse,time
from pathlib import Path
from collections import Counter
import numpy as np
from .pattern import dataset,counts,probabilities,motif,viterbi,scan,COLORS,OUTER
from photo2.r329.common import canonical,save,read,ROOT
from photo2.r329.photographic_diagnostics.explore import IM

def hierarchical(k,c,w,p,train,alpha=3.):
    if p<=104:return probabilities(k,c,w,p,train)[0]
    parent=hierarchical(k,c,w,p//2,train,alpha)
    cc=counts(k,c,w,p,train)
    return (cc+alpha*parent[np.arange(p)%(p//2)])/(cc.sum(1)[:,None]+alpha)

def photo_features(obs,ids,radius):
    feat=[]
    for oid in ids:
        x,y=np.rint(obs[oid]['xy']).astype(int);patch=IM[y-radius:y+radius+1,x-radius:x+radius+1]
        yy,xx=np.indices(patch.shape[:2]);px=patch[(xx-radius)**2+(yy-radius)**2<=radius**2]
        # RGB quantiles preserve darkness; ratios alone confuse tinted specular
        # highlights with pigment. These are local appearance features only.
        quant=np.quantile(px,[.1,.3,.5,.7,.9],axis=0).ravel()
        feat.append(quant)
    return np.array(feat)

def audit_colors(ids,obs,blocks,c):
    variants=[]
    for radius in [8,12,16]:
        f=photo_features(obs,ids,radius);preds=np.zeros((len(ids),3,3))
        for b in range(12):
            tr=np.flatnonzero(blocks!=b);te=np.flatnonzero(blocks==b)
            scale=np.maximum(np.percentile(f[tr],75,axis=0)-np.percentile(f[tr],25,axis=0),.05)
            distance=np.sum(((f[te,None]-f[None,tr])/scale)**2,axis=2)
            near=np.argsort(distance,axis=1)[:,:51]
            for j,kn in enumerate([15,31,51]):
                labels=c[tr[near[:,:kn]]]
                preds[te,j]=np.stack([(labels==a).mean(1) for a in range(3)],axis=1)
        variants.append(preds)
    values=np.stack(variants,axis=1).reshape(len(ids),9,3);output=[]
    for i,o in enumerate(ids):
        winner=values[i].mean(0).argmax();same=bool(np.all(values[i].argmax(1)==winner))
        output.append(dict(id=o,original=COLORS[c[i]],suggestion=COLORS[winner],stable=same,min_vote=float(values[i,:,winner].min()),mean_votes=values[i].mean(0).tolist(),variants=values[i].tolist(),strong=bool(same and values[i,:,winner].min()>=.8),policy='Votes from weak historical color labels outside this geographic section; not calibrated probability or body-center evidence.'))
    return output

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);args=ap.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=False);began=time.perf_counter()
    g,states,ids,obs,station,blocks,c,w=dataset();co=canonical(states['working']);ii=np.array([i for i,o in enumerate(ids) if o in co]);names=[ids[i] for i in ii];k=np.array([co[o] for o in names])@[7,6];cc,ww,bb=c[ii],w[ii],blocks[ii];n=len(ii)
    fits=[];predictions={}
    for p in [52,104,208,416]:
        for mode in ['flat','hierarchical'] if p>104 else ['flat']:
            for alpha in [1.,3.,6.] if mode=='hierarchical' else [3.]:
                pred=np.zeros((n,3));bas=np.zeros((n,3));entries=[]
                for block in range(12):
                    train=bb!=block;test=~train
                    th,base=probabilities(k,cc,ww,p,train)
                    if mode=='hierarchical':th=hierarchical(k,cc,ww,p,train,alpha)
                    pred[test]=th[k[test]%p];bas[test]=base
                loggain=np.log(pred[np.arange(n),cc])-np.log(bas[np.arange(n),cc])
                rec=dict(period=p,mode=mode,alpha=alpha,gain_nats=float(np.average(loggain,weights=ww)),hard_agreement=float((pred.argmax(1)==cc).mean()),per_section=[float(np.average(loggain[bb==b],weights=ww[bb==b])) for b in range(12)])
                fits.append(rec);predictions[(p,mode,alpha)]=pred
    # P208 is a development-selected harmonic from the original shortlist, not
    # inferred by minimizing newly opened test errors.
    pred=predictions[(208,'flat',3.)];theta,entries=motif(k,cc,ww,bb,208,np.ones(n,bool));suspects=[];crossrows=[]
    for block in range(12):
        train=bb!=block;th,en=motif(k,cc,ww,bb,208,train);cnt=counts(k,cc,ww,208,train)
        for j in np.flatnonzero(~train):
            e=en[k[j]%208];winner=cnt[k[j]%208].argmax();support=(train&(k%208==k[j]%208)&(cc==winner))
            strong=e['weighted_agreement']>=.8 and len(set(bb[support]))>=3 and support.sum()>=3
            row=dict(id=names[j],xy=obs[names[j]]['xy'],index=int(k[j]),residue=int(k[j]%208),section=int(block),color=COLORS[cc[j]],prediction=COLORS[winner] if strong else '?',plurality=COLORS[winner],weight=float(ww[j]),probabilities=th[k[j]%208].tolist(),support=[dict(id=names[l],index=int(k[l]),xy=obs[names[l]]['xy'],section=int(bb[l])) for l in np.flatnonzero(support)],strong=bool(strong),disagreement=bool(cc[j]!=winner))
            crossrows.append(row)
            if cc[j]!=winner:
                options=sorted([dict(shift=d,color=COLORS[th[(k[j]+d)%208].argmax()],likelihood=float(th[(k[j]+d)%208,cc[j]])) for d in [-7,-6,-1,0,1,6,7]],key=lambda r:-r['likelihood'])
                suspects.append(dict(**row,index_proposals=options))
    colors=audit_colors(ids,obs,blocks,c);bycolor={x['id']:x for x in colors}
    for s in suspects:
        audit=bycolor[s['id']];s['photographic_color_audit']=audit
        s['correction_candidate']=s['strong'] and audit['strong'] and audit['suggestion']==s['prediction']
        s['likely_mechanism']='color substitution supported by separate appearance audit' if s['correction_candidate'] else 'uncertain color / index / imperfect motif; unresolved'
    # All candidate color changes remain overlays, with unchanged IDs/pixels/graph.
    proposed={s['id']:s['prediction'] for s in suspects if s['correction_candidate']}
    corrected=cc.copy()
    for j,o in enumerate(names):
        if o in proposed:corrected[j]=COLORS.index(proposed[o])
    feedback=[]
    for p in [104,208]:
        for block in range(12):
            train=bb!=block;test=(bb==block)&np.array([o not in proposed for o in names])
            a,_=probabilities(k,cc,ww,p,train);b,_=probabilities(k,corrected,ww,p,train)
            gain=np.log(b[k[test]%p,cc[test]])-np.log(a[k[test]%p,cc[test]])
            feedback.append(dict(period=p,section=block,unchanged_targets=int(test.sum()),gain_nats=float(np.average(gain,weights=ww[test]))))
    # Post-selection data perturbations: keep the actual observations and their
    # sparsity, modify only copies. Compare recovery to frozen extracted labels,
    # which themselves are not ground truth.
    rng=np.random.default_rng(33001);perturb=[];basecnt=counts(k,cc,ww,208,np.ones(n,bool));ref=basecnt.argmax(1);qualified=(basecnt.sum(1)>=2)&(basecnt.max(1)/np.maximum(basecnt.sum(1),1e-8)>=.8)
    for trial in range(10):
        for number in [9,27,54]:
            chosen=rng.choice(n,number,replace=False);c1=cc.copy();c1[chosen]=(c1[chosen]+rng.integers(1,3,number))%3
            ct=counts(k,c1,ww,208,np.ones(n,bool));restored=ct.argmax(1)
            perturb.append(dict(kind='substitution',trial=trial,number=number,retained_reference_residues=int((restored[qualified]==ref[qualified]).sum()),reference_residues=int(qualified.sum()),injected_labels_corrected=int((restored[k[chosen]%208]==cc[chosen]).sum()),baseline_recoverable=int((ref[k[chosen]%208]==cc[chosen]).sum())))
        for kind,shift in [('single_index',1),('burst_index',1),('burst_index',6),('burst_index',7),('burst_color',0),('unobserved',0)]:
            bins=np.minimum((station[ii]/station[ii].max()*95).astype(int),95);lo=8+trial*7;affected=(bins>=lo)&(bins<=lo+5)
            if kind=='single_index':affected=np.zeros(n,bool);affected[rng.integers(n)]=True
            kk=k.copy();c1=cc.copy();w1=ww.copy()
            if 'index' in kind:kk[affected]+=shift
            if kind=='burst_color':c1[affected]=(c1[affected]+1)%3
            if kind=='unobserved':w1[affected]=0.
            th,_=probabilities(k,cc,ww,208,~affected)
            for penalty in [3.,6.,10.]:
                inferred,receipt=viterbi(kk,c1,w1,station[ii],th,np.ones(n,bool),penalty)
                perturb.append(dict(kind=kind,trial=trial,number=int(affected.sum()),imposed_shift=shift,penalty=penalty,offset_recovery=int((inferred[affected]==-shift).sum()) if shift else None,false_shift_elsewhere=int((inferred[~affected]!=0).sum()),changes=receipt['changes']))
    # Candidate-map pattern disagreement at E/G/H uses a motif learned with the
    # entire target geographic section withheld, common reference, same cohort.
    cases={}
    targetcases={'G':['NEW-1621-315','P5-1645-0309','C-1669-0293','NEW-1697-280','E5-1671-0325'],'H':['C-1125-2900','C-1119-2879','C-1098-2901','NEW-1074-2896','C-1144-2947'],'E':['C-1721-1566','C-1770-1577']}
    for case,targets in targetcases.items():
        excluded=set(blocks[ids.index(o)] for o in targets);train=~np.isin(bb,list(excluded));th,_=probabilities(k,cc,ww,208,train);rows=[]
        for o in targets:
            vals={}
            for name in ['working',{'G':'early','H':'lower','E':'closest'}[case]]:
                coord=canonical(states[name]).get(o)
                vals[name]=dict(index=int(np.dot(coord,[7,6])),prediction=COLORS[th[int(np.dot(coord,[7,6]))%208].argmax()],likelihood=float(th[int(np.dot(coord,[7,6]))%208,COLORS.index(obs[o]['color'])])) if coord is not None else None
            rows.append(dict(id=o,xy=obs[o]['xy'],color=obs[o]['color'],states=vals))
        cases[case]=dict(excluded_sections=sorted(excluded),rows=rows)
    save(out/'refinement.json.gz',dict(fits=fits,full208_entries=entries,full208_motif=''.join(e['color'][0].upper() if e['color']!='?' else '?' for e in entries),cross_predictions=crossrows,suspects=sorted(suspects,key=lambda s:(not s['correction_candidate'],not s['strong'],s['probabilities'][COLORS.index(s['color'])])),color_audit=colors,color_candidates=proposed,feedback=feedback,perturbations=perturb,cases=cases,seconds=time.perf_counter()-began,policy='Exploratory followup after original test opened. Color hypotheses and pattern-derived shifts are not adopted. Nearby measurements and reference predictions are correlated.'))
    print('FITS',fits,flush=True);print('COLOR CANDIDATES',proposed,flush=True);print('DONE',time.perf_counter()-began,flush=True)

if __name__=='__main__':main()
