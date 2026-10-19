"""One fixed recurrence/motif/staircase replay, with cohort effects separated."""
import argparse,time
from collections import Counter
import numpy as np
from .common import *

def fixed_traces(graph,obs,co,ids):
    ix={o:i for i,o in enumerate(ids)};step={}
    for e in graph['edges']:
        a,z=e['source'],e['target']
        if a not in ix or z not in ix:continue
        d=tuple(e['delta_ab'])
        if not np.array_equal(np.array(co[z])-co[a],d):continue # cut seam, no laps
        step[a,d]=z;step[z,tuple(-np.array(d))]=a
    output=[];summary=[]
    for pigment,runs in [('red',3),('yellow',2)]:
        word=[(1,0)]*runs+[(0,1)]*runs;options=[]
        for o in ids:
            for phase in range(len(word)):
                if obs[o]['color'] not in ['black',pigment]:continue
                chain=[o]
                for j in range(32):
                    z=step.get((chain[-1],word[(phase+j)%len(word)]))
                    if z is None or obs[z]['color'] not in ['black',pigment]:break
                    chain.append(z)
                if len({obs[z]['color'] for z in chain})==2:options.append((chain,phase))
        options.sort(key=lambda r:-len(r[0]));used=set();traces=[]
        for chain,phase in options:
            if len(chain)<8:break
            if len(set(chain)&used)>len(chain)//3:continue
            used.update(chain);traces.append(dict(palette=['black',pigment],ids=chain,length=len(chain),inferred_links=0,step_phase=phase,runs=[runs,runs]))
        output.extend(traces);summary.append(dict(palette=['black',pigment],segments=len(traces),lengths=[len(t['ids']) for t in traces],coverage=len(used)))
    return dict(traces=output,palettes=summary,coverage=len({o for t in output for o in t['ids']}))

def metrics(graph,obs,co,ids,blocks,weights):
    ids=sorted(ids);occ={tuple(co[o]):o for o in ids};pairs=[];pred=[]
    for o in ids:
        z=occ.get(tuple(np.array(co[o])+[16,16]))
        if z:pairs.append(dict(source=o,target=z,same=obs[o]['color']==obs[z]['color']))
        examples=[]
        for n in range(-15,16):
            z=occ.get(tuple(np.array(co[o])+[16*n,16*n]))
            if n and z and blocks[z] not in [(blocks[o]-1)%12,blocks[o],(blocks[o]+1)%12]:examples.append(z)
        counts=Counter(obs[z]['color'] for z in examples);win,k=counts.most_common(1)[0] if counts else ('?',0);sections={blocks[z] for z in examples if obs[z]['color']==win};strong=k>=3 and len(sections)>=3 and k/max(len(examples),1)>=.8
        pred.append(dict(id=o,color=obs[o]['color'],prediction=win if strong else '?',support=k,examples=examples,disagreement=bool(strong and obs[o]['color']!=win)))
    motif=[]
    for residue in range(208):
        jj=[o for o in ids if (7*co[o][0]+6*co[o][1])%208==residue];c=Counter()
        for o in jj:c[obs[o]['color']]+=weights[o]
        win=c.most_common(1)[0][0] if c else '?';support=[o for o in jj if obs[o]['color']==win];sections={blocks[o] for o in support};fraction=c[win]/sum(c.values()) if c else 0;known=len(support)>=3 and len(sections)>=3 and fraction>=.8
        motif.append(dict(residue=residue,color=win if known else '?',fraction=fraction,observations=len(jj),supporting=len(support),sections=sorted(sections),ids=jj))
    traces=fixed_traces(graph,obs,co,ids)
    return dict(observations=len(ids),recurrence_pairs=len(pairs),recurrence_agree=sum(r['same'] for r in pairs),pairs=pairs,breaks=[r for r in pred if r['disagreement']],predictions=pred,motif208=motif,known208=sum(e['color']!='?' for e in motif),unknown208=sum(e['color']=='?' for e in motif),staircases=traces)

def run(out):
    t=time.perf_counter();out=Path(out);out.mkdir(parents=True,exist_ok=False);old=read(ROOT/'photo2/r335/results/graph.json.gz');active=read(artifact('results/graph.json.gz'));retained=read(artifact('results/retained-graph.json.gz'));co={r['id']:r['ab'] for r in old['coordinates']};oo={r['id']:r for r in old['observations']};obs={r['id']:r for r in retained['observations']};ids=set(co);current={r['id'] for r in active['coordinates']};core={o for o in current if obs[o]['r336_roles']['pattern_extraction']};ctrl=read(ROOT/'photo2/r334/controls/controls.json.gz');blocks={r['id']:r['section'] for r in ctrl['rows']+ctrl['maker_geography']};raw={r['id']:r for r in read(ROOT/'photo2/r332/results/graph.json.gz')['observations']};weights={o:.25 if 'provisional' in str(raw[o]).lower() else .55 if raw[o]['color']=='black' else 1. for o in ids}
    stages={
      'R335_all':metrics(old,oo,co,ids,blocks,weights),
      'maker_colors_same_1041':metrics(old,obs,co,ids,blocks,weights),
      'common_active_before':metrics(old,oo,co,current,blocks,weights),
      'common_active_after':metrics(active,obs,co,current,blocks,weights),
      'fixed_interior_before':metrics(old,oo,co,core,blocks,weights),
      'fixed_interior_after':metrics(active,obs,co,core,blocks,weights)}
    summary={k:{q:v for q,v in x.items() if q not in ['pairs','breaks','predictions','motif208','staircases']}|dict(breaks=len(x['breaks']),regular_segments=len(x['staircases']['traces']),regular_coverage=x['staircases']['coverage'],palette_summaries=x['staircases']['palettes']) for k,x in stages.items()}
    save(out/'diagnostics.json.gz',dict(stages=stages,fixed_core_ids=sorted(core),policy='No period scan or new staircase rule learning. BR3/3 and BY2/2, fixed (16,16) copies and original weights/geography. Differences in coverage/consensus are descriptive, not independent accuracy.',seconds=time.perf_counter()-t));save(out/'summary.json',dict(stages=summary,seconds=time.perf_counter()-t));print(summary)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);run(p.parse_args().output)
