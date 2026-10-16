"""Independent source preservation, geometry, witnesses and native replay."""
from pathlib import Path
import subprocess,time
import numpy as np
from PIL import Image,ImageOps
from scipy.spatial import cKDTree
from photo2.r297.common import ROOT,read,save,sha
from photo2.r297.geometry import contact
from photo2.r295.geometry import AXES
from photo2.r295.physical_audit import independent_support
from photo2.r299.forward import Surface
from .geometry import Chain
from .evidence import load
from .objective import predict,match

def verify(out):
    out=Path(out);start=time.monotonic();data,m,obs=load();manifest=read(out/'export-manifest.json');receipts=[]
    models=[read(out/'exports'/f'{name}.json.gz') for name in manifest['models']]
    for model in models:
        t=time.monotonic();s=(Surface if model.get('historical') else Chain)(model['parameters'],data)
        from photo2.r297.geometry import reference
        strip_bound=float(cKDTree(reference().points).query(s.pc)[0].max()+s.query_radius)
        assert strip_bound<150.,'Projected body bound exceeds accelerated rendering strip'
        np.testing.assert_allclose(s.pc,[b['projected_center'] for b in model['positions']],rtol=0,atol=1e-9)
        np.testing.assert_allclose(s.centers,[b['center'] for b in model['positions']],rtol=0,atol=1e-10)
        if not model.get('historical'):
            from photo2.r297.geometry import reference
            u=np.linspace(0,reference().length,16385)[::8]
            axis=s.project(np.c_[s.spline(u),np.zeros(len(u))])
            np.testing.assert_allclose(axis,model['geometric_axis_xy'],rtol=0,atol=1e-9)
            np.testing.assert_allclose(axis[0],axis[-1],rtol=0,atol=1e-9)
        if model.get('historical'):
            identifier={'R297':'fixed-0-directional','R298-primary':'fixed-49-directional','R298-hand-plus-open':'fixed-29-directional','R298-hand-plus-closed':'fixed-76-directional','R299-primary':'joint-15'}[model['name']]
            historical=read(ROOT/f'photo2/r299/results/native-{identifier}.json.gz')
            np.testing.assert_allclose(s.pc,historical['positions'],rtol=0,atol=1e-9)
        assert len(s.indices)==model['parameters']['count']==len(model['positions'])
        cert=contact(s,exact=True);assert cert['certified']
        assert cert['pairs']==model['physical']['pairs']
        maximum=0.
        for w in model['physical']['witnesses']:
            a,b=w['pair'];v=np.asarray(w['normal'])
            gap=float((s.centers[b]-s.centers[a])@v-independent_support(v,s.g[AXES[0]][a],s.radius,s.axial)-independent_support(v,s.g[AXES[0]][b],s.radius,s.axial))
            maximum=max(maximum,abs(gap-w['gap_units']));assert gap>1e-6
        assert maximum<1e-9
        raster=np.load(out/'exports'/f'{model["name"]}-raster.npz');owner=raster['owner'];unknown=raster['unknown'];xy=raster['xy']
        sample=xy[np.linspace(0,len(xy)-1,min(20000,len(xy))).astype(int)];tr=s.trace(sample);ij=sample.astype(int)
        np.testing.assert_array_equal(tr['owner'],owner[ij[:,1],ij[:,0]]);np.testing.assert_array_equal(tr['unknown'],unknown[ij[:,1],ij[:,0]])
        # Probe outside the accelerated strip; no omitted body may own a ray.
        yy,xx=np.mgrid[0:3182:19,0:2540:19];grid=np.c_[xx.ravel(),yy.ravel()];d=s.tree.query(grid)[0];outside=grid[d>s.query_radius+1]
        assert np.all(s.trace(outside)['owner']<0)
        # Replay original support denominators against the native raster.
        from .export import complete_supports
        assert complete_supports(s,data,owner,unknown)==model['supports']
        receipts.append(dict(model=model['name'],positions=s.n,contacts=cert['pairs'],independent_witness_error=maximum,render_strip_bound_px=strip_bound,
            native_rays=len(sample),outside_acceleration_rays=len(outside),supports=len(model['supports']),seconds=time.monotonic()-t))
    primary=next(x for x in models if x['name']=='primary');s=Chain(primary['parameters'],data)
    # Resolution convergence at predetermined geographic strong observations.
    sample=[r for r in obs if r['strong']][::32];p1,_=predict(s,1.,sample);p2,meta=predict(s,.5,sample)
    one={p['index']:p for p in p1};two={p['index']:p for p in p2};common=sorted(set(one)&set(two));changes=[dict(index=k,centroid_change_px=float(np.linalg.norm(np.array(one[k]['point'])-two[k]['point']))) for k in common]
    numerical=dict(observations=[r['id'] for r in sample],common_lobes=len(common),changes=changes,
        median=float(np.median([r['centroid_change_px'] for r in changes])),maximum=float(np.max([r['centroid_change_px'] for r in changes])),
        native_only=sorted(set(one)-set(two)),half_only=sorted(set(two)-set(one)),half_numerics=meta,
        interpretation='Grid-sensitivity diagnostic, not statistical uncertainty. All N bodies occlude both predictions; no duplicated end guards.')
    save(out/'numerical.json',numerical)
    dense=Chain(primary['parameters'],data,resolution=32769);arcchange=float(np.max(np.linalg.norm(dense.pc-s.pc,axis=1)));assert arcchange<1e-4
    source=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');review=Image.open(out/'review/photo.png');assert np.array_equal(np.array(source),np.array(review))
    protected=read(ROOT/'photo2/r306/evidence/historical-sha256.json');modified=[];handoffs=[]
    for path,digest in protected.items():
        p=ROOT/path
        if not p.exists() or sha(p)!=digest:
            if path in ['AGENTS.md','PLAN.md','REQUEST_LOG.md','METHODS.md']:
                original=subprocess.check_output(['git','show',f'HEAD:{path}'],cwd=ROOT)
                if original not in p.read_bytes():raise AssertionError('Historical handoff text modified: '+path)
                handoffs.append(path)
            else:modified.append(path)
    assert not modified,modified
    result=dict(passed=True,models=receipts,arclength_resolution_max_pixel_change=arcchange,numerical=numerical,
        preserved_files=len(protected)-len(handoffs),additive_handoffs=handoffs,modified_historical_science=modified,
        original_photo_pixels_exact=True,seconds=time.monotonic()-start)
    save(out/'verification.json',result);print('R306 verification passed',len(models),'models',result['seconds'],'seconds',flush=True)
    return result

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('output',type=Path);verify(ap.parse_args().output)
