"""Original marcher, independent frame construction, contacts and photo invariance."""
from pathlib import Path
from types import MethodType
import time,subprocess
import numpy as np
from PIL import Image,ImageOps
from photo2.r297.common import ROOT,read,save,sha
from photo2.r306.evidence import load
from photo2.r306.geometry import Chain as Original
from photo2.r299.forward import Surface
from photo2.r295.geometry import AXES
from photo2.r295.physical_audit import independent_support
from .geometry import Chain
from .render import predict
from .measure import reference_dimension,distances

def verify(out):
    out=Path(out);began=time.monotonic();data,m,obs=load();results=[];D=reference_dimension(m)['D_px'];assert D==read(out/'D.json')['D_px']
    models=read(out/'selection.json')['models']
    for item in models:
        model=read(out/'exports'/f"{item['name']}.json.gz");p=model['parameters'];scene=Chain(p,data);old=Original(p,data)
        y=(old.project(old.line)[:,1]-1591)/1591;expected=old.line+p['minor']*(1+p.get('minor_y',0)*y)[:,None]*old.g['radial'];np.testing.assert_allclose(scene.centers,expected,atol=1e-11)
        angle=np.radians(p.get('tilt_y',0)*y+p.get('tilt_y2',0)*(y*y-1/3));a,b=old.g[AXES[0]],old.g[AXES[2]]
        np.testing.assert_allclose(scene.g[AXES[0]],np.cos(angle)[:,None]*a+np.sin(angle)[:,None]*b,atol=1e-12)
        np.testing.assert_allclose([b['center'] for b in model['positions']],scene.centers,atol=1e-10)
        cert=scene.certify(iterations=180,witnesses=False);assert cert['certified'];assert cert['pairs']==model['physical']['pairs'];assert scene.closure()['axis_storage_position_gap']<1e-8
        gaps=[]
        for w in model['physical']['witnesses']:
            a,b=w['pair'];v=np.array(w['normal']);gap=(scene.centers[b]-scene.centers[a])@v-independent_support(v,scene.g[AXES[0]][a],scene.radius,scene.axial)-independent_support(v,scene.g[AXES[0]][b],scene.radius,scene.axial);assert gap>=-1e-8;assert abs(gap-w['gap_units'])<1e-8;gaps.append(gap)
        raster=np.load(out/'exports'/f"{item['name']}-raster.npz");xy=raster['xy'];ix=np.linspace(0,len(xy)-1,min(15000,len(xy))).astype(int);sample=xy[ix];scene.trace=MethodType(Original.trace,scene);scene.blocked=MethodType(Surface.blocked,scene);tr=scene.trace(sample);ij=sample.astype(int);np.testing.assert_array_equal(tr['owner'],raster['owner'][ij[:,1],ij[:,0]]);np.testing.assert_array_equal(tr['unknown'],raster['unknown'][ij[:,1],ij[:,0]])
        # Independent Euclidean residual arithmetic, including exact maximum.
        detail=read(out/'metrics'/f"{item['name']}.json.gz")
        for split,record in detail.items():
            for r in record['reflections']:
                if r['predicted'] is not None:assert abs(np.linalg.norm(np.array(r['predicted'])-r['observed'])-r['error_px'])<1e-10
            calculated=distances(record['reflections'],D);assert abs(calculated['maximum_D']-record['metrics']['reflection']['maximum_D'])<1e-12
        optical_rays=0
        if item['name'] in ['primary','R309-reflection']:
            sample_obs=[r for r in obs if r['strong']][::90]
            fast_pred,fast_meta=predict(Chain(p,data),1.,sample_obs);original_pred,original_meta=predict(scene,1.,sample_obs)
            a={r['index']:r for r in fast_pred};b={r['index']:r for r in original_pred};assert set(a)==set(b)
            for k in a:np.testing.assert_allclose(a[k]['point'],b[k]['point'],atol=1e-8,rtol=0)
            optical_rays=original_meta['rays']
        results.append(dict(original_optical_rays=optical_rays,model=item['name'],positions=scene.n,physical_pairs=len(gaps),minimum_independent_margin=min(gaps),original_native_rays=len(sample),passed=True))
        print('independent R309 model',item['name'],flush=True)
    primary=read(out/'exports/primary.json.gz');s=Chain(primary['parameters'],data);ss=Chain(primary['parameters'],data,32769);delta=float(np.linalg.norm(s.pc-ss.pc,axis=1).max());assert delta<1e-4
    yy,xx=np.mgrid[246:426,1020:1200];xy=np.c_[xx.ravel(),yy.ravel()];s.trace=MethodType(Original.trace,s);tr=s.trace(xy);raster=np.load(out/'exports/primary-raster.npz');np.testing.assert_array_equal(tr['owner'].reshape(xx.shape),raster['owner'][yy,xx]);np.testing.assert_array_equal(tr['unknown'].reshape(xx.shape),raster['unknown'][yy,xx])
    # Optical half-grid controls at dispersed observations, not selected for fit.
    selected=[r for r in obs if r['strong']][::30];native,meta=predict(Chain(primary['parameters'],data),1.,selected);half,hmeta=predict(Chain(primary['parameters'],data),.5,selected);lookup={p['index']:p for p in half};changes=[dict(id=p['index'],point=p['point'],error_px=float(np.linalg.norm(np.array(p['point'])-lookup[p['index']]['point'])),ambiguous=True) for p in native if p['index'] in lookup]
    numeric=dict(displacement=distances(changes,D),native_only=[p['index'] for p in native if p['index'] not in lookup],half_only=[p['index'] for p in half if p['index'] not in {r['index'] for r in native}],native=meta,half=hmeta,policy='Grid sensitivity, not uncertainty or fitting. Entire necklace occludes all selected owners.');save(out/'numerical.json',numeric)
    original=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');review=Image.open(out/'review/photo.png');assert np.array_equal(original,review)
    if (out/'atlas.json').exists():
        for a in read(out/'atlas.json'):
            raw=Image.open(out/'review'/a['raw']);assert np.array_equal(np.asarray(raw),np.asarray(original.crop(a['crop'])))
    protected=read(ROOT/'photo2/r309/evidence/preservation.json.gz');changed=[];allowed=[]
    for p,h in protected.items():
        if not (ROOT/p).exists() or sha(ROOT/p)!=h:
            if p in ['AGENTS.md','PLAN.md','METHODS.md','REQUEST_LOG.md']:
                old=subprocess.check_output(['git','show',read(ROOT/'photo2/r309/evidence/start.json')['head']+':'+p]);assert old in (ROOT/p).read_bytes();allowed.append(p)
            else:changed.append(p)
    assert not changed,changed
    result=dict(passed=True,models=results,positions=sum(r['positions'] for r in results),contact_witnesses=sum(r['physical_pairs'] for r in results),original_rays=sum(r['original_native_rays'] for r in results),required_location_rays=len(xy),arclength_refinement_max_px=delta,photo_exact=True,atlas_raw_exact=True,D_px=D,preserved_files=len(protected),additive_handoffs=allowed,modified_historical_science=changed,seconds=time.monotonic()-began)
    save(out/'verification.json',result);return result


def boundary_audit(out):
    """Every saved viewer segment is the boundary of its native first-hit owner."""
    from photo2.r305.forward import segments
    out=Path(out);data,_,_=load();rows=[]
    for item in read(out/'selection.json')['models']:
        model=read(out/'exports'/f"{item['name']}.json.gz");scene=Chain(model['parameters'],data);owner=np.load(out/'exports'/f"{item['name']}-raster.npz")['owner'];count=0
        for b in model['positions']:
            j=b['index']-int(scene.indices[0]);x,y=b['projected_center'];rad=scene.query_radius+2;x0=max(0,int(x-rad));x1=min(2540,int(x+rad)+2);y0=max(0,int(y-rad));y1=min(3182,int(y+rad)+2)
            actual=segments(owner[y0:y1,x0:x1]==j,x0,y0);assert actual==b['boundary_segments'];count+=len(actual)
        rows.append(dict(model=item['name'],positions=scene.n,boundary_segments_exact=count))
    result=dict(passed=True,models=rows,boundary_segments_exact=sum(r['boundary_segments_exact'] for r in rows));save(out/'boundary-verification.json',result);return result

if __name__=='__main__':
    import sys
    verify(Path(sys.argv[1]));boundary_audit(Path(sys.argv[1]))
