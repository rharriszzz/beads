"""Conditional winding proposals from unresolved links, never a measured N."""
import json
from pathlib import Path
from collections import defaultdict,Counter
import numpy as np
from photo2.r323.tracker import save
OUT=Path(__file__).parent/'results'
def main():
    g=json.load(open(OUT/'graph.json'));nodes={n['id']:n for n in g['intersections']};adj=defaultdict(list)
    for e in g['graph']['edges']:
        w=e['circuit_wrap'];adj[e['source']].append((e['target'],w));adj[e['target']].append((e['source'],-w))
    winds={};
    for root in adj:
        if root in winds:continue
        winds[root]=0;todo=[root]
        while todo:
            a=todo.pop()
            for b,w in adj[a]:
                if b not in winds:winds[b]=winds[a]+w;todo.append(b)
                else:assert winds[b]==winds[a]+w
    proposals=[]
    for e in g['graph']['unresolved_edges']:
        a,b=e['source'],e['target']
        if a not in winds or b not in winds:continue
        w=round((g['stations_px'][a]-g['stations_px'][b])/g['period_px']);cycle=winds[a]+w-winds[b]
        if not cycle:continue
        for v in e['alternatives']:
            d=np.array(v['delta_ab'])*(1 if a<b else -1);H=(d-(np.array(nodes[b]['relative_ab'])-nodes[a]['relative_ab']))/cycle
            if np.max(abs(H-np.rint(H)))>1e-9:continue
            maps=[]
            for name,weights in [('A',[7,6]),('B',[6,7])]:
                N=abs(int(H@weights));groups=defaultdict(list)
                if not N:continue
                for n in nodes.values():
                    if n['component'] is not None:groups[n['conditional_indices'][name]%N].append(n)
                collisions=[]
                for ls in groups.values():
                    if len(ls)>1:collisions.append(dict(observations=[n['id'] for n in ls],colors=[n['color'] for n in ls],separation_px=float(np.linalg.norm(np.array(ls[0]['xy'])-ls[1]['xy']))))
                maps.append(dict(interpretation=name,N=N,modular_collisions=collisions,collision_free=not collisions))
            proposals.append(dict(source=a,target=b,xy=nodes[a]['xy'],delta_ab=d.tolist(),supporting_windows=sorted({z[0] for z in v['window_states']}),holonomy_ab=H.astype(int).tolist(),count_interpretations=maps,primary_delta=d.tolist()==e['delta_ab'],consensus=e['consensus'],reasons=e['reasons']))
    counts=sorted({(m['interpretation'],m['N']) for p in proposals for m in p['count_interpretations']});save(OUT/'closure-candidates.json',dict(accepted_winding_cycles=0,count_established=False,proposals=proposals,conditional_counts=[dict(interpretation=a,N=n) for a,n in counts],
        policy='Unresolved edges conditionally imply holonomy. They are not accepted, no N adopted. Distinct-support modular collisions are contradictions conditional on distinct physical identities; same-bead multiple reflections remain a possible alternative. Both reversals retained.'))
    print(dict(proposals=len(proposals),counts=counts))
if __name__=='__main__':main()
