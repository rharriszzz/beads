"""Independent numerical replay; never rewrites any historical artifact."""
import time,subprocess
from copy import copy
import numpy as np
from PIL import Image
from photo2.r318 import optics
from photo2.r318.detect import linear
from photo2.r314.bright import components
from photo2.r295.geometry import Chain as Python,AXES
from photo2.r299.forward import Surface,shade
from photo2.r317.verify import independent_support
from photo2.r307.fast import grid
from .common import *
from .local_model import Chain
from .evidence import Evidence,gate
optics.Chain=Chain

def measured(xy,v,step=1):
    cs=components(xy,v,step=step)
    if not cs:return None
    return max(cs,key=lambda c:c['peak_intensity'])['weighted_centroid']

def main():
    began=time.time();epoch=read(OLD/'epoch2/epoch.json');photo=np.array(Image.open(ROOT/'beads-photo-2.jpg'));assert sha(ROOT/'beads-photo-2.jpg')==epoch['photo_sha256'];obschecks=[]
    for o in epoch['observations']:
        x,y,w,h=o['window'];yy,xx=np.mgrid[y:y+h,x:x+w];q=measured(np.c_[xx.ravel(),yy.ravel()],linear(photo[y:y+h,x:x+w]).min(2).ravel());np.testing.assert_allclose(q,o['point'],atol=1e-12,rtol=0);obschecks.append(o['id'])
    rows=[read(p) for p in sorted((OUT/'trials').glob('*.gz'))];checks=0
    for i,r in enumerate(rows):
        assert r['id']==i;assert r['epoch_binding']==epoch['binding']
        if not r.get('feasible'):continue
        assert {q['id']:q['index'] for q in r['rows']}==epoch['mapping'];assert len(r['rows'])==22
        errors=[]
        for q,o in zip(r['rows'],epoch['observations']):
            assert q['id']==o['id'] and q['observed']==o['point']
            if q['predicted'] is not None:
                d=float(np.hypot(q['predicted'][0]-q['observed'][0],q['predicted'][1]-q['observed'][1]));assert abs(d-q['error_px'])<1e-10;errors.append(d)
        assert r['missing']==22-len(errors)
        if r['missing']:assert r['emax_px'] is None and r['maximum_is_infinite']
        else:assert abs(max(errors)-r['emax_px'])<1e-10
        checks+=1
    # Independent bilateral arithmetic and SVD reconstruction.
    derivative_checks=0
    for stem in ['bilateral','small-local','narrow-patch']:
        doc=read(OUT/(stem+'-sensitivity.json.gz'));base=rows[doc['parent']]
        for z in doc['records']:
            for f in [.25,1.]:
                if str(f) not in z:continue
                a,b=[rows[z['trials'][str(s*f)]] for s in [-1,1]];expected=(positions(b)-positions(a))/(2*f);np.testing.assert_allclose(expected,z[str(f)]['central'],atol=1e-12,rtol=0);derivative_checks+=1
    svdchecks=0
    for path in OUT.glob('*minimax.json.gz'):
        z=read(path)
        if 'left_vectors' not in z:continue
        J=np.array(z['jacobian']);U=np.array(z['left_vectors']);S=np.array(z['singular_values']);V=np.array(z['right_vectors']);np.testing.assert_allclose((U*S)@V,J.reshape(-1,J.shape[2]),atol=1e-10,rtol=0);svdchecks+=1
    e=optics.Engine(epoch);ev=Evidence(epoch);baseline=read(OUT/'baseline.json.gz');selected=[('baseline',baseline),('best-full',read(OUT/'best-full.json.gz')),('best-small',read(OUT/'best-small.json.gz'))]
    # Include best numerical rejected step and a nonzero narrow-field setting.
    complete=[r for r in rows if r.get('feasible') and not r.get('missing')]
    selected.append(('reflection-only',min(complete,key=lambda r:r['emax_px'])))
    narrow=[r for r in complete if any(r['parameters'].get('patch_phase',[])) or any(r['parameters'].get('patch_tilt',[]))]
    if narrow:selected.append(('narrow-control',min(narrow,key=lambda r:max(r['rows'][i]['error_px'] for i in read(OUT/'small-selection.json')['chosen']['cohort']))))
    models=[]
    for name,saved in selected:
        r,s,a=e.evaluate(saved['parameters'],True);np.testing.assert_allclose(positions(r),positions(saved),atol=1e-9,rtol=0);assert s.n==2405
        m,ea=ev.measure(s,True);assert gate(m,baseline['geometry'])==gate(saved['geometry'],baseline['geometry']);cert=s.certify(iterations=220,witnesses=True);assert cert['certified']
        minimum=np.inf
        for w in cert['witnesses']:
            i,j=w['pair'];n=np.array(w['normal']);g=(s.centers[j]-s.centers[i])@n-independent_support(s,n,s.g[AXES[0]][i])-independent_support(s,-n,s.g[AXES[0]][j]);assert abs(g-w['gap_units'])<1e-9 and g>1e-6;minimum=min(minimum,g)
        ix=np.arange(0,len(a['xy']),23);xy=a['xy'][ix];py=Python.trace(s,xy,True);known=~py['unknown'];np.testing.assert_array_equal(py['owner'][known],a['owner'][ix][known]);valid=known&(py['owner']>=0);np.testing.assert_allclose(py['points'][valid],a['points'][ix][valid],atol=1e-7,rtol=0)
        assert np.max(np.linalg.norm(py['normal'][valid]-a['normal'][ix][valid],axis=1))<.002
        proxy=copy(s);proxy.blocked=lambda points,direction,max_distance=np.inf:Surface.blocked(proxy,points,direction,max_distance);sample={k:a[k][ix] for k in ['points','normal','viewer','owner','unknown']};sh=shade(proxy,sample,optics.make_light(s.p,s));assert abs(sh['intensity']-a['intensity'][ix]).max()<1e-10
        js=np.array([np.flatnonzero(s.indices==i)[0] for i in epoch['mapping'].values()]);hxy=grid(s,.5,js);htr=s.camera(hxy);hsh=shade(s,htr,optics.make_light(s.p,s));half=[];lobes=[]
        for row in r['rows']:
            j=int(np.flatnonzero(s.indices==row['index'])[0]);mask=htr['owner']==j;q=measured(hxy[mask],hsh['intensity'][mask],.5);half.append(dict(id=row['id'],predicted=q,error_px=float(np.linalg.norm(np.array(q)-row['observed'])) if q else None,native_shift_px=float(np.linalg.norm(np.array(q)-row['predicted'])) if q else None))
            mask=a['owner']==j;cc=components(a['xy'][mask],a['intensity'][mask]);lobes.append(dict(id=row['id'],index=row['index'],components=[{k:v for k,v in c.items() if k not in ['pixels','intensities','near_maximum']} for c in cc]))
        np.savez_compressed(OUT/(name+'-optics.npz'),**a);np.savez_compressed(OUT/(name+'-visible.npz'),**ea)
        save(OUT/(name+'-geometry.json'),m);save(OUT/(name+'-contacts.json.gz'),cert);save(OUT/(name+'-positions.json.gz'),dict(indices=s.indices.tolist(),centers=s.centers.tolist(),projected=s.pc.tolist(),frames={k:s.g[k].tolist() for k in AXES}));save(OUT/(name+'-half-pixel.json'),half);save(OUT/(name+'-lobes.json'),lobes)
        models.append(dict(name=name,trial=saved['id'],emax=r['emax_px'],half_pixel_emax=max(z['error_px'] for z in half if z['error_px'] is not None),half_pixel_missing=sum(z['predicted'] is None for z in half),maximum_half_pixel_shift=max(z['native_shift_px'] for z in half if z['native_shift_px'] is not None),witnesses=len(cert['witnesses']),minimum_support_margin=float(minimum),independent_camera_rays=len(ix),unknown_python_rays=int(py['unknown'].sum()),shadow_samples=len(ix),shadow_unknown_pairs=sh['unknown_shadow_pairs'],acceptance=gate(m,baseline['geometry'])))
        print('VERIFIED MODEL',name,saved['id'],r['emax_px'],flush=True)
    changed=subprocess.check_output(['git','diff','--diff-filter=MDRT','--name-only','18d953b380fe5e89461fe0582dcb2b846eea314d'],text=True).splitlines();assert not changed,changed
    save(OUT/'verification.json',dict(passed=True,utc=utc(),seconds=time.time()-began,observations=len(obschecks),all_trial_count=len(rows),feasible_cohort_max_checks=checks,central_derivative_checks=derivative_checks,svd_checks=svdchecks,models=models,photo_sha256=sha(ROOT/'beads-photo-2.jpg'),historical_tracked_changes=changed,sources={str(p.relative_to(ROOT)):sha(p) for p in (OUT.parent).glob('*.py')}))
    print('VERIFIED',len(rows),time.time()-began,flush=True)
if __name__=='__main__':main()
