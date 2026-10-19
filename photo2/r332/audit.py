"""Inventory and display audit completed before changing scientific assignments."""
import argparse,ast,time
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
from .common import *

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);args=ap.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=False);start=time.perf_counter()
    g,co,H=baseline();obs={o['id']:o for o in g['observations']};edges=g['graph']['edges'];ek={edgekey(e['source'],e['target']) for e in edges}
    tree=ast.parse((ROOT/'photo2/r331/review.py').read_text());lists={}
    for node in ast.walk(tree):
        if isinstance(node,ast.Assign):
            for target in node.targets:
                if isinstance(target,ast.Name) and target.id in ['gids','eids','fids','blackids']:lists[target.id]=ast.literal_eval(node.value)
    panels=[]
    for name,bbox,key in [('G',[1510,205,1750,375],'gids'),('upper-F',[1230,208,1510,365],'fids'),('inward',[1640,1485,1810,1645],'eids'),('black-direction',[1600,240,1785,390],'blackids')]:
        local={o for o in obs if inside(obs[o]['xy'],bbox)};selected=set(lists[key]);actual=[e for e in edges if e['source'] in local and e['target'] in local];drawn=[]
        for a in selected:
            for z in selected:
                if tuple(np.array(co[z])-co[a]) in [(1,0),(0,1)]:drawn.append((a,z))
        panels.append(dict(region=name,bbox=bbox,recorded=len(local),displayed=len(selected),
            omitted_observation_ids=sorted(local-selected),working_edges=len(actual),
            working_edges_displayed=sum(edgekey(a,z) in ek for a,z in drawn),
            coordinate_inferred_drawn=len(drawn),drawn_without_working_edge=[list(e) for e in drawn if edgekey(*e) not in ek],
            third_family_working_edges=sum(e['family']=='difference' for e in actual),
            genuinely_unindexed=[o for o in sorted(local) if o not in co]))
    cells={representative(v,H):o for o,v in co.items()};missing=[]
    for a,ab in co.items():
        for d in STEPS:
            z=cells.get(representative(np.array(ab)+d,H))
            if z and edgekey(a,z) not in ek:missing.append(dict(source=a,target=z,delta_ab=d,family=FAMILY[d]))
    inventory=read(ROOT/'photo2/review/r275/inventory.json');old_ids={o['id'] for o in g['observations']}
    older=[dict(id=o['id'],color=o['color'],xy=o['bright_patch']['centroid']) for o in inventory['locations'] if o['id'] not in old_ids and o.get('bright_patch',{}).get('centroid')]
    # Also expose photographic alternatives that cannot be inferred merely by
    # enumerating neighbors of the selected coordinates. These are retained
    # native-tested local-patch edges, not automatically selected whole-graph links.
    bank=read(ROOT/'photo2/r328/development/final256/prepared.json.gz');candidate_edges=defaultdict(set)
    for wi,patches in enumerate(bank['patches']):
        for patch in patches:
            for a,z,d in patch['edges']:
                if a>z:a,z,d=z,a,[-v for v in d]
                candidate_edges[(a,z,*d)].add(wi)
    absent=[]
    for (a,z,da,db),windows in candidate_edges.items():
        if edgekey(a,z) in ek:continue
        compatible=None
        if a in co and z in co:
            diff=np.array(co[z])-co[a]-[da,db];compatible=bool(diff[0]%H[0]==0 and diff[1]==diff[0]//H[0]*H[1])
        absent.append(dict(source=a,target=z,delta_ab=[da,db],supporting_windows=sorted(windows),
            baseline_coordinate_compatible=compatible,classification='unindexed endpoint' if compatible is None else 'compatible neighbor not selected' if compatible else 'competing local row/direction'))
    save(out/'cached-edge-alternatives.json.gz',dict(edges=absent,counts=dict(Counter(e['classification'] for e in absent)),
        scope='Every absent endpoint-pair/direction retained in the R328 native-tested connected-patch bank. These alternatives are not pooled into the accepted graph. Multiple directions for the same pair remain separate.'))
    save(out/'audit.json',dict(base_commit=BASE,baseline=dict(recorded=len(obs),indexed=len(co),unindexed=len(obs)-len(co),
        colors=dict(Counter(o['color'] for o in obs.values())),indexed_colors=dict(Counter(obs[o]['color'] for o in co)),
        links=len(edges),families=dict(Counter(e['family'] for e in edges))),panels=panels,
        unindexed=[obs[o] for o in sorted(obs.keys()-co.keys())],coordinate_neighbors_without_working_edge=missing,
        older_r275_observations_not_in_baseline=older,seconds=time.perf_counter()-start,
        user_review='User found no incorrect displayed labels/links in R331. Evidence applies only to displayed assignments, not all hidden/unreviewed assignments.',
        policy='Display omissions, unindexed recorded observations, absent graph links and absent observation candidates remain separate. No scientific reconstruction changed in this audit.'))
    paths=['beads-photo-2.jpg','photo2/r328/results/graph.json.gz','photo2/r328/development/final256/search.json.gz','photo2/r328/development/final256/prepared.json.gz','photo2/r327/results/graph.json.gz','photo2/r331/review.py','photo2/review/r275/inventory.json','photo2/review/r275/band-edge-candidates.json','photo2/review/r266/straight-0-selected12/regions.json.gz','photo2/review/r266/straight-0-selected6/regions.json.gz']
    save(out/'input-seal.json',dict(sources={p:sha(ROOT/p) for p in paths}))
    print([(p['region'],p['displayed'],p['recorded'],p['working_edges_displayed'],p['working_edges']) for p in panels],flush=True)

if __name__=='__main__':main()
