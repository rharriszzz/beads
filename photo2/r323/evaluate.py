"""One post-freeze R161 evaluation. Never repairs or selects detector outputs."""
import json,time
from collections import Counter,deque
from pathlib import Path
import numpy as np
from photo2.r322.evaluate import association
from photo2.r323.tracker import ROOT,save,sha,utc
OUT=ROOT/'photo2/r323/results'
def main():
    began=time.perf_counter();freeze=json.loads((OUT/'freeze.json').read_text())
    for p,h in freeze['files'].items():assert sha(ROOT/p)==h,p
    g=json.loads((OUT/'graph.json').read_text());old=json.loads((ROOT/'photo2/r322/results/validation.json').read_text())
    doc=json.loads((ROOT/'photo2/manual-labels-r161.json').read_text());maker=sorted(doc['annotations'],key=lambda p:p['number']);num={p['id']:p['number'] for p in maker}
    manual=[dict(source=num[a],target=num[b],direction=s['direction']) for s in doc['series'] if s['status']=='complete' for a,b in zip(s['bead_ids'],s['bead_ids'][1:])]
    assert len(maker)==40 and len(manual)==86
    priority={a['maker']:a['priority'] for a in old['associations']};steps={'d2':np.array([1,0]),'d3':np.array([0,1]),'d1':np.array([1,-1])};fam={'F0':'d2','F1':'d3','difference':'d1'}
    coords={1:np.array([0,0])};adj={m['number']:[] for m in maker}
    for e in manual:adj[e['source']].append((e['target'],steps[e['direction']]));adj[e['target']].append((e['source'],-steps[e['direction']]))
    queue=deque([1])
    while queue:
        a=queue.popleft()
        for b,d in adj[a]:
            if b in coords:assert np.array_equal(coords[b],coords[a]+d)
            else:coords[b]=coords[a]+d;queue.append(b)
    nodes={n['id']:n for n in g['intersections']};edges=g['graph']['edges']
    def score(mapping):
        inv={v:k for k,v in mapping.items()};lookup={(e['source'],e['target'],fam[e['family']]) for e in edges};links=[];auto=[]
        for e in manual:
            a,b=e['source'],e['target'];p,q=mapping.get(a),mapping.get(b);status='unresolved'
            if p and q:
                if (p,q,e['direction']) in lookup:status='recovered'
                elif any((x==p and y==q) or (x==q and y==p) for x,y,f in lookup):status='wrong family or orientation'
                else:status='abstained link'
            links.append(dict(**e,status=status,automatic_source=p,automatic_target=q,priority='interior' if priority[a]==priority[b]=='interior' else 'edge'))
        for e in edges:
            a,b=inv.get(e['source']),inv.get(e['target']);status='unresolved endpoint identity'
            if a is not None and b is not None:status='agrees with maker chart' if np.array_equal(coords[b]-coords[a],steps[fam[e['family']]]) else 'disagrees with maker chart'
            auto.append(dict(**e,maker_source=a,maker_target=b,validation=status,maker_priority='interior' if a and b and priority[a]==priority[b]=='interior' else 'edge-or-unmatched'))
        return links,auto
    mapping,matches=association(g['intersections'],g['observations'],maker,18,3);links,auto=score(mapping)
    for r in matches:r['priority']=priority[r['maker']]
    summary=dict(beads=40,recorded_links=86,proximity_associated_beads=len(mapping),interior_beads=25,interior_recorded_links=45,
        interior_associated_beads=sum(priority[k]=='interior' for k in mapping),recovered_recorded_links=sum(e['status']=='recovered' for e in links),
        interior_recovered_links=sum(e['priority']=='interior' and e['status']=='recovered' for e in links),
        interior_wrong_automatic_links=sum(e['maker_priority']=='interior' and e['validation']=='disagrees with maker chart' for e in auto),
        recorded_link_status=dict(Counter(e['status'] for e in links)),automatic_link_status=dict(Counter(e['validation'] for e in auto)))
    sensitivities=[]
    for radius in (10,14,18,22):
        for margin in (0,3,5):
            mp,_=association(g['intersections'],g['observations'],maker,radius,margin);ll,aa=score(mp)
            sensitivities.append(dict(radius=radius,margin=margin,associated=len(mp),recovered=sum(e['status']=='recovered' for e in ll),wrong=sum(e['validation']=='disagrees with maker chart' for e in aa)))
    # Component origins aligned once to a central associated observation, then all
    # residuals reported, including any drift; no coordinate repair.
    residuals=[];origins={}
    for ci in sorted({nodes[oid]['component'] for oid in mapping.values()}):
        members=[m for m,oid in mapping.items() if nodes[oid]['component']==ci];origin=min(members,key=lambda m:abs(m-23));origins[ci]=origin
        for m in members:
            delta=np.array(nodes[mapping[m]]['relative_ab'])-nodes[mapping[origin]]['relative_ab']-(coords[m]-coords[origin])
            residuals.append(dict(maker=m,observation=mapping[m],component=ci,origin_maker=origin,residual_ab=delta.tolist(),A_error=int(delta@[7,6]),B_error=int(delta@[6,7])))
    report=dict(created_utc=utc(),freeze_sha256=sha(OUT/'freeze.json'),summary=summary,R322_baseline=old['summary'],associations=matches,recorded_links=links,automatic_links=auto,
        coordinate_residuals=residuals,sensitivity=sensitivities,r171_chain=[e for e in links if (e['source'],e['target']) in [(11,14),(14,16)]],
        bead10=next(r for r in matches if r['maker']==10),specific_failures=[e for e in links if (e['source'],e['target']) in [(2,3),(4,5)]],
        seconds=time.perf_counter()-began,
        limitation='Historical R322 failure geography was known; runtime data holdout and one final R161 scoring, not developer blindness. Larger unlabeled region has no independent accuracy denominator. Fixed R322 interior eligibility retained.')
    save(OUT/'validation.json',report);print(json.dumps(summary,indent=2));print('specific',report['specific_failures']);print('bead10',report['bead10']);print('r171',report['r171_chain']);print('wrong coordinates',[r for r in residuals if r['residual_ab']!=[0,0]])
if __name__=='__main__':main()
