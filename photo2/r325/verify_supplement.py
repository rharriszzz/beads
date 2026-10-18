"""Independent checks of post-freeze contexts, closure hypotheses and model mask."""
import json,gzip,time,hashlib
from pathlib import Path
from collections import Counter,defaultdict
import numpy as np
from photo2.r325.verify import read,sha,ROOT,OUT

def main():
    start=time.perf_counter();g=read(OUT/'graph.json');op={o['id']:o for o in g['observations']};nodes={n['id']:n for n in g['intersections']};c=read(OUT/'context-check.json');assignments=0;hypotheses=0
    for row in c['windows']:
        name=row['region'];wi=int(name.split('-')[-1]) if name.startswith('old-break-') else (72 if name=='winding-gap' else 11);R=np.array(g['windows'][wi]['frame']);cen=np.array(row['center'])
        for h in row['hypotheses']:
            cells={tuple(v['ab']) for v in h['assignments'].values()};assert len(cells)==len(h['assignments']);score=0;tri=0
            for oid,v in h['assignments'].items():
                pred=np.array(h['basis'])@v['ab']+h['offset'];assert np.max(abs(pred-v['predicted_xy']))<1e-9;err=np.linalg.norm(R@pred+cen-op[oid]['xy']);assert abs(err-v['residual_px'])<1e-9;sig=8 if op[oid]['color']=='black' else 5;assert err<2*sig+1e-9;weight=1 if op[oid]['band_clearance_px']>=18 else .55;score+=weight*(1-.25*(err/sig)**2);a,b=v['ab'];tri+=int((a+1,b) in cells and (a,b+1) in cells);assignments+=1
            assert tri==h['triangles'];assert abs(score+.18*tri-h['score'])<1e-8;hypotheses+=1
    for e in c['edges']:
        a,b=e['source'],e['target']
        for v in e['votes']:
            row=c['windows'][v['context']];best=max(h['score'] for h in row['hypotheses']);eligible=[(i,h) for i,h in enumerate(row['hypotheses']) if h['score']>=best-1.];assert [i for i,h in eligible]==v['selected_hypotheses'];deltas=sorted({tuple(np.array(h['assignments'][b]['ab'])-h['assignments'][a]['ab']) for i,h in eligible if a in h['assignments'] and b in h['assignments']});assert [list(d) for d in deltas]==v['deltas']
        assert e['excludes_global']==sum(e['global_delta'] not in v['deltas'] for v in e['votes']);assert e['only_global']==sum(v['deltas']==[e['global_delta']] for v in e['votes'])
    interface=read(OUT/'model-input.json');screen=read(OUT/'context-screening.json');contested={frozenset((e['source'],e['target'])) for e in c['edges'] if e['status']=='context-contested'};ii={o['id']:o for o in interface['observations']}
    assert len(interface['accepted_neighbors'])==screen['context_screened_edges']==1652
    for e in interface['accepted_neighbors']:
        assert frozenset((e['source'],e['target'])) not in contested;a,b=ii[e['source']],ii[e['target']];assert a['component']==b['component'];assert np.array_equal(np.array(b['relative_ab'])-a['relative_ab'],e['delta_ab'])
    assert len({o['component'] for o in ii.values() if o['component'] is not None})==screen['context_screened_components']==23
    # Reconstruct the winding coefficient from accepted graph edges independently.
    adj=defaultdict(list)
    for e in g['graph']['edges']:adj[e['source']].append((e['target'],e['circuit_wrap']));adj[e['target']].append((e['source'],-e['circuit_wrap']))
    root=next(iter(adj));wind={root:0};todo=[root]
    while todo:
        a=todo.pop()
        for b,w in adj[a]:
            if b not in wind:wind[b]=wind[a]+w;todo.append(b)
    closure=read(OUT/'closure-candidates.json')
    for p in closure['proposals']:
        a,b=p['source'],p['target'];w=round((g['stations_px'][a]-g['stations_px'][b])/g['period_px']);k=wind[a]+w-wind[b];assert k
        residual=np.array(p['delta_ab'])-(np.array(nodes[b]['relative_ab'])-nodes[a]['relative_ab']);assert np.array_equal(residual,k*np.array(p['holonomy_ab']))
        for m in p['count_interpretations']:
            weights=[7,6] if m['interpretation']=='A' else [6,7];assert m['N']==abs(np.array(p['holonomy_ab'])@weights)
            groups=defaultdict(list)
            for n in nodes.values():
                if n['component'] is not None:groups[n['conditional_indices'][m['interpretation']]%m['N']].append(n['id'])
            actual=sorted(sorted(v) for v in groups.values() if len(v)>1);assert actual==sorted(sorted(r['observations']) for r in m['modular_collisions'])
    model=read(OUT/'model-comparison.json');model_edges=0
    for m in model['models']:
        path=ROOT/'photo2/r324/results'/f"{m['model']}-frozen.json.gz";assert sha(path)==m['frozen_source_sha256'];old=json.load(gzip.open(path,'rt'));support={o['id']:o for o in old['support']};N=m['N'];startindex=old['positions']['indices'][0];best=m['best'];weights=best['weights'];fractions=[]
        for n in g['intersections']:
            if n['component'] is None:continue
            idx=(best['origin']+np.array(n['relative_ab'])@weights-startindex)%N+startindex;fractions.append(sum(x['fraction'] for x in support[n['id']]['owners'] if x['index']==idx))
        assert abs(np.mean(fractions)-best['mean_assigned_support'])<1e-12
        lookup={(e['source'],e['target']):e for e in g['graph']['edges']}
        for e in m['edge_rows']:
            a,b=support[e['source']],support[e['target']];assert e['expected_difference']==np.array(lookup[e['source'],e['target']]['delta_ab'])@weights
            if a['modal_index'] is not None and b['modal_index'] is not None:assert e['modal_owner_difference']==(b['modal_index']-a['modal_index']+N//2)%N-N//2
            model_edges+=1
    black=read(OUT/'colored-first.json');faint=[r for r in black['predictions'] if 'raw_support_pixels' in r];unique={tuple(map(tuple,r['raw_support_pixels'])) for r in faint}
    result=dict(passed=True,context_windows=len(c['windows']),context_hypotheses=hypotheses,context_assignments=assignments,context_edge_comparisons=len(c['edges']),screened_links=len(interface['accepted_neighbors']),screened_components=23,closure_proposals=len(closure['proposals']),frozen_model_edges=model_edges,faint_detection_records=len(faint),unique_faint_sites=len(unique),unique_faint_pixels=sum(map(len,unique)),seconds=time.perf_counter()-start,limitation='Independent numerical arithmetic, not additional independent photographic identity labels.')
    (OUT/'supplement-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
if __name__=='__main__':main()
