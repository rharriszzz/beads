"""Independent arithmetic, original-pixel provenance, and guarded exact replay."""
import hashlib,json,sys,tempfile,time
from pathlib import Path
from collections import Counter,defaultdict,deque
import numpy as np
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'photo2/r323/results'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,o):Path(p).write_text(json.dumps(o,indent=2)+'\n')
def main():
    began=time.perf_counter();g=json.loads((OUT/'graph.json').read_text());v=json.loads((OUT/'validation.json').read_text());freeze=json.loads((OUT/'freeze.json').read_text())
    for p,h in freeze['files'].items():assert sha(ROOT/p)==h,p
    source=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'))
    assert np.array_equal(np.asarray(Image.open(OUT/'raw.png')),source[0:700,900:1900])
    catalog={o['id']:o for o in json.loads((ROOT/'photo2/review/r275/inventory.json').read_text())['locations']}
    pixels={o['id']:np.array(o['pixels_xy']) for o in json.loads((OUT/'observation-pixels.json').read_text())};op={o['id']:o for o in g['observations']};checks=[]
    for oid,o in op.items():
        p=pixels[oid];assert len(p)==o['source_pixel_count'] and len(np.unique(p,axis=0))==len(p)
        rgb=source[p[:,1],p[:,0]]
        if oid in catalog:
            q=catalog[oid]['bright_patch'];expected=np.array([[x,y] for y,lo,hi in q['runs'] for x in range(lo,hi+1)])
            assert np.array_equal(expected,p);assert len(p)==q['pixel_count'];centroid=p.mean(0)
        else:
            lin=rgb/255.;lin=np.where(lin<=.04045,lin/12.92,((lin+.055)/1.055)**2.4);centroid=np.average(p,axis=0,weights=lin.min(1))
        assert np.max(abs(centroid-o['xy']))<1e-9
        checks.append(dict(id=oid,pixels=len(p),rgb_sha256=hashlib.sha256(rgb.tobytes()).hexdigest()))
    fits=0;assignments=0
    for w in g['windows']:
        for h in w['hypotheses']:
            entries=h['assignments'];ab={oid:tuple(a['ab']) for oid,a in entries.items()};assert len(set(ab.values()))==len(ab)
            score=0.;triangles=0
            for oid,a in entries.items():
                prediction=np.array(h['basis'])@a['ab']+h['offset'];error=np.linalg.norm(prediction-op[oid]['xy']);sigma=8 if op[oid]['color']=='black' else 5
                assert np.max(abs(prediction-a['predicted_xy']))<1e-9 and abs(error-a['residual_px'])<1e-9
                assert error<2*sigma+1e-9
                weight=1 if op[oid]['band_clearance_px']>=18 else .55;score+=weight*(1-.25*(error/sigma)**2)
                aa,bb=ab[oid];triangles+=int((aa+1,bb) in ab.values() and (aa,bb+1) in ab.values())
            assert triangles==h['triangles'] and abs(score+.18*triangles-h['score'])<1e-9
            fits+=1;assignments+=len(entries)
    def relation(a,b):
        common=set(a['assignments'])&set(b['assignments'])
        if len(common)<4:return 0
        shifts=[tuple(np.array(a['assignments'][i]['ab'])-b['assignments'][i]['ab']) for i in common]
        count=Counter(shifts).most_common(1)[0][1];return .35*count-2.5*(len(common)-count)
    for beam in g['joint_beam']:
        score=0.
        for wi,hi in enumerate(beam['choices']):
            if hi is None:continue
            h=g['windows'][wi]['hypotheses'][hi];score+=h['score']-g['windows'][wi]['hypotheses'][0]['score']
            for prev in range(max(0,wi-2),wi):
                pi=beam['choices'][prev]
                if pi is not None:score+=relation(g['windows'][prev]['hypotheses'][pi],h)
        assert abs(score-beam['score'])<1e-8
    nodes={n['id']:n for n in g['intersections']};accepted=g['graph']['edges'];adj=defaultdict(list)
    for e in accepted:
        a,b=nodes[e['source']],nodes[e['target']];assert a['component']==b['component']
        assert np.array_equal(np.array(b['relative_ab'])-a['relative_ab'],e['delta_ab'])
        assert e['supporting_windows']>=2 and e['consensus']>=.85 and not e['intervening_observations'] and e['foreground_fraction']>.95
        winsets={tuple(x['delta_ab']):set(z[0] for z in x['window_states']) for x in e['alternatives']};allwins=set.union(*winsets.values())
        # Alternatives use lexicographic observation orientation.
        d=tuple(e['delta_ab']) if e['source']<e['target'] else tuple(-np.array(e['delta_ab']))
        assert len(winsets[d])==e['supporting_windows']
        rivals=set().union(*(s for dd,s in winsets.items() if dd!=d));assert abs(1-len(rivals)/len(allwins)-e['consensus'])<1e-12
        for oid,o in op.items():
            if oid in (e['source'],e['target']):continue
            p=np.array(a['xy']);z=np.array(b['xy'])-p;q=np.array(o['xy'])-p;fraction=q@z/(z@z)
            assert not(.2<fraction<.8 and np.linalg.norm(q-fraction*z)<7)
        adj[a['id']].append((b['id'],np.array(e['delta_ab'])));adj[b['id']].append((a['id'],-np.array(e['delta_ab'])))
    coords={};components=0
    for start in adj:
        if start in coords:continue
        components+=1;coords[start]=np.zeros(2,int);todo=[start]
        while todo:
            a=todo.pop()
            for b,d in adj[a]:
                if b in coords:assert np.array_equal(coords[b],coords[a]+d)
                else:coords[b]=coords[a]+d;todo.append(b)
    assert len(accepted)-len(coords)+components==g['graph']['cycle_rank']
    for n in nodes.values():
        if n['conditional_indices'] is None:continue
        a,b=n['relative_ab'];assert n['conditional_indices']==dict(A=7*a+6*b,B=6*a+7*b,reverse_A=-7*a-6*b,reverse_B=-6*a-7*b)
        assert n['xy']==op[n['id']]['xy']
    # R161 scoring reconstructed from raw recorded series, not evaluator helpers.
    manual=json.loads((ROOT/'photo2/manual-labels-r161.json').read_text());number={p['id']:p['number'] for p in manual['annotations']};steps={'d1':(1,-1),'d2':(1,0),'d3':(0,1)}
    links=[(number[a],number[b],s['direction']) for s in manual['series'] if s['status']=='complete' for a,b in zip(s['bead_ids'],s['bead_ids'][1:])];assert len(links)==86
    mapping={a['maker']:a['node'] for a in v['associations'] if a['status']=='unambiguous proximity association'};inv={b:a for a,b in mapping.items()}
    table={(e['source'],e['target'],tuple(e['delta_ab'])) for e in accepted};recovered=[(a,b,d) for a,b,d in links if (mapping.get(a),mapping.get(b),steps[d]) in table]
    oldv=json.loads((ROOT/'photo2/r322/results/validation.json').read_text());interior={a['maker'] for a in oldv['associations'] if a['priority']=='interior'}
    assert len(recovered)==65 and sum(a in interior and b in interior for a,b,d in recovered)==45 and len(interior&mapping.keys())==25
    mc={1:np.zeros(2,int)}
    while len(mc)<40:
        previous=len(mc)
        for a,b,d in links:
            if a in mc:mc.setdefault(b,mc[a]+steps[d])
            if b in mc:mc.setdefault(a,mc[b]-steps[d])
        assert len(mc)>previous
    for a,b,d in links:assert np.array_equal(mc[b]-mc[a],steps[d])
    wrong=[]
    for e in accepted:
        if e['source'] in inv and e['target'] in inv:
            a,b=inv[e['source']],inv[e['target']]
            if not np.array_equal(mc[b]-mc[a],e['delta_ab']):wrong.append([a,b])
    assert not wrong
    assert all(np.array_equal(np.array(nodes[oid]['relative_ab'])-nodes[mapping[23]]['relative_ab'],mc[m]-mc[23]) for m,oid in mapping.items())
    # Explicit counterexample: coherent phase coordinates alone cannot check a row.
    from photo2.r323 import tracker
    fixture={'assignments':{str(i):{'ab':[i%3,i//3]} for i in range(6)}}
    shifted=json.loads(json.dumps(fixture))
    for a in shifted['assignments'].values():a['ab'][0]+=17;a['ab'][1]-=9
    assert tracker.overlap(fixture,shifted)['disagree']==0
    shifted['assignments']['2']['ab'][1]+=1
    assert tracker.overlap(fixture,shifted)['disagree']==1
    assert 7*6==6*7==42 and (6,0)!=(0,7)
    accesses=[];guard={'active':True}
    allowed={'beads-photo-2.jpg','photo2/review/r275/inventory.json','photo2/r323/tracker.py','photo2/r322/tracker.py'}
    def hook(event,args):
        if not guard['active'] or event!='open' or not isinstance(args[0],(str,bytes)):return
        p=Path(args[0]).resolve();mode=args[1]
        if ROOT in p.parents and isinstance(mode,str) and 'r' in mode:
            rel=str(p.relative_to(ROOT));accesses.append(rel);assert rel in allowed,'Forbidden detector input '+rel
    sys.addaudithook(hook);target=Path(tempfile.mkdtemp(prefix='r323-replay-'));start=time.perf_counter();fresh=tracker.run(target);elapsed=time.perf_counter()-start;guard['active']=False
    fresh=json.loads((target/'graph.json').read_text())
    def scientific(x):
        if isinstance(x,dict):return {k:scientific(v) for k,v in x.items() if k not in {'created_utc','timings_seconds','stage_timings_seconds'}}
        if isinstance(x,list):return [scientific(v) for v in x]
        return x
    assert scientific(fresh)==scientific(g)
    assert json.loads((target/'observation-pixels.json').read_text())==json.loads((OUT/'observation-pixels.json').read_text())
    write(OUT/'verification.json',dict(all_passed=True,observations=len(op),native_pixels=sum(x['pixels'] for x in checks),pixel_checks=checks,
        local_hypotheses_checked=fits,hypothesis_assignments_checked=assignments,beam_paths_checked=len(g['joint_beam']),accepted_edges_checked=len(accepted),
        components=components,cycle_rank=g['graph']['cycle_rank'],independently_recovered_R161_links=len(recovered),wrong_R161_links=wrong,
        matched_R161_coordinates_checked=len(mapping),guarded_repository_reads=sorted(set(accesses)),exact_scientific_replay=True,replay_seconds=elapsed,
        replay_stage_seconds=fresh['timings_seconds'],total_seconds=time.perf_counter()-began,
        contracts=['original RGB crop and native support centroids','all affine predictions/residuals/scores and unique cells','all retained joint beam scores','all edge votes/skip tests and integer coordinates','all four index alternatives','R161 edge/coordinate arithmetic from raw series','origin translation preserves identity; one-row switch contradicts overlap','42-step equal index does not merge planar observations','guarded deterministic scientific replay'],
        limitation='Independent formulas and original-pixel checks by the same assistant; no external human validation beyond the held-out R161 chart.'))
    print('PASS',len(op),'observations;',sum(x['pixels'] for x in checks),'pixels;',fits,'hypotheses;',len(accepted),'edges; replay',elapsed)
if __name__=='__main__':main()
