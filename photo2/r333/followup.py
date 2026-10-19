"""Bounded post-discovery checks: strand width, predictive controls and patch shifts."""
import argparse,time
from pathlib import Path
from .common import *
from photo2.r330.pattern import viterbi
from photo2.r331.analyze import evaluate

def run(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);t=time.perf_counter();g,obs,co,ids,ab,c,w,b,station=dataset();ix={o:i for i,o in enumerate(ids)};sp=read(artifact('spirals/spirals.json.gz'));st=read(artifact('staircases/staircases.json.gz'));di=read(artifact('diagnosis/diagnosis.json.gz'));occ={tuple(v):o for o,v in co.items()};lookup={o:i for i,o in enumerate(ids)};edgepairs={frozenset((e['source'],e['target'])) for e in g['edges']}
    # Within each station slice, maximal palette bands at d steps of2. These are
    # observed strip widths, censored at inventory edges; not physical bead widths.
    widths=[]
    for palette in [('black','red'),('black','yellow')]:
        for s in sorted(set(ab.sum(1))):
            rows=sorted([(a-bb,o) for o,(a,bb) in co.items() if a+bb==s]);run=[]
            for d,o in rows+[(10000,None)]:
                if run and (o is None or d!=run[-1][0]+2 or obs[o]['color'] not in palette):
                    if len(run)>=2 and len({obs[q]['color'] for _,q in run})==2:widths.append(dict(palette=palette,s=s,width_observed=len(run),ids=[q for _,q in run],d_range=[run[0][0],run[-1][0]],censored=True))
                    run=[]
                if o and obs[o]['color'] in palette:run.append((d,o))
    # Relative spacing of mixed-palette components along s; don't conflate nearby
    # path-cover traces with disjoint physical strands.
    starts={p:sorted(sum(co[x['ids'][0]]) for x in st['traces'] if x['palette'][1]==p) for p in ['red','yellow']}
    endpoints=[]
    for p in st['traces']:
        for side,sign in [('start',-1),('end',1)]:
            o=p['ids'][0 if sign<0 else -1];options=[]
            for step in [(sign,0),(0,sign)]:
                v=tuple(np.array(co[o])+step);z=occ.get(v);options.append(dict(ab=v,delta_ab=step,id=z,color=obs[z]['color'] if z else '?',working_link=bool(z and frozenset((o,z)) in edgepairs),classification='same-palette branch' if z and obs[z]['color'] in p['palette'] else 'other recorded palette; may be a genuine boundary' if z else 'unknown continuation'))
            endpoints.append(dict(trace=p['id'],endpoint=side,id=o,options=options))
    baselines=[]
    for fam,wt in [('A',[7,6]),('B',[6,7])]:
        k=ab@wt
        for p in [1,2,13,26,52,104,208]:baselines.append(dict(evaluate(k,c,w,b,p),family=fam))
    lowpen=[]
    for fam,p in [('A',208),('A',306),('B',207),('B',305)]:
        k=ab@([7,6] if fam=='A' else [6,7]);tr=~np.isin(b,[2,5,8,11]);th,ba,_=fit_keys(k%p,c,w,tr)
        if len(th)<p:th=np.concatenate([th,np.tile(ba,(p-len(th),1))])
        for pen in [1.,3.]:
            shift,receipt=viterbi(k,c,w,station,th,tr,pen);log=np.log(th[(k+shift)%p,c]/th[k%p,c]);shiftby=dict(zip(ids,shift));bad=[dict(source=e['source'],target=e['target']) for e in g['edges'] if shiftby[e['source']]!=shiftby[e['target']]];lowpen.append(dict(family=fam,period=p,**receipt,training_gain=float(np.average(log[tr],weights=w[tr])),withheld_gain=float(np.average(log[~tr],weights=w[~tr])),shifted_observations=int(np.count_nonzero(shift)),boundary_equations_violated=len(bad),violations=bad,admissible=not bool(bad),offsets=[dict(id=o,shift=int(shift[i])) for i,o in enumerate(ids) if shift[i]]))
    # Full-data motif partition equivalence is a precise alias diagnosis.
    A=ab@[7,6];B=ab@[6,7];same=0;pairs=0
    for i in range(len(ids)):
        for j in range(i):same+=((A[i]-A[j])%306==0)==((B[i]-B[j])%305==0);pairs+=1
    # Compare repetitions with target sections withheld. Conservative rule covers
    # only observed matching copies in >=3 other sections; print exact accuracy.
    qualified=[r for r in di['all_predictions'] if r['strong']];repeat=dict(qualified=len(qualified),agree=sum(r['prediction']==r['original'] for r in qualified),disagree=sum(r['prediction']!=r['original'] for r in qualified),coverage=len(qualified)/len(ids),guard=1,all_targets=len(ids))
    # Novel R332 associations are an exposed-data incremental check of the prior
    # R331 motif: freeze historical motif, NEVER train on the new 141 observations.
    oldco={r['id']:tuple(r['ab']) for r in read(ROOT/'photo2/r328/results/graph.json.gz')['coordinates']} if 'coordinates' in read(ROOT/'photo2/r328/results/graph.json.gz') else None
    from photo2.r330.pattern import dataset as old_dataset
    from photo2.r329.common import canonical
    _,states,*_=old_dataset();oldco=canonical(states['working']);new=[i for i,o in enumerate(ids) if o not in oldco];oldmask=np.array([o in oldco for o in ids]);prior=[]
    for p in [104,208]:
        th,ba,cc=fit_keys(A%p,c,w,oldmask);traces=[]
        for i in new:
            rows=np.flatnonzero(oldmask&(A%p==A[i]%p));win=int(cc[A[i]%p].argmax());support=rows[c[rows]==win];known=len(support)>=3 and len(set(b[support].tolist()))>=3 and cc[A[i]%p,win]/max(cc[A[i]%p].sum(),1e-9)>=.8
            traces.append(dict(id=ids[i],original=COLORS[c[i]],prediction=COLORS[win] if known else '?',strong=known,agree=bool(c[i]==win)))
        prior.append(dict(period=p,new_observations=len(new),confident=sum(r['strong'] for r in traces),agree=sum(r['strong'] and r['agree'] for r in traces),disagree=sum(r['strong'] and not r['agree'] for r in traces),rows=traces,scope='R332 completion omitted motif inputs, but chosen analysis after seeing data; not a new blind test.'))
    result=dict(observed_widths=widths,trace_starts=starts,regular_endpoints=endpoints,baselines=baselines,low_penalty_shifts=lowpen,partition_A306_B305=dict(equivalent_pair_decisions=same,total_pairs=pairs,exact=same==pairs),guarded_spatial_prediction=repeat,prior_motif_new_R332=prior,seconds=time.perf_counter()-t)
    save(out/'followup.json.gz',result);save(out/'summary.json',{k:v for k,v in result.items() if k not in ['observed_widths','regular_endpoints','trace_starts','prior_motif_new_R332','low_penalty_shifts']});print('FOLLOWUP',repeat,'lowpen',[(r['family'],r['period'],r['shifted_observations'],r['boundary_equations_violated']) for r in lowpen],flush=True)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);a=ap.parse_args();run(a.output)
