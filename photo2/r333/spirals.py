"""Discover orientation, then conservative measured palette paths and repetitions.

Greedy smooth DAG path cover is a descriptive tracer, not proof of unique design
strands. No geometric or color prediction creates an accepted link.
"""
import argparse,time
from collections import Counter,defaultdict
from pathlib import Path
from .common import *
from .explore import paths,D

def translation_scan(ab,c,blocks,limit=24):
    occupied={tuple(v):i for i,v in enumerate(ab)};rows=[]
    for a in range(-limit,limit+1):
        for b in range(-limit,limit+1):
            if a+b<=0:continue
            pairs=[(i,occupied[tuple(v+[a,b])]) for i,v in enumerate(ab) if tuple(v+[a,b]) in occupied]
            if len(pairs)<40:continue
            ii,jj=np.array(pairs).T;agreement=float(np.mean(c[ii]==c[jj]));distant=abs(blocks[ii]-blocks[jj]);distant=np.minimum(distant,12-distant)
            far=distant>=2
            rows.append(dict(delta_ab=[a,b],pairs=len(pairs),agree=int((c[ii]==c[jj]).sum()),agreement=agreement,distant_pairs=int(far.sum()),distant_agreement=float(np.mean(c[ii[far]]==c[jj[far]])) if far.any() else None))
    return sorted(rows,key=lambda r:-r['agreement'])

def run(out,controls=39):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);t=time.perf_counter();g,obs,co,ids,ab,c,w,b,station=dataset();lookup={o:i for i,o in enumerate(ids)};rows=[];selected=[]
    # Three undirected cones, opposite direction retained as a stability check.
    for palette in [('black','red'),('black','yellow')]:
        for cone in range(6):
            pp=paths(g,palette,cone);rows.append(dict(palette=list(palette),cone=cone,segments=len(pp),measured_nodes=sum(x['length'] for x in pp),maximum=max([x['length'] for x in pp] or [0]),lengths=[x['length'] for x in pp]))
        for j,p in enumerate(paths(g,palette,0)):
            steps=np.array(p['word']);counts=Counter(tuple(x) for x in p['word']);p.update(id=('BR' if palette[1]=='red' else 'BY')+f'-{j+1:03}',palette=list(palette),cone=0,measured_links=p['length']-1,inferred_links=0,step_counts={str(k):v for k,v in counts.items()},turns=int(np.count_nonzero(np.any(np.diff(steps,axis=0),axis=1))),alternating_color_edges=sum(obs[a]['color']!=obs[z]['color'] for a,z in zip(p['ids'],p['ids'][1:])),start_ab=co[p['ids'][0]],end_ab=co[p['ids'][-1]])
            selected.append(p)
    # Compare orientation selection against local-order-preserving controls.
    # Rotate each phase lane within geographic sections; never shuffle individual
    # labels globally. These controls retain local ordering except one circular cut.
    rng=np.random.default_rng(333);null=[]
    for trial in range(controls):
        cp=c.copy()
        for block in range(12):
            for phase in range(13):
                jj=np.flatnonzero((b==block)&((ab@[7,6])%13==phase));jj=jj[np.argsort(station[jj])]
                if len(jj):cp[jj]=np.roll(cp[jj],int(rng.integers(len(jj))))
        colors={o:COLORS[cp[i]] for i,o in enumerate(ids)};best={}
        for palette in [('black','red'),('black','yellow')]:
            choices=[]
            for cone in range(3):
                ps=paths(g,palette,cone,colors);choices.append(dict(cone=cone,measured_nodes=sum(p['length'] for p in ps),maximum=max([p['length'] for p in ps] or [0])))
            best[palette[1]]=max(choices,key=lambda r:r['measured_nodes'])
        null.append(dict(trial=trial,best=best))
    translations=translation_scan(ab,c,b);spatial=[]
    for delta in [(8,8),(16,16),(24,24),(16,15),(17,15),(24,23)]:
        keys,rep=spatial_keys(ab,delta)
        for guard in [0,1]:
            pr,ba=cross_predict(keys,c,w,b,guard);spatial.append(dict(delta_ab=delta,guard=guard,cells=int(max(keys)+1),**score(pr,ba,c,w,b)))
    # Connected palette graph is a rejected strand identifier: black junctions
    # permit many alternative paths. Record components and branch counts exactly.
    components=[]
    for palette in [('black','red'),('black','yellow')]:
        adj=defaultdict(set)
        for e in g['edges']:
            a,z=e['source'],e['target']
            if obs[a]['color'] in palette and obs[z]['color'] in palette:adj[a].add(z);adj[z].add(a)
        unseen={o for o in ids if obs[o]['color'] in palette};sizes=[]
        while unseen:
            todo=[next(iter(unseen))];cc=set()
            while todo:
                o=todo.pop()
                if o in cc:continue
                cc.add(o);todo+=list(adj[o]-cc)
            unseen-=cc;sizes.append(len(cc))
        components.append(dict(palette=palette,sizes=sorted(sizes,reverse=True),branch_nodes=sum(len(v)>2 for v in adj.values())))
    membership=defaultdict(list)
    for p in selected:
        for o in p['ids']:membership[o].append(p['id'])
    bypalette={col:set(o for p in selected if p['palette'][1]==col for o in p['ids']) for col in ['red','yellow']};overlap=bypalette['red']&bypalette['yellow']
    # Observed repeat correspondences for whole step words, including nearby
    # colored context, are retained without using them as independent labels.
    correspondences=[];occupied={tuple(v):o for o,v in co.items()}
    for p in selected:
        for mul in [-3,-2,-1,1,2,3]:
            shifted=[occupied.get(tuple(np.array(co[o])+mul*np.array([16,16]))) for o in p['ids']];pairs=[(a,z) for a,z in zip(p['ids'],shifted) if z]
            if len(pairs)>=4:
                correspondences.append(dict(segment=p['id'],translation=[16*mul,16*mul],measured_pairs=len(pairs),agree=sum(obs[a]['color']==obs[z]['color'] for a,z in pairs),pairs=pairs))
    res=dict(orientation_scan=rows,segments=selected,palette_components=components,nulls=null,spatial_models=spatial,translations=translations,repeat_correspondences=correspondences,coverage=dict(unique=len(membership),indexed=len(ids),fraction=len(membership)/len(ids),black_shared_by_both=len(overlap),by_color=dict(Counter(obs[o]['color'] for o in membership))),seconds=time.perf_counter()-t,policy='Measured paths use only working links and original colors; no gap is bridged. Path cover/strand boundaries are nonunique, reverse sensitivity and nulls retained. Spatial repetition is not a maker-compatible stringing sequence.')
    save(out/'spirals.json.gz',res);save(out/'summary.json',{k:v for k,v in res.items() if k not in ['segments','nulls','translations','repeat_correspondences']});print('SPIRALS',res['coverage'], 'seconds',res['seconds'],flush=True)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--controls',type=int,default=39);a=ap.parse_args();run(a.output,a.controls)
