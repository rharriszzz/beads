"""Independent photographic components, Python rays, support and minimax audit."""
import time,subprocess
from copy import copy
import numpy as np
from PIL import Image
from photo2.r297.common import ROOT,read,save,sha,digest,utc
from photo2.r295.geometry import Chain as Python,AXES,unit
from photo2.r299.forward import Surface,shade,light_params
from photo2.r314.bright import components
from photo2.r307.fast import grid
from photo2.r317.verify import independent_support
from .detect import OUT,linear
from .optics import Engine,Chain,make_light

def measure(xy,v,step=1):
    cc=components(xy,v,step=step)
    if not cc:return None
    # Spatial scan order fixes exact ties, as in the production lattice.
    c=max(cc,key=lambda c:c['peak_intensity'])
    return c['weighted_centroid']

def main():
    began=time.time();photo=np.array(Image.open(ROOT/'beads-photo-2.jpg'));obsdoc=read(OUT/'observations.json.gz')
    assert sha(ROOT/'beads-photo-2.jpg')==obsdoc['photo_sha256'];observed_checks=[];models=[];trial_checks=0
    for folder in [OUT,OUT/'epoch2']:
        if not (folder/'best.json.gz').exists():continue
        epoch=read(folder/'epoch.json');assert len(epoch['mapping'])==len(set(epoch['mapping'].values()))
        assert epoch['binding']==digest(dict(observations=epoch['observations'],mapping=epoch['mapping'],method=epoch['method']))
        for path in sorted((folder/'trials').glob('*.gz')):
            trial=read(path);assert trial['epoch_binding']==epoch['binding']
            if trial['feasible']:
                assert len(trial['rows'])==len(epoch['observations'])
                assert {r['id']:r['index'] for r in trial['rows']}==epoch['mapping']
                errors=[]
                for r in trial['rows']:
                    obs=next(o for o in epoch['observations'] if o['id']==r['id']);assert r['observed']==obs['point']
                    if r['predicted'] is not None:
                        error=float(np.linalg.norm(np.array(r['predicted'])-r['observed']));assert abs(error-r['error_px'])<1e-10;errors.append(error)
                assert trial['missing']==len(epoch['observations'])-len(errors)
                if not trial['missing']:assert abs(max(errors)-trial['emax_px'])<1e-10
                else:assert trial['maximum_is_infinite'] and trial['emax_px'] is None
            trial_checks+=1
        for o in epoch['observations']:
            x,y,w,h=o['window'];crop=photo[y:y+h,x:x+w];yy,xx=np.mgrid[y:y+h,x:x+w];xy=np.c_[xx.ravel(),yy.ravel()]
            v=linear(crop).min(2).ravel();q=measure(xy,v)
            np.testing.assert_allclose(q,o['point'],atol=1e-12,rtol=0)
            assert o['silhouette_distance_px']>=11
            observed_checks.append(o['id'])
        engine=Engine(epoch)
        for name in ['baseline','best']:
            saved=read(folder/f'{name}.json.gz');result,s,a=engine.evaluate(saved['parameters'],True)
            np.testing.assert_allclose([r['error_px'] for r in saved['rows']],[r['error_px'] for r in result['rows']],atol=1e-9,rtol=0)
            distances=np.linalg.norm(np.array([r['predicted'] for r in result['rows']])-np.array([r['observed'] for r in result['rows']]),axis=1)
            assert abs(float(distances.max())-saved['emax_px'])<1e-10 and result['missing']==0
            assert s.n==2405
            cert=s.certify(iterations=220,witnesses=True);assert cert['certified'];minimum=1e6
            for w in cert['witnesses']:
                i,j=w['pair'];n=np.array(w['normal']);gap=(s.centers[j]-s.centers[i])@n-independent_support(s,n,s.g[AXES[0]][i])-independent_support(s,-n,s.g[AXES[0]][j])
                assert abs(gap-w['gap_units'])<1e-9 and gap>1e-6;minimum=min(minimum,gap)
            # Independent Python marching and a different finite-difference normal step.
            ix=np.arange(0,len(a['xy']),11);xy=a['xy'][ix];parts=[Python.trace(s,xy[i:i+2000],True) for i in range(0,len(xy),2000)]
            py={k:np.concatenate([p[k] for p in parts]) for k in ['owner','unknown','points','normal']};known=~py['unknown']
            np.testing.assert_array_equal(py['owner'][known],a['owner'][ix][known]);valid=known&(py['owner']>=0)
            np.testing.assert_allclose(py['points'][valid],a['points'][ix][valid],atol=1e-7,rtol=0)
            normal_error=float(np.max(np.linalg.norm(py['normal'][valid]-a['normal'][ix][valid],axis=1))) if valid.any() else 0
            assert normal_error<.002
            # Shadow/BRDF replay through original uncompiled complete-chain rays.
            proxy=copy(s);proxy.blocked=lambda points,direction,max_distance=np.inf:Surface.blocked(proxy,points,direction,max_distance)
            sample={k:a[k][ix] for k in ['points','normal','viewer','owner','unknown']}
            light=make_light(s.p,s)
            sh=shade(proxy,sample,light);delta=np.abs(sh['intensity']-a['intensity'][ix]);assert delta.max()<1e-10
            half=None
            if name=='best':
                js=np.array([np.flatnonzero(s.indices==i)[0] for i in epoch['mapping'].values()]);hxy=grid(s,.5,js);htr=s.camera(hxy);hsh=shade(s,htr,light);hh=[]
                for o in epoch['observations']:
                    j=int(np.flatnonzero(s.indices==epoch['mapping'][o['id']])[0]);keep=htr['owner']==j;q=measure(hxy[keep],hsh['intensity'][keep],.5)
                    hh.append(dict(id=o['id'],point=q,error_px=float(np.linalg.norm(np.array(q)-o['point'])) if q else None,
                                   native_shift_px=float(np.linalg.norm(np.array(q)-next(r['predicted'] for r in result['rows'] if r['id']==o['id']))) if q else None))
                half=dict(rows=hh,missing=sum(r['point'] is None for r in hh),emax_px=max(r['error_px'] for r in hh if r['error_px'] is not None),maximum_native_shift_px=max(r['native_shift_px'] for r in hh if r['native_shift_px'] is not None),unknown_camera=int(htr['unknown'].sum()),unknown_shadow=hsh['unknown_shadow_pairs'])
                save(folder/'half-pixel.json',half)
                save(folder/'contacts.json.gz',cert)
                np.savez_compressed(folder/'best-optics.npz',**a)
                save(folder/'positions.json.gz',dict(indices=s.indices.tolist(),centers=s.centers.tolist(),frames={k:s.g[k].tolist() for k in AXES}))
            models.append(dict(epoch=epoch['id'],model=name,exact_maximum_px=saved['emax_px'],full_chain_witnesses=len(cert['witnesses']),minimum_support_margin=minimum,independent_camera_rays=len(ix),unresolved_python_camera=int(py['unknown'].sum()),normal_max_difference=normal_error,shadow_samples=len(ix),shadow_intensity_max_difference=float(delta.max()),original_unknown_shadow_pairs=sh['unknown_shadow_pairs'],half_pixel=half))
    base='b648d419809e2929c7ccafdb6ed643bbf53f3871';changed=subprocess.check_output(['git','diff','--diff-filter=MDRT',base,'--name-only'],text=True).splitlines()
    allowed=['AGENTS.md','PLAN.md','REQUEST_LOG.md','SESSION_HANDOFF.md']
    for path in changed:
        assert path in allowed,path
        assert subprocess.check_output(['git','show',base+':'+path]) in (ROOT/path).read_bytes()
    save(OUT/'verification.json',dict(passed=True,utc=utc(),seconds=time.time()-began,observed_component_checks=len(observed_checks),all_trial_cohort_and_maximum_checks=trial_checks,models=models,historical_changes=changed,photo_unchanged=True,source_hashes={str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'photo2/r318').glob('*.py'))}))
    print('VERIFIED',len(models),'models',len(observed_checks),'observations',time.time()-began,flush=True)

if __name__=='__main__':main()
