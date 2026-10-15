"""Read-only exact historical measurement replay, before new detector methods."""
import numpy as np
from photo2.reconstruct_r276 import observation_data
from .common import *

def main():
    rows,rgb=observation_data(False)
    old=read(ROOT/'photo2/review/r276/observations.json')['observations']
    assert rows==old, 'historical observations differ'
    ledger=[dict(id=r['id'],color=r['color'],split=r['split'],specular_candidate=r['specular_candidate'],peak_minus_interior_centroid=(np.array(r['xy'])-r['interior_centroid']).tolist(),bright_minus_interior_centroid=(np.array(r['bright_patch']['centroid'])-r['interior_centroid']).tolist(),warning='Interior centroid is NOT a physical or visible-silhouette center') for r in rows if r['interior_centroid'] is not None]
    assert ledger==read(ROOT/'photo2/review/r276/highlight-relative-interior.json')
    result={}
    for group in ('all','strong','specular_candidate'):
        for col in ('red','yellow','black'):
            rr=[r for r in rows if r['color']==col and r['interior_centroid'] is not None and (group=='all' or r[group])]
            for key in ('point','patch','weighted'):
                def xy(r):return r['xy'] if key=='point' else r['bright_patch']['centroid'] if key=='patch' else r['bright_shape']['centroid']
                tr=[r for r in rr if r['split']=='train'];te=[r for r in rr if r['split']=='holdout']
                shift=np.mean([np.array(r['interior_centroid'])-xy(r) for r in tr],axis=0)
                residual=np.array([np.array(xy(r))-r['interior_centroid'] for r in te])
                result[f'{group}/{col}/{key}']=dict(train=len(tr),shift=shift.tolist(),raw=stats(np.linalg.norm(residual,axis=1)),corrected=stats(np.linalg.norm(residual+shift,axis=1)))
    save(OUT/'historical-replay.json',dict(exact_observations=len(rows),exact_ledger=len(ledger),metrics=result,inputs={p:sha(ROOT/p) for p in ('photo2/review/r275/inventory.json','photo2/review/r276/observations.json','photo2/review/r276/highlight-relative-interior.json')},scope='Retrospective original R276 split; constant offsets recomputed from archived measurements. Not new confirmation.'))
    print('Exact',len(rows),len(ledger))
    for k,v in result.items():
        if k.startswith('strong/') and k.endswith('/patch'):print(k,v)
if __name__=='__main__':main()
