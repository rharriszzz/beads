"""Fragmentation attribution, transition outcomes, pattern constraints and interface."""
import json,math
from pathlib import Path
from collections import Counter,defaultdict
import numpy as np
from scipy.spatial import cKDTree
from photo2.r323.tracker import save
OUT=Path(__file__).parent/'results'
def main():
    g=json.load(open(OUT/'graph.json'));old=json.load(open('photo2/r324/results/graph.json'));op={o['id']:o for o in g['observations']};nodes={n['id']:n for n in g['intersections']};ons={n['id']:n for n in old['intersections']};L=g['period_px'];st=g['stations_px'];es=g['graph']['edges'];ue=g['graph']['unresolved_edges'];oldkeys={frozenset((e['source'],e['target'])):e for e in old['graph']['edges']};keys={frozenset((e['source'],e['target'])):e for e in es}
    breaks=[]
    def crossing(e,cut):
        a=((st[e['source']]-cut+L/2)%L)-L/2;b=((st[e['target']]-cut+L/2)%L)-L/2
        return a*b<=0 and max(abs(a),abs(b))<140
    for t in old['transitions']:
        if t['translation_consistent']:continue
        i=t['current'];w=g['windows'][i];cut=.5*(w['arc_px']+g['windows'][i-1]['arc_px']);cross=[e for e in es if crossing(e,cut)];un=[e for e in ue if crossing(e,cut)];nt=g['transitions'][i]
        bestD6=max([x['agree']/x['common'] for x in t['triangular_lattice_alternatives']] or [0]);before=max([x['agree']/x['common'] for x in t['checks'] if x['common']] or [0])
        breaks.append(dict(window=i,xy=w['center'],old_checks=t['checks'],old_best_D6_fraction=bestD6,old_identity_fraction=before,
            new_checks=nt['checks'],new_transition_all_agree=nt['translation_consistent'],accepted_links_across_geographic_cut=len(cross),unresolved_links_across_cut=len(un),
            cross_edges=[dict(source=e['source'],target=e['target'],family=e['family']) for e in cross],
            status='conditional cross-cut connectivity; overlap alternatives still disagree' if cross and not nt['translation_consistent'] else ('conditional overlap and cross-cut connectivity' if cross else 'no accepted crossing; closure remains open'),
            warning='A cross-cut edge is not independent proof that every row at this transition is correct.'))
    reason=Counter(r for e in old['graph']['unresolved_edges'] for r in e['reasons']);only=[e for e in old['graph']['unresolved_edges'] if e['reasons']==['unresolved transported chart boundary; no index propagation']]
    fixes=[e for e in es if frozenset((e['source'],e['target'])) not in oldkeys];lost=[e for e in old['graph']['edges'] if frozenset((e['source'],e['target'])) not in keys]
    black=json.load(open(OUT/'colored-first.json'));bp=black['indexed_black_with_colored_prediction'];newblack=[r for r in bp if ons[r['observation']]['component'] is None]
    ranges={};duplicates={}
    for name in ['A','B','reverse_A','reverse_B']:
        groups=defaultdict(list)
        for n in nodes.values():
            if n['component'] is not None:groups[n['conditional_indices'][name]].append(n['id'])
        ranges[name]=dict(minimum=min(groups),maximum=max(groups),span=max(groups)-min(groups),unknown_slots=max(groups)-min(groups)+1-len(groups));duplicates[name]=[dict(index=k,observations=v) for k,v in groups.items() if len(v)>1]
    # Exact-repeat rejection certificates for the full conditional map.
    patterns=[]
    for name in ['A','B','reverse_A','reverse_B']:
        ns=[n for n in nodes.values() if n['component'] is not None and n['color'] in ['red','yellow','black']]
        for period in range(1,501):
            groups=defaultdict(list)
            for n in ns:groups[n['conditional_indices'][name]%period].append(n)
            comparisons=sum(len(v)*(len(v)-1)//2 for v in groups.values());conflicts=[]
            for rem,ls in groups.items():
                colors={n['color'] for n in ls}
                if len(colors)>1:
                    a=ls[0];b=next(n for n in ls if n['color']!=a['color']);conflicts.append(dict(residue=rem,first=a['id'],second=b['id'],colors=[a['color'],b['color']]))
            patterns.append(dict(interpretation=name,period=period,pair_comparisons=comparisons,conflicting_residues=len(conflicts),first_conflicts=conflicts[:3],compatible=not conflicts,maker_nonmultiple13_compatible=period%13!=0))
    save(OUT/'pattern-constraints.json',dict(policy='Conditional integer map and observed colors only. Contradictions can indicate wrong map/color, not absence of a true repeat. No adoption.',periods=patterns))
    # A straight component path cannot prove N; conditional lower spans only.
    report=dict(R324_reasons=dict(reason),chart_only_rejected_links=len(only),chart_only_now_accepted=sum(frozenset((e['source'],e['target'])) in keys for e in only),
        R324_components=len(old['graph']['components']),R325_components=len(g['graph']['components']),new_edges=len(fixes),removed_edges=len(lost),new_edge_rows=fixes,removed_edge_rows=lost,
        breaks=breaks,black_colored_supported=len(bp),newly_indexed_black_colored_supported=len(newblack),new_black_rows=newblack,
        conditional_ranges=ranges,duplicate_conditional_indices=duplicates,
        proposed_N_controls=[dict(N=N,exceeds_conditional_A_span=N>ranges['A']['span'],exceeds_conditional_B_span=N>ranges['B']['span']) for N in [2700,2800,3000]],
        followed_families=dict(globally_oriented=2,certified_full_circuit=0,fragments=dict(Counter(t['family'] for t in g['tracks']))),
        outside_R161_accuracy='unknown; no additional maker labels or independent identity denominator',
        uncertainty='One component is conditional connected evidence, not certified physical reconstruction. No supported winding cycle or N.')
    save(OUT/'analysis.json',report)
    interface=dict(schema='graph-conditioned-photo-v1',image_sha256=g['image_sha256'],image_path='beads-photo-2.jpg',independent_of_model=True,
        origins=[dict(component=c['id'],observation=c['origin']) for c in g['graph']['components']],
        index_interpretations=dict(A=[7,6],B=[6,7],reverse_A=[-7,-6],reverse_B=[-6,-7]),closure=g['closure'],
        observations=[dict(id=n['id'],xy=n['xy'],color=n['color'],component=n['component'],relative_ab=n['relative_ab'],conditional_indices=n['conditional_indices'],
            confidence=n['status'],pixel_support=n['id'],original_source=op[n['id']]['source'],original_pixel_count=op[n['id']]['source_pixel_count'],
            hypotheses=n['local_hypothesis_evidence'],representative_xy=n['representative_xy'],representative_spread_px=n['representative_spread_px']) for n in nodes.values()],
        native_support_file='observation-pixels.json',accepted_neighbors=es,unresolved_neighbors=ue,
        unresolved_observations=[n['id'] for n in nodes.values() if n['component'] is None],
        restrictions=['Relative indices are conditional photo inference, never verified physical addresses.','Retain alternative 6/7 maps and reversal.','No N inferred; do not wrap indices using a fitted count as photographic evidence.','No target position is a measured bead center.','Unresolved links and native faint candidates must not silently become fixed fitting constraints.'])
    save(OUT/'model-input.json',interface)
    print({k:v for k,v in report.items() if k not in ['breaks','new_edge_rows','removed_edge_rows','new_black_rows']})
if __name__=='__main__':main()
