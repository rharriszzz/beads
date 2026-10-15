"""Native replay and prior-science preservation; writes only R297 receipts."""
import numpy as np
from .common import *
from .geometry import Chain,contact


def main():
    old=read(BASE/'evidence/preservation.json.gz');allowed={'photo2/phase2_autofit.py'}
    changed=[p for p,h in old.items() if p not in allowed and (not (ROOT/p).exists() or sha(ROOT/p)!=h)]
    if changed:raise AssertionError(changed)
    data,_=load_evidence();out=BASE/'results/pilot';manifest=read(out/'exports/manifest.json');checks=[]
    native,_,_=photo()
    from PIL import Image
    np.testing.assert_array_equal(np.asarray(Image.open(out/'review/original.png')),native)
    for identifier in manifest['ids']:
        model=read(out/f'exports/model-{identifier}.json.gz');evaluation=read(out/f'exports/evaluation-{identifier}.json.gz');scene=Chain(model['parameters'],data)
        np.testing.assert_allclose([r['projected_center'] for r in model['records']],scene.pc,atol=0,rtol=0)
        cert=contact(scene,exact=True);assert cert==evaluation['contact']
        rays=np.load(out/f'exports/model-{identifier}-visibility.npz');ix=np.linspace(0,len(rays['xy'])-1,4000).astype(int);trace=scene.trace(rays['xy'][ix]);signed=np.full(len(ix),np.iinfo(np.int32).min,np.int32);ok=trace['owner']>=0;signed[ok]=scene.indices[trace['owner'][ok]]
        np.testing.assert_array_equal(signed,rays['owner'][ix]);np.testing.assert_array_equal(trace['unknown'],rays['unknown'][ix])
        sources={r['id']:r for r in data['rows']};obs=evaluation['observations']
        for j in np.linspace(0,len(obs)-1,25).astype(int):
            r=obs[j];tr=scene.trace(pixels(sources[r['id']]['pixels']));ids,counts=np.unique(tr['owner'],return_counts=True)
            alts=sorted([dict(index=int(scene.indices[k]),fraction=float(n/len(tr['owner']))) for k,n in zip(ids,counts) if k>=0],key=lambda a:(-a['fraction'],a['index']))
            assert alts==r['alternatives']
        checks.append(dict(model=identifier,positions=scene.n,contact_pairs=cert['pairs'],native_rays=4000,native_supports=25))
    save(BASE/'results/verification.json',dict(preserved=len(old)-len(allowed),changed=changed,native_photo_exact=True,replays=checks,
        files={str(p.relative_to(ROOT)):sha(p) for p in sorted((out/'exports').glob('*')) if p.is_file()}))
    print('Preserved',len(old)-len(allowed),'prior files;',checks)

if __name__=='__main__':main()
