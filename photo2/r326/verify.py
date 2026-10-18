"""Independent pixel, equation, path-score, graph and guarded replay checks.
No evaluation function edits selections. Independent equations do not call the
compatibility implementation being verified.
"""
import json,time,tempfile,subprocess,sys,hashlib,copy,gzip
from pathlib import Path
from collections import Counter,defaultdict
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import lsqr
from PIL import Image,ImageOps
from photo2.r323.tracker import save
from photo2.r325.verify import path_objective
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'photo2/r326/results';FULL=OUT/'full'
def raw(p):
    p=Path(p)
    return p.read_bytes() if p.exists() else gzip.decompress(p.with_suffix(p.suffix+'.gz').read_bytes())
def read(p):return json.loads(raw(p))
def sha(p):return hashlib.sha256(raw(p)).hexdigest()
def clean(x):
    if isinstance(x,dict):return {k:clean(v) for k,v in x.items() if k not in ['seconds','total_seconds','factor_build_seconds','timings_seconds','stage_timings_seconds','stages_seconds','peak_rss_mb','source_sha256']}
    if isinstance(x,list):return [clean(v) for v in x]
    return x

def verify_equations(g):
    ids={o['id']:i for i,o in enumerate(g['observations'])};n=len(ids);ws=g['windows'];rows=[];cols=[];vals=[];rhs=[]
    for wi,ss in enumerate(g['selected_window_states']):
        assert len(ss)<=1
        for hi in ss:
            for o,a in ws[wi]['hypotheses'][hi]['assignments'].items():
                r=len(rhs);wrap=int(np.rint((ws[wi]['arc_px']-g['stations_px'][o])/g['period_px']))
                rows.extend([r,r,r]);cols.extend([ids[o],n+wi,n+len(ws)]);vals.extend([1.,-1.,float(wrap)]);rhs.append(a['ab'])
    A=sparse.coo_matrix((vals,(rows,cols)),shape=(len(rhs),n+len(ws)+1)).tocsr();rhs=np.array(rhs);worst=0
    for dim in range(2):
        fit=lsqr(A,rhs[:,dim],atol=1e-13,btol=1e-13,iter_lim=10000)[0];err=float(np.abs(A@fit-rhs[:,dim]).max());worst=max(worst,err);assert err<1e-7,err
    # Direct pair check all common observations, including far-window overlaps.
    pairs=0
    chosen=[(i,ws[i]['hypotheses'][ss[0]]['assignments']) for i,ss in enumerate(g['selected_window_states']) if ss]
    for pos,(i,a) in enumerate(chosen):
        for j,b in chosen[pos+1:]:
            shared=a.keys()&b.keys()
            if not shared:continue
            shifts={tuple(np.array(a[o]['ab'])-b[o]['ab']) for o in shared};assert len(shifts)==1;pairs+=1
    return dict(assignment_equations=len(rhs),overlapping_selected_pairs=pairs,max_independent_equation_residual=worst)

def main():
    start=time.perf_counter();g=read(FULL/'graph.json');old=read(ROOT/'photo2/r325/results/graph.json');op={o['id']:o for o in g['observations']};pixels=read(FULL/'observation-pixels.json');rgb=np.array(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));catalog={o['id']:o for o in read(ROOT/'photo2/review/r275/inventory.json')['locations']};native=0
    seal=read(OUT/'scientific-seal.json')
    for p,h in seal['files'].items():assert sha(ROOT/p)==h,p
    assert sha(ROOT/'beads-photo-2.jpg')==g['image_sha256']==old['image_sha256']
    original={o['id']:o for o in old['observations']}
    for o in g['observations']:
        if o['id'] in original:assert o==original[o['id']]
        else:assert o['provisional'] and not o['independent_detection'] and not o['body_identity_confirmed']
    for p in pixels:
        xy=np.array(p['pixels_xy']);o=op[p['id']];assert len(xy)==o['source_pixel_count']==len(np.unique(xy,axis=0));val=rgb[xy[:,1],xy[:,0]]/255
        if p['id'] in catalog:
            expected=np.array([[x,y] for y,a,b in catalog[p['id']]['bright_patch']['runs'] for x in range(a,b+1)]);assert np.array_equal(xy,expected);cen=xy.mean(0)
        else:
            v=val.min(1);v=np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4);cen=np.average(xy,axis=0,weights=v)
        assert np.max(abs(cen-o['xy']))<1e-9;native+=len(xy)
    hypotheses=0;assignments=0
    for wi,w in enumerate(g['windows']):
        for hi,h in enumerate(w['hypotheses']):
            a=h['assignments'];cells={tuple(z['ab']) for z in a.values()};assert len(cells)==len(a);score=0;tri=0
            for oid,z in a.items():
                pred=np.array(h['basis'])@z['ab']+h['offset'];err=np.linalg.norm(pred-op[oid]['xy']);assert np.max(abs(pred-z['predicted_xy']))<1e-8;assert abs(err-z['residual_px'])<1e-8;sig=8 if op[oid]['color']=='black' else 5;assert err<2*sig+1e-8;wt=1 if op[oid]['band_clearance_px']>=18 else .55;score+=wt*(1-.25*(err/sig)**2);aa,bb=z['ab'];tri+=int((aa+1,bb) in cells and (aa,bb+1) in cells);assignments+=1
            assert tri==h['triangles'];assert abs(score+.18*tri-h.get('photo_score',h['score']))<1e-8
            assert abs(h['score']-(h['photo_score']-h['context_penalty']-h['longrange_penalty']))<1e-9;hypotheses+=1
        # Every R325 hypothesis, original locations and score, remains as prefix.
        for before,after in zip(old['windows'][wi]['hypotheses'],w['hypotheses']):
            for k,v in before.items():assert v==(after['photo_score'] if k=='score' else after[k]),(wi,k)
    assert abs(path_objective(g['windows'],g['global_solution']['choices'])-g['global_solution']['score'])<1e-8
    eq=verify_equations(g)
    nodes={n['id']:n for n in g['intersections']};selected=g['selected_window_states'];edges=g['graph']['edges'];edgeschecked=0
    for e in edges:
        a,b=e['source'],e['target'];d=np.array(e['delta_ab']);witness=[]
        for wi,ss in enumerate(selected):
            if not ss:continue
            aa=g['windows'][wi]['hypotheses'][ss[0]]['assignments']
            if a in aa and b in aa:
                assert np.array_equal(np.array(aa[b]['ab'])-aa[a]['ab'],d);witness.append(wi)
        assert len(witness)>=2;assert len(witness)==e['supporting_windows'];assert e['consensus']==1.;assert not e['intervening_observations'];assert e['foreground_fraction']>.95
        assert nodes[a]['component']==nodes[b]['component'];assert np.array_equal(np.array(nodes[b]['relative_ab'])-nodes[a]['relative_ab'],d)
        assert not any(e['synchronization_residual_ab']);edgeschecked+=1
    for n in nodes.values():
        if n['component'] is not None:
            for name,v in [('A',[7,6]),('B',[6,7]),('reverse_A',[-7,-6]),('reverse_B',[-6,-7])]:assert n['conditional_indices'][name]==np.array(n['relative_ab'])@v
    assert not g['closure']['identified'];assert g['closure']['count_candidates'] is None
    # Native provenance and noncollinear colored-only support for all new sites.
    black=read(FULL/'black-evidence.json');ctx={c['id']:c for c in read(FULL/'contexts.json')};blackfits=0
    for p in black['fresh_colored_only_context_predictions']:
        R=np.array(p['context_frame']);cen=np.array(p['context_center']);B=np.array(p['basis_local']);off=np.array(p['offset_local']);pred=R@(B@p['cell_ab']+off)+cen;assert np.max(abs(pred-p['predicted_xy']))<1e-8
        anchors=np.array([p['colored_assignments'][o] for o in p['colored_anchors']])-p['cell_ab'];assert np.linalg.matrix_rank(anchors)>=2
        for o,ab in p['colored_assignments'].items():assert op[o]['color'] in ['red','yellow'];assert np.linalg.norm(R@(B@ab+off)+cen-op[o]['xy'])<10+1e-8
        blackfits+=1
    model=read(FULL/'model-input.json');mids={o['id'] for o in model['observations'] if o.get('provisional')};assert not any({e['source'],e['target']}&mids for e in model['edges']);assert all(e['photographic_context']['status'] not in ['contested','ambiguous'] for e in model['edges'])
    # Fresh guarded replay. Only original scientific measurement inputs and the
    # new run's own outputs are allowed; historical result JSON is blocked.
    dest=Path(tempfile.mkdtemp(prefix='r326-guarded-'));code='''import sys,pathlib
from photo2.r326.runner import run,ROOT
out=pathlib.Path(sys.argv[1]);allowed={ROOT/'beads-photo-2.jpg',ROOT/'photo2/review/r275/inventory.json',ROOT/'photo2/spline-seed-r175.json'};reads=set()
def guard(event,args):
 if event!='open' or not isinstance(args[0],(str,bytes)):return
 p=pathlib.Path(args[0]).resolve()
 if ROOT in p.parents and p.suffix in ['.json','.jpg','.npz','.csv','.gz']:
  if p not in allowed:raise RuntimeError('Undeclared detector data input: '+str(p))
  reads.add(str(p.relative_to(ROOT)))
sys.addaudithook(guard);run(out);print('AUDITED_READS',sorted(reads))
'''
    replay_start=time.perf_counter();p=subprocess.run([sys.executable,'-c',code,str(dest)],cwd=ROOT,text=True,capture_output=True);(OUT/'guarded-replay.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
    for name in ['graph.json','observation-pixels.json','contexts.json','black-evidence.json','model-input.json']:
        actual=clean(read(FULL/name));repeat=clean(read(dest/name));assert actual==repeat,name
    # Baseline is exactly R325 apart from source/timing bookkeeping.
    replaybaseline=read(FULL/'baseline/graph.json')
    assert clean(replaybaseline)==clean(old)
    diff=subprocess.run(['git','diff','--name-only','00ad411f20bfb96da4ff2c22374a39e69abd578a','--','beads-photo-2.jpg','beads.pov','photo2/manual-labels-r161.json','photo2/r319','photo2/r320','photo2/r321','photo2/r322','photo2/r323','photo2/r324','photo2/r325'],cwd=ROOT,text=True,capture_output=True);assert diff.returncode==0 and not diff.stdout
    result=dict(passed=True,observations=len(op),original_observations=len(original),native_pixels=native,hypotheses=hypotheses,assignments=assignments,accepted_edges=edgeschecked,whole_hypothesis_equations=eq,colored_only_context_fits=blackfits,guarded_replay_seconds=time.perf_counter()-replay_start,guarded_directory=str(dest),seconds=time.perf_counter()-start,original_R325_exact=True,preserved_historical_paths=True,limitations='Independent arithmetic and exact original-pixel replay; not new human photographic truth. No full lattice, winding or repeating pattern certified.')
    save(OUT/'verification.json',result);print(result)
if __name__=='__main__':main()
