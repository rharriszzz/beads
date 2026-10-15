"""Replay original M internals, before new segmentation changes."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-r288-mpl')
from scipy import ndimage as ndi
from photo2.r282.phase1 import image_features
from photo2.r285.run import local_mask
from photo2.r287.candidates import produce,PERTURBATIONS
from .common import *

def main():
    native,rgb,photo_meta=photo();f=image_features(rgb);results=[]
    for case in development():
        o=min(case['observations'],key=lambda o:np.linalg.norm(np.array(o['seed'])-case['seed']));x,y=o['seed'];origin=np.array([x,y])-48;sl=np.s_[y-48:y+49,x-48:x+49];lum,hs,paper=f['lum'][sl],f['hsv'][sl],f['paper'][sl];initial=local_mask(o['initial_support'],origin,(97,97));args=(lum,hs,paper,f['palette'],f['background_hue'],o['color'],initial);base=produce(*args);runs=[]
        for spec in [dict(name='baseline')]+PERTURBATIONS:
            variants=produce(*args,**{k:v for k,v in spec.items() if k!='name'});mask,info=variants['M'];yy,xx=np.where(mask);gain=mask&~base['M'][0];loss=base['M'][0]&~mask
            info=dict(info);positions={r['label']:r['placed'] for r in info['marker_ledger'] if r['label'] is not None};info['group_positions']=[positions[k] for k in info['group']]
            runs.append(dict(name=spec['name'],area=int(mask.sum()),gain=int(gain.sum()),loss=int(loss.sum()),support=support(np.c_[xx,yy]+origin),evidence=info))
        result=dict(name=case['name'],id=o['id'],seed=o['seed'],origin=origin.tolist(),color=o['color'],runs=runs);results.append(result)
        print(case['name'],[(q['name'],q['area'],q['evidence']['refined_seed'],q['evidence']['group_positions']) for q in runs],flush=True)
    save(OUT/'diagnosis.json.gz',dict(cases=results,photo=photo_meta,original_source_hash=sha(ROOT/'photo2/r287/candidates.py'),purpose='Causal original-M replay, before new algorithms; positions local to each M crop.'))
if __name__=='__main__':main()
