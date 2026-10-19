"""Bounded cached-data study. All new evaluations are exploratory reuse.

No detection, growth, rendering, relabeling or graph mutation. A new output
directory is mandatory. Original noisy labels remain the scoring reference.
"""
import argparse
import csv
import json
import time
from collections import Counter
from pathlib import Path
import numpy as np
from photo2.r330.pattern import dataset, counts, probabilities, scan, COLORS
from photo2.r329.common import ROOT, canonical, read, sha

BASE = '422a85ea10974f54ad5345b337d778448e7be48a'
PERIODS = [104] + list(range(200,400))

def save(path, value):
    from photo2.r330.refine import save as safe
    safe(path, value)

def fit(k,c,w,p,tr,parent=None,robust=False):
    theta,base=probabilities(k,c,w,p,tr)
    if parent:
        assert p%parent==0
        prior,_=probabilities(k,c,w,parent,tr)
        cc=counts(k,c,w,p,tr)
        theta=(cc+prior[np.arange(p)%parent])/(cc.sum(1)[:,None]+1)
    if robust:
        # One bounded Huber-like reweighting; target section never participates.
        ww=w.copy();ww[tr]*=np.minimum(1.,theta[k[tr]%p,c[tr]]/.25)
        theta,base=probabilities(k,c,ww,p,tr)
    return theta,base

def evaluate(k,c,w,b,p,present=None,parent=None,robust=False,guard=0,details=False):
    n=len(k);present=np.ones(n,bool) if present is None else present
    pred=np.zeros((n,3));baseline=np.zeros_like(pred);phase=np.zeros_like(pred)
    for block in range(12):
        excluded=[(block+d)%12 for d in range(-guard,guard+1)]
        tr=~np.isin(b,excluded)&present;te=b==block
        th,ba=fit(k,c,w,p,tr,parent,robust);ph,_=probabilities(k,c,w,13,tr)
        pred[te]=th[k[te]%p];baseline[te]=ba;phase[te]=ph[k[te]%13]
        pred[te&~present]=ba
    log=np.log(pred[np.arange(n),c])-np.log(baseline[np.arange(n),c])
    phasegain=np.log(pred[np.arange(n),c])-np.log(phase[np.arange(n),c])
    per=np.array([np.average(log[b==x],weights=w[b==x]) for x in range(12)])
    r=dict(period=p,parent=parent,robust=robust,guard=guard,gain_nats=float(np.average(log,weights=w)),
        gain_over_phase13=float(np.average(phasegain,weights=w)),agreement=float((pred.argmax(1)==c).mean()),
        penalized_gain=float(np.average(log,weights=w)-.1*(p+(parent or 0))*np.log(3)/w.sum()),
        per_section=per.tolist(),section_se=float(per.std(ddof=1)/np.sqrt(12)),
        per_color={col:dict(n=int((c==j).sum()),agreement=float((pred.argmax(1)[c==j]==j).mean()),
            gain=float(np.average(log[c==j],weights=w[c==j]))) for j,col in enumerate(COLORS)},
        indexed=int(present.sum()))
    return (r,pred,baseline) if details else r

def motif_entries(names,k,c,w,b,p):
    cc=counts(k,c,w,p,np.ones(len(k),bool));entries=[]
    for r in range(p):
        ix=np.flatnonzero(k%p==r);winner=int(cc[r].argmax());support=ix[c[ix]==winner]
        fraction=float(cc[r,winner]/max(cc[r].sum(),1e-12));sections=sorted(set(b[support].tolist()))
        known=len(support)>=3 and len(sections)>=3 and fraction>=.8
        entries.append(dict(residue=r,color=COLORS[winner] if known else '?',plurality=COLORS[winner],
            fraction=fraction,sections=sections,observations=len(ix),supporting=len(support),
            ids=[names[i] for i in ix],indices=k[ix].tolist()))
    return entries

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--null-trials',type=int,default=19)
    args=ap.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=False);start=time.perf_counter()
    g,states,ids,obs,station,blocks,c0,w0=dataset();lookup={o:i for i,o in enumerate(ids)}
    working=canonical(states['working']);names=sorted(working);ii=np.array([lookup[o] for o in names]);c,w,b=c0[ii],w0[ii],blocks[ii]
    ab=np.array([working[o] for o in names]);A=ab@[7,6];B=ab@[6,7]
    sources=['beads-photo-2.jpg','INITIAL_QUESTION.md','photo2/r328/results/graph.json.gz',
        'photo2/r328/development/final256/search.json.gz','photo2/r329/results/novel-windings.json.gz',
        'photo2/r330/refinement/refinement.json.gz','photo2/r330/photography/g-replays.json.gz',
        'photo2/r330/photography/photography.json.gz']
    save(out/'input-seal.json',dict(base_commit=BASE,sources={s:sha(ROOT/s) for s in sources},
        policy='Exploratory reuse of R330 observations; no new blind photographic test. No graph/count/pattern adopted.'))
    maps=[];rankings=[];loso=[]
    for name,state in states.items():
        co=canonical(state);present=np.array([o in co for o in names]);xy=np.array([co.get(o,(0,0)) for o in names])
        for family,wt in [('A',[7,6]),('B',[6,7])]:
            k=xy@wt;N=int(np.dot(state['H'],wt));key=name+'-'+family
            maps.append((key,k,present,N));ranking=scan(k[present],c[present],w[present],b[present],PERIODS)
            rankings.append(dict(map=key,N=N,H=state['H'],ranking=ranking))
            # Same fixed common cohort; absent candidate associations score baseline.
            for p in PERIODS:
                if name=='working' or (p%13 and N%p==0):
                    r=evaluate(k,c,w,b,p,present);loso.append(dict(r,map=key,N=N,cyclic=N%p==0,maker=p in range(200,400) and p%13!=0))
    print('cached scans',round(time.perf_counter()-start,2),flush=True)
    work=[r for r in loso if r['map'].startswith('working-')]
    maker=sorted([r for r in work if r['maker']],key=lambda r:-r['penalized_gain'])
    shortlist={('A',104,None),('A',208,None),('A',208,104),('B',207,None),('B',207,69),('B',299,None),('A',338,None)}
    shortlist.update((r['map'][-1],r['period'],None) for r in maker[:4])
    sensitivity=[]
    for family,p,parent in sorted(shortlist,key=str):
        k=A if family=='A' else B
        for black_weight in [.25,.55,1.]:
            ww=w.copy();ww[c==2]=black_weight
            for guard in [0,1]:
                r=evaluate(k,c,ww,b,p,parent=parent,guard=guard)
                sensitivity.append(dict(r,family=family,black_weight=black_weight))
        sensitivity.append(dict(evaluate(k,c,w,b,p,parent=parent,robust=True),family=family,black_weight=.55))
    # Exact lattice-derived alias witnesses. No scaling A by 207/208 is assumed.
    pairs=[]
    for i in range(len(A)):
        for j in range(i+1,len(A)):
            if A[j]-A[i] in [104,208] or A[i]-A[j] in [104,208]:
                if A[j]<A[i]:u,v=j,i
                else:u,v=i,j
                pairs.append(dict(a=names[u],z=names[v],deltaA=int(A[v]-A[u]),deltaB=int(B[v]-B[u]),
                    delta_ab=(ab[v]-ab[u]).tolist(),delta_d=int((A[v]-B[v])-(A[u]-B[u])),same_color=bool(c[u]==c[v])))
    # Phase-only / local-diagonal baselines and phase drift across B/207 repeats.
    baselines=[]
    for fam,k in [('A',A),('B',B)]:
        for p in [1,13,26,52,104,207,208,299]:baselines.append(dict(evaluate(k,c,w,b,p),family=fam))
    alias=dict(identities=['A-B=a-b','A+B=13(a+b)','B mod 13 = -A mod 13'],
        H=[214,201],N_A=2704,N_B=2691,divisors_A=[p for p in range(200,400) if 2704%p==0],
        divisors_B=[p for p in range(200,400) if 2691%p==0],d_histogram=dict(Counter((A-B).tolist())),pairs=pairs,
        pair_summary={str(p):dict(n=sum(x['deltaA']==p for x in pairs),deltaB=dict(Counter(x['deltaB'] for x in pairs if x['deltaA']==p)),
            same_color=sum(x['same_color'] for x in pairs if x['deltaA']==p)) for p in [104,208]},
        repeat_vector_A208_B207=[214/13,201/13],
        explanation='Simultaneous A+208/B+207 needs fractional lattice vector H/13. Actual A+208 pairs have deltaB divisible by13, usually208; a B207 repeat instead changes geometric phase by -1. Thirteen such repeats close arithmetically, not photographically.')
    # Stronger conditional nulls. Full original 40-map selection is repeated.
    # 1: move each entire section by a multiple of13 in index, preserving ALL
    # within-section relative indices, colors, weights and phase13 exactly.
    # 2: rotate labels+weights within (section,geometric phase), preserving exact
    # phase-color totals and most phase-lane local ordering, less 2D correlation.
    null=[];rng=np.random.default_rng(331)
    observed_best=max(r['ranking'][0]['selection_score'] for r in rankings)
    for kind in ['section_translation13','phase_lane_rotation']:
        records=[]
        for trial in range(args.null_trials):
            shifts=rng.integers(0,64,12)*13;cp=c.copy();wp=w.copy()
            if kind=='phase_lane_rotation':
                for block in range(12):
                    for phase in range(13):
                        jj=np.flatnonzero((b==block)&(A%13==phase));jj=jj[np.argsort(station[ii[jj]])]
                        if len(jj):
                            offset=int(rng.integers(len(jj)));cp[jj]=np.roll(c[jj],offset);wp[jj]=np.roll(w[jj],offset)
            best=None
            for key,k,present,N in maps:
                kk=k+shifts[b] if kind=='section_translation13' else k
                r=scan(kk[present],cp[present],wp[present],b[present],PERIODS)[0]
                if best is None or r['selection_score']>best['selection_score']:best=dict(r,map=key)
            alias_scores=[]
            for fam,k,p,parent in [('A',A,104,None),('A',A,208,104),('B',B,207,None)]:
                kk=k+shifts[b] if kind=='section_translation13' else k
                alias_scores.append(dict(evaluate(kk,cp,wp,b,p,parent=parent),family=fam))
            records.append(dict(trial=trial,best=best,fixed_models=alias_scores,section_offsets=shifts.tolist() if kind=='section_translation13' else None))
        null.append(dict(kind=kind,records=records,observed_best_selection=observed_best,
            empirical_tail=(1+sum(r['best']['selection_score']>=observed_best for r in records))/(1+len(records))))
        print('null',kind,round(time.perf_counter()-start,2),flush=True)
    # G alternatives: each owns its map; common fixed 900 targets; exclude G's
    # section and neighboring sections before evaluating G itself.
    gcandidates=read(ROOT/'photo2/r330/photography/g-replays.json.gz')[-1]['candidates']
    gs=[('working',states['working'],None),('early',states['early'],34)]+[(f'G-{j}',x['state'],x['last_replaced']) for j,x in enumerate(gcandidates)]
    grows=[];target=['NEW-1621-315','P5-1645-0309','C-1669-0293','NEW-1697-280','E5-1671-0325']
    gsection=int(b[names.index(target[0])]);gexcluded=[(gsection+d)%12 for d in [-1,0,1]]
    for name,state,last in gs:
        co=canonical(state);present=np.array([o in co for o in names]);xy=np.array([co.get(o,(0,0)) for o in names])
        for fam,wt,p,parent in [('A',[7,6],208,104),('B',[6,7],207,None),('B',[6,7],207,69),('B',[6,7],299,None)]:
            k=xy@wt;N=int(np.dot(state['H'],wt));r=evaluate(k,c,w,b,p,present,parent)
            tr=~np.isin(b,gexcluded)&present;th,ba=fit(k,c,w,p,tr,parent)
            tt=[]
            for o in target:
                i=names.index(o);tt.append(dict(id=o,index=int(k[i]),color=COLORS[c[i]],probability=float(th[k[i]%p,c[i]]),
                    prediction=COLORS[th[k[i]%p].argmax()],xy=obs[o]['xy']))
            grows.append(dict(r,name=name,family=fam,N=N,H=state['H'],cyclic=N%p==0,
                photo_score=state['score'],last_replaced=last,changed=int(sum(co.get(o)!=working[o] for o in names)),
                excluded_G_sections=gexcluded,G_targets=tt,G_gain=float(np.mean([np.log(t['probability']/ba[COLORS.index(t['color'])]) for t in tt]))))
    motifs=[]
    for fam,p in [('A',104),('A',208),('B',207),('B',299)]+[(r['map'][-1],r['period']) for r in maker[:2]]:
        k=A if fam=='A' else B;entries=motif_entries(names,k,c,w,b,p)
        motifs.append(dict(family=fam,period=p,entries=entries,known=sum(e['color']!='?' for e in entries),
            unobserved=sum(e['observations']==0 for e in entries)))
    proposals=read(ROOT/'photo2/r330/refinement/refinement.json.gz')['color_candidates'];color_checks=[]
    for fam,p,parent in [('A',208,104),('B',207,None),('B',299,None)]:
        k=A if fam=='A' else B;_,pred,_=evaluate(k,c,w,b,p,parent=parent,details=True)
        for o,col in proposals.items():
            j=names.index(o);color_checks.append(dict(id=o,family=fam,period=p,index=int(k[j]),original=COLORS[c[j]],
                proposed=col,proposed_probability=float(pred[j,COLORS.index(col)]),prediction=COLORS[pred[j].argmax()] ,probabilities=pred[j].tolist()))
    save(out/'analysis.json.gz',dict(alias=alias,scans=rankings,loso=loso,baselines=baselines,
        sensitivity=sensitivity,nulls=null,G=grows,motifs=motifs,color_checks=color_checks,
        best_maker=maker[:12],seconds=time.perf_counter()-start))
    with (out/'periods.csv').open('w',newline='') as f:
        fields=['map','N','period','cyclic','maker','gain_nats','gain_over_phase13','penalized_gain','agreement','section_se']
        wr=csv.DictWriter(f,fields,extrasaction='ignore',lineterminator='\n');wr.writeheader();wr.writerows(loso)
    print('BEST MAKER',[(r['map'],r['period'],round(r['gain_nats'],4),r['cyclic']) for r in maker[:8]],flush=True)
    print('DONE',round(time.perf_counter()-start,3),flush=True)

if __name__=='__main__':main()
