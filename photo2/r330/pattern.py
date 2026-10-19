"""Weighted periodic prediction and penalized piecewise-index Viterbi.

Run with --output a NEW directory. No writes to historical evidence. Color
weights are conservative sensitivity assumptions, not calibrated probabilities.
"""
import argparse, time
from collections import Counter
from pathlib import Path
import numpy as np
from photo2.r329.common import ROOT, read, save, canonical, sha

COLORS = ['red', 'yellow', 'black']
OUTER = [2, 5, 8, 11]

def dataset():
    g = read(ROOT/'photo2/r328/results/graph.json.gz')
    ss = read(ROOT/'photo2/r328/development/final256/search.json.gz')['states']
    novel = read(ROOT/'photo2/r329/results/novel-windings.json.gz')['alternatives']
    states = {('working' if i == 0 else 'closest' if i == 1 else 'lower' if i == 5 else f'saved-{i}'): s for i,s in enumerate(ss)}
    for i,r in enumerate(novel): states['early' if r['state']['H']==[214,176] else f'novel-{i}'] = r['state']
    ids = sorted(o['id'] for o in g['observations'])
    obs = {o['id']:o for o in g['observations']}
    station = np.array([g['stations_px'][o] % g['period_px'] for o in ids])
    blocks = np.minimum((station/g['period_px']*12).astype(int),11)
    color = np.array([COLORS.index(obs[o]['color']) for o in ids])
    # Do not interpret black highlights as body centers or as black pigment masks.
    weight = np.array([.55 if obs[o]['color']=='black' else 1. for o in ids])
    weight[np.array(['provisional' in str(obs[o]).lower() for o in ids])] = .25
    return g, states, ids, obs, station, blocks, color, weight

def counts(k, c, w, p, mask):
    return np.bincount((k[mask]%p)*3+c[mask],weights=w[mask],minlength=p*3).reshape(p,3)

def probabilities(k,c,w,p,mask):
    base = (np.bincount(c[mask],weights=w[mask],minlength=3)+1)
    base /= base.sum()
    cc = counts(k,c,w,p,mask)
    return (cc+3*base)/(cc.sum(1)[:,None]+3), base

def predictive(k,c,w,blocks,p,train_blocks,test_blocks):
    tr = np.isin(blocks,train_blocks); te = np.isin(blocks,test_blocks)
    theta,base = probabilities(k,c,w,p,tr)
    ll = np.log(theta[k[te]%p,c[te]])-np.log(base[c[te]])
    return float(np.sum(w[te]*ll)), float(w[te].sum())

def scan(k,c,w,blocks,periods):
    # Tune only on eight development sections. The other four remain unread
    # until a map/period shortlist has been frozen.
    dev = [b for b in range(12) if b not in OUTER]
    rows=[]
    for p in periods:
        gain=den=0.
        for test in [dev[::2],dev[1::2]]:
            a,b=predictive(k,c,w,blocks,p,[x for x in dev if x not in test],test)
            gain+=a;den+=b
        rows.append(dict(period=int(p),development_gain_nats=gain/den,
                         selection_score=gain/den-.1*p*np.log(3)/den))
    return sorted(rows,key=lambda r:-r['selection_score'])

def motif(k,c,w,blocks,p,mask):
    theta,base=probabilities(k,c,w,p,mask)
    cc=counts(k,c,w,p,mask);winner=cc.argmax(1)
    entries=[]
    for r in range(p):
        use=mask & (k%p==r); win=int(winner[r]);support=use & (c==win)
        groups=sorted(set(blocks[support].tolist()))
        fraction=float(cc[r,win]/max(cc[r].sum(),1e-9))
        known=len(groups)>=3 and fraction>=.8 and theta[r,win]>=.60
        entries.append(dict(residue=r,color=COLORS[win] if known else '?',plurality=COLORS[win],
            weighted_agreement=fraction,unique_observations=int(use.sum()),supporting_observations=int(support.sum()),
            supporting_sections=groups,observed_repeats=len(set((k[support]//p).tolist())),posterior=theta[r].tolist()))
    return theta,entries

def viterbi(k,c,w,station,theta,fit_mask,penalty=6.,maxshift=21):
    """Piecewise phase offsets in 96 photographic bins; transitions 0,+/-1,6,7.

    Missing index positions have no emission: they are unobserved physical beads.
    Unknown colors have weight zero. No insertions/deletions of physical beads.
    """
    p=len(theta); bins=np.minimum((station/station.max()*95).astype(int),95)
    shifts=np.arange(-maxshift,maxshift+1); S=len(shifts)
    emissions=np.zeros((96,S))
    for j,d in enumerate(shifts):
        ll=-w*np.log(theta[(k+d)%p,c])
        emissions[:,j]=np.bincount(bins[fit_mask],weights=ll[fit_mask],minlength=96)
    delta=shifts[None,:]-shifts[:,None]
    transition=np.where(delta==0,0.,np.where(np.isin(abs(delta),[1,6,7]),penalty,np.inf))
    cost=emissions[0]+np.where(shifts==0,0.,penalty)
    back=[]
    for e in emissions[1:]:
        mat=cost[:,None]+transition; ptr=mat.argmin(0);back.append(ptr);cost=e+mat[ptr,np.arange(S)]
    state=int(cost.argmin());path=[state]
    for ptr in back[::-1]:state=int(ptr[state]);path.append(state)
    path=np.array(path[::-1]);offset=shifts[path]
    return offset[bins],dict(bin_offsets=offset.tolist(),changes=int(np.count_nonzero(np.diff(offset))),penalty=penalty,cost=float(cost.min()))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--max-period',type=int,default=900);ap.add_argument('--controls',type=int,default=39);args=ap.parse_args()
    out=Path(args.output);out.mkdir(parents=True,exist_ok=False);start=time.perf_counter()
    g,states,ids,obs,station,blocks,c,w=dataset(); index={o:i for i,o in enumerate(ids)}
    save(out/'input-seal.json',dict(sources={str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'beads-photo-2.jpg',ROOT/'photo2/r328/results/graph.json.gz',ROOT/'photo2/r328/development/final256/search.json.gz',ROOT/'photo2/r329/results/novel-windings.json.gz']},outer_blocks=OUTER,policy='Outer sections not used for map/period selection; later diagnostics do not count as independent confirmation.'))
    datasets={}; scans=[]
    for name,state in states.items():
        co=canonical(state);ii=np.array([index[o] for o in ids if o in co]);ab=np.array([co[ids[i]] for i in ii])
        for family,wt in [('A',(7,6)),('B',(6,7))]:
            key=name+'-'+family;k=ab@wt; N=int(np.dot(state['H'],wt))
            rows=scan(k,c[ii],w[ii],blocks[ii],range(1,args.max_period+1))
            datasets[key]=(ii,k,N);scans.append(dict(map=key,N=N,H=state['H'],ranking=rows))
        print('scan',name,round(time.perf_counter()-start,2),flush=True)
    # Freeze six best map-periods and six distinct periods using development only.
    ranked=sorted([dict(r,map=s['map'],N=s['N']) for s in scans for r in s['ranking'][:8]],key=lambda r:-r['selection_score'])
    selected=ranked[:6];seen={r['period'] for r in selected}
    for r in ranked:
        if r['period'] not in seen: selected.append(r);seen.add(r['period'])
        if len(seen)>=6:break
    save(out/'development-scan.json.gz',dict(scans=scans,shortlist=selected))
    candidates=[]
    for cand in selected:
        key,p=cand['map'],cand['period'];ii,k,N=datasets[key];cc,ww,bb=c[ii],w[ii],blocks[ii];tr=~np.isin(bb,OUTER);te=~tr
        theta,entries=motif(k,cc,ww,bb,p,tr); gain,den=predictive(k,cc,ww,bb,p,[b for b in range(12) if b not in OUTER],OUTER)
        known=np.array([e['color']!='?' for e in entries]);pred=theta.argmax(1)[k%p]
        rows=[]
        for j,i in enumerate(ii):
            e=entries[int(k[j]%p)];rows.append(dict(id=ids[i],xy=obs[ids[i]]['xy'],index=int(k[j]),residue=int(k[j]%p),color=COLORS[cc[j]],weight=float(ww[j]),section=int(bb[j]),held_out=bool(te[j]),prediction=e['color'],probability=float(theta[k[j]%p,cc[j]]),conflict=e['color']!='?' and e['color']!=COLORS[cc[j]]))
        percolor={color:dict(observations=int((cc==j).sum()),heldout=int((te&(cc==j)).sum()),known_predictions=int((known[k%p]&(cc==j)).sum()),heldout_known=int((te&known[k%p]&(cc==j)).sum()),heldout_correct=int((te&known[k%p]&(cc==j)&(pred==cc)).sum())) for j,color in enumerate(COLORS)}
        # Frozen motif; fit shifts on development observations only, evaluate outer
        # sections without using their colors to select offsets.
        align=[]
        for penalty in [3.,6.,10.]:
            shift,receipt=viterbi(k,cc,ww,station[ii],theta,tr,penalty)
            loggain=np.log(theta[(k+shift)%p,cc])-np.log(theta[k%p,cc])
            align.append(dict(**receipt,development_gain=float(np.average(loggain[tr],weights=ww[tr])),outer_gain=float(np.average(loggain[te],weights=ww[te])),offsets=[dict(id=ids[i],shift=int(s)) for i,s in zip(ii,shift) if s]))
        # Reverse and origin are gauge transformations, checked numerically below.
        candidates.append(dict(**cand,outer_gain_nats=gain/den,exact_cyclic_compatible=N%p==0,compatible_counts=[n for n in range(2000,3601) if n%p==0],motif=''.join(e['color'][0].upper() if e['color']!='?' else '?' for e in entries),entries=entries,per_color=percolor,rows=rows,alignments=align))
    # Correlated null: independently circularly rotate labels within geographic
    # sections; retain labels/counts/local sequence order within each section.
    # Full period search per null; only best selected map (conditional, not global).
    key=selected[0]['map'];ii,k,N=datasets[key];rng=np.random.default_rng(330);null=[]
    for trial in range(args.controls):
        cc=c[ii].copy();ww=w[ii].copy()
        for block in range(12):
            jj=np.flatnonzero(blocks[ii]==block);jj=jj[np.argsort(k[jj])];shift=int(rng.integers(len(jj)))
            cc[jj]=np.roll(cc[jj],shift);ww[jj]=np.roll(ww[jj],shift)
        null.append(scan(k,cc,ww,blocks[ii],range(1,args.max_period+1))[0])
    # Mapping sensitivity at the selected periods, including own-N compatibility.
    sensitivity=[]
    for key,(ii,k,N) in datasets.items():
        for p in sorted(seen):
            gain,den=predictive(k,c[ii],w[ii],blocks[ii],p,[b for b in range(12) if b not in OUTER],OUTER)
            sensitivity.append(dict(map=key,period=p,N=N,outer_gain_nats=gain/den,exact_cyclic_compatible=N%p==0))
    save(out/'patterns.json.gz',dict(candidates=candidates,sensitivity=sensitivity,null=dict(map=selected[0]['map'],trials=null,conditional_empirical_tail=(1+sum(r['selection_score']>=selected[0]['selection_score'] for r in null))/(1+len(null))),seconds=time.perf_counter()-start,scope='Approximate/incomplete motif tests; no physical count or graph adopted. Independent sections are conservative proxies, not independently labeled truth.'))
    print('BEST',[(r['map'],r['period'],round(r['development_gain_nats'],4),round(r['outer_gain_nats'],4),len(r['motif'].replace('?',''))) for r in candidates],flush=True)

if __name__=='__main__':main()
