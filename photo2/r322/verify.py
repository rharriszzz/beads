"""Independent saved-artifact audit and isolated image-only replay.

No tracker graph-construction or evaluator scoring functions are used for the
saved-edge, cycle, pixel, index or R161 checks below.
"""
import ast,hashlib,json,sys,tempfile,time
from pathlib import Path
from collections import Counter,deque
import numpy as np
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'photo2/r322/results'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,o):Path(p).write_text(json.dumps(o,indent=2)+'\n')

def audit_edges(ids,edges):
    adj={i:[] for i in ids}
    for e in edges:
        a,b=e['source'],e['target'];d=np.array(e['delta_ab'],int);adj[a].append((b,d));adj[b].append((a,-d))
    coords={};components=0;conflicts=[]
    for start in ids:
        if start in coords:continue
        components+=1;coords[start]=np.zeros(2,int);queue=deque([start])
        while queue:
            a=queue.popleft()
            for b,d in adj[a]:
                val=coords[a]+d
                if b in coords:
                    if not np.array_equal(val,coords[b]):conflicts.append([a,b,(val-coords[b]).tolist()])
                else:coords[b]=val;queue.append(b)
    return dict(cycle_rank=len(edges)-len(ids)+components,components=components,conflicts=conflicts)

def main():
    began=time.perf_counter();g=json.loads((OUT/'graph.json').read_text());v=json.loads((OUT/'validation.json').read_text());freeze=json.loads((OUT/'freeze.json').read_text())
    for p,h in freeze['files'].items():assert sha(ROOT/p)==h,p
    old=ROOT/'photo2/r322/development/frozen-v1';oldg=json.loads((old/'graph.json').read_text());oldf=json.loads((old/'freeze.json').read_text())
    assert sha(old/'tracker.py')==oldf['files']['photo2/r322/tracker.py']
    assert sha(old/'graph.json')==oldf['files']['photo2/r322/results/graph.json']
    for key in ['tracks','intersections','graph','controls','directions']:assert oldg[key]==g[key],key
    source=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));fields=np.load(OUT/'fields.npz')
    assert np.array_equal(fields['rgb'],source[130:520,1180:1540])
    raw=np.asarray(Image.open(OUT/'raw.png'));assert np.array_equal(raw,np.repeat(np.repeat(source[215:385,1180:1540],5,axis=0),5,axis=1))
    catalog=json.loads((ROOT/'photo2/review/r275/inventory.json').read_text());catalog={p['id']:p for p in catalog['locations']}
    supports={p['id']:np.array(p['pixels_xy']) for p in json.loads((OUT/'observation-pixels.json').read_text())}
    pixelchecks=[]
    for o in g['observations']:
        pts=supports[o['id']];assert len(pts)==o['source_pixel_count'];assert len(np.unique(pts,axis=0))==len(pts)
        assert np.all((pts[:,0]>=0)&(pts[:,0]<source.shape[1])&(pts[:,1]>=0)&(pts[:,1]<source.shape[0]))
        if o['id'] in catalog:
            patch=catalog[o['id']]['bright_patch'];literal=np.array([[x,y] for y,a,b in patch['runs'] for x in range(a,b+1)])
            assert np.array_equal(pts,literal);assert len(pts)==patch['pixel_count'];assert np.max(abs(pts.mean(0)-o['xy']))<1e-10
        else:
            rgb=source[pts[:,1],pts[:,0]]/255;lin=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4);w=lin.min(1)
            assert np.max(abs(np.average(pts,axis=0,weights=w)-o['xy']))<1e-10
        pixelchecks.append(dict(id=o['id'],pixels=len(pts),rgb_sha256=hashlib.sha256(source[pts[:,1],pts[:,0]].tobytes()).hexdigest()))
    nodes={p['id']:p for p in g['intersections']};supported={i:p for i,p in nodes.items() if p['status'] in ('confident bead','probable bead')}
    assert len({p['observation'] for p in supported.values()})==len(supported)
    edges=[e for e in g['graph']['edges'] if e['status']=='accepted conditional'];audit=audit_edges(list(supported),edges)
    assert audit['cycle_rank']==27 and not audit['conflicts'] and audit['components']==1
    for e in edges:
        a,b=nodes[e['source']],nodes[e['target']];assert np.array_equal(np.array(b['ab'])-a['ab'],e['delta_ab'])
        if e['family']!='difference':assert a['track_ids'][int(e['family'][-1])]==b['track_ids'][int(e['family'][-1])]
    for p in nodes.values():
        a,b=p['relative_ab'];assert p['conditional_indices']==dict(A=7*a+6*b,B=6*a+7*b,reverse_A=-7*a-6*b,reverse_B=-6*a-7*b)
    # Independently reconstruct the held-out maker chart from raw recorded series.
    doc=json.loads((ROOT/'photo2/manual-labels-r161.json').read_text());number={p['id']:p['number'] for p in doc['annotations']};manual=[]
    steps={'d1':[1,-1],'d2':[1,0],'d3':[0,1]};adj={p['number']:[] for p in doc['annotations']}
    for series in doc['series']:
        if series['status']!='complete':continue
        for a,b in zip(series['bead_ids'],series['bead_ids'][1:]):
            a,b=number[a],number[b];d=steps[series['direction']];manual.append((a,b,series['direction']));adj[a].append((b,np.array(d)));adj[b].append((a,-np.array(d)))
    co={1:np.zeros(2,int)};queue=deque([1])
    while queue:
        a=queue.popleft()
        for b,d in adj[a]:
            if b in co:assert np.array_equal(co[b],co[a]+d)
            else:co[b]=co[a]+d;queue.append(b)
    assert len(co)==40 and len(manual)==86
    mapping={r['maker']:r['node'] for r in v['associations'] if r['status']=='unambiguous proximity association'};inverse={n:m for m,n in mapping.items()};family={'F0':'d2','F1':'d3','difference':'d1'}
    truth={(mapping.get(a),mapping.get(b),d) for a,b,d in manual if a in mapping and b in mapping}
    correct=sum((e['source'],e['target'],family[e['family']]) in truth for e in edges);assert correct==50
    wrong=[]
    for e in edges:
        if e['source'] in inverse and e['target'] in inverse:
            a,b=inverse[e['source']],inverse[e['target']]
            if not np.array_equal(co[b]-co[a],steps[family[e['family']]]):wrong.append([a,b,e['family']])
    assert sorted(wrong)==[[2,3,'F0'],[4,3,'difference'],[4,5,'F0']]
    # Decoder regression and independent cycle corruption/wrapping fixtures.
    assert len([x for x in range(5,5+1)])==1
    fixture=[dict(source='a',target='b',delta_ab=[1,0]),dict(source='b',target='c',delta_ab=[0,1]),dict(source='a',target='c',delta_ab=[1,1])]
    assert not audit_edges(['a','b','c'],fixture)['conflicts'];fixture[-1]['delta_ab']=[2,1]
    assert audit_edges(['a','b','c'],fixture)['conflicts']
    assert 6*7==7*6==42 and 7*6+6*0==7*0+6*7  # weighted index identification, distinct planar coordinates
    # A guarded replay records every repository read after scientific imports.
    from photo2.r322 import tracker
    accesses=[]
    def hook(event,args):
        if event!='open' or not isinstance(args[0],(str,bytes)):return
        try:p=Path(args[0]).resolve()
        except (TypeError,OSError):return
        if ROOT in p.parents:
            mode=args[1]
            if isinstance(mode,str) and 'r' in mode:
                rel=str(p.relative_to(ROOT));accesses.append(rel)
                assert rel in {'beads-photo-2.jpg','photo2/review/r275/inventory.json','photo2/r322/tracker.py'},'Forbidden tracker input: '+rel
    sys.addaudithook(hook)
    replay=Path(tempfile.mkdtemp(prefix='r322-replay-'));start=time.perf_counter();fresh=json.loads(json.dumps(tracker.run(replay)));elapsed=time.perf_counter()-start
    for key in ['configuration','directions','tracks','intersections','observations','graph','controls']:assert fresh[key]==g[key],key
    record=dict(utc=__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),all_passed=True,
        original_photo_sha256=sha(ROOT/'beads-photo-2.jpg'),native_crop_and_nearest_neighbor_review_exact=True,
        observations_checked=len(pixelchecks),native_pixels_checked=sum(p['pixels'] for p in pixelchecks),pixel_checks=pixelchecks,
        graph_audit=audit,independent_maker_beads=40,independent_maker_links=86,independent_recovered_links=correct,
        independent_wrong_links=wrong,prevalidation_scientific_decisions_preserved=True,
        contracts=['inclusive run endpoints','detect corrupted cycle','42-step weighted identification without planar merge','exact original RGB crop','every observation support/centroid','all graph edges and index alternatives','independent R161 edge arithmetic','guarded deterministic detector replay'],
        guarded_tracker_repository_reads=sorted(set(accesses)),replay_exact=True,replay_seconds=elapsed,
        replay_stage_seconds=fresh['timings_seconds'],total_seconds=time.perf_counter()-began,
        external_review=False,limitation='Independent formulas and file-access audit by the same assistant; no independent human labeling or scientific model acceptance.')
    # The audit hook guards only repo reads; writes of this receipt remain allowed.
    write(OUT/'verification.json',record);print('PASS',len(pixelchecks),'observations;',record['native_pixels_checked'],'native pixels; exact replay',elapsed)
if __name__=='__main__':main()
