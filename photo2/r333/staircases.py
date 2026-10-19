"""Discover regular staircase run lengths without imposing alternating colors.

Vectorized exhaustive 3 orientations x 36 run pairs x cyclic phases. Every edge
must be an actual working link. Irregular greedy paths remain a separate layer.
"""
import argparse,time
from pathlib import Path
from itertools import groupby
from .common import *
from .explore import D

def run(out,trials=19):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);t=time.perf_counter();g,obs,co,ids,ab,c,w,b,station=dataset();ix={o:i for i,o in enumerate(ids)};n=len(ids);occ={tuple(v):i for i,v in enumerate(ab)};nexts=np.full((6,n+1),n,int)
    for e in g['edges']:
        u,v=ix[e['source']],ix[e['target']];step=tuple(e['delta_ab']);j=list(map(tuple,D)).index(step);nexts[j,u]=v;nexts[(j+3)%6,v]=u
    # Cut seam consistently so finite measured paths do not make repeated laps.
    for j in range(6):
        for i in range(n):
            z=nexts[j,i]
            if z<n and not np.array_equal(ab[z]-ab[i],D[j]):nexts[j,i]=n
    templates=[]
    for cone in range(3):
        for r0 in range(1,7):
            for r1 in range(1,7):
                word=[cone]*r0+[(cone+1)%6]*r1;templates.append((cone,r0,r1,np.array(word)))
    def scan(colors,export=False):
        rows=[];details={}
        for palette in [(2,0),(2,1)]:
            allowed=np.r_[np.isin(colors,palette),False]
            for ti,(cone,r0,r1,word) in enumerate(templates):
                # All cyclic step phases considered; max32 measured steps.
                starts=np.repeat(np.arange(n),len(word));phase=np.tile(np.arange(len(word)),n);where=starts.copy();length=allowed[where].astype(int);active=allowed[where].copy();hasblack=colors[starts]==2;hascolor=colors[starts]==palette[1]
                for step in range(32):
                    dest=nexts[word[(phase+step)%len(word)],where];active &= allowed[dest];where=np.where(active,dest,n);length+=active
                    col=np.r_[colors,-1][where];hasblack|=active&(col==2);hascolor|=active&(col==palette[1])
                length=np.where(hasblack&hascolor,length,0);best=length.reshape(n,-1).max(1)
                val=float(np.maximum(best-5,0).sum()/n);row=dict(palette='BR' if palette[1]==0 else 'BY',cone=cone,runs=[r0,r1],score=val,maximum=int(best.max()),starts_at_least8=int((best>=8).sum()),starts_at_least12=int((best>=12).sum()))
                rows.append(row)
                if export:details[palette[1],ti]=(length.reshape(n,-1),word)
        return sorted(rows,key=lambda r:-r['score']),details
    ranking,details=scan(c,True);traces=[];model=[];used_by_palette={0:set(),1:set()}
    for palette in [0,1]:
        best=next(r for r in ranking if r['palette']==('BR' if palette==0 else 'BY'));ti=next(j for j,v in enumerate(templates) if list(v[:3])==[best['cone'],*best['runs']]);length,word=details[palette,ti];bestphase=length.argmax(1);options=sorted(range(n),key=lambda i:-length[i,bestphase[i]])
        for start in options:
            size=int(length[start,bestphase[start]])
            if size<8:break
            chain=[start];at=start;phase=int(bestphase[start])
            for step in range(size-1):at=int(nexts[word[(phase+step)%len(word)],at]);chain.append(at)
            if len(set(chain)&used_by_palette[palette])>size//3:continue
            used_by_palette[palette]|=set(chain);traces.append(dict(id=('SBR' if palette==0 else 'SBY')+f'-{len(traces)+1:03}',palette=['black',COLORS[palette]],ids=[ids[i] for i in chain],length=size,measured_links=size-1,inferred_links=0,runs=best['runs'],step_phase=phase,cone=best['cone'],word=[D[word[(phase+j)%len(word)]].tolist() for j in range(size-1)]))
        model.append(best)
    # Full template/orientation selection is repeated in each local correlation
    # null. Report the null honestly even if it explains simple palette paths.
    rng=np.random.default_rng(33302);null=[]
    for trial in range(trials):
        cp=c.copy()
        for block in range(12):
            for phase in range(13):
                jj=np.flatnonzero((b==block)&((ab@[7,6])%13==phase));jj=jj[np.argsort(station[jj])]
                if len(jj):cp[jj]=np.roll(cp[jj],int(rng.integers(len(jj))))
        rr,_=scan(cp);null.append(dict(trial=trial,best_BR=next(r for r in rr if r['palette']=='BR'),best_BY=next(r for r in rr if r['palette']=='BY')))
    # Repetition support from actual corresponding nodes AND actual edges.
    correspondence=[];reliable=set();reliable_ids=set()
    edgepairs={frozenset((e['source'],e['target'])) for e in g['edges']}
    for trace in traces:
        examples=[]
        for mul in range(-12,13):
            if not mul:continue
            pairs=[]
            for o in trace['ids']:
                z=occ.get(tuple(np.array(co[o])+mul*np.array([16,16])))
                if z is not None and min(abs(int(b[ix[o]])-int(b[z])),12-abs(int(b[ix[o]])-int(b[z])))>=2:pairs.append((o,ids[z]))
            if len(pairs)<6:continue
            agree=sum(obs[o]['color']==obs[z]['color'] for o,z in pairs);knownedges=sum(frozenset((pairs[j][1],pairs[j+1][1])) in edgepairs for j in range(len(pairs)-1) if frozenset((pairs[j][0],pairs[j+1][0])) in edgepairs)
            examples.append(dict(translation=[mul*16,mul*16],pairs=pairs,measured_pairs=len(pairs),agree=agree,measured_example_links=knownedges))
        supported=[e for e in examples if e['agree']/e['measured_pairs']>=.85 and e['measured_example_links']>=4]
        trace['repeated_examples']=examples;trace['repeat_supported']=len(supported)>=2
        if trace['repeat_supported']:reliable.add(trace['id']);reliable_ids|=set(trace['ids'])
    # Spatial autocorrelation nulls scan all original tested translations. This
    # protects against selecting (16,16) after seeing the photograph's labels.
    spatial=read(artifact('spirals/spirals.json.gz'));pairbanks=[]
    for row in spatial['translations']:
        d=row['delta_ab'];pairs=[(i,occ[tuple(v+d)]) for i,v in enumerate(ab) if tuple(v+d) in occ];pairbanks.append((row['delta_ab'],np.array(pairs)))
    transnull=[];rng=np.random.default_rng(33303)
    for trial in range(39):
        cp=c.copy()
        for block in range(12):
            jj=np.flatnonzero(b==block);jj=jj[np.argsort(station[jj])];cp[jj]=np.roll(cp[jj],int(rng.integers(len(jj))))
        vals=[(float(np.mean(cp[p[:,0]]==cp[p[:,1]])),d) for d,p in pairbanks];val,d=max(vals);transnull.append(dict(trial=trial,best_agreement=val,delta_ab=d))
    lengths=Counter()
    for p in spatial['segments']:
        for _,gg in groupby(map(tuple,p['word'])):lengths[len(list(gg))]+=1
    result=dict(template_ranking=ranking,selected_models=model,traces=traces,nulls=null,translation_nulls=transnull,greedy_runlength_histogram=dict(lengths),coverage=dict(repeated_supported_segments=len(reliable),repeated_supported_observations=len(reliable_ids),indexed=n,fraction=len(reliable_ids)/n,all_regular_traces=len(traces),all_regular_observations=len(set(o for p in traces for o in p['ids']))),seconds=time.perf_counter()-t,policy='Regular staircase family learned exhaustively. Measured paths are descriptive; only repeat-supported subset has >=2 distant color/edge counterparts. No inferred links or colors accepted.')
    save(out/'staircases.json.gz',result);save(out/'summary.json',{k:v for k,v in result.items() if k not in ['template_ranking','traces','nulls','translation_nulls']});print('STAIRCASES',model,result['coverage'],'seconds',result['seconds'],flush=True)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--trials',type=int,default=19);a=ap.parse_args();run(a.output,a.trials)
