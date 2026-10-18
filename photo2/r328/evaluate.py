"""Post-freeze retrospective labels and consequences of retained alternatives."""
import argparse,collections
from pathlib import Path
import numpy as np
from .grow import ROOT,BANK,read,save,sha
from .export import key

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',default='photo2/r328/results');args=ap.parse_args();out=Path(args.output);g=read(out/'graph.json.gz');seal=read(out/'scientific-seal.json');assert sha(out/'graph.json.gz')==seal['graph_sha256'];bank=read(BANK);prep=read(Path(seal['run'])/'prepared.json.gz');search=read(Path(seal['run'])/'search.json.gz');patches=prep['patches'];primary=search['states'][0]
    def metrics(state):
        rows=collections.defaultdict(list);seen=set();edges=set()
        for r in state['path']:
            if r.get('skipped'):continue
            wi,hi=r['window'],r['hypothesis'];p=patches[wi][r['patch']]
            edges.update(key(a,b,d) for a,b,d in p['edges'])
            if (wi,hi) in seen:continue
            seen.add((wi,hi));h=bank['windows'][wi]['hypotheses'][hi]
            for a in h['r327_evidence']['rows']:
                if a['observation'] in p['assignments']:rows[a['observation']].append([float(np.mean(a['errors_px'])),a['pixel_support'],a['utility']])
        return {o:np.mean(a,axis=0).tolist() for o,a in rows.items()},edges
    pm,pe=metrics(primary);alternatives=[]
    for i,a in enumerate(search['states'][1:]):
        am,ae=metrics(a);common=sorted(pm.keys()&am.keys());changed=[dict(observation=o,primary_error_response_utility=pm[o],alternative_error_response_utility=am[o]) for o in common if np.max(abs(np.array(pm[o])-am[o]))>1e-8];changed.sort(key=lambda r:-abs(r['alternative_error_response_utility'][0]-r['primary_error_response_utility'][0]))
        alternatives.append(dict(alternative=i,H=a['H'],score=a['score'],score_gap=primary['score']-a['score'],return_matches=len(a['returns']),changed_windows=[dict(step=j,window=r['window'],primary_hypothesis=r.get('hypothesis'),alternative_hypothesis=t.get('hypothesis')) for j,(r,t) in enumerate(zip(primary['path'],a['path'])) if r.get('hypothesis')!=t.get('hypothesis')],changed_support_predictions=changed,common_supports=len(common),common_mean_error_primary=float(np.mean([pm[o][0] for o in common])),common_mean_error_alternative=float(np.mean([am[o][0] for o in common])),added_links=[list(e) for e in sorted(ae-pe)],withdrawn_links=[list(e) for e in sorted(pe-ae)]))
    save(out/'alternative-consequences.json.gz',dict(alternatives=alternatives,policy='Selected patch predictions, with original native response and identical common-support cohorts. Score gaps are heuristic preferences, not probabilities or independent accuracy.'))
    # Historical R161 is already exposed. It is read only in this post-seal module.
    from photo2.r322.evaluate import association
    labels=read(ROOT/'photo2/manual-labels-r161.json');maker=sorted(labels['annotations'],key=lambda x:x['number']);num={a['id']:a['number'] for a in maker};steps={'d2':[1,0],'d3':[0,1],'d1':[1,-1]};priority={a['maker']:a['priority'] for a in read(ROOT/'photo2/r325/results/validation.json')['associations']}
    proxy=[dict(id=o['id'],observation=o['id'],status='probable bead') for o in g['observations'] if not o.get('provisional')];mapping,matches=association(proxy,g['observations'],maker,18,3);inv={o:m for m,o in mapping.items()};coords={1:np.zeros(2,int)};adj=collections.defaultdict(list);recorded=[]
    for s in labels['series']:
        if s['status']!='complete':continue
        for aa,bb in zip(s['bead_ids'],s['bead_ids'][1:]):
            a,b=num[aa],num[bb];d=np.array(steps[s['direction']]);recorded.append((a,b,d,s['direction']));adj[a].append((b,d));adj[b].append((a,-d))
    todo=[1]
    while todo:
        a=todo.pop()
        for b,d in adj[a]:
            if b not in coords:coords[b]=coords[a]+d;todo.append(b)
            else:assert np.array_equal(coords[b],coords[a]+d)
    indexed={n['id'] for n in g['intersections'] if n['component'] is not None};records=[]
    for a,b,d,direction in recorded:
        aa,bb=mapping.get(a),mapping.get(b);recovered=bool(aa and bb and key(aa,bb,d.tolist()) in pe);records.append(dict(maker_source=a,maker_target=b,source=aa,target=bb,direction=direction,delta_ab=d.tolist(),priority='interior' if priority[a]==priority[b]=='interior' else 'edge',recovered=recovered,missing_endpoint=not(aa and bb)))
    wrong=[]
    for e in g['graph']['edges']:
        a,b=inv.get(e['source']),inv.get(e['target'])
        if a is not None and b is not None and not np.array_equal(coords[b]-coords[a],e['delta_ab']):wrong.append(dict(e,maker_source=a,maker_target=b,priority='interior' if priority[a]==priority[b]=='interior' else 'edge'))
    summary=dict(indexed_associations=sum(o in indexed for o in mapping.values()),interior_indexed_associations=sum(priority[m]=='interior' and o in indexed for m,o in mapping.items()),recorded_links=len(records),recovered=sum(r['recovered'] for r in records),interior_recovered=sum(r['recovered'] and r['priority']=='interior' for r in records),missing_endpoint_links=sum(r['missing_endpoint'] for r in records),wrong_automatic_edges=len(wrong),wrong_interior_edges=sum(r['priority']=='interior' for r in wrong))
    save(out/'reference.json',dict(summary=summary,links=records,wrong_edges=wrong,associations=matches,policy='Post-seal historical R161 check; prior development exposed this reference. Radius18/margin3 association unchanged.'))
    save(out/'established-subset.json',dict(links=[r for r in records if r['recovered'] and r['priority']=='interior'],peripheral_links=[r for r in records if r['recovered'] and r['priority']!='interior'],summary=summary,new_independently_established_links=0,policy='Historical independent observations, conditional fixed endpoint association; working links remain separate.'))
    print(summary,flush=True)
if __name__=='__main__':main()
