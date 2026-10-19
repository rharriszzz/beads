"""Small, labeled post-scan diagnostics; no new search or image measurements."""
import argparse
from pathlib import Path
import numpy as np
from collections import Counter
from .analyze import evaluate,save,fit
from photo2.r330.pattern import dataset,COLORS
from photo2.r329.common import ROOT,read,canonical

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);args=ap.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=False)
    g,states,ids,obs,station,b0,c0,w0=dataset();base=canonical(states['working']);names=sorted(base);ii=np.array([ids.index(o) for o in names]);c,w,b=c0[ii],w0[ii],b0[ii];ab=np.array([base[o] for o in names]);A=ab@[7,6];B=ab@[6,7]
    models=[('A',104,None),('A',208,104),('B',207,None),('B',299,None),('A',306,None),('B',305,None)]
    controls=[];predictions={}
    for fam,p,parent in models:
        k=A if fam=='A' else B;N=2704 if fam=='A' else 2691
        r,pred,ba=evaluate(k,c,w,b,p,parent=parent,details=True);predictions[f'{fam}/{p}']=pred
        for cut in [0,500,1000,1500,2000]:
            kk=(k-cut)%N+cut
            controls.append(dict(evaluate(kk,c,w,b,p,parent=parent),family=fam,control='cyclic_cut',cut=cut))
        for mode in ['colored_only','equal_sections']:
            ww=w.copy()
            if mode=='colored_only':ww[c==2]=0
            else:
                for block in range(12):ww[b==block]/=ww[b==block].sum()/w.sum()*12
            # Zero-weight black rows still appear in agreement; log gain uses only
            # positive weights. Per-color diagnostics for zero mass are omitted.
            if mode=='colored_only':
                mask=c!=2;r=evaluate(k[mask],c[mask],ww[mask],b[mask],p,parent=parent)
            else:r=evaluate(k,c,ww,b,p,parent=parent)
            controls.append(dict(r,family=fam,control=mode))
    pairs=[]
    for fam,k,p in [('B',B,207),('B',B,299),('A',A,208),('A',A,306),('B',B,305)]:
        n=agree=0;diff=Counter()
        for i in range(len(k)):
            for j in range(i+1,len(k)):
                if abs(k[j]-k[i])!=p:continue
                u,v=(i,j) if k[j]>k[i] else (j,i);n+=1;agree+=int(c[u]==c[v]);diff[tuple((ab[v]-ab[u]).tolist())]+=1
        pairs.append(dict(family=fam,period=p,n=n,agree=agree,lattice_vectors={str(key):value for key,value in diff.items()}))
    # Residue partitions, not just score equality, audited on observed data.
    splitA=splitB=0
    for r in set(A%306):splitA+=len(set(B[A%306==r]%305))>1
    for r in set(B%305):splitB+=len(set(A[B%305==r]%306))>1
    candidates=read(ROOT/'photo2/r330/photography/g-replays.json.gz')[-1]['candidates'];grows=[]
    targets=['NEW-1621-315','P5-1645-0309','C-1669-0293','NEW-1697-280','E5-1671-0325'];excluded=[11,0,1]
    for name,state in [('working',states['working'])]+[(f'G-{j}',x['state']) for j,x in enumerate(candidates)]:
        co=canonical(state);present=np.array([o in co for o in names]);xy=np.array([co.get(o,(0,0)) for o in names])
        for fam,wt,p in [('A',[7,6],306),('B',[6,7],305)]:
            k=xy@wt;N=int(np.dot(state['H'],wt));r=evaluate(k,c,w,b,p,present)
            tr=~np.isin(b,excluded)&present;th,ba=fit(k,c,w,p,tr);targetrows=[]
            for o in targets:
                j=names.index(o);targetrows.append(dict(id=o,index=int(k[j]),color=COLORS[c[j]],probability=float(th[k[j]%p,c[j]])))
            grows.append(dict(r,name=name,family=fam,H=state['H'],N=N,cyclic=N%p==0,photo_score=state['score'],
                G_targets=targetrows,G_gain=float(np.mean([np.log(t['probability']/ba[COLORS.index(t['color'])]) for t in targetrows]))))
    phase=[]
    for r in range(13):phase.append(dict(phase=r,n=int(sum(A%13==r)),colors=dict(Counter(COLORS[j] for j in c[A%13==r]))))
    # A-repeat witnesses: actual B/207 phase drifts by exactly one for each
    # observed A+208 pair; all such pairs use delta_ab=(16,16).
    drift=[]
    for j,o in enumerate(names):
        if A[j]%208 in [0,19,32]:drift.append(dict(id=o,A=int(A[j]),B=int(B[j]),a=int(ab[j,0]),b=int(ab[j,1]),
            d=int(A[j]-B[j]),repeat=int(A[j]//208),residueA=int(A[j]%208),residueB207=int(B[j]%207),color=COLORS[c[j]]))
    save(out/'followup.json.gz',dict(controls=controls,pairs=pairs,G=grows,phase=phase,drift=sorted(drift,key=lambda x:x['A']),
        partition_A306_B305=dict(A_residues_splitting_B=splitA,B_residues_splitting_A=splitB,
            max_prediction_difference=float(np.max(abs(predictions['A/306']-predictions['B/305'])))),
        policy='Exploratory post-scan followup. Cyclic cuts test fragile nondivisor predictions; the true repeat must divide a verified physical N.'))

if __name__=='__main__':main()
