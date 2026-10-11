"""Exact linear-string repetition diagnostics; unknown colors never imply black.

The photographic origin is a label. A manufacturing seam is a separate cut of
its circular index chart, essential when P does not divide N.
"""
from __future__ import annotations
import argparse, csv, gzip, json, math
from collections import defaultdict
from pathlib import Path
import numpy as np
from global_fit_r253 import ROOT, save, table
OLD=ROOT/'photo2/review/r253'
OUT=ROOT/'photo2/review/r254'
COLORS=('red','yellow','black')


def residues(rows, period, n=None, cut=0):
    groups=[{c:[] for c in COLORS} for _ in range(period)]
    for r in rows:
        k=int(r['k'])
        if cut and k>=cut: k-=n  # anchor k=0 is preserved; seam is elsewhere
        groups[k%period][r['color']].append(r['observation_id'])
    return groups


def diagnostic(rows, period, n=None, cut=0):
    groups=residues(rows,period,n,cut)
    counts=np.array([[len(g[c]) for c in COLORS] for g in groups])
    loss=counts.sum(1)-counts.max(1)
    template=''.join('?' if not sum(map(len,g.values())) else
                     '!' if sum(bool(v) for v in g.values())>1 else
                     next(c[0].upper() for c,v in g.items() if v) for g in groups)
    return dict(P=period,minimum_conflicting_assignments=int(loss.sum()),
                conflict_residues=int((loss>0).sum()),constrained_residues=int((counts.sum(1)>0).sum()),
                unknown=template.count('?'),template=template,exact=not bool(loss.sum()),
                admissible_by_maker=period%13!=0 and (n is None or n%period==0),groups=groups)


def cut_scan(rows,n,period):
    """Exhaust all observationally distinct seams with incremental exact counts."""
    rr=sorted(rows,key=lambda r:r['k']);counts=np.zeros((period,3),int)
    for r in rr: counts[int(r['k'])%period,COLORS.index(r['color'])]+=1
    def loss(q):return int(q.sum()-q.max())
    total=sum(loss(q) for q in counts);best=total;cuts=[0];feasible=[0] if total==0 else []
    # Moving the cut past each point lifts its k by N. A global shift by -N
    # restores the anchor without changing conflicts. Include all unique gaps.
    byk=defaultdict(list)
    for r in rr:byk[int(r['k'])].append(r)
    for k,rs in byk.items():
        for r in rs:
            c=COLORS.index(r['color']);a=k%period;b=(k+n)%period
            if a==b:continue
            total-=loss(counts[a])+loss(counts[b]);counts[a,c]-=1;counts[b,c]+=1
            total+=loss(counts[a])+loss(counts[b])
        cut=k+1
        if total<best:best=total;cuts=[cut]
        elif total==best:cuts.append(cut)
        if total==0:feasible.append(cut)
    return dict(minimum=best,best_cuts=cuts,exact_cuts=feasible)


def propagate(rows, domains, period):
    """Sound necessary-condition propagation, with replayable small witnesses.

    Domains are index options. Enforces singleton identity and singleton residue
    color. Failure proves infeasibility of these domains; survival is NOT SAT.
    """
    ds=[set(d) for d in domains];reasons=[{r['observation_id']} for r in rows]
    while True:
        for i,d in enumerate(ds):
            if not d:return dict(status='infeasible',witness=sorted(reasons[i]),domains=[sorted(x) for x in ds])
        changed=False;fixed={};color={}
        for i,d in enumerate(ds):
            if len(d)==1:
                k=next(iter(d))
                if k in fixed:
                    j=fixed[k];return dict(status='infeasible',witness=sorted(reasons[i]|reasons[j]),reason='identity_collision',domains=[sorted(x) for x in ds])
                fixed[k]=i
            rs={k%period for k in d}
            if len(rs)==1:
                q=next(iter(rs))
                if q in color and rows[color[q]]['color']!=rows[i]['color']:
                    j=color[q];return dict(status='infeasible',witness=sorted(reasons[i]|reasons[j]),reason='residue_color',domains=[sorted(x) for x in ds])
                color[q]=i
        for i,d in enumerate(ds):
            for k in list(d):
                j=fixed.get(k,i);q=color.get(k%period,i)
                bad=j if j!=i else q if rows[q]['color']!=rows[i]['color'] else None
                if bad is not None:
                    d.remove(k);reasons[i]|=reasons[bad];changed=True
        if not changed:return dict(status='unresolved',witness=[],domains=[sorted(x) for x in ds])


def fixed(out=OUT):
    out.mkdir(parents=True,exist_ok=True);models=json.loads((OLD/'models.json').read_text());selected=json.loads((OLD/'selected.json').read_text())
    scans=[];summaries=[];details={};alternatives=[]
    for m in models:
        mid=m['model_id'];rows=json.loads((OLD/f'{mid}-assignments.json').read_text())
        for subset in ['unique','all','train_unique']:
            use=[r for r in rows if subset=='all' or r['conditional_unique'] and (subset!='train_unique' or r['split']=='train')]
            rr=[]
            for P in range(1,400):
                d=diagnostic(use,P,m['n']);seam=cut_scan(use,m['n'],P) if subset!='train_unique' else None
                rec=dict(model_id=mid,subset=subset,n_observations=len(use),**{k:v for k,v in d.items() if k not in ('groups','template')},
                         any_seam_minimum=seam['minimum'] if seam else '',best_cuts=';'.join(map(str,seam['best_cuts'])) if seam else '')
                scans.append(rec);rr.append(rec)
                if mid in selected and subset=='unique':details[f'{mid}/P{P}']=d
            best=min(rr,key=lambda r:(r['minimum_conflicting_assignments'],r['P']));allowed=[r for r in rr if r['admissible_by_maker']];abest=min(allowed,key=lambda r:(r['minimum_conflicting_assignments'],r['P']))
            summaries.append(dict(model_id=mid,subset=subset,n=m['n'],h=m['h'],n_observations=len(use),
                 geometry_train_score=m['train_score'],geometry_test_patch_support=m['test']['patch_support'],
                 best_P=best['P'],min_conflicts=best['minimum_conflicting_assignments'],admissible_periods=[r['P'] for r in allowed],best_admissible_P=abest['P'],admissible_min_conflicts=abest['minimum_conflicting_assignments'],
                 exact_periods=[r['P'] for r in rr if r['exact'] and r['admissible_by_maker']],
                 exact_any_seam_periods=[r['P'] for r in rr if r['any_seam_minimum']==0 and r['admissible_by_maker']],
                 any_seam_minimum=min(r['any_seam_minimum'] for r in rr) if subset!='train_unique' else None))
        # Strict exact-positive-representative domains, kept distinct from the
        # unsupported four-nearest alternative envelope.
        strict=[[a['k'] for a in r['alternatives'] if a['generator_index']==r['first_owner'] and not r['unfinished']] for r in rows]
        no_owner=[r['observation_id'] for r,d in zip(rows,strict) if not d]
        alternatives.append(dict(model_id=mid,domain_policy='exact_representative_owner',missing=no_owner,
                multiple_domains=sum(len(d)>1 for d in strict),status='infeasible_all_P' if no_owner else 'requires_period_scan',
                anchor_owned=next(r['ownership'] for r in rows if r['observation_id']=='C252-A948')))
        print(mid,'fixed complete',flush=True)
    table(out/'fixed-periods.csv',scans);save(out/'fixed-summary.json',summaries);save(out/'strict-domains.json',alternatives)
    with (out/'selected-residue-constraints.json.gz').open('wb') as f:
        f.write(gzip.compress(json.dumps(details,separators=(',',':')).encode(),mtime=0))
    # Select diagnostic periods using training colors only. Conflicted residues
    # abstain; never majority-vote a trusted color away.
    evaluations=[]
    for m in models:
        mid=m['model_id'];rows=json.loads((OLD/f'{mid}-assignments.json').read_text());train=[r for r in rows if r['conditional_unique'] and r['split']=='train']
        ds=[diagnostic(train,P,m['n']) for P in range(1,400) if P%13 and m['n']%P==0]
        chosen=sorted(ds,key=lambda d:(d['minimum_conflicting_assignments'],d['P']))[:3]
        for rank,d in enumerate(chosen):
            outcomes=[]
            for r in rows:
                if r['split']!='test':continue
                pred=d['template'][r['k']%d['P']];actual=r['color'][0].upper()
                status='correct' if pred==actual else 'wrong' if pred in 'RYB' else 'abstain'
                outcomes.append(dict(observation_id=r['observation_id'],k=r['k'],conditional_unique=r['conditional_unique'],prediction=pred,actual=actual,status=status))
            evaluations.append(dict(model_id=mid,rank=rank,P=d['P'],train_conflicts=d['minimum_conflicting_assignments'],determined=sum(d['template'].count(c) for c in 'RYB'),unknown=d['unknown'],conflicted=d['conflict_residues'],correct=sum(x['status']=='correct' for x in outcomes),wrong=sum(x['status']=='wrong' for x in outcomes),abstain=sum(x['status']=='abstain' for x in outcomes),outcomes=outcomes,status='inconsistent diagnostic, not recovered template'))
    save(out/'heldout-diagnostics.json',evaluations)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=OUT);args=ap.parse_args();fixed(args.output)
