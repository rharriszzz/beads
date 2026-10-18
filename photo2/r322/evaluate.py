"""Held-out R161 evaluation of a previously frozen automatic graph.

No calls to the tracker and no writes to the graph. Maker points are arbitrary
surface picks. Appearance-point proximity yields provisional identity association;
ambiguous matches abstain, and sensitivity is reported rather than tuned away.
"""
import hashlib,json,time
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter,deque
import numpy as np
from scipy import ndimage as ndi
from scipy.optimize import linear_sum_assignment
from PIL import ImageDraw
from photo2.r322.review import base,xy,text
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'photo2/r322/results'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,o):Path(p).write_text(json.dumps(o,indent=2,allow_nan=False)+'\n')

def association(nodes,observations,maker,radius,margin):
    supported=[p for p in nodes if p['status'] in ('confident bead','probable bead')]
    op={p['id']:p for p in observations};mxy=np.array([[p['x'],p['y']] for p in maker])
    axy=np.array([op[p['observation']]['xy'] for p in supported]);dist=np.linalg.norm(mxy[:,None]-axy[None,:],axis=2)
    ii,jj=linear_sum_assignment(np.column_stack([np.where(dist<=radius,dist,999),np.full((len(maker),len(maker)),radius+.1)]))
    chosen={int(i):int(j) for i,j in zip(ii,jj) if j<len(supported) and dist[i,j]<=radius};rows=[];mapping={}
    for i,m in enumerate(maker):
        candidates=[dict(node=supported[j]['id'],distance=float(dist[i,j])) for j in np.argsort(dist[i]) if dist[i,j]<=radius]
        row=dict(maker=m['number'],xy=[m['x'],m['y']],candidates=candidates,status='unresolved',node=None)
        if i in chosen:
            j=chosen[i];nearest_row=np.delete(dist[i],j);nearest_col=np.delete(dist[:,j],i)
            separation=min(nearest_row.min(),nearest_col.min())-dist[i,j]
            row.update(node=supported[j]['id'],distance=float(dist[i,j]),association_margin=float(separation))
            if separation>=margin:
                row['status']='unambiguous proximity association';mapping[m['number']]=supported[j]['id']
            else:row['status']='ambiguous proximity association'
        rows.append(row)
    return mapping,rows

def main():
    began=time.perf_counter();freeze=json.loads((OUT/'freeze.json').read_text())
    for p,h in freeze['files'].items():assert sha(ROOT/p)==h,p
    g=json.loads((OUT/'graph.json').read_text());doc=json.loads((ROOT/'photo2/manual-labels-r161.json').read_text())
    maker=sorted(doc['annotations'],key=lambda p:p['number']);number={p['id']:p['number'] for p in maker};manual=[]
    for series in doc['series']:
        if series['status']!='complete':continue
        seq=series['bead_ids']
        for a,b in zip(seq,seq[1:]):manual.append(dict(source=number[a],target=number[b],direction=series['direction']))
    assert len(maker)==40 and len(manual)==86
    steps={'d2':np.array([1,0]),'d3':np.array([0,1]),'d1':np.array([1,-1])}
    coords={1:np.array([0,0])};queue=deque([1]);adj={m['number']:[] for m in maker}
    for e in manual:adj[e['source']].append((e['target'],steps[e['direction']]));adj[e['target']].append((e['source'],-steps[e['direction']]))
    while queue:
        a=queue.popleft()
        for b,d in adj[a]:
            if b in coords:assert np.array_equal(coords[b],coords[a]+d)
            else:coords[b]=coords[a]+d;queue.append(b)
    fields=np.load(OUT/'fields.npz');clearance=fields['clearance'];origin=np.array(g['configuration']['crop'][:2])
    priority={m['number']:'interior' if ndi.map_coordinates(clearance,[[m['y']-origin[1]],[m['x']-origin[0]]],order=1)[0]>=18 else 'edge' for m in maker}
    edges=[e for e in g['graph']['edges'] if e['status']=='accepted conditional'];nodes={p['id']:p for p in g['intersections']};family={'F0':'d2','F1':'d3','difference':'d1'}
    def score(mapping):
        inverse={v:k for k,v in mapping.items()};automatic={(e['source'],e['target'],family[e['family']]) for e in edges};rows=[]
        for e in manual:
            a,b=e['source'],e['target'];p,q=mapping.get(a),mapping.get(b)
            status='unresolved'
            if p and q:
                if (p,q,e['direction']) in automatic:status='recovered'
                elif any(x==p and y==q or x==q and y==p for x,y,f in automatic):status='wrong family or orientation'
                else:status='abstained link'
            rows.append(dict(**e,status=status,automatic_source=p,automatic_target=q,priority='interior' if priority[a]==priority[b]=='interior' else 'edge'))
        auto=[]
        for e in edges:
            a,b=inverse.get(e['source']),inverse.get(e['target']);status='unresolved endpoint identity'
            if a is not None and b is not None:
                status='agrees with maker chart' if np.array_equal(coords[b]-coords[a],steps[family[e['family']]]) else 'disagrees with maker chart'
            auto.append(dict(**e,maker_source=a,maker_target=b,validation=status,
                maker_priority='interior' if a and b and priority[a]==priority[b]=='interior' else 'edge-or-unmatched'))
        return rows,auto
    controls=[]
    for radius in (10,14,18,22):
        for margin in (0,3,5):
            mapping,rows=association(g['intersections'],g['observations'],maker,radius,margin);links,auto=score(mapping)
            controls.append(dict(radius=radius,margin=margin,associated_beads=len(mapping),recovered_links=sum(e['status']=='recovered' for e in links),
                automatic_disagreements=sum(e['validation']=='disagrees with maker chart' for e in auto)))
    mapping,matches=association(g['intersections'],g['observations'],maker,18,3);links,auto=score(mapping)
    for r in matches:r['priority']=priority[r['maker']]
    summary=dict(beads=40,recorded_links=86,proximity_associated_beads=len(mapping),
        ambiguous_beads=sum(r['status']=='ambiguous proximity association' for r in matches),
        unresolved_beads=sum(r['status']=='unresolved' for r in matches),
        recovered_recorded_links=sum(e['status']=='recovered' for e in links),
        recorded_link_status=dict(Counter(e['status'] for e in links)),
        automatic_link_status=dict(Counter(e['validation'] for e in auto)),
        interior_beads=sum(v=='interior' for v in priority.values()),
        interior_associated_beads=sum(priority[k]=='interior' for k in mapping),
        interior_recorded_links=sum(e['priority']=='interior' for e in links),
        interior_recovered_links=sum(e['priority']=='interior' and e['status']=='recovered' for e in links),
        interior_wrong_automatic_links=sum(e['maker_priority']=='interior' and e['validation']=='disagrees with maker chart' for e in auto),
        automatic_cycle_rank=g['graph']['cycle_rank'],automatic_cycle_conflicts=len(g['graph']['conflicts']),
        maker_cycle_rank=86-40+1)
    success=summary['interior_associated_beads']>=.9*summary['interior_beads'] and summary['interior_recovered_links']>=.9*summary['interior_recorded_links'] and summary['interior_wrong_automatic_links']==0
    # All contradictions are retained; no graph editing or identity repair.
    wrong=[e for e in auto if e['validation']=='disagrees with maker chart']
    report=dict(created_utc=datetime.now(timezone.utc).isoformat(),freeze_sha256=sha(OUT/'freeze.json'),maker_sha256=sha(ROOT/'photo2/manual-labels-r161.json'),
        summary=summary,success_gate=success,associations=matches,recorded_links=links,automatic_links=auto,sensitivity=controls,
        first_disagreement=min(wrong,key=lambda e:min(e['maker_source'],e['maker_target'])) if wrong else None,
        r171_chain=[e for e in links if (e['source'],e['target']) in [(11,14),(14,16)]],
        seconds=time.perf_counter()-began,
        limitation='Proximity to arbitrary maker surface picks is a provisional identity association. Inspect all marked raw-photo cases; ambiguous associations abstain. No maker geometry entered the frozen tracker.')
    save(OUT/'validation.json',report)
    panel=base();draw=ImageDraw.Draw(panel)
    for m in maker:
        x,y=xy([m['x'],m['y']]);draw.ellipse((x-4,y-4,x+4,y+4),outline='white',width=2);text(draw,(x+5,y-22),str(m['number']),'white',18)
    for r in matches:
        if not r['node']:continue
        p=nodes[r['node']];a=xy(r['xy']);b=xy(p['xy']);color='#00ffff' if r['status'].startswith('unambiguous') else '#ff9d35';draw.line([a,b],fill=color,width=2);text(draw,(b[0]+4,b[1]+4),p['id'],color,14)
    for e in wrong:
        draw.line([xy(nodes[e['source']]['xy']),xy(nodes[e['target']]['xy'])],fill='#ff702a',width=5)
    panel.save(OUT/'heldout-validation.png')
    print(json.dumps(summary,indent=2));print('success_gate',success);print('first',report['first_disagreement']);print('r171',report['r171_chain'])
if __name__=='__main__':main()
