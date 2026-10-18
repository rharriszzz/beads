"""Independent replay of every growth edge and native photographic audit."""
import argparse, collections, time
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps
from scipy.ndimage import map_coordinates
from scipy.spatial import cKDTree
from .grow import ROOT,BANK,SEED,read,save,sha
from .export import key

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',default='photo2/r328/results');args=ap.parse_args();out=Path(args.output);start=time.perf_counter()
    g=read(out/'graph.json.gz');seal=read(out/'scientific-seal.json');assert sha(out/'graph.json.gz')==seal['graph_sha256'];assert sha(BANK)==seal['bank_sha256']
    bank=read(BANK);op={o['id']:o for o in bank['observations']};assert g['observations']==bank['observations'];prep=read(Path(seal['run'])/'prepared.json.gz');patches=prep['patches'];period=g['period_px'];stations=g['stations_px'];H=np.array(g['graph']['closure']['holonomy_ab']);N=len(bank['windows']);coords={(SEED,int(round(-stations[SEED]/period))):np.zeros(2,dtype=int)};all_edges=set();score=0.;equations=0
    for step,r in enumerate(g['growth']):
        if r.get('skipped'):continue
        wi=r['window'];p=patches[wi][r['patch']];arc=bank['windows'][wi]['arc_px']+(period if step==N else 0);local={(o,int(round((arc-stations[o])/period))):np.array(ab)+r['offset'] for o,ab in p['assignments'].items()};old=set(coords);common=old&local.keys();assert len(common)>=(1 if step==0 else 2)
        assert all(np.array_equal(coords[o],local[o]) for o in common)
        # Independent graph flood fill proves the whole patch attaches, including
        # newly added observations; no second component is created temporarily.
        adj=collections.defaultdict(set)
        for a,b,d in p['edges']:
            assert np.array_equal(np.array(p['assignments'][b])-p['assignments'][a],d)
            ka=(a,int(round((arc-stations[a])/period)));kb=(b,int(round((arc-stations[b])/period)))
            adj[ka].add(kb);adj[kb].add(ka);all_edges.add(key(a,b,d));equations+=1
        reached=set(common);todo=list(common)
        while todo:
            a=todo.pop()
            for b in adj[a]-reached:reached.add(b);todo.append(b)
        assert set(local)<=reached;coords.update(local);score+=p['score']
        assert set(map(tuple,r['attached_to']))==common
    assert abs(score-g['score'])<1e-8
    assert all_edges=={key(e['source'],e['target'],e['delta_ab']) for e in g['graph']['edges']}
    assert {(c['observation'],c['turn']):tuple(c['ab']) for c in g['unwrapped_coordinates']}=={k:tuple(v) for k,v in coords.items()}
    base={};turns=collections.defaultdict(set)
    for (o,k),v in coords.items():
        vv=v-k*H;turns[o].add(k)
        if o in base:assert np.array_equal(base[o],vv)
        base[o]=vv
    assert sorted(o for o,ks in turns.items() if len(ks)>1)==g['graph']['closure']['return_observations']
    assert len(g['graph']['closure']['return_observations'])>=3
    for n in g['intersections']:
        if n['component'] is not None:assert np.array_equal(n['relative_ab'],base[n['id']])
    # Independent scalar native checks on every exported edge, not only a sample.
    from photo2.r325.tracker import preprocess
    im=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');assert sha(ROOT/'beads-photo-2.jpg')==g['image_sha256'];data=preprocess(im);fg=data['fg'].astype(np.float32);xy=np.array([o['xy'] for o in g['observations']]);ids=[o['id'] for o in g['observations']]
    for e in g['graph']['edges']:
        a,b=e['source'],e['target'];p,q=np.array(op[a]['xy']),np.array(op[b]['xy']);v=q-p;zz=xy-p;fractions=zz@v/(v@v);perp=np.linalg.norm(zz-fractions[:,None]*v,axis=1);near={ids[i] for i in np.flatnonzero((fractions>.2)&(fractions<.8)&(perp<7))}-{a,b};assert not near
        pts=np.linspace(p,q,31);val=float(map_coordinates(fg,[pts[:,1],pts[:,0]],order=1,mode='nearest').mean());assert val>.95 and abs(val-e['foreground_fraction'])<1e-7
        wrap=int(round((stations[a]-stations[b])/period));assert np.array_equal(base[b]-base[a]+wrap*H,e['delta_ab'])
    # Recompute selected candidate predictions from original native RGB. This is
    # measurement replay, not independent truth or a cold detector benchmark.
    from photo2.r327.evidence import evaluate,maps
    fields=maps(data['rgb']);seen=set();rows=0;maxdelta=0.
    for r in g['growth']:
        if r.get('skipped'):continue
        k=(r['window'],r['hypothesis'])
        if k in seen:continue
        seen.add(k);h=bank['windows'][k[0]]['hypotheses'][k[1]];fresh=evaluate(h,op,fields);old=h['r327_evidence'];assert len(fresh['rows'])==len(old['rows'])
        for a,b in zip(fresh['rows'],old['rows']):
            assert a['observation']==b['observation'];d=float(np.max(abs(np.array(a['predictions_xy'])-b['predictions_xy'])));maxdelta=max(maxdelta,d);assert d<1e-8 and abs(a['utility']-b['utility'])<1e-9;rows+=1
        p=patches[k[0]][r['patch']];group=set(p['assignments']);rr={a['observation']:a for a in fresh['rows']};fraction=len(group)/len(h['assignments']);score=sum(rr[o]['utility'] for o in group if o in rr)+.35*sum(a['reward'] for a in fresh['runs'] if set(a['observations'])<=group)+.35*h['photo_score']*fraction-h['r327_shared_shape']['penalty']*fraction;assert abs(score-p['score'])<1e-9
    for c in read(out/'native-crops.json')['crops']:
        assert np.array_equal(np.array(im.crop(c['box'])),np.array(Image.open(out/(c['name']+'-native.png'))))
    save(out/'verification.json',dict(passed=True,seconds=time.perf_counter()-start,connected_growth_steps=len(g['growth']),local_edge_equations=equations,unique_edges=len(all_edges),native_prediction_rows=rows,max_prediction_delta_px=maxdelta,return_observations=len(g['graph']['closure']['return_observations']),original_observations_exact=True,native_crops_exact=True,all_exported_edges_native_checked=True,all_coordinate_equations_exact=True))
    print(read(out/'verification.json'))
if __name__=='__main__':main()
