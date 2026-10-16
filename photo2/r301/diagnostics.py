"""Frozen, image-only neighboring separator checks, never supplied to fitting."""
import itertools
import numpy as np
from photo2.r297.common import photo,pixels,save,read,utc,sha,ROOT
from .evidence import BASE

def freeze():
    path=BASE/'evidence/withheld-separators.json'
    if path.exists():return
    rgb,_,_=photo();lum=rgb@np.array([.299,.587,.114])/255;out=[]
    for s in read(BASE/'evidence/frozen.json.gz')['sections']:
        rr=[r for r in s['observations'] if r['color']!='black'];pairs=[]
        for a,b in itertools.combinations(rr,2):
            aa=pixels({'runs':a['positive_interior']}).mean(0);bb=pixels({'runs':b['positive_interior']}).mean(0);dist=np.linalg.norm(bb-aa)
            if not 15<dist<55:continue
            xy=aa+np.linspace(0,1,97)[:,None]*(bb-aa);ij=np.rint(xy).astype(int);v=lum[ij[:,1],ij[:,0]];middle=np.arange(29,68);trough=int(middle[np.argmin(v[middle])]);contrast=min(v[:20].max(),v[-20:].max())-v[trough]
            if contrast<.12:continue
            pairs.append(dict(id=a['id']+'--'+b['id'],xy=xy.tolist(),luminance=v.tolist(),valley_sample=trough,representative_distance=float(dist),contrast=float(contrast),meaning='Measured dark valley between separate historical colored supports; may be shading, not verified bead separation. No owner/index assumptions.'))
        out.append(dict(section=s['id'],records=pairs))
    save(path,dict(utc=utc(),photo_sha256=sha(ROOT/'beads-photo-2.jpg'),sections=out,purpose='Photographic diagnostic frozen before native predictions are inspected; excluded from all training, independent of fit residuals. Existing R298 separator selection has zero profiles in these small windows.'))

if __name__=='__main__':freeze()
