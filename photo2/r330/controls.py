"""Post-selection robustness controls; no model or observation mutation."""
import argparse,time
from pathlib import Path
import numpy as np
from .pattern import dataset,canonical,scan,probabilities,viterbi,COLORS,OUTER
from .refine import hierarchical,save
from photo2.r329.common import read

def mapping_followup(out):
    g,states,ids,obs,station,blocks,c,w=dataset();index={o:i for i,o in enumerate(ids)};base=canonical(states['working']);names=sorted(base);ii=np.array([index[o] for o in names]);runs=[]
    maps=[dict(name=name,state=s,kind='saved',family=fam) for name,s in states.items() for fam in ['A','B']]
    maps += [dict(name='G-'+str(j),state=r['state'],kind='G',family='A',last_replaced=r['last_replaced']) for j,r in enumerate(read(out.parent/'photography/g-replays.json.gz')[-1]['candidates'])]
    maps += [dict(name='H-'+str(j),state=r['state'],kind='H',family='A') for j,r in enumerate(read(out.parent/'checks/h-bundle-repair.json.gz')['candidates'])]
    for m in maps:
        co=canonical(m['state']);present=np.array([o in co for o in names]);wt=[7,6] if m['family']=='A' else [6,7];k=np.array([np.dot(co[o],wt) if o in co else 0 for o in names]);pred=np.zeros((len(names),3));bas=np.zeros_like(pred)
        for block in range(12):
            tr=(blocks[ii]!=block)&present;te=blocks[ii]==block;theta=hierarchical(k,c[ii],w[ii],208,tr,1.);_,ba=probabilities(k,c[ii],w[ii],208,tr);pred[te]=theta[k[te]%208];bas[te]=ba;pred[te&~present]=ba
        loggain=np.log(pred[np.arange(len(ii)),c[ii]])-np.log(bas[np.arange(len(ii)),c[ii]])
        runs.append(dict(name=m['name'],kind=m['kind'],family=m['family'],H=m['state']['H'],last_replaced=m.get('last_replaced'),missing_primary_observations=int((~present).sum()),additional_observations=sorted(set(co)-set(base)),own_motif_gain_nats=float(np.average(loggain,weights=w[ii])),hard_agreement=float((pred.argmax(1)==c[ii]).mean())))
    # Exploratory second decoder check using the refined motif and original
    # development/outer partition. Outer colors still do not choose offsets.
    k=np.array([base[o] for o in names])@[7,6];train=~np.isin(blocks[ii],OUTER);theta=hierarchical(k,c[ii],w[ii],208,train,1.);align=[]
    for penalty in [3.,6.,10.]:
        shift,r=viterbi(k,c[ii],w[ii],station[ii],theta,train,penalty);gain=np.log(theta[(k+shift)%208,c[ii]])-np.log(theta[k%208,c[ii]])
        align.append(dict(**r,development_gain=float(np.average(gain[train],weights=w[ii][train])),outer_gain=float(np.average(gain[~train],weights=w[ii][~train])),offsets=[dict(id=o,shift=int(s)) for o,s in zip(names,shift) if s]))
    save(out/'mapping-followup.json.gz',dict(runs=runs,refined_alignment=align,policy='Exploratory own-map motif refits on each held-out-section complement. A common 900-observation target cohort is used; missing candidate indices predict only training color frequencies. This avoids penalizing a candidate merely for a phase change relative to a working-map motif. Added observations are listed separately.'))
    print('OWN MAP',len(runs),'best',sorted(runs,key=lambda r:-r['own_motif_gain_nats'])[:3],flush=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--null-trials',type=int,default=19);ap.add_argument('--mapping-followup',action='store_true');args=ap.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=False);start=time.perf_counter()
    if args.mapping_followup:mapping_followup(out);return
    g,states,ids,obs,station,blocks,c,w=dataset();index={o:i for i,o in enumerate(ids)};datasets=[]
    for name,s in states.items():
        co=canonical(s);ii=np.array([index[o] for o in ids if o in co]);ab=np.array([co[ids[i]] for i in ii])
        for fam,wt in [('A',[7,6]),('B',[6,7])]:datasets.append((name+'-'+fam,ii,ab@wt))
    _,ii,k=datasets[0];rng=np.random.default_rng(33066);null=[]
    # Same permuted photo labels for all maps: maximize over the complete
    # original search so map selection is also present in the null comparison.
    order=[]
    for b in range(12):
        jj=np.flatnonzero(blocks==b);order.append(jj[np.argsort(station[jj])])
    for trial in range(args.null_trials):
        cp=c.copy();wp=w.copy()
        for jj in order:
            shift=int(rng.integers(len(jj)));cp[jj]=np.roll(c[jj],shift);wp[jj]=np.roll(w[jj],shift)
        best=None
        for name,idx,kk in datasets:
            row=scan(kk,cp[idx],wp[idx],blocks[idx],range(1,901))[0]
            if best is None or row['selection_score']>best['selection_score']:best=dict(row,map=name)
        null.append(best);print('global null',trial+1,round(best['selection_score'],4),flush=True)
    weights=[]
    for black_weight in [.25,.55,1.]:
        ww=np.where(c[ii]==2,black_weight,1.)
        for p in [104,208,416]:
            pred=np.zeros((len(ii),3));base=np.zeros_like(pred)
            for b in range(12):
                tr=blocks[ii]!=b;te=~tr;th=hierarchical(k,c[ii],ww,p,tr,1.);_,bas=probabilities(k,c[ii],ww,p,tr);pred[te]=th[k[te]%p];base[te]=bas
            gain=np.log(pred[np.arange(len(ii)),c[ii]])-np.log(base[np.arange(len(ii)),c[ii]])
            weights.append(dict(black_weight=black_weight,period=p,gain_nats=float(np.average(gain,weights=ww)),hard_agreement=float((pred.argmax(1)==c[ii]).mean())))
    # Explicit collision/coverage audit. Geographic feature proximity is not
    # sufficient to merge observations, especially specular highlights.
    co=canonical(states['working']);aliases={}
    for o,ab in co.items():aliases.setdefault(int(np.dot(ab,[7,6]))%2704,[]).append(o)
    xy=np.array([obs[o]['xy'] for o in ids]);dist=np.linalg.norm(xy[:,None]-xy[None,:],axis=2);pairs=np.argwhere(np.triu(dist<12,1));near=[dict(a=ids[a],b=ids[b],distance=float(dist[a,b]),both_indexed=ids[a] in co and ids[b] in co) for a,b in pairs]
    save(out/'controls.json.gz',dict(global_selection_null=null,weight_sensitivity=weights,index_aliases=[dict(index=k,ids=v) for k,v in aliases.items() if len(v)>1],nearby_observations=near,unindexed=[dict(id=o,xy=obs[o]['xy'],color=obs[o]['color']) for o in ids if o not in co],seconds=time.perf_counter()-start,policy='No null creates an image or a new physical bead. Circular within-section label shifts preserve section color totals and most local order. Repeated residues and overlapping photo references are not independent labels. Nearby supports are unresolved duplicate/neighbor candidates, not automatically merged.'))

if __name__=='__main__':main()
