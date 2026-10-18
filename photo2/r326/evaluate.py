"""Retrospective reference, fixed historical stress set, and closure diagnostics.
This module is NEVER imported by the detector. It cannot change selections.
"""
import json,copy,time
from pathlib import Path
from collections import Counter,defaultdict,deque
import numpy as np
from photo2.r322.evaluate import association
from photo2.r323.tracker import save,sha
from .runner import key
from .contexts import pair_evidence,edge_context
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'photo2/r326/results';FULL=OUT/'full'
def read(p):return json.load(open(p))


def reference_audit(g):
    labels=read(ROOT/'photo2/manual-labels-r161.json');maker=sorted(labels['annotations'],key=lambda x:x['number']);num={a['id']:a['number'] for a in maker};steps={'d2':[1,0],'d3':[0,1],'d1':[1,-1]}
    recorded=[dict(source=num[a],target=num[b],direction=s['direction']) for s in labels['series'] if s['status']=='complete' for a,b in zip(s['bead_ids'],s['bead_ids'][1:])]
    priority={a['maker']:a['priority'] for a in read(ROOT/'photo2/r325/results/validation.json')['associations']}
    # Associate measured observations, even if no candidate indexes them.
    proxy=[dict(id=o['id'],observation=o['id'],status='probable bead') for o in g['observations'] if not o.get('provisional')]
    mapping,matches=association(proxy,g['observations'],maker,18,3);inv={v:k for k,v in mapping.items()};coords={1:np.zeros(2,int)};adj=defaultdict(list)
    for e in recorded:
        d=np.array(steps[e['direction']]);adj[e['source']].append((e['target'],d));adj[e['target']].append((e['source'],-d))
    todo=[1]
    while todo:
        a=todo.pop()
        for b,d in adj[a]:
            if b not in coords:coords[b]=coords[a]+d;todo.append(b)
            else:assert np.array_equal(coords[b],coords[a]+d)
    rows=[];accepted={key(e) for e in g['graph']['edges']};selected=g['selected_window_states'];dp=g['global_solution']['choices']
    for e in recorded:
        a,b=mapping.get(e['source']),mapping.get(e['target']);d=steps[e['direction']];bank=[];correct=[];chosen=[];dpchosen=[];wrong=[]
        if a and b:
            for wi,w in enumerate(g['windows']):
                for hi,h in enumerate(w['hypotheses']):
                    aa=h['assignments']
                    if a not in aa or b not in aa:continue
                    delta=(np.array(aa[b]['ab'])-aa[a]['ab']).tolist();rec=dict(window=w['id'],hypothesis=hi,delta=delta);bank.append(rec)
                    if delta==d:
                        correct.append(rec)
                        if hi in selected[wi]:chosen.append(rec)
                        if hi==dp[wi]:dpchosen.append(rec)
                    elif hi in selected[wi]:wrong.append(rec)
        ek=key(dict(source=a or '?',target=b or '?',delta_ab=d));recovered=ek in accepted
        status='missing photographic endpoint' if not a or not b else ('missing candidate' if not correct else ('available but no compatible selected witness' if not chosen else ('recovered' if recovered else 'selected correct; acceptance abstention')))
        rows.append(dict(**e,automatic_source=a,automatic_target=b,priority='interior' if priority[e['source']]==priority[e['target']]=='interior' else 'edge',status=status,recovered=recovered,candidate_witnesses=correct,selected_witnesses=chosen,cyclic_selected_witnesses=dpchosen,wrong_selected_witnesses=wrong,represented_deltas=sorted({tuple(r['delta']) for r in bank})))
    wrong_edges=[]
    for e in g['graph']['edges']:
        a,b=inv.get(e['source']),inv.get(e['target'])
        if a is not None and b is not None and not np.array_equal(coords[b]-coords[a],e['delta_ab']):wrong_edges.append(dict(**e,maker_source=a,maker_target=b,priority='interior' if priority[a]==priority[b]=='interior' else 'edge'))
    joint=[]
    for wi,w in enumerate(g['windows']):
        expected=[o for o in w['observation_ids'] if o in inv]
        if len(expected)<4:continue
        full=[];partial=[]
        for hi,h in enumerate(w['hypotheses']):
            ids=[o for o in expected if o in h['assignments']]
            if len(ids)<2:continue
            shifts={tuple(np.array(h['assignments'][o]['ab'])-coords[inv[o]]) for o in ids}
            if len(shifts)==1:
                partial.append(hi)
                if len(ids)==len(expected):full.append(hi)
        joint.append(dict(window=w['id'],expected_associated_observations=len(expected),full_correct_local_hypotheses=full,correct_partial_hypotheses=partial,selected=selected[wi]))
    indexed={n['id'] for n in g['intersections'] if n['component'] is not None};association_count=sum(o in indexed for o in mapping.values())
    return dict(summary=dict(observation_associations=len(mapping),indexed_associations=association_count,interior_indexed_associations=sum(priority[m]=='interior' and o in indexed for m,o in mapping.items()),recorded_links=len(rows),recovered=sum(r['recovered'] for r in rows),interior_recovered=sum(r['priority']=='interior' and r['recovered'] for r in rows),candidate_recall=sum(bool(r['candidate_witnesses']) for r in rows),interior_candidate_recall=sum(r['priority']=='interior' and bool(r['candidate_witnesses']) for r in rows),statuses=dict(Counter(r['status'] for r in rows)),wrong_automatic_edges=len(wrong_edges),wrong_interior_edges=sum(r['priority']=='interior' for r in wrong_edges)),associations=matches,links=rows,joint_local_recall=joint,wrong_edges=wrong_edges,policy='Retrospective fixed R161 chart; native-observation association radius18/margin3 before candidate recall scoring. No detector tuning, new ground truth or maker runtime input.')


def main():
    g=read(FULL/'graph.json');old=read(ROOT/'photo2/r325/results/graph.json');contexts=read(FULL/'contexts.json');evidence=pair_evidence(contexts)
    save(OUT/'candidate-recall.json',dict(R325=reference_audit(old),R326=reference_audit(g)))
    historic=read(ROOT/'photo2/r325/results/context-check.json');fixed=[e for e in historic['edges'] if e['primary_status']=='accepted conditional' and e['status']=='context-contested'];assert len(fixed)==174
    actual={key(e):e for e in g['graph']['edges']};pairs=defaultdict(list)
    for e in g['graph']['edges']+g['graph']['unresolved_edges']:pairs[tuple(sorted([e['source'],e['target']]))].append(e)
    diagnostic=[]
    for h in fixed:
        e=dict(source=h['source'],target=h['target'],delta_ab=h['global_delta']);k=key(e);review=edge_context(e,evidence);alts=pairs[tuple(sorted([h['source'],h['target']]))]
        replacements=[a for a in alts if key(a)!=k and key(a) in actual and edge_context(a,evidence)['status']=='consistent']
        # Historical contradicting contexts never disappear from the evidence just
        # because the new schedule did not reproduce them. A resolution requires
        # both new and archived interpretations to be explicitly reconciled.
        status='still ambiguous'
        if k in actual and review['status']=='consistent':status='original favored by current contexts; historical disagreement remains'
        elif replacements:status='alternative favored by current contexts; historical disagreement remains'
        elif review['contexts'] and all(len(r['deltas'])==1 for r in review['contexts']):
            ds={tuple(r['deltas'][0]) for r in review['contexts']}
            if len(ds)==1 and tuple(k[2:]) not in ds and not any(tuple(d) in [(1,0),(0,1),(1,-1),(-1,0),(0,-1),(-1,1)] for d in ds):status='current evidence favors neither direct interpretation; historical disagreement remains'
        diagnostic.append(dict(source=h['source'],target=h['target'],original_delta=h['global_delta'],original_hypotheses=h['votes'],current_contexts=review,current_accepted=k in actual,revised_candidates=[dict(source=a['source'],target=a['target'],delta_ab=a['delta_ab'],accepted=key(a) in actual) for a in alts],status=status,certified_resolution=False))
    original_tested={tuple(sorted([e['source'],e['target']])) for e in historic['edges']};outside=[dict(source=e['source'],target=e['target'],delta_ab=e['delta_ab'],**edge_context(e,evidence)) for e in g['graph']['edges'] if tuple(sorted([e['source'],e['target']])) not in original_tested]
    save(OUT/'historical-contested.json',dict(fixed_count=174,categories=dict(Counter(r['status'] for r in diagnostic)),certified_resolved_original=0,certified_resolved_alternative=0,certified_neither=0,unresolved_historical_disagreement=174,links=diagnostic,outside_original_test_summary=dict(Counter(e['status'] for e in outside)),outside_original_test=outside,policy='No photographic ground truth is manufactured from context preference; strict historical resolution retains old counterevidence. Current preference changes reported separately.'))
    # Reexamine all four exact old lower-bend endpoint pairs, even if new graph
    # abstentions prevent transporting a global winding through the circuit.
    closure_old=read(ROOT/'photo2/r325/results/closure-candidates.json');closure=[]
    for a,b in sorted({(p['source'],p['target']) for p in closure_old['proposals']}):
        variants=[]
        for wi,w in enumerate(g['windows']):
            for hi,h in enumerate(w['hypotheses']):
                aa=h['assignments']
                if a in aa and b in aa:variants.append(dict(window=w['id'],hypothesis=hi,delta_ab=(np.array(aa[b]['ab'])-aa[a]['ab']).tolist(),selected=hi in g['selected_window_states'][wi]))
        e=dict(source=a,target=b,delta_ab=next(p['delta_ab'] for p in closure_old['proposals'] if p['source']==a and p['target']==b))
        closure.append(dict(source=a,target=b,context=edge_context(e,evidence),candidate_deltas=sorted({tuple(v['delta_ab']) for v in variants}),witnesses=variants,old_proposals=[p for p in closure_old['proposals'] if p['source']==a and p['target']==b],new_accepted=[e for e in g['graph']['edges'] if {e['source'],e['target']}=={a,b}]))
    save(OUT/'closure-investigation.json',dict(graph_closure=g['closure'],old_four_pairs=closure,count_adopted=None,missing_evidence='Unique row continuation across lower-bend supports, and compatible intervening whole-circuit relations; additional scale preferences still conflict. Fragmentation prevents assigning one global winding gauge.',policy='No favored N, numerical 6/7 assignment or repeat used in inference. Old conditional counts remain archived, not measurements.'))
    # Conditional pattern scan per conservative component. Different gauges must
    # never be silently aligned to assert whole-bracelet repetition.
    model=read(FULL/'model-input.json');scan=[]
    for name in ['A','B']:
        for period in range(1,501):
            bins={};conflicts=[];comparisons=0
            for o in model['observations']:
                if o['component'] is None or o.get('provisional'):continue
                k=(o['component'],o['conditional_indices'][name]%period)
                if k in bins:
                    comparisons+=1
                    if bins[k]['color']!=o['color'] and len(conflicts)<3:conflicts.append(dict(first=bins[k]['id'],second=o['id'],component=o['component'],residue=k[1]))
                else:bins[k]=o
            scan.append(dict(map=name,period=period,compared_pairs=comparisons,conflict_witnesses=conflicts,passes_observed_components=not conflicts,maker_nonmultiple13_compatible=period%13!=0))
    save(OUT/'pattern-diagnostic.json',dict(rows=scan,adopted=None,policy='Conditional component-local diagnostic only; both reversals give identical equality conflicts. Complete repetitions and maker shortest-period restriction retained; no total N or cross-component gauge is established. No pattern feedback to detector.'))
    print('REFERENCE',reference_audit(g)['summary']);print('CONTESTED',dict(Counter(r['status'] for r in diagnostic)));print('OUTSIDE',dict(Counter(e['status'] for e in outside)))
if __name__=='__main__':main()
