"""Conservative model-use mask for independent-context disagreements.
This does not refit or relabel the frozen global photographic solution.
"""
import json
from pathlib import Path
from collections import defaultdict,Counter
from photo2.r323.tracker import save
OUT=Path(__file__).parent/'results'
def main():
    g=json.load(open(OUT/'graph.json'));c=json.load(open(OUT/'context-check.json'));contract=json.load(open(OUT/'model-input.json'));contested={frozenset((e['source'],e['target'])) for e in c['edges'] if e['status']=='context-contested'}
    if 'model_use_policy' in contract:raise RuntimeError('Already screened: regenerate the unscreened interface with analyze before applying screening once.')
    kept=[];deferred=[];adj=defaultdict(set)
    for e in g['graph']['edges']:
        if frozenset((e['source'],e['target'])) in contested:deferred.append(dict(**e,model_use='unresolved: competing independent-size photo context'))
        else:kept.append(e);adj[e['source']].add(e['target']);adj[e['target']].add(e['source'])
    comp={};groups=[]
    for start in sorted(adj):
        if start in comp:continue
        ci=len(groups);comp[start]=ci;todo=[start];members=[]
        while todo:
            a=todo.pop();members.append(a)
            for b in adj[a]:
                if b not in comp:comp[b]=ci;todo.append(b)
        groups.append(dict(id=ci,origin=start,nodes=sorted(members)))
    primary={o['id']:o for o in contract['observations']};origins={c['id']:primary[c['origin']]['relative_ab'] for c in groups}
    for o in contract['observations']:
        o['global_candidate_component']=o['component'];o['global_candidate_ab']=o['relative_ab'];o['global_candidate_indices']=o['conditional_indices'];o['component']=comp.get(o['id'])
        if o['component'] is None:o['relative_ab']=None;o['conditional_indices']=None;o['confidence']='unresolved for fixed model use'
        else:
            origin=origins[o['component']];a,b=[x-y for x,y in zip(o['global_candidate_ab'],origin)];o['relative_ab']=[a,b];o['conditional_indices']=dict(A=7*a+6*b,B=6*a+7*b,reverse_A=-7*a-6*b,reverse_B=-6*a-7*b);o['confidence']='context-screened component-relative hypothesis; not independently certified'
    contract['conditional_global_neighbors']=contract['accepted_neighbors'];contract['accepted_neighbors']=kept;contract['unresolved_neighbors']+=deferred;contract['origins']=[dict(component=c['id'],observation=c['origin']) for c in groups];contract['model_use_policy']='Default fixed relative constraints exclude context-contested links and rebase each remaining component independently. Global candidate indices are diagnostic alternatives only. Untested and context-ambiguous links still require review; screened does not mean verified.'
    contract['unresolved_observations']=[o['id'] for o in contract['observations'] if o['component'] is None];save(OUT/'model-input.json',contract)
    result=dict(global_candidate_components=len(g['graph']['components']),global_candidate_edges=len(g['graph']['edges']),context_contested_accepted_edges=len(deferred),context_screened_edges=len(kept),context_screened_components=len(groups),context_screened_indexed=len(comp),context_screened_unresolved=len(primary)-len(comp),groups=groups,
        warning='This is a conservative downstream-use sensitivity, not independent ground truth and not a replacement globally optimized result. One conditional component must not be advertised as one certified physical lattice.')
    save(OUT/'context-screening.json',result);print({k:v for k,v in result.items() if k!='groups'})
if __name__=='__main__':main()
