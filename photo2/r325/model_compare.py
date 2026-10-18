"""Frozen R321 modal-owner comparison under ONE photographic component gauge.
Model evidence never flows back into the photograph inference. Saved original
R324 native ray ownership is reused and explicitly bound by SHA256.
"""
import json,gzip,time
from pathlib import Path
from collections import Counter
import numpy as np
from scipy.stats import spearmanr
from scipy.spatial import cKDTree
from photo2.r323.tracker import save,sha
OUT=Path(__file__).parent/'results'
def main():
    start=time.perf_counter();g=json.load(open(OUT/'graph.json'));nodes=[n for n in g['intersections'] if n['component'] is not None];op={o['id']:o for o in g['observations']};ab=np.array([n['relative_ab'] for n in nodes]);xy=np.array([n['xy'] for n in nodes]);nodeix={n['id']:i for i,n in enumerate(nodes)};rows=[]
    guide=json.load(open(OUT/'guide.json'))['samples'];tree=cKDTree(np.array([[p['x'],p['y']] for p in guide]));curv=np.abs(np.array([guide[tree.query(n['xy'])[1]]['curvature'] for n in nodes]))
    for name in ['R321-geometry-best','R321-photo-sized-rescue']:
        path=Path('photo2/r324/results')/(name+'-frozen.json.gz');d=json.load(gzip.open(path,'rt'));N=d['parameters']['count'];indices=np.array(d['positions']['indices']);first=int(indices[0]);support={r['id']:r for r in d['support']};frac=np.zeros((len(nodes),N))
        for i,n in enumerate(nodes):
            for row in support[n['id']]['owners']:frac[i,row['index']-first]=row['fraction']
        options=[]
        for name2,w in [('A',[7,6]),('B',[6,7]),('reverse_A',[-7,-6]),('reverse_B',[-6,-7])]:
            rel=ab@w;idx=(indices[:,None]+rel[None,:]-first)%N;scores=frac[np.arange(len(nodes))[None,:],idx].mean(1)
            for j in np.argsort(-scores,kind='stable')[:3]:options.append(dict(interpretation=name2,weights=w,origin=int(indices[j]),mean_assigned_support=float(scores[j])))
        options.sort(key=lambda r:-r['mean_assigned_support']);best=options[0];rel=ab@best['weights'];assigned=(best['origin']+rel-first)%N+first;actual=np.array([support[n['id']]['modal_index'] if support[n['id']]['modal_index'] is not None else 0 for n in nodes]);reliable=np.array([support[n['id']]['modal_fraction']>=.6 for n in nodes]);error=(actual-assigned+N//2)%N-N//2
        edge_rows=[]
        for e in g['graph']['edges']:
            i,j=nodeix[e['source']],nodeix[e['target']];expected=int(np.array(e['delta_ab'])@best['weights']);observed=int((actual[j]-actual[i]+N//2)%N-N//2)
            edge_rows.append(dict(source=e['source'],target=e['target'],expected_difference=expected,modal_owner_difference=observed,status='unresolved modal ownership' if not(reliable[i] and reliable[j]) else ('agrees' if (observed-expected)%N==0 else 'disagrees')))
        ref='C-1497-0271';ri=nodeix[ref];distance=np.abs(rel-rel[ri]);bad=[i for i in np.argsort(distance) if reliable[i] and error[i]!=error[ri]]
        # Reference-aligned alternative preserves exactly one global origin.
        refassigned=(actual[ri]+rel-rel[ri]-first)%N+first;referr=(actual-refassigned+N//2)%N-N//2
        firstbad=[dict(observation=nodes[i]['id'],xy=nodes[i]['xy'],conditional_offset=int(rel[i]-rel[ri]),expected_index=int(refassigned[i]),modal_owner=int(actual[i]),modal_fraction=support[nodes[i]['id']]['modal_fraction'],modular_disagreement=int(referr[i])) for i in bad[:8]]
        rho=float(spearmanr(curv[reliable],np.abs(error[reliable])).statistic)
        sections=[]
        for s in range(16):
            ii=[i for i,n in enumerate(nodes) if int(g['stations_px'][n['id']]/g['period_px']*16)==s]
            if ii:sections.append(dict(section=s,observations=len(ii),median_modular_index_discrepancy=float(np.median(error[ii])),reliable_disagreements=sum(bool(reliable[i] and error[i]) for i in ii)))
        rows.append(dict(model=name,N=N,frozen_source_sha256=sha(path),native_support_pixels=d['support_rays'],photographic_observations=len(nodes),global_options=options,best=best,
            reference_aligned_first_disagreements=firstbad,edge_summary=dict(Counter(e['status'] for e in edge_rows)),edge_rows=edge_rows,
            reliable_modal_observations=int(reliable.sum()),reliable_exact_global_index_matches=int(np.sum(reliable&(error==0))),curvature_abs_error_spearman=rho,sections=sections,
            policy='One origin for the entire conditional graph, not one per R324 chart. N used only to address this frozen model; no photograph count inference. Modal surface owners are model predictions, not independent photo labels.'))
    save(OUT/'model-comparison.json',dict(models=rows,seconds=time.perf_counter()-start,geometry_changed=False,ray_policy='Reused frozen R324 original native first-hit support ledgers, not newly timed tracing.',physical_conclusion='Disagreements do not identify whether the photograph topology, model shape/placement or correspondence is wrong. No fitting or causal curvature claim.'))
    print([{k:r[k] for k in ['model','N','best','edge_summary','reliable_exact_global_index_matches','curvature_abs_error_spearman']} for r in rows])
if __name__=='__main__':main()
