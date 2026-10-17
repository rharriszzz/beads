"""Independent original-Python rays, analytic supports, centers and preservation."""
from pathlib import Path
from types import MethodType
import subprocess,time,json
import numpy as np
from scipy.spatial import cKDTree
from PIL import Image,ImageOps
from photo2.r297.common import ROOT,read,save,sha,digest,utc
from photo2.r306.evidence import load
from photo2.r306.geometry import Chain as Original
from photo2.r299.forward import Surface
from photo2.r295.geometry import AXES
from photo2.r295.physical_audit import independent_support
from photo2.r309.render import predict
from photo2.r309.measure import distances,reference_dimension
from .model import starts,scene,VARIABLES
from .diagnostics import FirstErrors
from .search import sources

def native_segments_audit(model,raster):
    owner=raster['owner'];unknown=raster['unknown'];total=0;unit_edges=0
    for j,b in enumerate(model['positions']):
        for x,y,u,v in b['boundary_segments']:
            # Each merged edge must have this body on exactly one side at every
            # native cell; no assumption about convexity or missing inner holes.
            if y==v:
                xs=np.arange(round(x+.5),round(u+.5));ya=int(round(y-.5));yb=ya+1
                a=(owner[ya,xs]==j)&~unknown[ya,xs] if 0<=ya<3182 else np.zeros(len(xs),bool)
                z=(owner[yb,xs]==j)&~unknown[yb,xs] if 0<=yb<3182 else np.zeros(len(xs),bool)
            else:
                ys=np.arange(round(y+.5),round(v+.5));xa=int(round(x-.5));xb=xa+1
                a=(owner[ys,xa]==j)&~unknown[ys,xa] if 0<=xa<2540 else np.zeros(len(ys),bool)
                z=(owner[ys,xb]==j)&~unknown[ys,xb] if 0<=xb<2540 else np.zeros(len(ys),bool)
            assert len(a)>0 and np.all(a^z),(model['name'],b['index'],[x,y,u,v])
            total+=1;unit_edges+=int(round(abs(u-x)+abs(v-y)))
    effective=np.where(unknown,-1,owner);expected=0
    for a,b in [(effective[1:],effective[:-1]),(effective[:,1:],effective[:,:-1])]:
        change=a!=b;expected+=int(np.sum(change&(a>=0))+np.sum(change&(b>=0)))
    expected+=sum(int(np.sum(z>=0)) for z in [effective[0],effective[-1],effective[:,0],effective[:,-1]])
    assert unit_edges==expected,(model['name'],unit_edges,expected)
    return total

def run(out):
    out=Path(out);began=time.monotonic();data,m,obs=load();items=read(out/'selection.json')['models'];results=[]
    D=reference_dimension(m)['D_px'];assert D==read(out/'D.json')['D_px']
    for item in items:
        name=item['name'];model=read(out/'exports'/f'{name}.json.gz');p=model['parameters'];s=scene(p,data,item['implementation'])
        np.testing.assert_allclose(s.centers,[b['center'] for b in model['positions']],atol=1e-10,rtol=0)
        frame=np.stack([s.g[k] for k in AXES],axis=1)
        np.testing.assert_allclose(frame@np.swapaxes(frame,1,2),np.broadcast_to(np.eye(3),frame.shape),atol=1e-12,rtol=0)
        assert np.min(np.linalg.det(frame))>1-1e-12
        arcdelta=None
        if item['implementation']!='R297':
            from photo2.r309.geometry import Chain as Modern
            finer=Modern(p,data,resolution=32769);arcdelta=float(np.linalg.norm(finer.pc-s.pc,axis=1).max());assert arcdelta<1e-4
            assert finer.certify(iterations=220,witnesses=False)['certified']
            old=Original(p,data);height=(old.project(old.line)[:,1]-1591)/1591
            expected=old.line+p['minor']*(1+p.get('minor_y',0)*height)[:,None]*old.g['radial']
            np.testing.assert_allclose(s.centers,expected,atol=1e-11,rtol=0)
        gaps=[]
        pairs=cKDTree(s.centers).query_pairs(2*s.bound+1e-8,output_type='ndarray')
        witness={tuple(w['pair']):w for w in model['physical']['witnesses']}
        assert len(pairs)==len(witness)
        for a,b in pairs:
            w=witness[(int(a),int(b))];n=np.array(w['normal'])
            gap=float((s.centers[b]-s.centers[a])@n-independent_support(n,s.g[AXES[0]][a],s.radius,s.axial)-independent_support(n,s.g[AXES[0]][b],s.radius,s.axial))
            assert gap>0 and abs(gap-w['gap_units'])<1e-8;gaps.append(gap)
        raster=np.load(out/'exports'/f'{name}-raster.npz');xy=raster['xy'];idx=np.linspace(0,len(xy)-1,min(12000,len(xy))).astype(int);sample=xy[idx]
        viewer=ROOT/'photo2/review/r311'
        bodytext=(viewer/f'{name}.js').read_text();prefix='window.R311LoadedModel='
        assert bodytext.startswith(prefix)
        body=json.loads(bodytext[len(prefix):].strip().removesuffix(';'))
        assert body['positions']==model['positions'] and body['parameters']==p and body['first_errors']==model['first_errors']
        encoded=np.asarray(Image.open(viewer/f'{name}-owners.png')).astype(np.int32)
        decoded=encoded[:,:,0]+256*encoded[:,:,1]-32768
        np.testing.assert_array_equal(decoded,raster['address'])
        first=FirstErrors(data);sample=np.vstack([sample,*first.parts])
        s.trace=MethodType(Original.trace,s);s.blocked=MethodType(Surface.blocked,s)
        tr=s.trace(sample);ij=sample.astype(int)
        np.testing.assert_array_equal(tr['owner'],raster['owner'][ij[:,1],ij[:,0]])
        np.testing.assert_array_equal(tr['unknown'],raster['unknown'][ij[:,1],ij[:,0]])
        # Each reported local denominator and isolated-candidate body is checked
        # against the original marcher (no compiled bound methods on shallow copies).
        from copy import copy
        localrays=0
        for target,pts in zip(model['first_errors'],first.parts):
            original=next(r for r in data['rows'] if r['id']==target['id'] and r['kind']=='region')
            assert target['photographic_runs']==original['pixels']['runs']
            own=s.trace(pts);localrays+=len(pts)
            if target['modal_index'] is not None:
                j=int(np.searchsorted(s.indices,target['modal_index']))
                assert abs(np.mean((own['owner']==j)&~own['unknown'])-target['modal_fraction'])<1e-12
            for alt in target['isolated_candidates']:
                j=int(np.searchsorted(s.indices,alt['index']));one=copy(s);one.n=1;one.indices=s.indices[j:j+1];one.centers=s.centers[j:j+1];one.pc=s.pc[j:j+1];one.g={k:v[j:j+1] for k,v in s.g.items()};one.tree=cKDTree(one.pc)
                one.trace=MethodType(Original.trace,one);hit=one.trace(pts);localrays+=len(pts)
                assert abs(np.mean((hit['owner']>=0)&~hit['unknown'])-alt['isolated_fraction'])<1e-12
        # Independently recompute Euclidean metrics and missing denominators.
        metric=read(out/'metrics'/f'{name}.json.gz')
        for split,record in metric['detail'].items():
            for r in record['reflections']:
                if r['predicted'] is not None:assert abs(np.linalg.norm(np.array(r['predicted'])-r['observed'])-r['error_px'])<1e-10
            calc=distances(record['reflections'],D)
            for k in ['rms_D','maximum_D','p95_D','missing']:assert calc[k]==record['metrics']['reflection'][k]
        optical=0
        if not item['baseline'] or name.startswith('R297'):
            chosen=[r for r in obs if r['strong']][::100]
            fast,meta=predict(scene(p,data,item['implementation']),1.,chosen);slow,smeta=predict(s,1.,chosen)
            a={r['index']:r for r in fast};b={r['index']:r for r in slow};assert set(a)==set(b)
            for k in a:np.testing.assert_allclose(a[k]['point'],b[k]['point'],atol=1e-9,rtol=0)
            optical=smeta['rays']
        boundaries=native_segments_audit(model,raster)
        results.append(dict(name=name,positions=s.n,contact_pairs=len(gaps),minimum_independent_margin=min(gaps),original_rays=len(sample)+localrays,original_optical_rays=optical,boundary_segments=boundaries,arclength_refinement_max_px=arcdelta,right_handed_orthonormal_frames=True))
        print('verified original kernel',name,flush=True)
    seeds={s['name']:s for s in starts()};keys=set();trialcount=0
    for file in sorted((out/'trials').glob('*.gz')):
        row=read(file);trialcount+=1;key=row['key'];assert key not in keys;keys.add(key)
        seed=seeds[row['family']]
        for k,v in row['parameters'].items():
            if k not in VARIABLES:assert v==seed['parameters'][k],(file,k)
        if row['feasible']:assert row['physical']['certified'] and row['result']['D_px']==D
        else:assert row['status']!='feasible'
    review=ROOT/'photo2/review/r311';photo=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB')
    assert np.array_equal(photo,Image.open(review/'photo.png'))
    for row in read(out/'atlas.json'):assert np.array_equal(photo.crop(row['crop']),Image.open(review/row['raw']))
    pairfile=ROOT/'photo2/r311/evidence/phase-registration-example.json';pairrays=0
    if pairfile.exists():
        example=read(pairfile);crop=example['crop'];raw=Image.open(pairfile.with_name('phase-registration-raw.png'))
        assert np.array_equal(photo.crop(crop),raw)
        figure=np.asarray(Image.open(pairfile.with_suffix('.png')))
        np.testing.assert_array_equal(figure[50:310:2,:500:2],np.asarray(raw))
        yy,xx=np.mgrid[crop[1]:crop[3],crop[0]:crop[2]];xy=np.c_[xx.ravel(),yy.ravel()]
        for ident in [example['baseline_trial'],example['after_trial']]:
            row=read(out/'trials'/f'{ident:06d}.json.gz');s=scene(row['parameters'],data,row['implementation']);fast=s.trace(xy)
            s.trace=MethodType(Original.trace,s);slow=s.trace(xy)
            np.testing.assert_array_equal(fast['owner'],slow['owner']);np.testing.assert_array_equal(fast['unknown'],slow['unknown']);pairrays+=len(xy)
    protected=read(ROOT/'photo2/r311/evidence/preservation.json.gz');head=read(ROOT/'photo2/r311/evidence/start.json')['head'];additive=[]
    for p,h in protected.items():
        if sha(ROOT/p)!=h:
            assert p in ['AGENTS.md','PLAN.md','METHODS.md','REQUEST_LOG.md','SESSION_HANDOFF.md','.gitignore'],p
            before=subprocess.check_output(['git','show',head+':'+p]);assert before in (ROOT/p).read_bytes(),p
            additive.append(p)
    save(out/'source-manifest.json',sources())
    if (out/'coupled-4d.json').exists():
        assert read(out/'coupled-4d.json')['source_sha256']==sha(ROOT/'photo2/r311/coupled_refine.py')
    delivery_sources=list((ROOT/'photo2/r311').glob('*.py'))+[ROOT/'photo2/r311/viewer.html',ROOT/'photo2/R311_SPECIFICATION.md',ROOT/'photo2/R311_REPRODUCE.md']
    save(out/'delivery-source-manifest.json',{str(p.relative_to(ROOT)):sha(p) for p in delivery_sources})
    result=dict(passed=True,utc=utc(),models=results,positions=sum(r['positions'] for r in results),contact_pairs=sum(r['contact_pairs'] for r in results),original_native_rays=sum(r['original_rays'] for r in results)+pairrays,original_pair_figure_rays=pairrays,original_optical_rays=sum(r['original_optical_rays'] for r in results),native_boundary_segments=sum(r['boundary_segments'] for r in results),unique_trial_vectors=trialcount,frozen_fields_exact=True,complete_boundary_unit_edges=True,all_viewer_positions_parameters_and_native_owners_exact=True,D_px=D,preserved_files=len(protected),additive_handoffs=additive,historical_science_changed=[],raw_photo_and_atlas_exact=True,seconds=time.monotonic()-began)
    save(out/'verification.json',result);return result
