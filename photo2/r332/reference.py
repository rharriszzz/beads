"""Post-freeze extension of the already exposed R161 retrospective evaluation."""
import argparse
from pathlib import Path
from collections import defaultdict
import numpy as np
from .common import *

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',default='photo2/r332/results');args=ap.parse_args();out=Path(args.run);r=read(out/'graph.json.gz');graph_hash=sha(out/'graph.json.gz')
    from photo2.r322.evaluate import association
    labels=read(ROOT/'photo2/manual-labels-r161.json');ref=read(ROOT/'photo2/r328/results/reference.json');maker=sorted(labels['annotations'],key=lambda x:x['number']);obs=r['observations'];nodes=[dict(id=o['id'],observation=o['id'],status='probable bead') for o in obs if not o.get('provisional')];mapping,matches=association(nodes,obs,maker,18,3);inv={o:m for m,o in mapping.items()};mc={1:np.array([0,0])};adj=defaultdict(list)
    for row in ref['links']:
        a,z=row['maker_source'],row['maker_target'];d=np.array(row['delta_ab']);adj[a].append((z,d));adj[z].append((a,-d))
    todo=[1]
    while todo:
        a=todo.pop()
        for z,d in adj[a]:
            if z not in mc:mc[z]=mc[a]+d;todo.append(z)
            else:assert np.array_equal(mc[z],mc[a]+d)
    edge={edgekey(e['source'],e['target']):e for e in r['edges']};wrong=[];recovered=[]
    for e in r['edges']:
        a,z=inv.get(e['source']),inv.get(e['target'])
        if a is not None and z is not None and not np.array_equal(mc[z]-mc[a],e['delta_ab']):wrong.append(dict(e,maker_source=a,maker_target=z))
    for row in ref['links']:
        a,z=mapping.get(row['maker_source']),mapping.get(row['maker_target']);e=edge.get(edgekey(a,z)) if a and z else None
        if e and np.array_equal(np.array(e['delta_ab'])*(1 if e['source']==a else -1),row['delta_ab']):recovered.append(dict(row,source=a,target=z))
    oldids={o['id'] for o in baseline()[0]['observations']};new=[dict(maker=m,id=o) for m,o in mapping.items() if o not in oldids]
    save(out/'extended-reference.json',dict(graph_sha256=graph_hash,associated=len(mapping),recovered=len(recovered),wrong=wrong,matches=matches,new_associations=new,recovered_links=recovered,
        policy='Post-freeze full-inventory radius18/margin3 proximity association. Already-exposed R161, not a new blind test. Fixed original regression remains separate; no recovery code reads these labels.'))
    assert sha(out/'graph.json.gz')==graph_hash;print('R161 extended',len(mapping),len(recovered),'wrong',len(wrong),flush=True)

if __name__=='__main__':main()
