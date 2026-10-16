"""Independent contact witnesses, native replays, frozen evidence and preservation."""
from pathlib import Path
from copy import deepcopy
from time import monotonic
import numpy as np
from .calibrate import *
from .refine import dimension_loss
from .photometry import PhotoScore
from .fft import diagnostic
from photo2.r297.common import pixels,photo,environment

def main():
    start=monotonic();data,_=load_evidence();m=measurements();manifest=read(BASE/'results/export-manifest.json');h=read(BASE/'results/refinement-history.json.gz');rgb,_,_=photo();checks=[]
    protected=read(BASE/'evidence/preservation.json.gz');changed=[p for p,v in protected.items() if not (ROOT/p).exists() or sha(ROOT/p)!=v]
    assert not changed,changed
    assert sha(ROOT/'photo2/review/r298/original.jpg')==sha(ROOT/'beads-photo-2.jpg')
    for path,value in read(BASE/'evidence/freeze.json')['files'].items():assert sha(ROOT/path)==value,path
    # Every retained control's structural objective is regenerated, not just its winner.
    for row in h:
        scene,poly,bd,en=prediction(row['parameters'],data,m)
        np.testing.assert_allclose(bd,row['beads'],atol=1e-9,rtol=0);np.testing.assert_allclose(en,row['envelope'],atol=1e-9,rtol=0)
        assert abs(dimension_loss(bd,en,m)-row['dimension_loss'])<1e-10
        c=contact(scene);assert c==row['physical']
    obj=PhotoScore(data)
    for ident in manifest['ids']:
        result=read(BASE/f'results/model-{ident}.json.gz');scene=Chain(result['parameters'],data);native=np.load(BASE/f'results/native-{ident}.npz')
        np.testing.assert_array_equal(scene.pc,result['positions']);np.testing.assert_array_equal(scene.centers,result['world_centers']);cert=contact(scene,exact=True);assert cert==result['contact']
        ix=np.linspace(0,len(native['xy'])-1,8000).astype(int);rays=scene.trace(native['xy'][ix]);np.testing.assert_array_equal(rays['owner'],native['owner'][ix]);np.testing.assert_array_equal(rays['unknown'],native['unknown'][ix])
        sources={r['id']:r for r in data['rows']}
        for row in result['observations'][::37]:
            tr=scene.trace(pixels(sources[row['id']]['pixels']));ids,counts=np.unique(tr['owner'][tr['owner']>=0],return_counts=True);frac=float(counts.max()/len(tr['owner'])) if len(counts) else 0.
            assert frac==row['fraction']
        photo_result=obj.assess(scene);assert photo_result==result['photographic']['development'];assert photo_result==h[ident]['photographic']
        assert diagnostic(scene)==read(BASE/f'results/fft-{ident}.json')
        checks.append(dict(model=ident,positions=scene.n,contact_pairs=cert['pairs'],native_rays_replayed=len(ix),native_supports_replayed=len(result['observations'][::37]),rays_exported=result['native_rays'],unknown_exported=result['native_unknown']))
    # Exact deterministic solver replay of the crucial free-camera control.
    shape=fit(read(BASE/'results/baseline.json')['parameters'],data,m,'shape',max_nfev=35)
    saved=read(BASE/'results/control-camera-roll.json.gz');assert shape['parameters']==saved['parameters'];assert shape['history']==saved['history']
    evidence=[]
    for row in m['envelope']:
        xy=np.array(row['samples_xy']);np.testing.assert_array_equal(rgb[xy[:,1],xy[:,0]],row['samples_rgb'])
    from .serve import open_browser
    save(BASE/'results/verification.json',dict(preserved=len(protected),changed=changed,full_refinement_replays=len(h),selected_replays=checks,measurement_profiles=len(m['envelope']),solver_replay_evaluations=len(shape['history']),native_photo_exact=True,fft_replays=len(checks),environment=environment(),elapsed=monotonic()-start,limitations='Floating-point separation certificates; no interval proof. Photographic labels and physical identities remain uncertain.'))
    print('R298 preservation and numerical replays passed',checks,flush=True)
if __name__=='__main__':main()
