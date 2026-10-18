"""Independent arithmetic/native-pixel checks and read-guarded exact replay.
No validator changes inferred labels. Historical R161 is a separate read-only check.
"""
import json,hashlib,subprocess,sys,tempfile,time
from pathlib import Path
from collections import Counter,defaultdict,deque
import numpy as np
from PIL import Image,ImageOps
from scipy import ndimage as ndi
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'photo2/r325/results'
def read(p):return json.load(open(p))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def science(x):
    if isinstance(x,dict):return {k:science(v) for k,v in x.items() if k not in ['source_sha256','timings_seconds','stage_timings_seconds','peak_rss_mb','seconds']}
    if isinstance(x,list):return [science(v) for v in x]
    return x

def independent_overlap(a,b):
    common=a['assignments'].keys()&b['assignments'].keys()
    if len(common)<4:return 0.,None
    shifts=Counter(tuple(np.array(a['assignments'][o]['ab'])-b['assignments'][o]['ab']) for o in sorted(common));d,n=shifts.most_common(1)[0]
    return .35*n-2.5*(len(common)-n),np.array(d)

def path_objective(wins,path):
    hs=[w['hypotheses'][k] for w,k in zip(wins,path)];score=sum(h['score']-max(z['score'] for z in w['hypotheses']) for h,w in zip(hs,wins));n=len(hs)
    for i in range(n):
        x,dx=independent_overlap(hs[i],hs[(i+1)%n]);z,dz=independent_overlap(hs[i],hs[(i+2)%n]);_,dy=independent_overlap(hs[(i+1)%n],hs[(i+2)%n]);score+=x+z
        if all(d is not None for d in [dx,dy,dz]):score-=2.5*min(int(np.abs(dx+dy-dz).sum()),4)
    return score

def main():
    start=time.perf_counter()
    for path,h in read(OUT/'freeze.json')['files'].items():assert sha(ROOT/path)==h,path
    g=read(OUT/'graph.json');assert sha(ROOT/'photo2/r325/tracker.py')==g['source_sha256'];op={o['id']:o for o in g['observations']};ns={n['id']:n for n in g['intersections']};rgb=np.array(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));pixels=read(OUT/'observation-pixels.json');catalog={r['id']:r for r in read(ROOT/'photo2/review/r275/inventory.json')['locations']};assert sha(ROOT/'beads-photo-2.jpg')==g['image_sha256'];native=0
    for r in pixels:
        xy=np.array(r['pixels_xy']);o=op[r['id']];assert len(xy)==len(np.unique(xy,axis=0))==o['source_pixel_count'];v=rgb[xy[:,1],xy[:,0]]/255
        if r['id'] in catalog:
            expected=np.array([[x,y] for y,a,b in catalog[r['id']]['bright_patch']['runs'] for x in range(a,b+1)]);assert np.array_equal(xy,expected);centroid=xy.mean(0)
        else:
            linear=np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4);centroid=np.average(xy,axis=0,weights=linear.min(1))
        assert np.max(abs(centroid-o['xy']))<1e-9;native+=len(xy)
    assignments=0;hypotheses=0
    for w in g['windows']:
        R=np.array(w['frame']);assert np.max(abs(R.T@R-np.eye(2)))<1e-12
        for h in w['hypotheses']:
            assert np.max(abs(R@np.array(h['basis_local'])-h['basis']))<1e-9
            a=h['assignments'];cells={tuple(z['ab']) for z in a.values()};assert len(cells)==len(a);score=0;tri=0
            for oid,z in a.items():
                pred=np.array(h['basis'])@z['ab']+h['offset'];err=np.linalg.norm(pred-op[oid]['xy']);assert np.max(abs(pred-z['predicted_xy']))<1e-9;assert abs(err-z['residual_px'])<1e-9
                sigma=8 if op[oid]['color']=='black' else 5;assert err<2*sigma+1e-9;weight=1 if op[oid]['band_clearance_px']>=18 else .55;score+=weight*(1-.25*(err/sigma)**2);a0,b0=z['ab'];tri+=int((a0+1,b0) in cells and (a0,b0+1) in cells);assignments+=1
            assert tri==h['triangles'];assert abs(score+.18*tri-h['score'])<1e-8;hypotheses+=1
    # Independently recompute all retained full-path objective values.
    sol=g['global_solution'];assert abs(path_objective(g['windows'],sol['choices'])-sol['score'])<1e-8
    for path in sol['anchor_conditioned_paths']:assert abs(path_objective(g['windows'],path['choices'])-path['score'])<1e-8
    for sel,gaps in zip(sol['selected'],sol['max_marginal_gaps']):assert sel==[i for i,x in enumerate(gaps) if x<=sol['allowance']+1e-9]
    adjacency=defaultdict(list);pts=np.array([o['xy'] for o in op.values()]);ids=list(op)
    for e in g['graph']['edges']:
        a,b=ns[e['source']],ns[e['target']];assert a['component']==b['component'];assert np.array_equal(np.array(b['relative_ab'])-a['relative_ab'],e['delta_ab']);assert e['supporting_windows']>=2 and e['consensus']>=.85 and e['foreground_fraction']>.95 and not e['intervening_observations']
        votes={tuple(v['delta_ab']):{x[0] for x in v['window_states']} for v in e['alternatives']};d=tuple(e['delta_ab']) if e['source']<e['target'] else tuple(-np.array(e['delta_ab']));assert len(votes[d])==e['supporting_windows'];other=set().union(*(s for k,s in votes.items() if k!=d));allwins=set().union(*votes.values());assert abs(1-len(other)/len(allwins)-e['consensus'])<1e-12
        for v in e['alternatives']:
            for wi,hi in v['window_states']:
                assert hi in sol['selected'][wi];h=g['windows'][wi]['hypotheses'][hi]['assignments'];s,t=sorted([e['source'],e['target']]);assert np.array_equal(np.array(h[t]['ab'])-h[s]['ab'],v['delta_ab'])
        p,q=np.array(a['xy']),np.array(b['xy']);v=q-p;frac=(pts-p)@v/(v@v);dist=np.linalg.norm(pts-p-frac[:,None]*v,axis=1);assert not [ids[i] for i in np.flatnonzero((frac>.2)&(frac<.8)&(dist<7)) if ids[i] not in [a['id'],b['id']]]
        w=int(np.rint((g['stations_px'][a['id']]-g['stations_px'][b['id']])/g['period_px']));assert w==e['circuit_wrap'];adjacency[a['id']].append((b['id'],w));adjacency[b['id']].append((a['id'],-w))
    winds={};windcycles=[]
    for root in adjacency:
        if root in winds:continue
        winds[root]=0;todo=[root]
        while todo:
            x=todo.pop()
            for y,w in adjacency[x]:
                if y in winds:windcycles.append(winds[x]+w-winds[y])
                else:winds[y]=winds[x]+w;todo.append(y)
    assert not any(windcycles);assert not g['closure']['identified'];assert g['closure']['count_candidates'] is None
    for name,weights in [('A',[7,6]),('B',[6,7]),('reverse_A',[-7,-6]),('reverse_B',[-6,-7])]:
        indices=[]
        for n in ns.values():
            if n['component'] is not None:assert n['conditional_indices'][name]==np.array(n['relative_ab'])@weights;indices.append(n['conditional_indices'][name])
        assert len(set(indices))==len(indices)
    black=read(OUT/'colored-first.json');colored_checks=0;faint_pixels=0
    for p in black['predictions']:
        w=g['windows'][p['window']];B=np.array(p['basis_local']);offset=np.array(p['offset_local']);pred=np.array(w['frame'])@(B@p['cell_ab']+offset)+w['center'];assert np.max(abs(pred-p['predicted_xy']))<1e-9
        for oid,ab in p['colored_assignments'].items():
            assert op[oid]['color'] in ['red','yellow'];point=np.array(w['frame'])@(B@ab+offset)+w['center'];assert np.linalg.norm(point-op[oid]['xy'])<10+1e-9
        if p['measured_observation']:
            o=op[p['measured_observation']];assert o['color']=='black';assert np.linalg.norm(np.array(o['xy'])-pred)<=12+1e-9
        if 'raw_support_pixels' in p:
            xy=np.array(p['raw_support_pixels']);val=rgb[xy[:,1],xy[:,0]]/255;linear=np.where(val<=.04045,val/12.92,((val+.055)/1.055)**2.4);center=np.average(xy,axis=0,weights=linear.min(1));assert np.max(abs(center-p['raw_centroid_xy']))<1e-9;faint_pixels+=len(xy);assert p['measured_observation'] is None
        colored_checks+=1
    for r in black['indexed_black_with_colored_prediction']:assert len(r['windows'])>=2 and ns[r['observation']]['component'] is not None
    controls=read(OUT/'controls.json');assert all(r['same_selected'] and r['maximum_marginal_gap_delta']<1e-8 for r in controls['origin_controls'])
    assert read(OUT/'practice-reference-science.json')==read(OUT/'practice-optimized_reference-science.json')
    # Read-guarded replay permits only source RGB, appearance supports and guide.
    dest=Path(tempfile.mkdtemp(prefix='r325-guarded-'));code='''import sys,pathlib
from photo2.r325.tracker import run,ROOT
out=pathlib.Path(sys.argv[1]);allowed={ROOT/'beads-photo-2.jpg',ROOT/'photo2/review/r275/inventory.json',ROOT/'photo2/spline-seed-r175.json'};reads=set()
def guard(event,args):
 if event!='open' or not isinstance(args[0],(str,bytes)):return
 p=pathlib.Path(args[0]).resolve()
 if ROOT in p.parents and p.suffix in ['.json','.npz','.jpg','.gz','.csv']:
  if p not in allowed:raise RuntimeError('Undeclared detector data input: '+str(p))
  reads.add(str(p.relative_to(ROOT)))
sys.addaudithook(guard);run(out);print('AUDITED_READS',sorted(reads))
'''
    replay_start=time.perf_counter();r=subprocess.run([sys.executable,'-c',code,str(dest)],cwd=ROOT,text=True,capture_output=True);(OUT/'guarded-replay.log').write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr
    for name in ['graph.json','colored-first.json','observation-pixels.json']:assert science(read(dest/name))==science(read(OUT/name)),name
    result=dict(passed=True,observations=len(op),native_support_pixels=native,hypotheses=hypotheses,assignments=assignments,accepted_edges=len(g['graph']['edges']),colored_predictions=colored_checks,faint_candidate_pixels=faint_pixels,guarded_replay_seconds=time.perf_counter()-replay_start,replay_directory=str(dest),seconds=time.perf_counter()-start,
        checks=['original native supports and independent centroids','all shared-geometry candidates and scores','independent cyclic full-path objective','all accepted edge votes and spatial corridors','no winding cycle; unknown N retained','both index maps unique and reversals exact','colored-only prediction arithmetic and black exclusion from seed fits','native faint-candidate centroids remain unconfirmed','three cyclic origin controls','146-support same-result optimization replay','read-guarded full photograph replay'],
        limitation='Arithmetic and raw-pixel checks do not establish photographic identities outside the historical R161 cohort. No external human validation.')
    (OUT/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
if __name__=='__main__':main()
